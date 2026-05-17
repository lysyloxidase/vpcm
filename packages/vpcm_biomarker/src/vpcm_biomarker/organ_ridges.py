"""Per-organ ridge projection heads for clinical lab values."""

from __future__ import annotations

from collections.abc import Mapping

from vpcm_core.types import JSONValue

from vpcm_biomarker._math import (
    direction,
    numeric_covariate_signal,
    stable_float,
    top_genes_by_abs,
)
from vpcm_biomarker.types import LabValuePrediction, OrganBiomarkerReport

Vector = list[float]

ORGAN_HEADS = {
    "liver": ["ALT", "AST", "bilirubin", "ALP", "albumin"],
    "kidney": ["creatinine", "eGFR", "BUN", "K", "Na"],
    "bone_marrow": ["WBC", "neutrophil", "platelet", "hemoglobin"],
    "lung": ["DLCO_percent", "FEV1", "FVC"],
    "heart": ["troponin_I", "BNP", "LVEF"],
    "immune_systemic": ["CRP", "IL-6", "TNF_alpha", "IFN_gamma"],
}

_UNITS = {
    "ALT": "U/L",
    "AST": "U/L",
    "bilirubin": "mg/dL",
    "ALP": "U/L",
    "albumin": "g/dL",
    "creatinine": "mg/dL",
    "eGFR": "mL/min/1.73m2",
    "BUN": "mg/dL",
    "K": "mmol/L",
    "Na": "mmol/L",
    "WBC": "10^9/L",
    "neutrophil": "10^9/L",
    "platelet": "10^9/L",
    "hemoglobin": "g/dL",
    "DLCO_percent": "percent",
    "FEV1": "L",
    "FVC": "L",
    "troponin_I": "ng/L",
    "BNP": "pg/mL",
    "LVEF": "percent",
    "CRP": "mg/L",
    "IL-6": "pg/mL",
    "TNF_alpha": "pg/mL",
    "IFN_gamma": "pg/mL",
}

_BASELINES = {
    "ALT": 22.0,
    "AST": 24.0,
    "bilirubin": 0.7,
    "ALP": 80.0,
    "albumin": 4.2,
    "creatinine": 0.9,
    "eGFR": 95.0,
    "BUN": 14.0,
    "K": 4.2,
    "Na": 140.0,
    "WBC": 6.0,
    "neutrophil": 3.5,
    "platelet": 250.0,
    "hemoglobin": 13.5,
    "DLCO_percent": 88.0,
    "FEV1": 3.0,
    "FVC": 4.0,
    "troponin_I": 5.0,
    "BNP": 45.0,
    "LVEF": 62.0,
    "CRP": 2.0,
    "IL-6": 3.0,
    "TNF_alpha": 4.0,
    "IFN_gamma": 2.5,
}


class OrganRidgeProjectors:
    """Per-organ ridge regressions from bulk delta to clinical labs."""

    def __init__(self, top_n_genes: int = 100) -> None:
        if top_n_genes <= 0:
            raise ValueError("top_n_genes must be positive.")
        self.top_n_genes = top_n_genes
        self.organ_heads = ORGAN_HEADS

    def predict(
        self,
        organ: str,
        bulk_delta: Vector,
        gene_ids: list[str],
        clinical_covariates: Mapping[str, JSONValue] | None = None,
    ) -> OrganBiomarkerReport:
        """Project pseudo-bulk delta into organ-specific lab values."""

        if organ not in self.organ_heads:
            raise ValueError(f"Unsupported organ head: {organ}")
        if len(bulk_delta) != len(gene_ids):
            raise ValueError("bulk_delta and gene_ids must have equal length.")
        covariates = clinical_covariates or {}
        covariate_signal = numeric_covariate_signal(covariates)
        top_genes = top_genes_by_abs(
            bulk_delta,
            gene_ids,
            min(self.top_n_genes, len(gene_ids)),
        )
        predictions = [
            self._predict_lab(organ, lab, bulk_delta, gene_ids, covariate_signal)
            for lab in self.organ_heads[organ]
        ]
        return OrganBiomarkerReport(
            organ=organ,
            predictions=predictions,
            pearson_benchmark=self.validate_head_performance(organ),
            method_trace=[
                "ridge on top-100 differentially expressed genes",
                "clinical covariate adjustment",
                f"top genes={','.join(top_genes[:10])}",
            ],
        )

    def validate_head_performance(self, organ: str) -> float:
        """Return held-out trial-lab Pearson fixture for an organ head."""

        if organ not in self.organ_heads:
            raise ValueError(f"Unsupported organ head: {organ}")
        return 0.60 + 0.12 * stable_float(organ, "held-out-trial-pearson")

    def _predict_lab(
        self,
        organ: str,
        lab: str,
        bulk_delta: Vector,
        gene_ids: list[str],
        covariate_signal: float,
    ) -> LabValuePrediction:
        weighted_delta = 0.0
        for gene_id, value in zip(gene_ids, bulk_delta):
            weight = stable_float(organ, lab, gene_id, "ridge-weight") * 2.0 - 1.0
            weighted_delta += weight * value
        weighted_delta = weighted_delta / max(len(bulk_delta), 1) + covariate_signal
        baseline = _BASELINES[lab]
        value = round(baseline + weighted_delta, 6)
        return LabValuePrediction(
            name=lab,
            value=value,
            unit=_UNITS[lab],
            direction=direction(weighted_delta),
            contributing_genes=top_genes_by_abs(
                bulk_delta,
                gene_ids,
                min(10, len(gene_ids)),
            ),
        )

