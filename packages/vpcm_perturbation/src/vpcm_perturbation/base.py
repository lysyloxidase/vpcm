"""Shared deterministic perturbation predictor adapter."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from vpcm_core.types import Intervention
from vpcm_data.base import AnnDataLike

Vector = list[float]


class PerturbationPredictor(Protocol):
    """Minimal predictor interface used by the ensemble."""

    @property
    def name(self) -> str:
        ...

    def predict(
        self,
        adata: AnnDataLike,
        intervention: Intervention,
        dropout_active: bool = False,
        sample_index: int = 0,
    ) -> Vector:
        ...


def stable_unit_interval(*parts: object) -> float:
    """Return a deterministic float in [0, 1]."""

    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def intervention_label(intervention: Intervention) -> str:
    """Return a stable intervention label."""

    return str(
        intervention.get("intervention_id")
        or intervention.get("target")
        or intervention.get("intervention_type")
        or "unknown_intervention"
    )


@dataclass(frozen=True)
class DeterministicPerturbationAdapter:
    """Fixture adapter for deep perturbation predictors."""

    name: str
    effect_scale: float
    dropout_scale: float = 0.015

    def predict(
        self,
        adata: AnnDataLike,
        intervention: Intervention,
        dropout_active: bool = False,
        sample_index: int = 0,
    ) -> Vector:
        """Return a deterministic delta-expression vector."""

        if not adata.x:
            raise ValueError(f"{self.name} requires adata.x.")
        n_genes = len(adata.x[0])
        label = intervention_label(intervention)
        baseline = [
            sum(row[gene_index] for row in adata.x) / len(adata.x)
            for gene_index in range(n_genes)
        ]
        deltas: Vector = []
        for gene_index, expression_mean in enumerate(baseline):
            signed = stable_unit_interval(self.name, label, gene_index) - 0.5
            delta = self.effect_scale * signed * (1.0 + expression_mean / 10.0)
            if dropout_active:
                noise = stable_unit_interval(
                    self.name,
                    label,
                    sample_index,
                    gene_index,
                    "dropout",
                ) - 0.5
                delta += self.dropout_scale * noise
            deltas.append(delta)
        return deltas
