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
