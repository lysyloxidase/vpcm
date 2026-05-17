"""Patient-specific LoRA fine-tuning for VPCM Phase 4."""

from vpcm_lora.patient_embedding import PatientCovariateEncoder
from vpcm_lora.patient_lora import LoRAAdapter, PatientLoRATrainer
from vpcm_lora.scimilarity_retrieval import AtlasNeighborRetrieval

__all__ = [
    "AtlasNeighborRetrieval",
    "LoRAAdapter",
    "PatientCovariateEncoder",
    "PatientLoRATrainer",
]

