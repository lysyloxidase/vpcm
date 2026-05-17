"""Patient covariate encoding for LoRA adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from vpcm_core.types import JSONValue

from vpcm_lora._utils import stable_patient_embedding


@dataclass
class PatientCovariateEncoder:
    """Encode patient covariates as additional model channels."""

    embedding_dim: int = 64
    prs_weights_by_ancestry: dict[str, dict[str, float]] = field(
        default_factory=dict[str, dict[str, float]]
    )

    def load_prs_weights(
        self,
        ancestry: str,
        weights: dict[str, float],
    ) -> None:
        """Load ancestry-stratified PRS weights."""

        if not weights:
            raise ValueError("PRS weights must not be empty.")
        self.prs_weights_by_ancestry[ancestry] = dict(weights)

    def encode(
        self,
        patient_id: str,
        covariates: dict[str, JSONValue],
    ) -> dict[str, JSONValue]:
        """Encode patient covariates, preserving graceful missing-channel flags."""

        missing_channels: list[str] = []
        ancestry = str(covariates.get("ancestry", "unknown"))
        prs_scores = covariates.get("prs_scores", {})
        if not isinstance(prs_scores, dict):
            prs_scores = {}
        if ancestry not in self.prs_weights_by_ancestry:
            missing_channels.append("prs_weights")
        if not prs_scores:
            missing_channels.append("prs_scores")
        weighted_prs = self._weighted_prs(ancestry, prs_scores)

        encoded = {
            "patient_id_embedding": stable_patient_embedding(
                patient_id,
                self.embedding_dim,
            ),
            "ancestry": ancestry,
            "weighted_prs": weighted_prs,
            "somatic_mutations": covariates.get("somatic_mutations", []),
            "disease_subtype": covariates.get("disease_subtype", "unknown"),
            "age": covariates.get("age"),
            "sex": covariates.get("sex", "unknown"),
            "stage": covariates.get("stage", "unknown"),
            "prior_treatment_lines": covariates.get("prior_treatment_lines", 0),
            "missing_channels": missing_channels,
        }
        return cast(dict[str, JSONValue], encoded)

    def _weighted_prs(self, ancestry: str, prs_scores: dict[str, JSONValue]) -> float:
        weights = self.prs_weights_by_ancestry.get(ancestry, {})
        total = 0.0
        for key, weight in weights.items():
            value = prs_scores.get(key, 0.0)
            if isinstance(value, (float, int)):
                total += float(value) * weight
        return total
