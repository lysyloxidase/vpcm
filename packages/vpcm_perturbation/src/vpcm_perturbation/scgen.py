"""scGen perturbation predictor wrapper."""

from __future__ import annotations

from dataclasses import dataclass

from vpcm_perturbation.base import DeterministicPerturbationAdapter


@dataclass(frozen=True)
class scGenWrapper(DeterministicPerturbationAdapter):  # noqa: N801
    """Beta-VAE plus latent-space arithmetic.

    Lotfollahi et al., Nature Methods 16:715, 2019.
    DOI: 10.1038/s41592-019-0494-8
    """

    name: str = "scgen"
    effect_scale: float = 0.07

