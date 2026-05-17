from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from vpcm_core.provenance import DVCArtifact, ProvenanceTracker


class ProvenanceTest(unittest.TestCase):
    def test_patient_hash_is_stable(self) -> None:
        contents = b"patient h5ad bytes"

        first = ProvenanceTracker.patient_hash_bytes(contents)
        second = ProvenanceTracker.patient_hash_bytes(contents)

        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_manifest_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "manifest.json"
            artifact_path = Path(tmpdir) / "patient.h5ad"
            artifact_path.write_bytes(b"patient bytes")
            tracker = ProvenanceTracker(path)
            tracker.record_dataset(
                resource_id="cellxgene_census",
                source_uri="cellxgene://2025-01-30",
                version="2025-01-30",
                metadata={"cells": 50_000_000},
                dvc_artifacts=[
                    DVCArtifact(path="data/raw/census", hash_value="abc123")
                ],
            )
            tracker.write_manifest()

            loaded = ProvenanceTracker(path).load_manifest()

            self.assertIn("cellxgene_census:2025-01-30", loaded)
            self.assertEqual(
                ProvenanceTracker.hash_file(artifact_path),
                ProvenanceTracker.patient_hash_bytes(b"patient bytes"),
            )
            self.assertEqual(
                loaded["cellxgene_census:2025-01-30"].dvc_artifacts[0].path,
                "data/raw/census",
            )


if __name__ == "__main__":
    unittest.main()
