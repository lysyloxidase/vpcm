"""Norman combinatorial Perturb-seq loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class NormanLoader(BaseDatasetLoader):
    """Load Norman et al. dual-gene perturbation data."""

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("norman"), fixture_mode=fixture_mode)

    def load_dual_knockout(self, gene_a: str, gene_b: str) -> AnnDataLike:
        """Return a fixture for a dual perturbation."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            perturbation_type="combination",
            perturbation=f"{gene_a}+{gene_b}",
        )

