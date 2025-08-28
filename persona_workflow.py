from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from typing import List, Dict, Any
import json

class Persona:
    def __init__(self, name: str, system_prompt: str, description: str):
        self.name = name
        self.system_prompt = system_prompt
        self.description = description
        self.llm = ChatOpenAI(temperature=0.1)
        self.memory = ConversationBufferMemory(return_messages=True)
    
    def process(self, input_text: str, context: Dict[str, Any] = None) -> str:
        """Process input through this persona"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=input_text)
        ]
        
        if context:
            # Add context from previous personas
            context_str = json.dumps(context, indent=2)
            messages.append(SystemMessage(content=f"Previous context: {context_str}"))
        
        response = self.llm(messages)
        return response.content

class WorkflowEngine:
    def __init__(self):
        self.personas = {}
        self.workflow_history = []
        self.chat_memory = ConversationBufferMemory(return_messages=True)
    
    def add_persona(self, persona: Persona):
        """Add a persona to the workflow engine"""
        self.personas[persona.name] = persona
    
    def execute_workflow(self, input_text: str, persona_sequence: List[str]) -> Dict[str, Any]:
        """Execute a workflow with the specified persona sequence"""
        results = {}
        context = {}
        
        for persona_name in persona_sequence:
            if persona_name not in self.personas:
                raise ValueError(f"Persona '{persona_name}' not found")
            
            persona = self.personas[persona_name]
            
            # Process through current persona
            output = persona.process(input_text, context)
            results[persona_name] = output
            
            # Update context for next persona
            context[persona_name] = output
            
            # Store in workflow history
            self.workflow_history.append({
                'persona': persona_name,
                'input': input_text,
                'output': output,
                'context': context.copy()
            })
        
        return results
    
    def chat_with_output(self, message: str, workflow_results: Dict[str, Any]) -> str:
        """Allow user to chat with the workflow results"""
        # Create a context-aware prompt for chatting
        context_str = json.dumps(workflow_results, indent=2)
        
        chat_prompt = f"""You are an AI assistant helping the user understand and discuss the results from a multi-persona workflow analysis.

Workflow Results:
{context_str}

User Question: {message}

Please provide a helpful response based on the workflow results above. If the user asks about specific personas or their outputs, reference the relevant sections."""
        
        messages = [
            SystemMessage(content=chat_prompt),
            HumanMessage(content=message)
        ]
        
        # Add conversation history
        if self.chat_memory.chat_memory.messages:
            messages = self.chat_memory.chat_memory.messages + messages
        
        llm = ChatOpenAI(temperature=0.7)
        response = llm(messages)
        
        # Update memory
        self.chat_memory.chat_memory.add_user_message(message)
        self.chat_memory.chat_memory.add_ai_message(response.content)
        
        return response.content

# Example usage and persona definitions
def create_default_personas():
    """Create the default personas based on your requirements"""
    personas = {
        "Risk Assessment": Persona(
            name="Risk Assessment",
            system_prompt="""You are a Risk Assessment specialist. Analyze the provided information for potential risks, 
            vulnerabilities, and risk factors. Provide a structured risk assessment with likelihood and impact ratings.""",
            description="Identifies and evaluates potential risks in the given context"
        ),
        
        "Claims Analysis": Persona(
            name="Claims Analysis",
            system_prompt="""You are a Claims Analysis expert. Review and analyze claims-related information, 
            identify patterns, validate claims, and provide insights on claim processing and fraud detection.""",
            description="Analyzes claims data and identifies patterns or anomalies"
        ),
        
        "Compliance Review": Persona(
            name="Compliance Review",
            system_prompt="""You are a Compliance Review specialist. Evaluate the provided information against 
            relevant regulations, policies, and compliance requirements. Identify compliance gaps and recommendations.""",
            description="Ensures adherence to regulatory and policy requirements"
        ),
        
        "Financial Analysis": Persona(
            name="Financial Analysis",
            system_prompt="""You are a Financial Analysis expert. Analyze financial data, trends, and metrics. 
            Provide insights on financial performance, ratios, and recommendations for financial optimization.""",
            description="Analyzes financial data and provides insights"
        ),
        
        "Operational Excellence": Persona(
            name="Operational Excellence",
            system_prompt="""You are an Operational Excellence specialist. Evaluate operational processes, 
            identify inefficiencies, and provide recommendations for process improvement and optimization.""",
            description="Focuses on operational efficiency and process improvement"
        ),
        
        "Summary Only": Persona(
            name="Summary Only",
            system_prompt="""You are a Summary specialist. Create concise, well-structured summaries of the provided information. 
            Focus on key points, findings, and actionable insights.""",
            description="Creates concise summaries of complex information"
        )
    }
    
    return personas

# Example workflow execution
def example_usage():
    # Initialize workflow engine
    engine = WorkflowEngine()
    
    # Add personas
    personas = create_default_personas()
    for persona in personas.values():
        engine.add_persona(persona)
    
    # Example input
    input_text = """
    Customer XYZ has filed a claim for $50,000 due to property damage. 
    The incident occurred on 2024-01-15. Initial assessment shows moderate damage.
    Customer has been with us for 3 years with no previous claims.
    """
    
    # Execute workflow with multiple personas
    persona_sequence = ["Risk Assessment", "Claims Analysis", "Compliance Review", "Summary Only"]
    results = engine.execute_workflow(input_text, persona_sequence)
    
    print("Workflow Results:")
    for persona, output in results.items():
        print(f"\n{persona}:")
        print(output)
    
    # Chat with the results
    chat_response = engine.chat_with_output(
        "What are the main risks identified in this claim?", 
        results
    )
    print(f"\nChat Response: {chat_response}")

if __name__ == "__main__":
    example_usage()