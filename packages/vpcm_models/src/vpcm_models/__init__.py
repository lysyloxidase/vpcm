"""Single-cell foundation model ensemble for VPCM Phase 2."""

from vpcm_models.loaders import FoundationModelEnsemble
from vpcm_models.registry import (
    FOUNDATION_MODELS,
    PAPER_REPRODUCTION_GATES,
    total_fp16_memory_gb,
)

__all__ = [
    "FOUNDATION_MODELS",
    "PAPER_REPRODUCTION_GATES",
    "FoundationModelEnsemble",
    "total_fp16_memory_gb",
]

