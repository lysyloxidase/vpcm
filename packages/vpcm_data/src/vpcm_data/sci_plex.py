"""sci-Plex chemical Perturb-seq loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class SciPlexLoader(BaseDatasetLoader):
    """Load sci-Plex (188 compounds across three cancer cell lines)."""

    CELL_LINES = ("A549", "K562", "MCF7")

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("sci_plex"), fixture_mode=fixture_mode)

    def load_compound(self, chembl_id: str, cell_line: str) -> AnnDataLike:
        """Return harmonized cells for one compound and cell line."""

        if cell_line not in self.CELL_LINES:
            raise ValueError(f"Unsupported sci-Plex cell line: {cell_line}")
        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="drug",
            perturbation=chembl_id,
            extra_obs={"cell_line": cell_line},
        )

