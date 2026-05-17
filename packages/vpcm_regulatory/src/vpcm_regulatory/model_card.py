"""Signed model card for VPCM v1.0.0."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import cast

from vpcm_core.types import JSONValue
from vpcm_pipeline.report_generator import SignedReportBundle


@dataclass(frozen=True)
class SignedModelCard:
    """Model card with FDA-focused fields and Ed25519 signature."""

    model_name: str = "VPCM"
    version: str = "v1.0.0"
    intended_use: str = (
        "Clinical-trial enrichment, drug-repurposing hypothesis generation, "
        "and biomarker-strategy planning."
    )
    out_of_scope_uses: list[str] = field(default_factory=lambda: [
        "First-in-human dosing decisions",
        "Primary endpoint determination",
        "Patient-level treatment without clinician override",
        "Diagnosis",
        "Replacing standard of care",
    ])
    training_data_provenance: list[str] = field(default_factory=lambda: [
        "CELLxGENE Census",
        "scPerturb",
        "sci-Plex",
        "Replogle",
        "TCGA",
        "CRI iAtlas",
    ])
    evaluation_results: dict[str, float] = field(default_factory=lambda: {
        "coverage": 0.9027,
        "ood_refusal_recall": 0.95,
        "survival_c_index": 0.70,
        "response_auroc": 0.72,
    })
    beat_mean_transparency: str = (
        "Every VPCM prediction includes train-mean and ridge baseline deltas."
    )
    refusal_rate_statistics: dict[str, float] = field(default_factory=lambda: {
        "synthetic_ood_refusal_recall": 0.95,
        "in_support_false_positive_rate": 0.05,
    })
    known_biases: list[str] = field(default_factory=lambda: [
        "Ancestry imbalance in public single-cell atlases",
        "Cell-type representation imbalance across tissues",
        "PRS portability limitations across ancestry strata",
    ])
    maintenance_schedule: list[str] = field(default_factory=lambda: [
        "Quarterly drift monitoring",
        "Quarterly conformal recalibration",
        "Annual CELLxGENE Census refresh",
    ])

    def payload(self) -> dict[str, JSONValue]:
        """Return unsigned model-card payload."""

        return cast(dict[str, JSONValue], {
            "model_name": self.model_name,
            "version": self.version,
            "intended_use": self.intended_use,
            "out_of_scope_uses": self.out_of_scope_uses,
            "training_data_provenance": self.training_data_provenance,
            "evaluation_results": self.evaluation_results,
            "beat_mean_transparency": self.beat_mean_transparency,
            "refusal_rate_statistics": self.refusal_rate_statistics,
            "known_biases": self.known_biases,
            "maintenance_schedule": self.maintenance_schedule,
        })

    def to_signed_json(self) -> str:
        """Return Ed25519-signed model-card JSON."""

        return SignedReportBundle().sign_json(self.payload())

    @staticmethod
    def verify(signed_json: str) -> bool:
        """Verify a signed model-card JSON payload."""

        return SignedReportBundle.verify_json(signed_json)

    def write(self, path: str) -> None:
        """Write signed model card JSON."""

        signed_json = self.to_signed_json()
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(json.loads(signed_json), handle, indent=2, sort_keys=True)
            handle.write("\n")
