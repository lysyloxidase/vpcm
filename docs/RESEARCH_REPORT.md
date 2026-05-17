# Research Report

## Phase 1 Dataset Inventory

| Resource | Status | Used in | DOI/Source |
|---|---|---|---|
| CELLxGENE Census | LOAD | FM pretraining; SCimilarity retrieval | 10.1101/2023.10.30.563174 |
| Human Cell Atlas | LOAD | Atlas reference | 10.7554/eLife.27041 |
| Tabula Sapiens v1/v2 | LOAD | Cross-tissue benchmark | 10.1126/science.abl4896 |
| LINCS L1000 | LOAD | Chemical perturbation prior | 10.1016/j.cell.2017.10.049 |
| Connectivity Map | LOAD | Drug-disease matching | 10.1126/science.1132939 |
| sci-Plex | LOAD | Drug perturbation benchmark | 10.1126/science.aax6234 |
| Replogle (K562+RPE1) | LOAD | Genetic perturbation gold standard | 10.1016/j.cell.2022.05.013 |
| Adamson (UPR) | LOAD | Benchmark | 10.1016/j.cell.2016.11.048 |
| Norman (dual KO) | LOAD | Combinatorial perturbation | 10.1126/science.aax4438 |
| Jost (CRISPRi) | LOAD | Benchmark | 10.1038/s41587-019-0387-5 |
| scPerturb (unified) | LOAD | Benchmark + E-distance | 10.1038/s41592-023-02144-y |
| Tahoe-100M | LOAD | Next-gen chemical Perturb-seq | 10.1101/2025.02.20.639398 |
| X-Atlas/Orion | LOAD | Genome-wide fix-cryopreserve | 10.1101/2025.06.11.659105 |
| DepMap / CCLE | LOAD | Drug sensitivity bulk validation | depmap.org |
| GDSC | LOAD | Drug sensitivity | cancerrxgene.org |
| PRISM | LOAD | Drug sensitivity | depmap.org |
| TCGA pan-cancer | LOAD | Patient outcome modeling | cbioportal.org |
| GTEx | LOAD | Healthy tissue reference | gtexportal.org |
| CRI iAtlas | LOAD | Immunotherapy cohorts | cri-iatlas.org |
| OneK1K (MR anchors) | LOAD | Mendelian-randomization causal anchors | 10.1126/science.abf3041 |

## Phase 1 Caveats

CELLxGENE Census and other human atlases over-represent some ancestry groups.
Phase 1 records this as a required fairness audit condition for later model
validation. Live source loaders must preserve provenance, licensing metadata,
and donor-level privacy constraints before data can leave raw storage.

The scPerturb dataset list follows the Nature Methods 2024 resource
description and source accessions published by the authors.

## Phase 2 Foundation Model Ensemble

| Model | Parameters | Source | DOI/Source | Caveat |
|---|---:|---|---|---|
| scGPT | 51M | `bowang-lab/scGPT` | 10.1038/s41592-024-02201-0 | Loses to train-mean on Perturb-seq in Csendes reproduction. |
| scFoundation | 100M | `biomap-research/scFoundation` | 10.1038/s41592-024-02305-7 | Research-only license requires commercial review. |
| Geneformer V2 | 104M | `ctheodoris/Geneformer` | 10.1101/2024.08.16.608180 | Oncology continual-pretraining variant tracked separately. |
| UCE | 650M | `snap-stanford/UCE` | 10.1101/2023.11.28.568918 | Largest memory footprint in ensemble. |
| CellPLM | 80M | `OmicsML/CellPLM` | 10.1101/2023.10.03.560734 | Cell-as-token speed advantage. |

Estimated BF16/FP16 memory is 63 GB, below the Phase 2 80 GB H100 budget.
All adapters are frozen by default; patient-specific LoRA belongs to Phase 4.

## Mandatory Baselines

VPCM treats train-set mean as the credibility anchor, not a toy baseline.
Csendes et al. reported that scGPT and scFoundation can be beaten by predicting
the train-set mean on Perturb-seq benchmarks, including Adamson, Norman, and
Replogle, when the perturbation target gene is excluded:
10.1101/2024.09.30.615843 and 10.1186/s12864-025-11600-2.

Ahlmann-Eltze et al. extended this warning to GEARS and emphasized systematic
evaluation of perturbation-response prediction: 10.1038/s41592-025-02772-6.
Wenteler et al. report that PCA/ridge remains a strong baseline in PertEval-scFM
for leave-perturbation-out evaluation: arXiv 2410.13956.
