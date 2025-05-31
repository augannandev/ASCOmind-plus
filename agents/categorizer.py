# agents/categorizer.py - INTELLIGENT STUDY CATEGORIZATION

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import re
from loguru import logger
import streamlit as st
from anthropic import Anthropic

from config.settings import settings


class StudyCategory(Enum):
    """Study category classifications"""
    CLINICAL_TRIAL = "Clinical Trial"
    REAL_WORLD_STUDY = "Real-World Study"
    META_ANALYSIS = "Meta-Analysis"
    CASE_SERIES = "Case Series"
    REVIEW = "Review"
    PRECLINICAL = "Preclinical"


class PopulationType(Enum):
    """Patient population types"""
    NEWLY_DIAGNOSED = "Newly Diagnosed MM (NDMM)"
    RELAPSED_REFRACTORY = "Relapsed/Refractory MM (RRMM)"
    HIGH_RISK = "High-Risk Population"
    ELDERLY = "Elderly Population"
    TRANSPLANT_ELIGIBLE = "Transplant-Eligible"
    TRANSPLANT_INELIGIBLE = "Transplant-Ineligible"
    EXTRAMEDULLARY = "Extramedullary Disease"
    RENAL_IMPAIRMENT = "Renal Impairment"
    FRAIL = "Frail Population"


class TreatmentCategory(Enum):
    """Treatment mechanism categories"""
    IMMUNOMODULATORY = "Immunomodulatory (IMiDs)"
    PROTEASOME_INHIBITOR = "Proteasome Inhibitor"
    ANTI_CD38 = "Anti-CD38 Monoclonal Antibody"
    ADC = "Antibody-Drug Conjugate"
    CAR_T = "CAR-T Cell Therapy"
    BISPECIFIC = "Bispecific Antibody"
    BCL2_INHIBITOR = "BCL-2 Inhibitor"
    HDAC_INHIBITOR = "HDAC Inhibitor"
    SINE = "Selective Inhibitor of Nuclear Export"
    COMBINATION = "Combination Therapy"
    CONVENTIONAL = "Conventional Chemotherapy"


class SmartCategorizer:
    """Advanced AI-powered study categorization agent"""
    
    def __init__(self):
        try:
            anthropic_key = st.secrets["api_keys"]["claude"]
        except:
            anthropic_key = settings.ANTHROPIC_API_KEY
        
        self.anthropic_client = Anthropic(api_key=anthropic_key)
        self.classification_prompt = self._build_classification_prompt()
    
    async def categorize_study(self, abstract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Comprehensively categorize a study across multiple dimensions
        
        Args:
            abstract_text: Full abstract text
            metadata: Optional extracted metadata for context
            
        Returns:
            Dictionary with comprehensive categorization
        """
        
        logger.info("Starting intelligent study categorization")
        
        try:
            # Phase 1: Rule-based quick classification
            quick_category = self._quick_classification(abstract_text)
            
            # Phase 2: AI-powered detailed classification
            ai_classification = await self._ai_classification(abstract_text, metadata)
            
            # Phase 3: Population analysis
            population_analysis = self._analyze_population(abstract_text, metadata)
            
            # Phase 4: Treatment categorization
            treatment_analysis = self._categorize_treatments(abstract_text, metadata)
            
            # Phase 5: Risk stratification
            risk_analysis = self._analyze_risk_factors(abstract_text, metadata)
            
            # Combine all analyses
            comprehensive_categorization = {
                'study_category': ai_classification.get('study_category', quick_category),
                'population_types': population_analysis,
                'treatment_categories': treatment_analysis,
                'risk_stratification': risk_analysis,
                'clinical_setting': ai_classification.get('clinical_setting'),
                'therapeutic_intent': ai_classification.get('therapeutic_intent'),
                'study_design_complexity': ai_classification.get('complexity_score', 0),
                'novelty_score': ai_classification.get('novelty_score', 0),
                'confidence_scores': {
                    'overall': ai_classification.get('confidence', 0.8),
                    'study_category': ai_classification.get('category_confidence', 0.8),
                    'population': population_analysis.get('confidence', 0.8),
                    'treatment': treatment_analysis.get('confidence', 0.8)
                },
                'classification_notes': ai_classification.get('notes', [])
            }
            
            logger.info("Study categorization completed successfully")
            return comprehensive_categorization
            
        except Exception as e:
            logger.error(f"Error in study categorization: {str(e)}")
            return self._create_fallback_categorization()
    
    def _quick_classification(self, abstract_text: str) -> StudyCategory:
        """Quick rule-based classification for common patterns"""
        
        text_lower = abstract_text.lower()
        
        # Clinical trial indicators
        if any(indicator in text_lower for indicator in [
            'randomized', 'phase 1', 'phase 2', 'phase 3', 'phase i', 'phase ii', 'phase iii',
            'clinical trial', 'nct', 'controlled trial', 'double-blind', 'placebo'
        ]):
            return StudyCategory.CLINICAL_TRIAL
        
        # Real-world study indicators  
        elif any(indicator in text_lower for indicator in [
            'real-world', 'retrospective', 'cohort', 'registry', 'database analysis',
            'medical records', 'claims data', 'observational'
        ]):
            return StudyCategory.REAL_WORLD_STUDY
        
        # Meta-analysis indicators
        elif any(indicator in text_lower for indicator in [
            'meta-analysis', 'systematic review', 'pooled analysis'
        ]):
            return StudyCategory.META_ANALYSIS
        
        # Case series indicators
        elif any(indicator in text_lower for indicator in [
            'case series', 'case report', 'single center'
        ]):
            return StudyCategory.CASE_SERIES
        
        # Preclinical indicators
        elif any(indicator in text_lower for indicator in [
            'preclinical', 'in vitro', 'cell line', 'xenograft', 'mouse model'
        ]):
            return StudyCategory.PRECLINICAL
        
        # Default to clinical trial if unsure
        return StudyCategory.CLINICAL_TRIAL
    
    async def _ai_classification(self, abstract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """AI-powered detailed classification"""
        
        context = ""
        if metadata:
            context = f"\nAdditional Context:\n{str(metadata)[:500]}"
        
        message = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": f"{self.classification_prompt}\n\nABSTRACT:\n{abstract_text}{context}"
                }
            ]
        )
        
        response_text = message.content[0].text
        
        try:
            import json
            classification = json.loads(response_text)
            return classification
        except:
            logger.warning("Could not parse AI classification, using fallback")
            return {'study_category': 'Clinical Trial', 'confidence': 0.5}
    
    def _analyze_population(self, abstract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze patient population characteristics"""
        
        text_lower = abstract_text.lower()
        detected_populations = []
        confidence_scores = {}
        
        # NDMM vs RRMM detection
        if any(term in text_lower for term in ['newly diagnosed', 'treatment-naive', 'first-line', 'ndmm']):
            detected_populations.append(PopulationType.NEWLY_DIAGNOSED)
            confidence_scores[PopulationType.NEWLY_DIAGNOSED.value] = 0.9
        
        if any(term in text_lower for term in ['relapsed', 'refractory', 'rrmm', 'second-line', 'third-line']):
            detected_populations.append(PopulationType.RELAPSED_REFRACTORY)
            confidence_scores[PopulationType.RELAPSED_REFRACTORY.value] = 0.9
        
        # High-risk detection
        if any(term in text_lower for term in ['high-risk', 'del(17p)', 't(4;14)', 't(14;16)', 'amp(1q)']):
            detected_populations.append(PopulationType.HIGH_RISK)
            confidence_scores[PopulationType.HIGH_RISK.value] = 0.85
        
        # Elderly detection
        if any(term in text_lower for term in ['elderly', 'geriatric', 'age ≥75', 'age >70', 'older patients']):
            detected_populations.append(PopulationType.ELDERLY)
            confidence_scores[PopulationType.ELDERLY.value] = 0.8
        
        # Transplant eligibility
        if any(term in text_lower for term in ['transplant-eligible', 'transplant eligible', 'asct eligible']):
            detected_populations.append(PopulationType.TRANSPLANT_ELIGIBLE)
            confidence_scores[PopulationType.TRANSPLANT_ELIGIBLE.value] = 0.85
        
        if any(term in text_lower for term in ['transplant-ineligible', 'transplant ineligible', 'not eligible']):
            detected_populations.append(PopulationType.TRANSPLANT_INELIGIBLE)
            confidence_scores[PopulationType.TRANSPLANT_INELIGIBLE.value] = 0.85
        
        # Extramedullary disease
        if any(term in text_lower for term in ['extramedullary', 'plasmacytoma', 'soft tissue']):
            detected_populations.append(PopulationType.EXTRAMEDULLARY)
            confidence_scores[PopulationType.EXTRAMEDULLARY.value] = 0.9
        
        return {
            'populations': [pop.value for pop in detected_populations],
            'confidence_scores': confidence_scores,
            'confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
        }
    
    def _categorize_treatments(self, abstract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Categorize treatment mechanisms and approaches"""
        
        text_lower = abstract_text.lower()
        detected_treatments = []
        confidence_scores = {}
        
        # Drug class detection patterns
        treatment_patterns = {
            TreatmentCategory.IMMUNOMODULATORY: ['lenalidomide', 'pomalidomide', 'thalidomide', 'iberdomide', 'mezigdomide', 'imid'],
            TreatmentCategory.PROTEASOME_INHIBITOR: ['bortezomib', 'carfilzomib', 'ixazomib', 'proteasome'],
            TreatmentCategory.ANTI_CD38: ['daratumumab', 'isatuximab', 'cd38', 'anti-cd38'],
            TreatmentCategory.ADC: ['belantamab', 'mafodotin', 'adc', 'antibody-drug conjugate'],
            TreatmentCategory.CAR_T: ['car-t', 'cart', 'chimeric antigen receptor', 'idecabtagene', 'ciltacabtagene'],
            TreatmentCategory.BISPECIFIC: ['bispecific', 'teclistamab', 'talquetamab', 'elranatamab'],
            TreatmentCategory.BCL2_INHIBITOR: ['venetoclax', 'bcl-2', 'bcl2'],
            TreatmentCategory.HDAC_INHIBITOR: ['panobinostat', 'hdac'],
            TreatmentCategory.SINE: ['selinexor', 'sine', 'nuclear export']
        }
        
        for category, patterns in treatment_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                detected_treatments.append(category)
                confidence_scores[category.value] = 0.85
        
        # Check for combinations
        if len(detected_treatments) > 1:
            detected_treatments.append(TreatmentCategory.COMBINATION)
            confidence_scores[TreatmentCategory.COMBINATION.value] = 0.9
        
        return {
            'treatment_categories': [cat.value for cat in detected_treatments],
            'confidence_scores': confidence_scores,
            'confidence': sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5,
            'is_combination': len(detected_treatments) > 1,
            'mechanism_count': len(detected_treatments)
        }
    
    def _analyze_risk_factors(self, abstract_text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze risk stratification and patient characteristics"""
        
        text_lower = abstract_text.lower()
        risk_factors = []
        
        # Cytogenetic risk factors
        if any(factor in text_lower for factor in ['del(17p)', 'del 17p', 't(4;14)', 't(14;16)', 'amp(1q)']):
            risk_factors.append('High-risk cytogenetics')
        
        # Clinical risk factors
        if any(factor in text_lower for factor in ['extramedullary', 'plasma cell leukemia', 'renal impairment']):
            risk_factors.append('High-risk clinical features')
        
        # Treatment resistance
        if any(factor in text_lower for factor in ['refractory', 'resistance', 'lenalidomide-refractory']):
            risk_factors.append('Treatment-resistant disease')
        
        return {
            'risk_factors': risk_factors,
            'risk_level': 'High' if risk_factors else 'Standard',
            'confidence': 0.8 if risk_factors else 0.6
        }
    
    def _build_classification_prompt(self) -> str:
        """Build comprehensive classification prompt"""
        
        return """You are an expert medical AI agent specializing in multiple myeloma research classification.

Analyze the provided abstract and classify it across multiple dimensions. Return a JSON response with:

{
    "study_category": "Clinical Trial" | "Real-World Study" | "Meta-Analysis" | "Case Series" | "Review" | "Preclinical",
    "clinical_setting": "First-line" | "Second-line" | "Third-line+" | "Mixed" | "Maintenance",
    "therapeutic_intent": "Curative" | "Palliative" | "Supportive" | "Preventive",
    "complexity_score": 0.0-1.0,
    "novelty_score": 0.0-1.0,
    "confidence": 0.0-1.0,
    "category_confidence": 0.0-1.0,
    "notes": ["brief classification reasoning"]
}

Consider:
- Study design (randomized, controlled, observational)
- Patient population (NDMM, RRMM, high-risk)
- Treatment approach (novel vs standard)
- Endpoints and outcomes
- Clinical significance"""
    
    def _create_fallback_categorization(self) -> Dict[str, Any]:
        """Create fallback categorization when AI fails"""
        
        return {
            'study_category': StudyCategory.CLINICAL_TRIAL.value,
            'population_types': {'populations': [], 'confidence': 0.3},
            'treatment_categories': {'treatment_categories': [], 'confidence': 0.3},
            'risk_stratification': {'risk_factors': [], 'confidence': 0.3},
            'clinical_setting': 'Unknown',
            'therapeutic_intent': 'Unknown',
            'study_design_complexity': 0.5,
            'novelty_score': 0.5,
            'confidence_scores': {'overall': 0.3},
            'classification_notes': ['Fallback classification due to processing error']
        }


class BatchCategorizer:
    """Batch categorization for multiple studies"""
    
    def __init__(self):
        self.categorizer = SmartCategorizer()
    
    async def categorize_batch(self, studies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize multiple studies in batch
        
        Args:
            studies: List of studies with 'abstract_text' and optional 'metadata'
            
        Returns:
            List of categorization results
        """
        
        tasks = []
        for study in studies:
            task = self.categorizer.categorize_study(
                study['abstract_text'], 
                study.get('metadata')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Categorization failed for study {i}: {result}")
                processed_results.append(self.categorizer._create_fallback_categorization())
            else:
                processed_results.append(result)
        
        return processed_results
    
    def generate_categorization_summary(self, categorizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from batch categorization"""
        
        summary = {
            'total_studies': len(categorizations),
            'study_categories': {},
            'population_distribution': {},
            'treatment_distribution': {},
            'risk_distribution': {},
            'confidence_metrics': {
                'mean_confidence': 0.0,
                'high_confidence_count': 0
            }
        }
        
        # Count categories
        for cat in categorizations:
            # Study categories
            study_cat = cat.get('study_category', 'Unknown')
            summary['study_categories'][study_cat] = summary['study_categories'].get(study_cat, 0) + 1
            
            # Population types
            pops = cat.get('population_types', {}).get('populations', [])
            for pop in pops:
                summary['population_distribution'][pop] = summary['population_distribution'].get(pop, 0) + 1
            
            # Treatment categories
            treatments = cat.get('treatment_categories', {}).get('treatment_categories', [])
            for treatment in treatments:
                summary['treatment_distribution'][treatment] = summary['treatment_distribution'].get(treatment, 0) + 1
            
            # Confidence metrics
            overall_conf = cat.get('confidence_scores', {}).get('overall', 0)
            summary['confidence_metrics']['mean_confidence'] += overall_conf
            if overall_conf > 0.8:
                summary['confidence_metrics']['high_confidence_count'] += 1
        
        # Calculate averages
        if categorizations:
            summary['confidence_metrics']['mean_confidence'] /= len(categorizations)
        
        return summary


# Export main classes
__all__ = ['SmartCategorizer', 'BatchCategorizer', 'StudyCategory', 'PopulationType', 'TreatmentCategory'] 