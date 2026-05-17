"""Batch-effect detection metrics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from vpcm_data.base import AnnDataLike


@dataclass(frozen=True)
class BatchDetectionReport:
    """Batch detection result with iLISI/kBET-style flags."""

    ilisi: float
    kbet_rejection_rate: float
    flagged: bool
    messages: list[str]


def compute_ilisi(adata: AnnDataLike, batch_key: str = "batch") -> float:
    """Compute a deterministic inverse Simpson diversity proxy for iLISI."""

    batches = [str(observation.get(batch_key, "missing")) for observation in adata.obs]
    if not batches:
        return 0.0
    counts = Counter(batches)
    total = float(len(batches))
    concentration = sum((count / total) ** 2 for count in counts.values())
    if concentration == 0.0:
        return 0.0
    return 1.0 / concentration


def compute_kbet_rejection_rate(adata: AnnDataLike, batch_key: str = "batch") -> float:
    """Compute a lightweight kBET-style imbalance flag proxy."""

    batches = [str(observation.get(batch_key, "missing")) for observation in adata.obs]
    if not batches:
        return 0.0
    counts = Counter(batches)
    majority_fraction = max(counts.values()) / len(batches)
    return max(0.0, majority_fraction - 0.5) * 2.0


def detect_batch_effects(
    adata: AnnDataLike,
    ilisi_minimum: float = 1.5,
    kbet_maximum: float = 0.25,
) -> BatchDetectionReport:
    """Return iLISI/kBET batch-effect flags."""

    ilisi = compute_ilisi(adata)
    kbet = compute_kbet_rejection_rate(adata)
    messages: list[str] = []
    if ilisi < ilisi_minimum:
        messages.append("iLISI below minimum")
    if kbet > kbet_maximum:
        messages.append("kBET rejection above maximum")
    return BatchDetectionReport(
        ilisi=ilisi,
        kbet_rejection_rate=kbet,
        flagged=bool(messages),
        messages=messages,
    )
