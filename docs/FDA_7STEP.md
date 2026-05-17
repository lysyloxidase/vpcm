# FDA 7-Step Credibility Mapping

| Step | VPCM v1.0.0 Evidence |
|---|---|
| 1. Question of Interest | Will intervention z administered to patient x produce >=30% tumor-cell viability reduction, >=1.5x CD8+ T-cell infiltration, and composite PFS >=6 months? |
| 2. Context of Use | Clinical-trial enrichment / patient-stratification hypothesis generation. |
| 3. Risk Assessment | High influence x Moderate consequence -> SIGNIFICANT tier. |
| 4. Credibility Plan | Monorepo governance, deterministic execution, provenance, audit logs, dataset inventory, foundation-model registry, mandatory train-mean/ridge baselines, perturbation ensemble, do-calculus refusal gate, conformal UQ, patient LoRA adapters, mechanism heads, biomarker projection, outcome heads, signed reports, and strict CI. |
| 5. Execute Plan | Phase 1-7 tests, prospective benchmark fixture, DOI verification, coverage, pyright strict, and ruff provide verification evidence. |
| 6. Credibility Report | `VV40DossierGenerator`, `SignedModelCard`, `VPCMReportGenerator`, and `FDATypeCPackage` generate the documented evidence bundle. |
| 7. Adequacy Decision | Adequate only when all thresholds pass, OOD refusal recall >=0.95, in-support refusal FPR <=0.05, and conformal coverage remains in the [0.88, 0.92] band. |

The Type C package asks FDA six yes/no questions about COU risk tier,
baseline transparency, conformal coverage, do-calculus refusal, external
validation adequacy, frozen foundation-model weights with LoRA adapters,
ancestry-stratified PRS fairness, and evidence needed for any future
decision-support COU.
