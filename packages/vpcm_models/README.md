# vpcm_models

Phase 2 five-model single-cell foundation model ensemble.

The package exposes `FoundationModelEnsemble` plus a registry for scGPT,
scFoundation, Geneformer V2, UCE, and CellPLM. Fixture mode is deterministic
and frozen for CI; live checkpoint loading is gated behind optional Hugging
Face/PyTorch dependencies and GPU memory validation.
