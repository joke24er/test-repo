import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

@dataclass
class PersonaConfig:
    name: str
    description: str
    prompt_template: str
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    parallel_processing: bool = False

class PersonaOutput(BaseModel):
    analysis: str = Field(description="The main analysis output")
    confidence: float = Field(description="Confidence score 0-1")
    key_findings: List[str] = Field(description="List of key findings")
    recommendations: List[str] = Field(description="List of recommendations")

class AdvancedPersona:
    def __init__(self, config: PersonaConfig):
        self.config = config
        self.llm = ChatOpenAI(
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_template(config.prompt_template)
        
        # Create output parser
        self.output_parser = PydanticOutputParser(pydantic_object=PersonaOutput)
    
    async def process_async(self, input_text: str, context: Dict[str, Any] = None) -> PersonaOutput:
        """Process input asynchronously through this persona"""
        messages = self.prompt_template.format_messages(
            input_text=input_text,
            context=json.dumps(context, indent=2) if context else "{}"
        )
        
        response = await self.llm.agenerate([messages])
        content = response.generations[0][0].text
        
        try:
            # Try to parse as structured output
            return self.output_parser.parse(content)
        except:
            # Fallback to simple text output
            return PersonaOutput(
                analysis=content,
                confidence=0.8,
                key_findings=[content[:100] + "..."],
                recommendations=[]
            )
    
    def process(self, input_text: str, context: Dict[str, Any] = None) -> PersonaOutput:
        """Process input synchronously through this persona"""
        return asyncio.run(self.process_async(input_text, context))

class AdvancedWorkflowEngine:
    def __init__(self):
        self.personas = {}
        self.workflow_history = []
        self.chat_memory = ConversationBufferMemory(return_messages=True)
        self.llm = ChatOpenAI(temperature=0.7)
    
    def load_personas_from_config(self, config_file: str):
        """Load personas from a configuration file"""
        with open(config_file, 'r') as f:
            configs = json.load(f)
        
        for config_data in configs:
            config = PersonaConfig(**config_data)
            persona = AdvancedPersona(config)
            self.personas[config.name] = persona
    
    def load_personas_from_prompts_directory(self, prompts_dir: str):
        """Load personas from a directory containing prompt files"""
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.txt') or filename.endswith('.md'):
                persona_name = filename.replace('.txt', '').replace('.md', '')
                
                with open(os.path.join(prompts_dir, filename), 'r') as f:
                    prompt_template = f.read()
                
                config = PersonaConfig(
                    name=persona_name,
                    description=f"Persona loaded from {filename}",
                    prompt_template=prompt_template
                )
                
                persona = AdvancedPersona(config)
                self.personas[persona_name] = persona
    
    async def execute_workflow_async(self, input_text: str, persona_sequence: List[str]) -> Dict[str, PersonaOutput]:
        """Execute workflow asynchronously, allowing parallel processing where possible"""
        results = {}
        context = {}
        
        # Group personas by processing type
        parallel_personas = []
        sequential_personas = []
        
        for persona_name in persona_sequence:
            if persona_name not in self.personas:
                raise ValueError(f"Persona '{persona_name}' not found")
            
            persona = self.personas[persona_name]
            if persona.config.parallel_processing:
                parallel_personas.append(persona_name)
            else:
                sequential_personas.append(persona_name)
        
        # Process parallel personas first
        if parallel_personas:
            tasks = []
            for persona_name in parallel_personas:
                persona = self.personas[persona_name]
                task = persona.process_async(input_text, context)
                tasks.append((persona_name, task))
            
            # Execute parallel tasks
            for persona_name, task in tasks:
                output = await task
                results[persona_name] = output
                context[persona_name] = output
        
        # Process sequential personas
        for persona_name in sequential_personas:
            persona = self.personas[persona_name]
            output = await persona.process_async(input_text, context)
            results[persona_name] = output
            context[persona_name] = output
            
            # Store in workflow history
            self.workflow_history.append({
                'persona': persona_name,
                'input': input_text,
                'output': output.dict(),
                'context': context.copy()
            })
        
        return results
    
    def execute_workflow(self, input_text: str, persona_sequence: List[str]) -> Dict[str, PersonaOutput]:
        """Execute workflow synchronously"""
        return asyncio.run(self.execute_workflow_async(input_text, persona_sequence))
    
    def chat_with_output(self, message: str, workflow_results: Dict[str, PersonaOutput]) -> str:
        """Enhanced chat functionality with structured outputs"""
        # Convert PersonaOutput objects to readable format
        readable_results = {}
        for persona_name, output in workflow_results.items():
            readable_results[persona_name] = {
                'analysis': output.analysis,
                'confidence': output.confidence,
                'key_findings': output.key_findings,
                'recommendations': output.recommendations
            }
        
        context_str = json.dumps(readable_results, indent=2)
        
        chat_prompt = f"""You are an AI assistant helping the user understand and discuss the results from a multi-persona workflow analysis.

Workflow Results:
{context_str}

User Question: {message}

Please provide a helpful response based on the workflow results above. If the user asks about specific personas or their outputs, reference the relevant sections. Be conversational and helpful."""

        messages = [
            SystemMessage(content=chat_prompt),
            HumanMessage(content=message)
        ]
        
        # Add conversation history
        if self.chat_memory.chat_memory.messages:
            messages = self.chat_memory.chat_memory.messages + messages
        
        response = self.llm(messages)
        
        # Update memory
        self.chat_memory.chat_memory.add_user_message(message)
        self.chat_memory.chat_memory.add_ai_message(response.content)
        
        return response.content
    
    def get_workflow_summary(self, workflow_results: Dict[str, PersonaOutput]) -> str:
        """Generate a summary of the workflow results"""
        summary_parts = []
        
        for persona_name, output in workflow_results.items():
            summary_parts.append(f"## {persona_name}")
            summary_parts.append(f"**Confidence:** {output.confidence:.2f}")
            summary_parts.append(f"**Analysis:** {output.analysis[:200]}...")
            summary_parts.append(f"**Key Findings:** {', '.join(output.key_findings[:3])}")
            if output.recommendations:
                summary_parts.append(f"**Recommendations:** {', '.join(output.recommendations[:3])}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)

# Example configuration file structure
def create_example_config():
    """Create an example configuration file for personas"""
    config = [
        {
            "name": "Risk Assessment",
            "description": "Identifies and evaluates potential risks",
            "prompt_template": """You are a Risk Assessment specialist. Analyze the provided information for potential risks, vulnerabilities, and risk factors.

Input: {input_text}
Previous Context: {context}

Provide a structured risk assessment with:
1. Risk identification
2. Likelihood and impact ratings
3. Risk mitigation strategies

Format your response as a structured analysis with clear sections.""",
            "temperature": 0.1,
            "parallel_processing": False
        },
        {
            "name": "Claims Analysis",
            "description": "Analyzes claims data and identifies patterns",
            "prompt_template": """You are a Claims Analysis expert. Review and analyze claims-related information.

Input: {input_text}
Previous Context: {context}

Focus on:
1. Claim validation
2. Pattern recognition
3. Fraud indicators
4. Processing recommendations

Provide detailed analysis with specific insights.""",
            "temperature": 0.1,
            "parallel_processing": True
        }
    ]
    
    with open('persona_config.json', 'w') as f:
        json.dump(config, f, indent=2)

# Example usage
def example_advanced_usage():
    # Create example config
    create_example_config()
    
    # Initialize workflow engine
    engine = AdvancedWorkflowEngine()
    
    # Load personas from config
    engine.load_personas_from_config('persona_config.json')
    
    # Example input
    input_text = """
    Customer ABC has submitted a claim for $75,000 for business interruption due to a fire incident.
    The incident occurred on 2024-02-01. The business has been closed for 3 weeks.
    Customer has 2 previous claims in the last 5 years, both for minor property damage.
    Initial investigation shows the fire was caused by electrical malfunction.
    """
    
    # Execute workflow
    persona_sequence = ["Risk Assessment", "Claims Analysis"]
    results = engine.execute_workflow(input_text, persona_sequence)
    
    print("Workflow Results:")
    for persona, output in results.items():
        print(f"\n{persona}:")
        print(f"Confidence: {output.confidence}")
        print(f"Analysis: {output.analysis}")
        print(f"Key Findings: {output.key_findings}")
        print(f"Recommendations: {output.recommendations}")
    
    # Generate summary
    summary = engine.get_workflow_summary(results)
    print(f"\nWorkflow Summary:\n{summary}")
    
    # Chat with results
    chat_response = engine.chat_with_output(
        "What are the main risks and what should we do about them?",
        results
    )
    print(f"\nChat Response: {chat_response}")

if __name__ == "__main__":
    example_advanced_usage()