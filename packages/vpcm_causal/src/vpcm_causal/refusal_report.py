"""Refusal report for out-of-support causal extrapolation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast

from vpcm_core.types import JSONValue, PredictionOutput

DO_CALCULUS_NOTE = (
    "Per Pearl's identifiability theorems, p(Y|do(X)) is not identifiable "
    "from observational p(Y|X) alone without sufficient causal assumptions "
    "or interventional support. VPCM refuses to emit a causal estimate here."
)


@dataclass(frozen=True)
class RefusalReport:
    """Returned when VPCM refuses to extrapolate."""

    reason: str
    mahalanobis_distance: float
    nearest_training_intervention: str
    wide_observational_interval: tuple[float, float]
    do_calculus_note: str
    suggested_data: str

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable refusal payload."""

        return cast(dict[str, JSONValue], asdict(self))

    def to_audit_output(self) -> PredictionOutput:
        """Return a prediction output payload suitable for audit logging."""

        return {
            "mechanism_summary": (
                f"REFUSAL: {self.reason} Nearest seen intervention: "
                f"{self.nearest_training_intervention}. {self.do_calculus_note}"
            ),
            "uncertainty_interval": [
                self.wide_observational_interval[0],
                self.wide_observational_interval[1],
            ],
        }


def suggested_intervention_data(intervention_label: str) -> str:
    """Suggest the experiment that would close the interventional gap."""

    return (
        "Run matched Perturb-seq or sci-Plex evidence for "
        f"{intervention_label} in the queried cell type, dose, and subtype."
    )


def observational_interval(values: list[float]) -> tuple[float, float]:
    """Return a 5th-95th percentile observational interval."""

    if not values:
        return (0.0, 0.0)
    ordered = sorted(values)
    low_index = int(0.05 * (len(ordered) - 1))
    high_index = int(0.95 * (len(ordered) - 1))
    return (ordered[low_index], ordered[high_index])

