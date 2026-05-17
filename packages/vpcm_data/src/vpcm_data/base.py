"""Base dataset loader abstractions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Optional

from vpcm_core.types import DatasetResource, JSONValue


class DatasetUnavailableError(RuntimeError):
    """Raised when a live data source is requested without its dependency."""


@dataclass(frozen=True)
class AnnDataLike:
    """Small AnnData-compatible fixture surface used by Phase 1 tests."""

    obs: list[dict[str, JSONValue]]
    var_names: list[str]
    x_shape: tuple[int, int]
    uns: Mapping[str, JSONValue] = field(default_factory=dict[str, JSONValue])

    @property
    def n_obs(self) -> int:
        """Number of observations."""

        return len(self.obs)

    @property
    def n_vars(self) -> int:
        """Number of variables."""

        return len(self.var_names)


def make_fixture_adata(
    resource_id: str,
    n_obs: int = 8,
    n_vars: int = 16,
    perturbation_type: str = "control",
    perturbation: str = "non-targeting",
    extra_obs: Optional[Mapping[str, str]] = None,
) -> AnnDataLike:
    """Create a deterministic AnnData-like fixture with harmonized columns."""

    var_names = [f"ENSG{index:011d}" for index in range(1, n_vars + 1)]
    extra = dict(extra_obs or {})
    observations: list[dict[str, JSONValue]] = []
    for index in range(n_obs):
        observation: dict[str, JSONValue] = {
            "cell_id": f"{resource_id}_cell_{index:04d}",
            "patient_id": f"{resource_id}_patient_{index % 3}",
            "patient_hash": f"{index:064x}",
            "disease_id": "MONDO:0004992",
            "disease_label": "cancer",
            "cell_type_id": "CL:0000000",
            "cell_type_label": "cell",
            "perturbation_type": perturbation_type,
            "perturbation": perturbation,
            "dose": "0",
            "batch": f"batch_{index % 2}",
            "source_dataset": resource_id,
        }
        observation.update(extra)
        observations.append(observation)
    return AnnDataLike(
        obs=observations,
        var_names=var_names,
        x_shape=(n_obs, n_vars),
        uns={
            "resource_id": resource_id,
            "fixture_mode": True,
            "schema": "vpcm.phase1.anndata-like.v1",
        },
    )


class BaseDatasetLoader:
    """Uniform loader interface for all Phase 1 resources."""

    def __init__(self, resource: DatasetResource, fixture_mode: bool = True) -> None:
        self.resource = resource
        self.fixture_mode = fixture_mode

    def load(self, **filters: JSONValue) -> AnnDataLike:
        """Load a harmonized dataset or a deterministic fixture."""

        if not self.fixture_mode:
            raise DatasetUnavailableError(
                f"Live loader for {self.resource['resource_id']} requires "
                "source-specific credentials/dependencies."
            )
        max_cells_value = filters.get("max_cells", 8)
        max_cells = max_cells_value if isinstance(max_cells_value, int) else 8
        extra = {
            "disease_label": str(filters.get("disease", "cancer")),
            "cell_type_label": str(filters.get("cell_type", "cell")),
        }
        return make_fixture_adata(
            resource_id=self.resource["resource_id"],
            n_obs=max_cells,
            extra_obs=extra,
        )

    def manifest(self) -> dict[str, JSONValue]:
        """Return a harmonized manifest for catalog registration."""

        return {
            "resource_id": self.resource["resource_id"],
            "name": self.resource["name"],
            "doi_or_source": self.resource["doi_or_source"],
            "fixture_mode": self.fixture_mode,
            "status": self.resource["status"],
        }
