# agents/visualizer.py - REWRITTEN INTERACTIVE VISUALIZATIONS

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import math
import logging
from typing import Dict, List, Any, Optional, Union
from collections import Counter, defaultdict
import streamlit as st

# Import your metadata models
from models.abstract_metadata import (
    ComprehensiveAbstractMetadata, StudyType, MMSubtype
)

class AdvancedVisualizer:
    """Create interactive, publication-quality visualizations from extracted metadata"""
    
    def __init__(self, db_client=None):
        self.db = db_client
        self.color_palette = self._define_medical_color_palette()
        self.theme = self._get_safe_theme()
        self.logger = logging.getLogger(__name__)
        
    def _get_safe_theme(self) -> str:
        """Safely get chart theme with fallback"""
        try:
            from config.settings import settings
            return getattr(settings, 'CHART_THEME', 'plotly_white')
        except (ImportError, AttributeError):
            return 'plotly_white'
    
    def _define_medical_color_palette(self) -> Dict[str, str]:
        """Define comprehensive medical-specific color palette"""
        return {
            # Primary colors
            'primary': '#667eea',
            'secondary': '#764ba2',
            'success': '#43e97b',
            'warning': '#f093fb',
            'danger': '#f5576c',
            'info': '#4facfe',
            
            # Clinical colors
            'efficacy': '#00f2fe',
            'safety': '#38f9d7',
            'high_risk': '#ff6b6b',
            'standard_risk': '#4ecdc4',
            'ultra_high_risk': '#8b0000',
            
            # MM subtypes
            'ndmm': '#3498db',
            'rrmm': '#e74c3c',
            'smoldering': '#f39c12',
            'amyloidosis': '#9b59b6',
            'pcl': '#e67e22',
            
            # Study phases
            'phase1': '#9b59b6',
            'phase2': '#3498db',
            'phase3': '#2ecc71',
            'phase4': '#e67e22',
            'real_world': '#95a5a6',
            
            # Treatment classes
            'imid': '#3498db',
            'pi': '#e74c3c',
            'anti_cd38': '#f39c12',
            'car_t': '#9b59b6',
            'bispecific': '#1abc9c',
            'adc': '#e67e22',
            
            # Age groups
            'young': '#2ecc71',
            'elderly': '#f39c12',
            'very_elderly': '#e74c3c',
            
            # Default fallback
            'default': '#95a5a6',
            'background': '#f8f9fa'
        }
    
    def _get_color(self, key: str) -> str:
        """Safely get color with fallback"""
        return self.color_palette.get(key, self.color_palette['default'])
    
    def _create_error_figure(self, title: str, error_message: str) -> go.Figure:
        """Create error figure with debugging info"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"⚠️ Error in {title}<br><br>Details: {error_message}<br><br>Check data structure and logs",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=self._get_color('danger')),
            bgcolor="rgba(255, 0, 0, 0.1)",
            bordercolor=self._get_color('danger'),
            borderwidth=2
        )
        
        fig.update_layout(
            title=f"Error: {title}",
            template=self.theme,
            height=400
        )
        
        return fig
    
    def _create_empty_figure(self, title: str, message: str = None) -> go.Figure:
        """Create empty figure with helpful message"""
        default_message = (
            "📊 No data available for this visualization<br><br>"
            "Possible reasons:<br>"
            "• Data not extracted from abstracts<br>"
            "• Insufficient studies in dataset<br>"
            "• Filters applied removed all data"
        )
        
        fig = go.Figure()
        
        fig.add_annotation(
            text=message or default_message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=self._get_color('default')),
            bgcolor=self._get_color('background'),
            bordercolor=self._get_color('default'),
            borderwidth=1
        )
        
        fig.update_layout(
            title=title,
            template=self.theme,
            height=400
        )
        
        return fig
    
    def create_comprehensive_dashboard(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> Dict[str, go.Figure]:
        """Create comprehensive visualization suite from metadata list"""
        
        if not metadata_list:
            empty_fig = self._create_empty_figure("No Studies Available", "No metadata provided for visualization")
            return {key: empty_fig for key in [
                'study_overview', 'mm_subtype_distribution', 'phase_distribution',
                'treatment_landscape', 'efficacy_analysis', 'safety_analysis',
                'patient_demographics', 'temporal_trends', 'competitive_analysis'
            ]}
        
        self.logger.info(f"Creating dashboard for {len(metadata_list)} studies")
        
        visualizations = {}
        
        # Study Overview Section
        try:
            visualizations['study_overview'] = self._create_study_overview_dashboard(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating study overview: {e}")
            visualizations['study_overview'] = self._create_error_figure("Study Overview", str(e))
        
        try:
            visualizations['mm_subtype_distribution'] = self._create_mm_subtype_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating MM subtype chart: {e}")
            visualizations['mm_subtype_distribution'] = self._create_error_figure("MM Subtype Distribution", str(e))
        
        try:
            visualizations['phase_distribution'] = self._create_phase_distribution_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating phase distribution: {e}")
            visualizations['phase_distribution'] = self._create_error_figure("Phase Distribution", str(e))
        
        # Treatment Analysis Section
        try:
            visualizations['treatment_landscape'] = self._create_treatment_landscape_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating treatment landscape: {e}")
            visualizations['treatment_landscape'] = self._create_error_figure("Treatment Landscape", str(e))
        
        try:
            visualizations['novel_agents_adoption'] = self._create_novel_agents_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating novel agents chart: {e}")
            visualizations['novel_agents_adoption'] = self._create_error_figure("Novel Agents Adoption", str(e))
        
        # Efficacy Analysis Section
        try:
            visualizations['efficacy_analysis'] = self._create_efficacy_analysis_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating efficacy analysis: {e}")
            visualizations['efficacy_analysis'] = self._create_error_figure("Efficacy Analysis", str(e))
        
        try:
            visualizations['response_rates_by_line'] = self._create_response_rates_by_line_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating response rates chart: {e}")
            visualizations['response_rates_by_line'] = self._create_error_figure("Response Rates by Line", str(e))
        
        # Safety Analysis Section
        try:
            visualizations['safety_analysis'] = self._create_safety_analysis_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating safety analysis: {e}")
            visualizations['safety_analysis'] = self._create_error_figure("Safety Analysis", str(e))
        
        # Patient Demographics Section
        try:
            visualizations['patient_demographics'] = self._create_patient_demographics_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating patient demographics: {e}")
            visualizations['patient_demographics'] = self._create_error_figure("Patient Demographics", str(e))
        
        # Advanced Analytics
        try:
            visualizations['efficacy_safety_bubble'] = self._create_efficacy_safety_bubble_chart(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating efficacy-safety bubble: {e}")
            visualizations['efficacy_safety_bubble'] = self._create_error_figure("Efficacy-Safety Analysis", str(e))
        
        try:
            visualizations['study_size_distribution'] = self._create_study_size_distribution(metadata_list)
        except Exception as e:
            self.logger.error(f"Error creating study size distribution: {e}")
            visualizations['study_size_distribution'] = self._create_error_figure("Study Size Distribution", str(e))
        
        self.logger.info(f"Dashboard created with {len(visualizations)} visualizations")
        return visualizations
    
    def _create_study_overview_dashboard(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create comprehensive study overview with key metrics"""
        
        # Calculate key metrics
        total_studies = len(metadata_list)
        total_patients = sum([
            m.patient_demographics.total_enrolled or 0 
            for m in metadata_list
        ])
        
        # Extract study types
        study_types = [m.study_design.study_type.value for m in metadata_list if m.study_design.study_type]
        study_type_counts = Counter(study_types)
        
        # Extract MM subtypes (flatten nested lists)
        mm_subtypes = []
        for m in metadata_list:
            if m.disease_characteristics.mm_subtype:
                for subtype in m.disease_characteristics.mm_subtype:
                    mm_subtypes.append(subtype.value)
        mm_subtype_counts = Counter(mm_subtypes)
        
        # Create subplots - simplified to just 2 charts
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                'Study Phase Distribution', 
                'MM Subtype Distribution'
            ),
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Study phase pie chart
        if study_type_counts:
            phases = list(study_type_counts.keys())
            counts = list(study_type_counts.values())
            colors = [self._get_color(f'phase{i+1}') for i in range(len(phases))]
            
            fig.add_trace(
                go.Pie(
                    labels=phases,
                    values=counts,
                    name="Study Phases",
                    marker_colors=colors,
                    textinfo='label+percent',
                    hovertemplate="<b>%{label}</b><br>Studies: %{value}<br>Percentage: %{percent}<extra></extra>"
                ),
                row=1, col=1
            )
        
        # MM subtype bar chart
        if mm_subtype_counts:
            subtypes = list(mm_subtype_counts.keys())
            subtype_counts = list(mm_subtype_counts.values())
            colors = [self._get_color(subtype.lower().replace(' ', '_')) for subtype in subtypes]
            
            fig.add_trace(
                go.Bar(
                    x=subtypes,
                    y=subtype_counts,
                    name="MM Subtypes",
                    marker_color=colors,
                    text=subtype_counts,
                    textposition='auto',
                    hovertemplate="<b>%{x}</b><br>Studies: %{y}<extra></extra>"
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title=f"📊 Study Overview Dashboard - {total_studies} Studies, {total_patients:,} Patients",
            height=500,
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def _create_mm_subtype_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create detailed MM subtype distribution"""
        
        # Extract MM subtypes
        mm_subtypes = []
        for m in metadata_list:
            if m.disease_characteristics.mm_subtype:
                for subtype in m.disease_characteristics.mm_subtype:
                    mm_subtypes.append(subtype.value)
        
        if not mm_subtypes:
            return self._create_empty_figure("MM Subtype Distribution", "No MM subtype data available")
        
        subtype_counts = Counter(mm_subtypes)
        total = sum(subtype_counts.values())
        
        # Create enhanced pie chart
        labels = list(subtype_counts.keys())
        values = list(subtype_counts.values())
        percentages = [v/total*100 for v in values]
        
        # Map subtypes to colors
        colors = []
        for label in labels:
            if 'RRMM' in label or 'Relapsed' in label:
                colors.append(self._get_color('rrmm'))
            elif 'Newly Diagnosed' in label or 'NDMM' in label:
                colors.append(self._get_color('ndmm'))
            elif 'Smoldering' in label:
                colors.append(self._get_color('smoldering'))
            elif 'Amyloidosis' in label:
                colors.append(self._get_color('amyloidosis'))
            else:
                colors.append(self._get_color('default'))
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.3,
            marker=dict(colors=colors, line=dict(color='#FFFFFF', width=2)),
            textinfo='label+percent',
            textposition='auto',
            hovertemplate="<b>%{label}</b><br>Studies: %{value}<br>Percentage: %{percent}<extra></extra>"
        )])
        
        # Add center annotation
        fig.add_annotation(
            text=f"Total<br>{total} Studies",
            x=0.5, y=0.5,
            font=dict(size=20, color=self._get_color('primary')),
            showarrow=False
        )
        
        fig.update_layout(
            title="🎯 Multiple Myeloma Subtype Distribution",
            template=self.theme,
            height=500,
            annotations=[dict(text=f"Total Studies: {total}", x=0.5, y=0.5, showarrow=False)]
        )
        
        return fig
    
    def _create_phase_distribution_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create study phase distribution with detailed breakdown"""
        
        # Extract study phases
        study_types = [m.study_design.study_type.value for m in metadata_list if m.study_design.study_type]
        
        if not study_types:
            return self._create_empty_figure("Phase Distribution", "No study phase data available")
        
        phase_counts = Counter(study_types)
        total_studies = sum(phase_counts.values())
        
        # Sort phases logically
        phase_order = ['Phase 1', 'Phase 1/2', 'Phase 2', 'Phase 3', 'Phase 4', 'Real World Study']
        sorted_phases = []
        sorted_counts = []
        sorted_colors = []
        
        for phase in phase_order:
            if phase in phase_counts:
                sorted_phases.append(phase)
                sorted_counts.append(phase_counts[phase])
                sorted_colors.append(self._get_color(f'phase{phase.split()[-1].replace("/", "")}'.lower()))
        
        # Add any remaining phases not in standard order
        for phase, count in phase_counts.items():
            if phase not in phase_order:
                sorted_phases.append(phase)
                sorted_counts.append(count)
                sorted_colors.append(self._get_color('default'))
        
        # Create bar chart with percentages
        percentages = [count/total_studies*100 for count in sorted_counts]
        
        fig = go.Figure(data=[
            go.Bar(
                x=sorted_phases,
                y=sorted_counts,
                text=[f"{count}<br>({pct:.1f}%)" for count, pct in zip(sorted_counts, percentages)],
                textposition='auto',
                marker_color=sorted_colors,
                hovertemplate="<b>%{x}</b><br>Studies: %{y}<br>Percentage: %{text}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title=f"📈 Clinical Trial Phase Distribution (n={total_studies})",
            xaxis_title="Study Phase",
            yaxis_title="Number of Studies",
            template=self.theme,
            height=500,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def _create_treatment_landscape_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create treatment regimen landscape analysis"""
        
        # Extract treatment regimens
        all_regimens = []
        for m in metadata_list:
            for regimen in m.treatment_regimens:
                if regimen.regimen_name and regimen.regimen_name != "Unknown":
                    all_regimens.append(regimen.regimen_name)
        
        if not all_regimens:
            return self._create_empty_figure("Treatment Landscape", "No treatment regimen data available")
        
        regimen_counts = Counter(all_regimens)
        
        # Get top 15 most common regimens
        top_regimens = dict(regimen_counts.most_common(15))
        
        regimens = list(top_regimens.keys())
        counts = list(top_regimens.values())
        
        # Create horizontal bar chart for better readability
        fig = go.Figure(data=[
            go.Bar(
                y=regimens,
                x=counts,
                orientation='h',
                text=counts,
                textposition='auto',
                marker_color=self._get_color('primary'),
                hovertemplate="<b>%{y}</b><br>Studies: %{x}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title=f"💊 Treatment Regimen Landscape (Top 15)",
            xaxis_title="Number of Studies",
            yaxis_title="Treatment Regimens",
            template=self.theme,
            height=max(500, len(regimens) * 25),
            margin=dict(l=200)  # More space for long regimen names
        )
        
        return fig
    
    def _create_efficacy_analysis_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create comprehensive efficacy analysis"""
        
        # Extract efficacy data
        efficacy_data = []
        for m in metadata_list:
            if m.efficacy_outcomes.overall_response_rate:
                orr_data = m.efficacy_outcomes.overall_response_rate
                orr_value = None
                
                if isinstance(orr_data, dict):
                    orr_value = orr_data.get('value') or orr_data.get('rate')
                elif isinstance(orr_data, (int, float)):
                    orr_value = orr_data
                
                if orr_value and 0 <= orr_value <= 100:
                    # Get MM subtype for this study
                    mm_subtype = "Unknown"
                    if m.disease_characteristics.mm_subtype:
                        mm_subtype = m.disease_characteristics.mm_subtype[0].value
                    
                    # Get line of therapy
                    line_of_therapy = m.treatment_history.line_of_therapy or "Unknown"
                    
                    # Get study size
                    study_size = m.patient_demographics.total_enrolled or 0
                    
                    efficacy_data.append({
                        'orr': orr_value,
                        'mm_subtype': mm_subtype,
                        'line_of_therapy': line_of_therapy,
                        'study_size': study_size,
                        'study_title': m.study_identification.title[:50] + "..." if len(m.study_identification.title) > 50 else m.study_identification.title
                    })
        
        if not efficacy_data:
            return self._create_empty_figure("Efficacy Analysis", "No efficacy data available")
        
        df = pd.DataFrame(efficacy_data)
        
        # Create bubble chart: ORR by MM subtype, sized by study size
        fig = px.scatter(
            df,
            x='mm_subtype',
            y='orr',
            size='study_size',
            color='line_of_therapy',
            hover_data=['study_title'],
            title="🎯 Efficacy Analysis: ORR by MM Subtype",
            labels={
                'orr': 'Overall Response Rate (%)',
                'mm_subtype': 'MM Subtype',
                'line_of_therapy': 'Line of Therapy',
                'study_size': 'Study Size'
            }
        )
        
        fig.update_layout(
            template=self.theme,
            height=600,
            xaxis_tickangle=-45
        )
        
        # Add median lines for each subtype
        for subtype in df['mm_subtype'].unique():
            subtype_data = df[df['mm_subtype'] == subtype]
            median_orr = subtype_data['orr'].median()
            
            fig.add_hline(
                y=median_orr,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Median: {median_orr:.1f}%",
                annotation_position="top right"
            )
        
        return fig
    
    def _create_safety_analysis_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create safety profile analysis"""
        
        # Extract safety data
        safety_data = []
        for m in metadata_list:
            if m.safety_profile.grade_3_4_aes:
                ae_data = m.safety_profile.grade_3_4_aes
                
                # Handle different data structures
                total_ae_rate = 0
                if isinstance(ae_data, list):
                    # List of AE events with percentages
                    for ae in ae_data:
                        if isinstance(ae, dict) and 'percentage' in ae:
                            total_ae_rate += ae['percentage']
                elif isinstance(ae_data, dict):
                    # Dictionary with overall rate
                    total_ae_rate = ae_data.get('total_rate', 0)
                elif isinstance(ae_data, (int, float)):
                    total_ae_rate = ae_data
                
                if 0 <= total_ae_rate <= 100:
                    # Get treatment info
                    treatment_name = "Unknown"
                    if m.treatment_regimens:
                        treatment_name = m.treatment_regimens[0].regimen_name or "Unknown"
                    
                    # Get discontinuation rate
                    disc_rate = 0
                    if m.safety_profile.discontinuations:
                        disc_data = m.safety_profile.discontinuations
                        if isinstance(disc_data, dict):
                            disc_rate = disc_data.get('total', 0) or disc_data.get('rate', 0)
                        elif isinstance(disc_data, (int, float)):
                            disc_rate = disc_data
                    
                    safety_data.append({
                        'treatment': treatment_name,
                        'grade_3_4_ae_rate': total_ae_rate,
                        'discontinuation_rate': disc_rate,
                        'study_title': m.study_identification.title[:30] + "..."
                    })
        
        if not safety_data:
            return self._create_empty_figure("Safety Analysis", "No safety data available")
        
        df = pd.DataFrame(safety_data)
        
        # Create safety scatter plot
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['grade_3_4_ae_rate'],
            y=df['discontinuation_rate'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['grade_3_4_ae_rate'],
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Grade 3-4 AE Rate (%)")
            ),
            text=df['treatment'],
            hovertemplate="<b>%{text}</b><br>Grade 3-4 AEs: %{x}%<br>Discontinuations: %{y}%<extra></extra>"
        ))
        
        # Add quadrant lines
        fig.add_vline(x=50, line_dash="dash", line_color="gray", annotation_text="High AE Rate")
        fig.add_hline(y=20, line_dash="dash", line_color="gray", annotation_text="High Discontinuation")
        
        fig.update_layout(
            title="⚠️ Safety Profile Analysis",
            xaxis_title="Grade 3-4 Adverse Event Rate (%)",
            yaxis_title="Treatment Discontinuation Rate (%)",
            template=self.theme,
            height=500
        )
        
        return fig
    
    def _create_patient_demographics_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create patient demographics analysis"""
        
        # Extract demographic data
        ages = []
        male_percentages = []
        enrollments = []
        
        for m in metadata_list:
            if m.patient_demographics.median_age:
                ages.append(m.patient_demographics.median_age)
            
            if m.patient_demographics.male_percentage:
                male_percentages.append(m.patient_demographics.male_percentage)
            
            if m.patient_demographics.total_enrolled:
                enrollments.append(m.patient_demographics.total_enrolled)
        
        if not any([ages, male_percentages, enrollments]):
            return self._create_empty_figure("Patient Demographics", "No demographic data available")
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Age Distribution', 'Gender Distribution', 'Enrollment Size'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}, {"type": "histogram"}]]
        )
        
        # Age distribution
        if ages:
            fig.add_trace(
                go.Histogram(
                    x=ages,
                    nbinsx=10,
                    name="Median Age",
                    marker_color=self._get_color('primary'),
                    hovertemplate="Age Range: %{x}<br>Studies: %{y}<extra></extra>"
                ),
                row=1, col=1
            )
        
        # Gender distribution
        if male_percentages:
            fig.add_trace(
                go.Histogram(
                    x=male_percentages,
                    nbinsx=10,
                    name="Male %",
                    marker_color=self._get_color('secondary'),
                    hovertemplate="Male %: %{x}<br>Studies: %{y}<extra></extra>"
                ),
                row=1, col=2
            )
        
        # Enrollment distribution
        if enrollments:
            fig.add_trace(
                go.Histogram(
                    x=enrollments,
                    nbinsx=15,
                    name="Enrollment",
                    marker_color=self._get_color('success'),
                    hovertemplate="Enrollment: %{x}<br>Studies: %{y}<extra></extra>"
                ),
                row=1, col=3
            )
        
        fig.update_layout(
            title="👥 Patient Demographics Analysis",
            template=self.theme,
            height=400,
            showlegend=False
        )
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Median Age (years)", row=1, col=1)
        fig.update_xaxes(title_text="Male Percentage (%)", row=1, col=2)
        fig.update_xaxes(title_text="Total Enrollment", row=1, col=3)
        fig.update_yaxes(title_text="Number of Studies")
        
        return fig
    
    def _create_efficacy_safety_bubble_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create efficacy vs safety bubble chart"""
        
        # Extract efficacy and safety data
        bubble_data = []
        for m in metadata_list:
            orr = None
            ae_rate = None
            study_size = m.patient_demographics.total_enrolled or 10
            
            # Extract ORR
            if m.efficacy_outcomes.overall_response_rate:
                orr_data = m.efficacy_outcomes.overall_response_rate
                if isinstance(orr_data, dict):
                    orr = orr_data.get('value') or orr_data.get('rate')
                elif isinstance(orr_data, (int, float)):
                    orr = orr_data
            
            # Extract AE rate
            if m.safety_profile.grade_3_4_aes:
                ae_data = m.safety_profile.grade_3_4_aes
                if isinstance(ae_data, list) and ae_data:
                    # Sum percentages from list
                    ae_rate = sum([ae.get('percentage', 0) for ae in ae_data if isinstance(ae, dict)])
                elif isinstance(ae_data, dict):
                    ae_rate = ae_data.get('total_rate', 0)
                elif isinstance(ae_data, (int, float)):
                    ae_rate = ae_data
            
            # Get treatment name
            treatment_name = "Unknown"
            if m.treatment_regimens and m.treatment_regimens[0].regimen_name:
                treatment_name = m.treatment_regimens[0].regimen_name
            
            # Get MM subtype
            mm_subtype = "Unknown"
            if m.disease_characteristics.mm_subtype:
                mm_subtype = m.disease_characteristics.mm_subtype[0].value
            
            if orr and ae_rate and 0 <= orr <= 100 and 0 <= ae_rate <= 100:
                bubble_data.append({
                    'orr': orr,
                    'ae_rate': ae_rate,
                    'study_size': study_size,
                    'treatment': treatment_name,
                    'mm_subtype': mm_subtype,
                    'study_title': m.study_identification.title[:40] + "..."
                })
        
        if not bubble_data:
            return self._create_empty_figure("Efficacy-Safety Analysis", "Insufficient efficacy and safety data")
        
        df = pd.DataFrame(bubble_data)
        
        # Create bubble chart
        fig = px.scatter(
            df,
            x='ae_rate',
            y='orr',
            size='study_size',
            color='mm_subtype',
            hover_data=['treatment', 'study_title'],
            title="⚖️ Efficacy vs Safety Analysis",
            labels={
                'ae_rate': 'Grade 3-4 Adverse Event Rate (%)',
                'orr': 'Overall Response Rate (%)',
                'study_size': 'Study Size',
                'mm_subtype': 'MM Subtype'
            }
        )
        
        # Add quadrant lines
        median_orr = df['orr'].median()
        median_ae = df['ae_rate'].median()
        
        fig.add_hline(y=median_orr, line_dash="dash", line_color="gray", 
                     annotation_text=f"Median ORR: {median_orr:.1f}%")
        fig.add_vline(x=median_ae, line_dash="dash", line_color="gray",
                     annotation_text=f"Median AE: {median_ae:.1f}%")
        
        # Add quadrant annotations
        fig.add_annotation(x=10, y=90, text="🎯 Ideal<br>Quadrant", 
                          bgcolor="lightgreen", bordercolor="green")
        fig.add_annotation(x=90, y=90, text="⚠️ High Efficacy<br>High Toxicity", 
                          bgcolor="yellow", bordercolor="orange")
        fig.add_annotation(x=10, y=10, text="❌ Low Efficacy<br>Low Toxicity", 
                          bgcolor="lightcoral", bordercolor="red")
        fig.add_annotation(x=90, y=10, text="💀 Worst<br>Quadrant", 
                          bgcolor="red", bordercolor="darkred")
        
        fig.update_layout(
            template=self.theme,
            height=600
        )
        
        return fig
    
    def _create_novel_agents_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create novel agents adoption analysis"""
        
        # Define novel agent keywords
        novel_keywords = {
            'CAR-T': ['car-t', 'cart', 'ciltacabtagene', 'idecabtagene', 'cilta-cel', 'ide-cel'],
            'Bispecific': ['bispecific', 'teclistamab', 'talquetamab', 'elranatamab'],
            'ADC': ['belantamab', 'mafodotin', 'adc', 'antibody-drug'],
            'BCL-2': ['venetoclax', 'bcl-2', 'bcl2'],
            'SINE': ['selinexor', 'sine', 'exportin'],
            'HDAC': ['panobinostat', 'hdac', 'histone deacetylase']
        }
        
        # Count novel agents
        novel_counts = {agent_type: 0 for agent_type in novel_keywords.keys()}
        total_studies = len(metadata_list)
        
        for m in metadata_list:
            study_text = (m.study_identification.title + " " + 
                         " ".join([r.regimen_name or "" for r in m.treatment_regimens])).lower()
            
            for agent_type, keywords in novel_keywords.items():
                if any(keyword in study_text for keyword in keywords):
                    novel_counts[agent_type] += 1
        
        # Calculate percentages
        agent_types = list(novel_counts.keys())
        counts = list(novel_counts.values())
        percentages = [count/total_studies*100 if total_studies > 0 else 0 for count in counts]
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=agent_types,
                x=percentages,
                orientation='h',
                text=[f"{count} ({pct:.1f}%)" for count, pct in zip(counts, percentages)],
                textposition='auto',
                marker_color=[
                    self._get_color('car_t'), self._get_color('bispecific'), 
                    self._get_color('adc'), self._get_color('primary'),
                    self._get_color('secondary'), self._get_color('warning')
                ],
                hovertemplate="<b>%{y}</b><br>Studies: %{text}<br>% of Total: %{x:.1f}%<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title=f"🧬 Novel Agent Adoption (n={total_studies} studies)",
            xaxis_title="Percentage of Studies (%)",
            yaxis_title="Novel Agent Type",
            template=self.theme,
            height=400
        )
        
        return fig
    
    def _create_response_rates_by_line_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create response rates by line of therapy"""
        
        # Extract response rates by line of therapy
        line_data = defaultdict(list)
        
        for m in metadata_list:
            line_of_therapy = m.treatment_history.line_of_therapy
            if not line_of_therapy:
                continue
                
            # Clean up line of therapy naming
            if 'first' in line_of_therapy.lower() or '1' in line_of_therapy:
                line_key = "First Line"
            elif 'second' in line_of_therapy.lower() or '2' in line_of_therapy:
                line_key = "Second Line"
            elif 'third' in line_of_therapy.lower() or '3' in line_of_therapy:
                line_key = "Third Line"
            elif 'fourth' in line_of_therapy.lower() or '4' in line_of_therapy:
                line_key = "Fourth+ Line"
            else:
                line_key = "Other"
            
            # Extract ORR
            if m.efficacy_outcomes.overall_response_rate:
                orr_data = m.efficacy_outcomes.overall_response_rate
                orr = None
                if isinstance(orr_data, dict):
                    orr = orr_data.get('value') or orr_data.get('rate')
                elif isinstance(orr_data, (int, float)):
                    orr = orr_data
                
                if orr and 0 <= orr <= 100:
                    line_data[line_key].append(orr)
        
        if not line_data:
            return self._create_empty_figure("Response Rates by Line", "No line of therapy data available")
        
        # Create box plot
        fig = go.Figure()
        
        colors = [self._get_color('success'), self._get_color('primary'), 
                 self._get_color('warning'), self._get_color('danger')]
        
        for i, (line, orr_values) in enumerate(sorted(line_data.items())):
            if orr_values:
                fig.add_trace(go.Box(
                    y=orr_values,
                    name=line,
                    marker_color=colors[i % len(colors)],
                    boxpoints='all',
                    jitter=0.3,
                    pointpos=-1.5,
                    hovertemplate="<b>%{fullData.name}</b><br>ORR: %{y}%<extra></extra>"
                ))
        
        fig.update_layout(
            title="📊 Overall Response Rates by Line of Therapy",
            yaxis_title="Overall Response Rate (%)",
            xaxis_title="Line of Therapy",
            template=self.theme,
            height=500,
            showlegend=False
        )
        
        return fig
    
    def _create_study_size_distribution(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create study size distribution analysis"""
        
        # Extract enrollment data
        enrollments = []
        for m in metadata_list:
            if m.patient_demographics.total_enrolled:
                enrollments.append(m.patient_demographics.total_enrolled)
        
        if not enrollments:
            return self._create_empty_figure("Study Size Distribution", "No enrollment data available")
        
        # Create histogram with size categories
        size_categories = []
        for enrollment in enrollments:
            if enrollment < 30:
                size_categories.append("Small (<30)")
            elif enrollment < 100:
                size_categories.append("Medium (30-99)")
            elif enrollment < 300:
                size_categories.append("Large (100-299)")
            else:
                size_categories.append("Very Large (≥300)")
        
        category_counts = Counter(size_categories)
        
        # Define order
        ordered_categories = ["Small (<30)", "Medium (30-99)", "Large (100-299)", "Very Large (≥300)"]
        ordered_counts = [category_counts.get(cat, 0) for cat in ordered_categories]
        
        fig = go.Figure(data=[
            go.Bar(
                x=ordered_categories,
                y=ordered_counts,
                text=ordered_counts,
                textposition='auto',
                marker_color=[
                    self._get_color('danger'), self._get_color('warning'),
                    self._get_color('primary'), self._get_color('success')
                ],
                hovertemplate="<b>%{x}</b><br>Studies: %{y}<extra></extra>"
            )
        ])
        
        # Add statistics
        total_patients = sum(enrollments)
        median_size = np.median(enrollments)
        mean_size = np.mean(enrollments)
        
        fig.add_annotation(
            text=f"Total Patients: {total_patients:,}<br>Median Size: {median_size:.0f}<br>Mean Size: {mean_size:.0f}",
            xref="paper", yref="paper",
            x=0.95, y=0.95,
            bgcolor="white",
            bordercolor="gray",
            borderwidth=1
        )
        
        fig.update_layout(
            title=f"📏 Study Size Distribution (n={len(enrollments)} studies)",
            xaxis_title="Study Size Category",
            yaxis_title="Number of Studies",
            template=self.theme,
            height=500
        )
        
        return fig
    
    # Additional utility methods for advanced analytics
    
    def create_treatment_timeline_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create treatment evolution timeline if publication years available"""
        
        # Extract publication years and treatments
        timeline_data = []
        for m in metadata_list:
            pub_year = m.study_identification.publication_year
            if pub_year and m.treatment_regimens:
                for regimen in m.treatment_regimens:
                    if regimen.regimen_name and regimen.regimen_name != "Unknown":
                        timeline_data.append({
                            'year': pub_year,
                            'treatment': regimen.regimen_name,
                            'title': m.study_identification.title
                        })
        
        if not timeline_data:
            return self._create_empty_figure("Treatment Timeline", "No publication year data available")
        
        df = pd.DataFrame(timeline_data)
        
        # Count treatments by year
        yearly_counts = df.groupby(['year', 'treatment']).size().reset_index(name='count')
        
        fig = px.line(
            yearly_counts,
            x='year',
            y='count',
            color='treatment',
            title="📅 Treatment Evolution Timeline",
            labels={'year': 'Publication Year', 'count': 'Number of Studies'}
        )
        
        fig.update_layout(
            template=self.theme,
            height=500
        )
        
        return fig
    
    def create_competitive_landscape_chart(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> go.Figure:
        """Create competitive landscape analysis"""
        
        # Extract sponsor/company information if available
        sponsors = []
        for m in metadata_list:
            sponsor = m.study_identification.study_group
            if sponsor:
                sponsors.append(sponsor)
        
        if not sponsors:
            return self._create_empty_figure("Competitive Landscape", "No sponsor data available")
        
        sponsor_counts = Counter(sponsors)
        top_sponsors = dict(sponsor_counts.most_common(10))
        
        fig = go.Figure(data=[
            go.Pie(
                labels=list(top_sponsors.keys()),
                values=list(top_sponsors.values()),
                hole=.3,
                textinfo='label+percent',
                hovertemplate="<b>%{label}</b><br>Studies: %{value}<br>Percentage: %{percent}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            title="🏢 Competitive Landscape - Top Study Sponsors",
            template=self.theme,
            height=500
        )
        
        return fig
    
    def export_dashboard_data(self, metadata_list: List[ComprehensiveAbstractMetadata]) -> Dict[str, pd.DataFrame]:
        """Export all visualization data as DataFrames for further analysis"""
        
        export_data = {}
        
        # Study overview data
        study_overview = []
        for m in metadata_list:
            study_overview.append({
                'title': m.study_identification.title,
                'study_type': m.study_design.study_type.value if m.study_design.study_type else None,
                'mm_subtype': ', '.join([s.value for s in m.disease_characteristics.mm_subtype]) if m.disease_characteristics.mm_subtype else None,
                'total_enrolled': m.patient_demographics.total_enrolled,
                'confidence_score': m.extraction_confidence
            })
        export_data['study_overview'] = pd.DataFrame(study_overview)
        
        # Treatment data
        treatment_data = []
        for m in metadata_list:
            for regimen in m.treatment_regimens:
                treatment_data.append({
                    'study_title': m.study_identification.title,
                    'regimen_name': regimen.regimen_name,
                    'drugs': ', '.join([drug.get('name', '') for drug in regimen.drugs]) if regimen.drugs else None,
                    'cycle_length': regimen.cycle_length
                })
        export_data['treatments'] = pd.DataFrame(treatment_data)
        
        # Efficacy data
        efficacy_data = []
        for m in metadata_list:
            efficacy_data.append({
                'study_title': m.study_identification.title,
                'orr': self._extract_numeric_value(m.efficacy_outcomes.overall_response_rate),
                'cr_rate': self._extract_numeric_value(m.efficacy_outcomes.complete_response_rate),
                'pfs_median': self._extract_numeric_value(m.efficacy_outcomes.progression_free_survival)
            })
        export_data['efficacy'] = pd.DataFrame(efficacy_data)
        
        return export_data
    
    def _extract_numeric_value(self, data: Any) -> Optional[float]:
        """Helper to extract numeric values from various data structures"""
        if isinstance(data, dict):
            return data.get('value') or data.get('rate') or data.get('median')
        elif isinstance(data, (int, float)):
            return data
        return None

    def _create_efficacy_analysis_chart_from_analyzer(self, efficacy_benchmarks: Dict[str, Any]) -> go.Figure:
        """Create efficacy analysis plot using analyzer results (benchmarks by line of therapy)"""
        if not efficacy_benchmarks or 'overall_benchmarks' not in efficacy_benchmarks:
            return self._create_empty_figure("Efficacy Analysis", "No efficacy benchmark data available")
        df = pd.DataFrame(efficacy_benchmarks['overall_benchmarks'])
        if df.empty:
            return self._create_empty_figure("Efficacy Analysis", "No efficacy benchmark data available")
        fig = go.Figure()
        if 'line_of_therapy' in df and 'mean_orr' in df:
            fig.add_trace(go.Bar(
                x=df['line_of_therapy'],
                y=df['mean_orr'],
                name='Mean ORR',
                marker_color=self._get_color('efficacy')
            ))
        if 'line_of_therapy' in df and 'mean_pfs' in df:
            fig.add_trace(go.Bar(
                x=df['line_of_therapy'],
                y=df['mean_pfs'],
                name='Mean PFS',
                marker_color=self._get_color('primary')
            ))
        fig.update_layout(
            title="Efficacy Benchmarks by Line of Therapy",
            barmode='group',
            template=self.theme,
            xaxis_title="Line of Therapy",
            yaxis_title="Value"
        )
        return fig

    def _create_safety_analysis_chart_from_analyzer(self, safety_patterns: Dict[str, Any]) -> go.Figure:
        """Create safety analysis plot using analyzer results (safety by line of therapy)"""
        if not safety_patterns or 'safety_by_line' not in safety_patterns:
            return self._create_empty_figure("Safety Analysis", "No safety pattern data available")
        df = pd.DataFrame(safety_patterns['safety_by_line'])
        if df.empty:
            return self._create_empty_figure("Safety Analysis", "No safety pattern data available")
        fig = go.Figure()
        if 'line_of_therapy' in df and 'avg_completion_rate' in df:
            fig.add_trace(go.Bar(
                x=df['line_of_therapy'],
                y=df['avg_completion_rate'],
                name='Avg Completion Rate',
                marker_color=self._get_color('success')
            ))
        if 'line_of_therapy' in df and 'death_rate_percentage' in df:
            fig.add_trace(go.Bar(
                x=df['line_of_therapy'],
                y=df['death_rate_percentage'],
                name='Death Rate (%)',
                marker_color=self._get_color('danger')
            ))
        fig.update_layout(
            title="Safety Patterns by Line of Therapy",
            barmode='group',
            template=self.theme,
            xaxis_title="Line of Therapy",
            yaxis_title="Percentage"
        )
        return fig