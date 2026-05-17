from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vpcm_pipeline.report_generator import SignedReportBundle
from vpcm_regulatory.fda_7step import FDA7StepCredibilityMap
from vpcm_regulatory.model_card import SignedModelCard
from vpcm_regulatory.prospective_benchmark import ProspectiveBlindedBenchmark
from vpcm_regulatory.type_c_package import FDATypeCPackage
from vpcm_regulatory.vv40_dossier import VV40DossierGenerator


class RegulatoryTest(unittest.TestCase):
    def test_vv40_dossier_generates_all_nine_dimensions(self) -> None:
        generator = VV40DossierGenerator()
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = generator.generate(Path(tmpdir) / "vv40.pdf")
            text = Path(artifact.path).read_text(encoding="utf-8")

        self.assertTrue(generator.validate_sections())
        self.assertEqual(len(generator.sections()), 9)
        self.assertIn("Generated from CI artifacts", text)
        self.assertEqual(artifact.validation_status, "pass")

    def test_fda_7step_map_is_complete(self) -> None:
        mapping = FDA7StepCredibilityMap()
        markdown = mapping.render_markdown()

        self.assertTrue(mapping.validate_complete())
        self.assertEqual(len(mapping.to_dict()), 7)
        self.assertIn("Determine adequacy", markdown)

    def test_signed_model_card_validates_with_ed25519(self) -> None:
        card = SignedModelCard()
        signed = card.to_signed_json()
        payload = json.loads(signed)["payload"]

        self.assertTrue(SignedModelCard.verify(signed))
        self.assertTrue(SignedReportBundle.verify_json(signed))
        self.assertIn("out_of_scope_uses", payload)
        self.assertIn("beat_mean_transparency", payload)

    def test_prospective_benchmark_all_thresholds_pass_or_report(self) -> None:
        benchmark = ProspectiveBlindedBenchmark()
        results = benchmark.run()

        self.assertEqual(len(results), 13)
        self.assertTrue(benchmark.all_passed_or_reported())
        self.assertTrue(all(result.passed for result in results))
        self.assertIn("ood_refusal_recall", benchmark.to_markdown())

    def test_type_c_package_briefing_and_questions_are_valid(self) -> None:
        package = FDATypeCPackage()
        briefing = package.briefing_document()

        self.assertLessEqual(package.estimated_page_count(briefing), 25)
        self.assertTrue(package.validate_questions_yes_no())

        with tempfile.TemporaryDirectory() as tmpdir:
            artifacts = package.assemble(Path(tmpdir))

        self.assertIn("briefing", artifacts)
        self.assertLessEqual(artifacts["briefing"].page_count, 25)
        self.assertEqual(len(package.questions_for_fda), 6)


if __name__ == "__main__":
    unittest.main()
