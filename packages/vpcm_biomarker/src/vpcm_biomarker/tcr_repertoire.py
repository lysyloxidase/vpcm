"""Optional TCR repertoire integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from vpcm_biomarker._math import mean
from vpcm_biomarker.types import TCRRepertoireReport

Vector = list[float]


class TCRRepertoireHead:
    """Integrate matched TCR-seq when available."""

    tools: ClassVar[list[str]] = ["mvTCR", "scirpy"]

    def integrate(
        self,
        expression_delta: Vector,
        clonotype_frequencies: Mapping[str, float] | None = None,
        top_n: int = 10,
    ) -> TCRRepertoireReport:
        """Return TCR repertoire features or an explicit missing-data report."""

        if clonotype_frequencies is None or not clonotype_frequencies:
            return TCRRepertoireReport(
                available=False,
                clonality=0.0,
                expansion_delta=0.0,
                top_clonotypes=[],
                tools=list(self.tools),
            )
        total = sum(max(value, 0.0) for value in clonotype_frequencies.values())
        if total <= 0.0:
            raise ValueError("At least one positive clonotype frequency is required.")
        normalized = {
            clonotype: max(value, 0.0) / total
            for clonotype, value in clonotype_frequencies.items()
        }
        clonality = sum(value * value for value in normalized.values())
        expansion_delta = clonality * (1.0 + mean(expression_delta))
        top_clonotypes = [
            clonotype
            for clonotype, _ in sorted(
                normalized.items(),
                key=lambda item: (-item[1], item[0]),
            )[:top_n]
        ]
        return TCRRepertoireReport(
            available=True,
            clonality=clonality,
            expansion_delta=expansion_delta,
            top_clonotypes=top_clonotypes,
            tools=list(self.tools),
        )
