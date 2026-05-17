from __future__ import annotations

import unittest

from vpcm_core.reproducibility import (
    batch_statistics,
    cosine_similarity,
    deterministic_vector,
    set_deterministic_mode,
)


class ReproducibilityTest(unittest.TestCase):
    def test_fixed_seed_batch_statistics_are_bit_identical(self) -> None:
        set_deterministic_mode(42)
        first = batch_statistics(deterministic_vector(seed=42, length=256))

        set_deterministic_mode(42)
        second = batch_statistics(deterministic_vector(seed=42, length=256))

        self.assertEqual(first, second)
        self.assertGreaterEqual(
            cosine_similarity(first.as_vector(), second.as_vector()),
            0.999999,
        )

    def test_statistics_edge_cases_are_deterministic(self) -> None:
        empty = batch_statistics(())

        self.assertEqual(empty.as_vector(), (0.0, 0.0, 0.0, 0.0))
        self.assertEqual(cosine_similarity((), ()), 1.0)
        self.assertEqual(cosine_similarity((0.0,), (1.0,)), 0.0)
        with self.assertRaises(ValueError):
            cosine_similarity((1.0,), (1.0, 2.0))


if __name__ == "__main__":
    unittest.main()
