# models/abstract_metadata.py - COMPREHENSIVE SCHEMA

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class StudyType(str, Enum):
    PHASE_1 = "Phase 1"
    PHASE_1_2 = "Phase 1/2"
    PHASE_2 = "Phase 2"
    PHASE_3 = "Phase 3"
    RETROSPECTIVE = "Retrospective"
    REAL_WORLD = "Real-World Evidence"
    META_ANALYSIS = "Meta-Analysis"
    REGISTRY = "Registry Study"

class MMSubtype(str, Enum):
    NDMM = "Newly Diagnosed"
    RRMM = "Relapsed/Refractory"
    HIGH_RISK = "High-Risk"
    ELDERLY = "Elderly"
    TRANSPLANT_ELIGIBLE = "Transplant Eligible"
    TRANSPLANT_INELIGIBLE = "Transplant Ineligible"
    SMOLDERING = "Smoldering"

class StudyIdentification(BaseModel):
    """Study identification and metadata"""
    title: str = Field(description="Full study title")
    study_acronym: Optional[str] = Field(default=None, description="Study acronym/short name")
    nct_number: Optional[str] = Field(default=None, description="ClinicalTrials.gov identifier")
    abstract_number: Optional[str] = Field(default=None, description="Conference abstract number")
    study_group: Optional[str] = Field(default=None, description="Sponsoring organization")
    principal_investigator: Optional[str] = Field(default=None, description="Lead investigator")
    publication_year: Optional[int] = Field(default=None, description="Publication/presentation year")
    conference_name: Optional[str] = Field(default=None, description="Conference name (e.g., ASCO)")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class StudyDesign(BaseModel):
    """Comprehensive study design characteristics"""
    study_type: StudyType
    trial_phase: Optional[str] = Field(default=None, description="Phase designation")
    randomized: bool = Field(default=False)
    blinded: bool = Field(default=False)
    placebo_controlled: bool = Field(default=False)
    multicenter: bool = Field(default=False)
    international: bool = Field(default=False)
    
    # Design specifics
    number_of_arms: Optional[int] = Field(default=None, description="Number of treatment arms")
    randomization_ratio: Optional[str] = Field(default=None, description="e.g., 1:1, 2:1")
    number_of_centers: Optional[int] = Field(default=None, description="Number of participating centers")
    countries: Optional[List[str]] = Field(default=None, description="Countries involved")
    
    # Timeline
    enrollment_period: Optional[str] = Field(default=None, description="Study enrollment period")
    follow_up_duration: Optional[float] = Field(default=None, description="Median follow-up in months")
    data_cutoff_date: Optional[str] = Field(default=None, description="Data cutoff date")
    
    # Endpoints
    primary_endpoints: Optional[List[str]] = Field(default=None, description="Primary endpoints")
    secondary_endpoints: Optional[List[str]] = Field(default=None, description="Secondary endpoints")
    exploratory_endpoints: Optional[List[str]] = Field(default=None, description="Exploratory endpoints")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class PatientDemographics(BaseModel):
    """Detailed patient population characteristics"""
    # Sample sizes
    total_enrolled: Optional[int] = Field(description="Total patients enrolled")
    evaluable_patients: Optional[int] = Field(description="Evaluable population")
    safety_population: Optional[int] = Field(description="Safety population")
    itt_population: Optional[int] = Field(description="Intent-to-treat population")
    
    # Age characteristics
    median_age: Optional[float] = Field(description="Median age in years")
    mean_age: Optional[float] = Field(description="Mean age in years")
    age_range: Optional[str] = Field(description="Age range (min-max)")
    elderly_percentage: Optional[float] = Field(description="Patients ≥65 years (%)")
    very_elderly_percentage: Optional[float] = Field(description="Patients ≥75 years (%)")
    
    # Gender and demographics
    male_percentage: Optional[float] = Field(description="Male patients (%)")
    female_percentage: Optional[float] = Field(description="Female patients (%)")
    race_distribution: Optional[Dict[str, float]] = Field(description="Race/ethnicity breakdown")
    
    # Performance status
    ecog_0_percentage: Optional[float] = Field(description="ECOG PS 0 (%)")
    ecog_1_percentage: Optional[float] = Field(description="ECOG PS 1 (%)")
    ecog_2_plus_percentage: Optional[float] = Field(description="ECOG PS ≥2 (%)")
    karnofsky_median: Optional[float] = Field(description="Median Karnofsky score")
    frailty_score_high: Optional[float] = Field(description="High frailty score (%)")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class DiseaseCharacteristics(BaseModel):
    """Disease-specific characteristics"""
    mm_subtype: List[MMSubtype] = Field(description="MM subtype classifications")
    disease_stage: Optional[str] = Field(description="Disease stage (ISS, R-ISS)")
    
    # Risk stratification
    high_risk_percentage: Optional[float] = Field(description="High-risk patients (%)")
    standard_risk_percentage: Optional[float] = Field(description="Standard-risk patients (%)")
    ultra_high_risk_percentage: Optional[float] = Field(description="Ultra high-risk (%)")
    
    # Cytogenetics
    cytogenetic_abnormalities: Optional[List[Dict[str, Any]]] = Field(
        description="Cytogenetic abnormalities with frequencies"
    )
    del_17p_percentage: Optional[float] = Field(description="del(17p) frequency (%)")
    t_4_14_percentage: Optional[float] = Field(description="t(4;14) frequency (%)")
    t_14_16_percentage: Optional[float] = Field(description="t(14;16) frequency (%)")
    amp_1q_percentage: Optional[float] = Field(description="1q amplification (%)")
    
    # Disease features
    extramedullary_disease_percentage: Optional[float] = Field(description="EMD presence (%)")
    plasma_cell_leukemia_percentage: Optional[float] = Field(description="PCL (%)")
    amyloidosis_percentage: Optional[float] = Field(description="Amyloidosis (%)")
    
    # Laboratory values
    ldh_elevated_percentage: Optional[float] = Field(description="Elevated LDH (%)")
    beta2_microglobulin_high: Optional[float] = Field(description="High β2-microglobulin (%)")
    albumin_low_percentage: Optional[float] = Field(description="Low albumin (%)")
    renal_impairment_percentage: Optional[float] = Field(description="Renal impairment (%)")
    
    # Biomarkers
    biomarker_results: Optional[List[Dict[str, Any]]] = Field(description="Biomarker analysis results")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class TreatmentHistory(BaseModel):
    """Prior treatment and therapy history"""
    line_of_therapy: Optional[str] = Field(description="Treatment line (1st, 2nd, 3rd+)")
    treatment_setting: Optional[str] = Field(description="NDMM/RRMM/maintenance")
    
    # Prior therapy metrics
    median_prior_therapies: Optional[float] = Field(description="Median number of prior therapies")
    prior_therapy_range: Optional[str] = Field(description="Range of prior therapies")
    heavily_pretreated_percentage: Optional[float] = Field(description="≥3 prior therapies (%)")
    
    # Specific prior therapies
    prior_therapies: Optional[List[Dict[str, Any]]] = Field(
        description="Specific prior therapies with exposure rates"
    )
    lenalidomide_exposed_percentage: Optional[float] = Field(description="Prior lenalidomide (%)")
    lenalidomide_refractory_percentage: Optional[float] = Field(description="Lenalidomide-refractory (%)")
    pomalidomide_exposed_percentage: Optional[float] = Field(description="Prior pomalidomide (%)")
    bortezomib_exposed_percentage: Optional[float] = Field(description="Prior bortezomib (%)")
    carfilzomib_exposed_percentage: Optional[float] = Field(description="Prior carfilzomib (%)")
    daratumumab_exposed_percentage: Optional[float] = Field(description="Prior daratumumab (%)")
    daratumumab_refractory_percentage: Optional[float] = Field(description="Daratumumab-refractory (%)")
    
    # Transplant history
    prior_autologous_sct_percentage: Optional[float] = Field(description="Prior auto-SCT (%)")
    prior_allogeneic_sct_percentage: Optional[float] = Field(description="Prior allo-SCT (%)")
    
    # Refractory patterns
    double_refractory_percentage: Optional[float] = Field(description="Double-refractory (%)")
    triple_refractory_percentage: Optional[float] = Field(description="Triple-refractory (%)")
    penta_refractory_percentage: Optional[float] = Field(description="Penta-refractory (%)")
    
    # Timing
    time_since_diagnosis_median: Optional[float] = Field(description="Time since diagnosis (months)")
    time_since_last_therapy_median: Optional[float] = Field(description="Time since last therapy (months)")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class TreatmentRegimen(BaseModel):
    """Treatment regimen information"""
    regimen_name: str = Field(description="Treatment regimen name/acronym")
    arm_designation: Optional[str] = Field(default=None, description="Treatment arm designation")
    is_novel_regimen: bool = Field(default=False, description="Whether this is a novel regimen")
    drugs: List[Dict[str, Any]] = Field(default_factory=list, description="Individual drug details")
    drug_classes: Optional[List[str]] = Field(default=None, description="Drug class categories")
    mechanism_of_action: Optional[List[str]] = Field(default=None, description="Mechanisms of action")
    cycle_length: Optional[int] = Field(default=None, description="Cycle length in days")
    total_planned_cycles: Optional[int] = Field(default=None, description="Total planned cycles")
    treatment_until_progression: bool = Field(default=False, description="Treatment until progression")
    dose_reductions_allowed: bool = Field(default=True, description="Dose reductions allowed")
    growth_factor_support: Optional[str] = Field(default=None, description="Growth factor support")
    premedications: Optional[List[str]] = Field(default=None, description="Required premedications")
    outpatient_administration: bool = Field(default=True, description="Outpatient administration")
    hospitalization_required: bool = Field(default=False, description="Hospitalization required")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class EfficacyOutcomes(BaseModel):
    """Comprehensive efficacy results"""
    # Response rates
    overall_response_rate: Optional[Dict[str, Any]] = Field(description="ORR with CI and p-value")
    complete_response_rate: Optional[Dict[str, Any]] = Field(description="CR rate")
    very_good_partial_response_rate: Optional[Dict[str, Any]] = Field(description="VGPR rate")
    partial_response_rate: Optional[Dict[str, Any]] = Field(description="PR rate")
    stable_disease_rate: Optional[Dict[str, Any]] = Field(description="SD rate")
    progressive_disease_rate: Optional[Dict[str, Any]] = Field(description="PD rate")
    clinical_benefit_rate: Optional[Dict[str, Any]] = Field(description="CBR (CR+VGPR+PR+SD)")
    
    # Survival outcomes
    progression_free_survival: Optional[Dict[str, Any]] = Field(description="PFS data")
    overall_survival: Optional[Dict[str, Any]] = Field(description="OS data")
    event_free_survival: Optional[Dict[str, Any]] = Field(description="EFS data")
    time_to_next_treatment: Optional[Dict[str, Any]] = Field(description="TTNT data")
    
    # Response kinetics
    time_to_response: Optional[Dict[str, Any]] = Field(description="Time to first response")
    duration_of_response: Optional[Dict[str, Any]] = Field(description="DOR data")
    time_to_progression: Optional[Dict[str, Any]] = Field(description="TTP data")
    
    # Deep response measures
    mrd_negative_rate: Optional[Dict[str, Any]] = Field(description="MRD negativity rate")
    mrd_method: Optional[str] = Field(description="MRD detection method")
    stringent_cr_rate: Optional[Dict[str, Any]] = Field(description="sCR rate")
    
    # Subgroup analyses
    subgroup_analyses: Optional[List[Dict[str, Any]]] = Field(description="Subgroup efficacy results")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class SafetyProfile(BaseModel):
    """Comprehensive safety and tolerability data"""
    safety_population: Optional[int] = Field(description="Safety evaluable population")
    
    # Treatment exposure
    median_treatment_duration: Optional[float] = Field(description="Median treatment duration (months)")
    median_cycles_received: Optional[float] = Field(description="Median cycles received")
    completion_rate: Optional[float] = Field(description="Treatment completion rate (%)")
    
    # Adverse events
    any_grade_aes: Optional[List[Dict[str, Any]]] = Field(description="Any grade AEs")
    grade_3_4_aes: Optional[List[Dict[str, Any]]] = Field(description="Grade 3-4 AEs")
    grade_5_aes: Optional[List[Dict[str, Any]]] = Field(description="Grade 5 (fatal) AEs")
    serious_aes: Optional[List[Dict[str, Any]]] = Field(description="Serious AEs")
    treatment_related_aes: Optional[List[Dict[str, Any]]] = Field(description="Treatment-related AEs")
    
    # Specific AE categories
    hematologic_aes: Optional[List[Dict[str, Any]]] = Field(description="Hematologic toxicities")
    infections: Optional[List[Dict[str, Any]]] = Field(description="Infection rates")
    secondary_malignancies: Optional[List[Dict[str, Any]]] = Field(description="Secondary cancers")
    
    # Dose modifications
    dose_reductions: Optional[Dict[str, Any]] = Field(description="Dose reduction rates and reasons")
    treatment_delays: Optional[Dict[str, Any]] = Field(description="Treatment delay rates")
    discontinuations: Optional[Dict[str, Any]] = Field(description="Discontinuation rates and reasons")
    
    # Deaths and serious outcomes
    treatment_related_deaths: Optional[int] = Field(description="Treatment-related deaths")
    total_deaths: Optional[int] = Field(description="Total deaths during study")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class QualityOfLife(BaseModel):
    """Quality of life and patient-reported outcomes"""
    qol_instruments: Optional[List[str]] = Field(description="QoL instruments used")
    baseline_qol_scores: Optional[Dict[str, float]] = Field(description="Baseline QoL scores")
    qol_improvement_rate: Optional[float] = Field(description="QoL improvement rate (%)")
    symptom_relief_rate: Optional[float] = Field(description="Symptom relief rate (%)")
    time_to_qol_improvement: Optional[float] = Field(description="Time to QoL improvement")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class StatisticalAnalysis(BaseModel):
    """Statistical methodology and results"""
    primary_analysis_method: Optional[str] = Field(description="Primary statistical method")
    significance_level: Optional[float] = Field(description="Alpha level")
    power_calculation: Optional[str] = Field(description="Statistical power details")
    sample_size_rationale: Optional[str] = Field(description="Sample size calculation")
    
    # Survival analysis
    survival_analysis_method: Optional[str] = Field(description="Survival analysis method")
    censoring_details: Optional[str] = Field(description="Censoring information")
    
    # Comparative analysis
    hazard_ratios: Optional[List[Dict[str, Any]]] = Field(description="Hazard ratios with CIs")
    p_values: Optional[Dict[str, float]] = Field(description="Key p-values")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)

class ComprehensiveAbstractMetadata(BaseModel):
    """Master metadata model with all 50+ elements"""
    # Core identification
    abstract_id: str = Field(description="Unique abstract identifier")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    
    # Major data categories
    study_identification: StudyIdentification
    study_design: StudyDesign
    patient_demographics: PatientDemographics
    disease_characteristics: DiseaseCharacteristics
    treatment_history: TreatmentHistory
    treatment_regimens: List[TreatmentRegimen]
    efficacy_outcomes: EfficacyOutcomes
    safety_profile: SafetyProfile
    quality_of_life: Optional[QualityOfLife] = None
    statistical_analysis: StatisticalAnalysis
    
    # Meta information
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    data_completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    clinical_significance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Source information
    source_text: Optional[str] = Field(default=None, description="Original abstract text")
    source_file: Optional[str] = Field(default=None, description="Source file name")
    processing_notes: Optional[List[str]] = Field(default_factory=list, description="Processing notes and warnings") 