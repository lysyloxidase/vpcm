from __future__ import annotations

import unittest

from vpcm_data.registry import DATASET_INVENTORY, DatasetCatalog, list_resources


class DatasetCatalogTest(unittest.TestCase):
    def test_inventory_covers_all_phase1_resources(self) -> None:
        self.assertEqual(len(DATASET_INVENTORY), 20)
        self.assertTrue(
            all(resource["status"] == "LOAD" for resource in list_resources())
        )

    def test_all_datasets_queryable_through_single_catalog_api(self) -> None:
        catalog = DatasetCatalog(fixture_mode=True)

        catalog.assert_all_queryable()

        for resource_id in DATASET_INVENTORY:
            adata = catalog.query(resource_id, max_cells=3)
            self.assertEqual(adata.n_obs, 3)
            self.assertGreater(adata.n_vars, 0)
            self.assertEqual(adata.obs[0].get("source_dataset"), resource_id)

    def test_catalog_manifests_include_doi_or_source(self) -> None:
        catalog = DatasetCatalog(fixture_mode=True)

        manifests = catalog.manifests()

        self.assertEqual(len(manifests), 20)
        self.assertTrue(all("doi_or_source" in manifest for manifest in manifests))


if __name__ == "__main__":
    unittest.main()
