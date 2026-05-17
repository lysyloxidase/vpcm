from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vpcm_core.config import default_config, hydra_overrides, write_default_config


class ConfigTest(unittest.TestCase):
    def test_context_of_use_allows_only_declared_uses(self) -> None:
        config = default_config()

        self.assertTrue(
            config.context_of_use.is_use_allowed(
                "Drug-repurposing hypothesis generation"
            )
        )
        self.assertFalse(config.context_of_use.is_use_allowed("Diagnosis"))

    def test_hydra_overrides_and_yaml_export(self) -> None:
        config = default_config()
        overrides = hydra_overrides(config)

        self.assertIn("reproducibility.seed=42", overrides)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "default.yaml"
            write_default_config(path)

            self.assertIn("context_of_use:", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

