# Architecture

VPCM is organized as a staged monorepo:

- Phase 1: `vpcm_core` and `vpcm_data` establish governance, provenance,
  reproducibility, and harmonized data access.
- Phase 2: `vpcm_models` and `vpcm_baselines` add the foundation-model
  ensemble and mandatory beat-the-mean controls.
- Phase 3: `vpcm_perturbation` and `vpcm_causal` will add perturbation
  predictors and the do-calculus refusal gate.
- Phase 4: `vpcm_conformal` and `vpcm_lora` will add uncertainty and
  patient-specific adapters.
- Phase 5: `vpcm_mechanism` and `vpcm_biomarker` will add pathway and biomarker
  projection.
- Phase 6: `vpcm_outcome` and `vpcm_pipeline` will add outcome modeling and
  orchestration.
- Phase 7: `vpcm_regulatory` will generate the V&V40 dossier.

The Phase 1 data layer routes every resource through `DatasetCatalog`, which
can operate in deterministic fixture mode or hand off to source-specific live
loaders once credentials and large data dependencies are configured.

The Phase 2 model layer routes all single-cell foundation model embeddings
through `FoundationModelEnsemble`. Fixture adapters are deterministic and
frozen; live adapters require explicit checkpoint review, Hugging Face runtime
dependencies, and GPU memory validation. Every perturbation prediction must
carry a `BaselineReport` comparing VPCM to train-mean and ridge baselines.
