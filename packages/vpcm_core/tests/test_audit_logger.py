from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vpcm_core.logging import AuditLogger
from vpcm_core.provenance import ProvenanceTracker


class AuditLoggerTest(unittest.TestCase):
    def test_prediction_entry_roundtrips_through_ed25519(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        patient_hash = ProvenanceTracker.patient_hash_bytes(b"patient")
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")

            entry_uuid = logger.log_prediction(
                patient_hash=patient_hash,
                intervention={
                    "intervention_id": "CHEMBL1201585",
                    "intervention_type": "drug",
                    "target": "EGFR",
                },
                model_versions={
                    "foundation_model": "fixture-fm",
                    "perturbation_predictor": "fixture-predictor",
                    "checkpoint_hashes": {"fixture": "sha256:abc"},
                },
                output={
                    "tumor_cell_viability_delta": -0.35,
                    "cd8_t_cell_infiltration_fold_change": 1.8,
                    "composite_pfs_months": 7.0,
                },
                refusal_flag=False,
                beat_mean_delta=0.12,
                conformal_coverage=0.91,
            )
            entries = logger.read_entries()

            self.assertEqual(entries[0].get("entry_uuid"), entry_uuid)
            self.assertTrue(AuditLogger.verify_entry(entries[0]))

    def test_invalid_hash_and_unsigned_entry_are_rejected(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")

            with self.assertRaises(ValueError):
                logger.log_prediction(
                    patient_hash="not-a-sha",
                    intervention={"intervention_type": "drug"},
                    model_versions={},
                    output={},
                    refusal_flag=True,
                    beat_mean_delta=0.0,
                    conformal_coverage=0.0,
                )

        self.assertFalse(AuditLogger.verify_entry({"entry_uuid": "unsigned"}))


if __name__ == "__main__":
    unittest.main()
