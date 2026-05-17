# VPCM

VPCM is a patient-specific, cell-type-specific causal perturbation prediction
system. Phase 1 establishes the monorepo, governance, MLOps tooling, and
harmonized data layer for all training and validation datasets.

The repo is intentionally usable before large data pulls are available:
loaders expose deterministic fixture mode by default, while package metadata
declares the live dependencies for CELLxGENE Census, AnnData, DVC, LaminDB,
RDKit, PyTorch, and downstream model work.

## Phase 1 Scope

- `packages/vpcm_core`: COU config, deterministic execution, audit logging,
  provenance manifests, and typed records.
- `packages/vpcm_data`: 20-resource data inventory, single catalog API,
  dataset-specific loaders, harmonization, QC, and batch detection.
- `packages/vpcm_models`: five-model single-cell foundation model ensemble
  registry and frozen fixture adapters.
- `packages/vpcm_baselines`: mandatory train-mean and ridge baselines plus
  Csendes/Ahlmann-Eltze reproduction fixtures.
- `.github/workflows`: ruff, pyright strict, pytest, coverage, and nightly DOI
  verification.
- `docs`: COU, FDA 7-step mapping, V&V40 dossier scaffold, architecture,
  research references, and data dictionary.

## Local Smoke Test

```bash
make smoke-test
```

For full CI parity:

```bash
python -m pip install -e "packages/vpcm_core[dev]"
python -m pip install -e "packages/vpcm_data[dev]"
make ruff
make pyright
make coverage
```

## Context of Use

VPCM is only intended for clinical-trial enrichment, drug-repurposing
hypothesis generation, and biomarker-strategy planning. It must not be used for
first-in-human dosing, diagnosis, primary endpoint determination, or replacing
standard-of-care clinical decision-making.
