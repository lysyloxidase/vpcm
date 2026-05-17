from __future__ import annotations

import unittest

from vpcm_data.adamson import AdamsonLoader
from vpcm_data.base import BaseDatasetLoader, DatasetUnavailableError
from vpcm_data.cellxgene_census import CellxGeneCensusLoader
from vpcm_data.cri_iatlas import CRIiAtlasLoader
from vpcm_data.gdsc_prism import GDSCLoader, PRISMLoader
from vpcm_data.lincs_l1000 import LINCSL1000Loader
from vpcm_data.norman import NormanLoader
from vpcm_data.registry import get_resource
from vpcm_data.replogle import ReplogleLoader
from vpcm_data.sci_plex import SciPlexLoader
from vpcm_data.scperturb import scPerturbLoader
from vpcm_data.tabula_sapiens import TabulaSapiensLoader
from vpcm_data.tahoe_100m import Tahoe100MLoader
from vpcm_data.tcga import TCGALoader
from vpcm_data.xatlas_orion import XAtlasOrionLoader


class LoaderTest(unittest.TestCase):
    def test_named_loader_methods_return_harmonized_fixtures(self) -> None:
        census = CellxGeneCensusLoader()
        disease_slice = census.query_by_disease("melanoma", max_cells=4)
        neighbors = census.retrieve_neighbors(disease_slice, k=5)

        fixtures = [
            disease_slice,
            neighbors,
            scPerturbLoader().load_unified("adamson_2016"),
            SciPlexLoader().load_compound("CHEMBL25", "A549"),
            ReplogleLoader().load_cell_line("K562"),
            NormanLoader().load_dual_knockout("CEBPA", "SPI1"),
            AdamsonLoader().load_upr_screen(),
            Tahoe100MLoader().load_drug_slice("CHEMBL25", max_cells=4),
            XAtlasOrionLoader().load_gene("ENSG00000000001"),
            LINCSL1000Loader().load_signature("trichostatin-a"),
            GDSCLoader().load_drug("CHEMBL25"),
            PRISMLoader().load_drug("CHEMBL25"),
            TCGALoader().load_cohort("SKCM"),
            CRIiAtlasLoader().load_immunotherapy_cohort("anti-PD1"),
            TabulaSapiensLoader().load_tissue("lung"),
        ]

        self.assertTrue(all(fixture.n_obs > 0 for fixture in fixtures))
        self.assertIn("leave_cell_line_out", ReplogleLoader().split_plan())

    def test_loader_error_branches_are_explicit(self) -> None:
        with self.assertRaises(KeyError):
            scPerturbLoader().load_unified("missing_dataset")
        with self.assertRaises(ValueError):
            SciPlexLoader().load_compound("CHEMBL25", "BAD")
        with self.assertRaises(ValueError):
            ReplogleLoader().load_cell_line("BAD")
        with self.assertRaises(DatasetUnavailableError):
            BaseDatasetLoader(get_resource("gtex"), fixture_mode=False).load()


if __name__ == "__main__":
    unittest.main()

