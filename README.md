# Multi-Persona Workflow System

A flexible LangChain-based system for orchestrating multiple AI personas in sequential workflows. Perfect for complex analysis tasks that require different specialized perspectives.

## Why LangChain for Multi-Persona Workflows?

### Advantages:
- **Built-in workflow orchestration** - Seamlessly chain multiple personas together
- **Memory management** - Maintain context across different personas in the workflow
- **Prompt templating** - Easy to manage and version your existing prompts
- **Observability** - Built-in tracing and monitoring for complex workflows
- **Error handling** - Robust retry mechanisms and fallback strategies
- **Agent evolution** - Natural path to evolve personas into full agents

### When to Consider Direct API Calls:
- Simple single-persona scenarios
- Extremely latency-sensitive applications
- When you need maximum control over API features
- Cost optimization for simple use cases

## Features

- **Multiple Personas**: Risk Assessment, Claims Analysis, Compliance Review, Financial Analysis, Operational Excellence, Summary
- **Workflow Templates**: Predefined sequences for common analysis patterns
- **External Prompt Loading**: Load your manager's existing prompts from YAML/JSON files
- **Cost Tracking**: Monitor API usage across the entire workflow
- **Context Preservation**: Each persona builds on previous analyses
- **Flexible Configuration**: Easy to add new personas and modify existing ones

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Set up your OpenAI API key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Basic Usage

```python
from advanced_persona_workflow import AdvancedPersonaWorkflow

# Initialize the workflow
workflow = AdvancedPersonaWorkflow(openai_api_key="your-api-key-here")

# Execute a predefined workflow template
results = workflow.execute_template_workflow(
    template_name="quick_review",
    input_data="Your analysis data here",
    track_costs=True
)

# Print results
for persona, result in results["results"].items():
    print(f"Persona: {result['persona_name']}")
    print(f"Analysis: {result['analysis']}")
```

## Integrating Your Manager's Existing Prompts

### Option 1: YAML Configuration File

Create a `personas_config.yaml` file:

```yaml
personas:
  risk_assessment:
    name: "Risk Assessment Specialist"
    description: "Analyzes potential risks and their impact"
    prompt_template: |
      You are a Risk Assessment Specialist with expertise in identifying and evaluating potential risks.
      
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
      - Priority Ranking
    output_format: "structured_analysis"
    temperature: 0.1
    required_inputs: ["input", "context"]
  
  claims_analysis:
    name: "Claims Analysis Expert"
    description: "Reviews and analyzes claims for validity and processing"
    prompt_template: |
      [Your manager's existing claims analysis prompt here]
      Context from previous analysis: {context}
      Claims information to analyze: {input}
    output_format: "structured_analysis"
    temperature: 0.1
```

### Option 2: Programmatic Addition

```python
from advanced_persona_workflow import AdvancedPersonaWorkflow, PersonaConfig, OutputFormat

workflow = AdvancedPersonaWorkflow(openai_api_key="your-api-key-here")

# Add your manager's existing persona
custom_persona = PersonaConfig(
    name="Custom Claims Analyst",
    description="Your custom description",
    prompt_template="""Your manager's existing prompt template here.
    
    Context from previous analysis: {context}
    Information to analyze: {input}
    
    [Rest of your prompt]""",
    output_format=OutputFormat.STRUCTURED_ANALYSIS,
    temperature=0.1
)

workflow.add_persona("custom_claims", custom_persona)
```

## Workflow Templates

### Available Templates:
- **full_analysis**: Complete analysis with all personas
- **quick_review**: Risk + Claims + Summary
- **compliance_focus**: Compliance + Risk + Summary
- **financial_focus**: Financial + Risk + Summary

### Custom Workflow Sequences:

```python
# Define your own sequence
custom_sequence = [
    "risk_assessment",
    "claims_analysis",
    "summary_only"
]

results = workflow.execute_workflow(
    input_data="Your data",
    persona_sequence=custom_sequence,
    track_costs=True
)
```

## Advanced Features

### Cost Tracking

```python
results = workflow.execute_template_workflow(
    template_name="full_analysis",
    input_data="Your data",
    track_costs=True
)

print(f"Total cost: ${results['total_cost']:.4f}")
```

### Export Results

```python
# Export to JSON
json_export = workflow.export_results(results, "json")
with open("results.json", "w") as f:
    f.write(json_export)

# Export to YAML
yaml_export = workflow.export_results(results, "yaml")
with open("results.yaml", "w") as f:
    f.write(yaml_export)
```

### Workflow Validation

```python
# Validate before execution
issues = workflow.validate_workflow(["risk_assessment", "unknown_persona"])
if issues:
    print(f"Validation issues: {issues}")
```

## Best Practices

### 1. Prompt Design
- Use `{context}` placeholder to reference previous analyses
- Use `{input}` placeholder for the original data
- Structure prompts for consistent output formats
- Include clear instructions for each persona's role

### 2. Workflow Design
- Start with risk assessment for most workflows
- End with summary for executive consumption
- Consider persona dependencies (e.g., financial analysis after claims)
- Use appropriate templates for different use cases

### 3. Cost Optimization
- Use `track_costs=True` during development
- Monitor token usage per persona
- Consider using different models for different personas
- Implement caching for repeated analyses

### 4. Error Handling
- Validate workflows before execution
- Implement retry logic for API failures
- Handle context length limitations
- Monitor for prompt injection attempts

## Example Use Cases

### Insurance Claims Processing
```python
# Full claims analysis workflow
results = workflow.execute_template_workflow(
    template_name="full_analysis",
    input_data=claim_data,
    track_costs=True
)
```

### Compliance Reviews
```python
# Compliance-focused workflow
results = workflow.execute_template_workflow(
    template_name="compliance_focus",
    input_data=compliance_data,
    track_costs=True
)
```

### Financial Analysis
```python
# Financial analysis workflow
results = workflow.execute_template_workflow(
    template_name="financial_focus",
    input_data=financial_data,
    track_costs=True
)
```

## Troubleshooting

### Common Issues:

1. **API Key Issues**
   ```python
   # Ensure your API key is set
   import os
   os.environ["OPENAI_API_KEY"] = "your-key-here"
   ```

2. **Context Length Limits**
   - Monitor context size in workflow results
   - Consider truncating previous analyses
   - Use summary personas to compress context

3. **Prompt Template Errors**
   - Ensure all placeholders (`{input}`, `{context}`) are present
   - Check for proper YAML/JSON formatting
   - Validate prompt templates before execution

## Future Enhancements

- **Agent Evolution**: Convert personas to full LangChain agents
- **Parallel Execution**: Run independent personas in parallel
- **Conditional Workflows**: Dynamic persona selection based on input
- **Integration APIs**: Connect to external data sources
- **UI Interface**: Web-based workflow builder
- **Advanced Memory**: Long-term memory across sessions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
