# V&V40 Dossier

## Verification Gates

1. `make smoke-test` passes with deterministic mode enabled.
2. All 20 datasets are queryable through `DatasetCatalog`.
3. Ensembl <-> HGNC roundtrip reaches 100% on 1000 deterministic test genes.
4. Patient h5ad SHA-256 hash is stable across runs.
5. Audit log entry round-trips through Ed25519 sign + verify.
6. Fixed-seed batch statistics are bit-identical with cosine similarity
   >= 0.999999.
7. `ruff` and `pyright --strict` pass.
8. Coverage is >=85% for `vpcm_core` and `vpcm_data`.
9. Nightly DOI verification passes for Markdown references in `docs/`.

## Validation Gates

Later phases will bind these verification gates to perturbation prediction,
OOD refusal, conformal coverage, pathway projection, biomarker projection, and
outcome modeling evidence.

## Phase 2 Quality Gates

1. All five foundation models are represented in `FOUNDATION_MODELS`.
2. Estimated frozen ensemble memory is <=80 GB BF16/FP16.
3. Each fixture adapter reproduces its paper headline threshold within 2%.
4. `TrainMeanBaseline` returns the queried cell type mean and ignores
   intervention identity.
5. `RidgeBaseline` fits PCA(50) plus perturbation x cell-type one-hot features.
6. `data/baselines/csendes_repro.json` records Train-Mean >= scGPT on Adamson
   top-20 DE genes with perturbation target excluded.
7. `BaselineReport` validates mandatory deltas and target-gene removal.
8. Ruff, pyright strict, pytest, coverage, and DOI checks pass.

## Phase 3 Quality Gates

1. CPA, ChemCPA, GEARS, CellOT, and scGen wrappers load and predict on dummy
   data.
2. `PerturbationEnsemble` returns 100 MC-dropout samples by default.
3. MC-dropout produces non-zero per-gene standard deviation.
4. Every ensemble prediction includes a validated `BaselineReport`.
5. Norman unseen-double evaluation either beats train-mean by >=0.10 Pearson
   delta or reports transparent failure.
6. `InterventionalSupportManifold` builds from scPerturb, sci-Plex, Tahoe-100M,
   and LINCS-style profiles.
7. Tau calibration reaches refusal recall >=0.95 and in-support FPR <=0.05 in
   fixture splits.
8. Out-of-support queries return `RefusalReport` with Pearl identifiability
   note and nearest training intervention.
9. Audit logs capture refusal events and the full reasoning trace.
10. Ruff, pyright strict, pytest, coverage, and DOI checks pass.

## Phase 4 Quality Gates

1. Split conformal marginal coverage at alpha=0.1 lies in [0.88, 0.92].
2. Mondrian conformal conditional coverage per cell type lies in [0.88, 0.92].
3. CQR per-gene intervals are tighter on low-variance genes.
4. Coverage audit raises a recalibration alarm outside the V&V40 band.
5. Patient LoRA trainer handles 5,000 patient cells plus 50,000 atlas
   neighbors within the H100 30-minute budget fixture.
6. LoRA VRAM overhead is <=1 GB per patient x cell-type adapter.
7. Patient covariate encoder handles missing channels gracefully.
8. Ancestry-stratified PRS weights load and apply correctly.
9. Audit log captures every LoRA adapter fit with hyperparameter trace.
10. Ruff, pyright strict, pytest, coverage, and DOI checks pass.

## Phase 5 Quality Gates

1. decoupleR-style pathway projection returns top-10 pathways and TF
   activities with FDR <0.05.
2. CellOracle-style GRN simulation cross-validates delta direction with
   Spearman concordance >=0.6 on top genes.
3. Attention attribution emits the co-expression-not-causation caveat for
   every gene attribution.
4. CIBERSORTx-style deconvolution benchmark error is <=5%.
5. Organ ridge heads return held-out Pearson fixture >=0.60.
6. Bagaev TME classification fixture macro-F1 is >=0.70.
7. Exhaustion and IFN-gamma signature fixtures meet Spearman/AUROC gates.
8. CellChat v2, LIANA+, NicheNet, TCR, and spatial heads run on dummy data.
9. Audit logs capture mechanism and biomarker projections with method traces.
10. Ruff, pyright strict, pytest, coverage, and DOI checks pass.

## Phase 6 Quality Gates

1. DeepSurv TCGA-style held-out C-index fixture is >=0.70.
2. DeepHit competing-risks C-index fixture is >=0.65.
3. Immunotherapy response classifier pooled held-out AUROC fixture is >=0.72.
4. End-to-end `VPCM.predict()` runs in <60 seconds excluding LoRA fit.
5. Signed report JSON round-trips through Ed25519 verification.
6. Report PDF-like artifact contains all 10 required sections, including the
   mandatory Section F beat-the-mean / beat-ridge section.
7. Synthetic OOD intervention returns `RefusalReport`.
8. FastAPI fixture service handles 10 concurrent prediction calls.
9. Audit log captures every prediction with provenance.
10. Two identical fixed-seed fixture runs produce identical signed reports.
11. Ruff, pyright strict, pytest, coverage, and DOI checks pass.
