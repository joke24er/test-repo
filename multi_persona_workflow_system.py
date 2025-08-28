#!/usr/bin/env python3
"""
Multi-Persona Workflow System
============================

A comprehensive LangChain-based system for orchestrating multiple AI personas in sequential workflows.
This system is designed for complex analysis tasks that require different specialized perspectives.

Key Features:
- Multiple specialized personas (Risk Assessment, Claims Analysis, Compliance Review, etc.)
- Workflow orchestration with context preservation
- External prompt loading from YAML/JSON files
- Cost tracking and monitoring
- Predefined workflow templates
- Easy integration of existing prompts

Why LangChain over Direct API Calls:
- Built-in workflow orchestration for chaining personas
- Memory management across different personas
- Prompt templating and versioning
- Observability and tracing
- Error handling and retry mechanisms
- Natural evolution path to full agents

Author: AI Assistant
Date: 2024
"""

import os
import json
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# LangChain imports for workflow orchestration
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback


class OutputFormat(Enum):
    """
    Enumeration for different output formats that personas can produce.
    This helps standardize the output structure across different personas.
    """
    STRUCTURED_ANALYSIS = "structured_analysis"  # Detailed analysis with sections
    EXECUTIVE_SUMMARY = "executive_summary"      # High-level summary
    BULLET_POINTS = "bullet_points"              # Bullet-point format
    JSON_FORMAT = "json_format"                  # JSON structured output


@dataclass
class PersonaConfig:
    """
    Configuration class for individual personas.
    Contains all the necessary information to create and run a persona.
    """
    name: str                                    # Human-readable name
    description: str                             # Description of persona's role
    prompt_template: str                         # The actual prompt template
    output_format: OutputFormat                  # Expected output format
    temperature: float = 0.1                     # LLM temperature (creativity vs consistency)
    max_tokens: Optional[int] = None             # Maximum tokens for response
    required_inputs: List[str] = None            # Required input placeholders
    
    def __post_init__(self):
        """Set default required inputs if not specified"""
        if self.required_inputs is None:
            self.required_inputs = ["input", "context"]


class MultiPersonaWorkflow:
    """
    Main workflow orchestrator that manages multiple personas and executes workflows.
    
    This class handles:
    - Loading persona configurations from files or defaults
    - Creating LangChain chains for each persona
    - Executing workflows with multiple personas in sequence
    - Managing context flow between personas
    - Cost tracking and result export
    """
    
    def __init__(self, 
                 openai_api_key: str,
                 model_name: str = "gpt-4",
                 base_temperature: float = 0.1):
        """
        Initialize the workflow system.
        
        Args:
            openai_api_key: OpenAI API key for LLM access
            model_name: Name of the LLM model to use
            base_temperature: Default temperature for LLM responses
        """
        # Initialize the LLM with OpenAI
        self.llm = ChatOpenAI(
            temperature=base_temperature,
            openai_api_key=openai_api_key,
            model=model_name
        )
        
        # Memory system to maintain context across personas
        self.memory = ConversationBufferMemory()
        
        # Storage for personas and workflow templates
        self.personas: Dict[str, PersonaConfig] = {}
        self.workflow_templates: Dict[str, List[str]] = {}
        
        # Load configurations
        self._load_personas()
        self._load_workflow_templates()
    
    def _load_personas(self):
        """
        Load persona configurations from external files or use defaults.
        
        This method tries to load from configuration files first:
        1. personas_config.yaml
        2. personas_config.json
        3. config/personas.yaml
        
        If no external files are found, it loads the default personas.
        """
        # List of possible configuration file paths
        config_paths = [
            "personas_config.yaml",
            "personas_config.json",
            "config/personas.yaml"
        ]
        
        # Try to load from external config files
        loaded = False
        for path in config_paths:
            if os.path.exists(path):
                print(f"Loading personas from {path}")
                self._load_personas_from_file(path)
                loaded = True
                break
        
        # If no external files found, load default personas
        if not loaded:
            print("No external config found, loading default personas")
            self._load_default_personas()
    
    def _load_personas_from_file(self, file_path: str):
        """
        Load persona configurations from YAML or JSON file.
        
        Args:
            file_path: Path to the configuration file
        """
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
        
        # Convert configuration data to PersonaConfig objects
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
        """
        Load the default set of personas with predefined prompts.
        
        These personas are designed for insurance and business analysis workflows.
        Each persona has a specific role and expertise area.
        """
        default_personas = {
            # Risk Assessment Specialist - Analyzes potential risks and their impact
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
            
            # Claims Analysis Expert - Reviews and analyzes claims for validity and processing
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
            
            # Compliance Review Officer - Ensures adherence to regulatory and policy requirements
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
            
            # Financial Analyst - Performs financial analysis and projections
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
            
            # Operational Excellence Specialist - Identifies process improvements and operational efficiencies
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
            
            # Summary Specialist - Creates concise summaries of complex information
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
        
        # Add all default personas to the system
        self.personas.update(default_personas)
    
    def _load_workflow_templates(self):
        """
        Load predefined workflow templates for common analysis patterns.
        
        These templates provide pre-configured sequences of personas
        for different types of analysis scenarios.
        """
        self.workflow_templates = {
            # Full analysis with all personas in logical sequence
            "full_analysis": [
                "risk_assessment",
                "claims_analysis",
                "compliance_review", 
                "financial_analysis",
                "operational_excellence",
                "summary_only"
            ],
            # Quick review for fast analysis
            "quick_review": [
                "risk_assessment",
                "claims_analysis",
                "summary_only"
            ],
            # Compliance-focused analysis
            "compliance_focus": [
                "compliance_review",
                "risk_assessment",
                "summary_only"
            ],
            # Financial analysis focus
            "financial_focus": [
                "financial_analysis",
                "risk_assessment",
                "summary_only"
            ]
        }
    
    def add_persona(self, persona_id: str, config: PersonaConfig):
        """
        Add a new persona to the workflow system.
        
        Args:
            persona_id: Unique identifier for the persona
            config: PersonaConfig object with persona details
        """
        self.personas[persona_id] = config
        print(f"Added persona: {config.name} (ID: {persona_id})")
    
    def create_persona_chain(self, persona_name: str) -> LLMChain:
        """
        Create a LangChain chain for a specific persona.
        
        Args:
            persona_name: Name/ID of the persona to create chain for
            
        Returns:
            LLMChain: Configured LangChain chain for the persona
            
        Raises:
            ValueError: If persona_name is not found
        """
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
        
        # Create prompt template from persona's prompt
        prompt = ChatPromptTemplate.from_template(persona.prompt_template)
        
        # Create and return the LangChain chain
        return LLMChain(
            llm=persona_llm,
            prompt=prompt,
            memory=self.memory,
            verbose=True
        )
    
    def validate_workflow(self, persona_sequence: List[str]) -> List[str]:
        """
        Validate a workflow sequence and return any issues found.
        
        Args:
            persona_sequence: List of persona names in the workflow
            
        Returns:
            List[str]: List of validation issues (empty if valid)
        """
        issues = []
        
        for persona_name in persona_sequence:
            if persona_name not in self.personas:
                issues.append(f"Unknown persona: {persona_name}")
        
        return issues
    
    def execute_workflow(self, 
                        input_data: str, 
                        persona_sequence: List[str],
                        track_costs: bool = True) -> Dict[str, Any]:
        """
        Execute a workflow with multiple personas in sequence.
        
        This is the main method that orchestrates the entire workflow:
        1. Validates the workflow sequence
        2. Executes each persona in order
        3. Passes context from previous personas to subsequent ones
        4. Tracks costs and collects results
        
        Args:
            input_data: The data to be analyzed
            persona_sequence: List of persona names in execution order
            track_costs: Whether to track API costs
            
        Returns:
            Dict containing results, costs, and workflow summary
            
        Raises:
            ValueError: If workflow validation fails
        """
        # Validate workflow before execution
        issues = self.validate_workflow(persona_sequence)
        if issues:
            raise ValueError(f"Workflow validation failed: {', '.join(issues)}")
        
        results = {}
        context = ""
        total_cost = 0
        
        # Execute each persona in sequence
        for i, persona_name in enumerate(persona_sequence):
            print(f"\n=== Step {i+1}: Executing {self.personas[persona_name].name} ===")
            
            # Create chain for this persona
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
            
            # Store results for this persona
            results[persona_name] = {
                "persona_name": self.personas[persona_name].name,
                "analysis": response,
                "output_format": self.personas[persona_name].output_format.value,
                "step": i + 1
            }
            
            # Update context for next persona
            context += f"\n{self.personas[persona_name].name} Analysis:\n{response}\n"
        
        # Return comprehensive results
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
        """
        Execute a predefined workflow template.
        
        Args:
            template_name: Name of the template to execute
            input_data: Data to be analyzed
            track_costs: Whether to track API costs
            
        Returns:
            Dict containing workflow results
            
        Raises:
            ValueError: If template_name is not found
        """
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow template: {template_name}")
        
        return self.execute_workflow(
            input_data=input_data,
            persona_sequence=self.workflow_templates[template_name],
            track_costs=track_costs
        )
    
    def get_available_personas(self) -> List[str]:
        """Get list of available persona names/IDs"""
        return list(self.personas.keys())
    
    def get_available_templates(self) -> List[str]:
        """Get list of available workflow template names"""
        return list(self.workflow_templates.keys())
    
    def export_results(self, results: Dict[str, Any], format: str = "json") -> str:
        """
        Export workflow results in specified format.
        
        Args:
            results: Results dictionary from workflow execution
            format: Export format ("json" or "yaml")
            
        Returns:
            String representation of results in specified format
            
        Raises:
            ValueError: If format is not supported
        """
        if format.lower() == "json":
            return json.dumps(results, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump(results, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")


def create_sample_config():
    """
    Create a sample configuration file for personas.
    
    This function demonstrates how to create external configuration files
    that can be loaded by the workflow system.
    """
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


def integrate_manager_prompts_example():
    """
    Example function showing how to integrate your manager's existing prompts.
    
    This demonstrates how to add custom personas with specific business logic
    and methodologies that your manager has already developed.
    """
    
    # Initialize the workflow
    workflow = MultiPersonaWorkflow(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    # Example 1: Add a custom risk assessor with manager's methodology
    custom_risk_assessor = PersonaConfig(
        name="Custom Risk Assessor",
        description="Specialized risk assessment using manager's methodology",
        prompt_template="""You are a specialized Risk Assessment Specialist using our company's proprietary methodology.

Your task is to analyze the provided information using our 5-point risk matrix:
1. Risk Identification (Low/Medium/High)
2. Impact Assessment (1-5 scale)
3. Likelihood Assessment (1-5 scale)
4. Risk Score Calculation (Impact × Likelihood)
5. Mitigation Priority (Immediate/Short-term/Long-term)

Context from previous analysis: {context}

Current information to analyze: {input}

Please provide your analysis in the following format:

RISK IDENTIFICATION:
- [List identified risks]

IMPACT ASSESSMENT:
- [Assess impact on scale 1-5]

LIKELIHOOD ASSESSMENT:
- [Assess likelihood on scale 1-5]

RISK SCORE:
- [Calculate Impact × Likelihood]

MITIGATION PRIORITY:
- [Assign priority level]

RECOMMENDATIONS:
- [Specific action items]""",
        output_format=OutputFormat.STRUCTURED_ANALYSIS,
        temperature=0.1
    )
    
    workflow.add_persona("custom_risk", custom_risk_assessor)
    
    # Example 2: Add a claims analysis persona with specific business rules
    custom_claims_analyzer = PersonaConfig(
        name="Claims Processing Specialist",
        description="Claims analysis following company-specific procedures",
        prompt_template="""You are a Claims Processing Specialist following our company's established procedures.

ANALYSIS FRAMEWORK:
1. Claim Validity Check
2. Documentation Completeness
3. Policy Coverage Verification
4. Fraud Risk Assessment
5. Processing Recommendation

Context from previous analysis: {context}

Claims information to analyze: {input}

Please analyze using our standard format:

CLAIM VALIDITY:
- [Valid/Invalid/Needs Review]
- [Reasoning]

DOCUMENTATION STATUS:
- [Complete/Incomplete/Missing]
- [List missing documents]

POLICY COVERAGE:
- [Covered/Not Covered/Partial]
- [Coverage details]

FRAUD RISK:
- [Low/Medium/High]
- [Risk indicators]

PROCESSING RECOMMENDATION:
- [Approve/Deny/Investigate Further]
- [Next steps]

SPECIAL CONSIDERATIONS:
- [Any unique factors]""",
        output_format=OutputFormat.STRUCTURED_ANALYSIS,
        temperature=0.1
    )
    
    workflow.add_persona("custom_claims", custom_claims_analyzer)
    
    # Add custom workflow templates
    workflow.workflow_templates.update({
        "manager_approved_analysis": [
            "custom_risk",
            "custom_claims", 
            "summary_only"
        ]
    })
    
    return workflow


def run_example_analysis():
    """
    Run a complete example analysis using the workflow system.
    
    This function demonstrates the full workflow execution process
    with sample data and shows how to handle results.
    """
    
    # Set up the workflow with custom personas
    workflow = integrate_manager_prompts_example()
    
    # Sample insurance claim data for analysis
    sample_claim = """
    INSURANCE CLAIM DETAILS:
    
    Claim Number: CLM-2024-001
    Policy Holder: Sarah Johnson
    Policy Number: POL-2023-456
    Claim Amount: $25,000
    Incident Date: 2024-01-20
    Incident Type: Vehicle Accident
    Vehicle: 2021 Honda Accord
    Damage Description: Front-end collision, airbag deployment
    Police Report: Filed (Report #PR-2024-789)
    Witnesses: 1 available
    Medical Treatment: Emergency room visit, minor injuries
    Estimated Repair Cost: $18,000
    Rental Car: $2,000
    Medical Bills: $5,000
    
    ADDITIONAL INFORMATION:
    - Policy holder has 2 previous claims in last 3 years
    - Weather conditions: Clear, dry
    - Time of incident: 2:30 PM
    - Location: Intersection of Main St and Oak Ave
    - Other driver: Uninsured motorist
    - Photos available: Yes (10 photos)
    - Witness statement: Available
    """
    
    print("Available personas:", workflow.get_available_personas())
    print("Available templates:", workflow.get_available_templates())
    
    # Execute the manager-approved analysis workflow
    print("\n" + "="*60)
    print("EXECUTING MANAGER-APPROVED ANALYSIS WORKFLOW")
    print("="*60)
    
    try:
        results = workflow.execute_template_workflow(
            template_name="manager_approved_analysis",
            input_data=sample_claim,
            track_costs=True
        )
        
        # Display results
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        
        for persona, result in results["results"].items():
            print(f"\n{'-'*50}")
            print(f"PERSONA: {result['persona_name']} (Step {result['step']})")
            print(f"{'-'*50}")
            print(result['analysis'])
        
        print(f"\nTotal Cost: ${results['total_cost']:.4f}")
        print(f"Workflow Summary: {results['workflow_summary']}")
        
        # Export results
        exported = workflow.export_results(results, "json")
        with open("workflow_results.json", 'w') as f:
            f.write(exported)
        print("\nResults exported to workflow_results.json")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("This is expected if OpenAI API key is not set.")


def main():
    """
    Main function that demonstrates the complete workflow system.
    
    This function shows:
    1. How to set up the system
    2. How to integrate custom prompts
    3. How to execute workflows
    4. How to handle results
    """
    print("Multi-Persona Workflow System")
    print("="*50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Set it before running analysis.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
        print("\nCreating sample configuration files...")
        
        # Create sample config if it doesn't exist
        if not os.path.exists("personas_config.yaml"):
            create_sample_config()
    
    # Show system capabilities
    print("\n" + "="*50)
    print("SYSTEM CAPABILITIES")
    print("="*50)
    
    # Initialize basic workflow to show available features
    workflow = MultiPersonaWorkflow(
        openai_api_key=os.getenv("OPENAI_API_KEY", "demo-key")
    )
    
    print("Available personas:", workflow.get_available_personas())
    print("Available templates:", workflow.get_available_templates())
    
    # Run example analysis
    print("\n" + "="*50)
    print("EXAMPLE ANALYSIS")
    print("="*50)
    run_example_analysis()
    
    print("\n" + "="*50)
    print("NEXT STEPS")
    print("="*50)
    print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
    print("2. Replace example prompts with your manager's actual prompts")
    print("3. Customize workflow templates for your use cases")
    print("4. Run analysis with your real data")
    print("5. Monitor costs and optimize as needed")


if __name__ == "__main__":
    main()