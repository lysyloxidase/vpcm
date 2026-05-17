"""Optional multi-omic fusion for outcome modeling."""

from __future__ import annotations

from collections.abc import Mapping

from vpcm_outcome._math import mean
from vpcm_outcome.types import MultiomicFusionReport

Vector = list[float]

_EXPECTED_MODALITIES = ["scrna", "scatac", "cite_seq", "proteomics", "metabolomics"]
_TOOLS = ["MOFA+", "totalVI", "MultiVI"]


class MultiomicFusion:
    """Fuse optional scRNA, scATAC, CITE-seq, proteomics, and metabolomics."""

    def fuse(
        self,
        modalities: Mapping[str, Vector],
    ) -> MultiomicFusionReport:
        """Return fused feature summary and missing-modality trace."""

        present = sorted(modalities)
        missing = [
            modality for modality in _EXPECTED_MODALITIES if modality not in modalities
        ]
        fused = {
            f"{modality}_mean": mean(values)
            for modality, values in sorted(modalities.items())
        }
        fused["n_modalities"] = float(len(present))
        return MultiomicFusionReport(
            modalities=present,
            fused_features=fused,
            missing_modalities=missing,
            tools=list(_TOOLS),
        )

