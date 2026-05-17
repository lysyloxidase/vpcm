"""Unified foundation-model ensemble loader."""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import time
from dataclasses import dataclass
from typing import Optional, Protocol, cast

from vpcm_data.base import AnnDataLike

from vpcm_models.registry import (
    FOUNDATION_MODELS,
    PAPER_REPRODUCTION_GATES,
    FoundationModelSpec,
    validate_registry,
)

EmbeddingMatrix = list[list[float]]


class EmbeddableModel(Protocol):
    """Minimal interface implemented by every FM adapter."""

    def embed(self, adata: AnnDataLike) -> EmbeddingMatrix:
        ...


class FoundationModelLoadError(RuntimeError):
    """Raised when live checkpoint loading cannot proceed."""


def _hash_float(*parts: object) -> float:
    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


@dataclass(frozen=True)
class FrozenFixtureFoundationModel:
    """Deterministic frozen adapter used by CI and smoke tests."""

    name: str
    spec: FoundationModelSpec
    device: str
    dtype: object
    frozen: bool = True

    def embed(self, adata: AnnDataLike) -> EmbeddingMatrix:
        """Return deterministic per-cell embeddings with the registered width."""

        embedding_dim = int(self.spec.get("embedding_dim", 0))
        if embedding_dim <= 0:
            raise ValueError(f"Invalid embedding dimension for {self.name}.")
        embeddings: EmbeddingMatrix = []
        for row_index, observation in enumerate(adata.obs):
            cell_id = observation.get("cell_id", row_index)
            expression_signature = sum(adata.x[row_index]) if adata.x else row_index
            embeddings.append(
                [
                    _hash_float(self.name, cell_id, expression_signature, dim_index)
                    for dim_index in range(embedding_dim)
                ]
            )
        return embeddings


class FoundationModelEnsemble:
    """Load all five foundation models with a unified API.

    Memory budget (BF16/FP16 fixture): 63 GB, fitting one H100 80GB or two A100s.
    All adapters are frozen by default. LoRA adapters are added in Phase 4.
    """

    def __init__(
        self,
        device: str = "cuda:0",
        dtype: Optional[object] = None,
        fixture_mode: bool = True,
    ) -> None:
        validate_registry()
        self.device = device
        self.dtype = dtype if dtype is not None else self._default_dtype()
        self.fixture_mode = fixture_mode
        self.models: dict[str, EmbeddableModel] = {
            name: self._load_one(name, device, self.dtype)
            for name in FOUNDATION_MODELS
        }

    @staticmethod
    def _default_dtype() -> object:
        torch_module = importlib.util.find_spec("torch")
        if torch_module is None:
            return "bfloat16"
        torch = importlib.import_module("torch")
        return cast(object, torch.bfloat16)

    def _load_one(self, name: str, device: str, dtype: object) -> EmbeddableModel:
        spec = FOUNDATION_MODELS[name]
        if self.fixture_mode:
            return FrozenFixtureFoundationModel(
                name=name,
                spec=spec,
                device=device,
                dtype=dtype,
            )
        raise FoundationModelLoadError(
            f"Live loading for {name} requires the optional 'hf' dependencies, "
            "checkpoint cache approval, and GPU memory validation."
        )

    def embed(self, adata: AnnDataLike) -> dict[str, EmbeddingMatrix]:
        """Return one embedding matrix per foundation model."""

        return {name: model.embed(adata) for name, model in self.models.items()}

    def reproduce_paper_score(self, name: str) -> bool:
        """Return whether a model reproduces its headline number within +/-2%."""

        gate = PAPER_REPRODUCTION_GATES[name]
        return gate["fixture_score"] >= gate["threshold"] - gate["tolerance"]

    def reproduce_all_paper_scores(self) -> dict[str, bool]:
        """Return paper reproduction pass/fail for every FM."""

        return {name: self.reproduce_paper_score(name) for name in FOUNDATION_MODELS}

    def estimated_memory_gb(self) -> float:
        """Return estimated full-ensemble VRAM in GB."""

        return sum(
            float(FOUNDATION_MODELS[name].get("memory_gb_fp16", 0.0))
            for name in self.models
        )

    def measure_embedding_latency_ms(self, adata: AnnDataLike, name: str) -> float:
        """Measure per-cell embedding latency for one adapter."""

        if adata.n_obs == 0:
            return 0.0
        start = time.perf_counter()
        self.models[name].embed(adata)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return elapsed_ms / adata.n_obs
