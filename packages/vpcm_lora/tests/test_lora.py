from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import cast

from vpcm_core.logging import AuditLogger
from vpcm_data.base import AnnDataLike
from vpcm_lora.patient_embedding import PatientCovariateEncoder
from vpcm_lora.patient_lora import PatientLoRATrainer
from vpcm_lora.scimilarity_retrieval import AtlasNeighborRetrieval
from vpcm_models.loaders import FoundationModelEnsemble


def _adata(n_obs: int, cell_type: str = "tumor") -> AnnDataLike:
    return AnnDataLike(
        obs=[
            {
                "cell_id": f"{cell_type}_{index}",
                "cell_type_label": cell_type,
                "patient_id": "patient-1",
            }
            for index in range(n_obs)
        ],
        var_names=["ENSG00000000001", "ENSG00000000002"],
        x_shape=(n_obs, 2),
        x=[[1.0 + index * 0.0001, 2.0 + index * 0.0001] for index in range(n_obs)],
    )


class LoRATest(unittest.TestCase):
    def test_atlas_retrieval_returns_top_k_neighbors(self) -> None:
        patient = _adata(10)
        atlas = _adata(100)
        retrieval = AtlasNeighborRetrieval(default_k=50_000)

        neighbors = retrieval.retrieve(patient, atlas, k=25)

        self.assertEqual(neighbors.n_obs, 25)
        self.assertEqual(neighbors.uns["retrieval"], "scimilarity_sctab_fixture")

    def test_lora_trainer_handles_5000_patient_cells_and_50k_neighbors(self) -> None:
        patient = _adata(5_000)
        atlas = _adata(50_000)
        trainer = PatientLoRATrainer(
            FoundationModelEnsemble(device="cpu", dtype="bfloat16"),
            rank=8,
        )

        result = trainer.fit_patient(
            patient_adata=patient,
            nn_atlas=atlas,
            patient_id="patient-1",
            max_epochs=5,
        )

        self.assertEqual(result["n_adapters"], 5)
        self.assertTrue(result["within_h100_budget"])
        self.assertLessEqual(trainer.estimate_vram_overhead_gb(), 1.0)

    def test_covariate_encoder_handles_missing_channels_and_prs_weights(self) -> None:
        encoder = PatientCovariateEncoder()
        missing = encoder.encode("patient-1", {})
        missing_channels = cast(list[str], missing["missing_channels"])

        self.assertIn("prs_weights", missing_channels)
        self.assertIn("prs_scores", missing_channels)

        encoder.load_prs_weights("EUR", {"BRCA1": 0.5, "TP53": 2.0})
        encoded = encoder.encode(
            "patient-1",
            {
                "ancestry": "EUR",
                "prs_scores": {"BRCA1": 2.0, "TP53": 3.0},
                "age": 61,
            },
        )

        self.assertEqual(encoded["weighted_prs"], 7.0)
        self.assertEqual(encoded["missing_channels"], [])
        embedding = cast(list[float], encoded["patient_id_embedding"])
        self.assertEqual(len(embedding), 64)

    def test_lora_fit_is_signed_in_audit_log(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        patient = _adata(8)
        atlas = _adata(20)
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")
            trainer = PatientLoRATrainer(
                FoundationModelEnsemble(device="cpu", dtype="bfloat16"),
                rank=8,
                audit_logger=logger,
            )

            trainer.fit_patient(patient, atlas, patient_id="patient-1")
            entries = logger.read_entries()

        self.assertEqual(len(entries), 5)
        self.assertTrue(all(AuditLogger.verify_entry(entry) for entry in entries))
        output = entries[0].get("output", {})
        self.assertIn("LoRA adapter fit", output.get("mechanism_summary", ""))


if __name__ == "__main__":
    unittest.main()
