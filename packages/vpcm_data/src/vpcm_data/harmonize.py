"""Identifier harmonization across VPCM datasets."""

from __future__ import annotations

import re
import uuid
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from vpcm_core.provenance import ProvenanceTracker


@dataclass(frozen=True)
class DrugIdentity:
    """Canonical drug identity."""

    chembl_id: str
    inchikey: str
    canonical_smiles: str


class IDHarmonizer:
    """Unified ID system across all VPCM datasets.

    Genes: Ensembl IDs (human GENCODE v45 / Ensembl 111)
    Drugs: ChEMBL IDs + InChIKey
    Diseases: MONDO + DOID
    Cell types: Cell Ontology + scTab labels
    Patients: opaque UUID + SHA-256 of input h5ad
    """

    _ENSEMBL_RE = re.compile(r"^ENSG[0-9]{11}$")
    _CHEMBL_RE = re.compile(r"^CHEMBL[0-9]+$")

    def __init__(self) -> None:
        self._hgnc_to_ensembl: dict[str, str] = {}
        self._ensembl_to_hgnc: dict[str, str] = {}
        self._drugs: dict[str, DrugIdentity] = {}

    def register_gene_mapping(self, hgnc_symbol: str, ensembl_id: str) -> None:
        """Register a bidirectional HGNC <-> Ensembl mapping."""

        normalized_hgnc = hgnc_symbol.upper()
        normalized_ensembl = self.normalize_ensembl(ensembl_id)
        self._hgnc_to_ensembl[normalized_hgnc] = normalized_ensembl
        self._ensembl_to_hgnc[normalized_ensembl] = normalized_hgnc

    def register_gene_mappings(self, mappings: Mapping[str, str]) -> None:
        """Register many HGNC <-> Ensembl mappings."""

        for hgnc_symbol, ensembl_id in mappings.items():
            self.register_gene_mapping(hgnc_symbol, ensembl_id)

    def normalize_ensembl(self, ensembl_id: str) -> str:
        """Normalize and validate an Ensembl gene ID."""

        versionless = ensembl_id.split(".", maxsplit=1)[0].upper()
        if not self._ENSEMBL_RE.fullmatch(versionless):
            raise ValueError(f"Invalid Ensembl gene ID: {ensembl_id}")
        return versionless

    def hgnc_to_ensembl(self, hgnc_symbol: str) -> str:
        """Map HGNC symbol to Ensembl ID."""

        return self._hgnc_to_ensembl[hgnc_symbol.upper()]

    def ensembl_to_hgnc(self, ensembl_id: str) -> str:
        """Map Ensembl ID to HGNC symbol."""

        return self._ensembl_to_hgnc[self.normalize_ensembl(ensembl_id)]

    def roundtrip_gene_ids(self, hgnc_symbols: Iterable[str]) -> float:
        """Return the fraction that round-trips HGNC -> Ensembl -> HGNC."""

        total = 0
        matched = 0
        for symbol in hgnc_symbols:
            total += 1
            ensembl_id = self.hgnc_to_ensembl(symbol)
            if self.ensembl_to_hgnc(ensembl_id) == symbol.upper():
                matched += 1
        if total == 0:
            return 1.0
        return matched / total

    def register_drug(self, chembl_id: str, inchikey: str, smiles: str) -> None:
        """Register a ChEMBL/InChIKey/SMILES mapping."""

        normalized_chembl = chembl_id.upper()
        if not self._CHEMBL_RE.fullmatch(normalized_chembl):
            raise ValueError(f"Invalid ChEMBL ID: {chembl_id}")
        self._drugs[normalized_chembl] = DrugIdentity(
            chembl_id=normalized_chembl,
            inchikey=inchikey.upper(),
            canonical_smiles=smiles,
        )

    def drug_identity(self, chembl_id: str) -> DrugIdentity:
        """Return canonical drug identity."""

        return self._drugs[chembl_id.upper()]

    def patient_identity(self, patient_h5ad_bytes: bytes) -> tuple[str, str]:
        """Return opaque patient UUID and SHA-256 h5ad hash."""

        patient_hash = ProvenanceTracker.patient_hash_bytes(patient_h5ad_bytes)
        patient_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, patient_hash))
        return patient_uuid, patient_hash


def synthetic_gene_mapping(size: int = 1000) -> dict[str, str]:
    """Generate deterministic synthetic HGNC/Ensembl mappings for QC tests."""

    return {f"GENE{index}": f"ENSG{index:011d}" for index in range(1, size + 1)}
