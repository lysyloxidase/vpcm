"""Mondrian group-conditional conformal prediction."""

from __future__ import annotations

from dataclasses import dataclass, field

from vpcm_conformal.split_conformal import SplitConformalPredictor
from vpcm_conformal.types import PredictionIntervals, Vector, ensure_equal_length


@dataclass
class MondrianConformalPredictor:
    """Group-conditional conformal prediction per cell type."""

    alpha: float = 0.1
    group_predictors: dict[str, SplitConformalPredictor] = field(
        default_factory=dict[str, SplitConformalPredictor]
    )
    fallback_predictor: SplitConformalPredictor = field(init=False)

    def __post_init__(self) -> None:
        self.fallback_predictor = SplitConformalPredictor(alpha=self.alpha)

    def calibrate(
        self,
        y_true_cal: Vector,
        y_pred_cal: Vector,
        sigma_cal: Vector,
        groups: list[str],
    ) -> None:
        """Calibrate one split-conformal predictor per group."""

        ensure_equal_length(y_true_cal, y_pred_cal, sigma_cal)
        if len(groups) != len(y_true_cal):
            raise ValueError("groups must match calibration length.")
        grouped_indices: dict[str, list[int]] = {}
        for index, group in enumerate(groups):
            grouped_indices.setdefault(group, []).append(index)
        self.group_predictors = {}
        for group, indices in grouped_indices.items():
            predictor = SplitConformalPredictor(alpha=self.alpha)
            predictor.calibrate(
                [y_true_cal[index] for index in indices],
                [y_pred_cal[index] for index in indices],
                [sigma_cal[index] for index in indices],
            )
            self.group_predictors[group] = predictor
        self.fallback_predictor.calibrate(y_true_cal, y_pred_cal, sigma_cal)

    def predict_interval(
        self,
        y_pred: Vector,
        sigma: Vector,
        groups: list[str],
    ) -> PredictionIntervals:
        """Return group-conditional conformal intervals."""

        ensure_equal_length(y_pred, sigma)
        if len(groups) != len(y_pred):
            raise ValueError("groups must match prediction length.")
        lo: Vector = []
        hi: Vector = []
        for pred, std, group in zip(y_pred, sigma, groups):
            predictor = self.group_predictors.get(group, self.fallback_predictor)
            interval = predictor.predict_interval([pred], [std])
            lo.append(interval.lo[0])
            hi.append(interval.hi[0])
        return PredictionIntervals(lo=lo, hi=hi)

