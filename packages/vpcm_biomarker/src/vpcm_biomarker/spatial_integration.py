"""Optional spatial transcriptomics integration layer."""

from __future__ import annotations

from collections.abc import Sequence

from vpcm_biomarker._math import mean
from vpcm_biomarker.types import SpatialIntegrationReport

Vector = list[float]

SUPPORTED_PLATFORMS = ["Visium", "Visium HD", "MERFISH", "Xenium"]
SPATIAL_TOOLS = ["cell2location", "Tangram", "NicheCompass", "STAGATE", "squidpy"]


class SpatialTranscriptomicsIntegrator:
    """Add spatial context to biomarker projection when available."""

    def integrate(
        self,
        tissue_delta: Vector,
        spot_coordinates: Sequence[tuple[float, float]] | None = None,
        platform: str = "Visium",
    ) -> SpatialIntegrationReport:
        """Return spatial context scores or an explicit missing-data report."""

        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError(f"Unsupported spatial platform: {platform}")
        if spot_coordinates is None or not spot_coordinates:
            return SpatialIntegrationReport(
                available=False,
                platform=platform,
                spatial_context_score=0.0,
                infiltration_gradient=0.0,
                tools=list(SPATIAL_TOOLS),
                caveat=(
                    "Spatial context unavailable; projection used non-spatial delta."
                ),
            )
        expression_signal = mean(tissue_delta)
        x_values = [coordinate[0] for coordinate in spot_coordinates]
        y_values = [coordinate[1] for coordinate in spot_coordinates]
        x_span = max(x_values) - min(x_values) if x_values else 0.0
        y_span = max(y_values) - min(y_values) if y_values else 0.0
        gradient = (x_span + y_span) / max(len(spot_coordinates), 1)
        return SpatialIntegrationReport(
            available=True,
            platform=platform,
            spatial_context_score=round(expression_signal + gradient, 6),
            infiltration_gradient=round(gradient, 6),
            tools=list(SPATIAL_TOOLS),
            caveat=(
                "Spatial integration improves TME context but remains platform- "
                "and registration-quality dependent."
            ),
        )
