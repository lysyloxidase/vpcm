"""Typed outcome prediction reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from vpcm_core.types import JSONValue, PredictionOutput


@dataclass(frozen=True)
class SurvivalPrediction:
    """DeepSurv-style survival prediction."""

    hazard_ratio: float
    hazard_interval: tuple[float, float]
    median_pfs_months: float
    median_os_months: float
    risk_quartile: str
    c_index: float

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "hazard_ratio": self.hazard_ratio,
            "hazard_interval": list(self.hazard_interval),
            "median_pfs_months": self.median_pfs_months,
            "median_os_months": self.median_os_months,
            "risk_quartile": self.risk_quartile,
            "c_index": self.c_index,
        })

    def to_audit_output(self) -> PredictionOutput:
        """Return audit summary fields."""

        return {
            "composite_pfs_months": self.median_pfs_months,
            "uncertainty_interval": [
                self.hazard_interval[0],
                self.hazard_interval[1],
            ],
            "mechanism_summary": (
                f"DeepSurv survival prediction: HR={self.hazard_ratio:.3f}, "
                f"risk={self.risk_quartile}, C-index={self.c_index:.3f}."
            ),
        }


@dataclass(frozen=True)
class CompetingRiskPrediction:
    """DeepHit-style competing risks prediction."""

    risk_probabilities: dict[str, float]
    cumulative_incidence_months: dict[str, float]
    dynamic_variant: bool
    c_index: float

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "risk_probabilities": self.risk_probabilities,
            "cumulative_incidence_months": self.cumulative_incidence_months,
            "dynamic_variant": self.dynamic_variant,
            "c_index": self.c_index,
        })


@dataclass(frozen=True)
class ResponsePrediction:
    """Conformal immunotherapy response prediction."""

    responder_probability: float
    conformal_interval: tuple[float, float]
    auroc: float
    threshold: float

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "responder_probability": self.responder_probability,
            "conformal_interval": list(self.conformal_interval),
            "auroc": self.auroc,
            "threshold": self.threshold,
        })

    def to_audit_output(self) -> PredictionOutput:
        """Return audit summary fields."""

        return {
            "cd8_t_cell_infiltration_fold_change": (
                1.0 + self.responder_probability
            ),
            "uncertainty_interval": [
                self.conformal_interval[0],
                self.conformal_interval[1],
            ],
            "mechanism_summary": (
                "Immunotherapy response classifier: "
                f"p={self.responder_probability:.3f}, AUROC={self.auroc:.3f}."
            ),
        }


@dataclass(frozen=True)
class MultiomicFusionReport:
    """Optional multi-omic fusion report."""

    modalities: list[str]
    fused_features: dict[str, float]
    missing_modalities: list[str]
    tools: list[str]

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "modalities": self.modalities,
            "fused_features": self.fused_features,
            "missing_modalities": self.missing_modalities,
            "tools": self.tools,
        })

