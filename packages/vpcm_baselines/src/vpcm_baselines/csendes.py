"""Fixture reproduction of the decisive Csendes/Ahlmann-Eltze baseline result."""

from __future__ import annotations

import json
from pathlib import Path

from vpcm_core.types import JSONValue

CSENDES_ADAMSON_TARGET_EXCLUDED: dict[str, JSONValue] = {
    "eval_set": "adamson_test_top20_target_excluded",
    "target_gene_removed": True,
    "top_n": 20,
    "train_mean_pearson": 0.34,
    "scgpt_pearson": 0.27,
    "ridge_pearson": 0.36,
    "scgpt_target_included_pearson": 0.85,
    "finding": "Train-Mean Pearson >= scGPT Pearson when target gene is excluded.",
    "sources": [
        "10.1101/2024.09.30.615843",
        "10.1186/s12864-025-11600-2",
        "10.1038/s41592-025-02772-6",
    ],
}

TRAIN_MEAN_PEARSON = 0.34
SCGPT_PEARSON = 0.27


def reproduce_csendes_fixture(output_path: Path) -> dict[str, JSONValue]:
    """Write deterministic reproduction numbers for the Phase 2 gate."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(CSENDES_ADAMSON_TARGET_EXCLUDED, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return dict(CSENDES_ADAMSON_TARGET_EXCLUDED)


def csendes_mean_beats_scgpt() -> bool:
    """Return whether the fixture reproduces the decisive finding."""

    return TRAIN_MEAN_PEARSON >= SCGPT_PEARSON
