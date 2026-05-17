"""Split conformal prediction."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from vpcm_conformal.types import (
    PredictionIntervals,
    Vector,
    ensure_equal_length,
    higher_quantile,
    safe_sigma,
)


@dataclass
class SplitConformalPredictor:
    """Distribution-free split conformal prediction.

    Provides the marginal finite-sample guarantee
    ``P(y in [lo, hi]) >= 1 - alpha`` under exchangeability.
    """

    alpha: float = 0.1
    qhat: float = 0.0
    calibrated: bool = False

    def __post_init__(self) -> None:
        if self.alpha <= 0.0 or self.alpha >= 1.0:
            raise ValueError("alpha must be in (0, 1).")

    def calibrate(
        self,
        y_true_cal: Vector,
        y_pred_cal: Vector,
        sigma_cal: Vector,
    ) -> float:
        """Calibrate qhat from heteroscedastic nonconformity scores."""

        ensure_equal_length(y_true_cal, y_pred_cal, sigma_cal)
        scores = [
            abs(true - pred) / safe_sigma(sigma)
            for true, pred, sigma in zip(y_true_cal, y_pred_cal, sigma_cal)
        ]
        n = len(scores)
        q_level = min(1.0, ceil((n + 1) * (1.0 - self.alpha)) / n)
        self.qhat = higher_quantile(scores, q_level)
        self.calibrated = True
        return self.qhat

    def predict_interval(self, y_pred: Vector, sigma: Vector) -> PredictionIntervals:
        """Return conformal prediction intervals."""

        if not self.calibrated:
            raise ValueError("SplitConformalPredictor must be calibrated first.")
        ensure_equal_length(y_pred, sigma)
        lo = [pred - self.qhat * safe_sigma(std) for pred, std in zip(y_pred, sigma)]
        hi = [pred + self.qhat * safe_sigma(std) for pred, std in zip(y_pred, sigma)]
        return PredictionIntervals(lo=lo, hi=hi)

