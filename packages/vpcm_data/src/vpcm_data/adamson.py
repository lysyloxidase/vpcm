"""Adamson UPR Perturb-seq loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class AdamsonLoader(BaseDatasetLoader):
    """Load Adamson et al. UPR Perturb-seq benchmark data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("adamson"), fixture_mode=fixture_mode)

    def load_upr_screen(self) -> AnnDataLike:
        """Return a harmonized UPR screen fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="genetic",
            perturbation="UPR_CRISPRi",
        )

