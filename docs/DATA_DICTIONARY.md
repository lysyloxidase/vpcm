# Data Dictionary

## Required Observation Columns

| Column | Meaning |
|---|---|
| `cell_id` | Source-stable cell identifier. |
| `patient_id` | Opaque patient or donor identifier. |
| `patient_hash` | SHA-256 hash of source patient h5ad bytes. |
| `disease_id` | MONDO/DOID disease identifier. |
| `disease_label` | Human-readable disease label. |
| `cell_type_id` | Cell Ontology identifier. |
| `cell_type_label` | Harmonized cell type label, compatible with scTab labels. |
| `perturbation_type` | `control`, `drug`, `genetic`, `combination`, or related type. |
| `perturbation` | ChEMBL ID, Ensembl ID, perturbation pair, or source label. |
| `dose` | Dose string for chemical perturbations when available. |
| `batch` | Batch identifier for iLISI/kBET flagging. |
| `source_dataset` | VPCM dataset resource ID. |

## Baseline Report Fields

| Field | Meaning |
|---|---|
| `mean_baseline_pearson` | Train-set cell-type mean Pearson on top-N DE genes. |
| `ridge_baseline_pearson` | Ridge/PCA Pearson on the same evaluation set. |
| `vpcm_ensemble_pearson` | VPCM ensemble Pearson on the same genes. |
| `beat_mean_delta` | `vpcm_ensemble_pearson - mean_baseline_pearson`. |
| `beat_ridge_delta` | `vpcm_ensemble_pearson - ridge_baseline_pearson`. |
| `target_gene_removed` | Must be true for fair Perturb-seq evaluation. |
| `top_n` | Number of DE genes scored, typically 20. |
| `eval_set` | Held-out split name. |

## Refusal Report Fields

| Field | Meaning |
|---|---|
| `reason` | Human-readable support failure explanation. |
| `mahalanobis_distance` | Distance to nearest interventional support cluster. |
| `nearest_training_intervention` | Closest observed interventional anchor. |
| `wide_observational_interval` | 5th-95th percentile observational interval, not causal. |
| `do_calculus_note` | Pearl-style identifiability warning. |
| `suggested_data` | Interventional experiment that would close the support gap. |

## Conformal Interval Fields

| Field | Meaning |
|---|---|
| `lo` | Lower conformal bound for each prediction target. |
| `hi` | Upper conformal bound for each prediction target. |
| `qhat` | Calibrated nonconformity quantile. |
| `alpha` | Target miscoverage rate. |

## LoRA Adapter Fields

| Field | Meaning |
|---|---|
| `adapter_id` | Stable adapter identifier. |
| `patient_id` | Opaque patient UUID. |
| `cell_type` | Adapter cell-type stratum. |
| `fm_name` | Foundation model receiving the adapter. |
| `rank` | LoRA rank, default 8. |
| `trained_cells` | Patient cells used for this adapter. |
| `atlas_neighbor_cells` | Retrieved atlas neighbors used for regularization. |
| `vram_overhead_gb` | Estimated extra VRAM per adapter. |
| `mean_shift` | Fixture patient-vs-atlas expression shift. |

## Mechanism Report Fields

| Field | Meaning |
|---|---|
| `pathway_hits` | Top pathway effects with source database, direction, Z-score, and FDR. |
| `tf_activities` | DoRothEA-style transcription factor activities. |
| `spearman_concordance` | Agreement between VPCM delta and GRN-propagated delta on top genes. |
| `interactions` | Ligand-receptor communication changes between sender and receiver cell types. |
| `caveat` | Required note when an attribution is correlational rather than causal. |

## Biomarker Report Fields

| Field | Meaning |
|---|---|
| `pseudo_bulk_delta` | Cell-type-proportion-weighted tissue delta expression. |
| `normalized_proportions` | TME proportions normalized before pseudo-bulk aggregation. |
| `predictions` | Organ-specific projected clinical lab values. |
| `pearson_benchmark` | Fixture held-out organ ridge Pearson gate, threshold >=0.60. |
| `bagaev_type` | Projected tumor microenvironment class. |
| `responder_probability` | IFN-gamma / exhaustion-derived immunotherapy response score. |

## Outcome Report Fields

| Field | Meaning |
|---|---|
| `hazard_ratio` | DeepSurv-style Cox-PH hazard ratio. |
| `hazard_interval` | Conformal predictive interval around the hazard ratio. |
| `median_pfs_months` | Predicted median progression-free survival. |
| `median_os_months` | Predicted median overall survival. |
| `risk_probabilities` | DeepHit-style competing risk probabilities. |
| `responder_probability` | Immunotherapy responder classifier probability. |
| `conformal_interval` | Calibrated response probability interval. |

## Signed VPCM Report Fields

| Field | Meaning |
|---|---|
| `payload` | Deterministic machine-readable VPCM report. |
| `payload_hash` | SHA-256 hash of the canonical payload. |
| `signature` | Ed25519 detached signature and public key. |
| `baseline_report` | Mandatory train-mean/ridge transparency section. |
| `refusal_flag` | Whether the causal support gate refused the query. |

## Identifier Standards

- Genes: Ensembl IDs, human GENCODE v45 / Ensembl 111.
- Drugs: ChEMBL ID plus InChIKey and canonical SMILES.
- Diseases: MONDO and DOID.
- Cell types: Cell Ontology and scTab-compatible labels.
- Patients: opaque UUID plus SHA-256 patient h5ad hash.
