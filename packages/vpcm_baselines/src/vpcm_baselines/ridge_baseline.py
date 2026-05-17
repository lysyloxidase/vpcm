"""Ridge baseline on PCA features plus perturbation x cell-type one-hot."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from vpcm_core.types import Intervention
from vpcm_data.base import AnnDataLike

from vpcm_baselines._matrix import Matrix, Vector, dot, gaussian_solve, mean_vector


def _obs_label(observation: Mapping[str, object], key: str, fallback: str) -> str:
    value = observation.get(key)
    if value is None and key == "cell_type":
        value = observation.get("cell_type_label")
    if value is None:
        value = fallback
    return str(value)


@dataclass
class PCAProjection:
    """Small variance-ranked PCA-like projection for fixture mode."""

    n_components: int = 50
    means: Vector = field(default_factory=list[float])
    component_indices: list[int] = field(default_factory=list[int])

    def fit(self, matrix: Matrix) -> None:
        """Fit variance-ranked components."""

        self.means = mean_vector(matrix)
        n_rows = len(matrix)
        variances: list[tuple[float, int]] = []
        for col_index, mean_value in enumerate(self.means):
            variance = (
                sum((row[col_index] - mean_value) ** 2 for row in matrix) / n_rows
            )
            variances.append((variance, col_index))
        variances.sort(reverse=True)
        n_components = min(self.n_components, len(variances))
        self.component_indices = [index for _, index in variances[:n_components]]

    def transform(self, matrix: Matrix) -> Matrix:
        """Project matrix onto selected centered expression features."""

        if not self.component_indices:
            raise ValueError("PCAProjection must be fitted before transform().")
        return [
            [row[index] - self.means[index] for index in self.component_indices]
            for row in matrix
        ]


@dataclass
class RidgeBaseline:
    """Linear ridge regression on PCA features and perturbation x cell-type."""

    n_pca: int = 50
    alpha: float = 1.0
    pca: PCAProjection = field(init=False)
    feature_names: list[str] = field(default_factory=list[str])
    coefficients: Matrix = field(default_factory=list[list[float]])
    output_dim: int = 0

    def __post_init__(self) -> None:
        self.pca = PCAProjection(n_components=self.n_pca)

    def fit(self, adata_train: AnnDataLike) -> None:
        """Fit ridge coefficients on expression and perturbation metadata."""

        if not adata_train.x:
            raise ValueError("RidgeBaseline requires adata_train.x.")
        self.output_dim = len(adata_train.x[0])
        self.pca.fit(adata_train.x)
        pca_features = self.pca.transform(adata_train.x)
        interaction_names = sorted(
            {
                self._interaction_name(observation)
                for observation in adata_train.obs
            }
        )
        self.feature_names = [
            "bias",
            *[f"pc_{index}" for index in self.pca.component_indices],
            *interaction_names,
        ]
        design = [
            self._design_row(pca_row, observation)
            for pca_row, observation in zip(pca_features, adata_train.obs)
        ]
        self.coefficients = self._fit_multioutput_ridge(design, adata_train.x)

    def predict(
        self,
        adata_query: AnnDataLike,
        intervention: Intervention,
    ) -> Vector:
        """Predict expression for the first query row."""

        del intervention
        if not self.coefficients:
            raise ValueError("RidgeBaseline must be fitted before predict().")
        if not adata_query.x:
            raise ValueError("RidgeBaseline requires adata_query.x.")
        pca_row = self.pca.transform([adata_query.x[0]])[0]
        design_row = self._design_row(pca_row, adata_query.obs[0])
        return [
            dot(design_row, [coef_row[col] for coef_row in self.coefficients])
            for col in range(self.output_dim)
        ]

    def _interaction_name(self, observation: Mapping[str, object]) -> str:
        cell_type = _obs_label(observation, "cell_type", "unknown_cell")
        perturbation = _obs_label(observation, "perturbation", "unknown_perturbation")
        return f"perturbation={perturbation}|cell_type={cell_type}"

    def _design_row(
        self,
        pca_row: Vector,
        observation: Mapping[str, object],
    ) -> Vector:
        interaction_name = self._interaction_name(observation)
        one_hot = [
            1.0 if feature_name == interaction_name else 0.0
            for feature_name in self.feature_names
            if feature_name.startswith("perturbation=")
        ]
        return [1.0, *pca_row, *one_hot]

    def _fit_multioutput_ridge(self, design: Matrix, targets: Matrix) -> Matrix:
        n_features = len(design[0])
        xtx = [
            [
                sum(row[left] * row[right] for row in design)
                + (self.alpha if left == right and left != 0 else 0.0)
                for right in range(n_features)
            ]
            for left in range(n_features)
        ]
        coefficient_columns: list[Vector] = []
        for gene_index in range(self.output_dim):
            rhs = [
                sum(
                    row[feature_index] * target_row[gene_index]
                    for row, target_row in zip(design, targets)
                )
                for feature_index in range(n_features)
            ]
            coefficient_columns.append(gaussian_solve(xtx, rhs))
        return [
            [coefficient_columns[col][row] for col in range(self.output_dim)]
            for row in range(n_features)
        ]
