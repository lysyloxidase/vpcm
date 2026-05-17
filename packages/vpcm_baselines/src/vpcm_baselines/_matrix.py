"""Small deterministic matrix helpers for fixture-mode baselines."""

from __future__ import annotations

from math import sqrt

Matrix = list[list[float]]
Vector = list[float]


def ensure_matrix(matrix: Matrix) -> None:
    """Validate a non-empty rectangular matrix."""

    if not matrix:
        raise ValueError("Expression matrix is empty.")
    width = len(matrix[0])
    if width == 0:
        raise ValueError("Expression matrix has zero genes.")
    if any(len(row) != width for row in matrix):
        raise ValueError("Expression matrix must be rectangular.")


def mean_vector(matrix: Matrix) -> Vector:
    """Return column means for a matrix."""

    ensure_matrix(matrix)
    n_rows = len(matrix)
    n_cols = len(matrix[0])
    return [sum(row[col] for row in matrix) / n_rows for col in range(n_cols)]


def transpose(matrix: Matrix) -> Matrix:
    """Return matrix transpose."""

    ensure_matrix(matrix)
    return [[row[col] for row in matrix] for col in range(len(matrix[0]))]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    """Multiply two matrices."""

    if not left or not right:
        return []
    right_t = transpose(right)
    return [
        [
            sum(left_value * right_value for left_value, right_value in zip(row, col))
            for col in right_t
        ]
        for row in left
    ]


def dot(left: Vector, right: Vector) -> float:
    """Return vector dot product."""

    if len(left) != len(right):
        raise ValueError("Vectors must be the same length.")
    return sum(left_value * right_value for left_value, right_value in zip(left, right))


def pearson(left: Vector, right: Vector) -> float:
    """Return Pearson correlation with stable constant-vector handling."""

    if len(left) != len(right):
        raise ValueError("Vectors must be the same length.")
    if not left:
        raise ValueError("Vectors must not be empty.")
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    left_norm = sqrt(sum(value * value for value in left_centered))
    right_norm = sqrt(sum(value * value for value in right_centered))
    if left_norm == 0.0 and right_norm == 0.0:
        return 1.0
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot(left_centered, right_centered) / (left_norm * right_norm)


def mse(left: Vector, right: Vector) -> float:
    """Return mean squared error."""

    if len(left) != len(right):
        raise ValueError("Vectors must be the same length.")
    squared_error = sum(
        (left_value - right_value) ** 2
        for left_value, right_value in zip(left, right)
    )
    return squared_error / len(left)


def mae(left: Vector, right: Vector) -> float:
    """Return mean absolute error."""

    if len(left) != len(right):
        raise ValueError("Vectors must be the same length.")
    absolute_error = sum(
        abs(left_value - right_value)
        for left_value, right_value in zip(left, right)
    )
    return absolute_error / len(left)


def gaussian_solve(matrix: Matrix, rhs: Vector) -> Vector:
    """Solve a dense linear system with Gauss-Jordan elimination."""

    ensure_matrix(matrix)
    n = len(matrix)
    if len(matrix[0]) != n or len(rhs) != n:
        raise ValueError("Linear system must be square.")
    augmented = [[*list(row), rhs[index]] for index, row in enumerate(matrix)]
    for pivot_index in range(n):
        best_index = max(
            range(pivot_index, n),
            key=lambda row_index: abs(augmented[row_index][pivot_index]),
        )
        augmented[pivot_index], augmented[best_index] = (
            augmented[best_index],
            augmented[pivot_index],
        )
        pivot = augmented[pivot_index][pivot_index]
        if abs(pivot) < 1e-12:
            raise ValueError("Linear system is singular.")
        augmented[pivot_index] = [value / pivot for value in augmented[pivot_index]]
        for row_index in range(n):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            augmented[row_index] = [
                value - factor * pivot_value
                for value, pivot_value in zip(
                    augmented[row_index],
                    augmented[pivot_index],
                )
            ]
    return [row[-1] for row in augmented]


def top_n_indices(
    reference: Vector,
    baseline: Vector,
    top_n: int,
    excluded_index: int = -1,
) -> list[int]:
    """Rank genes by absolute delta, excluding the perturbation target."""

    if len(reference) != len(baseline):
        raise ValueError("Vectors must be the same length.")
    candidates = [
        index
        for index in range(len(reference))
        if index != excluded_index
    ]
    ranked = sorted(
        candidates,
        key=lambda index: abs(reference[index] - baseline[index]),
        reverse=True,
    )
    return ranked[:top_n]


def select(vector: Vector, indices: list[int]) -> Vector:
    """Select vector indices."""

    return [vector[index] for index in indices]
