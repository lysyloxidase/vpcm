# vpcm_causal

Phase 3 do-calculus refusal gate.

`InterventionalSupportManifold` builds interventional support from perturbation
anchors, calibrates an OOD threshold, and returns `RefusalReport` rather than a
causal estimate when a query is outside support.
