# config/cancer_types.py - CANCER TYPE DEFINITIONS

from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel

class CancerType(str, Enum):
    """Supported cancer types with display names"""
    MULTIPLE_MYELOMA = "multiple_myeloma"
    BREAST_CANCER = "breast_cancer"
    LUNG_CANCER = "lung_cancer"
    COLORECTAL = "colorectal"
    LYMPHOMA = "lymphoma"
    LEUKEMIA = "leukemia"
    MELANOMA = "melanoma"
    OVARIAN = "ovarian"
    PANCREATIC = "pancreatic"
    PROSTATE = "prostate"

class CancerTypeConfig(BaseModel):
    """Configuration for each cancer type"""
    id: str
    display_name: str
    description: str
    icon: str
    color_primary: str
    color_secondary: str
    specializations: List[str]
    key_endpoints: List[str]
    typical_treatments: List[str]
    available_years: List[int]  # ASCO years with data available

# Cancer type configurations
CANCER_TYPE_CONFIGS = {
    CancerType.MULTIPLE_MYELOMA: CancerTypeConfig(
        id="multiple_myeloma",
        display_name="Multiple Myeloma",
        description="Plasma cell malignancy affecting bone marrow",
        icon="🩸",
        color_primary="#e53e3e",
        color_secondary="#feb2b2",
        specializations=["NDMM", "RRMM", "High-Risk", "Elderly", "Transplant Eligible"],
        key_endpoints=["Overall Response Rate", "Progression-Free Survival", "Overall Survival", "MRD Negativity"],
        typical_treatments=["Proteasome Inhibitors", "IMiDs", "Anti-CD38", "CAR-T", "Bispecific Antibodies"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.BREAST_CANCER: CancerTypeConfig(
        id="breast_cancer",
        display_name="Breast Cancer",
        description="Malignant tumor in breast tissue",
        icon="🎗️",
        color_primary="#d53f8c",
        color_secondary="#fbb6ce",
        specializations=["Triple Negative", "HER2+", "Hormone Receptor+", "Metastatic", "Early Stage"],
        key_endpoints=["Disease-Free Survival", "Overall Survival", "Pathological Complete Response", "Objective Response Rate"],
        typical_treatments=["Chemotherapy", "Targeted Therapy", "Immunotherapy", "Hormone Therapy", "CDK4/6 Inhibitors"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.LUNG_CANCER: CancerTypeConfig(
        id="lung_cancer",
        display_name="Lung Cancer",
        description="Malignant lung tumors including NSCLC and SCLC",
        icon="🫁",
        color_primary="#3182ce",
        color_secondary="#bee3f8",
        specializations=["NSCLC", "SCLC", "EGFR+", "ALK+", "PD-L1 High", "Squamous", "Adenocarcinoma"],
        key_endpoints=["Overall Survival", "Progression-Free Survival", "Objective Response Rate", "Duration of Response"],
        typical_treatments=["Immunotherapy", "Targeted Therapy", "Chemotherapy", "Radiation", "EGFR Inhibitors"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.COLORECTAL: CancerTypeConfig(
        id="colorectal",
        display_name="Colorectal Cancer",
        description="Malignancies of colon and rectum",
        icon="🎯",
        color_primary="#38a169",
        color_secondary="#c6f6d5",
        specializations=["Metastatic", "Adjuvant", "MSI-H", "KRAS Wild-type", "BRAF Mutant"],
        key_endpoints=["Overall Survival", "Progression-Free Survival", "Objective Response Rate", "Disease-Free Survival"],
        typical_treatments=["FOLFOX", "FOLFIRI", "Anti-VEGF", "Anti-EGFR", "Immunotherapy"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.LYMPHOMA: CancerTypeConfig(
        id="lymphoma",
        display_name="Lymphoma",
        description="Blood cancers affecting lymphatic system",
        icon="🔬",
        color_primary="#805ad5",
        color_secondary="#d6bcfa",
        specializations=["Hodgkin", "Non-Hodgkin", "DLBCL", "Follicular", "Mantle Cell", "T-Cell"],
        key_endpoints=["Complete Response Rate", "Overall Response Rate", "Event-Free Survival", "Overall Survival"],
        typical_treatments=["R-CHOP", "CAR-T Therapy", "Immunotherapy", "Targeted Therapy", "Stem Cell Transplant"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.LEUKEMIA: CancerTypeConfig(
        id="leukemia",
        display_name="Leukemia",
        description="Blood and bone marrow cancers",
        icon="💊",
        color_primary="#dd6b20",
        color_secondary="#fbd38d",
        specializations=["AML", "ALL", "CLL", "CML", "Pediatric", "Elderly"],
        key_endpoints=["Complete Remission Rate", "Overall Survival", "Event-Free Survival", "MRD Negativity"],
        typical_treatments=["Chemotherapy", "Targeted Therapy", "Immunotherapy", "Stem Cell Transplant", "CAR-T"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.MELANOMA: CancerTypeConfig(
        id="melanoma",
        display_name="Melanoma",
        description="Malignant skin cancer",
        icon="☀️",
        color_primary="#2d3748",
        color_secondary="#cbd5e0",
        specializations=["Metastatic", "Adjuvant", "BRAF Mutant", "BRAF Wild-type", "Mucosal", "Uveal"],
        key_endpoints=["Overall Survival", "Progression-Free Survival", "Objective Response Rate", "Recurrence-Free Survival"],
        typical_treatments=["Immunotherapy", "BRAF/MEK Inhibitors", "Targeted Therapy", "Interferon", "Interleukin-2"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.OVARIAN: CancerTypeConfig(
        id="ovarian",
        display_name="Ovarian Cancer",
        description="Malignancies of ovaries and fallopian tubes",
        icon="🌸",
        color_primary="#9f7aea",
        color_secondary="#e9d8fd",
        specializations=["High-Grade Serous", "BRCA Mutant", "HRD+", "Platinum-Sensitive", "Platinum-Resistant"],
        key_endpoints=["Progression-Free Survival", "Overall Survival", "Objective Response Rate", "CA-125 Response"],
        typical_treatments=["Chemotherapy", "PARP Inhibitors", "Anti-VEGF", "Immunotherapy", "Bevacizumab"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.PANCREATIC: CancerTypeConfig(
        id="pancreatic",
        display_name="Pancreatic Cancer",
        description="Adenocarcinoma of pancreas",
        icon="🥞",
        color_primary="#b83280",
        color_secondary="#f687b3",
        specializations=["Metastatic", "Locally Advanced", "Adjuvant", "BRCA Mutant", "MSI-H"],
        key_endpoints=["Overall Survival", "Progression-Free Survival", "Objective Response Rate", "Disease-Free Survival"],
        typical_treatments=["FOLFIRINOX", "Gemcitabine-based", "Immunotherapy", "Targeted Therapy", "PARP Inhibitors"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    ),
    CancerType.PROSTATE: CancerTypeConfig(
        id="prostate",
        display_name="Prostate Cancer",
        description="Adenocarcinoma of prostate gland",
        icon="👨",
        color_primary="#3182ce",
        color_secondary="#bee3f8",
        specializations=["Metastatic CRPC", "Hormone-Sensitive", "High-Risk", "Adjuvant", "Biochemical Recurrence"],
        key_endpoints=["Overall Survival", "Radiographic PFS", "PSA Response", "Time to PSA Progression"],
        typical_treatments=["Androgen Receptor Inhibitors", "Chemotherapy", "Immunotherapy", "Radium-223", "PARP Inhibitors"],
        available_years=[2020, 2021, 2022, 2023, 2024, 2025]
    )
}

def get_cancer_type_config(cancer_type: CancerType) -> CancerTypeConfig:
    """Get configuration for a specific cancer type"""
    return CANCER_TYPE_CONFIGS[cancer_type]

def get_all_cancer_types() -> List[CancerTypeConfig]:
    """Get all cancer type configurations"""
    return list(CANCER_TYPE_CONFIGS.values())

def get_cancer_type_by_id(cancer_id: str) -> CancerTypeConfig:
    """Get cancer type config by ID"""
    for cancer_type, config in CANCER_TYPE_CONFIGS.items():
        if config.id == cancer_id:
            return config
    raise ValueError(f"Cancer type not found: {cancer_id}")
