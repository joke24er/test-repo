# Persona Workflow System

A sophisticated multi-persona workflow system built with LangChain that allows users to create custom workflows using specialized AI personas. Each persona is a glorified prompt template that can be chained together to provide comprehensive analysis.

## Features

- **Multi-Persona Workflows**: Chain multiple personas together in custom sequences
- **Context Awareness**: Each persona can access outputs from previous personas
- **Parallel Processing**: Support for parallel execution where appropriate
- **Structured Outputs**: Consistent, parseable outputs with confidence scores
- **Chat Interface**: Interactive chat with workflow results
- **Web Interface**: Beautiful, modern web UI for easy interaction
- **Flexible Configuration**: Load personas from config files or prompt directories

## Personas Included

1. **Risk Assessment** - Identifies and evaluates potential risks
2. **Claims Analysis** - Analyzes claims data and identifies patterns
3. **Compliance Review** - Ensures adherence to regulatory requirements
4. **Financial Analysis** - Analyzes financial data and provides insights
5. **Operational Excellence** - Focuses on operational efficiency
6. **Summary Only** - Creates concise summaries of complex information

## Why LangChain?

For your use case, LangChain is the better choice over direct API calls because:

1. **Workflow Orchestration**: Built-in support for complex multi-step workflows
2. **Memory Management**: Automatic context and conversation history management
3. **Prompt Management**: Better organization and templating of your existing prompts
4. **Observability**: Built-in tracing and monitoring capabilities
5. **Extensibility**: Easy to add new personas or modify existing ones
6. **Structured Outputs**: Better handling of complex, multi-format responses

## Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Set up your OpenAI API key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Run the web interface

```bash
python web_interface.py
```

Visit `http://localhost:8000` to access the web interface.

## Integrating Your Manager's Existing Prompts

### Option 1: Configuration File

Create a `persona_config.json` file:

```json
[
  {
    "name": "Risk Assessment",
    "description": "Your manager's risk assessment prompt",
    "prompt_template": "Your manager's existing prompt template here...",
    "temperature": 0.1,
    "parallel_processing": false
  }
]
```

### Option 2: Prompt Files Directory

Create a `prompts/` directory and add your manager's prompts as text files:

```
prompts/
├── Risk Assessment.txt
├── Claims Analysis.txt
├── Compliance Review.txt
└── ...
```

### Option 3: Direct Integration

Modify the `create_default_personas()` function in `persona_workflow.py`:

```python
def create_default_personas():
    return {
        "Risk Assessment": Persona(
            name="Risk Assessment",
            system_prompt="YOUR_MANAGER'S_PROMPT_HERE",
            description="Your description"
        ),
        # ... other personas
    }
```

## Usage Examples

### Basic Workflow Execution

```python
from persona_workflow import WorkflowEngine, create_default_personas

# Initialize engine
engine = WorkflowEngine()
personas = create_default_personas()
for persona in personas.values():
    engine.add_persona(persona)

# Execute workflow
input_text = "Your input text here..."
persona_sequence = ["Risk Assessment", "Claims Analysis", "Summary Only"]
results = engine.execute_workflow(input_text, persona_sequence)

# Chat with results
response = engine.chat_with_output("What are the main risks?", results)
```

### Advanced Workflow with Structured Outputs

```python
from advanced_workflow import AdvancedWorkflowEngine

# Initialize advanced engine
engine = AdvancedWorkflowEngine()

# Load from config file
engine.load_personas_from_config('persona_config.json')

# Execute workflow
results = engine.execute_workflow(input_text, persona_sequence)

# Access structured outputs
for persona_name, output in results.items():
    print(f"Confidence: {output.confidence}")
    print(f"Key Findings: {output.key_findings}")
    print(f"Recommendations: {output.recommendations}")
```

## Architecture Benefits

### 1. Sequential vs Parallel Processing

- **Sequential**: Personas that depend on previous outputs (e.g., Summary after Analysis)
- **Parallel**: Independent personas that can run simultaneously (e.g., Risk + Compliance)

### 2. Context Flow

```
Input → Persona 1 → Context → Persona 2 → Context → Persona 3 → Final Output
```

Each persona receives:
- Original input text
- Context from all previous personas
- Structured outputs for better understanding

### 3. Chat Integration

The chat system provides:
- Context-aware responses based on workflow results
- Conversation memory for follow-up questions
- Ability to reference specific persona outputs

## Customization

### Adding New Personas

1. **Simple Addition**:
```python
new_persona = Persona(
    name="Custom Analysis",
    system_prompt="Your custom prompt...",
    description="Description of what this persona does"
)
engine.add_persona(new_persona)
```

2. **Advanced Addition**:
```python
config = PersonaConfig(
    name="Custom Analysis",
    description="Custom analysis persona",
    prompt_template="Your template with {input_text} and {context}",
    temperature=0.2,
    parallel_processing=True
)
persona = AdvancedPersona(config)
engine.personas[config.name] = persona
```

### Modifying Existing Personas

```python
# Update prompt template
persona = engine.personas["Risk Assessment"]
persona.system_prompt = "Your updated prompt..."
```

## Best Practices

1. **Prompt Design**: Make prompts specific and include clear output formats
2. **Temperature Settings**: Use lower temperatures (0.1-0.3) for analysis, higher (0.7-0.9) for creative tasks
3. **Context Management**: Ensure personas can handle varying context sizes
4. **Error Handling**: Implement fallbacks for parsing failures
5. **Performance**: Use parallel processing for independent personas

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `OPENAI_API_KEY` environment variable is set
2. **Import Errors**: Install all requirements with `pip install -r requirements.txt`
3. **Prompt Parsing**: Check that your prompts use the correct template variables (`{input_text}`, `{context}`)

### Performance Optimization

- Use parallel processing for independent personas
- Implement caching for repeated workflows
- Consider using streaming for long-running personas

## Future Enhancements

- **Agent Integration**: Convert personas to full LangChain agents
- **Database Storage**: Persist workflow results and chat history
- **Advanced Analytics**: Add workflow performance metrics
- **Multi-Modal Support**: Handle images, documents, and other media types
- **API Endpoints**: RESTful API for integration with other systems

## Support

For questions or issues, please refer to the LangChain documentation or create an issue in the repository.
