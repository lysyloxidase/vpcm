# vpcm_regulatory

Phase 7 regulatory package:

- `VV40DossierGenerator` generates the ASME V&V 40 credibility dossier from CI
  evidence.
- `FDA7StepCredibilityMap` maps FDA-2024-D-4689 seven-step credibility
  guidance to VPCM evidence.
- `SignedModelCard` emits an Ed25519-signed v1.0.0 model card.
- `ProspectiveBlindedBenchmark` evaluates all 13 pre-registered thresholds.
- `FDATypeCPackage` assembles the Type C pre-submission briefing package.

The default implementation is deterministic fixture mode, suitable for CI and
regulatory artifact shape validation before live external validation data are
unblinded.
