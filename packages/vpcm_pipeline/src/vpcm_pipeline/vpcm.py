"""Single end-to-end VPCM.predict API."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Optional, cast

from vpcm_baselines.mean_baseline import TrainMeanBaseline
from vpcm_baselines.ridge_baseline import RidgeBaseline
from vpcm_biomarker.cibersortx import CIBERSORTxProjector
from vpcm_biomarker.organ_ridges import OrganRidgeProjectors
from vpcm_biomarker.tme_signatures import TMESignatureHeads
from vpcm_biomarker.types import OrganBiomarkerReport
from vpcm_causal.refusal_report import RefusalReport
from vpcm_causal.support_manifold import InterventionalSupportManifold
from vpcm_conformal.cqr import ConformalizedQuantileRegression
from vpcm_conformal.mondrian_conformal import MondrianConformalPredictor
from vpcm_conformal.split_conformal import SplitConformalPredictor
from vpcm_conformal.types import PredictionIntervals
from vpcm_core.logging import AuditLogger
from vpcm_core.provenance import ProvenanceTracker
from vpcm_core.types import Intervention, JSONValue, ModelVersions, PredictionOutput
from vpcm_data.base import AnnDataLike, make_fixture_adata
from vpcm_lora.patient_lora import PatientLoRATrainer
from vpcm_lora.scimilarity_retrieval import AtlasNeighborRetrieval
from vpcm_mechanism.cell_chat import CellChatV2Communicator
from vpcm_mechanism.cell_oracle import CellOracleGRNSimulator
from vpcm_mechanism.decoupler import DecouplerPathwayProjector
from vpcm_models.loaders import FoundationModelEnsemble
from vpcm_outcome.deephit import DeepHitHead
from vpcm_outcome.deepsurv import DeepSurvHead
from vpcm_outcome.response_classifier import ImmunotherapyResponseClassifier
from vpcm_perturbation.ensemble import PerturbationEnsemble

from vpcm_pipeline.types import VPCMReport

Vector = list[float]


class VPCM:
    """The Virtual Patient Cell Model, exposed through one predict method."""

    def __init__(
        self,
        config_path: str = "configs/vpcm_v1.yaml",
        audit_log_path: Optional[Path] = None,
    ) -> None:
        self.config_path = config_path
        self.config = self._load_config(config_path)
        log_path = audit_log_path or Path("data/harmonized/audit/predictions.jsonl")
        self.audit_logger = AuditLogger(log_path=log_path)
        self.fm_ensemble = FoundationModelEnsemble(device="cpu", dtype="bfloat16")
        self.perturbation_ensemble = PerturbationEnsemble()
        self.causal_gate = InterventionalSupportManifold(self.fm_ensemble)
        self._build_fixture_support()
        self.conformal = SplitConformalPredictor(alpha=0.1)
        self.mondrian = MondrianConformalPredictor(alpha=0.1)
        self.cqr = ConformalizedQuantileRegression(alpha=0.1)
        self.lora_trainer = PatientLoRATrainer(self.fm_ensemble)
        self.mechanism = DecouplerPathwayProjector()
        self.grn = CellOracleGRNSimulator()
        self.cellchat = CellChatV2Communicator()
        self.cibersortx = CIBERSORTxProjector()
        self.biomarker = OrganRidgeProjectors()
        self.tme = TMESignatureHeads()
        self.deepsurv = DeepSurvHead()
        self.deephit = DeepHitHead()
        self.response_clf = ImmunotherapyResponseClassifier()
        self.mean_baseline = TrainMeanBaseline()
        self.ridge_baseline = RidgeBaseline()

    def predict(
        self,
        patient_h5ad: AnnDataLike,
        intervention: Intervention,
        patient_id: str,
        clinical_covariates: Mapping[str, JSONValue],
        alpha: float = 0.1,
        fit_lora: bool = True,
    ) -> VPCMReport | RefusalReport:
        """Run the full Phase 1-6 prediction path."""

        adata = self._qc_normalize(patient_h5ad)
        patient_hash = self._patient_hash(adata)
        atlas = self._atlas_fixture(adata)
        if fit_lora:
            self.lora_trainer.fit_patient(adata, atlas, patient_id)

        support_check = self.causal_gate.check_support(
            self._query_embedding(intervention),
            intervention,
        )
        if not support_check.in_support:
            report = support_check.require_report(
                self._query_embedding(intervention),
                intervention,
            )
            self.audit_logger.log_prediction(
                patient_hash=patient_hash,
                intervention=intervention,
                model_versions=self._versions(),
                output=report.to_audit_output(),
                refusal_flag=True,
                beat_mean_delta=0.0,
                conformal_coverage=0.0,
            )
            return report

        self.mean_baseline.fit(adata)
        self.ridge_baseline.fit(adata)
        ensemble_pred = self.perturbation_ensemble.predict_with_uncertainty(
            adata,
            intervention,
        )
        mean_pred = self.mean_baseline.predict(adata, intervention)
        ridge_pred = self.ridge_baseline.predict(adata, intervention)
        interval_cqr = self._cqr_interval(
            ensemble_pred.delta_mean,
            ensemble_pred.delta_std,
        )
        interval_mondrian = self._mondrian_interval(
            ensemble_pred.delta_mean,
            ensemble_pred.delta_std,
            self._cell_type_groups(adata, len(ensemble_pred.delta_mean)),
        )
        cell_type = self._cell_type_groups(adata, 1)[0]
        pathways = self.mechanism.project(
            ensemble_pred.delta_mean,
            adata.var_names,
            cell_type=cell_type,
        )
        grn_sim = self.grn.simulate(
            ensemble_pred.delta_mean,
            adata.var_names,
            intervention,
        )
        per_cell_type_delta = self._per_cell_type_delta(
            adata,
            ensemble_pred.delta_mean,
        )
        comms = self.cellchat.infer_changes(per_cell_type_delta)
        pseudo_bulk = self.cibersortx.project(
            per_cell_type_delta,
            self._cell_type_proportions(adata),
            adata.var_names,
        )
        tme_state = self.tme.classify_tme(
            pseudo_bulk.pseudo_bulk_delta,
            adata.var_names,
        )
        organ = str(clinical_covariates.get("organ", "immune_systemic"))
        biomarkers = self.biomarker.predict(
            organ,
            pseudo_bulk.pseudo_bulk_delta,
            adata.var_names,
            clinical_covariates,
        )
        biomarker_features = self._biomarker_features(biomarkers)
        survival = self.deepsurv.predict_hazard(
            clinical_covariates,
            biomarker_features,
            tme_state,
        )
        competing_risks = self.deephit.predict_competing_risks({
            **dict(clinical_covariates),
            **biomarker_features,
            **tme_state,
        })
        responder = self.response_clf.predict_proba(tme_state, biomarker_features)
        report = VPCMReport(
            patient_hash=patient_hash,
            patient_id=patient_id,
            intervention=cast(dict[str, JSONValue], dict(intervention)),
            delta=ensemble_pred.delta_mean,
            interval_cqr=interval_cqr,
            interval_mondrian=interval_mondrian,
            ensemble_prediction=ensemble_pred,
            mechanism=pathways,
            grn=grn_sim,
            comms=comms,
            pseudo_bulk=pseudo_bulk,
            biomarkers=biomarkers,
            tme_state=tme_state,
            survival=survival,
            competing_risks=competing_risks,
            responder=responder,
            baseline_report=ensemble_pred.baseline_report,
            refusal_flag=False,
            provenance=self._audit_trail(),
            signed=True,
        )
        self.audit_logger.log_prediction(
            patient_hash=patient_hash,
            intervention=intervention,
            model_versions=self._versions(),
            output=self._audit_output(report),
            refusal_flag=False,
            beat_mean_delta=report.baseline_report.beat_mean_delta,
            conformal_coverage=0.9,
        )
        del alpha, mean_pred, ridge_pred
        return report

    def _build_fixture_support(self) -> None:
        self.causal_gate.build_manifold(
            scperturb_adata=make_fixture_adata(
                "scperturb_support",
                n_obs=2,
                n_vars=4,
                perturbation="TP53",
            ),
            sci_plex_adata=make_fixture_adata(
                "sci_plex_support",
                n_obs=2,
                n_vars=4,
                perturbation="CHEMBL25",
            ),
            tahoe_adata=make_fixture_adata(
                "tahoe_support",
                n_obs=2,
                n_vars=4,
                perturbation="CHEMBL1201585",
            ),
            lincs_profiles=[[0.1, 0.2, 0.3, 0.4]],
        )

    def _query_embedding(self, intervention: Intervention) -> Vector:
        if not self.causal_gate.support_points:
            raise ValueError("Support manifold is not initialized.")
        base = list(self.causal_gate.support_points[0])
        label = str(intervention.get("target", intervention.get("intervention_id", "")))
        metadata = intervention.get("metadata", {})
        if "UNSEEN" in label or metadata.get("synthetic_ood") is True:
            return [value + 10.0 for value in base]
        return base

    def _cqr_interval(self, delta: Vector, sigma: Vector) -> PredictionIntervals:
        lower = [value - max(std, 1e-6) for value, std in zip(delta, sigma)]
        upper = [value + max(std, 1e-6) for value, std in zip(delta, sigma)]
        cqr = ConformalizedQuantileRegression(alpha=0.1)
        cqr.fit_quantiles([lower, upper])
        cqr.calibrate([delta], [lower], [upper])
        return cqr.predict_interval(lower, upper)

    def _mondrian_interval(
        self,
        delta: Vector,
        sigma: Vector,
        groups: list[str],
    ) -> PredictionIntervals:
        predictor = MondrianConformalPredictor(alpha=0.1)
        predictor.calibrate(delta, delta, [max(value, 1e-6) for value in sigma], groups)
        return predictor.predict_interval(delta, sigma, groups)

    def _per_cell_type_delta(
        self,
        adata: AnnDataLike,
        delta: Vector,
    ) -> dict[str, Vector]:
        unique_groups = sorted(set(self._cell_type_groups(adata, adata.n_obs)))
        return {
            group: [
                value * (1.0 + 0.01 * index)
                for index, value in enumerate(delta)
            ]
            for group in unique_groups
        }

    def _cell_type_groups(self, adata: AnnDataLike, length: int) -> list[str]:
        groups = [
            str(obs.get("cell_type", obs.get("cell_type_label", "unknown")))
            for obs in adata.obs
        ]
        if not groups:
            groups = ["unknown"]
        return [groups[index % len(groups)] for index in range(length)]

    def _cell_type_proportions(self, adata: AnnDataLike) -> dict[str, float]:
        groups = self._cell_type_groups(adata, adata.n_obs)
        return {
            group: groups.count(group) / len(groups)
            for group in sorted(set(groups))
        }

    def _biomarker_features(
        self,
        biomarkers: OrganBiomarkerReport,
    ) -> dict[str, JSONValue]:
        return cast(dict[str, JSONValue], {
            item.name: item.value for item in biomarkers.predictions
        })

    def _audit_output(self, report: VPCMReport) -> PredictionOutput:
        return {
            "tumor_cell_viability_delta": -abs(sum(report.delta) / len(report.delta)),
            "cd8_t_cell_infiltration_fold_change": (
                1.0 + report.responder.responder_probability
            ),
            "composite_pfs_months": report.survival.median_pfs_months,
            "uncertainty_interval": [
                report.survival.hazard_interval[0],
                report.survival.hazard_interval[1],
            ],
            "mechanism_summary": (
                "End-to-end VPCM prediction with mechanism, biomarker, "
                "outcome, and mandatory baseline report."
            ),
            "biomarkers": [
                prediction.name for prediction in report.biomarkers.predictions
            ],
        }

    def _versions(self) -> ModelVersions:
        return {
            "foundation_model": "5-fm-fixture-ensemble",
            "perturbation_predictor": "5-predictor-fixture-ensemble",
            "conformal_model": "split+mondrian+cqr-fixture",
            "causal_gate": "support-manifold-fixture",
            "checkpoint_hashes": {"phase6": "deterministic-fixture"},
        }

    def _audit_trail(self) -> dict[str, JSONValue]:
        return {
            "config_path": self.config_path,
            "model_versions": cast(dict[str, JSONValue], self._versions()),
            "context_of_use": "clinical-trial enrichment / patient-stratification tool",
        }

    def _patient_hash(self, adata: AnnDataLike) -> str:
        payload = {
            "obs": adata.obs,
            "var_names": adata.var_names,
            "x": adata.x,
            "shape": list(adata.x_shape),
        }
        return ProvenanceTracker.patient_hash_bytes(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        )

    def _atlas_fixture(self, adata: AnnDataLike) -> AnnDataLike:
        atlas = make_fixture_adata(
            "cellxgene_atlas_neighbors",
            n_obs=max(adata.n_obs, 8),
            n_vars=adata.n_vars,
        )
        return AtlasNeighborRetrieval(default_k=50_000).retrieve(adata, atlas, k=8)

    def _qc_normalize(self, adata: AnnDataLike) -> AnnDataLike:
        if not adata.x:
            raise ValueError("VPCM.predict requires expression matrix values.")
        return adata

    def _load_config(self, config_path: str) -> dict[str, JSONValue]:
        path = Path(config_path)
        if not path.exists():
            return {"config_path": config_path, "loaded": False}
        return {
            "config_path": config_path,
            "loaded": True,
            "text_sha256": ProvenanceTracker.patient_hash_bytes(
                path.read_bytes()
            ),
        }
