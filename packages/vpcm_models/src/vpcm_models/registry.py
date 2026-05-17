"""Registry for the five mandatory single-cell foundation models."""

from __future__ import annotations

from typing import Literal, TypedDict, Union


class FoundationModelSpec(TypedDict, total=False):
    """Foundation-model registry metadata."""

    params: int
    hf_id: str
    ckpt: str
    embedding_dim: int
    max_genes: Union[int, Literal["cell-as-token"]]
    license: str
    doi: str
    arxiv: str
    variant: str
    caveat: str
    key_feature: str
    memory_gb_fp16: float


class PaperGate(TypedDict):
    """Headline reproduction gate for each FM."""

    metric: str
    threshold: float
    fixture_score: float
    tolerance: float
    eval_set: str


FOUNDATION_MODELS: dict[str, FoundationModelSpec] = {
    "scgpt": {
        "params": 51_000_000,
        "hf_id": "bowang-lab/scGPT",
        "ckpt": "scGPT_human",
        "embedding_dim": 512,
        "max_genes": 1200,
        "license": "MIT",
        "doi": "10.1038/s41592-024-02201-0",
        "caveat": "Loses to mean baseline on Perturb-seq (Csendes 2024)",
        "memory_gb_fp16": 5.0,
    },
    "scfoundation": {
        "params": 100_000_000,
        "hf_id": "biomap-research/scFoundation",
        "ckpt": "scFoundation_v0.1",
        "embedding_dim": 512,
        "max_genes": 20_000,
        "license": "research-only",
        "doi": "10.1038/s41592-024-02305-7",
        "caveat": "Loses to mean baseline on Perturb-seq (Csendes 2025 BMC)",
        "memory_gb_fp16": 10.0,
    },
    "geneformer_v2": {
        "params": 104_000_000,
        "hf_id": "ctheodoris/Geneformer",
        "ckpt": "gf-12L-95M-i4096",
        "embedding_dim": 512,
        "max_genes": 4096,
        "license": "Apache-2.0",
        "doi": "10.1101/2024.08.16.608180",
        "variant": "V2-104M-CLcancer",
        "memory_gb_fp16": 10.0,
    },
    "uce": {
        "params": 650_000_000,
        "hf_id": "snap-stanford/UCE",
        "ckpt": "uce-33-layer",
        "embedding_dim": 5120,
        "max_genes": 4096,
        "license": "MIT",
        "doi": "10.1101/2023.11.28.568918",
        "key_feature": "Cross-species zero-shot via ESM-2 gene embeddings",
        "memory_gb_fp16": 30.0,
    },
    "cellplm": {
        "params": 80_000_000,
        "hf_id": "OmicsML/CellPLM",
        "ckpt": "CellPLM-v1.0",
        "embedding_dim": 512,
        "max_genes": "cell-as-token",
        "license": "MIT",
        "doi": "10.1101/2023.10.03.560734",
        "key_feature": "Cell-as-token (~100x faster than gene-token FMs)",
        "memory_gb_fp16": 8.0,
    },
}


PAPER_REPRODUCTION_GATES: dict[str, PaperGate] = {
    "scgpt": {
        "metric": "zero-shot PBMC annotation F1",
        "threshold": 0.79,
        "fixture_score": 0.81,
        "tolerance": 0.02,
        "eval_set": "pbmc_annotation",
    },
    "scfoundation": {
        "metric": "DeepCDR drug-response Pearson on CCLE",
        "threshold": 0.91,
        "fixture_score": 0.93,
        "tolerance": 0.02,
        "eval_set": "ccle_deepcdr",
    },
    "geneformer_v2": {
        "metric": "fine-tuned cardiomyopathy AUC",
        "threshold": 0.91,
        "fixture_score": 0.93,
        "tolerance": 0.02,
        "eval_set": "cardiomyopathy_auc",
    },
    "uce": {
        "metric": "cross-species F1",
        "threshold": 0.78,
        "fixture_score": 0.80,
        "tolerance": 0.02,
        "eval_set": "cross_species",
    },
    "cellplm": {
        "metric": "NMI",
        "threshold": 0.80,
        "fixture_score": 0.82,
        "tolerance": 0.02,
        "eval_set": "cellplm_nmi",
    },
}


def total_fp16_memory_gb() -> float:
    """Return estimated FP16/BF16 VRAM for the full frozen ensemble."""

    return sum(
        float(spec.get("memory_gb_fp16", 0.0))
        for spec in FOUNDATION_MODELS.values()
    )


def validate_registry() -> None:
    """Raise if the registry does not satisfy the Phase 2 contract."""

    if set(FOUNDATION_MODELS) != set(PAPER_REPRODUCTION_GATES):
        raise ValueError("Foundation model registry and paper gates must align.")
    if total_fp16_memory_gb() > 80.0:
        raise ValueError("Foundation model ensemble exceeds 80 GB VRAM budget.")
    for name, spec in FOUNDATION_MODELS.items():
        if "embedding_dim" not in spec or int(spec["embedding_dim"]) <= 0:
            raise ValueError(f"Invalid embedding dimension for {name}.")
        if "hf_id" not in spec:
            raise ValueError(f"Missing Hugging Face identifier for {name}.")
