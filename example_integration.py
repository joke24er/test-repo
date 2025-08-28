#!/usr/bin/env python3
"""
Example script showing how to integrate your manager's existing prompts
into the multi-persona workflow system.
"""

import os
from advanced_persona_workflow import AdvancedPersonaWorkflow, PersonaConfig, OutputFormat

def integrate_manager_prompts():
    """
    Example of how to integrate your manager's existing prompts
    """
    
    # Initialize the workflow
    workflow = AdvancedPersonaWorkflow(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    # Example 1: Add a custom persona with your manager's existing prompt
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
    
    # Example 3: Add a compliance specialist with regulatory knowledge
    compliance_specialist = PersonaConfig(
        name="Regulatory Compliance Officer",
        description="Ensures compliance with industry-specific regulations",
        prompt_template="""You are a Regulatory Compliance Officer with expertise in insurance regulations.

COMPLIANCE FRAMEWORK:
1. Regulatory Requirements Check
2. Policy Compliance Verification
3. Documentation Standards Review
4. Reporting Requirements Assessment
5. Compliance Risk Evaluation

Context from previous analysis: {context}

Information to review: {input}

Please provide compliance analysis in this format:

REGULATORY REQUIREMENTS:
- [List applicable regulations]
- [Compliance status]

POLICY COMPLIANCE:
- [Internal policy adherence]
- [Gaps identified]

DOCUMENTATION STANDARDS:
- [Meets standards: Yes/No]
- [Documentation issues]

REPORTING REQUIREMENTS:
- [Required reports]
- [Timeline for reporting]

COMPLIANCE RISKS:
- [Risk level: Low/Medium/High]
- [Specific compliance risks]

REMEDIATION ACTIONS:
- [Required actions]
- [Timeline for completion]

COMPLIANCE STATUS:
- [Overall compliance rating]""",
        output_format=OutputFormat.STRUCTURED_ANALYSIS,
        temperature=0.1
    )
    
    workflow.add_persona("regulatory_compliance", compliance_specialist)
    
    return workflow

def create_custom_workflow_templates(workflow):
    """
    Create custom workflow templates using your integrated personas
    """
    
    # Add custom workflow templates
    workflow.workflow_templates.update({
        "manager_approved_analysis": [
            "custom_risk",
            "custom_claims", 
            "regulatory_compliance",
            "summary_only"
        ],
        "quick_claims_review": [
            "custom_claims",
            "summary_only"
        ],
        "compliance_focused": [
            "regulatory_compliance",
            "custom_risk",
            "summary_only"
        ]
    })

def run_example_analysis():
    """
    Run an example analysis using the integrated personas
    """
    
    # Set up the workflow with custom personas
    workflow = integrate_manager_prompts()
    create_custom_workflow_templates(workflow)
    
    # Sample insurance claim data
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
    workflow.export_results(results, "json")
    print("\nResults exported to workflow_results.json")

def load_from_external_config():
    """
    Example of loading personas from external configuration files
    """
    
    # Create a sample external config file
    external_config = {
        "personas": {
            "external_risk_assessor": {
                "name": "External Risk Assessor",
                "description": "Risk assessment using external methodology",
                "prompt_template": """You are an External Risk Assessor using industry-standard methodologies.

Your analysis should follow these steps:
1. Risk Identification
2. Risk Quantification
3. Risk Prioritization
4. Mitigation Planning

Context from previous analysis: {context}
Information to analyze: {input}

Provide your analysis in a structured format.""",
                "output_format": "structured_analysis",
                "temperature": 0.1,
                "required_inputs": ["input", "context"]
            }
        }
    }
    
    # Save to file
    import yaml
    with open("external_personas_config.yaml", 'w') as f:
        yaml.dump(external_config, f, default_flow_style=False)
    
    print("Created external_personas_config.yaml")
    
    # The workflow will automatically load this file if it exists
    workflow = AdvancedPersonaWorkflow(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    print("Available personas after loading external config:", workflow.get_available_personas())

if __name__ == "__main__":
    print("Multi-Persona Workflow Integration Example")
    print("="*50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Set it before running analysis.")
        print("Example: export OPENAI_API_KEY='your-key-here'")
    
    # Run the integration example
    try:
        run_example_analysis()
    except Exception as e:
        print(f"Error running analysis: {e}")
        print("This is expected if OpenAI API key is not set.")
    
    # Show external config loading
    print("\n" + "="*50)
    print("EXTERNAL CONFIG LOADING EXAMPLE")
    print("="*50)
    load_from_external_config()
    
    print("\nIntegration example completed!")
    print("\nNext steps:")
    print("1. Set your OpenAI API key")
    print("2. Replace the example prompts with your manager's actual prompts")
    print("3. Customize the workflow templates for your use cases")
    print("4. Run the analysis with your real data")