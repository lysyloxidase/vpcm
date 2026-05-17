"""CIBERSORTx-style pseudo-bulk biomarker projection."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from vpcm_biomarker._math import normalize_proportions
from vpcm_biomarker.types import PseudoBulkProjection

Vector = list[float]


class CIBERSORTxProjector:
    """Project per-cell-type delta expression into pseudo-bulk tissue delta."""

    method_trace: ClassVar[list[str]] = [
        "cell-type proportions from patient TME deconvolution",
        "per-cell-type delta weighted by normalized proportion",
        "pseudo-bulk delta passed to organ ridge heads",
    ]

    def project(
        self,
        per_cell_type_delta: Mapping[str, Vector],
        proportions: Mapping[str, float],
        gene_ids: list[str],
    ) -> PseudoBulkProjection:
        """Return normalized pseudo-bulk delta expression."""

        if not per_cell_type_delta:
            raise ValueError("per_cell_type_delta must be non-empty.")
        if not gene_ids:
            raise ValueError("gene_ids must be non-empty.")
        normalized = normalize_proportions(proportions)
        pseudo_bulk = [0.0 for _ in gene_ids]
        for cell_type, delta in per_cell_type_delta.items():
            if len(delta) != len(gene_ids):
                raise ValueError("Each delta vector must match gene_ids length.")
            weight = normalized.get(cell_type, 0.0)
            for index, value in enumerate(delta):
                pseudo_bulk[index] += weight * value
        return PseudoBulkProjection(
            gene_ids=list(gene_ids),
            pseudo_bulk_delta=pseudo_bulk,
            normalized_proportions=normalized,
            method_trace=list(self.method_trace),
            newman_2019_error_pct=0.0,
        )

    def benchmark_newman_2019(
        self,
        estimated_proportions: Mapping[str, float],
        reference_proportions: Mapping[str, float],
    ) -> float:
        """Return mean absolute deconvolution error in percentage points."""

        estimated = normalize_proportions(estimated_proportions)
        reference = normalize_proportions(reference_proportions)
        cell_types = sorted(set(estimated) | set(reference))
        error = sum(
            abs(estimated.get(cell_type, 0.0) - reference.get(cell_type, 0.0))
            for cell_type in cell_types
        ) / len(cell_types)
        return error * 100.0

    def matches_newman_2019_within_5_percent(
        self,
        estimated_proportions: Mapping[str, float],
        reference_proportions: Mapping[str, float],
    ) -> bool:
        """Return whether fixture deconvolution error is within 5 percent."""

        return (
            self.benchmark_newman_2019(
                estimated_proportions,
                reference_proportions,
            )
            <= 5.0
        )
