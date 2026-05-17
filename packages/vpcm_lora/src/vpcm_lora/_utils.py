"""Small helpers shared by LoRA fixture modules."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

from vpcm_core.types import JSONValue
from vpcm_data.base import AnnDataLike

Vector = list[float]


def stable_float(*parts: object) -> float:
    """Return a deterministic float in [0, 1]."""

    joined = "::".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(joined).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64 - 1)


def stable_patient_embedding(patient_id: str, dim: int = 64) -> Vector:
    """Return a deterministic learned-embedding fixture."""

    return [stable_float(patient_id, index) - 0.5 for index in range(dim)]


def cell_type_value(observation: Mapping[str, JSONValue]) -> str:
    """Extract cell type from an observation."""

    value = observation.get("cell_type")
    if value is None:
        value = observation.get("cell_type_label", "unknown")
    return str(value)


def subset_by_cell_type(adata: AnnDataLike, cell_type: str) -> AnnDataLike:
    """Return cells matching a cell type."""

    indices = [
        index
        for index, observation in enumerate(adata.obs)
        if cell_type_value(observation) == cell_type
    ]
    return AnnDataLike(
        obs=[adata.obs[index] for index in indices],
        var_names=list(adata.var_names),
        x_shape=(len(indices), adata.n_vars),
        x=[adata.x[index] for index in indices],
        uns=adata.uns,
    )


def unique_cell_types(adata: AnnDataLike) -> list[str]:
    """Return sorted cell types present in AnnData-like observations."""

    return sorted({cell_type_value(observation) for observation in adata.obs})


def mean_expression(adata: AnnDataLike) -> Vector:
    """Return mean expression vector."""

    if not adata.x:
        return [0.0 for _ in adata.var_names]
    return [
        sum(row[col] for row in adata.x) / len(adata.x)
        for col in range(adata.n_vars)
    ]

