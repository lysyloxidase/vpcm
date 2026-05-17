"""Conformalized quantile regression in fixture mode."""

from __future__ import annotations

from dataclasses import dataclass, field

from vpcm_conformal.types import (
    Matrix,
    PredictionIntervals,
    Vector,
    column,
    ensure_equal_length,
    higher_quantile,
)


@dataclass
class ConformalizedQuantileRegression:
    """Per-gene conformalized quantile regression.

    Production deployments can swap this fixture implementation for MAPIE
    0.9+ estimators. The API and calibration adjustment mirror CQR.
    """

    alpha: float = 0.1
    lower_quantiles: Vector = field(default_factory=list[float])
    upper_quantiles: Vector = field(default_factory=list[float])
    adjustments: Vector = field(default_factory=list[float])

    def __post_init__(self) -> None:
        if self.alpha <= 0.0 or self.alpha >= 1.0:
            raise ValueError("alpha must be in (0, 1).")

    def fit_quantiles(self, y_train: Matrix) -> None:
        """Fit fixture per-gene empirical quantiles."""

        if not y_train:
            raise ValueError("y_train must not be empty.")
        n_genes = len(y_train[0])
        self.lower_quantiles = []
        self.upper_quantiles = []
        for gene_index in range(n_genes):
            values = column(y_train, gene_index)
            self.lower_quantiles.append(higher_quantile(values, self.alpha / 2.0))
            self.upper_quantiles.append(higher_quantile(values, 1.0 - self.alpha / 2.0))
        self.adjustments = [0.0 for _ in range(n_genes)]

    def calibrate(
        self,
        y_true_cal: Matrix,
        lo_pred_cal: Matrix,
        hi_pred_cal: Matrix,
    ) -> Vector:
        """Calibrate nonconformity adjustment per gene."""

        if not y_true_cal:
            raise ValueError("calibration data must not be empty.")
        n_genes = len(y_true_cal[0])
        adjustments: Vector = []
        for gene_index in range(n_genes):
            scores: Vector = []
            for true_row, lo_row, hi_row in zip(y_true_cal, lo_pred_cal, hi_pred_cal):
                scores.append(
                    max(
                        lo_row[gene_index] - true_row[gene_index],
                        true_row[gene_index] - hi_row[gene_index],
                    )
                )
            q_level = min(1.0, (len(scores) + 1) * (1.0 - self.alpha) / len(scores))
            adjustments.append(max(0.0, higher_quantile(scores, q_level)))
        self.adjustments = adjustments
        return list(self.adjustments)

    def predict_interval(self, lo_pred: Vector, hi_pred: Vector) -> PredictionIntervals:
        """Return CQR-adjusted per-gene intervals."""

        ensure_equal_length(lo_pred, hi_pred, self.adjustments)
        return PredictionIntervals(
            lo=[lo - adjustment for lo, adjustment in zip(lo_pred, self.adjustments)],
            hi=[hi + adjustment for hi, adjustment in zip(hi_pred, self.adjustments)],
        )
