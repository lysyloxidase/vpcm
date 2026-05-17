"""Shared conformal prediction types and math helpers."""

from __future__ import annotations

from dataclasses import dataclass

Vector = list[float]
Matrix = list[list[float]]


@dataclass(frozen=True)
class PredictionIntervals:
    """Vectorized prediction interval."""

    lo: Vector
    hi: Vector

    def widths(self) -> Vector:
        """Return interval widths."""

        return [hi_value - lo_value for lo_value, hi_value in zip(self.lo, self.hi)]


def flatten(matrix: Matrix) -> Vector:
    """Flatten a matrix row-major."""

    return [value for row in matrix for value in row]


def ensure_equal_length(*vectors: Vector) -> None:
    """Validate equal vector lengths."""

    if not vectors:
        return
    length = len(vectors[0])
    if any(len(vector) != length for vector in vectors):
        raise ValueError("Vectors must have equal length.")


def safe_sigma(value: float, minimum: float = 1e-8) -> float:
    """Avoid division by zero in heteroscedastic conformal scores."""

    return max(abs(value), minimum)


def higher_quantile(values: Vector, q_level: float) -> float:
    """Return the higher empirical quantile for q in [0, 1]."""

    if not values:
        raise ValueError("Cannot compute a quantile of an empty vector.")
    if q_level < 0.0 or q_level > 1.0:
        raise ValueError("q_level must be in [0, 1].")
    ordered = sorted(values)
    raw_index = q_level * (len(ordered) - 1)
    index = int(raw_index)
    if raw_index > index:
        index += 1
    return ordered[min(index, len(ordered) - 1)]


def column(matrix: Matrix, index: int) -> Vector:
    """Return one matrix column."""

    return [row[index] for row in matrix]

