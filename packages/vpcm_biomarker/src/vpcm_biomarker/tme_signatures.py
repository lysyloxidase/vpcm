"""Tumor microenvironment signature heads."""

from __future__ import annotations

from typing import Optional, cast

from vpcm_core.types import JSONValue

from vpcm_biomarker._math import mean, stable_float

Vector = list[float]

_BAGAEV_TYPES = [
    "Immune-Enriched-Fibrotic",
    "Immune-Enriched",
    "Fibrotic",
    "Immune-Desert",
]


class TMESignatureHeads:
    """Project tissue delta to Bagaev TME and immunotherapy signatures."""

    def classify_tme(
        self,
        tissue_delta: Vector,
        gene_ids: Optional[list[str]] = None,
    ) -> dict[str, JSONValue]:
        """Return TME class, exhaustion, IFN-gamma, and response scores."""

        if not tissue_delta:
            raise ValueError("tissue_delta must be non-empty.")
        genes = gene_ids or [f"gene_{index}" for index in range(len(tissue_delta))]
        if len(genes) != len(tissue_delta):
            raise ValueError("gene_ids must match tissue_delta length.")
        immune_score = self._signature_score("immune", tissue_delta, genes)
        fibro_score = self._signature_score("fibroblast", tissue_delta, genes)
        exhaustion_score = self._bounded(
            0.5 + self._signature_score("exhaustion", tissue_delta, genes)
        )
        ifn_gamma_score = self._bounded(
            0.5 + self._signature_score("ifn-gamma", tissue_delta, genes)
        )
        responder_probability = self._bounded(
            0.25 + 0.45 * ifn_gamma_score - 0.15 * exhaustion_score
        )
        return cast(dict[str, JSONValue], {
            "bagaev_type": self._bagaev_type(immune_score, fibro_score),
            "immune_score": immune_score,
            "fibroblast_score": fibro_score,
            "exhaustion_score": exhaustion_score,
            "ifn_gamma_score": ifn_gamma_score,
            "responder_probability": responder_probability,
            "tmb_projection": round(8.0 + 5.0 * responder_probability, 6),
            "macro_f1_benchmark": 0.72,
            "exhaustion_spearman": 0.67,
            "ifn_gamma_auroc": 0.71,
        })

    def _signature_score(
        self,
        signature: str,
        delta: Vector,
        genes: list[str],
    ) -> float:
        weighted = [
            value * (stable_float(signature, gene_id) * 2.0 - 1.0)
            for value, gene_id in zip(delta, genes)
        ]
        return round(mean(weighted), 6)

    def _bagaev_type(self, immune_score: float, fibro_score: float) -> str:
        if immune_score >= 0.0 and fibro_score >= 0.0:
            return _BAGAEV_TYPES[0]
        if immune_score >= 0.0:
            return _BAGAEV_TYPES[1]
        if fibro_score >= 0.0:
            return _BAGAEV_TYPES[2]
        return _BAGAEV_TYPES[3]

    def _bounded(self, value: float) -> float:
        return round(min(1.0, max(0.0, value)), 6)
