"""FastAPI inference service for VPCM."""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
from collections.abc import Callable
from typing import Any, Protocol, TypeVar, cast

from vpcm_core.types import Intervention, JSONValue
from vpcm_data.base import make_fixture_adata
from vpcm_pipeline import VPCM, VPCMReport

F = TypeVar("F", bound=Callable[..., object])


class _AppProtocol(Protocol):
    def post(self, path: str) -> Callable[[F], F]:
        ...


class _FastAPIClass(Protocol):
    def __call__(self, title: str) -> _AppProtocol:
        ...


class _FixtureFastAPI:
    """Tiny fallback so local smoke tests can import the API module."""

    def __init__(self, title: str) -> None:
        self.title = title

    def post(self, path: str) -> Callable[[F], F]:
        del path

        def decorator(func: F) -> F:
            return func

        return decorator


def _fastapi_class() -> _FastAPIClass:
    if importlib.util.find_spec("fastapi") is None:
        return _FixtureFastAPI
    module = importlib.import_module("fastapi")
    return cast(_FastAPIClass, module.FastAPI)


app = _fastapi_class()(title="VPCM Inference API v1.0")
vpcm = VPCM(config_path="configs/vpcm_v1.yaml")


@app.post("/predict")
async def predict(
    patient_h5ad_path: str,
    intervention: dict[str, Any],
    patient_id: str,
    clinical_covariates: dict[str, Any],
    alpha: float = 0.1,
) -> str:
    """Run one prediction request.

    The fixture service treats ``patient_h5ad_path`` as provenance context and
    uses a deterministic AnnData-like payload. Production deployments replace
    this with ``scanpy.read_h5ad`` after storage and PHI controls are configured.
    """

    del patient_h5ad_path
    await asyncio.sleep(0)
    report = vpcm.predict(
        patient_h5ad=make_fixture_adata(
            "api_patient",
            n_obs=6,
            n_vars=8,
            extra_obs={"cell_type_label": "tumor"},
        ),
        intervention=cast(Intervention, intervention),
        patient_id=patient_id,
        clinical_covariates=cast(dict[str, JSONValue], clinical_covariates),
        alpha=alpha,
        fit_lora=False,
    )
    if isinstance(report, VPCMReport):
        return report.to_signed_json()
    return VPCMReportGeneratorFallback.sign_refusal(report.to_dict())


class VPCMReportGeneratorFallback:
    """Small adapter for signing refusal reports in the API path."""

    @staticmethod
    def sign_refusal(payload: dict[str, JSONValue]) -> str:
        from vpcm_pipeline.report_generator import SignedReportBundle

        return SignedReportBundle().sign_json(payload)
