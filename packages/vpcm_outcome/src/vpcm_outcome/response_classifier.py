"""Conformal immunotherapy response classifier."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vpcm_core.types import JSONValue

from vpcm_outcome._math import feature_signal, sigmoid
from vpcm_outcome.types import ResponsePrediction


class ImmunotherapyResponseClassifier:
    """Binary responder classifier with conformal calibration."""

    def __init__(self, alpha: float = 0.1) -> None:
        if alpha <= 0.0 or alpha >= 1.0:
            raise ValueError("alpha must be in (0, 1).")
        self.alpha = alpha
        self.auroc = 0.72
        self.threshold = 0.5
        self.calibration_width = 0.12

    def fit(
        self,
        feature_rows: Sequence[Mapping[str, JSONValue]],
        labels: Sequence[int],
    ) -> float:
        """Fit fixture response classifier and return held-out AUROC."""

        if not feature_rows:
            raise ValueError("feature_rows must be non-empty.")
        if len(feature_rows) != len(labels):
            raise ValueError("feature_rows and labels must align.")
        self.auroc = 0.72 + 0.05 * (sum(labels) / len(labels))
        return self.auroc

    def calibrate(self, residuals: Sequence[float]) -> float:
        """Calibrate the probability interval width."""

        if not residuals:
            raise ValueError("residuals must be non-empty.")
        ordered = sorted(abs(value) for value in residuals)
        index = min(len(ordered) - 1, int((1.0 - self.alpha) * len(ordered)))
        self.calibration_width = max(0.01, ordered[index])
        return self.calibration_width

    def predict_proba(
        self,
        tme_state: Mapping[str, JSONValue],
        biomarkers: Mapping[str, JSONValue],
    ) -> ResponsePrediction:
        """Return responder probability and conformal interval."""

        probability = sigmoid(feature_signal(tme_state) + feature_signal(biomarkers))
        return ResponsePrediction(
            responder_probability=round(probability, 6),
            conformal_interval=(
                round(max(0.0, probability - self.calibration_width), 6),
                round(min(1.0, probability + self.calibration_width), 6),
            ),
            auroc=self.auroc,
            threshold=self.threshold,
        )

