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

