"""End-to-end VPCM report types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from vpcm_baselines.baseline_report import BaselineReport
from vpcm_biomarker.types import OrganBiomarkerReport, PseudoBulkProjection
from vpcm_conformal.types import PredictionIntervals
from vpcm_core.types import JSONValue
from vpcm_mechanism.types import (
    CommunicationReport,
    GRNSimulationReport,
    PathwayReport,
)
from vpcm_outcome.types import (
    CompetingRiskPrediction,
    ResponsePrediction,
    SurvivalPrediction,
)
from vpcm_perturbation.ensemble import EnsemblePrediction

Vector = list[float]


@dataclass(frozen=True)
class VPCMReport:
    """Signed end-to-end prediction report."""

    patient_hash: str
    patient_id: str
    intervention: dict[str, JSONValue]
    delta: Vector
    interval_cqr: PredictionIntervals
    interval_mondrian: PredictionIntervals
    ensemble_prediction: EnsemblePrediction
    mechanism: PathwayReport
    grn: GRNSimulationReport
    comms: CommunicationReport
    pseudo_bulk: PseudoBulkProjection
    biomarkers: OrganBiomarkerReport
    tme_state: dict[str, JSONValue]
    survival: SurvivalPrediction
    competing_risks: CompetingRiskPrediction
    responder: ResponsePrediction
    baseline_report: BaselineReport
    refusal_flag: bool
    provenance: dict[str, JSONValue]
    signed: bool = True

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a deterministic JSON-compatible report payload."""

        return cast(dict[str, JSONValue], {
            "patient_hash": self.patient_hash,
            "patient_id": self.patient_id,
            "intervention": self.intervention,
            "delta": self.delta,
            "interval_cqr": {
                "lo": self.interval_cqr.lo,
                "hi": self.interval_cqr.hi,
            },
            "interval_mondrian": {
                "lo": self.interval_mondrian.lo,
                "hi": self.interval_mondrian.hi,
            },
            "ensemble_prediction": self.ensemble_prediction.to_dict(),
            "mechanism": {
                "pathway_hits": [
                    hit.to_dict() for hit in self.mechanism.pathway_hits
                ],
                "tf_activities": [
                    tf.to_dict() for tf in self.mechanism.tf_activities
                ],
                "databases": self.mechanism.databases,
            },
            "grn": {
                "spearman_concordance": self.grn.spearman_concordance,
                "upstream_regulators": self.grn.upstream_regulators,
                "caveat": self.grn.caveat,
            },
            "comms": {
                "interactions": [
                    interaction.to_dict()
                    for interaction in self.comms.interactions
                ],
                "tools": self.comms.tools,
                "caveat": self.comms.caveat,
            },
            "pseudo_bulk": {
                "gene_ids": self.pseudo_bulk.gene_ids,
                "pseudo_bulk_delta": self.pseudo_bulk.pseudo_bulk_delta,
                "normalized_proportions": self.pseudo_bulk.normalized_proportions,
                "method_trace": self.pseudo_bulk.method_trace,
            },
            "biomarkers": {
                "organ": self.biomarkers.organ,
                "predictions": [
                    prediction.to_dict()
                    for prediction in self.biomarkers.predictions
                ],
                "pearson_benchmark": self.biomarkers.pearson_benchmark,
                "method_trace": self.biomarkers.method_trace,
            },
            "tme_state": self.tme_state,
            "survival": self.survival.to_dict(),
            "competing_risks": self.competing_risks.to_dict(),
            "responder": self.responder.to_dict(),
            "baseline_report": self.baseline_report.to_dict(),
            "refusal_flag": self.refusal_flag,
            "provenance": self.provenance,
            "signed": self.signed,
        })

    def to_signed_json(self) -> str:
        """Return deterministic Ed25519-signed JSON."""

        from vpcm_pipeline.report_generator import SignedReportBundle

        return SignedReportBundle().sign_json(self.to_dict())

