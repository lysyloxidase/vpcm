"""CellOT perturbation predictor wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_perturbation.base import DeterministicPerturbationAdapter


@dataclass(frozen=True)
class CellOTWrapper(DeterministicPerturbationAdapter):
    """Neural optimal transport via input-convex neural networks.

    Bunne et al., Nature Methods 20:1759, 2023.
    DOI: 10.1038/s41592-023-01969-x
    """

    name: str = "cellot"
    effect_scale: float = 0.10

