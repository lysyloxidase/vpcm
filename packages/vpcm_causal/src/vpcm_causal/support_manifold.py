"""Interventional support manifold and do-calculus refusal gate."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from vpcm_core.types import Intervention
from vpcm_data.base import AnnDataLike
from vpcm_models.loaders import FoundationModelEnsemble

from vpcm_causal.refusal_report import (
    DO_CALCULUS_NOTE,
    RefusalReport,
    observational_interval,
    suggested_intervention_data,
)

Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class SupportCheck:
    """Result of interventional support evaluation."""

    in_support: bool
    mahalanobis_distance: float
    nearest_training_intervention: str = ""
    refusal_reason: str = ""

    def require_report(
        self,
        query_embedding: Vector,
        intervention: Intervention,
    ) -> RefusalReport:
        """Build a refusal report for an out-of-support query."""

        if self.in_support:
            raise ValueError("Cannot build a refusal report for an in-support query.")
        label = intervention_label(intervention)
        return RefusalReport(
            reason=self.refusal_reason,
            mahalanobis_distance=self.mahalanobis_distance,
            nearest_training_intervention=self.nearest_training_intervention,
            wide_observational_interval=observational_interval(query_embedding),
            do_calculus_note=DO_CALCULUS_NOTE,
            suggested_data=suggested_intervention_data(label),
        )


def intervention_label(intervention: Intervention) -> str:
    """Return a stable intervention label."""

    return str(
        intervention.get("intervention_id")
        or intervention.get("target")
        or intervention.get("intervention_type")
        or "unknown_intervention"
    )


def _obs_intervention_label(observation: Mapping[str, object]) -> str:
    value = observation.get("perturbation")
    if value is None:
        value = observation.get("intervention_id", "unknown_intervention")
    return str(value)


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _feature_variances(points: Matrix) -> Vector:
    n_points = len(points)
    width = len(points[0])
    means = [_mean([point[col] for point in points]) for col in range(width)]
    return [
        sum((point[col] - means[col]) ** 2 for point in points) / n_points
        for col in range(width)
    ]


def _align_width(matrix: Matrix, width: int) -> Matrix:
    aligned: Matrix = []
    for row in matrix:
        if len(row) == width:
            aligned.append(list(row))
        elif len(row) > width:
            aligned.append(list(row[:width]))
        else:
            aligned.append([*row, *([0.0] * (width - len(row)))])
    return aligned


def _concat_embeddings(embeddings: dict[str, Matrix]) -> Matrix:
    matrices = list(embeddings.values())
    if not matrices:
        return []
    n_rows = len(matrices[0])
    concatenated: Matrix = []
    for row_index in range(n_rows):
        row: Vector = []
        for matrix in matrices:
            row.extend(matrix[row_index])
        concatenated.append(row)
    return concatenated


def mahalanobis_to_nearest(
    query_embedding: Vector,
    support_points: Matrix,
    cov_inv_diag: Vector,
) -> tuple[float, int]:
    """Return diagonal-Mahalanobis distance to nearest support point."""

    if not support_points:
        raise ValueError("Support manifold is empty.")
    if len(query_embedding) != len(support_points[0]):
        raise ValueError("Query embedding width does not match support manifold.")
    best_distance = float("inf")
    best_index = 0
    for index, point in enumerate(support_points):
        squared = sum(
            (query_value - point_value) ** 2 * cov_inv_diag[col]
            for col, (query_value, point_value) in enumerate(
                zip(query_embedding, point)
            )
        )
        distance = squared**0.5
        if distance < best_distance:
            best_distance = distance
            best_index = index
    return best_distance, best_index


class InterventionalSupportManifold:
    """Explicit do-calculus refusal mechanism for causal support."""

    def __init__(self, fm_ensemble: FoundationModelEnsemble) -> None:
        self.fm = fm_ensemble
        self.support_points: Matrix = []
        self.cov_inv: Vector = []
        self.tau_ood: float = 0.0
        self.training_interventions: list[str] = []
        self.calibration_recall: float = 0.0
        self.calibration_fpr: float = 1.0

    def build_manifold(
        self,
        scperturb_adata: AnnDataLike,
        sci_plex_adata: AnnDataLike,
        tahoe_adata: AnnDataLike,
        lincs_profiles: Matrix,
    ) -> None:
        """Embed training interventions and fit diagonal Mahalanobis weights."""

        embedded_sources = [
            self.embed_adata(source_adata)
            for source_adata in (scperturb_adata, sci_plex_adata, tahoe_adata)
        ]
        if not embedded_sources:
            raise ValueError("At least one interventional source is required.")
        width = len(embedded_sources[0][0])
        aligned_lincs = _align_width(lincs_profiles, width)
        self.support_points = [
            point
            for source_points in embedded_sources
            for point in source_points
        ]
        self.support_points.extend(aligned_lincs)
        self.training_interventions = [
            _obs_intervention_label(observation)
            for source in (scperturb_adata, sci_plex_adata, tahoe_adata)
            for observation in source.obs
        ]
        self.training_interventions.extend(
            f"lincs_profile_{index}" for index in range(len(aligned_lincs))
        )
        variances = _feature_variances(self.support_points)
        self.cov_inv = [1.0 / (variance + 1e-6) for variance in variances]
        self.tau_ood = max(
            mahalanobis_to_nearest(point, self.support_points, self.cov_inv)[0]
            for point in self.support_points
        ) + 1e-6

    def embed_adata(self, adata: AnnDataLike) -> Matrix:
        """Embed AnnData-like cells through the full FM ensemble."""

        return _concat_embeddings(self.fm.embed(adata))

    def calibrate_tau(
        self,
        in_support_queries: AnnDataLike,
        ood_queries: AnnDataLike,
        target_refusal_recall: float = 0.95,
        target_in_support_fpr: float = 0.05,
    ) -> float:
        """Calibrate tau on held-out support and synthetic OOD splits."""

        if not self.support_points or not self.cov_inv:
            raise ValueError("Manifold must be built before tau calibration.")
        in_distances = [
            self._distance_only(point)
            for point in self.embed_adata(in_support_queries)
        ]
        ood_distances = [
            self._distance_only(point)
            for point in self.embed_adata(ood_queries)
        ]
        if not in_distances or not ood_distances:
            raise ValueError("Calibration requires non-empty splits.")

        candidates = sorted(set(in_distances + ood_distances))
        best_tau = candidates[-1]
        for candidate in candidates:
            refusal_recall = (
                sum(distance > candidate for distance in ood_distances)
                / len(ood_distances)
            )
            in_support_fpr = (
                sum(distance > candidate for distance in in_distances)
                / len(in_distances)
            )
            if (
                refusal_recall >= target_refusal_recall
                and in_support_fpr <= target_in_support_fpr
            ):
                best_tau = candidate
                break
        self.tau_ood = best_tau
        self.calibration_recall = (
            sum(distance > best_tau for distance in ood_distances)
            / len(ood_distances)
        )
        self.calibration_fpr = (
            sum(distance > best_tau for distance in in_distances)
            / len(in_distances)
        )
        return self.tau_ood

    def check_support(
        self,
        query_embedding: Vector,
        intervention: Intervention,
    ) -> SupportCheck:
        """Return whether a query is within interventional support."""

        if not self.support_points or not self.cov_inv:
            raise ValueError("Manifold must be built before support checks.")
        distance, nearest_index = mahalanobis_to_nearest(
            query_embedding,
            self.support_points,
            self.cov_inv,
        )
        nearest = self.training_interventions[nearest_index]
        if distance > self.tau_ood:
            label = intervention_label(intervention)
            return SupportCheck(
                in_support=False,
                mahalanobis_distance=distance,
                nearest_training_intervention=nearest,
                refusal_reason=(
                    f"Mahalanobis distance {distance:.2f} exceeds calibrated "
                    f"tau_OOD={self.tau_ood:.2f}. Query intervention {label} "
                    "lies outside the interventional training manifold in "
                    "foundation-model latent space. Observational "
                    "extrapolation is not a causal estimate."
                ),
            )
        return SupportCheck(
            in_support=True,
            mahalanobis_distance=distance,
            nearest_training_intervention=nearest,
        )

    def _distance_only(self, query_embedding: Vector) -> float:
        return mahalanobis_to_nearest(
            query_embedding,
            self.support_points,
            self.cov_inv,
        )[0]
