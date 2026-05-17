"""CRI iAtlas immunotherapy cohort loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class CRIiAtlasLoader(BaseDatasetLoader):
    """Load CRI iAtlas immunotherapy cohorts."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("cri_iatlas"), fixture_mode=fixture_mode)

    def load_immunotherapy_cohort(self, therapy: str) -> AnnDataLike:
        """Return an immunotherapy cohort fixture."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="immunotherapy",
            perturbation=therapy,
        )

