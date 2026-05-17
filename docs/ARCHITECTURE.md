# Architecture

VPCM is organized as a staged monorepo:

- Phase 1: `vpcm_core` and `vpcm_data` establish governance, provenance,
  reproducibility, and harmonized data access.
- Phase 2: `vpcm_models` and `vpcm_baselines` add the foundation-model
  ensemble and mandatory beat-the-mean controls.
- Phase 3: `vpcm_perturbation` and `vpcm_causal` add perturbation predictors
  and the do-calculus refusal gate.
- Phase 4: `vpcm_conformal` and `vpcm_lora` add uncertainty and
  patient-specific adapters.
- Phase 5: `vpcm_mechanism` and `vpcm_biomarker` add pathway and biomarker
  projection.
- Phase 6: `vpcm_outcome` and `vpcm_pipeline` add outcome modeling and
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

The Phase 3 prediction layer routes CPA, ChemCPA, GEARS, CellOT, and scGen
through `PerturbationEnsemble`, returning ensemble mean delta expression,
MC-dropout standard deviation, per-model deltas, and baseline deltas. The
causal layer builds an interventional support manifold from Perturb-seq,
sci-Plex, Tahoe-100M, and LINCS anchors. Queries outside calibrated support
return `RefusalReport` instead of a causal estimate.

The Phase 4 uncertainty layer applies distribution-free conformal intervals
around any model output. `SplitConformalPredictor` provides marginal coverage,
`MondrianConformalPredictor` calibrates cell-type-specific coverage, and
`ConformalizedQuantileRegression` provides adaptive per-gene intervals.
`PatientLoRATrainer` trains frozen-foundation-model rank-8 adapters per
patient x cell type while preserving audit traces and upstream model weights.

The Phase 5 interpretation layer projects per-cell-type delta expression into
mechanism and clinical-biomarker spaces. `DecouplerPathwayProjector` returns
ranked pathways and TF activities, `CellOracleGRNSimulator` cross-validates
delta direction through GRN propagation, `CellChatV2Communicator` reports
ligand-receptor communication changes, and attention attributions always carry
a co-expression-not-causation caveat. `CIBERSORTxProjector` converts
per-cell-type deltas to pseudo-bulk tissue deltas; `OrganRidgeProjectors`,
`TMESignatureHeads`, `TCRRepertoireHead`, and
`SpatialTranscriptomicsIntegrator` project those changes to lab values, TME
state, TCR context, and spatial context.

The Phase 6 outcome layer exposes DeepSurv-style survival prediction,
DeepHit-style competing risks, conformal immunotherapy response prediction, and
optional multi-omic fusion. `VPCM.predict()` composes all prior phases into one
audited call: optional patient LoRA, do-calculus refusal, perturbation ensemble,
conformal intervals, mechanism interpretation, biomarker projection, outcome
heads, mandatory baseline deltas, signed JSON, PDF-like report bundle, and
audit/provenance outputs.
