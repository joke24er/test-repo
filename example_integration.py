"""
Example: Integrating Your Manager's Existing Prompts

This file demonstrates how to integrate your manager's existing prompts
into the persona workflow system.
"""

from advanced_workflow import AdvancedWorkflowEngine, PersonaConfig
import json

def integrate_manager_prompts():
    """
    Example of how to integrate your manager's existing prompts
    """
    
    # Your manager's existing prompts (replace with actual prompts)
    manager_prompts = {
        "Risk Assessment": """
        You are a Risk Assessment specialist with 15 years of experience in insurance and risk management.
        
        Analyze the provided information for potential risks, vulnerabilities, and risk factors.
        
        Input: {input_text}
        Previous Context: {context}
        
        Provide a comprehensive risk assessment including:
        1. Risk Identification: List all potential risks
        2. Risk Categorization: Classify risks by type (financial, operational, strategic, etc.)
        3. Likelihood Assessment: Rate each risk (Low/Medium/High)
        4. Impact Assessment: Rate potential impact (Low/Medium/High)
        5. Risk Score: Calculate risk score (Likelihood × Impact)
        6. Mitigation Strategies: Provide specific recommendations
        7. Priority Actions: List immediate actions needed
        
        Format your response as a structured analysis with clear sections and bullet points.
        """,
        
        "Claims Analysis": """
        You are a Claims Analysis expert with expertise in insurance claims processing and fraud detection.
        
        Review and analyze the claims-related information provided.
        
        Input: {input_text}
        Previous Context: {context}
        
        Conduct a thorough claims analysis covering:
        1. Claim Validation: Verify claim legitimacy and completeness
        2. Pattern Recognition: Identify any patterns or anomalies
        3. Fraud Indicators: Assess potential fraud risk factors
        4. Coverage Analysis: Review policy coverage and exclusions
        5. Processing Recommendations: Suggest next steps
        6. Settlement Considerations: Evaluate settlement options
        7. Documentation Requirements: List required documentation
        
        Provide specific insights and actionable recommendations.
        """,
        
        "Compliance Review": """
        You are a Compliance Review specialist with deep knowledge of insurance regulations and industry standards.
        
        Evaluate the provided information against relevant regulations, policies, and compliance requirements.
        
        Input: {input_text}
        Previous Context: {context}
        
        Perform a comprehensive compliance review including:
        1. Regulatory Requirements: Identify applicable regulations
        2. Policy Compliance: Check against internal policies
        3. Documentation Standards: Verify documentation compliance
        4. Reporting Requirements: Identify required reports
        5. Compliance Gaps: Highlight any compliance issues
        6. Remediation Steps: Provide corrective actions
        7. Monitoring Recommendations: Suggest ongoing compliance measures
        
        Focus on practical compliance guidance and risk mitigation.
        """,
        
        "Financial Analysis": """
        You are a Financial Analysis expert specializing in insurance financial metrics and performance analysis.
        
        Analyze the financial aspects of the provided information.
        
        Input: {input_text}
        Previous Context: {context}
        
        Conduct a detailed financial analysis covering:
        1. Financial Impact Assessment: Evaluate monetary implications
        2. Cost-Benefit Analysis: Compare costs vs benefits
        3. Budget Considerations: Assess budget implications
        4. ROI Analysis: Calculate return on investment
        5. Financial Risk Factors: Identify financial risks
        6. Optimization Opportunities: Suggest cost savings
        7. Financial Recommendations: Provide financial guidance
        
        Include specific calculations and financial metrics where applicable.
        """,
        
        "Operational Excellence": """
        You are an Operational Excellence specialist focused on process improvement and efficiency optimization.
        
        Evaluate the operational processes and identify improvement opportunities.
        
        Input: {input_text}
        Previous Context: {context}
        
        Conduct an operational excellence review including:
        1. Process Analysis: Evaluate current processes
        2. Efficiency Assessment: Identify inefficiencies
        3. Bottleneck Identification: Find process bottlenecks
        4. Automation Opportunities: Suggest automation possibilities
        5. Quality Improvement: Recommend quality enhancements
        6. Performance Metrics: Suggest KPIs and metrics
        7. Implementation Roadmap: Provide improvement timeline
        
        Focus on practical, implementable improvements.
        """,
        
        "Summary Only": """
        You are a Summary specialist with expertise in distilling complex information into clear, actionable summaries.
        
        Create a concise, well-structured summary of the provided information.
        
        Input: {input_text}
        Previous Context: {context}
        
        Provide a comprehensive summary including:
        1. Executive Summary: High-level overview (2-3 sentences)
        2. Key Findings: Most important discoveries
        3. Critical Issues: Urgent matters requiring attention
        4. Recommendations: Priority actions needed
        5. Risk Assessment: Summary of risks and mitigation
        6. Next Steps: Immediate actions required
        7. Timeline: Suggested implementation timeline
        
        Keep the summary concise but comprehensive, focusing on actionable insights.
        """
    }
    
    # Create persona configurations from your manager's prompts
    persona_configs = []
    
    for name, prompt in manager_prompts.items():
        config = PersonaConfig(
            name=name,
            description=f"Your manager's {name} prompt",
            prompt_template=prompt,
            temperature=0.1,  # Low temperature for consistent analysis
            parallel_processing=name in ["Risk Assessment", "Claims Analysis"]  # These can run in parallel
        )
        persona_configs.append(config)
    
    # Save to configuration file
    with open('manager_persona_config.json', 'w') as f:
        config_data = [config.__dict__ for config in persona_configs]
        json.dump(config_data, f, indent=2)
    
    print("✅ Manager's prompts integrated into persona_config.json")
    return persona_configs

def load_and_test_manager_prompts():
    """
    Test the integrated manager prompts
    """
    
    # Initialize workflow engine
    engine = AdvancedWorkflowEngine()
    
    # Load personas from the configuration file
    engine.load_personas_from_config('manager_persona_config.json')
    
    # Test input (replace with your actual use case)
    test_input = """
    Customer XYZ has filed a claim for $75,000 for business interruption due to a fire incident.
    The incident occurred on 2024-02-01. The business has been closed for 3 weeks.
    Customer has been with us for 5 years with 2 previous claims (both minor property damage under $5,000).
    Initial investigation shows the fire was caused by electrical malfunction in equipment.
    The customer has comprehensive business interruption coverage with a $10,000 deductible.
    """
    
    # Execute workflow with your manager's personas
    persona_sequence = ["Risk Assessment", "Claims Analysis", "Compliance Review", "Summary Only"]
    
    print("🚀 Executing workflow with your manager's prompts...")
    results = engine.execute_workflow(test_input, persona_sequence)
    
    # Display results
    print("\n📊 Workflow Results:")
    print("=" * 50)
    
    for persona_name, output in results.items():
        print(f"\n🔍 {persona_name}")
        print(f"Confidence: {output.confidence:.1%}")
        print(f"Analysis: {output.analysis[:200]}...")
        print(f"Key Findings: {', '.join(output.key_findings[:3])}")
        if output.recommendations:
            print(f"Recommendations: {', '.join(output.recommendations[:3])}")
    
    # Test chat functionality
    print("\n💬 Testing chat functionality...")
    chat_response = engine.chat_with_output(
        "What are the main risks and what should we do about them?",
        results
    )
    print(f"Chat Response: {chat_response}")
    
    return results

def create_prompt_directory_example():
    """
    Example of creating a prompts directory structure
    """
    import os
    
    # Create prompts directory
    os.makedirs("manager_prompts", exist_ok=True)
    
    # Example prompt files (replace with your manager's actual prompts)
    prompt_files = {
        "Risk Assessment.txt": """
        You are a Risk Assessment specialist with 15 years of experience in insurance and risk management.
        
        Analyze the provided information for potential risks, vulnerabilities, and risk factors.
        
        Input: {input_text}
        Previous Context: {context}
        
        Provide a comprehensive risk assessment including:
        1. Risk Identification: List all potential risks
        2. Risk Categorization: Classify risks by type
        3. Likelihood Assessment: Rate each risk (Low/Medium/High)
        4. Impact Assessment: Rate potential impact (Low/Medium/High)
        5. Risk Score: Calculate risk score (Likelihood × Impact)
        6. Mitigation Strategies: Provide specific recommendations
        7. Priority Actions: List immediate actions needed
        
        Format your response as a structured analysis with clear sections.
        """,
        
        "Claims Analysis.txt": """
        You are a Claims Analysis expert with expertise in insurance claims processing and fraud detection.
        
        Review and analyze the claims-related information provided.
        
        Input: {input_text}
        Previous Context: {context}
        
        Conduct a thorough claims analysis covering:
        1. Claim Validation: Verify claim legitimacy and completeness
        2. Pattern Recognition: Identify any patterns or anomalies
        3. Fraud Indicators: Assess potential fraud risk factors
        4. Coverage Analysis: Review policy coverage and exclusions
        5. Processing Recommendations: Suggest next steps
        6. Settlement Considerations: Evaluate settlement options
        7. Documentation Requirements: List required documentation
        
        Provide specific insights and actionable recommendations.
        """
    }
    
    # Write prompt files
    for filename, content in prompt_files.items():
        with open(f"manager_prompts/{filename}", 'w') as f:
            f.write(content.strip())
    
    print("✅ Created manager_prompts/ directory with example prompt files")
    print("📁 You can now replace these with your manager's actual prompts")

if __name__ == "__main__":
    print("🔧 Persona Workflow Integration Examples")
    print("=" * 50)
    
    # Example 1: Integration via configuration file
    print("\n1️⃣ Integrating via configuration file...")
    integrate_manager_prompts()
    
    # Example 2: Testing the integration
    print("\n2️⃣ Testing the integration...")
    try:
        load_and_test_manager_prompts()
    except Exception as e:
        print(f"⚠️  Test failed (likely due to missing API key): {e}")
        print("💡 Set OPENAI_API_KEY environment variable to test")
    
    # Example 3: Creating prompt directory
    print("\n3️⃣ Creating prompt directory structure...")
    create_prompt_directory_example()
    
    print("\n✅ Integration examples completed!")
    print("\n📋 Next steps:")
    print("1. Replace the example prompts with your manager's actual prompts")
    print("2. Set your OPENAI_API_KEY environment variable")
    print("3. Run the web interface: python web_interface.py")
    print("4. Test with your actual use cases")