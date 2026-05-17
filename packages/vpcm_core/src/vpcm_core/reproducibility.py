"""Deterministic execution utilities."""

from __future__ import annotations

import importlib
import os
import random
from collections.abc import Sequence
from dataclasses import dataclass
from math import sqrt
from typing import Any, Optional


@dataclass(frozen=True)
class BatchStatistics:
    """Small deterministic summary used by smoke tests and V&V evidence."""

    count: int
    mean: float
    variance: float
    l2_norm: float

    def as_vector(self) -> Sequence[float]:
        """Return the statistic vector for cosine comparison."""

        return (float(self.count), self.mean, self.variance, self.l2_norm)


def _optional_module(module_name: str) -> Optional[Any]:
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def set_deterministic_mode(seed: int = 42) -> None:
    """Set CUDA / Python / NumPy / PyTorch deterministic mode.

    Required for V&V40 Verification - Calculation evidence and for
    bit-reproducibility on fixed seed. Python-only environments still receive
    deterministic standard-library seeding; NumPy/PyTorch hooks are applied
    when those packages are installed.
    """

    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    random.seed(seed)

    numpy_module = _optional_module("numpy")
    if numpy_module is not None:
        numpy_module.random.seed(seed)

    torch_module = _optional_module("torch")
    if torch_module is None:
        return

    torch_module.manual_seed(seed)
    torch_module.cuda.manual_seed_all(seed)
    torch_module.use_deterministic_algorithms(True, warn_only=False)
    torch_module.backends.cudnn.deterministic = True
    torch_module.backends.cudnn.benchmark = False


def deterministic_vector(seed: int, length: int) -> Sequence[float]:
    """Generate a deterministic vector without scientific dependencies."""

    rng = random.Random(seed)
    return tuple(rng.random() for _ in range(length))


def batch_statistics(values: Sequence[float]) -> BatchStatistics:
    """Compute deterministic batch statistics for verification evidence."""

    count = len(values)
    if count == 0:
        return BatchStatistics(count=0, mean=0.0, variance=0.0, l2_norm=0.0)
    mean = sum(values) / count
    variance = sum((value - mean) ** 2 for value in values) / count
    l2_norm = sqrt(sum(value * value for value in values))
    return BatchStatistics(
        count=count,
        mean=mean,
        variance=variance,
        l2_norm=l2_norm,
    )


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """Return cosine similarity with stable zero-vector handling."""

    if len(left) != len(right):
        raise ValueError("Vectors must have the same length.")
    dot_product = sum(
        left_value * right_value for left_value, right_value in zip(left, right)
    )
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 and right_norm == 0.0:
        return 1.0
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)
