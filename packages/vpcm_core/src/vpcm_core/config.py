"""Hydra-oriented configuration objects for Phase 1."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import cast


@dataclass(frozen=True)
class ContextOfUse:
    """Regulatory Context of Use guardrails."""

    intended_uses: list[str] = field(
        default_factory=lambda: [
            "Clinical-trial enrichment / patient-stratification hypothesis generation",
            "Drug-repurposing hypothesis generation",
            "Biomarker-strategy planning for clinical-trial design",
        ]
    )
    prohibited_uses: list[str] = field(
        default_factory=lambda: [
            "First-in-human dosing decisions",
            "Primary endpoint determination",
            "Patient-level treatment decisions without clinician override",
            "Diagnosis",
            "Replacing standard-of-care decision-making",
        ]
    )
    fda_guidance_docket: str = "FDA-2024-D-4689"
    fda_guidance_date: str = "2025-01-06"
    credibility_tier: str = "SIGNIFICANT"
    ood_refusal_recall_threshold: float = 0.95

    def is_use_allowed(self, declared_use: str) -> bool:
        """Return whether a declared use is inside the approved COU."""

        normalized = declared_use.strip().casefold()
        return any(use.casefold() == normalized for use in self.intended_uses)


@dataclass(frozen=True)
class ReproducibilityConfig:
    """Deterministic execution settings."""

    seed: int = 42
    cublas_workspace_config: str = ":4096:8"
    deterministic_algorithms: bool = True
    cudnn_benchmark: bool = False


@dataclass(frozen=True)
class DataConfig:
    """Harmonized data-layer defaults."""

    raw_dir: str = "data/raw"
    harmonized_dir: str = "data/harmonized"
    checkpoints_dir: str = "data/checkpoints"
    census_release: str = "2025-01-30"
    gencode_release: str = "v45"
    ensembl_release: str = "111"
    fixture_mode: bool = True


@dataclass(frozen=True)
class AuditConfig:
    """Audit logging defaults."""

    log_path: str = "data/harmonized/audit/predictions.jsonl"
    service_identity: str = "vpcm-phase1-service"
    purpose: str = "clinical-trial enrichment / patient-stratification tool"
    data_version: str = "phase1-fixture"
    dvc_hash: str = "untracked"


@dataclass(frozen=True)
class VPCMConfig:
    """Top-level config assembled by Hydra in deployed environments."""

    context_of_use: ContextOfUse = field(default_factory=ContextOfUse)
    reproducibility: ReproducibilityConfig = field(
        default_factory=ReproducibilityConfig
    )
    data: DataConfig = field(default_factory=DataConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON/YAML-serializable config mapping."""

        return cast(dict[str, object], asdict(self))


def default_config() -> VPCMConfig:
    """Return the Phase 1 default config."""

    return VPCMConfig()


def hydra_overrides(config: VPCMConfig) -> list[str]:
    """Flatten a config into Hydra-style command-line overrides."""

    values = cast(Mapping[str, object], config.to_dict())
    overrides: list[str] = []
    for section_name, section_value in values.items():
        if isinstance(section_value, Mapping):
            section_mapping = cast(Mapping[str, object], section_value)
            for key, value in section_mapping.items():
                overrides.append(f"{section_name}.{key}={value}")
        else:
            overrides.append(f"{section_name}={section_value}")
    return overrides


def write_default_config(path: Path) -> None:
    """Write the default config as a minimal YAML file without extra deps."""

    config = cast(Mapping[str, object], default_config().to_dict())
    lines: list[str] = []
    for section, values in config.items():
        lines.append(f"{section}:")
        if isinstance(values, Mapping):
            section_mapping = cast(Mapping[str, object], values)
            for key, value in section_mapping.items():
                lines.append(f"  {key}: {value!r}")
        else:
            lines.append(f"  value: {values!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
