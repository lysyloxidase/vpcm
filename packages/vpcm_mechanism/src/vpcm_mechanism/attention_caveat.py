"""Attention attribution with mandatory causality caveat."""

from __future__ import annotations

from vpcm_mechanism.types import (
    ATTENTION_CAUSALITY_CAVEAT,
    AttentionAttribution,
    AttentionReport,
)

Vector = list[float]


class AttentionAttributionWithCaveat:
    """Rank attention-derived gene attributions and attach caveats."""

    caveat = ATTENTION_CAUSALITY_CAVEAT

    def attribute(
        self,
        attention_scores: Vector,
        gene_ids: list[str],
        model_name: str,
        top_n: int = 10,
    ) -> AttentionReport:
        """Return top attention attributions with per-gene caveat text."""

        if len(attention_scores) != len(gene_ids):
            raise ValueError("attention_scores and gene_ids must have equal length.")
        if top_n <= 0:
            raise ValueError("top_n must be positive.")
        ranked = sorted(
            range(len(attention_scores)),
            key=lambda index: (-abs(attention_scores[index]), index),
        )
        attributions = [
            AttentionAttribution(
                gene_id=gene_ids[index],
                importance=attention_scores[index],
                rank=rank,
                caveat=self.caveat,
            )
            for rank, index in enumerate(ranked[:top_n], start=1)
        ]
        return AttentionReport(model_name=model_name, attributions=attributions)

