"""GEARS perturbation predictor wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_perturbation.base import DeterministicPerturbationAdapter


@dataclass(frozen=True)
class GEARSWrapper(DeterministicPerturbationAdapter):
    """Graph Enhanced Gene Activation Response Simulator.

    Roohani, Huang, and Leskovec, Nature Biotechnology 42:927, 2024.
    DOI: 10.1038/s41587-023-01905-6

    Uses gene ontology and co-expression graphs for multi-gene perturbations.
    Caveat: on Norman unseen-double interventions, GEARS may lose to a ridge
    baseline and must be reported transparently.
    """

    name: str = "gears"
    effect_scale: float = 0.11

