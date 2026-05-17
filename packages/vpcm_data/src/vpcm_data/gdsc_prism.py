"""GDSC and PRISM drug sensitivity panel loaders."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class GDSCLoader(BaseDatasetLoader):
    """Load GDSC drug sensitivity data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("gdsc"), fixture_mode=fixture_mode)

    def load_drug(self, chembl_id: str) -> AnnDataLike:
        """Return a GDSC drug-response fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="drug",
            perturbation=chembl_id,
            extra_obs={"response_metric": "IC50"},
        )


class PRISMLoader(BaseDatasetLoader):
    """Load DepMap PRISM pooled drug sensitivity data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("prism"), fixture_mode=fixture_mode)

    def load_drug(self, chembl_id: str) -> AnnDataLike:
        """Return a PRISM drug-response fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="drug",
            perturbation=chembl_id,
            extra_obs={"response_metric": "viability"},
        )

