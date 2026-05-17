# vpcm_outcome

Phase 6 outcome heads:

- `DeepSurvHead` for Cox-PH survival prediction with hazard ratio, PFS/OS
  summaries, risk quartiles, and C-index fixtures.
- `DeepHitHead` for competing risks: progression, death from disease, death
  from other causes, and toxicity discontinuation.
- `ImmunotherapyResponseClassifier` for conformal responder probability.
- `MultiomicFusion` for optional MOFA+, totalVI, and MultiVI-style feature
  summaries.

The default implementation is deterministic fixture mode. Production pycox and
multi-omic backends are declared as optional extras.
