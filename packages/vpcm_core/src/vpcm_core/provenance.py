"""Provenance helpers for LaminDB and DVC-backed data artifacts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from vpcm_core.types import JSONValue


@dataclass(frozen=True)
class DVCArtifact:
    """DVC artifact identity captured in provenance manifests."""

    path: str
    hash_value: str
    remote: str = "local"


@dataclass(frozen=True)
class ProvenanceRecord:
    """Single dataset or model provenance record."""

    record_id: str
    resource_id: str
    source_uri: str
    version: str
    created_at: str
    metadata: dict[str, JSONValue] = field(default_factory=dict[str, JSONValue])
    dvc_artifacts: list[DVCArtifact] = field(default_factory=list[DVCArtifact])


class ProvenanceTracker:
    """Small LaminDB/DVC facade used by Phase 1 tests and manifests."""

    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        self.records: dict[str, ProvenanceRecord] = {}

    @staticmethod
    def patient_hash_bytes(contents: bytes) -> str:
        """Return the stable HIPAA-safe SHA-256 hash for patient h5ad bytes."""

        return hashlib.sha256(contents).hexdigest()

    @staticmethod
    def hash_file(path: Path) -> str:
        """Hash a file in chunks for deterministic artifact identity."""

        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def record_dataset(
        self,
        resource_id: str,
        source_uri: str,
        version: str,
        metadata: Optional[dict[str, JSONValue]] = None,
        dvc_artifacts: Optional[list[DVCArtifact]] = None,
    ) -> ProvenanceRecord:
        """Record dataset provenance for a harmonized artifact."""

        record = ProvenanceRecord(
            record_id=f"{resource_id}:{version}",
            resource_id=resource_id,
            source_uri=source_uri,
            version=version,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {},
            dvc_artifacts=dvc_artifacts or [],
        )
        self.records[record.record_id] = record
        return record

    def write_manifest(self) -> None:
        """Persist a JSON manifest consumable by LaminDB/DVC tooling."""

        payload = {
            "records": [asdict(record) for record in self.records.values()],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def load_manifest(self) -> dict[str, ProvenanceRecord]:
        """Load records from a manifest written by :meth:`write_manifest`."""

        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        loaded: dict[str, ProvenanceRecord] = {}
        for item in payload.get("records", []):
            artifact_items = item.get("dvc_artifacts", [])
            artifacts = [DVCArtifact(**artifact) for artifact in artifact_items]
            record = ProvenanceRecord(
                record_id=item["record_id"],
                resource_id=item["resource_id"],
                source_uri=item["source_uri"],
                version=item["version"],
                created_at=item["created_at"],
                metadata=item.get("metadata", {}),
                dvc_artifacts=artifacts,
            )
            loaded[record.record_id] = record
        self.records = loaded
        return loaded
