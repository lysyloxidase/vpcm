"""Typed regulatory report surfaces for VPCM v1.0.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from vpcm_core.types import JSONValue


@dataclass(frozen=True)
class EvidenceItem:
    """One regulatory evidence item."""

    name: str
    status: str
    evidence: str
    artifact: str

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "name": self.name,
            "status": self.status,
            "evidence": self.evidence,
            "artifact": self.artifact,
        })


@dataclass(frozen=True)
class DossierSection:
    """One ASME V&V 40 dossier dimension."""

    dimension: str
    risk_relevance: str
    evidence_items: list[EvidenceItem] = field(default_factory=list[EvidenceItem])

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "dimension": self.dimension,
            "risk_relevance": self.risk_relevance,
            "evidence_items": [
                item.to_dict() for item in self.evidence_items
            ],
        })


@dataclass(frozen=True)
class RegulatoryArtifact:
    """Generated regulatory artifact metadata."""

    path: str
    artifact_type: str
    signed: bool
    page_count: int
    validation_status: str

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "path": self.path,
            "artifact_type": self.artifact_type,
            "signed": self.signed,
            "page_count": self.page_count,
            "validation_status": self.validation_status,
        })
