"""Mandatory baseline report returned alongside every VPCM prediction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast

from vpcm_core.types import JSONValue


@dataclass(frozen=True)
class BaselineReport:
    """Credibility comparison for one perturbation prediction."""

    mean_baseline_pearson: float
    ridge_baseline_pearson: float
    vpcm_ensemble_pearson: float
    beat_mean_delta: float
    beat_ridge_delta: float
    target_gene_removed: bool
    top_n: int
    eval_set: str

    @classmethod
    def from_scores(
        cls,
        mean_baseline_pearson: float,
        ridge_baseline_pearson: float,
        vpcm_ensemble_pearson: float,
        target_gene_removed: bool,
        top_n: int,
        eval_set: str,
    ) -> BaselineReport:
        """Build a report and compute deltas against mandatory baselines."""

        return cls(
            mean_baseline_pearson=mean_baseline_pearson,
            ridge_baseline_pearson=ridge_baseline_pearson,
            vpcm_ensemble_pearson=vpcm_ensemble_pearson,
            beat_mean_delta=vpcm_ensemble_pearson - mean_baseline_pearson,
            beat_ridge_delta=vpcm_ensemble_pearson - ridge_baseline_pearson,
            target_gene_removed=target_gene_removed,
            top_n=top_n,
            eval_set=eval_set,
        )

    def validate(self) -> None:
        """Validate report fields used by regulatory audit records."""

        for field_name in (
            "mean_baseline_pearson",
            "ridge_baseline_pearson",
            "vpcm_ensemble_pearson",
        ):
            value = float(getattr(self, field_name))
            if value < -1.0 or value > 1.0:
                raise ValueError(f"{field_name} must be in [-1, 1].")
        if not self.target_gene_removed:
            raise ValueError("target_gene_removed must be true for fair evaluation.")
        if self.top_n <= 0:
            raise ValueError("top_n must be positive.")
        if not self.eval_set:
            raise ValueError("eval_set is required.")

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-serializable report."""

        return cast(dict[str, JSONValue], asdict(self))
