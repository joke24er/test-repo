from typing import List, Dict, Any
from .models import Persona, PersonaType
import uuid


class PersonaManager:
    def __init__(self):
        self.personas: Dict[str, Persona] = {}
        self._initialize_default_personas()
    
    def _initialize_default_personas(self):
        """Initialize default personas for document analysis"""
        
        # Contract Review Persona (Agent - complex analysis)
        contract_review = Persona(
            id=str(uuid.uuid4()),
            name="Contract Review Specialist",
            description="Expert in legal contract analysis, identifying risks, obligations, and compliance issues",
            persona_type=PersonaType.AGENT,
            prompt_template="""You are a senior contract review specialist with 15+ years of experience in corporate law. 
            Analyze the provided contract document thoroughly and provide:
            
            1. **Key Terms Summary**: Extract and summarize critical terms, dates, and obligations
            2. **Risk Assessment**: Identify potential legal, financial, and operational risks
            3. **Compliance Check**: Verify compliance with relevant laws and regulations
            4. **Recommendations**: Suggest modifications or areas requiring legal counsel
            5. **Clause Analysis**: Review specific clauses for fairness and enforceability
            
            Document: {document_content}
            
            Provide a structured analysis with clear sections and actionable insights.""",
            analysis_focus=["legal_terms", "risk_assessment", "compliance", "recommendations"]
        )
        
        # Financial Analysis Persona (Agent - complex calculations)
        financial_analysis = Persona(
            id=str(uuid.uuid4()),
            name="Financial Analyst",
            description="Expert in financial document analysis, ratios, trends, and investment insights",
            persona_type=PersonaType.AGENT,
            prompt_template="""You are a certified financial analyst specializing in financial statement analysis and investment evaluation.
            Analyze the provided financial document and provide:
            
            1. **Financial Ratios**: Calculate and interpret key financial ratios
            2. **Trend Analysis**: Identify financial trends and patterns
            3. **Cash Flow Analysis**: Evaluate liquidity and cash management
            4. **Risk Assessment**: Identify financial risks and red flags
            5. **Investment Insights**: Provide investment recommendations and valuation insights
            
            Document: {document_content}
            
            Provide quantitative analysis with clear metrics and financial insights.""",
            analysis_focus=["financial_ratios", "trends", "cash_flow", "risk_assessment", "investment_insights"]
        )
        
        # Risk Analysis Persona (Agent - comprehensive risk evaluation)
        risk_analysis = Persona(
            id=str(uuid.uuid4()),
            name="Risk Management Specialist",
            description="Expert in identifying, assessing, and mitigating various types of risks",
            persona_type=PersonaType.AGENT,
            prompt_template="""You are a senior risk management specialist with expertise in enterprise risk assessment.
            Analyze the provided document for comprehensive risk evaluation:
            
            1. **Risk Identification**: Identify all potential risks (operational, financial, strategic, compliance)
            2. **Risk Assessment**: Evaluate probability and impact of each risk
            3. **Risk Categorization**: Classify risks by type and severity
            4. **Mitigation Strategies**: Suggest risk mitigation and control measures
            5. **Risk Monitoring**: Recommend ongoing monitoring and reporting mechanisms
            
            Document: {document_content}
            
            Provide a detailed risk matrix with clear mitigation strategies.""",
            analysis_focus=["risk_identification", "risk_assessment", "mitigation_strategies", "monitoring"]
        )
        
        # Technical Review Persona (Prompt - straightforward analysis)
        technical_review = Persona(
            id=str(uuid.uuid4()),
            name="Technical Reviewer",
            description="Expert in technical document review, specifications, and technical feasibility",
            persona_type=PersonaType.PROMPT,
            prompt_template="""Review the technical document and provide:
            
            1. **Technical Specifications**: Extract and validate technical requirements
            2. **Feasibility Assessment**: Evaluate technical feasibility and constraints
            3. **Implementation Considerations**: Identify implementation challenges and solutions
            4. **Quality Assurance**: Review for technical accuracy and completeness
            5. **Recommendations**: Suggest improvements or alternatives
            
            Document: {document_content}""",
            analysis_focus=["specifications", "feasibility", "implementation", "quality_assurance"]
        )
        
        # Compliance Review Persona (Prompt - regulatory analysis)
        compliance_review = Persona(
            id=str(uuid.uuid4()),
            name="Compliance Officer",
            description="Expert in regulatory compliance, policy adherence, and governance",
            persona_type=PersonaType.PROMPT,
            prompt_template="""As a compliance officer, analyze the document for:
            
            1. **Regulatory Compliance**: Check adherence to relevant regulations and standards
            2. **Policy Alignment**: Verify alignment with internal policies and procedures
            3. **Governance Issues**: Identify governance and oversight considerations
            4. **Documentation Standards**: Review for proper documentation and record-keeping
            5. **Compliance Recommendations**: Suggest compliance improvements
            
            Document: {document_content}""",
            analysis_focus=["regulatory_compliance", "policy_alignment", "governance", "documentation"]
        )
        
        # Market Analysis Persona (Agent - market intelligence)
        market_analysis = Persona(
            id=str(uuid.uuid4()),
            name="Market Intelligence Analyst",
            description="Expert in market analysis, competitive intelligence, and strategic insights",
            persona_type=PersonaType.AGENT,
            prompt_template="""You are a market intelligence analyst with deep expertise in competitive analysis and market dynamics.
            Analyze the provided document for market insights:
            
            1. **Market Position**: Assess current market position and competitive landscape
            2. **Market Trends**: Identify key market trends and opportunities
            3. **Competitive Analysis**: Evaluate competitive advantages and threats
            4. **Strategic Implications**: Provide strategic recommendations based on market analysis
            5. **Market Intelligence**: Extract actionable market intelligence
            
            Document: {document_content}
            
            Provide strategic market insights with clear competitive positioning.""",
            analysis_focus=["market_position", "trends", "competitive_analysis", "strategic_implications"]
        )
        
        # Add all personas to the manager
        for persona in [contract_review, financial_analysis, risk_analysis, 
                       technical_review, compliance_review, market_analysis]:
            self.personas[persona.id] = persona
    
    def get_all_personas(self) -> List[Persona]:
        """Get all available personas"""
        return list(self.personas.values())
    
    def get_persona_by_id(self, persona_id: str) -> Persona:
        """Get a specific persona by ID"""
        return self.personas.get(persona_id)
    
    def create_custom_persona(self, name: str, description: str, 
                            prompt_template: str, analysis_focus: List[str],
                            created_by: str) -> Persona:
        """Create a custom persona"""
        persona = Persona(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            persona_type=PersonaType.PROMPT,  # Custom personas default to prompt type
            prompt_template=prompt_template,
            analysis_focus=analysis_focus,
            is_custom=True,
            created_by=created_by
        )
        self.personas[persona.id] = persona
        return persona
    
    def delete_persona(self, persona_id: str) -> bool:
        """Delete a custom persona"""
        if persona_id in self.personas:
            persona = self.personas[persona_id]
            if persona.is_custom:
                del self.personas[persona_id]
                return True
        return False


# Global persona manager instance
persona_manager = PersonaManager()