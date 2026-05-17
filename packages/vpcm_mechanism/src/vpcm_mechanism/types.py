"""Typed report surfaces for Phase 5 mechanism interpretation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from vpcm_core.types import JSONValue, PredictionOutput

Vector = list[float]

ATTENTION_CAUSALITY_CAVEAT = (
    "Attention attribution is correlational: scGPT/Geneformer-style attention "
    "can encode co-expression rather than causation. VPCM requires "
    "cross-validation against perturbational, GRN, pathway, or MR evidence."
)

GRN_CAVEAT = (
    "CellOracle-style GRN propagation is prior-network constrained and remains "
    "correlational unless paired with experimental validation."
)


@dataclass(frozen=True)
class PathwayHit:
    """One pathway projection hit."""

    name: str
    source: str
    z_score: float
    fdr: float
    direction: str
    contributing_genes: list[str]

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "name": self.name,
            "source": self.source,
            "z_score": self.z_score,
            "fdr": self.fdr,
            "direction": self.direction,
            "contributing_genes": self.contributing_genes,
        })


@dataclass(frozen=True)
class TFActivity:
    """One DoRothEA-style transcription-factor activity."""

    tf: str
    z_score: float
    fdr: float
    direction: str
    target_genes: list[str]

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "tf": self.tf,
            "z_score": self.z_score,
            "fdr": self.fdr,
            "direction": self.direction,
            "target_genes": self.target_genes,
        })


@dataclass(frozen=True)
class PathwayReport:
    """Pathway and TF projection report for one cell type."""

    cell_type: str
    method: str
    pathway_hits: list[PathwayHit]
    tf_activities: list[TFActivity]
    databases: list[str]

    def to_audit_output(self) -> PredictionOutput:
        """Summarize pathway projection for the audit log."""

        top_pathway = self.pathway_hits[0].name if self.pathway_hits else "none"
        top_tf = self.tf_activities[0].tf if self.tf_activities else "none"
        return {
            "mechanism_summary": (
                f"MoA projection for {self.cell_type} via {self.method}: "
                f"top pathway={top_pathway}, top TF={top_tf}; databases="
                f"{','.join(self.databases)}."
            ),
            "biomarkers": [hit.name for hit in self.pathway_hits[:5]],
        }


@dataclass(frozen=True)
class GRNSimulationReport:
    """GRN propagation cross-validation report."""

    intervention_label: str
    predicted_delta: Vector
    simulated_delta: Vector
    spearman_concordance: float
    upstream_regulators: list[str]
    caveat: str = GRN_CAVEAT

    def to_audit_output(self) -> PredictionOutput:
        """Summarize GRN simulation for the audit log."""

        return {
            "mechanism_summary": (
                f"CellOracle-style GRN simulation for {self.intervention_label}: "
                f"Spearman concordance={self.spearman_concordance:.3f}; "
                f"upstream regulators={','.join(self.upstream_regulators[:5])}. "
                f"{self.caveat}"
            )
        }


@dataclass(frozen=True)
class CommunicationChange:
    """One inferred ligand-receptor communication change."""

    sender: str
    receiver: str
    ligand: str
    receptor: str
    pathway: str
    probability_delta: float

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "sender": self.sender,
            "receiver": self.receiver,
            "ligand": self.ligand,
            "receptor": self.receptor,
            "pathway": self.pathway,
            "probability_delta": self.probability_delta,
        })


@dataclass(frozen=True)
class CommunicationReport:
    """Cell-cell communication report."""

    interactions: list[CommunicationChange]
    tools: list[str]
    caveat: str

    def to_audit_output(self) -> PredictionOutput:
        """Summarize communication inference for the audit log."""

        top = self.interactions[0] if self.interactions else None
        top_summary = (
            f"{top.sender}->{top.receiver}:{top.ligand}-{top.receptor}"
            if top is not None
            else "none"
        )
        return {
            "mechanism_summary": (
                f"Communication projection via {','.join(self.tools)}: "
                f"top interaction={top_summary}. {self.caveat}"
            )
        }


@dataclass(frozen=True)
class AttentionAttribution:
    """One attention-derived gene attribution with mandatory caveat."""

    gene_id: str
    importance: float
    rank: int
    caveat: str = ATTENTION_CAUSALITY_CAVEAT

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "gene_id": self.gene_id,
            "importance": self.importance,
            "rank": self.rank,
            "caveat": self.caveat,
        })


@dataclass(frozen=True)
class AttentionReport:
    """Attention attribution report with global caveat."""

    model_name: str
    attributions: list[AttentionAttribution]
    caveat: str = ATTENTION_CAUSALITY_CAVEAT

    def to_audit_output(self) -> PredictionOutput:
        """Summarize attention attribution for the audit log."""

        genes = ",".join(attribution.gene_id for attribution in self.attributions[:5])
        return {
            "mechanism_summary": (
                f"Attention attribution for {self.model_name}: top genes={genes}. "
                f"{self.caveat}"
            )
        }
