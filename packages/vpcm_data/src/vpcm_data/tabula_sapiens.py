"""Tabula Sapiens atlas loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class TabulaSapiensLoader(BaseDatasetLoader):
    """Load Tabula Sapiens v1/v2 multi-tissue atlas data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("tabula_sapiens"), fixture_mode=fixture_mode)

    def load_tissue(self, tissue: str) -> AnnDataLike:
        """Return a multi-tissue atlas fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            extra_obs={"tissue": tissue},
        )

