"""AnnData quality-control checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from vpcm_data.base import AnnDataLike


@dataclass(frozen=True)
class QCThresholds:
    """Minimal QC thresholds for harmonized fixtures and live AnnData."""

    min_cells: int = 1
    min_genes: int = 1
    required_obs_columns: tuple[str, ...] = (
        "cell_id",
        "patient_hash",
        "disease_id",
        "cell_type_id",
        "perturbation_type",
        "perturbation",
        "source_dataset",
    )


@dataclass(frozen=True)
class QCReport:
    """QC report returned by the AnnData QC pipeline."""

    passed: bool
    n_obs: int
    n_vars: int
    errors: list[str]


DEFAULT_QC_THRESHOLDS = QCThresholds()


def run_qc(
    adata: AnnDataLike,
    thresholds: Optional[QCThresholds] = None,
) -> QCReport:
    """Run schema and dimensionality checks on an AnnData-like object."""

    active_thresholds = thresholds or DEFAULT_QC_THRESHOLDS
    errors: list[str] = []
    if adata.n_obs < active_thresholds.min_cells:
        errors.append("n_obs below threshold")
    if adata.n_vars < active_thresholds.min_genes:
        errors.append("n_vars below threshold")
    if adata.x_shape != (adata.n_obs, adata.n_vars):
        errors.append("x_shape does not match obs/var dimensions")
    for index, observation in enumerate(adata.obs):
        missing = [
            column
            for column in active_thresholds.required_obs_columns
            if column not in observation
        ]
        if missing:
            errors.append(f"obs[{index}] missing columns: {', '.join(missing)}")
    return QCReport(
        passed=not errors,
        n_obs=adata.n_obs,
        n_vars=adata.n_vars,
        errors=errors,
    )
