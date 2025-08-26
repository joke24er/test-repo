from typing import List, Dict
import uuid
from datetime import datetime
from .simplified_models import Persona


class SimplePersonaManager:
    def __init__(self):
        self.personas: Dict[str, Persona] = {}
        self._initialize_default_personas()
    
    def _initialize_default_personas(self):
        """Initialize default personas with simplified templates"""
        
        default_personas = [
            Persona(
                id=str(uuid.uuid4()),
                name="Contract Reviewer",
                description="Analyzes contracts for risks, terms, and compliance",
                prompt_template="Analyze this contract document. Focus on: 1) Key terms and obligations 2) Potential risks 3) Compliance issues 4) Recommendations. Document: {content}",
                analysis_focus=["legal_terms", "risk_assessment", "compliance", "recommendations"]
            ),
            Persona(
                id=str(uuid.uuid4()),
                name="Financial Analyst",
                description="Analyzes financial documents for ratios, trends, and insights",
                prompt_template="Analyze this financial document. Focus on: 1) Key financial ratios 2) Trends and patterns 3) Risk assessment 4) Investment insights. Document: {content}",
                analysis_focus=["financial_ratios", "trends", "risk_assessment", "investment_insights"]
            ),
            Persona(
                id=str(uuid.uuid4()),
                name="Risk Manager",
                description="Identifies and assesses various types of risks",
                prompt_template="Perform a risk assessment of this document. Focus on: 1) Risk identification 2) Risk categorization 3) Mitigation strategies 4) Monitoring recommendations. Document: {content}",
                analysis_focus=["risk_identification", "risk_assessment", "mitigation_strategies", "monitoring"]
            ),
            Persona(
                id=str(uuid.uuid4()),
                name="Technical Reviewer",
                description="Reviews technical documents for specifications and feasibility",
                prompt_template="Review this technical document. Focus on: 1) Technical specifications 2) Feasibility assessment 3) Implementation considerations 4) Quality assurance. Document: {content}",
                analysis_focus=["specifications", "feasibility", "implementation", "quality_assurance"]
            ),
            Persona(
                id=str(uuid.uuid4()),
                name="Compliance Officer",
                description="Checks regulatory compliance and policy adherence",
                prompt_template="Review this document for compliance. Focus on: 1) Regulatory compliance 2) Policy alignment 3) Governance issues 4) Compliance recommendations. Document: {content}",
                analysis_focus=["regulatory_compliance", "policy_alignment", "governance", "documentation"]
            )
        ]
        
        for persona in default_personas:
            self.personas[persona.id] = persona
    
    def get_all_personas(self) -> List[Persona]:
        return list(self.personas.values())
    
    def get_persona_by_id(self, persona_id: str) -> Persona:
        return self.personas.get(persona_id)
    
    def create_custom_persona(self, name: str, description: str, 
                            prompt_template: str, analysis_focus: List[str],
                            created_by: str) -> Persona:
        persona = Persona(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            prompt_template=prompt_template,
            analysis_focus=analysis_focus,
            is_custom=True,
            created_by=created_by
        )
        self.personas[persona.id] = persona
        return persona
    
    def delete_persona(self, persona_id: str) -> bool:
        if persona_id in self.personas:
            persona = self.personas[persona_id]
            if persona.is_custom:
                del self.personas[persona_id]
                return True
        return False


# Global instance
persona_manager = SimplePersonaManager()