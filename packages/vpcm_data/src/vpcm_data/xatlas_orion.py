"""X-Atlas / Orion fix-cryopreserve perturbation loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class XAtlasOrionLoader(BaseDatasetLoader):
    """Load genome-wide fix-cryopreserve perturbation data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("xatlas_orion"), fixture_mode=fixture_mode)

    def load_gene(self, ensembl_id: str) -> AnnDataLike:
        """Return a fixture for one genome-wide perturbation target."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="genetic",
            perturbation=ensembl_id,
        )

