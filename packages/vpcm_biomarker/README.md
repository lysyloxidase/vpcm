# vpcm_biomarker

Phase 5 biomarker projection heads:

- `CIBERSORTxProjector` for cell-type-proportion weighted pseudo-bulk delta.
- `OrganRidgeProjectors` for per-organ clinical lab projections.
- `TMESignatureHeads` for Bagaev TME type, exhaustion, IFN-gamma, TMB, and
  responder probability fixtures.
- `TCRRepertoireHead` and `SpatialTranscriptomicsIntegrator` for optional
  matched TCR-seq and spatial transcriptomics context.

The default implementation is deterministic fixture mode. Optional live
backends are declared under the `bio` extra.
