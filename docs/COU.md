# Context Of Use

VPCM is intended ONLY for the following clinical contexts:

1. Clinical-trial enrichment / patient-stratification hypothesis generation
2. Drug-repurposing hypothesis generation
3. Biomarker-strategy planning for clinical-trial design

VPCM is NOT intended for and MUST NOT be used for:

1. First-in-human dosing decisions
2. Primary endpoint determination
3. Patient-level treatment decisions without clinician override
4. Diagnosis
5. Replacing standard-of-care decision-making

Per FDA Draft Guidance Jan 6, 2025 (FDA-2024-D-4689) 7-step credibility
framework:

- Step 1 Question: "Will intervention z administered to patient x produce
  >=30% reduction in tumor-cell viability AND >=1.5x CD8+ T-cell infiltration
  in TME, with composite PFS >=6 months?"
- Step 2 COU: clinical-trial enrichment / patient-stratification tool
- Step 3 Risk: High influence x Moderate consequence -> SIGNIFICANT tier
- Step 4-6: Credibility plan + execution + report (Phases 1-7 of this build)
- Step 7 Adequacy: All thresholds met AND OOD refusal recall >= 0.95

