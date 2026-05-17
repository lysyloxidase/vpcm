from __future__ import annotations

import unittest

from vpcm_data.base import make_fixture_adata
from vpcm_models.loaders import FoundationModelEnsemble, FoundationModelLoadError
from vpcm_models.registry import (
    FOUNDATION_MODELS,
    PAPER_REPRODUCTION_GATES,
    total_fp16_memory_gb,
    validate_registry,
)


class FoundationModelEnsembleTest(unittest.TestCase):
    def test_registry_contains_five_models_and_fits_h100_budget(self) -> None:
        validate_registry()

        self.assertEqual(list(FOUNDATION_MODELS), [
            "scgpt",
            "scfoundation",
            "geneformer_v2",
            "uce",
            "cellplm",
        ])
        self.assertLessEqual(total_fp16_memory_gb(), 80.0)
        self.assertEqual(set(FOUNDATION_MODELS), set(PAPER_REPRODUCTION_GATES))

    def test_fixture_ensemble_embeds_every_model(self) -> None:
        adata = make_fixture_adata("fm_fixture", n_obs=2, n_vars=6)
        ensemble = FoundationModelEnsemble(device="cpu", dtype="bfloat16")

        embeddings = ensemble.embed(adata)

        self.assertEqual(set(embeddings), set(FOUNDATION_MODELS))
        for model_name, matrix in embeddings.items():
            self.assertEqual(len(matrix), adata.n_obs)
            self.assertEqual(
                len(matrix[0]),
                FOUNDATION_MODELS[model_name].get("embedding_dim"),
            )
        self.assertLess(ensemble.measure_embedding_latency_ms(adata, "cellplm"), 50.0)

    def test_paper_reproduction_gates_pass_in_fixture_mode(self) -> None:
        ensemble = FoundationModelEnsemble(device="cpu", dtype="bfloat16")

        self.assertTrue(all(ensemble.reproduce_all_paper_scores().values()))

    def test_live_loading_requires_explicit_runtime_dependencies(self) -> None:
        with self.assertRaises(FoundationModelLoadError):
            FoundationModelEnsemble(device="cpu", dtype="bfloat16", fixture_mode=False)


if __name__ == "__main__":
    unittest.main()
