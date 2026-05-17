"""Dataset inventory and single query API for VPCM Phase 1."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from vpcm_core.types import DatasetResource, JSONValue

from vpcm_data.base import AnnDataLike, BaseDatasetLoader

DATASET_INVENTORY: dict[str, DatasetResource] = {
    "cellxgene_census": {
        "resource_id": "cellxgene_census",
        "name": "CELLxGENE Census",
        "status": "LOAD",
        "used_in": ["FM pretraining", "SCimilarity retrieval"],
        "doi_or_source": "10.1101/2023.10.30.563174",
        "modality": "single-cell RNA-seq atlas",
        "access": "cellxgene-census Python API release 2025-01-30",
    },
    "human_cell_atlas": {
        "resource_id": "human_cell_atlas",
        "name": "Human Cell Atlas",
        "status": "LOAD",
        "used_in": ["Atlas reference"],
        "doi_or_source": "10.7554/eLife.27041",
        "modality": "single-cell atlas",
        "access": "HCA data portal",
    },
    "tabula_sapiens": {
        "resource_id": "tabula_sapiens",
        "name": "Tabula Sapiens v1/v2",
        "status": "LOAD",
        "used_in": ["Cross-tissue benchmark"],
        "doi_or_source": "10.1126/science.abl4896",
        "modality": "single-cell RNA-seq atlas",
        "access": "cellxgene and Tabula Sapiens portal",
    },
    "lincs_l1000": {
        "resource_id": "lincs_l1000",
        "name": "LINCS L1000",
        "status": "LOAD",
        "used_in": ["Chemical perturbation prior"],
        "doi_or_source": "10.1016/j.cell.2017.10.049",
        "modality": "bulk expression perturbation",
        "access": "clue.io / LINCS",
    },
    "connectivity_map": {
        "resource_id": "connectivity_map",
        "name": "Connectivity Map",
        "status": "LOAD",
        "used_in": ["Drug-disease matching"],
        "doi_or_source": "10.1126/science.1132939",
        "modality": "bulk expression perturbation",
        "access": "Broad Connectivity Map",
    },
    "sci_plex": {
        "resource_id": "sci_plex",
        "name": "sci-Plex",
        "status": "LOAD",
        "used_in": ["Drug perturbation benchmark"],
        "doi_or_source": "10.1126/science.aax6234",
        "modality": "single-cell chemical Perturb-seq",
        "access": "GEO GSE139944",
    },
    "replogle": {
        "resource_id": "replogle",
        "name": "Replogle K562 + RPE1",
        "status": "LOAD",
        "used_in": ["Genetic perturbation gold standard"],
        "doi_or_source": "10.1016/j.cell.2022.05.013",
        "modality": "single-cell CRISPRi Perturb-seq",
        "access": "GEO GSE176022/GSE176032 and gwps.wi.mit.edu",
    },
    "adamson": {
        "resource_id": "adamson",
        "name": "Adamson UPR Perturb-seq",
        "status": "LOAD",
        "used_in": ["Benchmark"],
        "doi_or_source": "10.1016/j.cell.2016.11.048",
        "modality": "single-cell CRISPRi Perturb-seq",
        "access": "GEO GSE90546",
    },
    "norman": {
        "resource_id": "norman",
        "name": "Norman dual KO",
        "status": "LOAD",
        "used_in": ["Combinatorial perturbation"],
        "doi_or_source": "10.1126/science.aax4438",
        "modality": "single-cell combinatorial CRISPRa",
        "access": "GEO GSE133344",
    },
    "jost": {
        "resource_id": "jost",
        "name": "Jost CRISPRi",
        "status": "LOAD",
        "used_in": ["Benchmark"],
        "doi_or_source": "10.1038/s41587-019-0387-5",
        "modality": "single-cell CRISPRi",
        "access": "GEO / publication supplement",
    },
    "scperturb": {
        "resource_id": "scperturb",
        "name": "scPerturb unified atlas",
        "status": "LOAD",
        "used_in": ["Benchmark", "E-distance", "interventional support"],
        "doi_or_source": "10.1038/s41592-023-02144-y",
        "modality": "single-cell perturbation atlas",
        "access": "scperturb.org and Zenodo",
    },
    "tahoe_100m": {
        "resource_id": "tahoe_100m",
        "name": "Tahoe-100M",
        "status": "LOAD",
        "used_in": ["Next-gen chemical Perturb-seq"],
        "doi_or_source": "10.1101/2025.02.20.639398",
        "modality": "single-cell chemical Perturb-seq",
        "access": "bioRxiv supplement / CELLxGENE collections",
    },
    "xatlas_orion": {
        "resource_id": "xatlas_orion",
        "name": "X-Atlas / Orion",
        "status": "LOAD",
        "used_in": ["Genome-wide fix-cryopreserve benchmark"],
        "doi_or_source": "10.1101/2025.06.11.659105",
        "modality": "single-cell genome-wide perturbation",
        "access": "bioRxiv supplement",
    },
    "depmap_ccle": {
        "resource_id": "depmap_ccle",
        "name": "DepMap / CCLE",
        "status": "LOAD",
        "used_in": ["Drug sensitivity bulk validation"],
        "doi_or_source": "depmap.org",
        "modality": "bulk expression and dependency",
        "access": "DepMap portal",
    },
    "gdsc": {
        "resource_id": "gdsc",
        "name": "GDSC",
        "status": "LOAD",
        "used_in": ["Drug sensitivity"],
        "doi_or_source": "cancerrxgene.org",
        "modality": "drug sensitivity panel",
        "access": "GDSC portal",
    },
    "prism": {
        "resource_id": "prism",
        "name": "PRISM",
        "status": "LOAD",
        "used_in": ["Drug sensitivity"],
        "doi_or_source": "depmap.org",
        "modality": "pooled drug sensitivity",
        "access": "DepMap PRISM",
    },
    "tcga": {
        "resource_id": "tcga",
        "name": "TCGA pan-cancer",
        "status": "LOAD",
        "used_in": ["Patient outcome modeling"],
        "doi_or_source": "cbioportal.org",
        "modality": "clinical and bulk RNA pan-cancer",
        "access": "cBioPortal / GDC",
    },
    "gtex": {
        "resource_id": "gtex",
        "name": "GTEx",
        "status": "LOAD",
        "used_in": ["Healthy tissue reference"],
        "doi_or_source": "gtexportal.org",
        "modality": "bulk RNA healthy tissue",
        "access": "GTEx portal",
    },
    "cri_iatlas": {
        "resource_id": "cri_iatlas",
        "name": "CRI iAtlas",
        "status": "LOAD",
        "used_in": ["Immunotherapy cohorts"],
        "doi_or_source": "cri-iatlas.org",
        "modality": "clinical immunotherapy cohorts",
        "access": "CRI iAtlas portal",
    },
    "onek1k": {
        "resource_id": "onek1k",
        "name": "OneK1K",
        "status": "LOAD",
        "used_in": ["Mendelian-randomization causal anchors"],
        "doi_or_source": "10.1126/science.abf3041",
        "modality": "single-cell eQTL immune atlas",
        "access": "publication supplement",
    },
}


def list_resources() -> list[DatasetResource]:
    """Return all Phase 1 dataset inventory records."""

    return list(DATASET_INVENTORY.values())


def get_resource(resource_id: str) -> DatasetResource:
    """Return one dataset inventory record."""

    try:
        return DATASET_INVENTORY[resource_id]
    except KeyError as exc:
        raise KeyError(f"Unknown VPCM dataset resource: {resource_id}") from exc


def _loader_for(resource_id: str, fixture_mode: bool) -> BaseDatasetLoader:
    if resource_id == "cellxgene_census":
        from vpcm_data.cellxgene_census import CellxGeneCensusLoader

        return CellxGeneCensusLoader(fixture_mode=fixture_mode)
    if resource_id == "scperturb":
        from vpcm_data.scperturb import scPerturbLoader

        return scPerturbLoader(fixture_mode=fixture_mode)
    if resource_id == "sci_plex":
        from vpcm_data.sci_plex import SciPlexLoader

        return SciPlexLoader(fixture_mode=fixture_mode)
    if resource_id == "replogle":
        from vpcm_data.replogle import ReplogleLoader

        return ReplogleLoader(fixture_mode=fixture_mode)
    if resource_id == "norman":
        from vpcm_data.norman import NormanLoader

        return NormanLoader(fixture_mode=fixture_mode)
    if resource_id == "adamson":
        from vpcm_data.adamson import AdamsonLoader

        return AdamsonLoader(fixture_mode=fixture_mode)
    if resource_id == "tahoe_100m":
        from vpcm_data.tahoe_100m import Tahoe100MLoader

        return Tahoe100MLoader(fixture_mode=fixture_mode)
    if resource_id == "xatlas_orion":
        from vpcm_data.xatlas_orion import XAtlasOrionLoader

        return XAtlasOrionLoader(fixture_mode=fixture_mode)
    if resource_id == "lincs_l1000":
        from vpcm_data.lincs_l1000 import LINCSL1000Loader

        return LINCSL1000Loader(fixture_mode=fixture_mode)
    if resource_id == "gdsc":
        from vpcm_data.gdsc_prism import GDSCLoader

        return GDSCLoader(fixture_mode=fixture_mode)
    if resource_id == "prism":
        from vpcm_data.gdsc_prism import PRISMLoader

        return PRISMLoader(fixture_mode=fixture_mode)
    if resource_id == "tcga":
        from vpcm_data.tcga import TCGALoader

        return TCGALoader(fixture_mode=fixture_mode)
    if resource_id == "cri_iatlas":
        from vpcm_data.cri_iatlas import CRIiAtlasLoader

        return CRIiAtlasLoader(fixture_mode=fixture_mode)
    if resource_id == "tabula_sapiens":
        from vpcm_data.tabula_sapiens import TabulaSapiensLoader

        return TabulaSapiensLoader(fixture_mode=fixture_mode)
    return BaseDatasetLoader(get_resource(resource_id), fixture_mode=fixture_mode)


class DatasetCatalog:
    """Single API facade across LaminDB, Census, and fixture-backed resources."""

    def __init__(
        self,
        fixture_mode: bool = True,
        resource_ids: Optional[Iterable[str]] = None,
    ) -> None:
        selected_ids = (
            list(resource_ids) if resource_ids is not None else list(DATASET_INVENTORY)
        )
        self.fixture_mode = fixture_mode
        self.loaders = {
            resource_id: _loader_for(resource_id, fixture_mode=fixture_mode)
            for resource_id in selected_ids
        }

    def list_resources(self) -> list[DatasetResource]:
        """Return resources available through this catalog."""

        return [loader.resource for loader in self.loaders.values()]

    def query(self, resource_id: str, **filters: JSONValue) -> AnnDataLike:
        """Query a harmonized resource by ID."""

        return self.loaders[resource_id].load(**filters)

    def assert_all_queryable(self) -> None:
        """Load a tiny fixture from every Phase 1 resource."""

        for resource_id in self.loaders:
            self.query(resource_id, max_cells=2)

    def manifests(self) -> list[dict[str, JSONValue]]:
        """Return loader manifests for LaminDB registration."""

        return [loader.manifest() for loader in self.loaders.values()]
