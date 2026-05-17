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

## Identifier Standards

- Genes: Ensembl IDs, human GENCODE v45 / Ensembl 111.
- Drugs: ChEMBL ID plus InChIKey and canonical SMILES.
- Diseases: MONDO and DOID.
- Cell types: Cell Ontology and scTab-compatible labels.
- Patients: opaque UUID plus SHA-256 patient h5ad hash.
