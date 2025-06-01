# agents/protocol_maker.py - INTELLIGENT PROTOCOL GENERATION

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from enum import Enum
from loguru import logger
import streamlit as st
from anthropic import Anthropic

from config.settings import settings


class ProtocolType(Enum):
    """Types of analysis protocols"""
    EFFICACY_ANALYSIS = "Efficacy Analysis Protocol"
    SAFETY_ANALYSIS = "Safety Analysis Protocol"
    COMPARATIVE_ANALYSIS = "Comparative Analysis Protocol"
    META_ANALYSIS = "Meta-Analysis Protocol"
    REAL_WORLD_EVIDENCE = "Real-World Evidence Protocol"
    BIOMARKER_ANALYSIS = "Biomarker Analysis Protocol"
    HEALTH_ECONOMICS = "Health Economics Protocol"


class AnalysisComplexity(Enum):
    """Analysis complexity levels"""
    BASIC = "Basic"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class ProtocolMaker:
    """Advanced AI agent for generating analysis protocols and workflows"""
    
    def __init__(self):
        try:
            anthropic_key = st.secrets["api_keys"]["claude"]
        except:
            anthropic_key = settings.ANTHROPIC_API_KEY
        
        self.anthropic_client = Anthropic(api_key=anthropic_key)
        self.protocol_templates = self._load_protocol_templates()
    
    async def generate_analysis_protocol(self, 
                                       studies: List[Dict[str, Any]], 
                                       analysis_objective: str,
                                       user_requirements: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive analysis protocol based on studies and objectives
        
        Args:
            studies: List of study metadata and categorizations
            analysis_objective: Primary objective of the analysis
            user_requirements: Optional user-specific requirements
            
        Returns:
            Comprehensive analysis protocol
        """
        
        logger.info(f"Generating analysis protocol for {len(studies)} studies")
        
        try:
            # Phase 1: Analyze study characteristics
            study_analysis = self._analyze_study_characteristics(studies)
            
            # Phase 2: Determine optimal protocol type and complexity
            protocol_recommendation = await self._determine_protocol_type(
                study_analysis, analysis_objective, user_requirements
            )
            
            # Phase 3: Generate detailed protocol steps
            detailed_protocol = await self._generate_detailed_protocol(
                study_analysis, protocol_recommendation, analysis_objective
            )
            
            # Phase 4: Create statistical analysis plan
            statistical_plan = self._create_statistical_plan(study_analysis, protocol_recommendation)
            
            # Phase 5: Generate quality assessment framework
            quality_framework = self._create_quality_framework(study_analysis)
            
            # Phase 6: Create validation and sensitivity analysis plan
            validation_plan = self._create_validation_plan(study_analysis)
            
            # Combine all components
            comprehensive_protocol = {
                'protocol_id': f"ASCOMIND_PROTOCOL_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'generation_timestamp': datetime.now().isoformat(),
                'analysis_objective': analysis_objective,
                'study_overview': study_analysis,
                'protocol_recommendation': protocol_recommendation,
                'detailed_protocol': detailed_protocol,
                'statistical_analysis_plan': statistical_plan,
                'quality_assessment': quality_framework,
                'validation_plan': validation_plan,
                'estimated_timeline': self._estimate_timeline(protocol_recommendation),
                'resource_requirements': self._estimate_resources(protocol_recommendation),
                'deliverables': self._define_deliverables(protocol_recommendation),
                'risk_mitigation': self._identify_risks(study_analysis),
                'protocol_version': '1.0'
            }
            
            logger.info("Analysis protocol generated successfully")
            return comprehensive_protocol
            
        except Exception as e:
            logger.error(f"Error generating analysis protocol: {str(e)}")
            return self._create_fallback_protocol(analysis_objective)
    
    def _analyze_study_characteristics(self, studies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze characteristics of input studies"""
        
        characteristics = {
            'total_studies': len(studies),
            'study_types': {},
            'population_types': {},
            'treatment_categories': {},
            'geographic_distribution': {},
            'temporal_distribution': {},
            'data_quality_metrics': {
                'high_quality_count': 0,
                'medium_quality_count': 0,
                'low_quality_count': 0,
                'mean_confidence': 0.0
            },
            'study_sizes': [],
            'follow_up_durations': [],
            'primary_endpoints': {},
            'heterogeneity_indicators': {}
        }
        
        total_confidence = 0
        
        for study in studies:
            # Study types
            study_type = study.get('study_category', 'Unknown')
            characteristics['study_types'][study_type] = characteristics['study_types'].get(study_type, 0) + 1
            
            # Population analysis
            populations = study.get('population_types', {}).get('populations', [])
            for pop in populations:
                characteristics['population_types'][pop] = characteristics['population_types'].get(pop, 0) + 1
            
            # Treatment categories
            treatments = study.get('treatment_categories', {}).get('treatment_categories', [])
            for treatment in treatments:
                characteristics['treatment_categories'][treatment] = characteristics['treatment_categories'].get(treatment, 0) + 1
            
            # Quality assessment
            confidence = study.get('confidence_scores', {}).get('overall', 0.5)
            total_confidence += confidence
            
            if confidence > 0.8:
                characteristics['data_quality_metrics']['high_quality_count'] += 1
            elif confidence > 0.5:
                characteristics['data_quality_metrics']['medium_quality_count'] += 1
            else:
                characteristics['data_quality_metrics']['low_quality_count'] += 1
            
            # Study size (if available in metadata)
            if 'metadata' in study and study['metadata'].get('patient_demographics'):
                size = study['metadata']['patient_demographics'].get('total_enrolled')
                if size:
                    characteristics['study_sizes'].append(size)
        
        # Calculate averages
        if studies:
            characteristics['data_quality_metrics']['mean_confidence'] = total_confidence / len(studies)
        
        # Assess heterogeneity
        characteristics['heterogeneity_indicators'] = {
            'study_type_diversity': len(characteristics['study_types']),
            'population_diversity': len(characteristics['population_types']),
            'treatment_diversity': len(characteristics['treatment_categories']),
            'heterogeneity_score': self._calculate_heterogeneity_score(characteristics)
        }
        
        return characteristics
    
    async def _determine_protocol_type(self, 
                                     study_analysis: Dict[str, Any], 
                                     objective: str,
                                     user_requirements: Optional[Dict] = None) -> Dict[str, Any]:
        """Determine optimal protocol type and complexity using AI"""
        
        prompt = f"""You are an expert biostatistician and medical researcher. Based on the study characteristics and analysis objective, recommend the optimal analysis protocol.

STUDY CHARACTERISTICS:
{json.dumps(study_analysis, indent=2)}

ANALYSIS OBJECTIVE:
{objective}

USER REQUIREMENTS:
{json.dumps(user_requirements or {}, indent=2)}

Provide a JSON response with:
{{
    "recommended_protocol_type": "Efficacy Analysis Protocol" | "Safety Analysis Protocol" | "Comparative Analysis Protocol" | "Meta-Analysis Protocol" | "Real-World Evidence Protocol" | "Biomarker Analysis Protocol" | "Health Economics Protocol",
    "complexity_level": "Basic" | "Intermediate" | "Advanced" | "Expert",
    "primary_endpoints": ["list of primary endpoints to focus on"],
    "secondary_endpoints": ["list of secondary endpoints"],
    "statistical_methods": ["recommended statistical approaches"],
    "potential_challenges": ["identified analysis challenges"],
    "data_requirements": ["specific data requirements"],
    "confidence_score": 0.0-1.0,
    "reasoning": "detailed explanation of recommendations"
}}"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            response = json.loads(message.content[0].text)
            return response
        except:
            logger.warning("Could not parse protocol recommendation, using fallback")
            return self._create_fallback_recommendation(study_analysis, objective)
    
    async def _generate_detailed_protocol(self, 
                                        study_analysis: Dict[str, Any],
                                        protocol_recommendation: Dict[str, Any],
                                        objective: str) -> Dict[str, Any]:
        """Generate detailed step-by-step protocol"""
        
        prompt = f"""Generate a detailed, step-by-step analysis protocol for multiple myeloma research.

ANALYSIS OBJECTIVE: {objective}

PROTOCOL RECOMMENDATION:
{json.dumps(protocol_recommendation, indent=2)}

STUDY CHARACTERISTICS:
{json.dumps(study_analysis, indent=2)}

Create a comprehensive protocol with:
1. Data preparation steps
2. Quality assessment procedures
3. Statistical analysis workflow
4. Interpretation guidelines
5. Reporting standards

Format as JSON with detailed steps, rationale, and acceptance criteria for each phase."""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            response = json.loads(message.content[0].text)
            return response
        except:
            logger.warning("Could not parse detailed protocol, using template")
            return self._get_protocol_template(protocol_recommendation.get('recommended_protocol_type', 'Efficacy Analysis Protocol'))
    
    def _create_statistical_plan(self, study_analysis: Dict[str, Any], protocol_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed statistical analysis plan"""
        
        plan = {
            'primary_analysis': {
                'objective': 'Primary efficacy/safety endpoint analysis',
                'statistical_methods': protocol_recommendation.get('statistical_methods', ['Descriptive statistics']),
                'significance_level': 0.05,
                'power_calculation': 'To be determined based on effect size',
                'handling_missing_data': 'Multiple imputation if >5% missing',
                'interim_analyses': 'Not planned'
            },
            'secondary_analyses': {
                'subgroup_analyses': [
                    'High-risk vs standard-risk populations',
                    'NDMM vs RRMM populations',
                    'Age-based subgroups (elderly vs younger)',
                    'Treatment mechanism subgroups'
                ],
                'sensitivity_analyses': [
                    'Per-protocol analysis',
                    'Complete case analysis',
                    'Different imputation methods'
                ],
                'exploratory_analyses': [
                    'Biomarker correlations',
                    'Geographic variations',
                    'Temporal trends'
                ]
            },
            'heterogeneity_assessment': {
                'methods': ['I² statistic', 'Cochran Q test', 'Tau² estimation'],
                'thresholds': {
                    'low_heterogeneity': 'I² < 25%',
                    'moderate_heterogeneity': 'I² 25-75%',
                    'high_heterogeneity': 'I² > 75%'
                },
                'investigation_plan': 'Meta-regression for sources of heterogeneity'
            },
            'quality_assessment': {
                'study_quality_tools': ['Newcastle-Ottawa Scale', 'Cochrane Risk of Bias'],
                'data_quality_metrics': ['Completeness', 'Consistency', 'Plausibility'],
                'exclusion_criteria': ['Studies with <80% data completeness']
            }
        }
        
        return plan
    
    def _create_quality_framework(self, study_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create quality assessment framework"""
        
        framework = {
            'study_selection_criteria': {
                'inclusion_criteria': [
                    'Multiple myeloma studies',
                    'Adequate sample size (n>20)',
                    'Clear outcome definitions',
                    'Sufficient follow-up duration'
                ],
                'exclusion_criteria': [
                    'Preclinical studies only',
                    'Case reports (n<10)',
                    'Insufficient data for analysis'
                ]
            },
            'data_quality_assessment': {
                'completeness_thresholds': {
                    'primary_endpoints': '≥90% complete',
                    'baseline_characteristics': '≥80% complete',
                    'safety_data': '≥85% complete'
                },
                'consistency_checks': [
                    'Internal consistency validation',
                    'Cross-study consistency assessment',
                    'Temporal consistency evaluation'
                ],
                'plausibility_assessment': [
                    'Range checks for continuous variables',
                    'Logical consistency checks',
                    'Outlier detection and investigation'
                ]
            },
            'bias_assessment': {
                'selection_bias': 'Patient selection criteria assessment',
                'information_bias': 'Outcome measurement standardization',
                'confounding_bias': 'Baseline characteristic comparison',
                'publication_bias': 'Funnel plot analysis (if applicable)'
            }
        }
        
        return framework
    
    def _create_validation_plan(self, study_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create validation and sensitivity analysis plan"""
        
        plan = {
            'internal_validation': {
                'cross_validation': 'Leave-one-out cross-validation for meta-analyses',
                'bootstrap_validation': '1000 bootstrap samples for confidence intervals',
                'sensitivity_analyses': [
                    'Exclusion of low-quality studies',
                    'Alternative statistical methods',
                    'Different inclusion criteria'
                ]
            },
            'external_validation': {
                'comparison_datasets': 'Compare with external registries if available',
                'generalizability_assessment': 'Population representativeness evaluation',
                'temporal_validation': 'Compare early vs recent studies'
            },
            'robustness_testing': {
                'assumption_testing': [
                    'Normality assumptions',
                    'Proportional hazards assumptions',
                    'Independence assumptions'
                ],
                'model_diagnostics': [
                    'Residual analysis',
                    'Influence diagnostics',
                    'Goodness-of-fit testing'
                ]
            }
        }
        
        return plan
    
    def _estimate_timeline(self, protocol_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate project timeline"""
        
        complexity = protocol_recommendation.get('complexity_level', 'Intermediate')
        
        base_timeline = {
            'Basic': {'total_weeks': 4, 'analysis_weeks': 2, 'reporting_weeks': 2},
            'Intermediate': {'total_weeks': 8, 'analysis_weeks': 5, 'reporting_weeks': 3},
            'Advanced': {'total_weeks': 12, 'analysis_weeks': 8, 'reporting_weeks': 4},
            'Expert': {'total_weeks': 16, 'analysis_weeks': 10, 'reporting_weeks': 6}
        }
        
        timeline = base_timeline.get(complexity, base_timeline['Intermediate'])
        
        detailed_timeline = {
            'total_duration': f"{timeline['total_weeks']} weeks",
            'phases': {
                'data_preparation': '1-2 weeks',
                'quality_assessment': '1 week',
                'statistical_analysis': f"{timeline['analysis_weeks']} weeks",
                'interpretation_reporting': f"{timeline['reporting_weeks']} weeks",
                'review_finalization': '1 week'
            },
            'milestones': [
                'Data preparation complete',
                'Quality assessment complete',
                'Primary analysis complete',
                'Draft report complete',
                'Final report delivered'
            ]
        }
        
        return detailed_timeline
    
    def _estimate_resources(self, protocol_recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements"""
        
        complexity = protocol_recommendation.get('complexity_level', 'Intermediate')
        
        resources = {
            'personnel': {
                'biostatistician': '0.5-1.0 FTE',
                'clinical_researcher': '0.3-0.5 FTE',
                'data_manager': '0.2-0.3 FTE',
                'medical_writer': '0.2-0.3 FTE'
            },
            'software_requirements': [
                'Statistical software (R/SAS/STATA)',
                'Reference management software',
                'Data visualization tools',
                'Cloud computing resources (if large dataset)'
            ],
            'infrastructure': [
                'Secure data storage',
                'High-performance computing (for complex analyses)',
                'Collaborative platforms',
                'Version control system'
            ],
            'estimated_cost': {
                'Basic': '$10,000-$25,000',
                'Intermediate': '$25,000-$75,000',
                'Advanced': '$75,000-$150,000',
                'Expert': '$150,000-$300,000'
            }.get(complexity, '$25,000-$75,000')
        }
        
        return resources
    
    def _define_deliverables(self, protocol_recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define project deliverables"""
        
        deliverables = [
            {
                'name': 'Analysis Protocol Document',
                'description': 'Detailed statistical analysis plan and methodology',
                'format': 'PDF document',
                'timeline': 'Week 1'
            },
            {
                'name': 'Data Quality Report',
                'description': 'Assessment of study quality and data completeness',
                'format': 'PDF report with visualizations',
                'timeline': 'Week 2-3'
            },
            {
                'name': 'Primary Analysis Results',
                'description': 'Main efficacy and safety analysis findings',
                'format': 'Statistical report with tables and figures',
                'timeline': f"Week {4 if protocol_recommendation.get('complexity_level') == 'Basic' else 6}"
            },
            {
                'name': 'Interactive Dashboard',
                'description': 'Web-based visualization of key findings',
                'format': 'Interactive web application',
                'timeline': 'Final week'
            },
            {
                'name': 'Final Report',
                'description': 'Comprehensive analysis report with clinical interpretation',
                'format': 'PDF document with executive summary',
                'timeline': 'Final week'
            },
            {
                'name': 'Supplementary Materials',
                'description': 'Code, data dictionaries, and additional analyses',
                'format': 'Digital archive',
                'timeline': 'Final week'
            }
        ]
        
        return deliverables
    
    def _identify_risks(self, study_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify potential risks and mitigation strategies"""
        
        risks = []
        
        # Data quality risks
        low_quality_pct = study_analysis['data_quality_metrics']['low_quality_count'] / study_analysis['total_studies']
        if low_quality_pct > 0.3:
            risks.append({
                'risk': 'High proportion of low-quality studies',
                'impact': 'High',
                'probability': 'High',
                'mitigation': 'Implement strict quality filters and sensitivity analyses'
            })
        
        # Heterogeneity risks
        if study_analysis['heterogeneity_indicators']['heterogeneity_score'] > 0.7:
            risks.append({
                'risk': 'High study heterogeneity',
                'impact': 'Medium',
                'probability': 'Medium',
                'mitigation': 'Use random-effects models and subgroup analyses'
            })
        
        # Sample size risks
        if study_analysis['total_studies'] < 10:
            risks.append({
                'risk': 'Limited number of studies',
                'impact': 'Medium',
                'probability': 'High',
                'mitigation': 'Use conservative statistical methods and wider confidence intervals'
            })
        
        return risks
    
    def _calculate_heterogeneity_score(self, characteristics: Dict[str, Any]) -> float:
        """Calculate overall heterogeneity score"""
        
        # Calculate diversity metrics directly from characteristics data
        study_type_diversity = len(characteristics['study_types']) / 6  # Max 6 study types
        population_diversity = len(characteristics['population_types']) / 9  # Max 9 population types
        treatment_diversity = len(characteristics['treatment_categories']) / 11  # Max 11 treatment categories
        
        diversity_metrics = [study_type_diversity, population_diversity, treatment_diversity]
        
        return sum(diversity_metrics) / len(diversity_metrics)
    
    def _load_protocol_templates(self) -> Dict[str, Dict]:
        """Load predefined protocol templates"""
        
        templates = {
            'Efficacy Analysis Protocol': {
                'primary_focus': 'Treatment effectiveness outcomes',
                'key_endpoints': ['Overall Response Rate', 'Progression-Free Survival', 'Overall Survival'],
                'statistical_methods': ['Descriptive statistics', 'Meta-analysis', 'Survival analysis']
            },
            'Safety Analysis Protocol': {
                'primary_focus': 'Treatment safety and tolerability',
                'key_endpoints': ['Grade 3-4 AEs', 'Serious AEs', 'Discontinuation rates'],
                'statistical_methods': ['Descriptive statistics', 'Risk ratios', 'Meta-analysis']
            },
            'Comparative Analysis Protocol': {
                'primary_focus': 'Head-to-head treatment comparisons',
                'key_endpoints': ['Comparative effectiveness', 'Safety profiles', 'Quality of life'],
                'statistical_methods': ['Network meta-analysis', 'Indirect comparisons', 'MAIC']
            }
        }
        
        return templates
    
    def _get_protocol_template(self, protocol_type: str) -> Dict[str, Any]:
        """Get template for specific protocol type"""
        
        return self.protocol_templates.get(protocol_type, self.protocol_templates['Efficacy Analysis Protocol'])
    
    def _create_fallback_recommendation(self, study_analysis: Dict[str, Any], objective: str) -> Dict[str, Any]:
        """Create fallback recommendation when AI fails"""
        
        return {
            'recommended_protocol_type': 'Efficacy Analysis Protocol',
            'complexity_level': 'Intermediate',
            'primary_endpoints': ['Overall Response Rate', 'Progression-Free Survival'],
            'secondary_endpoints': ['Safety outcomes', 'Quality of life'],
            'statistical_methods': ['Descriptive statistics', 'Meta-analysis'],
            'potential_challenges': ['Study heterogeneity', 'Data quality variations'],
            'data_requirements': ['Primary efficacy outcomes', 'Safety data'],
            'confidence_score': 0.5,
            'reasoning': 'Fallback recommendation due to AI processing error'
        }
    
    def _create_fallback_protocol(self, objective: str) -> Dict[str, Any]:
        """Create fallback protocol when generation fails"""
        
        return {
            'protocol_id': f"FALLBACK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generation_timestamp': datetime.now().isoformat(),
            'analysis_objective': objective,
            'protocol_type': 'Basic Efficacy Analysis',
            'error_note': 'Fallback protocol generated due to processing error',
            'basic_steps': [
                'Data collection and validation',
                'Descriptive statistical analysis',
                'Primary endpoint analysis',
                'Safety assessment',
                'Report generation'
            ]
        }


# Export main class
__all__ = ['ProtocolMaker', 'ProtocolType', 'AnalysisComplexity'] 