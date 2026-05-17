"""ChemCPA perturbation predictor wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_perturbation.base import DeterministicPerturbationAdapter


@dataclass(frozen=True)
class ChemCPAWrapper(DeterministicPerturbationAdapter):
    """SMILES-aware CPA extension.

    Hetzel et al., NeurIPS 2022. Adds a chemistry encoder such as ChemBERTa-2
    or MolFormer-XL to support prediction on unseen compounds.
    """

    name: str = "chemcpa"
    effect_scale: float = 0.09

