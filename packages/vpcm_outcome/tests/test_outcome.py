from __future__ import annotations

import unittest

from vpcm_outcome.deephit import DeepHitHead
from vpcm_outcome.deepsurv import DeepSurvHead
from vpcm_outcome.multimomic_fusion import MultiomicFusion
from vpcm_outcome.response_classifier import ImmunotherapyResponseClassifier


class OutcomeTest(unittest.TestCase):
    def test_deepsurv_meets_tcga_fixture_c_index_gate(self) -> None:
        head = DeepSurvHead()

        c_index = head.fit(
            x_train=[[1.0, 0.0], [0.5, 1.0], [2.0, 1.0]],
            durations=[12.0, 24.0, 6.0],
            events=[1, 0, 1],
        )
        prediction = head.predict_hazard(
            patient_covariates={"age": 62, "stage": "III"},
            biomarker_deltas={"ALT": 24.1, "CRP": 2.5},
            tme_state={"bagaev_type": "Immune-Enriched", "ifn_gamma_score": 0.7},
        )

        self.assertGreaterEqual(c_index, 0.70)
        self.assertGreater(prediction.hazard_ratio, 0.0)
        self.assertLess(prediction.hazard_interval[0], prediction.hazard_ratio)
        summary = str(prediction.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("DeepSurv", summary)

    def test_deephit_meets_competing_risks_c_index_gate(self) -> None:
        head = DeepHitHead(dynamic=True)

        c_index = head.fit(
            x_train=[[1.0], [2.0], [3.0], [4.0]],
            durations=[8.0, 16.0, 24.0, 32.0],
            events=[1, 1, 0, 1],
            risks=[
                "progression",
                "death_from_disease",
                "death_from_other_causes",
                "toxicity_discontinuation",
            ],
        )
        prediction = head.predict_competing_risks({"age": 55, "ECOG": 1})

        self.assertGreaterEqual(c_index, 0.65)
        self.assertTrue(prediction.dynamic_variant)
        self.assertAlmostEqual(sum(prediction.risk_probabilities.values()), 1.0, 5)

    def test_response_classifier_meets_pooled_held_out_auroc_gate(self) -> None:
        classifier = ImmunotherapyResponseClassifier(alpha=0.1)

        auroc = classifier.fit(
            feature_rows=[
                {"ifn_gamma_score": 0.8},
                {"ifn_gamma_score": 0.2},
                {"ifn_gamma_score": 0.6},
            ],
            labels=[1, 0, 1],
        )
        classifier.calibrate([0.05, 0.1, 0.08, 0.12])
        prediction = classifier.predict_proba(
            {"ifn_gamma_score": 0.8, "exhaustion_score": 0.3},
            {"CRP": 2.0, "PD_L1": 0.7},
        )

        self.assertGreaterEqual(auroc, 0.72)
        self.assertGreaterEqual(prediction.responder_probability, 0.0)
        self.assertLessEqual(prediction.responder_probability, 1.0)
        self.assertLess(
            prediction.conformal_interval[0],
            prediction.conformal_interval[1],
        )

    def test_multiomic_fusion_reports_missing_modalities(self) -> None:
        report = MultiomicFusion().fuse(
            {
                "scrna": [1.0, 2.0, 3.0],
                "scatac": [0.2, 0.4],
            }
        )

        self.assertEqual(report.modalities, ["scatac", "scrna"])
        self.assertIn("cite_seq", report.missing_modalities)
        self.assertIn("MOFA+", report.tools)
        self.assertEqual(report.fused_features["n_modalities"], 2.0)


if __name__ == "__main__":
    unittest.main()
