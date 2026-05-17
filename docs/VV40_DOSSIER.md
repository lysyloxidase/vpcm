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
