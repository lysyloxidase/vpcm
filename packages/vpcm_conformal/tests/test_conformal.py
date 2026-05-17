from __future__ import annotations

import unittest

from vpcm_conformal.coverage_audit import CoverageAlarm, CoverageAudit
from vpcm_conformal.cqr import ConformalizedQuantileRegression
from vpcm_conformal.mondrian_conformal import MondrianConformalPredictor
from vpcm_conformal.split_conformal import SplitConformalPredictor
from vpcm_conformal.types import PredictionIntervals


class ConformalTest(unittest.TestCase):
    def test_split_conformal_marginal_coverage_is_in_fda_band(self) -> None:
        predictor = SplitConformalPredictor(alpha=0.1)
        predictor.calibrate(
            y_true_cal=[1.0] * 92 + [2.0] * 8,
            y_pred_cal=[0.0] * 100,
            sigma_cal=[1.0] * 100,
        )

        intervals = predictor.predict_interval([0.0] * 100, [1.0] * 100)
        ground_truth = [0.5] * 90 + [2.0] * 10
        coverage = CoverageAudit().audit(intervals, ground_truth)

        self.assertEqual(predictor.qhat, 1.0)
        self.assertEqual(coverage, 0.9)

    def test_mondrian_conditional_coverage_per_cell_type(self) -> None:
        predictor = MondrianConformalPredictor(alpha=0.1)
        groups = ["T"] * 50 + ["B"] * 50
        predictor.calibrate(
            y_true_cal=[1.0] * 47 + [2.0] * 3 + [1.0] * 47 + [2.0] * 3,
            y_pred_cal=[0.0] * 100,
            sigma_cal=[1.0] * 100,
            groups=groups,
        )

        intervals = predictor.predict_interval([0.0] * 100, [1.0] * 100, groups)
        ground_truth = [0.5] * 45 + [2.0] * 5 + [0.5] * 45 + [2.0] * 5
        coverages = CoverageAudit().audit_by_group(intervals, ground_truth, groups)

        self.assertEqual(coverages, {"B": 0.9, "T": 0.9})

    def test_cqr_adaptive_intervals_are_tighter_for_low_variance_gene(self) -> None:
        cqr = ConformalizedQuantileRegression(alpha=0.1)
        cqr.fit_quantiles(
            [
                [1.0, 10.0],
                [1.1, 20.0],
                [0.9, 30.0],
                [1.05, 40.0],
                [0.95, 50.0],
            ]
        )
        cqr.calibrate(
            y_true_cal=[[1.0, 11.0], [1.1, 49.0]],
            lo_pred_cal=[[0.9, 8.0], [0.9, 45.0]],
            hi_pred_cal=[[1.2, 15.0], [1.2, 55.0]],
        )

        intervals = cqr.predict_interval(
            cqr.lower_quantiles,
            cqr.upper_quantiles,
        )
        widths = intervals.widths()

        self.assertLess(widths[0], widths[1])

    def test_coverage_audit_raises_recalibration_alarm(self) -> None:
        with self.assertRaises(CoverageAlarm):
            CoverageAudit().audit(
                PredictionIntervals(lo=[0.0] * 100, hi=[1.0] * 100),
                ground_truth=[0.5] * 50 + [2.0] * 50,
            )


if __name__ == "__main__":
    unittest.main()

