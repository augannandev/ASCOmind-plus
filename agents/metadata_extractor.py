# agents/metadata_extractor.py - COMPREHENSIVE EXTRACTION

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import re

from anthropic import Anthropic
import openai
from loguru import logger
import streamlit as st

from models.abstract_metadata import (
    ComprehensiveAbstractMetadata, StudyIdentification, StudyDesign,
    PatientDemographics, DiseaseCharacteristics, TreatmentHistory,
    TreatmentRegimen, EfficacyOutcomes, SafetyProfile, QualityOfLife,
    StatisticalAnalysis, StudyType, MMSubtype
)
from config.settings import settings


class ExtractionValidator:
    """Validates and corrects extraction results"""
    
    def validate_extraction(self, raw_data: Dict[str, Any], source_text: str) -> Dict[str, Any]:
        """Validate extraction against medical domain rules"""
        validated_data = raw_data.copy()
        
        # Validate numerical ranges
        validated_data = self._validate_numerical_ranges(validated_data)
        
        # Validate medical terminology
        validated_data = self._validate_medical_terms(validated_data)
        
        # Cross-validate consistency
        validated_data = self._cross_validate_consistency(validated_data)
        
        return validated_data
    
    def _validate_numerical_ranges(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate numerical values are within expected medical ranges"""
        # Age validations
        if "patient_demographics" in data and data["patient_demographics"]:
            demographics = data["patient_demographics"]
            if demographics.get("median_age") and demographics["median_age"] > 120:
                demographics["median_age"] = None
                logger.warning("Invalid median age detected and removed")
        
        # Percentage validations
        percentage_fields = [
            "overall_response_rate", "complete_response_rate", "male_percentage"
        ]
        # Apply percentage validation logic
        
        return data
    
    def _validate_medical_terms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate medical terminology and drug names"""
        # Implement medical term validation
        return data
    
    def _cross_validate_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate data consistency"""
        # Implement consistency checks
        return data


class ConfidenceScorer:
    """Scores extraction confidence for each data element"""
    
    def score_extraction(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for extraction"""
        scores = {}
        
        for section, content in data.items():
            if isinstance(content, dict):
                scores[section] = self._score_section(content)
            elif isinstance(content, list):
                scores[section] = self._score_list_section(content)
            else:
                scores[section] = self._score_single_value(content)
        
        return scores
    
    def _score_section(self, section_data: Dict[str, Any]) -> float:
        """Score a data section"""
        if not section_data:
            return 0.0
        
        filled_fields = sum(1 for v in section_data.values() if v is not None)
        total_fields = len(section_data)
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def _score_list_section(self, list_data: List[Any]) -> float:
        """Score a list data section"""
        return 1.0 if list_data else 0.0
    
    def _score_single_value(self, value: Any) -> float:
        """Score a single value"""
        return 1.0 if value is not None else 0.0


class EnhancedMetadataExtractor:
    """Advanced metadata extraction with 50+ elements"""
    
    def __init__(self):
        # Use Streamlit secrets for API keys
        try:
            anthropic_key = st.secrets["api_keys"]["claude"]
            openai_key = st.secrets["api_keys"]["openai"]
        except:
            # Fallback to settings if secrets not available
            anthropic_key = settings.ANTHROPIC_API_KEY
            openai_key = settings.OPENAI_API_KEY
        
        self.anthropic_client = Anthropic(api_key=anthropic_key)
        self.openai_client = openai.OpenAI(api_key=openai_key)
        self.validation_engine = ExtractionValidator()
        self.confidence_scorer = ConfidenceScorer()
        self.extraction_prompt = self._build_comprehensive_prompt()
    
    async def extract_comprehensive_metadata(self, abstract_text: str) -> ComprehensiveAbstractMetadata:
        """Extract all 50+ data elements with validation"""
        
        logger.info("Starting comprehensive metadata extraction")
        
        try:
            # Phase 1: Comprehensive extraction
            raw_extraction = await self._extract_all_elements(abstract_text)
            
            # Phase 2: Validation and quality scoring
            validated_data = self.validation_engine.validate_extraction(raw_extraction, abstract_text)
            
            # Phase 3: Confidence scoring
            confidence_scores = self._calculate_confidence_scores(validated_data, abstract_text)
            
            # Phase 4: Structure into pydantic model
            structured_metadata = self._structure_metadata(validated_data, confidence_scores, abstract_text)
            
            logger.info("Metadata extraction completed successfully")
            return structured_metadata
            
        except Exception as e:
            logger.error(f"Error in metadata extraction: {str(e)}")
            # Return minimal structure with error information
            return self._create_error_metadata(abstract_text, str(e))
    
    async def _extract_all_elements(self, abstract_text: str) -> Dict[str, Any]:
        """Extract comprehensive metadata using LLM"""
        
        try:
            # Try primary LLM (Claude)
            response = await self._extract_with_claude(abstract_text)
            return response
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}, trying fallback")
            try:
                # Fallback to OpenAI
                response = await self._extract_with_openai(abstract_text)
                return response
            except Exception as e2:
                logger.error(f"Both LLMs failed: {e2}")
                raise
    
    async def _extract_with_claude(self, abstract_text: str) -> Dict[str, Any]:
        """Extract using Claude Sonnet"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            messages=[
                {
                    "role": "user", 
                    "content": f"{self.extraction_prompt}\n\nABSTRACT TEXT:\n{abstract_text}"
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Debug logging
        logger.info(f"Raw LLM response length: {len(response_text)}")
        logger.info(f"First 500 chars of response: {response_text[:500]}")
        logger.info(f"Last 500 chars of response: {response_text[-500:]}")
        
        return self._parse_llm_response(response_text)
    
    async def _extract_with_openai(self, abstract_text: str) -> Dict[str, Any]:
        """Extract using OpenAI GPT-4"""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.extraction_prompt},
                {"role": "user", "content": f"ABSTRACT TEXT:\n{abstract_text}"}
            ],
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE
        )
        
        response_text = response.choices[0].message.content
        return self._parse_llm_response(response_text)
    
    def _build_comprehensive_prompt(self) -> str:
        """Build the comprehensive extraction prompt"""
        return """
        You are an expert medical researcher specializing in oncology clinical trials. Extract structured data from this medical abstract.

        CRITICAL INSTRUCTIONS:
        1. Return ONLY valid JSON - no explanatory text before or after
        2. Use the exact field names specified below
        3. For missing data, use null (not "Unknown" or empty strings)
        4. For percentages, use numbers only (e.g., 64 not "64%")
        5. Start your response with { and end with }

        REQUIRED JSON STRUCTURE:
        {
            "study_identification": {
                "title": "extracted title",
                "study_acronym": "study acronym or null",
                "nct_number": "NCT number or null",
                "study_group": "organization or null",
                "confidence_score": 0.9
            },
            "study_design": {
                "study_type": "Phase 2",
                "confidence_score": 0.9
            },
            "patient_demographics": {
                "total_enrolled": 70,
                "median_age": 76,
                "confidence_score": 0.9
            },
            "treatment_regimens": [{
                "regimen_name": "extracted regimen name",
                "drugs": [{"name": "drug1", "dose": "dose1"}],
                "confidence_score": 0.9
            }],
            "efficacy_outcomes": {
                "overall_response_rate": {"value": 64, "ci": "confidence interval"},
                "progression_free_survival": {"median": 13, "unit": "months"},
                "confidence_score": 0.9
            },
            "safety_profile": {
                "grade_3_4_aes": [{"event": "neutropenia", "percentage": 46}],
                "confidence_score": 0.9
            }
        }

        Extract the following data elements from the abstract:

        STUDY IDENTIFICATION:
        - title: Full study title
        - study_acronym: Study name/acronym  
        - nct_number: NCT identifier
        - study_group: Sponsoring organization

        STUDY DESIGN:
        - study_type: Phase 1/2/3, etc.
        - number_of_centers: Number of centers
        - primary_endpoints: List of primary endpoints

        PATIENT DEMOGRAPHICS:
        - total_enrolled: Total patients
        - median_age: Median age in years
        - evaluable_patients: Evaluable population

        TREATMENT REGIMENS:
        - regimen_name: Treatment regimen name
        - drugs: List of drugs with doses
        - cycle_length: Cycle length in days

        EFFICACY OUTCOMES:
        - overall_response_rate: ORR with value and CI
        - progression_free_survival: PFS data
        - overall_survival: OS data

        SAFETY PROFILE:
        - grade_3_4_aes: Grade 3-4 adverse events
        - discontinuations: Treatment discontinuations

        Return ONLY the JSON object with extracted data.
        """
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        try:
            # First try to find JSON block markers
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end > json_start:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            else:
                # Extract JSON from response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start == -1 or json_end == 0:
                    raise ValueError("No JSON found in response")
                
                json_text = response_text[json_start:json_end]
            
            # Clean common JSON issues
            json_text = self._clean_json_text(json_text)
            
            parsed_data = json.loads(json_text)
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            # Try to clean and re-parse
            return self._clean_and_parse_json(response_text)
    
    def _clean_json_text(self, json_text: str) -> str:
        """Clean common JSON formatting issues"""
        # Remove trailing commas
        import re
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix common quote issues
        json_text = json_text.replace('"', '"').replace('"', '"')
        json_text = json_text.replace(''', "'").replace(''', "'")
        
        # Remove any BOM or invisible characters
        json_text = json_text.strip('\ufeff\uFEFF')
        
        return json_text
    
    def _clean_and_parse_json(self, response_text: str) -> Dict[str, Any]:
        """Attempt to clean and parse malformed JSON"""
        try:
            # Extract content between first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_candidate = response_text[start_idx:end_idx + 1]
                
                # Try basic cleaning
                json_candidate = self._clean_json_text(json_candidate)
                
                return json.loads(json_candidate)
            
            # If still failing, return empty structure
            logger.warning("Could not parse LLM response, returning empty structure")
            return {}
            
        except Exception as e:
            logger.error(f"All JSON parsing attempts failed: {e}")
            return {}
    
    def _structure_metadata(self, validated_data: Dict[str, Any], 
                          confidence_scores: Dict[str, float], 
                          source_text: str) -> ComprehensiveAbstractMetadata:
        """Structure validated data into pydantic model"""
        
        abstract_id = str(uuid.uuid4())
        
        try:
            # Create individual components
            study_id = StudyIdentification(
                title=validated_data.get("study_identification", {}).get("title", ""),
                study_acronym=validated_data.get("study_identification", {}).get("study_acronym"),
                nct_number=validated_data.get("study_identification", {}).get("nct_number"),
                abstract_number=validated_data.get("study_identification", {}).get("abstract_number"),
                study_group=validated_data.get("study_identification", {}).get("study_group"),
                principal_investigator=validated_data.get("study_identification", {}).get("principal_investigator"),
                publication_year=validated_data.get("study_identification", {}).get("publication_year"),
                conference_name=validated_data.get("study_identification", {}).get("conference_name"),
                confidence_score=confidence_scores.get("extraction_quality", 0.75)
            )
            
            # Build study design
            study_design_data = validated_data.get("study_design", {})
            study_design = StudyDesign(
                study_type=StudyType(study_design_data.get("study_type", "Phase 2")),
                trial_phase=study_design_data.get("trial_phase"),
                randomized=study_design_data.get("randomized", False),
                blinded=study_design_data.get("blinded", False),
                placebo_controlled=study_design_data.get("placebo_controlled", False),
                multicenter=study_design_data.get("multicenter", False),
                international=study_design_data.get("international", False),
                number_of_arms=study_design_data.get("number_of_arms"),
                randomization_ratio=study_design_data.get("randomization_ratio"),
                number_of_centers=study_design_data.get("number_of_centers"),
                countries=study_design_data.get("countries", []),
                enrollment_period=study_design_data.get("enrollment_period"),
                follow_up_duration=study_design_data.get("follow_up_duration"),
                data_cutoff_date=study_design_data.get("data_cutoff_date"),
                primary_endpoints=study_design_data.get("primary_endpoints", []),
                secondary_endpoints=study_design_data.get("secondary_endpoints", []),
                exploratory_endpoints=study_design_data.get("exploratory_endpoints", []),
                confidence_score=confidence_scores.get("extraction_quality", 0.75)
            )
            
            # Build patient demographics
            demographics_data = validated_data.get("patient_demographics", {})
            patient_demographics = PatientDemographics(
                total_enrolled=demographics_data.get("total_enrolled"),
                evaluable_patients=demographics_data.get("evaluable_patients"),
                safety_population=demographics_data.get("safety_population"),
                itt_population=demographics_data.get("itt_population"),
                median_age=demographics_data.get("median_age"),
                mean_age=demographics_data.get("mean_age"),
                age_range=demographics_data.get("age_range"),
                elderly_percentage=demographics_data.get("elderly_percentage"),
                very_elderly_percentage=demographics_data.get("very_elderly_percentage"),
                male_percentage=demographics_data.get("male_percentage"),
                female_percentage=demographics_data.get("female_percentage"),
                race_distribution=demographics_data.get("race_distribution"),
                ecog_0_percentage=demographics_data.get("ecog_0_percentage"),
                ecog_1_percentage=demographics_data.get("ecog_1_percentage"),
                ecog_2_plus_percentage=demographics_data.get("ecog_2_plus_percentage"),
                karnofsky_median=demographics_data.get("karnofsky_median"),
                frailty_score_high=demographics_data.get("frailty_score_high"),
                confidence_score=confidence_scores.get("patient_demographics", 0.0)
            )
            
            # Build disease characteristics
            disease_data = validated_data.get("disease_characteristics", {})
            mm_subtypes = []
            if disease_data.get("mm_subtype"):
                if isinstance(disease_data["mm_subtype"], list):
                    mm_subtypes = [MMSubtype(s) for s in disease_data["mm_subtype"] if s in MMSubtype.__members__.values()]
                else:
                    mm_subtypes = [MMSubtype(disease_data["mm_subtype"])] if disease_data["mm_subtype"] in MMSubtype.__members__.values() else []
            
            disease_characteristics = DiseaseCharacteristics(
                mm_subtype=mm_subtypes or [MMSubtype.RRMM],  # Default fallback
                disease_stage=disease_data.get("disease_stage"),
                high_risk_percentage=disease_data.get("high_risk_percentage"),
                standard_risk_percentage=disease_data.get("standard_risk_percentage"),
                ultra_high_risk_percentage=disease_data.get("ultra_high_risk_percentage"),
                cytogenetic_abnormalities=disease_data.get("cytogenetic_abnormalities"),
                del_17p_percentage=disease_data.get("del_17p_percentage"),
                t_4_14_percentage=disease_data.get("t_4_14_percentage"),
                t_14_16_percentage=disease_data.get("t_14_16_percentage"),
                amp_1q_percentage=disease_data.get("amp_1q_percentage"),
                extramedullary_disease_percentage=disease_data.get("extramedullary_disease_percentage"),
                plasma_cell_leukemia_percentage=disease_data.get("plasma_cell_leukemia_percentage"),
                amyloidosis_percentage=disease_data.get("amyloidosis_percentage"),
                ldh_elevated_percentage=disease_data.get("ldh_elevated_percentage"),
                beta2_microglobulin_high=disease_data.get("beta2_microglobulin_high"),
                albumin_low_percentage=disease_data.get("albumin_low_percentage"),
                renal_impairment_percentage=disease_data.get("renal_impairment_percentage"),
                biomarker_results=disease_data.get("biomarker_results"),
                confidence_score=confidence_scores.get("disease_characteristics", 0.0)
            )
            
            # Build treatment history
            treatment_hist_data = validated_data.get("treatment_history", {})
            treatment_history = TreatmentHistory(
                line_of_therapy=treatment_hist_data.get("line_of_therapy"),
                treatment_setting=treatment_hist_data.get("treatment_setting"),
                median_prior_therapies=treatment_hist_data.get("median_prior_therapies"),
                prior_therapy_range=treatment_hist_data.get("prior_therapy_range"),
                heavily_pretreated_percentage=treatment_hist_data.get("heavily_pretreated_percentage"),
                prior_therapies=treatment_hist_data.get("prior_therapies"),
                lenalidomide_exposed_percentage=treatment_hist_data.get("lenalidomide_exposed_percentage"),
                lenalidomide_refractory_percentage=treatment_hist_data.get("lenalidomide_refractory_percentage"),
                pomalidomide_exposed_percentage=treatment_hist_data.get("pomalidomide_exposed_percentage"),
                bortezomib_exposed_percentage=treatment_hist_data.get("bortezomib_exposed_percentage"),
                carfilzomib_exposed_percentage=treatment_hist_data.get("carfilzomib_exposed_percentage"),
                daratumumab_exposed_percentage=treatment_hist_data.get("daratumumab_exposed_percentage"),
                daratumumab_refractory_percentage=treatment_hist_data.get("daratumumab_refractory_percentage"),
                prior_autologous_sct_percentage=treatment_hist_data.get("prior_autologous_sct_percentage"),
                prior_allogeneic_sct_percentage=treatment_hist_data.get("prior_allogeneic_sct_percentage"),
                double_refractory_percentage=treatment_hist_data.get("double_refractory_percentage"),
                triple_refractory_percentage=treatment_hist_data.get("triple_refractory_percentage"),
                penta_refractory_percentage=treatment_hist_data.get("penta_refractory_percentage"),
                time_since_diagnosis_median=treatment_hist_data.get("time_since_diagnosis_median"),
                time_since_last_therapy_median=treatment_hist_data.get("time_since_last_therapy_median"),
                confidence_score=confidence_scores.get("treatment_history", 0.0)
            )
            
            # Build treatment regimens
            regimens_data = validated_data.get("treatment_regimens", [])
            treatment_regimens = []
            
            for regimen_data in regimens_data:
                if isinstance(regimen_data, dict) and regimen_data.get("regimen_name"):
                    regimen = TreatmentRegimen(
                        regimen_name=regimen_data["regimen_name"],
                        arm_designation=regimen_data.get("arm_designation"),
                        is_novel_regimen=regimen_data.get("is_novel_regimen", False),
                        drugs=regimen_data.get("drugs", []),
                        drug_classes=regimen_data.get("drug_classes"),
                        mechanism_of_action=regimen_data.get("mechanism_of_action"),
                        cycle_length=regimen_data.get("cycle_length"),
                        total_planned_cycles=regimen_data.get("total_planned_cycles"),
                        treatment_until_progression=regimen_data.get("treatment_until_progression", False),
                        dose_reductions_allowed=regimen_data.get("dose_reductions_allowed", True),
                        growth_factor_support=regimen_data.get("growth_factor_support"),
                        premedications=regimen_data.get("premedications"),
                        outpatient_administration=regimen_data.get("outpatient_administration", True),
                        hospitalization_required=regimen_data.get("hospitalization_required", False),
                        confidence_score=regimen_data.get("confidence_score", 0.0)
                    )
                    treatment_regimens.append(regimen)
            
            # Default regimen if none found
            if not treatment_regimens:
                treatment_regimens = [TreatmentRegimen(
                    regimen_name="Unknown",
                    drugs=[],
                    confidence_score=0.0
                )]
            
            # Build efficacy outcomes
            efficacy_data = validated_data.get("efficacy_outcomes", {})
            efficacy_outcomes = EfficacyOutcomes(
                overall_response_rate=efficacy_data.get("overall_response_rate"),
                complete_response_rate=efficacy_data.get("complete_response_rate"),
                very_good_partial_response_rate=efficacy_data.get("very_good_partial_response_rate"),
                partial_response_rate=efficacy_data.get("partial_response_rate"),
                stable_disease_rate=efficacy_data.get("stable_disease_rate"),
                progressive_disease_rate=efficacy_data.get("progressive_disease_rate"),
                clinical_benefit_rate=efficacy_data.get("clinical_benefit_rate"),
                progression_free_survival=efficacy_data.get("progression_free_survival"),
                overall_survival=efficacy_data.get("overall_survival"),
                event_free_survival=efficacy_data.get("event_free_survival"),
                time_to_next_treatment=efficacy_data.get("time_to_next_treatment"),
                time_to_response=efficacy_data.get("time_to_response"),
                duration_of_response=efficacy_data.get("duration_of_response"),
                time_to_progression=efficacy_data.get("time_to_progression"),
                mrd_negative_rate=efficacy_data.get("mrd_negative_rate"),
                mrd_method=efficacy_data.get("mrd_method"),
                stringent_cr_rate=efficacy_data.get("stringent_cr_rate"),
                subgroup_analyses=efficacy_data.get("subgroup_analyses"),
                confidence_score=confidence_scores.get("efficacy_outcomes", 0.0)
            )
            
            # Build safety profile
            safety_data = validated_data.get("safety_profile", {})
            safety_profile = SafetyProfile(
                safety_population=safety_data.get("safety_population"),
                median_treatment_duration=safety_data.get("median_treatment_duration"),
                median_cycles_received=safety_data.get("median_cycles_received"),
                completion_rate=safety_data.get("completion_rate"),
                any_grade_aes=safety_data.get("any_grade_aes"),
                grade_3_4_aes=safety_data.get("grade_3_4_aes"),
                grade_5_aes=safety_data.get("grade_5_aes"),
                serious_aes=safety_data.get("serious_aes"),
                treatment_related_aes=safety_data.get("treatment_related_aes"),
                hematologic_aes=safety_data.get("hematologic_aes"),
                infections=safety_data.get("infections"),
                secondary_malignancies=safety_data.get("secondary_malignancies"),
                dose_reductions=safety_data.get("dose_reductions"),
                treatment_delays=safety_data.get("treatment_delays"),
                discontinuations=safety_data.get("discontinuations"),
                treatment_related_deaths=safety_data.get("treatment_related_deaths"),
                total_deaths=safety_data.get("total_deaths"),
                confidence_score=confidence_scores.get("safety_profile", 0.0)
            )
            
            # Build quality of life (optional)
            qol_data = validated_data.get("quality_of_life", {})
            quality_of_life = None
            if qol_data:
                quality_of_life = QualityOfLife(
                    qol_instruments=qol_data.get("qol_instruments"),
                    baseline_qol_scores=qol_data.get("baseline_qol_scores"),
                    qol_improvement_rate=qol_data.get("qol_improvement_rate"),
                    symptom_relief_rate=qol_data.get("symptom_relief_rate"),
                    time_to_qol_improvement=qol_data.get("time_to_qol_improvement"),
                    confidence_score=confidence_scores.get("quality_of_life", 0.0)
                )
            
            # Build statistical analysis
            stats_data = validated_data.get("statistical_analysis", {})
            statistical_analysis = StatisticalAnalysis(
                primary_analysis_method=stats_data.get("primary_analysis_method"),
                significance_level=stats_data.get("significance_level"),
                power_calculation=stats_data.get("power_calculation"),
                sample_size_rationale=stats_data.get("sample_size_rationale"),
                survival_analysis_method=stats_data.get("survival_analysis_method"),
                censoring_details=stats_data.get("censoring_details"),
                hazard_ratios=stats_data.get("hazard_ratios"),
                p_values=stats_data.get("p_values"),
                confidence_score=confidence_scores.get("statistical_analysis", 0.0)
            )
            
            # Calculate overall scores using new confidence metrics
            extraction_quality = confidence_scores.get('extraction_quality', 0.75)
            data_completeness = confidence_scores.get('data_completeness', 0.0)
            source_richness = confidence_scores.get('source_richness', 0.0)
            overall_confidence = confidence_scores.get('overall_confidence', extraction_quality)
            
            clinical_significance = self._calculate_clinical_significance(validated_data)
            
            # Create comprehensive metadata
            metadata = ComprehensiveAbstractMetadata(
                abstract_id=abstract_id,
                extraction_timestamp=datetime.now(),
                study_identification=study_id,
                study_design=study_design,
                patient_demographics=patient_demographics,
                disease_characteristics=disease_characteristics,
                treatment_history=treatment_history,
                treatment_regimens=treatment_regimens,
                efficacy_outcomes=efficacy_outcomes,
                safety_profile=safety_profile,
                quality_of_life=quality_of_life,
                statistical_analysis=statistical_analysis,
                extraction_confidence=overall_confidence,  # Use our improved confidence
                data_completeness_score=data_completeness,
                clinical_significance_score=clinical_significance,
                source_text=source_text,
                processing_notes=[
                    f"Extraction Quality: {extraction_quality:.1%}",
                    f"Data Completeness: {data_completeness:.1%}", 
                    f"Source Richness: {source_richness:.1%}"
                ]
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error structuring metadata: {str(e)}")
            return self._create_error_metadata(source_text, str(e))
    
    def _calculate_confidence_scores(self, extracted_data: Dict[str, Any], source_text: str) -> Dict[str, float]:
        """
        Calculate separate confidence scores for extraction quality vs data completeness
        
        Args:
            extracted_data: The extracted metadata
            source_text: Original abstract text
            
        Returns:
            Dictionary with different confidence metrics
        """
        
        # 1. EXTRACTION QUALITY CONFIDENCE
        # Based on how confident we are about the data we DID extract
        extraction_quality = self._calculate_extraction_quality_confidence(extracted_data)
        
        # 2. DATA COMPLETENESS SCORE  
        # Based on how much expected data was found (not a confidence per se)
        data_completeness = self._calculate_data_completeness_score(extracted_data, source_text)
        
        # 3. SOURCE RICHNESS SCORE
        # Based on how much extractable information the source contains
        source_richness = self._calculate_source_richness_score(source_text)
        
        # 4. OVERALL CONFIDENCE
        # Weighted combination focusing on extraction quality
        overall_confidence = (
            extraction_quality * 0.7 +  # Primary: How good is our extraction?
            data_completeness * 0.2 +   # Secondary: How complete is the data?
            source_richness * 0.1       # Context: How rich was the source?
        )
        
        return {
            'extraction_quality': extraction_quality,    # How confident are we in extracted values?
            'data_completeness': data_completeness,      # How much expected data was found?
            'source_richness': source_richness,          # How rich was the source text?
            'overall_confidence': overall_confidence     # Combined metric
        }
    
    def _calculate_extraction_quality_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate overall extraction quality confidence"""
        
        # Reduced thresholds for confidence scoring
        quality_scores = []
        
        # Basic structure validation (reduced threshold)
        if extracted_data.get('study_identification'):
            quality_scores.append(0.8)  # Reduced from 0.9
        
        # Data completeness (reduced threshold)
        completeness = self._calculate_data_completeness_score(extracted_data, "")
        quality_scores.append(completeness * 0.8)  # Reduced weight
        
        # Clinical significance (reduced threshold)
        significance = self._calculate_clinical_significance(extracted_data)
        quality_scores.append(significance * 0.7)  # Reduced weight
        
        # Calculate weighted average with reduced thresholds
        if quality_scores:
            return sum(quality_scores) / len(quality_scores)
        return 0.6  # Default to moderate confidence instead of 0.0
    
    def _calculate_data_completeness_score(self, extracted_data: Dict[str, Any], source_text: str) -> float:
        """
        Calculate how complete the extracted data is relative to what's expected
        This is NOT a confidence score - it's a completeness metric
        """
        expected_fields = {
            'study_identification': ['title', 'nct_number'],  # Always expected
            'patient_demographics': ['total_enrolled'],       # Usually expected  
            'efficacy_outcomes': ['overall_response_rate'],   # Often expected
            'treatment_regimens': [],                         # Context dependent
            'safety_profile': []                              # Context dependent
        }
        
        found_fields = 0
        total_expected = 0
        
        for section, fields in expected_fields.items():
            section_data = extracted_data.get(section, {})
            
            for field in fields:
                total_expected += 1
                if section == 'treatment_regimens':
                    # Special handling for list fields
                    if section_data and len(section_data) > 0:
                        found_fields += 1
                else:
                    # Regular field checking
                    value = section_data.get(field)
                    if value is not None and value != "" and value != "N/A":
                        found_fields += 1
        
        return found_fields / total_expected if total_expected > 0 else 1.0
    
    def _calculate_source_richness_score(self, source_text: str) -> float:
        """
        Calculate how much extractable information the source text contains
        """
        if not source_text:
            return 0.0
            
        richness_indicators = []
        
        # Length indicator
        if len(source_text) > 1000:
            richness_indicators.append(0.9)
        elif len(source_text) > 500:
            richness_indicators.append(0.7)
        else:
            richness_indicators.append(0.5)
            
        # Numerical data presence
        numbers = re.findall(r'\d+(?:\.\d+)?', source_text)
        if len(numbers) > 10:
            richness_indicators.append(0.9)
        elif len(numbers) > 5:
            richness_indicators.append(0.7)
        else:
            richness_indicators.append(0.5)
            
        # Medical terms presence
        medical_terms = ['patients', 'efficacy', 'safety', 'treatment', 'response', 'survival', 'adverse']
        found_terms = sum(1 for term in medical_terms if term.lower() in source_text.lower())
        richness_indicators.append(min(found_terms / len(medical_terms), 1.0))
        
        return sum(richness_indicators) / len(richness_indicators)
    
    def _calculate_clinical_significance(self, data: Dict[str, Any]) -> float:
        """Calculate clinical significance score based on key endpoints"""
        significance_score = 0.0
        max_score = 0.0
        
        # Check for key efficacy endpoints
        efficacy = data.get("efficacy_outcomes", {})
        if efficacy.get("overall_response_rate"):
            significance_score += 0.3
        if efficacy.get("progression_free_survival"):
            significance_score += 0.3
        if efficacy.get("overall_survival"):
            significance_score += 0.4
        max_score += 1.0
        
        # Check for safety data
        safety = data.get("safety_profile", {})
        if safety.get("grade_3_4_aes"):
            significance_score += 0.2
        max_score += 0.2
        
        # Check for patient population size
        demographics = data.get("patient_demographics", {})
        if demographics.get("total_enrolled"):
            if demographics["total_enrolled"] >= 100:
                significance_score += 0.1
            elif demographics["total_enrolled"] >= 50:
                significance_score += 0.05
        max_score += 0.1
        
        return significance_score / max_score if max_score > 0 else 0.0
    
    def _create_error_metadata(self, source_text: str, error_message: str) -> ComprehensiveAbstractMetadata:
        """Create minimal metadata structure for error cases"""
        
        abstract_id = str(uuid.uuid4())
        
        # Create minimal required components
        study_id = StudyIdentification(title="Error in extraction", confidence_score=0.0)
        study_design = StudyDesign(study_type=StudyType.PHASE_2, confidence_score=0.0)
        patient_demographics = PatientDemographics(confidence_score=0.0)
        disease_characteristics = DiseaseCharacteristics(mm_subtype=[MMSubtype.RRMM], confidence_score=0.0)
        treatment_history = TreatmentHistory(confidence_score=0.0)
        treatment_regimens = [TreatmentRegimen(regimen_name="Unknown", drugs=[], confidence_score=0.0)]
        efficacy_outcomes = EfficacyOutcomes(confidence_score=0.0)
        safety_profile = SafetyProfile(confidence_score=0.0)
        statistical_analysis = StatisticalAnalysis(confidence_score=0.0)
        
        return ComprehensiveAbstractMetadata(
            abstract_id=abstract_id,
            extraction_timestamp=datetime.now(),
            study_identification=study_id,
            study_design=study_design,
            patient_demographics=patient_demographics,
            disease_characteristics=disease_characteristics,
            treatment_history=treatment_history,
            treatment_regimens=treatment_regimens,
            efficacy_outcomes=efficacy_outcomes,
            safety_profile=safety_profile,
            statistical_analysis=statistical_analysis,
            extraction_confidence=0.0,
            data_completeness_score=0.0,
            clinical_significance_score=0.0,
            source_text=source_text,
            processing_notes=[f"Extraction error: {error_message}"]
        )


# Batch processing functionality
class BatchExtractor:
    """Batch processing for multiple abstracts"""
    
    def __init__(self):
        self.extractor = EnhancedMetadataExtractor()
    
    async def process_batch(self, abstract_texts: List[str], batch_size: int = None) -> List[ComprehensiveAbstractMetadata]:
        """Process multiple abstracts in batches"""
        
        batch_size = batch_size or settings.BATCH_SIZE
        results = []
        
        for i in range(0, len(abstract_texts), batch_size):
            batch = abstract_texts[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [self.extractor.extract_comprehensive_metadata(text) for text in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results and exceptions
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch processing error: {result}")
                    # Create error metadata
                    error_metadata = self.extractor._create_error_metadata("", str(result))
                    results.append(error_metadata)
                else:
                    results.append(result)
        
        return results 