"""Coverage audit and recalibration trigger."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_conformal.types import PredictionIntervals, Vector, ensure_equal_length


class CoverageAlarmError(AssertionError):
    """Raised when conformal coverage is outside the acceptance band."""


CoverageAlarm = CoverageAlarmError


@dataclass(frozen=True)
class CoverageAudit:
    """Verify marginal coverage at alpha=0.1 lies in the V&V40 band."""

    lower: float = 0.88
    upper: float = 0.92

    def audit(self, predictions: PredictionIntervals, ground_truth: Vector) -> float:
        """Return coverage or raise a recalibration alarm."""

        ensure_equal_length(predictions.lo, predictions.hi, ground_truth)
        covered = [
            lo <= truth <= hi
            for lo, hi, truth in zip(predictions.lo, predictions.hi, ground_truth)
        ]
        coverage = sum(1 for value in covered if value) / len(covered)
        if coverage < self.lower or coverage > self.upper:
            raise CoverageAlarmError(
                f"Coverage {coverage:.3f} outside acceptable band. "
                "Triggering re-calibration."
            )
        return coverage

    def audit_by_group(
        self,
        predictions: PredictionIntervals,
        ground_truth: Vector,
        groups: list[str],
    ) -> dict[str, float]:
        """Audit coverage per group."""

        if len(groups) != len(ground_truth):
            raise ValueError("groups must match ground-truth length.")
        group_coverages: dict[str, float] = {}
        for group in sorted(set(groups)):
            indices = [index for index, value in enumerate(groups) if value == group]
            group_prediction = PredictionIntervals(
                lo=[predictions.lo[index] for index in indices],
                hi=[predictions.hi[index] for index in indices],
            )
            group_truth = [ground_truth[index] for index in indices]
            group_coverages[group] = self.audit(group_prediction, group_truth)
        return group_coverages
