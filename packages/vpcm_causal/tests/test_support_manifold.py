from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vpcm_causal.refusal_report import DO_CALCULUS_NOTE
from vpcm_causal.support_manifold import InterventionalSupportManifold
from vpcm_core.logging import AuditLogger
from vpcm_core.provenance import ProvenanceTracker
from vpcm_data.base import make_fixture_adata
from vpcm_models.loaders import FoundationModelEnsemble


class SupportManifoldTest(unittest.TestCase):
    def _manifold(self) -> InterventionalSupportManifold:
        fm = FoundationModelEnsemble(device="cpu", dtype="bfloat16")
        manifold = InterventionalSupportManifold(fm)
        manifold.build_manifold(
            scperturb_adata=make_fixture_adata(
                "scperturb_support",
                n_obs=2,
                n_vars=3,
                perturbation="TP53",
            ),
            sci_plex_adata=make_fixture_adata(
                "sci_plex_support",
                n_obs=2,
                n_vars=3,
                perturbation="CHEMBL25",
            ),
            tahoe_adata=make_fixture_adata(
                "tahoe_support",
                n_obs=2,
                n_vars=3,
                perturbation="CHEMBL1201585",
            ),
            lincs_profiles=[[0.1, 0.2, 0.3]],
        )
        return manifold

    def test_manifold_builds_and_calibrates_tau(self) -> None:
        manifold = self._manifold()
        in_support = make_fixture_adata(
            "scperturb_support",
            n_obs=2,
            n_vars=3,
            perturbation="TP53",
        )
        ood = make_fixture_adata(
            "synthetic_ood",
            n_obs=2,
            n_vars=3,
            perturbation="RANDOM_GENE+UNSEEN_DRUG",
        )

        tau = manifold.calibrate_tau(in_support, ood)

        self.assertGreaterEqual(manifold.calibration_recall, 0.95)
        self.assertLessEqual(manifold.calibration_fpr, 0.05)
        self.assertGreaterEqual(tau, 0.0)

    def test_support_check_and_refusal_report_include_pearl_note(self) -> None:
        manifold = self._manifold()
        in_support = make_fixture_adata(
            "scperturb_support",
            n_obs=2,
            n_vars=3,
            perturbation="TP53",
        )
        ood = make_fixture_adata(
            "synthetic_ood",
            n_obs=1,
            n_vars=3,
            perturbation="UNSEEN",
        )
        manifold.calibrate_tau(in_support, ood)

        in_support_embedding = manifold.embed_adata(in_support)[0]
        ood_embedding = manifold.embed_adata(ood)[0]
        pass_check = manifold.check_support(
            in_support_embedding,
            {"intervention_type": "genetic", "target": "TP53"},
        )
        refusal_check = manifold.check_support(
            ood_embedding,
            {"intervention_type": "combination", "target": "UNSEEN"},
        )
        report = refusal_check.require_report(
            ood_embedding,
            {"intervention_type": "combination", "target": "UNSEEN"},
        )

        self.assertTrue(pass_check.in_support)
        self.assertFalse(refusal_check.in_support)
        self.assertIn("Mahalanobis", report.reason)
        self.assertIn("Pearl", report.do_calculus_note)
        self.assertIn("Perturb-seq", report.suggested_data)
        self.assertEqual(report.do_calculus_note, DO_CALCULUS_NOTE)

    def test_audit_log_captures_refusal_reasoning_trace(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        manifold = self._manifold()
        ood = make_fixture_adata("synthetic_ood", n_obs=1, n_vars=3)
        manifold.calibrate_tau(
            make_fixture_adata("scperturb_support", n_obs=1, n_vars=3),
            ood,
        )
        ood_embedding = manifold.embed_adata(ood)[0]
        check = manifold.check_support(
            ood_embedding,
            {"intervention_type": "drug", "target": "UNSEEN"},
        )
        report = check.require_report(
            ood_embedding,
            {"intervention_type": "drug", "target": "UNSEEN"},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")
            logger.log_prediction(
                patient_hash=ProvenanceTracker.patient_hash_bytes(b"patient"),
                intervention={"intervention_type": "drug", "target": "UNSEEN"},
                model_versions={"causal_gate": "support-manifold-fixture"},
                output=report.to_audit_output(),
                refusal_flag=True,
                beat_mean_delta=0.0,
                conformal_coverage=0.0,
            )
            entry = logger.read_entries()[0]

        self.assertTrue(AuditLogger.verify_entry(entry))
        output = entry.get("output", {})
        self.assertTrue(entry.get("refusal_flag"))
        self.assertIn("REFUSAL", output.get("mechanism_summary", ""))


if __name__ == "__main__":
    unittest.main()
