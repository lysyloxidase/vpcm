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

## Phase 3 Perturbation Predictor Ensemble

| Predictor | Role | DOI/Source | Transparent caveat |
|---|---|---|---|
| CPA | Drug/dose/cell-type disentanglement | 10.15252/msb.202211517 | Requires interventional training coverage. |
| ChemCPA | SMILES-aware unseen-compound extrapolation | NeurIPS 2022 / theislab ChemCPA | Chemistry encoder does not solve causal support. |
| GEARS | GO/co-expression GNN for genetic perturbations | 10.1038/s41587-023-01905-6 | Can lose to ridge on Norman unseen-double splits. |
| CellOT | Neural optimal transport | 10.1038/s41592-023-01969-x | Strong for distribution shift but support-limited. |
| scGen | Beta-VAE latent arithmetic | 10.1038/s41592-019-0494-8 | Simple deep-family baseline, not causal by itself. |

`PerturbationEnsemble` returns mean delta expression, per-gene standard
deviation from MC-dropout, per-model deltas for disagreement analysis, and a
mandatory `BaselineReport`.

## Do-Calculus Refusal Gate

The novel VPCM contribution is the explicit refusal gate. Observational
foundation-model pretraining cannot identify p(Y|do(X)) without interventional
support or strong DAG assumptions. The gate builds an interventional support
manifold from scPerturb, sci-Plex, Tahoe-100M, and LINCS anchors, embeds those
anchors in foundation-model latent space, and calibrates an OOD threshold.

When a query exceeds the calibrated threshold, VPCM returns a `RefusalReport`
with the Mahalanobis distance, nearest training intervention, wide
observational interval, Pearl-style identifiability note, and suggested
interventional experiment. Recent interpretability work by Kendiukhov on
scGPT/Geneformer attention and sparse-autoencoder probing is tracked as
supporting evidence that co-expression representations should not be treated as
causal mechanisms without perturbational anchors.

## Phase 4 Conformal Uncertainty Quantification

VPCM uses conformal prediction as the regulatory uncertainty primitive because
it is distribution-free and model-agnostic. Split conformal prediction follows
Vovk, Gammerman, and Shafer, with the overview by Angelopoulos and Bates in
Foundations and Trends in Machine Learning: 10.1561/2200000101.

The Phase 4 package includes:

- Split conformal intervals with heteroscedastic scores
  `|y_true - y_pred| / sigma`.
- Mondrian group-conditional calibration per cell type.
- CQR-style per-gene interval adjustment, with MAPIE listed as the optional
  production estimator backend.
- Coverage audits that require alpha=0.1 marginal coverage in the 0.88-0.92
  lifecycle band and raise a recalibration alarm otherwise.

## Phase 4 Patient-Specific LoRA

LoRA adapters follow Hu et al. ICLR 2022, arXiv 2106.09685. Foundation-model
weights stay frozen; patient-specific rank-8 adapters are trained per
patient x cell type x foundation model. Atlas augmentation uses SCimilarity
neighbors from CELLxGENE-style references and scTab-style large-scale
annotation models. References include Heimberg et al. bioRxiv
10.1101/2023.07.18.549537 and scTab by Fischer et al. Nature Communications
15:6611, 10.1038/s41467-024-51059-5.

Patient covariates are encoded as additional channels: patient embedding,
ancestry-stratified PRS, somatic calls, disease subtype, age, sex, stage, and
prior treatment lines. Missing channels are preserved explicitly so downstream
fairness and audit checks can distinguish absent evidence from zero evidence.

## Phase 5 Mechanism-of-Action Interpretation

VPCM separates mechanism interpretation from causal estimation. The mechanism
head explains a predicted delta expression vector; it does not override the
do-calculus support gate. Pathway projection follows the decoupleR framework
from Badia-i-Mompel et al., 10.1093/bioadv/vbac016, with PROGENy, DoRothEA,
Reactome, KEGG, and WikiPathways-style resources. KEGG is tracked from
Kanehisa and Goto, 10.1093/nar/28.1.27.

`DecouplerPathwayProjector` returns top pathways and transcription-factor
activities with direction, Z-score, FDR, and contributing genes. The
`CellOracleGRNSimulator` follows Kamimoto et al., 10.1038/s41586-022-05688-9,
as a GRN propagation cross-check, with the caveat that prior TF-target networks
are incomplete and correlational without experimental validation.

`CellChatV2Communicator` exposes a shared interface for CellChat v2, LIANA+,
and NicheNet-style ligand-receptor communication changes. Attention-derived
gene importance always carries the explicit warning that attention can encode
co-expression rather than causation and must be cross-validated against
perturbational, GRN, pathway, or Mendelian-randomization evidence.

## Phase 5 Biomarker Projection

Clinical biomarker projection maps per-cell-type delta expression to
pseudo-bulk tissue delta and then to organ-specific clinical readouts.
`CIBERSORTxProjector` follows the CIBERSORTx deconvolution framing from Newman
et al., 10.1038/s41587-019-0114-2. `OrganRidgeProjectors` expose liver,
kidney, bone marrow, lung, heart, and systemic immune lab heads with held-out
Pearson performance gates.

`TMESignatureHeads` track Bagaev tumor-microenvironment classes, T-cell
exhaustion, IFN-gamma response, TMB projection, and responder probability.
Optional `TCRRepertoireHead` and `SpatialTranscriptomicsIntegrator` add matched
TCR-seq and spatial transcriptomics context when those modalities are present.
Missing optional modalities are reported explicitly rather than imputed as zero
evidence.

## Phase 6 Outcome Modeling

The outcome layer adds survival, competing-risk, and response prediction heads
on top of Phase 5 biomarker and TME outputs. `DeepSurvHead` follows the Cox-PH
deep network framing from Katzman et al., 10.1186/s12874-018-0482-1, and
returns hazard ratio, predictive interval, median PFS/OS, risk quartile, and a
held-out C-index fixture gate. `DeepHitHead` covers competing cancer risks:
progression, death from disease, death from other causes, and toxicity
discontinuation.

`ImmunotherapyResponseClassifier` combines Bagaev TME type, IFN-gamma score,
TMB projection, CD8/T-cell context, exhaustion, and biomarker features into a
conformal responder probability. `MultiomicFusion` records optional scRNA,
scATAC, CITE-seq, proteomics, and metabolomics features using MOFA+, totalVI,
and MultiVI-style summary surfaces. Optional modalities remain explicit when
missing.

## Phase 6 End-to-End Prediction API

`VPCM.predict()` composes every credibility primitive into one signed call:

1. QC-normalize patient AnnData-like input and hash it.
2. Optionally fit patient-specific LoRA adapters.
3. Check interventional support and return `RefusalReport` for synthetic OOD.
4. Run the five-predictor perturbation ensemble and mandatory baselines.
5. Construct CQR and Mondrian conformal intervals.
6. Project mechanism, GRN, and cell-cell communication reports.
7. Project pseudo-bulk, organ biomarkers, and TME state.
8. Predict survival, competing risks, and immunotherapy response.
9. Emit mandatory beat-the-mean / beat-ridge transparency.
10. Sign the machine-readable JSON and write report/provenance artifacts.

The report bundle contains `report.json`, `report.pdf`, `audit.jsonl`, and
`provenance.yaml`. Section F of the PDF-like artifact is reserved for the
non-negotiable Csendes/Ahlmann-Eltze baseline comparison.
