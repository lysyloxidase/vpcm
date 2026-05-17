"""TCGA pan-cancer clinical and bulk RNA loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class TCGALoader(BaseDatasetLoader):
    """Load TCGA pan-cancer clinical and expression data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("tcga"), fixture_mode=fixture_mode)

    def load_cohort(self, cancer_type: str) -> AnnDataLike:
        """Return a TCGA cohort fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            extra_obs={"cancer_type": cancer_type, "endpoint": "PFS"},
        )

