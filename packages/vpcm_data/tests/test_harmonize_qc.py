from __future__ import annotations

import unittest

from vpcm_data.base import AnnDataLike, make_fixture_adata
from vpcm_data.batch_detection import detect_batch_effects
from vpcm_data.harmonize import IDHarmonizer, synthetic_gene_mapping
from vpcm_data.qc import run_qc


class HarmonizeQCTest(unittest.TestCase):
    def test_gene_id_roundtrip_matches_1000_random_like_genes(self) -> None:
        harmonizer = IDHarmonizer()
        mappings = synthetic_gene_mapping(size=1000)
        harmonizer.register_gene_mappings(mappings)

        self.assertEqual(harmonizer.roundtrip_gene_ids(mappings.keys()), 1.0)

    def test_patient_identity_is_stable_and_hipaa_safe(self) -> None:
        harmonizer = IDHarmonizer()

        first_uuid, first_hash = harmonizer.patient_identity(b"patient h5ad")
        second_uuid, second_hash = harmonizer.patient_identity(b"patient h5ad")

        self.assertEqual(first_uuid, second_uuid)
        self.assertEqual(first_hash, second_hash)
        self.assertEqual(len(first_hash), 64)

    def test_qc_and_batch_detection_pass_balanced_fixture(self) -> None:
        adata = make_fixture_adata("fixture", n_obs=8, n_vars=12)

        qc_report = run_qc(adata)
        batch_report = detect_batch_effects(adata)

        self.assertTrue(qc_report.passed)
        self.assertFalse(batch_report.flagged)
        self.assertGreaterEqual(batch_report.ilisi, 1.5)

    def test_qc_and_batch_detection_flag_bad_inputs(self) -> None:
        empty = AnnDataLike(obs=[], var_names=[], x_shape=(0, 1))

        qc_report = run_qc(empty)
        batch_report = detect_batch_effects(empty)

        self.assertFalse(qc_report.passed)
        self.assertTrue(qc_report.errors)
        self.assertTrue(batch_report.flagged)

    def test_harmonizer_validates_gene_and_drug_ids(self) -> None:
        harmonizer = IDHarmonizer()

        with self.assertRaises(ValueError):
            harmonizer.normalize_ensembl("BAD")
        with self.assertRaises(ValueError):
            harmonizer.register_drug("BAD", "inchikey", "CC")

        harmonizer.register_drug("CHEMBL25", "BSYNRYMUTXBXSQ-UHFFFAOYSA-N", "CC")
        self.assertEqual(harmonizer.drug_identity("chembl25").chembl_id, "CHEMBL25")


if __name__ == "__main__":
    unittest.main()
