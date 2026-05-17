"""FDA 7-step credibility mapping for VPCM."""

from __future__ import annotations

from typing import ClassVar, cast

from vpcm_core.types import JSONValue


class FDA7StepCredibilityMap:
    """Map FDA-2024-D-4689 credibility steps to VPCM evidence."""

    steps: ClassVar[dict[int, dict[str, str]]] = {
        1: {
            "name": "Define the question of interest",
            "vpcm_instantiation": (
                "Will intervention z administered to patient x produce >=30% "
                "tumor-cell viability reduction, >=1.5x CD8+ T-cell "
                "infiltration, and composite PFS >=6 months?"
            ),
        },
        2: {
            "name": "Define Context of Use",
            "vpcm_instantiation": (
                "Clinical-trial enrichment / patient-stratification, "
                "drug-repurposing hypotheses, and biomarker strategy planning."
            ),
        },
        3: {
            "name": "Assess model risk",
            "vpcm_instantiation": (
                "High model influence x Moderate consequence -> Significant tier."
            ),
        },
        4: {
            "name": "Develop credibility assessment plan",
            "vpcm_instantiation": (
                "Phases 1-7 plus ASME V&V 40 evidence plan and CI gates."
            ),
        },
        5: {
            "name": "Execute the plan",
            "vpcm_instantiation": (
                "Beat-the-mean, conformal coverage, OOD refusal, outcome, "
                "and prospective benchmark gates."
            ),
        },
        6: {
            "name": "Document results in credibility report",
            "vpcm_instantiation": (
                "Signed model card, report bundle, and ASME V&V 40 dossier."
            ),
        },
        7: {
            "name": "Determine adequacy for COU",
            "vpcm_instantiation": (
                "Adequate only if all thresholds pass and OOD recall >=0.95."
            ),
        },
    }

    def to_dict(self) -> dict[str, JSONValue]:
        """Return JSON-compatible FDA map."""

        return cast(dict[str, JSONValue], {
            str(step): payload for step, payload in self.steps.items()
        })

    def validate_complete(self) -> bool:
        """Return whether all seven steps have VPCM instantiations."""

        return set(self.steps) == set(range(1, 8)) and all(
            payload.get("vpcm_instantiation") for payload in self.steps.values()
        )

    def render_markdown(self) -> str:
        """Return a compact Markdown mapping table."""

        lines = ["# FDA 7-Step Credibility Map", "", "| Step | Evidence |", "|---|---|"]
        for step, payload in sorted(self.steps.items()):
            lines.append(
                f"| {step}. {payload['name']} | {payload['vpcm_instantiation']} |"
            )
        return "\n".join(lines) + "\n"
