from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vpcm_core.logging import AuditLogger
from vpcm_core.provenance import ProvenanceTracker
from vpcm_mechanism.attention_caveat import AttentionAttributionWithCaveat
from vpcm_mechanism.cell_chat import CellChatV2Communicator
from vpcm_mechanism.cell_oracle import CellOracleGRNSimulator
from vpcm_mechanism.decoupler import DecouplerPathwayProjector


def _genes(n_genes: int = 24) -> list[str]:
    return [f"ENSG{index:011d}" for index in range(1, n_genes + 1)]


def _delta(n_genes: int = 24) -> list[float]:
    return [((-1.0) ** index) * (0.05 + index * 0.01) for index in range(n_genes)]


class MechanismTest(unittest.TestCase):
    def test_decoupler_returns_top_10_pathways_and_tfs_with_fdr_gate(self) -> None:
        projector = DecouplerPathwayProjector()

        report = projector.project(_delta(), _genes(), cell_type="tumor")

        self.assertEqual(len(report.pathway_hits), 10)
        self.assertEqual(len(report.tf_activities), 10)
        self.assertTrue(all(hit.fdr < 0.05 for hit in report.pathway_hits))
        self.assertTrue(all(tf.fdr < 0.05 for tf in report.tf_activities))
        self.assertIn("PROGENy", report.databases)
        summary = str(report.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("top pathway", summary)

    def test_cell_oracle_grn_cross_validates_delta_direction(self) -> None:
        simulator = CellOracleGRNSimulator()

        report = simulator.simulate(
            predicted_delta=_delta(),
            gene_ids=_genes(),
            intervention={"intervention_type": "genetic", "target": "TP53"},
        )

        self.assertGreaterEqual(report.spearman_concordance, 0.6)
        self.assertEqual(len(report.simulated_delta), len(report.predicted_delta))
        summary = str(report.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("CellOracle-style", summary)

    def test_attention_attribution_emits_caveat_per_gene(self) -> None:
        attributor = AttentionAttributionWithCaveat()

        report = attributor.attribute(
            attention_scores=[0.1, 0.7, -0.4, 0.2],
            gene_ids=_genes(4),
            model_name="scgpt",
            top_n=3,
        )

        self.assertEqual(len(report.attributions), 3)
        for attribution in report.attributions:
            self.assertIn("correlational", attribution.caveat)
            caveat = str(attribution.to_dict().get("caveat", ""))
            self.assertIn("co-expression", caveat)
        summary = str(report.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("Attention attribution", summary)

    def test_cellchat_liana_nichenet_run_on_dummy_data(self) -> None:
        communicator = CellChatV2Communicator()

        report = communicator.infer_changes(
            {
                "tumor": _delta(),
                "cd8_t": [value * -0.5 for value in _delta()],
                "fibroblast": [value * 0.25 for value in _delta()],
            }
        )

        self.assertEqual(report.tools, ["CellChat v2", "LIANA+", "NicheNet"])
        self.assertEqual(len(report.interactions), 10)
        summary = str(report.to_audit_output().get("mechanism_summary", ""))
        self.assertIn("Communication projection", summary)

    def test_projection_trace_is_signed_in_audit_log(self) -> None:
        if not AuditLogger.signing_available():
            self.skipTest("cryptography is not installed in this local environment")

        report = DecouplerPathwayProjector().project(
            _delta(),
            _genes(),
            cell_type="tumor",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_path=Path(tmpdir) / "audit.jsonl")
            logger.log_prediction(
                patient_hash=ProvenanceTracker.patient_hash_bytes(b"patient"),
                intervention={"intervention_type": "drug", "target": "CHEMBL25"},
                model_versions={"foundation_model": "phase5-fixture"},
                output=report.to_audit_output(),
                refusal_flag=False,
                beat_mean_delta=0.12,
                conformal_coverage=0.9,
            )
            entry = logger.read_entries()[0]

        self.assertTrue(AuditLogger.verify_entry(entry))
        output = entry.get("output", {})
        self.assertIn("databases", str(output.get("mechanism_summary", "")))


if __name__ == "__main__":
    unittest.main()
