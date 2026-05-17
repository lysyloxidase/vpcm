"""CPA perturbation predictor wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_perturbation.base import DeterministicPerturbationAdapter


@dataclass(frozen=True)
class CPAWrapper(DeterministicPerturbationAdapter):
    """Compositional Perturbation Autoencoder.

    Lotfollahi et al., Molecular Systems Biology 19:e11517.
    DOI: 10.15252/msb.202211517
    GitHub: theislab/CPA

    Disentangles drug, dose, and cell type via adversarial classifiers.
    """

    name: str = "cpa"
    effect_scale: float = 0.08

