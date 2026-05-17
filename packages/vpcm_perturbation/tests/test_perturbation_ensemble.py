from __future__ import annotations

import unittest

from vpcm_core.types import Intervention
from vpcm_data.base import AnnDataLike, make_fixture_adata
from vpcm_perturbation.cellot import CellOTWrapper
from vpcm_perturbation.chemcpa import ChemCPAWrapper
from vpcm_perturbation.cpa import CPAWrapper
from vpcm_perturbation.ensemble import PerturbationEnsemble
from vpcm_perturbation.gears import GEARSWrapper
from vpcm_perturbation.scgen import scGenWrapper


class PerturbationEnsembleTest(unittest.TestCase):
    def test_all_five_predictors_load_and_predict(self) -> None:
        adata = make_fixture_adata("perturb_fixture", n_obs=4, n_vars=5)
        intervention: Intervention = {"intervention_type": "drug", "target": "EGFR"}

        predictors = [
            CPAWrapper(),
            ChemCPAWrapper(),
            GEARSWrapper(),
            CellOTWrapper(),
            scGenWrapper(),
        ]

        self.assertEqual({predictor.name for predictor in predictors}, {
            "cpa",
            "chemcpa",
            "gears",
            "cellot",
            "scgen",
        })
        for predictor in predictors:
            prediction = predictor.predict(adata, intervention)
            self.assertEqual(len(prediction), adata.n_vars)

    def test_ensemble_mc_dropout_produces_uncertainty_and_baseline_report(self) -> None:
        adata = make_fixture_adata("perturb_fixture", n_obs=5, n_vars=6)
        ensemble = PerturbationEnsemble()

        prediction = ensemble.predict_with_uncertainty(
            adata,
            {
                "intervention_id": "CHEMBL25",
                "intervention_type": "drug",
                "metadata": {"eval_set": "adamson_test"},
            },
        )

        self.assertEqual(prediction.n_samples, 5 * 20)
        self.assertEqual(len(prediction.per_model_deltas), 5)
        self.assertTrue(any(value > 0.0 for value in prediction.delta_std))
        self.assertGreater(prediction.baseline_report.beat_mean_delta, 0.0)
        self.assertTrue(prediction.baseline_report.target_gene_removed)

    def test_norman_unseen_double_gate_reports_success_or_failure(self) -> None:
        ensemble = PerturbationEnsemble()

        success = ensemble.norman_unseen_double_gate(beat_delta=0.10)
        failure = ensemble.norman_unseen_double_gate(beat_delta=0.20)

        self.assertFalse(success.transparent_failure_reported)
        self.assertTrue(failure.transparent_failure_reported)
        self.assertEqual(success.baseline_report.eval_set, "norman_unseen_double")

    def test_fixture_latency_estimate_for_large_query_is_bounded(self) -> None:
        adata = AnnDataLike(
            obs=[
                {"cell_id": f"cell_{index}", "cell_type_label": "K562"}
                for index in range(1000)
            ],
            var_names=["ENSG00000000001", "ENSG00000000002"],
            x_shape=(1000, 2),
            x=[[1.0, 2.0] for _ in range(1000)],
        )
        ensemble = PerturbationEnsemble(m_dropout=2)

        latency = ensemble.measure_latency_seconds(
            adata,
            {"intervention_type": "genetic", "target": "TP53"},
        )

        self.assertLess(latency, 15.0)


if __name__ == "__main__":
    unittest.main()
