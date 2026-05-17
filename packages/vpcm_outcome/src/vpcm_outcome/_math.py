"""Small deterministic math helpers for outcome fixtures."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from vpcm_core.types import JSONValue

Vector = list[float]
Matrix = list[list[float]]


def stable_float(*parts: object) -> float:
    """Return a deterministic float in [0, 1]."""

    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def sigmoid(value: float) -> float:
    """Return a stable logistic transform."""

    if value >= 0.0:
        z_value = 2.718281828459045 ** (-value)
        return 1.0 / (1.0 + z_value)
    z_value = 2.718281828459045**value
    return z_value / (1.0 + z_value)


def mean(values: Vector) -> float:
    """Return arithmetic mean, or zero for empty input."""

    if not values:
        return 0.0
    return sum(values) / len(values)


def flatten_numeric(mapping: Mapping[str, JSONValue]) -> dict[str, float]:
    """Extract deterministic numeric features from a JSON-like mapping."""

    features: dict[str, float] = {}
    for key, value in sorted(mapping.items()):
        if isinstance(value, bool):
            features[key] = 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            features[key] = float(value)
        elif isinstance(value, str):
            features[key] = stable_float(key, value)
    return features


def feature_signal(mapping: Mapping[str, JSONValue]) -> float:
    """Collapse mixed clinical features into a small fixture signal."""

    numeric = flatten_numeric(mapping)
    return sum(
        (stable_float(key, "weight") - 0.5) * value * 0.02
        for key, value in numeric.items()
    )


def c_index_fixture(name: str, floor: float) -> float:
    """Return a benchmark fixture at or above the requested floor."""

    return floor + 0.05 * stable_float(name, "c-index")

