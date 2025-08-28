from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from typing import List, Dict, Any, Optional
import json
import yaml
import os
from dataclasses import dataclass
from enum import Enum

class OutputFormat(Enum):
    STRUCTURED_ANALYSIS = "structured_analysis"
    EXECUTIVE_SUMMARY = "executive_summary"
    BULLET_POINTS = "bullet_points"
    JSON_FORMAT = "json_format"

@dataclass
class PersonaConfig:
    name: str
    description: str
    prompt_template: str
    output_format: OutputFormat
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    required_inputs: List[str] = None
    
    def __post_init__(self):
        if self.required_inputs is None:
            self.required_inputs = ["input", "context"]

class AdvancedPersonaWorkflow:
    def __init__(self, 
                 openai_api_key: str,
                 model_name: str = "gpt-4",
                 base_temperature: float = 0.1):
        self.llm = ChatOpenAI(
            temperature=base_temperature,
            openai_api_key=openai_api_key,
            model=model_name
        )
        self.memory = ConversationBufferMemory()
        self.personas: Dict[str, PersonaConfig] = {}
        self.workflow_templates: Dict[str, List[str]] = {}
        self._load_personas()
        self._load_workflow_templates()
    
    def _load_personas(self):
        """Load personas from configuration files or use defaults"""
        # Try to load from external config files
        config_paths = [
            "personas_config.yaml",
            "personas_config.json",
            "config/personas.yaml"
        ]
        
        loaded = False
        for path in config_paths:
            if os.path.exists(path):
                self._load_personas_from_file(path)
                loaded = True
                break
        
        if not loaded:
            self._load_default_personas()
    
    def _load_personas_from_file(self, file_path: str):
        """Load persona configurations from YAML or JSON file"""
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        for persona_id, persona_data in config['personas'].items():
            self.personas[persona_id] = PersonaConfig(
                name=persona_data['name'],
                description=persona_data['description'],
                prompt_template=persona_data['prompt_template'],
                output_format=OutputFormat(persona_data.get('output_format', 'structured_analysis')),
                temperature=persona_data.get('temperature', 0.1),
                max_tokens=persona_data.get('max_tokens'),
                required_inputs=persona_data.get('required_inputs', ['input', 'context'])
            )
    
    def _load_default_personas(self):
        """Load default persona configurations"""
        default_personas = {
            "risk_assessment": PersonaConfig(
                name="Risk Assessment Specialist",
                description="Analyzes potential risks and their impact",
                prompt_template="""You are a Risk Assessment Specialist with expertise in identifying and evaluating potential risks.

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
                output_format=OutputFormat.STRUCTURED_ANALYSIS
            ),
            
            "claims_analysis": PersonaConfig(
                name="Claims Analysis Expert",
                description="Reviews and analyzes claims for validity and processing",
                prompt_template="""You are a Claims Analysis Expert with deep knowledge of claims processing and validation.

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
                output_format=OutputFormat.STRUCTURED_ANALYSIS
            ),
            
            "compliance_review": PersonaConfig(
                name="Compliance Review Officer",
                description="Ensures adherence to regulatory and policy requirements",
                prompt_template="""You are a Compliance Review Officer responsible for ensuring regulatory and policy compliance.

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
                output_format=OutputFormat.STRUCTURED_ANALYSIS
            ),
            
            "financial_analysis": PersonaConfig(
                name="Financial Analyst",
                description="Performs financial analysis and projections",
                prompt_template="""You are a Financial Analyst with expertise in financial modeling and analysis.

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
                output_format=OutputFormat.STRUCTURED_ANALYSIS
            ),
            
            "operational_excellence": PersonaConfig(
                name="Operational Excellence Specialist",
                description="Identifies process improvements and operational efficiencies",
                prompt_template="""You are an Operational Excellence Specialist focused on process improvement and efficiency.

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
                output_format=OutputFormat.STRUCTURED_ANALYSIS
            ),
            
            "summary_only": PersonaConfig(
                name="Summary Specialist",
                description="Creates concise summaries of complex information",
                prompt_template="""You are a Summary Specialist who creates clear, concise summaries of complex information.

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
                output_format=OutputFormat.EXECUTIVE_SUMMARY
            )
        }
        
        self.personas.update(default_personas)
    
    def _load_workflow_templates(self):
        """Load predefined workflow templates"""
        self.workflow_templates = {
            "full_analysis": [
                "risk_assessment",
                "claims_analysis",
                "compliance_review", 
                "financial_analysis",
                "operational_excellence",
                "summary_only"
            ],
            "quick_review": [
                "risk_assessment",
                "claims_analysis",
                "summary_only"
            ],
            "compliance_focus": [
                "compliance_review",
                "risk_assessment",
                "summary_only"
            ],
            "financial_focus": [
                "financial_analysis",
                "risk_assessment",
                "summary_only"
            ]
        }
    
    def add_persona(self, persona_id: str, config: PersonaConfig):
        """Add a new persona to the workflow"""
        self.personas[persona_id] = config
    
    def create_persona_chain(self, persona_name: str) -> LLMChain:
        """Create a LangChain chain for a specific persona"""
        if persona_name not in self.personas:
            raise ValueError(f"Unknown persona: {persona_name}")
            
        persona = self.personas[persona_name]
        
        # Create LLM with persona-specific settings
        persona_llm = ChatOpenAI(
            temperature=persona.temperature,
            openai_api_key=self.llm.openai_api_key,
            model=self.llm.model_name,
            max_tokens=persona.max_tokens
        )
        
        prompt = ChatPromptTemplate.from_template(persona.prompt_template)
        
        return LLMChain(
            llm=persona_llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def validate_workflow(self, persona_sequence: List[str]) -> List[str]:
        """Validate workflow and return any issues"""
        issues = []
        
        for persona_name in persona_sequence:
            if persona_name not in self.personas:
                issues.append(f"Unknown persona: {persona_name}")
        
        return issues
    
    def execute_workflow(self, 
                        input_data: str, 
                        persona_sequence: List[str],
                        track_costs: bool = True) -> Dict[str, Any]:
        """Execute a workflow with multiple personas in sequence"""
        
        # Validate workflow
        issues = self.validate_workflow(persona_sequence)
        if issues:
            raise ValueError(f"Workflow validation failed: {', '.join(issues)}")
        
        results = {}
        context = ""
        total_cost = 0
        
        for i, persona_name in enumerate(persona_sequence):
            print(f"\n=== Step {i+1}: Executing {self.personas[persona_name].name} ===")
            
            chain = self.create_persona_chain(persona_name)
            
            # Execute with cost tracking if enabled
            if track_costs:
                with get_openai_callback() as cb:
                    response = chain.run({
                        "input": input_data,
                        "context": context
                    })
                    total_cost += cb.total_cost
                    print(f"Cost for {persona_name}: ${cb.total_cost:.4f}")
            else:
                response = chain.run({
                    "input": input_data,
                    "context": context
                })
            
            results[persona_name] = {
                "persona_name": self.personas[persona_name].name,
                "analysis": response,
                "output_format": self.personas[persona_name].output_format.value,
                "step": i + 1
            }
            
            # Update context for next persona
            context += f"\n{self.personas[persona_name].name} Analysis:\n{response}\n"
        
        return {
            "results": results,
            "total_cost": total_cost if track_costs else None,
            "workflow_summary": {
                "total_steps": len(persona_sequence),
                "personas_used": persona_sequence,
                "input_length": len(input_data)
            }
        }
    
    def execute_template_workflow(self, 
                                 template_name: str,
                                 input_data: str,
                                 track_costs: bool = True) -> Dict[str, Any]:
        """Execute a predefined workflow template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        return self.execute_workflow(
            input_data=input_data,
            persona_sequence=self.workflow_templates[template_name],
            track_costs=track_costs
        )
    
    def get_available_personas(self) -> List[str]:
        """Get list of available persona names"""
        return list(self.personas.keys())
    
    def get_available_templates(self) -> List[str]:
        """Get list of available workflow templates"""
        return list(self.workflow_templates.keys())
    
    def export_results(self, results: Dict[str, Any], format: str = "json") -> str:
        """Export workflow results in specified format"""
        if format.lower() == "json":
            return json.dumps(results, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump(results, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Example usage and configuration file creation
def create_sample_config():
    """Create a sample configuration file for personas"""
    sample_config = {
        "personas": {
            "risk_assessment": {
                "name": "Risk Assessment Specialist",
                "description": "Analyzes potential risks and their impact",
                "prompt_template": "You are a Risk Assessment Specialist...",
                "output_format": "structured_analysis",
                "temperature": 0.1,
                "required_inputs": ["input", "context"]
            }
        }
    }
    
    with open("personas_config.yaml", 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False)
    
    print("Created sample personas_config.yaml")

if __name__ == "__main__":
    # Create sample config if it doesn't exist
    if not os.path.exists("personas_config.yaml"):
        create_sample_config()
    
    # Initialize the workflow
    workflow = AdvancedPersonaWorkflow(openai_api_key="your-api-key-here")
    
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
    
    # Execute using a template
    print("Available templates:", workflow.get_available_templates())
    print("Available personas:", workflow.get_available_personas())
    
    # Execute quick review workflow
    results = workflow.execute_template_workflow(
        template_name="quick_review",
        input_data=sample_data,
        track_costs=True
    )
    
    # Print results
    print("\n" + "="*60)
    print("WORKFLOW RESULTS")
    print("="*60)
    
    for persona, result in results["results"].items():
        print(f"\n{'-'*40}")
        print(f"Persona: {result['persona_name']} (Step {result['step']})")
        print(f"{'-'*40}")
        print(result['analysis'])
    
    print(f"\nTotal Cost: ${results['total_cost']:.4f}")
    print(f"Workflow Summary: {results['workflow_summary']}")
    
    # Export results
    exported = workflow.export_results(results, "json")
    with open("workflow_results.json", 'w') as f:
        f.write(exported)