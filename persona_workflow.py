from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
import json

class PersonaWorkflow:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            temperature=0.1,
            openai_api_key=openai_api_key,
            model="gpt-4"
        )
        self.memory = ConversationBufferMemory()
        self.personas = self._initialize_personas()
        
    def _initialize_personas(self) -> Dict[str, Dict[str, Any]]:
        """Initialize all personas with their prompts and configurations"""
        return {
            "risk_assessment": {
                "name": "Risk Assessment Specialist",
                "description": "Analyzes potential risks and their impact",
                "prompt_template": """You are a Risk Assessment Specialist with expertise in identifying and evaluating potential risks.

Your task is to analyze the provided information and assess:
1. Potential risks and their likelihood
2. Impact severity of identified risks
3. Risk mitigation strategies
4. Risk priority ranking

Context from previous analysis: {context}

Current information to analyze: {input}

Provide a comprehensive risk assessment following this structure:
- Risk Identification
- Risk Analysis (Likelihood & Impact)
- Risk Evaluation
- Risk Treatment Recommendations
- Priority Ranking""",
                "output_format": "structured_analysis"
            },
            
            "claims_analysis": {
                "name": "Claims Analysis Expert",
                "description": "Reviews and analyzes claims for validity and processing",
                "prompt_template": """You are a Claims Analysis Expert with deep knowledge of claims processing and validation.

Your task is to analyze claims information and provide insights on:
1. Claim validity and completeness
2. Documentation requirements
3. Processing recommendations
4. Potential issues or red flags

Context from previous analysis: {context}

Claims information to analyze: {input}

Provide a detailed claims analysis covering:
- Claim Validity Assessment
- Documentation Review
- Processing Recommendations
- Risk Indicators
- Next Steps""",
                "output_format": "structured_analysis"
            },
            
            "compliance_review": {
                "name": "Compliance Review Officer",
                "description": "Ensures adherence to regulatory and policy requirements",
                "prompt_template": """You are a Compliance Review Officer responsible for ensuring regulatory and policy compliance.

Your task is to review information for compliance with:
1. Regulatory requirements
2. Internal policies and procedures
3. Industry standards
4. Legal obligations

Context from previous analysis: {context}

Information to review: {input}

Provide a comprehensive compliance review including:
- Regulatory Compliance Assessment
- Policy Adherence Review
- Compliance Risk Identification
- Remediation Recommendations
- Compliance Status Summary""",
                "output_format": "structured_analysis"
            },
            
            "financial_analysis": {
                "name": "Financial Analyst",
                "description": "Performs financial analysis and projections",
                "prompt_template": """You are a Financial Analyst with expertise in financial modeling and analysis.

Your task is to analyze financial information and provide insights on:
1. Financial performance indicators
2. Cost-benefit analysis
3. Financial risk assessment
4. Budget implications

Context from previous analysis: {context}

Financial information to analyze: {input}

Provide a detailed financial analysis covering:
- Financial Performance Review
- Cost-Benefit Analysis
- Financial Risk Assessment
- Budget Impact Analysis
- Financial Recommendations""",
                "output_format": "structured_analysis"
            },
            
            "operational_excellence": {
                "name": "Operational Excellence Specialist",
                "description": "Identifies process improvements and operational efficiencies",
                "prompt_template": """You are an Operational Excellence Specialist focused on process improvement and efficiency.

Your task is to analyze operational aspects and identify:
1. Process inefficiencies
2. Improvement opportunities
3. Best practice recommendations
4. Operational risk factors

Context from previous analysis: {context}

Operational information to analyze: {input}

Provide a comprehensive operational analysis including:
- Process Efficiency Assessment
- Improvement Opportunities
- Best Practice Recommendations
- Operational Risk Factors
- Implementation Roadmap""",
                "output_format": "structured_analysis"
            },
            
            "summary_only": {
                "name": "Summary Specialist",
                "description": "Creates concise summaries of complex information",
                "prompt_template": """You are a Summary Specialist who creates clear, concise summaries of complex information.

Your task is to synthesize all previous analyses into a comprehensive summary covering:
1. Key findings and insights
2. Critical recommendations
3. Priority actions
4. Executive summary

Previous analyses: {context}

Provide a structured summary including:
- Executive Summary
- Key Findings
- Critical Recommendations
- Priority Actions
- Risk Level Assessment""",
                "output_format": "executive_summary"
            }
        }
    
    def create_persona_chain(self, persona_name: str) -> LLMChain:
        """Create a LangChain chain for a specific persona"""
        if persona_name not in self.personas:
            raise ValueError(f"Unknown persona: {persona_name}")
            
        persona = self.personas[persona_name]
        prompt = ChatPromptTemplate.from_template(persona["prompt_template"])
        
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def execute_workflow(self, input_data: str, persona_sequence: List[str]) -> Dict[str, Any]:
        """Execute a workflow with multiple personas in sequence"""
        results = {}
        context = ""
        
        for persona_name in persona_sequence:
            print(f"\n=== Executing {self.personas[persona_name]['name']} ===")
            
            chain = self.create_persona_chain(persona_name)
            
            # Execute the persona analysis
            response = chain.run({
                "input": input_data,
                "context": context
            })
            
            results[persona_name] = {
                "persona_name": self.personas[persona_name]["name"],
                "analysis": response,
                "output_format": self.personas[persona_name]["output_format"]
            }
            
            # Update context for next persona
            context += f"\n{self.personas[persona_name]['name']} Analysis:\n{response}\n"
        
        return results
    
    def get_available_personas(self) -> List[str]:
        """Get list of available persona names"""
        return list(self.personas.keys())

# Example usage
if __name__ == "__main__":
    # Initialize the workflow (you'll need to set your OpenAI API key)
    workflow = PersonaWorkflow(openai_api_key="your-api-key-here")
    
    # Example workflow execution
    sample_data = """
    Insurance claim for vehicle damage:
    - Claim amount: $15,000
    - Incident date: 2024-01-15
    - Policy holder: John Doe
    - Vehicle: 2022 Toyota Camry
    - Damage description: Rear-end collision
    - Police report: Filed
    - Witnesses: 2 available
    """
    
    # Define the workflow sequence
    persona_sequence = [
        "risk_assessment",
        "claims_analysis", 
        "compliance_review",
        "financial_analysis",
        "operational_excellence",
        "summary_only"
    ]
    
    # Execute the workflow
    results = workflow.execute_workflow(sample_data, persona_sequence)
    
    # Print results
    for persona, result in results.items():
        print(f"\n{'='*50}")
        print(f"Persona: {result['persona_name']}")
        print(f"{'='*50}")
        print(result['analysis'])