# vpcm_pipeline

Phase 6 end-to-end orchestration:

- `VPCM.predict()` composes data QC, optional LoRA, causal refusal, the
  perturbation ensemble, conformal intervals, mechanism heads, biomarker heads,
  outcome heads, and mandatory beat-the-mean/ridge reporting.
- `VPCMReport` is the machine-readable end-to-end report surface.
- `SignedReportBundle` emits deterministic Ed25519-signed JSON.
- `VPCMReportGenerator` writes `report.json`, `report.pdf`, `audit.jsonl`, and
  `provenance.yaml` bundle files.
