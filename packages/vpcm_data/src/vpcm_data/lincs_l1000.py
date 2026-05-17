"""LINCS L1000 and Connectivity Map loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class LINCSL1000Loader(BaseDatasetLoader):
    """Load LINCS L1000 chemical perturbation profiles."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("lincs_l1000"), fixture_mode=fixture_mode)

    def load_signature(self, perturbagen: str) -> AnnDataLike:
        """Return a fixture for a L1000 perturbagen signature."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="drug",
            perturbation=perturbagen,
        )

