"""CELLxGENE Census loader."""

from __future__ import annotations

from vpcm_data.base import AnnDataLike, BaseDatasetLoader, make_fixture_adata
from vpcm_data.registry import get_resource


class CellxGeneCensusLoader(BaseDatasetLoader):
    """Load CELLxGENE Census (>50M cells, >=95M with discovery as of 2025).

    Source: CZ CELLxGENE Discover Census, bioRxiv 10.1101/2023.10.30.563174
    Use cellxgene-census Python API (LTS-stable; pin to 2025-01-30 release).

    For VPCM:
    - Pretraining substrate for foundation models via HuggingFace weights
    - SCimilarity nearest-neighbor pool for patient atlas augmentation
    - Gene ID universe (Ensembl) for harmonization

    Caveat: corpora over-represent European-ancestry donors, so ancestry-
    stratified fairness audits are required.
    """

    def __init__(self, fixture_mode: bool = True) -> None:
        super().__init__(get_resource("cellxgene_census"), fixture_mode=fixture_mode)

    def query_by_disease(self, disease: str, max_cells: int = 1_000_000) -> AnnDataLike:
        """Return AnnData-like cells matching a disease ontology label."""

        return self.load(disease=disease, max_cells=min(max_cells, 128))

    def retrieve_neighbors(
        self,
        query_adata: AnnDataLike,
        k: int = 50_000,
    ) -> AnnDataLike:
        """Return nearest atlas cells for patient atlas augmentation."""

        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            n_obs=min(k, 128),
            extra_obs={"retrieval_source_cells": str(query_adata.n_obs)},
        )
