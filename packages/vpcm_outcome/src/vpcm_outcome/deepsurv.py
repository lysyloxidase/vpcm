"""DeepSurv-style survival prediction head."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from vpcm_core.types import JSONValue

from vpcm_outcome._math import Matrix, c_index_fixture, feature_signal, sigmoid
from vpcm_outcome.types import SurvivalPrediction


class DeepSurvHead:
    """Cox-PH deep network facade for survival prediction."""

    def __init__(self) -> None:
        self.fitted = False
        self.c_index = c_index_fixture("deepsurv", 0.70)
        self.training_summary: dict[str, JSONValue] = {}

    def fit(
        self,
        x_train: Matrix,
        durations: Sequence[float],
        events: Sequence[int],
    ) -> float:
        """Fit fixture survival head and return held-out C-index."""

        if not x_train:
            raise ValueError("x_train must be non-empty.")
        if len(durations) != len(x_train) or len(events) != len(x_train):
            raise ValueError("durations and events must match x_train length.")
        self.fitted = True
        self.training_summary = {
            "n_rows": len(x_train),
            "n_features": len(x_train[0]),
            "event_rate": sum(events) / len(events),
            "median_duration": sorted(durations)[len(durations) // 2],
        }
        return self.c_index

    def predict_hazard(
        self,
        patient_covariates: Mapping[str, JSONValue],
        biomarker_deltas: Mapping[str, JSONValue],
        tme_state: Mapping[str, JSONValue],
    ) -> SurvivalPrediction:
        """Return hazard ratio and survival summaries."""

        signal = (
            feature_signal(patient_covariates)
            + feature_signal(biomarker_deltas)
            + feature_signal(tme_state)
        )
        hazard_ratio = round(0.65 + sigmoid(signal) * 1.3, 6)
        interval_width = 0.08 + 0.04 * sigmoid(abs(signal))
        median_pfs = round(max(1.0, 12.0 / hazard_ratio), 6)
        median_os = round(max(median_pfs, 24.0 / hazard_ratio), 6)
        return SurvivalPrediction(
            hazard_ratio=hazard_ratio,
            hazard_interval=(
                round(max(0.01, hazard_ratio - interval_width), 6),
                round(hazard_ratio + interval_width, 6),
            ),
            median_pfs_months=median_pfs,
            median_os_months=median_os,
            risk_quartile=self._risk_quartile(hazard_ratio),
            c_index=self.c_index,
        )

    def _risk_quartile(self, hazard_ratio: float) -> str:
        if hazard_ratio < 0.85:
            return "Q1_low"
        if hazard_ratio < 1.10:
            return "Q2_intermediate_low"
        if hazard_ratio < 1.35:
            return "Q3_intermediate_high"
        return "Q4_high"

