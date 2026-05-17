"""DeepHit-style competing risks survival head."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vpcm_core.types import JSONValue

from vpcm_outcome._math import Matrix, c_index_fixture, feature_signal, sigmoid
from vpcm_outcome.types import CompetingRiskPrediction

_RISKS = [
    "progression",
    "death_from_disease",
    "death_from_other_causes",
    "toxicity_discontinuation",
]


class DeepHitHead:
    """Competing-risks survival facade with optional dynamic variant."""

    def __init__(self, dynamic: bool = True) -> None:
        self.dynamic = dynamic
        self.fitted = False
        self.c_index = c_index_fixture("deephit", 0.65)

    def fit(
        self,
        x_train: Matrix,
        durations: Sequence[float],
        events: Sequence[int],
        risks: Sequence[str],
    ) -> float:
        """Fit fixture competing-risks head and return held-out C-index."""

        if not x_train:
            raise ValueError("x_train must be non-empty.")
        if not (len(durations) == len(events) == len(risks) == len(x_train)):
            raise ValueError("durations, events, risks, and x_train must align.")
        self.fitted = True
        return self.c_index

    def predict_competing_risks(
        self,
        features: Mapping[str, JSONValue],
    ) -> CompetingRiskPrediction:
        """Return risk probabilities and median event-time fixtures."""

        signal = feature_signal(features)
        raw = {
            risk: 0.05 + 0.9 * sigmoid(signal + index * 0.2)
            for index, risk in enumerate(_RISKS)
        }
        total = sum(raw.values())
        probabilities = {
            risk: round(value / total, 6)
            for risk, value in raw.items()
        }
        incidence = {
            risk: round(6.0 + 36.0 * (1.0 - probability), 6)
            for risk, probability in probabilities.items()
        }
        return CompetingRiskPrediction(
            risk_probabilities=probabilities,
            cumulative_incidence_months=incidence,
            dynamic_variant=self.dynamic,
            c_index=self.c_index,
        )

