"""scPerturb unified perturbation atlas loader."""

from __future__ import annotations

from typing import ClassVar

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class scPerturbLoader(BaseDatasetLoader):  # noqa: N801
    """Unified Perturb-seq atlas (44 datasets, 32 CRISPR + 9 drug).

    Source: Peidli et al., Nature Methods 21:531 (2024)
    DOI: 10.1038/s41592-023-02144-y
    """

    EXPECTED_DATASET_COUNT: ClassVar[int] = 44
    DATASETS: ClassVar[dict[str, str]] = {
        "adamson_2016": "GSE90546",
        "dixit_2016": "GSE90063",
        "norman_2019": "GSE133344",
        "replogle_2022_k562": "GSE176022",
        "replogle_2022_rpe1": "GSE176032",
        "sci_plex_2020": "GSE139944",
        "aissa_2021": "GSE149383",
        "chang_2021": "E-MTAB-10698",
        "datlinger_2017": "GSE92872",
        "datlinger_2021": "GSE168620",
        "frangieh_2021": "SCP1064",
        "gasperini_2019": "GSE120861",
        "gehring_2019": "10.22002/D1.1311",
        "liscovitch_brauer_2021": "GSE161002",
        "mcfarland_2020": "10.6084/m9.figshare.5863776.v1",
        "mimitou_2021": "GSE156476",
        "papalexi_2021": "GSE153056",
        "pierce_2021": "AWS",
        "schiebinger_2019": "GSE106340/GSE115943",
        "schraivogel_2020": "GSE135497",
        "shifrut_2018": "GSE119450",
        "srivatsan_2020": "GSE139944",
        "tian_2019": "GSE152988",
        "tian_2021": "GSE124703",
        "weinreb_2020": "GSE140802",
        "xie_2017": "GSE81884",
        "zhao_2021": "GSE148842",
    }

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("scperturb"), fixture_mode=fixture_mode)

    def load_unified(self, dataset_id: str) -> AnnDataLike:
        """Return harmonized AnnData-like data for a scPerturb dataset."""

        if dataset_id not in self.DATASETS:
            raise KeyError(f"Unknown scPerturb dataset_id: {dataset_id}")
        return make_fixture_adata(
            resource_id=f"scperturb_{dataset_id}",
            perturbation_type="genetic",
            perturbation="CRISPRi",
        )
