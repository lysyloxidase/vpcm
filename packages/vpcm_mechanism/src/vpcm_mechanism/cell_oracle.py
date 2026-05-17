"""CellOracle-style GRN perturbation simulation fixture."""

from __future__ import annotations

from vpcm_core.types import Intervention

from vpcm_mechanism._math import spearman, stable_float, top_indices_by_abs
from vpcm_mechanism.types import GRNSimulationReport

Vector = list[float]


class CellOracleGRNSimulator:
    """Cross-validate predicted delta expression against GRN propagation."""

    def simulate(
        self,
        predicted_delta: Vector,
        gene_ids: list[str],
        intervention: Intervention,
        top_n: int = 20,
    ) -> GRNSimulationReport:
        """Return GRN-propagated delta and concordance with prediction."""

        if len(predicted_delta) != len(gene_ids):
            raise ValueError("predicted_delta and gene_ids must have equal length.")
        if not predicted_delta:
            raise ValueError("predicted_delta must be non-empty.")
        simulated_delta = [
            value * (0.92 + 0.06 * stable_float(gene_id, "grn-propagation"))
            for value, gene_id in zip(predicted_delta, gene_ids)
        ]
        top_indices = top_indices_by_abs(predicted_delta, min(top_n, len(gene_ids)))
        concordance = spearman(
            [predicted_delta[index] for index in top_indices],
            [simulated_delta[index] for index in top_indices],
        )
        upstream = [
            gene_ids[index]
            for index in top_indices_by_abs(simulated_delta, min(10, len(gene_ids)))
        ]
        return GRNSimulationReport(
            intervention_label=self._intervention_label(intervention),
            predicted_delta=predicted_delta,
            simulated_delta=simulated_delta,
            spearman_concordance=concordance,
            upstream_regulators=upstream,
        )

    def _intervention_label(self, intervention: Intervention) -> str:
        return str(
            intervention.get("intervention_id")
            or intervention.get("target")
            or intervention.get("intervention_type")
            or "unknown_intervention"
        )

