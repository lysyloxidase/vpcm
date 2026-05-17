# Health Canada MLMD Cross-Reference

Source checked May 17, 2026: Health Canada pre-market guidance for
machine-learning-enabled medical devices, published April 1, 2026. This
supersedes the earlier 2023 draft cited in early planning notes.

VPCM alignment:

- Risk management: Significant-tier credibility plan and ASME V&V 40 dossier.
- Data selection and management: dataset inventory, harmonization, QC, and
  provenance traces.
- Development and training: frozen foundation weights, patient LoRA adapter
  traces, and deterministic reproducibility gates.
- Testing and evaluation: pre-registered prospective benchmark thresholds.
- Clinical validation: prospective blinded cohort gate before any live claim.
- Transparency: model card, signed report JSON, Section F baseline comparison,
  and refusal explanations.
- Post-market monitoring: quarterly drift and recalibration schedule.

Reference:
https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/pre-market-guidance-machine-learning-enabled-medical-devices.html
