"""Tahoe-100M chemical Perturb-seq loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class Tahoe100MLoader(BaseDatasetLoader):
    """Load Tahoe-100M chemical Perturb-seq data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("tahoe_100m"), fixture_mode=fixture_mode)

    def load_drug_slice(self, chembl_id: str, max_cells: int = 100_000) -> AnnDataLike:
        """Return a fixture for one chemical perturbation slice."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            n_obs=min(max_cells, 128),
            perturbation_type="drug",
            perturbation=chembl_id,
        )

