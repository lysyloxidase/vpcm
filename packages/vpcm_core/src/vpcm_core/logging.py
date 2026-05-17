"""21 CFR Part 11 audit logger for VPCM predictions."""

from __future__ import annotations

import base64
import hashlib
import importlib
import json
import re
import uuid
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol, cast

from vpcm_core.types import AuditLogEntry, Intervention, ModelVersions, PredictionOutput


class AuditSigningUnavailableError(RuntimeError):
    """Raised when Ed25519 signing is requested without cryptography installed."""


class _Ed25519PublicKey(Protocol):
    def verify(self, signature: bytes, data: bytes) -> None:
        ...

    def public_bytes(self, encoding: Any, public_format: Any) -> bytes:
        ...


class _Ed25519PrivateKey(Protocol):
    def sign(self, data: bytes) -> bytes:
        ...

    def public_key(self) -> _Ed25519PublicKey:
        ...


def _cryptography_module(module_name: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise AuditSigningUnavailableError(
            "Ed25519 audit signing requires the 'cryptography' package."
        ) from exc


def _raw_public_bytes(public_key: _Ed25519PublicKey) -> bytes:
    serialization = _cryptography_module("cryptography.hazmat.primitives.serialization")
    encoding = serialization.Encoding.Raw
    public_format = serialization.PublicFormat.Raw
    return public_key.public_bytes(encoding, public_format)


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _hash_payload(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_json(payload)).hexdigest()


class AuditLogger:
    """21 CFR Part 11 compliant audit log for every VPCM prediction.

    Every electronic record captures who, what, when, why, how, and with what.
    Records are signed with Ed25519 and appended as JSON Lines for immutable
    storage or downstream ETCD ingestion.
    """

    _PATIENT_HASH_RE = re.compile(r"^[0-9a-f]{64}$")

    def __init__(
        self,
        log_path: Path,
        signing_key: Optional[_Ed25519PrivateKey] = None,
        service_identity: str = "vpcm-phase1-service",
        purpose: str = "clinical-trial enrichment / patient-stratification tool",
        code_commit_sha: str = "unknown",
        data_version: str = "phase1-fixture",
        dvc_hash: str = "untracked",
    ) -> None:
        self.log_path = log_path
        self.signing_key = signing_key or self.generate_signing_key()
        self.service_identity = service_identity
        self.purpose = purpose
        self.code_commit_sha = code_commit_sha
        self.data_version = data_version
        self.dvc_hash = dvc_hash

    @staticmethod
    def signing_available() -> bool:
        """Return whether Ed25519 signing dependencies are installed."""

        try:
            importlib.import_module("cryptography.hazmat.primitives.asymmetric.ed25519")
        except ImportError:
            return False
        return True

    @staticmethod
    def generate_signing_key() -> _Ed25519PrivateKey:
        """Generate an Ed25519 private key."""

        ed25519 = _cryptography_module(
            "cryptography.hazmat.primitives.asymmetric.ed25519"
        )
        private_key_class = ed25519.Ed25519PrivateKey
        return cast(_Ed25519PrivateKey, private_key_class.generate())

    def log_prediction(
        self,
        patient_hash: str,
        intervention: Intervention,
        model_versions: ModelVersions,
        output: PredictionOutput,
        refusal_flag: bool,
        beat_mean_delta: float,
        conformal_coverage: float,
    ) -> str:
        """Append and sign a prediction record, returning its UUID."""

        if not self._PATIENT_HASH_RE.fullmatch(patient_hash):
            raise ValueError("patient_hash must be a lowercase SHA-256 hex digest.")

        entry_uuid = str(uuid.uuid4())
        entry: AuditLogEntry = {
            "entry_uuid": entry_uuid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_identity": self.service_identity,
            "patient_hash": patient_hash,
            "intervention": intervention,
            "model_versions": model_versions,
            "output": output,
            "refusal_flag": refusal_flag,
            "beat_mean_delta": beat_mean_delta,
            "conformal_coverage": conformal_coverage,
            "purpose": self.purpose,
            "code_commit_sha": self.code_commit_sha,
            "data_version": self.data_version,
            "dvc_hash": self.dvc_hash,
        }
        entry_hash = _hash_payload(cast(Mapping[str, object], entry))
        entry["entry_hash"] = entry_hash
        signature_bytes = self.signing_key.sign(
            _canonical_json(cast(Mapping[str, object], entry))
        )
        public_key = self.signing_key.public_key()
        entry["signature"] = {
            "algorithm": "Ed25519",
            "public_key": base64.b64encode(_raw_public_bytes(public_key)).decode(
                "ascii"
            ),
            "value": base64.b64encode(signature_bytes).decode("ascii"),
        }

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry_uuid

    @staticmethod
    def verify_entry(entry: AuditLogEntry) -> bool:
        """Verify an audit log entry signature and content hash."""

        signature = entry.get("signature")
        entry_hash = entry.get("entry_hash")
        if signature is None or entry_hash is None:
            return False

        unsigned_entry = dict(entry)
        unsigned_entry.pop("signature", None)
        expected_hash_entry = dict(unsigned_entry)
        expected_hash_entry.pop("entry_hash", None)
        if _hash_payload(expected_hash_entry) != entry_hash:
            return False

        public_key_bytes = base64.b64decode(signature["public_key"])
        signature_bytes = base64.b64decode(signature["value"])
        ed25519 = _cryptography_module(
            "cryptography.hazmat.primitives.asymmetric.ed25519"
        )
        public_key_class = ed25519.Ed25519PublicKey
        public_key = cast(
            _Ed25519PublicKey,
            public_key_class.from_public_bytes(public_key_bytes),
        )
        try:
            public_key.verify(signature_bytes, _canonical_json(unsigned_entry))
        except Exception:
            return False
        return True

    def read_entries(self) -> list[AuditLogEntry]:
        """Read JSONL entries from the audit log."""

        if not self.log_path.exists():
            return []
        entries: list[AuditLogEntry] = []
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            entries.append(cast(AuditLogEntry, json.loads(line)))
        return entries
