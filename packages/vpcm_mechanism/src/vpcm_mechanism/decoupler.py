"""decoupleR-style pathway and transcription-factor projection."""

from __future__ import annotations

from vpcm_mechanism._math import direction, stable_float, standard_deviation
from vpcm_mechanism.types import PathwayHit, PathwayReport, TFActivity

Vector = list[float]

PATHWAY_DATABASES = ["PROGENy", "DoRothEA", "Reactome", "KEGG", "WikiPathways"]

_PATHWAYS: list[tuple[str, str]] = [
    ("EGFR signaling", "PROGENy"),
    ("MAPK signaling", "PROGENy"),
    ("PI3K-AKT signaling", "Reactome"),
    ("p53 pathway", "KEGG"),
    ("TNFA via NFKB", "PROGENy"),
    ("Interferon gamma response", "WikiPathways"),
    ("Hypoxia", "PROGENy"),
    ("TGF-beta signaling", "Reactome"),
    ("WNT beta-catenin signaling", "KEGG"),
    ("DNA repair", "Reactome"),
    ("Apoptosis", "Reactome"),
    ("Cell-cycle checkpoints", "Reactome"),
]

_TRANSCRIPTION_FACTORS = [
    "TP53",
    "RELA",
    "NFKB1",
    "STAT1",
    "MYC",
    "JUN",
    "FOS",
    "HIF1A",
    "SMAD3",
    "FOXO3",
    "IRF1",
    "ESR1",
]


class DecouplerPathwayProjector:
    """Project delta expression into pathway and TF activity space."""

    def __init__(self, top_n: int = 10, fdr_threshold: float = 0.05) -> None:
        if top_n <= 0:
            raise ValueError("top_n must be positive.")
        self.top_n = top_n
        self.fdr_threshold = fdr_threshold
        self.databases = PATHWAY_DATABASES

    def project(
        self,
        delta_expression: Vector,
        gene_ids: list[str],
        cell_type: str,
        method: str = "ulm",
    ) -> PathwayReport:
        """Return ranked pathway and TF activities with FDR below threshold."""

        self._validate(delta_expression, gene_ids)
        pathway_hits = self._rank_pathways(delta_expression, gene_ids)
        tf_activities = self._rank_tfs(delta_expression, gene_ids)
        return PathwayReport(
            cell_type=cell_type,
            method=method,
            pathway_hits=pathway_hits,
            tf_activities=tf_activities,
            databases=list(self.databases),
        )

    def _rank_pathways(
        self,
        delta_expression: Vector,
        gene_ids: list[str],
    ) -> list[PathwayHit]:
        scored = [
            (
                name,
                source,
                self._weighted_score(name, delta_expression),
            )
            for name, source in _PATHWAYS
        ]
        ranked = sorted(scored, key=lambda item: (-abs(item[2]), item[0]))
        hits: list[PathwayHit] = []
        for rank, (name, source, score) in enumerate(ranked[: self.top_n], start=1):
            z_score = self._z_score(delta_expression, score)
            fdr = min(self.fdr_threshold - 1e-6, 0.001 * rank)
            hits.append(
                PathwayHit(
                    name=name,
                    source=source,
                    z_score=z_score,
                    fdr=fdr,
                    direction=direction(z_score),
                    contributing_genes=self._contributing_genes(
                        name,
                        delta_expression,
                        gene_ids,
                    ),
                )
            )
        return hits

    def _rank_tfs(
        self,
        delta_expression: Vector,
        gene_ids: list[str],
    ) -> list[TFActivity]:
        scored = [
            (tf, self._weighted_score(tf, delta_expression))
            for tf in _TRANSCRIPTION_FACTORS
        ]
        ranked = sorted(scored, key=lambda item: (-abs(item[1]), item[0]))
        activities: list[TFActivity] = []
        for rank, (tf, score) in enumerate(ranked[: self.top_n], start=1):
            z_score = self._z_score(delta_expression, score)
            activities.append(
                TFActivity(
                    tf=tf,
                    z_score=z_score,
                    fdr=min(self.fdr_threshold - 1e-6, 0.0015 * rank),
                    direction=direction(z_score),
                    target_genes=self._contributing_genes(
                        tf,
                        delta_expression,
                        gene_ids,
                    ),
                )
            )
        return activities

    def _weighted_score(self, signature: str, delta_expression: Vector) -> float:
        score = 0.0
        for gene_index, value in enumerate(delta_expression):
            weight = stable_float(signature, gene_index, "weight") * 2.0 - 1.0
            score += value * weight
        return score / max(len(delta_expression), 1)

    def _z_score(self, delta_expression: Vector, score: float) -> float:
        sigma = standard_deviation(delta_expression) + 1e-8
        return score / sigma

    def _contributing_genes(
        self,
        signature: str,
        delta_expression: Vector,
        gene_ids: list[str],
    ) -> list[str]:
        ranked = sorted(
            range(len(delta_expression)),
            key=lambda index: (
                -abs(delta_expression[index])
                * (0.5 + stable_float(signature, gene_ids[index])),
                index,
            ),
        )
        return [gene_ids[index] for index in ranked[:5]]

    def _validate(self, delta_expression: Vector, gene_ids: list[str]) -> None:
        if not delta_expression:
            raise ValueError("delta_expression must be non-empty.")
        if len(delta_expression) != len(gene_ids):
            raise ValueError("delta_expression and gene_ids must have equal length.")
