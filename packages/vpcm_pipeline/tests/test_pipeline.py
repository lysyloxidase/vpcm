from __future__ import annotations

import asyncio
import json
import tempfile
import time
import unittest
from pathlib import Path

from vpcm_causal.refusal_report import RefusalReport
from vpcm_core.logging import AuditLogger
from vpcm_data.base import AnnDataLike, make_fixture_adata
from vpcm_pipeline.report_generator import SignedReportBundle, VPCMReportGenerator
from vpcm_pipeline.types import VPCMReport
from vpcm_pipeline.vpcm import VPCM


def _patient() -> AnnDataLike:
    return make_fixture_adata(
        "phase6_patient",
        n_obs=8,
        n_vars=10,
        perturbation="TP53",
        extra_obs={"cell_type_label": "tumor"},
    )


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

    def test_end_to_end_predict_runs_under_latency_budget_and_audits(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vpcm = VPCM(audit_log_path=Path(tmpdir) / "audit.jsonl")
            start = time.perf_counter()

            report = vpcm.predict(
                patient_h5ad=_patient(),
                intervention={"intervention_type": "genetic", "target": "TP53"},
                patient_id="patient-1",
                clinical_covariates={"age": 61, "stage": "III"},
                fit_lora=False,
            )
            elapsed = time.perf_counter() - start

            if not isinstance(report, VPCMReport):
                self.fail("Expected VPCMReport")
            self.assertLess(elapsed, 60.0)
            self.assertGreater(
                report.baseline_report.beat_mean_delta,
                0.0,
            )
            entries = vpcm.audit_logger.read_entries()

        self.assertEqual(len(entries), 1)
        self.assertTrue(AuditLogger.verify_entry(entries[0]))

    def test_signed_report_roundtrips_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vpcm = VPCM(audit_log_path=Path(tmpdir) / "audit.jsonl")

            first = vpcm.predict(
                _patient(),
                {"intervention_type": "genetic", "target": "TP53"},
                "patient-1",
                {"age": 61},
                fit_lora=False,
            )
            second = vpcm.predict(
                _patient(),
                {"intervention_type": "genetic", "target": "TP53"},
                "patient-1",
                {"age": 61},
                fit_lora=False,
            )

        self.assertIsInstance(first, VPCMReport)
        self.assertIsInstance(second, VPCMReport)
        first_json = first.to_signed_json() if isinstance(first, VPCMReport) else ""
        second_json = second.to_signed_json() if isinstance(second, VPCMReport) else ""
        self.assertEqual(first_json, second_json)
        self.assertTrue(SignedReportBundle.verify_json(first_json))
        payload = json.loads(first_json)["payload"]
        self.assertFalse(payload["refusal_flag"])

    def test_report_bundle_contains_all_pdf_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "bundle"
            vpcm = VPCM(audit_log_path=Path(tmpdir) / "audit.jsonl")
            report = vpcm.predict(
                _patient(),
                {"intervention_type": "genetic", "target": "TP53"},
                "patient-1",
                {"age": 61},
                fit_lora=False,
            )
            self.assertIsInstance(report, VPCMReport)
            if not isinstance(report, VPCMReport):
                self.fail("Expected VPCMReport")
            bundle = VPCMReportGenerator().generate_bundle(report, output_dir)
            pdf_text = Path(bundle["report_pdf"]).read_text(encoding="utf-8")
            signed_text = Path(bundle["report_json"]).read_text(encoding="utf-8")

            for section in VPCMReportGenerator.sections:
                self.assertIn(section, pdf_text)
            self.assertIn("Section F", pdf_text)
            self.assertTrue(SignedReportBundle.verify_json(signed_text))

    def test_refusal_path_returns_refusal_report_and_audit_trace(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vpcm = VPCM(audit_log_path=Path(tmpdir) / "audit.jsonl")

            report = vpcm.predict(
                patient_h5ad=_patient(),
                intervention={
                    "intervention_type": "combination",
                    "target": "UNSEEN_DRUG+UNSEEN_GENE",
                    "metadata": {"synthetic_ood": True},
                },
                patient_id="patient-ood",
                clinical_covariates={"age": 61},
                fit_lora=False,
            )
            entries = vpcm.audit_logger.read_entries()

        self.assertIsInstance(report, RefusalReport)
        self.assertEqual(len(entries), 1)
        self.assertTrue(entries[0].get("refusal_flag"))
        output = entries[0].get("output", {})
        self.assertIn("REFUSAL", str(output.get("mechanism_summary", "")))

    def test_fastapi_predict_handles_10_concurrent_fixture_requests(self) -> None:
        from apps.api.main import predict

        async def run_many() -> list[str]:
            tasks = [
                predict(
                    patient_h5ad_path=f"/tmp/patient_{index}.h5ad",
                    intervention={"intervention_type": "drug", "target": "TP53"},
                    patient_id=f"patient-{index}",
                    clinical_covariates={"age": 50 + index},
                    alpha=0.1,
                )
                for index in range(10)
            ]
            return await asyncio.gather(*tasks)

        results = asyncio.run(run_many())

        self.assertEqual(len(results), 10)
        self.assertTrue(
            all(SignedReportBundle.verify_json(result) for result in results)
        )


if __name__ == "__main__":
    unittest.main()
