"""Signed JSON and PDF-like report bundle generation."""

from __future__ import annotations

import base64
import importlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, Optional, Protocol, cast

from vpcm_core.provenance import ProvenanceTracker
from vpcm_core.types import JSONValue

from vpcm_pipeline.types import VPCMReport


class _PublicKey(Protocol):
    def verify(self, signature: bytes, data: bytes) -> None:
        ...

    def public_bytes(self, encoding: object, public_format: object) -> bytes:
        ...


class _PrivateKey(Protocol):
    def sign(self, data: bytes) -> bytes:
        ...

    def public_key(self) -> _PublicKey:
        ...


def _deterministic_private_key() -> _PrivateKey:
    ed25519 = importlib.import_module(
        "cryptography.hazmat.primitives.asymmetric.ed25519"
    )
    private_bytes = bytes.fromhex(
        "46cc2eb9c37605591fc5ba7d5ddca48fd1b21a1ae0564fbcd8cbf7f0d6f842bb"
    )
    return cast(
        _PrivateKey,
        ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes),
    )


def _raw_public_bytes(public_key: _PublicKey) -> bytes:
    serialization = importlib.import_module(
        "cryptography.hazmat.primitives.serialization"
    )
    return public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )


class SignedReportBundle:
    """Create and verify deterministic Ed25519 report signatures."""

    def __init__(self, signing_key: Optional[_PrivateKey] = None) -> None:
        self.signing_key = signing_key or _deterministic_private_key()

    def sign(self, payload: Mapping[str, JSONValue]) -> dict[str, JSONValue]:
        """Return signed JSON-compatible report bundle."""

        payload_dict = dict(payload)
        payload_bytes = _canonical_json(cast(Mapping[str, object], payload_dict))
        signature = self.signing_key.sign(payload_bytes)
        public_key = self.signing_key.public_key()
        payload_hash = ProvenanceTracker.patient_hash_bytes(payload_bytes)
        return cast(dict[str, JSONValue], {
            "payload": payload_dict,
            "payload_hash": payload_hash,
            "signature": {
                "algorithm": "Ed25519",
                "public_key": base64.b64encode(
                    _raw_public_bytes(public_key)
                ).decode("ascii"),
                "value": base64.b64encode(signature).decode("ascii"),
            },
        })

    def sign_json(self, payload: Mapping[str, JSONValue]) -> str:
        """Return sorted signed report JSON."""

        return json.dumps(self.sign(payload), sort_keys=True)

    @staticmethod
    def verify_json(signed_json: str) -> bool:
        """Verify a signed report JSON payload."""

        signed = json.loads(signed_json)
        payload = cast(Mapping[str, object], signed["payload"])
        expected_hash = ProvenanceTracker.patient_hash_bytes(_canonical_json(payload))
        if signed.get("payload_hash") != expected_hash:
            return False
        signature = signed["signature"]
        public_bytes = base64.b64decode(signature["public_key"])
        signature_bytes = base64.b64decode(signature["value"])
        ed25519 = importlib.import_module(
            "cryptography.hazmat.primitives.asymmetric.ed25519"
        )
        public_key = cast(
            _PublicKey,
            ed25519.Ed25519PublicKey.from_public_bytes(public_bytes),
        )
        try:
            public_key.verify(signature_bytes, _canonical_json(payload))
        except Exception:
            return False
        return True


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class VPCMReportGenerator:
    """Generate signed JSON, PDF-like report, audit, and provenance files."""

    sections: ClassVar[list[str]] = [
        "Cover page",
        "Section A: Predicted delta-expression per cell type + intervals",
        "Section B: Mechanism",
        "Section C: Biomarker projection",
        "Section D: TME state classification",
        "Section E: Outcome prediction",
        "Section F: Beat-the-mean and beat-ridge deltas",
        "Section G: Refusal status and reasoning trace",
        "Section H: Provenance",
        "Appendix: V&V40 conformance summary",
    ]

    def __init__(self, signer: Optional[SignedReportBundle] = None) -> None:
        self.signer = signer or SignedReportBundle()

    def generate_bundle(self, report: VPCMReport, output_dir: Path) -> dict[str, str]:
        """Write report.json, report.pdf, audit.jsonl, and provenance.yaml."""

        output_dir.mkdir(parents=True, exist_ok=True)
        signed_json = self.signer.sign_json(report.to_dict())
        json_path = output_dir / "report.json"
        pdf_path = output_dir / "report.pdf"
        audit_path = output_dir / "audit.jsonl"
        provenance_path = output_dir / "provenance.yaml"
        json_path.write_text(signed_json + "\n", encoding="utf-8")
        pdf_path.write_text(self.render_pdf_text(report), encoding="utf-8")
        audit_path.write_text(signed_json + "\n", encoding="utf-8")
        provenance_path.write_text(self._provenance_yaml(report), encoding="utf-8")
        return {
            "report_json": str(json_path),
            "report_pdf": str(pdf_path),
            "audit_jsonl": str(audit_path),
            "provenance_yaml": str(provenance_path),
        }

    def render_pdf_text(self, report: VPCMReport) -> str:
        """Return a deterministic human-readable report body."""

        lines = ["%PDF-1.4", "VPCM signed prediction report"]
        lines.extend(self.sections)
        lines.append(f"patient_hash: {report.patient_hash}")
        lines.append(f"intervention: {report.intervention}")
        lines.append(
            "beat_mean_delta: "
            f"{report.baseline_report.beat_mean_delta:.6f}; "
            "beat_ridge_delta: "
            f"{report.baseline_report.beat_ridge_delta:.6f}"
        )
        lines.append("Csendes 2024 and Ahlmann-Eltze 2025 baseline caveat included.")
        return "\n".join(lines) + "\n"

    def _provenance_yaml(self, report: VPCMReport) -> str:
        lines = [
            f"patient_hash: {report.patient_hash}",
            "code_commit_sha: unknown",
            "model_versions:",
            "  foundation_model: phase6-fixture",
            "  perturbation_predictor: ensemble-fixture",
            f"signed: {report.signed}",
        ]
        return "\n".join(lines) + "\n"
