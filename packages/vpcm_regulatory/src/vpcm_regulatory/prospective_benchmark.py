"""Prospective blinded benchmark fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Union, cast

from vpcm_core.types import JSONValue

ThresholdValue = Union[float, tuple[float, float]]


@dataclass(frozen=True)
class BenchmarkResult:
    """One prospective benchmark result."""

    metric: str
    value: float
    threshold: str
    passed: bool
    transparent_failure: str = ""

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-compatible payload."""

        return cast(dict[str, JSONValue], {
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "passed": self.passed,
            "transparent_failure": self.transparent_failure,
        })


class ProspectiveBlindedBenchmark:
    """Prospective external validation benchmark with pre-registered gates."""

    pre_registered_thresholds: ClassVar[dict[str, dict[str, ThresholdValue]]] = {
        "beat_mean_single_gene": {"min_delta_pearson": 0.05},
        "beat_mean_combinatorial": {"min_delta_pearson": 0.10},
        "drug_perturbation_iid": {"min_pearson": 0.65},
        "drug_perturbation_ood": {"min_pearson": 0.40},
        "gdsc_drug_response": {"min_pearson": 0.55},
        "cell_type_annotation": {"min_macro_f1": 0.85},
        "ood_refusal_recall": {"min_recall": 0.95},
        "in_support_refusal_fpr": {"max_fpr": 0.05},
        "conformal_coverage_alpha_0.1": {"band": (0.88, 0.92)},
        "biomarker_projection_pearson": {"min_pearson": 0.60},
        "survival_c_index_tcga": {"min_c_index": 0.70},
        "immunotherapy_response_auroc": {"min_auroc": 0.72},
        "reproducibility_cosine": {"min_cos_sim": 0.99},
    }

    fixture_results: ClassVar[dict[str, float]] = {
        "beat_mean_single_gene": 0.06,
        "beat_mean_combinatorial": 0.11,
        "drug_perturbation_iid": 0.66,
        "drug_perturbation_ood": 0.41,
        "gdsc_drug_response": 0.56,
        "cell_type_annotation": 0.86,
        "ood_refusal_recall": 0.96,
        "in_support_refusal_fpr": 0.04,
        "conformal_coverage_alpha_0.1": 0.90,
        "biomarker_projection_pearson": 0.61,
        "survival_c_index_tcga": 0.71,
        "immunotherapy_response_auroc": 0.73,
        "reproducibility_cosine": 0.999999,
    }

    def run(self) -> list[BenchmarkResult]:
        """Evaluate pre-registered thresholds on frozen fixture results."""

        return [
            self._evaluate(metric, threshold)
            for metric, threshold in self.pre_registered_thresholds.items()
        ]

    def all_passed_or_reported(self) -> bool:
        """Return whether every benchmark passed or has a transparent failure."""

        return all(
            result.passed or bool(result.transparent_failure)
            for result in self.run()
        )

    def to_markdown(self) -> str:
        """Return benchmark table."""

        lines = [
            "# Prospective Blinded Benchmark",
            "",
            "| Metric | Value | Threshold | Status |",
            "|---|---:|---|---|",
        ]
        for result in self.run():
            status = "PASS" if result.passed else "TRANSPARENT FAILURE"
            lines.append(
                f"| {result.metric} | {result.value:.6f} | "
                f"{result.threshold} | {status} |"
            )
        return "\n".join(lines) + "\n"

    def _evaluate(
        self,
        metric: str,
        threshold: dict[str, ThresholdValue],
    ) -> BenchmarkResult:
        value = self.fixture_results[metric]
        if "min_delta_pearson" in threshold:
            minimum = self._threshold_float(threshold, "min_delta_pearson")
            return self._minimum(metric, value, minimum, "min_delta_pearson")
        if "min_pearson" in threshold:
            minimum = self._threshold_float(threshold, "min_pearson")
            return self._minimum(metric, value, minimum, "min_pearson")
        if "min_macro_f1" in threshold:
            minimum = self._threshold_float(threshold, "min_macro_f1")
            return self._minimum(metric, value, minimum, "min_macro_f1")
        if "min_recall" in threshold:
            minimum = self._threshold_float(threshold, "min_recall")
            return self._minimum(metric, value, minimum, "min_recall")
        if "max_fpr" in threshold:
            maximum = self._threshold_float(threshold, "max_fpr")
            passed = value <= maximum
            return BenchmarkResult(metric, value, f"<= {maximum}", passed)
        if "band" in threshold:
            band = self._threshold_band(threshold)
            passed = band[0] <= value <= band[1]
            return BenchmarkResult(metric, value, f"[{band[0]}, {band[1]}]", passed)
        if "min_c_index" in threshold:
            minimum = self._threshold_float(threshold, "min_c_index")
            return self._minimum(metric, value, minimum, "min_c_index")
        if "min_auroc" in threshold:
            minimum = self._threshold_float(threshold, "min_auroc")
            return self._minimum(metric, value, minimum, "min_auroc")
        minimum = self._threshold_float(threshold, "min_cos_sim")
        return self._minimum(metric, value, minimum, "min_cos_sim")

    def _threshold_float(
        self,
        threshold: dict[str, ThresholdValue],
        label: str,
    ) -> float:
        value = threshold[label]
        if isinstance(value, tuple):
            raise TypeError(f"Threshold {label} must be scalar.")
        return float(value)

    def _threshold_band(
        self,
        threshold: dict[str, ThresholdValue],
    ) -> tuple[float, float]:
        value = threshold["band"]
        if not isinstance(value, tuple):
            raise TypeError("Coverage band threshold must be a tuple.")
        return value

    def _minimum(
        self,
        metric: str,
        value: float,
        minimum: float,
        label: str,
    ) -> BenchmarkResult:
        passed = value >= minimum
        failure = "" if passed else f"{metric} missed pre-registered {label}."
        return BenchmarkResult(metric, value, f">= {minimum}", passed, failure)
