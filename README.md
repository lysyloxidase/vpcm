# VPCM

First open AI/ML system with do-calculus refusal gate and FDA-grade
credibility for patient-specific perturbation prediction.

VPCM is a patient-specific, cell-type-specific causal perturbation prediction
system. Version 1.0.0 includes the full Phase 1-7 stack: harmonized data,
foundation-model ensemble, mandatory beat-the-mean baselines, perturbation
predictors, causal refusal, conformal uncertainty, patient LoRA, mechanism and
biomarker projection, outcome heads, signed prediction reports, and regulatory
dossier generation.

The repo is intentionally usable before large data pulls are available:
loaders expose deterministic fixture mode by default, while package metadata
declares the live dependencies for CELLxGENE Census, AnnData, DVC, LaminDB,
RDKit, PyTorch, and downstream model work.

## Implemented Scope

- `packages/vpcm_core`: COU config, deterministic execution, audit logging,
  provenance manifests, and typed records.
- `packages/vpcm_data`: 20-resource data inventory, single catalog API,
  dataset-specific loaders, harmonization, QC, and batch detection.
- `packages/vpcm_models`: five-model single-cell foundation model ensemble
  registry and frozen fixture adapters.
- `packages/vpcm_baselines`: mandatory train-mean and ridge baselines plus
  Csendes/Ahlmann-Eltze reproduction fixtures.
- `packages/vpcm_perturbation`: five-predictor perturbation ensemble with
  MC-dropout uncertainty.
- `packages/vpcm_causal`: interventional support manifold and do-calculus
  refusal gate.
- `packages/vpcm_conformal`: split conformal, Mondrian conformal, CQR, and
  lifecycle coverage audits.
- `packages/vpcm_lora`: patient-specific rank-8 LoRA adapters, atlas retrieval,
  and patient covariate encoding.
- `packages/vpcm_mechanism`: decoupleR-style pathway projection, CellOracle
  GRN simulation, CellChat/LIANA/NicheNet communication inference, and
  attention attribution caveats.
- `packages/vpcm_biomarker`: CIBERSORTx-style pseudo-bulk projection, organ
  ridge lab heads, Bagaev TME signatures, TCR repertoire, and spatial context.
- `packages/vpcm_outcome`: DeepSurv, DeepHit, immunotherapy response, and
  multi-omic fusion outcome heads.
- `packages/vpcm_pipeline`: single signed `VPCM.predict()` API, report bundle
  generation, provenance, and FastAPI inference entrypoint.
- `packages/vpcm_regulatory`: ASME V&V 40 dossier generator, FDA 7-step
  credibility map, signed model card, prospective blinded benchmark fixture,
  and Type C pre-submission package assembly.
- `.github/workflows`: ruff, pyright strict, pytest, coverage, and nightly DOI
  verification.
- `docs`: COU, FDA 7-step mapping, V&V40 dossier, architecture, research
  references, data dictionary, and international regulatory cross-references.

## Local Smoke Test

```bash
make smoke-test
```

For full CI parity:

```bash
python -m pip install -e "packages/vpcm_core[dev]"
python -m pip install -e "packages/vpcm_data[dev]"
python -m pip install -e "packages/vpcm_models[dev]"
python -m pip install -e "packages/vpcm_baselines[dev]"
python -m pip install -e "packages/vpcm_perturbation[dev]"
python -m pip install -e "packages/vpcm_causal[dev]"
python -m pip install -e "packages/vpcm_conformal[dev]"
python -m pip install -e "packages/vpcm_lora[dev]"
python -m pip install -e "packages/vpcm_mechanism[dev]"
python -m pip install -e "packages/vpcm_biomarker[dev]"
python -m pip install -e "packages/vpcm_outcome[dev]"
python -m pip install -e "packages/vpcm_pipeline[dev]"
python -m pip install -e "packages/vpcm_regulatory[dev]"
make ruff
make pyright
make coverage
```

## Context of Use

VPCM is only intended for clinical-trial enrichment, drug-repurposing
hypothesis generation, and biomarker-strategy planning. It must not be used for
first-in-human dosing, diagnosis, primary endpoint determination, or replacing
standard-of-care clinical decision-making.
