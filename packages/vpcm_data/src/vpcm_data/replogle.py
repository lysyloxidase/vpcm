"""Replogle genome-scale Perturb-seq loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class ReplogleLoader(BaseDatasetLoader):
    """Genome-scale Perturb-seq (Replogle et al., Cell 185:2559, 2022).

    DOI: 10.1016/j.cell.2022.05.013
    Approximately 2.5M cells across K562 and RPE1.
    """

    CELL_LINES = ("K562", "RPE1")

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("replogle"), fixture_mode=fixture_mode)

    def load_cell_line(self, cell_line: str) -> AnnDataLike:
        """Return one Replogle cell-line fixture."""

        if cell_line not in self.CELL_LINES:
            raise ValueError(f"Unsupported Replogle cell line: {cell_line}")
        return make_fixture_adata(
            resource_id=f"replogle_{cell_line.lower()}",
            perturbation_type="genetic",
            perturbation="CRISPRi",
            extra_obs={"cell_line": cell_line},
        )

    def split_plan(self) -> dict[str, list[str]]:
        """Return Phase 1 split definitions."""

        return {
            "leave_perturbation_out": ["held_out_gene_knockdowns"],
            "leave_cell_line_out": ["train_K562", "test_RPE1"],
        }
