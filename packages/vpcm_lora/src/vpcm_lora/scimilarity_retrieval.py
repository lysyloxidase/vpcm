"""SCimilarity/scTab atlas neighbor retrieval fixture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from vpcm_data.base import AnnDataLike

from vpcm_lora._utils import Vector, mean_expression


def _squared_distance(left: Vector, right: Vector) -> float:
    return sum(
        (left_value - right_value) ** 2
        for left_value, right_value in zip(left, right)
    )


@dataclass(frozen=True)
class AtlasNeighborRetrieval:
    """Retrieve nearest atlas cells for patient LoRA augmentation.

    References include Heimberg et al. 2024 and scTab by Fischer et al. 2024.
    """

    default_k: int = 50_000

    def retrieve(
        self,
        patient_adata: AnnDataLike,
        atlas_adata: AnnDataLike,
        k: Optional[int] = None,
    ) -> AnnDataLike:
        """Return top-K nearest atlas neighbors in fixture expression space."""

        if not atlas_adata.x:
            raise ValueError("atlas_adata must contain expression rows.")
        active_k = min(k or self.default_k, atlas_adata.n_obs)
        patient_mean = mean_expression(patient_adata)
        ranked = sorted(
            range(atlas_adata.n_obs),
            key=lambda index: _squared_distance(patient_mean, atlas_adata.x[index]),
        )
        selected = ranked[:active_k]
        return AnnDataLike(
            obs=[atlas_adata.obs[index] for index in selected],
            var_names=list(atlas_adata.var_names),
            x_shape=(len(selected), atlas_adata.n_vars),
            x=[atlas_adata.x[index] for index in selected],
            uns={
                "retrieval": "scimilarity_sctab_fixture",
                "k": active_k,
                "source": str(atlas_adata.uns.get("resource_id", "atlas")),
            },
        )
