"""Train-set mean baseline, the mandatory VPCM credibility anchor."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from vpcm_core.types import Intervention
from vpcm_data.base import AnnDataLike

from vpcm_baselines._matrix import (
    Matrix,
    Vector,
    mae,
    mean_vector,
    mse,
    pearson,
    select,
    top_n_indices,
)


def _cell_type(observation: Mapping[str, object]) -> str:
    value = observation.get("cell_type")
    if value is None:
        value = observation.get("cell_type_label", "unknown")
    return str(value)


@dataclass
class TrainMeanBaseline:
    """Predict each cell type's training-set mean expression vector.

    The intervention is intentionally ignored. Every VPCM perturbation
    prediction must report this baseline because published perturbation
    benchmarks show it can outperform scGPT and scFoundation.
    """

    cell_type_means: dict[str, Vector] = field(default_factory=dict[str, Vector])
    global_mean: Vector = field(default_factory=list[float])

    def fit(self, adata_train: AnnDataLike) -> None:
        """Compute one mean expression vector per cell type."""

        if not adata_train.x:
            raise ValueError("TrainMeanBaseline requires adata_train.x.")
        grouped: dict[str, Matrix] = {}
        for row, observation in zip(adata_train.x, adata_train.obs):
            grouped.setdefault(_cell_type(observation), []).append(row)
        self.cell_type_means = {
            cell_type: mean_vector(rows) for cell_type, rows in grouped.items()
        }
        self.global_mean = mean_vector(adata_train.x)

    def predict(
        self,
        adata_query: AnnDataLike,
        intervention: Intervention,
    ) -> Vector:
        """Return the train-set mean for the query cell type.

        ``intervention`` is accepted for API parity and deliberately ignored.
        """

        del intervention
        if not self.cell_type_means:
            raise ValueError("TrainMeanBaseline must be fitted before predict().")
        if not adata_query.obs:
            return list(self.global_mean)
        query_cell_type = _cell_type(adata_query.obs[0])
        return list(self.cell_type_means.get(query_cell_type, self.global_mean))

    def score(
        self,
        adata_query: AnnDataLike,
        observed: Vector,
        intervention: Intervention,
        top_n: int = 20,
        target_gene_index: int = -1,
    ) -> dict[str, float]:
        """Score a query prediction on top-N DE genes with target removed."""

        prediction = self.predict(adata_query, intervention)
        baseline = self.global_mean or prediction
        indices = top_n_indices(
            reference=observed,
            baseline=baseline,
            top_n=top_n,
            excluded_index=target_gene_index,
        )
        observed_top = select(observed, indices)
        prediction_top = select(prediction, indices)
        return {
            "pearson": pearson(prediction_top, observed_top),
            "mse": mse(prediction_top, observed_top),
            "mae": mae(prediction_top, observed_top),
        }
