"""Shared typed schemas for VPCM records."""

from __future__ import annotations

from typing import Literal, TypedDict, Union

JSONPrimitive = Union[str, int, float, bool, None]
JSONValue = Union[JSONPrimitive, dict[str, "JSONValue"], list["JSONValue"]]

DatasetStatus = Literal["LOAD", "OPTIONAL", "DEPRECATED"]


class Intervention(TypedDict, total=False):
    """Patient intervention declaration."""

    intervention_id: str
    intervention_type: Literal["drug", "genetic", "combination", "other"]
    target: str
    dose: str
    duration: str
    metadata: dict[str, JSONValue]


class ModelVersions(TypedDict, total=False):
    """Model and checkpoint identity surface."""

    foundation_model: str
    perturbation_predictor: str
    conformal_model: str
    causal_gate: str
    checkpoint_hashes: dict[str, str]


class PredictionOutput(TypedDict, total=False):
    """Prediction output attached to every audited inference call."""

    tumor_cell_viability_delta: float
    cd8_t_cell_infiltration_fold_change: float
    composite_pfs_months: float
    uncertainty_interval: list[float]
    mechanism_summary: str
    biomarkers: list[str]


class PredictionInput(TypedDict):
    """Minimum input identity for a VPCM prediction."""

    patient_hash: str
    intervention: Intervention
    context_of_use: str


class AuditSignature(TypedDict):
    """Detached signature payload for an audit log entry."""

    algorithm: Literal["Ed25519"]
    public_key: str
    value: str


class AuditLogEntry(TypedDict, total=False):
    """21 CFR Part 11 JSONL record."""

    entry_uuid: str
    timestamp: str
    service_identity: str
    patient_hash: str
    intervention: Intervention
    model_versions: ModelVersions
    output: PredictionOutput
    refusal_flag: bool
    beat_mean_delta: float
    conformal_coverage: float
    purpose: str
    code_commit_sha: str
    data_version: str
    dvc_hash: str
    entry_hash: str
    signature: AuditSignature


class DatasetResource(TypedDict):
    """Dataset inventory record used by the harmonized catalog."""

    resource_id: str
    name: str
    status: DatasetStatus
    used_in: list[str]
    doi_or_source: str
    modality: str
    access: str


class DatasetQuery(TypedDict, total=False):
    """Uniform data-layer query request."""

    resource_id: str
    filters: dict[str, JSONValue]
    max_cells: int
    split: str
    fixture_mode: bool


class HarmonizedObservation(TypedDict, total=False):
    """Required observation columns for harmonized single-cell data."""

    cell_id: str
    patient_id: str
    patient_hash: str
    disease_id: str
    disease_label: str
    cell_type_id: str
    cell_type_label: str
    perturbation_type: str
    perturbation: str
    dose: str
    batch: str
    source_dataset: str
