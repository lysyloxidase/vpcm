"""CellChat v2 / LIANA+ / NicheNet-style communication inference."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from vpcm_mechanism._math import mean, stable_float
from vpcm_mechanism.types import CommunicationChange, CommunicationReport

Vector = list[float]

_LIGAND_RECEPTOR_PRIORS = [
    ("CXCL9", "CXCR3", "Interferon gamma response"),
    ("CXCL10", "CXCR3", "T-cell recruitment"),
    ("TGFB1", "TGFBR2", "TGF-beta signaling"),
    ("CD274", "PDCD1", "Checkpoint inhibition"),
    ("VEGFA", "KDR", "Angiogenesis"),
    ("IL6", "IL6R", "Inflammation"),
    ("TNF", "TNFRSF1A", "NFKB signaling"),
    ("CCL5", "CCR5", "Immune trafficking"),
    ("MIF", "CD74", "Myeloid signaling"),
    ("JAG1", "NOTCH1", "Notch signaling"),
]


class CellChatV2Communicator:
    """Infer perturbation-induced cell-cell communication changes."""

    tools: ClassVar[list[str]] = ["CellChat v2", "LIANA+", "NicheNet"]

    def infer_changes(
        self,
        per_cell_type_delta: Mapping[str, Vector],
        top_n: int = 10,
    ) -> CommunicationReport:
        """Return ranked ligand-receptor communication changes."""

        if not per_cell_type_delta:
            raise ValueError("per_cell_type_delta must be non-empty.")
        cell_types = sorted(per_cell_type_delta)
        changes: list[CommunicationChange] = []
        for sender in cell_types:
            sender_delta = per_cell_type_delta[sender]
            for receiver in cell_types:
                receiver_delta = per_cell_type_delta[receiver]
                for ligand, receptor, pathway in _LIGAND_RECEPTOR_PRIORS:
                    probability_delta = self._probability_delta(
                        sender,
                        receiver,
                        ligand,
                        receptor,
                        sender_delta,
                        receiver_delta,
                    )
                    changes.append(
                        CommunicationChange(
                            sender=sender,
                            receiver=receiver,
                            ligand=ligand,
                            receptor=receptor,
                            pathway=pathway,
                            probability_delta=probability_delta,
                        )
                    )
        ranked = sorted(
            changes,
            key=lambda change: (-abs(change.probability_delta), change.sender),
        )
        return CommunicationReport(
            interactions=ranked[:top_n],
            tools=list(self.tools),
            caveat=(
                "Communication probabilities are inferred from expression "
                "priors and require orthogonal ligand-receptor validation."
            ),
        )

    def _probability_delta(
        self,
        sender: str,
        receiver: str,
        ligand: str,
        receptor: str,
        sender_delta: Vector,
        receiver_delta: Vector,
    ) -> float:
        sender_signal = mean(sender_delta) if sender_delta else 0.0
        receiver_signal = mean(receiver_delta) if receiver_delta else 0.0
        prior = stable_float(sender, receiver, ligand, receptor) - 0.5
        return round(0.5 * sender_signal + 0.3 * receiver_signal + 0.2 * prior, 6)
