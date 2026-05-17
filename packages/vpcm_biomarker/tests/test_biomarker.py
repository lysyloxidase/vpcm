from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import cast

from vpcm_biomarker.cibersortx import CIBERSORTxProjector
from vpcm_biomarker.organ_ridges import ORGAN_HEADS, OrganRidgeProjectors
from vpcm_biomarker.spatial_integration import SpatialTranscriptomicsIntegrator
from vpcm_biomarker.tcr_repertoire import TCRRepertoireHead
from vpcm_biomarker.tme_signatures import TMESignatureHeads
from vpcm_core.logging import AuditLogger
from vpcm_core.provenance import ProvenanceTracker


def _genes(n_genes: int = 24) -> list[str]:
    return [f"ENSG{index:011d}" for index in range(1, n_genes + 1)]


def _delta(n_genes: int = 24) -> list[float]:
    return [0.03 + index * 0.01 for index in range(n_genes)]


class BiomarkerTest(unittest.TestCase):
    def test_cibersortx_pseudobulk_and_newman_benchmark_gate(self) -> None:
        projector = CIBERSORTxProjector()
        tumor = _delta()
        immune = [value * -0.5 for value in tumor]

        projection = projector.project(
            {"tumor": tumor, "immune": immune},
            {"tumor": 0.7, "immune": 0.3},
            _genes(),
        )
        error = projector.benchmark_newman_2019(
            {"tumor": 0.69, "immune": 0.31},
            {"tumor": 0.7, "immune": 0.3},
        )

        self.assertAlmostEqual(
            projection.pseudo_bulk_delta[0],
            0.7 * tumor[0] + 0.3 * immune[0],
        )
        self.assertLessEqual(error, 5.0)
        self.assertTrue(
            projector.matches_newman_2019_within_5_percent(
                {"tumor": 0.69, "immune": 0.31},
                {"tumor": 0.7, "immune": 0.3},
            )
        )

    def test_organ_ridge_heads_project_labs_with_pearson_gate(self) -> None:
        projector = OrganRidgeProjectors()

        report = projector.predict(
            "liver",
            _delta(),
            _genes(),
            clinical_covariates={"age": 61, "stage": "III"},
        )

        self.assertEqual(
            [prediction.name for prediction in report.predictions],
            ORGAN_HEADS["liver"],
        )
        self.assertGreaterEqual(report.pearson_benchmark, 0.60)
        summary = str(report.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("Organ ridge", summary)

    def test_bagaev_exhaustion_and_ifn_gamma_quality_gates(self) -> None:
        report = TMESignatureHeads().classify_tme(_delta(), _genes())

        self.assertIn(report["bagaev_type"], {
            "Immune-Enriched-Fibrotic",
            "Immune-Enriched",
            "Fibrotic",
            "Immune-Desert",
        })
        self.assertGreaterEqual(cast(float, report["macro_f1_benchmark"]), 0.70)
        self.assertGreaterEqual(cast(float, report["exhaustion_spearman"]), 0.65)
        self.assertGreaterEqual(cast(float, report["ifn_gamma_auroc"]), 0.70)
        self.assertGreaterEqual(cast(float, report["responder_probability"]), 0.0)

    def test_tcr_and_spatial_optional_heads_handle_dummy_data(self) -> None:
        tcr = TCRRepertoireHead().integrate(
            _delta(),
            {"clonotype_A": 50.0, "clonotype_B": 25.0, "clonotype_C": 25.0},
        )
        missing_tcr = TCRRepertoireHead().integrate(_delta())
        spatial = SpatialTranscriptomicsIntegrator().integrate(
            _delta(),
            spot_coordinates=[(0.0, 0.0), (2.0, 1.0), (4.0, 3.0)],
            platform="Visium",
        )

        self.assertTrue(tcr.available)
        self.assertFalse(missing_tcr.available)
        self.assertGreater(tcr.clonality, 0.0)
        self.assertTrue(spatial.available)
        self.assertIn("squidpy", spatial.tools)

    def test_biomarker_projection_trace_is_signed_in_audit_log(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        output = OrganRidgeProjectors().predict(
            "immune_systemic",
            _delta(),
            _genes(),
        ).to_audit_output()
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")
            logger.log_prediction(
                patient_hash=ProvenanceTracker.patient_hash_bytes(b"patient"),
                intervention={"intervention_type": "drug", "target": "CHEMBL25"},
                model_versions={"foundation_model": "phase5-fixture"},
                output=output,
                refusal_flag=False,
                beat_mean_delta=0.10,
                conformal_coverage=0.9,
            )
            entry = logger.read_entries()[0]

        self.assertTrue(AuditLogger.verify_entry(entry))
        entry_output = entry.get("output", {})
        self.assertIn(
            "Organ ridge projection",
            str(entry_output.get("mechanism_summary", "")),
        )


if __name__ == "__main__":
    unittest.main()
