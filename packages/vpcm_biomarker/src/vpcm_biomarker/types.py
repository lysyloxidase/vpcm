"""Typed report surfaces for Phase 5 biomarker projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from vpcm_core.types import JSONValue, PredictionOutput

Vector = list[float]


@dataclass(frozen=True)
class PseudoBulkProjection:
    """Cell-type deconvolution weighted pseudo-bulk projection."""

    gene_ids: list[str]
    pseudo_bulk_delta: Vector
    normalized_proportions: dict[str, float]
    method_trace: list[str]
    newman_2019_error_pct: float

    def to_audit_output(self) -> PredictionOutput:
        """Summarize pseudo-bulk projection for the audit log."""

        return {
            "mechanism_summary": (
                "CIBERSORTx-style pseudo-bulk projection: "
                f"n_genes={len(self.gene_ids)}, "
                f"Newman2019 fixture error={self.newman_2019_error_pct:.2f}%."
            )
        }


@dataclass(frozen=True)
class LabValuePrediction:
    """One projected clinical lab value."""

    name: str
    value: float
    unit: str
    direction: str
    contributing_genes: list[str]

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "direction": self.direction,
            "contributing_genes": self.contributing_genes,
        })


@dataclass(frozen=True)
class OrganBiomarkerReport:
    """Per-organ ridge projection report."""

    organ: str
    predictions: list[LabValuePrediction]
    pearson_benchmark: float
    method_trace: list[str]

    def to_audit_output(self) -> PredictionOutput:
        """Summarize organ projection for the audit log."""

        labs = [prediction.name for prediction in self.predictions]
        return {
            "mechanism_summary": (
                f"Organ ridge projection for {self.organ}: labs={','.join(labs)}; "
                f"held-out Pearson fixture={self.pearson_benchmark:.2f}."
            ),
            "biomarkers": labs,
        }


@dataclass(frozen=True)
class TCRRepertoireReport:
    """Optional TCR-seq integration report."""

    available: bool
    clonality: float
    expansion_delta: float
    top_clonotypes: list[str]
    tools: list[str]

    def to_audit_output(self) -> PredictionOutput:
        """Summarize TCR integration for the audit log."""

        status = "available" if self.available else "missing"
        return {
            "mechanism_summary": (
                f"TCR repertoire integration {status}: clonality={self.clonality:.3f}, "
                f"expansion_delta={self.expansion_delta:.3f}; "
                f"tools={','.join(self.tools)}."
            )
        }


@dataclass(frozen=True)
class SpatialIntegrationReport:
    """Optional spatial transcriptomics integration report."""

    available: bool
    platform: str
    spatial_context_score: float
    infiltration_gradient: float
    tools: list[str]
    caveat: str

    def to_audit_output(self) -> PredictionOutput:
        """Summarize spatial integration for the audit log."""

        return {
            "mechanism_summary": (
                f"Spatial integration for {self.platform}: "
                f"context_score={self.spatial_context_score:.3f}, "
                f"infiltration_gradient={self.infiltration_gradient:.3f}; "
                f"tools={','.join(self.tools)}. {self.caveat}"
            )
        }
