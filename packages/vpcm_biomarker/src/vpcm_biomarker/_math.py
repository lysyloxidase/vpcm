"""Small deterministic math helpers for biomarker fixtures."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from vpcm_core.types import JSONValue

Vector = list[float]


def stable_float(*parts: object) -> float:
    """Return a deterministic float in [0, 1]."""

    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def mean(values: Vector) -> float:
    """Return arithmetic mean, or zero for an empty vector."""

    if not values:
        return 0.0
    return sum(values) / len(values)


def normalize_proportions(proportions: Mapping[str, float]) -> dict[str, float]:
    """Normalize cell-type proportions to sum to one."""

    total = sum(max(value, 0.0) for value in proportions.values())
    if total <= 0.0:
        raise ValueError("At least one positive cell-type proportion is required.")
    return {
        cell_type: max(value, 0.0) / total
        for cell_type, value in proportions.items()
    }


def top_genes_by_abs(delta: Vector, gene_ids: list[str], top_n: int) -> list[str]:
    """Return top genes by absolute delta."""

    ranked = sorted(range(len(delta)), key=lambda index: (-abs(delta[index]), index))
    return [gene_ids[index] for index in ranked[:top_n]]


def direction(value: float) -> str:
    """Return up/down/neutral label."""

    if value > 0.0:
        return "up"
    if value < 0.0:
        return "down"
    return "neutral"


def numeric_covariate_signal(covariates: Mapping[str, JSONValue]) -> float:
    """Collapse numeric clinical covariates into a small deterministic signal."""

    signal = 0.0
    for key, value in sorted(covariates.items()):
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            signal += float(value) * 0.0005
        elif isinstance(value, str):
            signal += (stable_float(key, value) - 0.5) * 0.01
    return signal

