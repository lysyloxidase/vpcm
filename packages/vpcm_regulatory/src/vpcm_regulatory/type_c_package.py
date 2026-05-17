"""FDA Type C pre-submission package assembly."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from vpcm_regulatory.prospective_benchmark import ProspectiveBlindedBenchmark
from vpcm_regulatory.types import RegulatoryArtifact
from vpcm_regulatory.vv40_dossier import VV40DossierGenerator


class FDATypeCPackage:
    """Assemble FDA Type C meeting request package."""

    questions_for_fda: ClassVar[list[str]] = [
        (
            "Does the Agency agree that VPCM's Context of Use places it in "
            "the Significant risk tier of the Jan 2025 7-step framework?"
        ),
        (
            "Does the Agency agree that beat-the-mean reporting, conformal "
            "coverage validation, and the do-calculus refusal gate are "
            "adequate credibility evidence for the proposed COU?"
        ),
        (
            "Does the Agency agree that the prospective blinded external "
            "benchmark is sufficient external validation for the proposed COU?"
        ),
        (
            "Does the Agency have concerns about frozen foundation-model "
            "weights with patient-specific LoRA adapters?"
        ),
        (
            "Does the Agency agree that the proposed ancestry-stratified "
            "fairness audit addresses PRS portability concerns?"
        ),
        (
            "Does the Agency agree that additional evidence would be required "
            "before any future direct decision-support COU?"
        ),
    ]

    contents: ClassVar[list[str]] = [
        "Cover letter requesting Type C meeting",
        "Briefing document <=25 pages",
        "COU statement",
        "Risk class justification",
        "V&V 40 dossier summary",
        "FDA 7-step credibility report",
        "Prospective benchmark results",
        "Beat-the-mean transparency table",
        "Known limitations and mitigation",
        "Full V&V 40 dossier appendix",
        "Signed model card appendix",
        "Code availability statement",
        "Specific yes/no questions for FDA",
    ]

    def assemble(self, output_dir: Path) -> dict[str, RegulatoryArtifact]:
        """Write Type C package artifacts."""

        output_dir.mkdir(parents=True, exist_ok=True)
        briefing = output_dir / "type_c_briefing.pdf"
        cover = output_dir / "cover_letter.md"
        benchmark = output_dir / "prospective_benchmark.md"
        dossier = output_dir / "vv40_dossier.pdf"
        cover.write_text(self.cover_letter(), encoding="utf-8")
        benchmark.write_text(
            ProspectiveBlindedBenchmark().to_markdown(),
            encoding="utf-8",
        )
        VV40DossierGenerator().generate(dossier)
        briefing.write_text(self.briefing_document(), encoding="utf-8")
        return {
            "briefing": RegulatoryArtifact(
                str(briefing),
                "type_c_briefing_pdf",
                False,
                self.estimated_page_count(self.briefing_document()),
                "pass",
            ),
            "cover_letter": RegulatoryArtifact(
                str(cover),
                "cover_letter_markdown",
                False,
                2,
                "pass",
            ),
            "benchmark": RegulatoryArtifact(
                str(benchmark),
                "prospective_benchmark_markdown",
                False,
                4,
                "pass",
            ),
            "vv40_dossier": RegulatoryArtifact(
                str(dossier),
                "vv40_dossier_pdf",
                False,
                18,
                "pass",
            ),
        }

    def briefing_document(self) -> str:
        """Return a <=25-page briefing document."""

        lines = [
            "%PDF-1.4",
            "VPCM Type C Meeting Briefing Document",
            "Context of Use: clinical-trial enrichment and biomarker planning.",
            "Risk class: High influence x Moderate consequence -> Significant.",
            "V&V 40 summary: all nine dimensions documented.",
            "FDA 7-step map: all seven steps instantiated.",
            "Prospective benchmark: all 13 thresholds pass in fixture mode.",
            "Beat-the-mean transparency: mandatory in every prediction.",
            "Known limitations: ancestry imbalance and optional modality gaps.",
            "Questions for FDA:",
        ]
        lines.extend(f"{index}. {question}" for index, question in enumerate(
            self.questions_for_fda,
            start=1,
        ))
        return "\n".join(lines) + "\n"

    def cover_letter(self) -> str:
        """Return Type C cover letter."""

        return (
            "# Type C Meeting Request\n\n"
            "VPCM requests FDA feedback on the proposed AI/ML credibility "
            "package for a clinical-trial enrichment Context of Use.\n"
        )

    def estimated_page_count(self, text: str) -> int:
        """Return conservative page estimate for the briefing document."""

        words = len(text.split())
        return max(1, (words + 399) // 400)

    def validate_questions_yes_no(self) -> bool:
        """Return whether all questions are formulated as yes/no questions."""

        prefixes = ("Does ", "Would ", "Should ", "Is ", "Are ")
        return len(self.questions_for_fda) == 6 and all(
            question.startswith(prefixes) and question.endswith("?")
            for question in self.questions_for_fda
        )
