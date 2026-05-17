# vpcm_mechanism

Phase 5 mechanism-of-action interpretation heads:

- `DecouplerPathwayProjector` for PROGENy, DoRothEA, Reactome, KEGG, and
  WikiPathways-style pathway/TF projection.
- `CellOracleGRNSimulator` for GRN propagation cross-validation.
- `CellChatV2Communicator` for CellChat v2, LIANA+, and NicheNet-style
  ligand-receptor communication changes.
- `AttentionAttributionWithCaveat` for correlational attention attribution
  with mandatory causality caveats.

The default implementation is deterministic fixture mode. Optional live
backends are declared under the `bio` extra.
