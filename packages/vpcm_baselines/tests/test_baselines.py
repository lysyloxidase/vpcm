from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import cast

from vpcm_baselines.baseline_report import BaselineReport
from vpcm_baselines.csendes import (
    csendes_mean_beats_scgpt,
    reproduce_csendes_fixture,
)
from vpcm_baselines.mean_baseline import TrainMeanBaseline
from vpcm_baselines.ridge_baseline import RidgeBaseline
from vpcm_data.base import AnnDataLike


def _baseline_fixture() -> AnnDataLike:
    return AnnDataLike(
        obs=[
            {"cell_type_label": "T", "perturbation": "ctrl"},
            {"cell_type_label": "T", "perturbation": "drug"},
            {"cell_type_label": "B", "perturbation": "ctrl"},
            {"cell_type_label": "B", "perturbation": "drug"},
        ],
        var_names=["ENSG00000000001", "ENSG00000000002", "ENSG00000000003"],
        x_shape=(4, 3),
        x=[
            [1.0, 2.0, 3.0],
            [3.0, 4.0, 5.0],
            [10.0, 20.0, 30.0],
            [14.0, 24.0, 34.0],
        ],
    )


class BaselineTest(unittest.TestCase):
    def test_train_mean_outputs_cell_type_mean_and_ignores_intervention(self) -> None:
        baseline = TrainMeanBaseline()
        baseline.fit(_baseline_fixture())
        query = AnnDataLike(
            obs=[{"cell_type_label": "T", "perturbation": "unseen"}],
            var_names=["ENSG00000000001", "ENSG00000000002", "ENSG00000000003"],
            x_shape=(1, 3),
            x=[[9.0, 9.0, 9.0]],
        )

        first = baseline.predict(query, {"intervention_type": "drug", "target": "A"})
        second = baseline.predict(query, {"intervention_type": "drug", "target": "B"})

        self.assertEqual(first, [2.0, 3.0, 4.0])
        self.assertEqual(first, second)
        scores = baseline.score(
            query,
            observed=[2.1, 3.1, 4.1],
            intervention={"intervention_type": "drug"},
            top_n=2,
            target_gene_index=0,
        )
        self.assertIn("pearson", scores)

    def test_ridge_baseline_trains_on_pca50_features_without_error(self) -> None:
        baseline = RidgeBaseline(n_pca=50, alpha=1.0)
        train = _baseline_fixture()
        baseline.fit(train)

        prediction = baseline.predict(train, {"intervention_type": "drug"})

        self.assertEqual(len(prediction), len(train.var_names))
        self.assertEqual(baseline.feature_names[0], "bias")

    def test_baseline_report_schema_validates_dummy_data(self) -> None:
        report = BaselineReport.from_scores(
            mean_baseline_pearson=0.34,
            ridge_baseline_pearson=0.36,
            vpcm_ensemble_pearson=0.40,
            target_gene_removed=True,
            top_n=20,
            eval_set="adamson_test",
        )

        report.validate()

        self.assertAlmostEqual(report.beat_mean_delta, 0.06)
        self.assertEqual(report.to_dict()["eval_set"], "adamson_test")
        with self.assertRaises(ValueError):
            BaselineReport.from_scores(0.0, 0.0, 1.2, True, 20, "x").validate()
        with self.assertRaises(ValueError):
            BaselineReport.from_scores(0.0, 0.0, 0.1, False, 20, "x").validate()

    def test_csendes_reproduction_fixture_is_saved(self) -> None:
        self.assertTrue(csendes_mean_beats_scgpt())
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "csendes_repro.json"

            payload = reproduce_csendes_fixture(path)

            self.assertTrue(path.exists())
            self.assertGreaterEqual(
                cast(float, payload["train_mean_pearson"]),
                cast(float, payload["scgpt_pearson"]),
            )


if __name__ == "__main__":
    unittest.main()
