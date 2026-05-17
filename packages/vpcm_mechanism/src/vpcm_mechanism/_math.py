"""Small deterministic math helpers for mechanism fixtures."""

from __future__ import annotations

import hashlib

Vector = list[float]


def stable_float(*parts: object) -> float:
    """Return a deterministic float in [0, 1]."""

    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def mean(values: Vector) -> float:
    """Return the arithmetic mean."""

    if not values:
        raise ValueError("Cannot take the mean of an empty vector.")
    return sum(values) / len(values)


def centered(values: Vector) -> Vector:
    """Return values centered by their mean."""

    value_mean = mean(values)
    return [value - value_mean for value in values]


def standard_deviation(values: Vector) -> float:
    """Return population standard deviation."""

    if not values:
        raise ValueError("Cannot take standard deviation of an empty vector.")
    value_mean = mean(values)
    variance = sum((value - value_mean) ** 2 for value in values) / len(values)
    return variance**0.5


def rank_values(values: Vector) -> Vector:
    """Return average-free deterministic ranks for a vector."""

    ordered = sorted(range(len(values)), key=lambda index: (values[index], index))
    ranks = [0.0 for _ in values]
    for rank, index in enumerate(ordered, start=1):
        ranks[index] = float(rank)
    return ranks


def spearman(values_a: Vector, values_b: Vector) -> float:
    """Return Spearman correlation for two equal-length vectors."""

    if len(values_a) != len(values_b):
        raise ValueError("Spearman correlation requires equal-length vectors.")
    if not values_a:
        raise ValueError("Spearman correlation requires non-empty vectors.")
    ranks_a = centered(rank_values(values_a))
    ranks_b = centered(rank_values(values_b))
    denom_a = sum(value * value for value in ranks_a) ** 0.5
    denom_b = sum(value * value for value in ranks_b) ** 0.5
    denominator = denom_a * denom_b
    if denominator == 0.0:
        return 0.0
    return sum(a * b for a, b in zip(ranks_a, ranks_b)) / denominator


def top_indices_by_abs(values: Vector, top_n: int) -> list[int]:
    """Return indices for the largest absolute values."""

    return sorted(
        range(len(values)),
        key=lambda index: (-abs(values[index]), index),
    )[:top_n]


def direction(value: float) -> str:
    """Return up/down/neutral direction label."""

    if value > 0.0:
        return "up"
    if value < 0.0:
        return "down"
    return "neutral"

