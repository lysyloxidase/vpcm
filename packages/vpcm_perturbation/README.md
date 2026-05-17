# vpcm_perturbation

Phase 3 perturbation predictor ensemble.

The package wraps CPA, ChemCPA, GEARS, CellOT, and scGen behind a common
`PerturbationEnsemble` API. Fixture mode returns deterministic delta-expression
vectors with MC-dropout uncertainty and mandatory baseline deltas.
