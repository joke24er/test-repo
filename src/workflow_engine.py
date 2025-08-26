from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
import json
import uuid
from datetime import datetime

from .models import Persona, PersonaType, Workflow, AnalysisResult, DocumentInput
from .personas import persona_manager


class WorkflowState:
    """State object for the workflow execution"""
    def __init__(self, document: DocumentInput, personas: List[Persona], user_id: str):
        self.document = document
        self.personas = personas
        self.user_id = user_id
        self.results = {}
        self.current_persona = None
        self.errors = []
        self.metadata = {
            "start_time": datetime.now().isoformat(),
            "total_personas": len(personas),
            "completed_personas": 0
        }


class WorkflowEngine:
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.workflows: Dict[str, Workflow] = {}
        self.analysis_results: Dict[str, AnalysisResult] = {}
    
    def create_workflow(self, name: str, description: str, 
                       persona_ids: List[str], created_by: str) -> Workflow:
        """Create a new workflow with selected personas"""
        personas = []
        for persona_id in persona_ids:
            persona = persona_manager.get_persona_by_id(persona_id)
            if persona:
                personas.append(persona)
        
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            personas=personas,
            created_by=created_by,
            created_at=datetime.now().isoformat()
        )
        
        self.workflows[workflow.id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Workflow:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        """Get all workflows"""
        return list(self.workflows.values())
    
    def _create_persona_node(self, persona: Persona):
        """Create a LangGraph node for a specific persona"""
        
        def persona_analysis(state: WorkflowState) -> WorkflowState:
            try:
                state.current_persona = persona
                
                if persona.persona_type == PersonaType.PROMPT:
                    # Simple prompt-based analysis
                    result = self._execute_prompt_analysis(persona, state.document)
                else:
                    # Agent-based analysis with more complex logic
                    result = self._execute_agent_analysis(persona, state.document)
                
                state.results[persona.id] = result
                state.metadata["completed_personas"] += 1
                
            except Exception as e:
                state.errors.append(f"Error in {persona.name}: {str(e)}")
            
            return state
        
        return persona_analysis
    
    def _execute_prompt_analysis(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Execute prompt-based analysis"""
        prompt = PromptTemplate(
            input_variables=["document_content"],
            template=persona.prompt_template
        )
        
        formatted_prompt = prompt.format(document_content=document.content)
        
        messages = [
            SystemMessage(content="You are an expert document analyst. Provide detailed, structured analysis."),
            HumanMessage(content=formatted_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            "persona_name": persona.name,
            "persona_type": persona.persona_type.value,
            "analysis": response.content,
            "analysis_focus": persona.analysis_focus,
            "timestamp": datetime.now().isoformat()
        }
    
    def _execute_agent_analysis(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Execute agent-based analysis with more sophisticated logic"""
        
        # Create a more complex analysis based on persona type
        if "Contract Review" in persona.name:
            return self._contract_review_agent(persona, document)
        elif "Financial Analyst" in persona.name:
            return self._financial_analysis_agent(persona, document)
        elif "Risk Management" in persona.name:
            return self._risk_analysis_agent(persona, document)
        elif "Market Intelligence" in persona.name:
            return self._market_analysis_agent(persona, document)
        else:
            # Fallback to prompt-based analysis
            return self._execute_prompt_analysis(persona, document)
    
    def _contract_review_agent(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Specialized contract review agent"""
        contract_prompt = f"""
        As a senior contract review specialist, perform a comprehensive analysis of this contract:
        
        {document.content}
        
        Provide your analysis in the following JSON format:
        {{
            "key_terms": {{
                "parties": "identified parties",
                "effective_date": "contract effective date",
                "termination_date": "contract termination date",
                "key_obligations": ["list of key obligations"]
            }},
            "risk_assessment": {{
                "high_risks": ["list of high-risk items"],
                "medium_risks": ["list of medium-risk items"],
                "low_risks": ["list of low-risk items"]
            }},
            "compliance_issues": ["list of compliance concerns"],
            "recommendations": ["list of recommendations"],
            "summary": "executive summary of findings"
        }}
        """
        
        messages = [
            SystemMessage(content="You are a contract review specialist. Respond with valid JSON only."),
            HumanMessage(content=contract_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            analysis_data = json.loads(response.content)
        except:
            analysis_data = {"raw_analysis": response.content}
        
        return {
            "persona_name": persona.name,
            "persona_type": persona.persona_type.value,
            "analysis": analysis_data,
            "analysis_focus": persona.analysis_focus,
            "timestamp": datetime.now().isoformat()
        }
    
    def _financial_analysis_agent(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Specialized financial analysis agent"""
        financial_prompt = f"""
        As a certified financial analyst, analyze this financial document:
        
        {document.content}
        
        Provide your analysis in the following JSON format:
        {{
            "financial_ratios": {{
                "liquidity_ratios": {{"current_ratio": "value", "quick_ratio": "value"}},
                "profitability_ratios": {{"gross_margin": "value", "net_margin": "value"}},
                "efficiency_ratios": {{"asset_turnover": "value", "inventory_turnover": "value"}}
            }},
            "trend_analysis": ["key trends identified"],
            "cash_flow_analysis": {{
                "operating_cash_flow": "analysis",
                "investing_cash_flow": "analysis",
                "financing_cash_flow": "analysis"
            }},
            "risk_assessment": ["financial risks identified"],
            "investment_insights": ["investment recommendations"]
        }}
        """
        
        messages = [
            SystemMessage(content="You are a financial analyst. Respond with valid JSON only."),
            HumanMessage(content=financial_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            analysis_data = json.loads(response.content)
        except:
            analysis_data = {"raw_analysis": response.content}
        
        return {
            "persona_name": persona.name,
            "persona_type": persona.persona_type.value,
            "analysis": analysis_data,
            "analysis_focus": persona.analysis_focus,
            "timestamp": datetime.now().isoformat()
        }
    
    def _risk_analysis_agent(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Specialized risk analysis agent"""
        risk_prompt = f"""
        As a risk management specialist, perform a comprehensive risk assessment:
        
        {document.content}
        
        Provide your analysis in the following JSON format:
        {{
            "risk_matrix": {{
                "high_probability_high_impact": ["risks"],
                "high_probability_low_impact": ["risks"],
                "low_probability_high_impact": ["risks"],
                "low_probability_low_impact": ["risks"]
            }},
            "risk_categories": {{
                "operational_risks": ["list"],
                "financial_risks": ["list"],
                "strategic_risks": ["list"],
                "compliance_risks": ["list"]
            }},
            "mitigation_strategies": ["strategies"],
            "monitoring_plan": ["monitoring activities"]
        }}
        """
        
        messages = [
            SystemMessage(content="You are a risk management specialist. Respond with valid JSON only."),
            HumanMessage(content=risk_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            analysis_data = json.loads(response.content)
        except:
            analysis_data = {"raw_analysis": response.content}
        
        return {
            "persona_name": persona.name,
            "persona_type": persona.persona_type.value,
            "analysis": analysis_data,
            "analysis_focus": persona.analysis_focus,
            "timestamp": datetime.now().isoformat()
        }
    
    def _market_analysis_agent(self, persona: Persona, document: DocumentInput) -> Dict[str, Any]:
        """Specialized market analysis agent"""
        market_prompt = f"""
        As a market intelligence analyst, analyze this document for market insights:
        
        {document.content}
        
        Provide your analysis in the following JSON format:
        {{
            "market_position": {{
                "current_position": "description",
                "competitive_advantages": ["list"],
                "competitive_threats": ["list"]
            }},
            "market_trends": ["key trends"],
            "opportunities": ["market opportunities"],
            "strategic_recommendations": ["recommendations"]
        }}
        """
        
        messages = [
            SystemMessage(content="You are a market intelligence analyst. Respond with valid JSON only."),
            HumanMessage(content=market_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            analysis_data = json.loads(response.content)
        except:
            analysis_data = {"raw_analysis": response.content}
        
        return {
            "persona_name": persona.name,
            "persona_type": persona.persona_type.value,
            "analysis": analysis_data,
            "analysis_focus": persona.analysis_focus,
            "timestamp": datetime.now().isoformat()
        }
    
    def execute_workflow(self, workflow_id: str, document: DocumentInput, user_id: str) -> AnalysisResult:
        """Execute a workflow with the given document"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create workflow state
        state = WorkflowState(document, workflow.personas, user_id)
        
        # Build the workflow graph
        workflow_graph = StateGraph(WorkflowState)
        
        # Add nodes for each persona
        for persona in workflow.personas:
            workflow_graph.add_node(persona.id, self._create_persona_node(persona))
        
        # Set entry point to first persona
        if workflow.personas:
            workflow_graph.set_entry_point(workflow.personas[0].id)
        
        # Connect personas in sequence
        for i in range(len(workflow.personas) - 1):
            current_persona = workflow.personas[i]
            next_persona = workflow.personas[i + 1]
            workflow_graph.add_edge(current_persona.id, next_persona.id)
        
        # Set end point
        if workflow.personas:
            workflow_graph.add_edge(workflow.personas[-1].id, END)
        
        # Compile and run the workflow
        compiled_graph = workflow_graph.compile()
        final_state = compiled_graph.invoke(state)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            document_name=document.filename,
            analysis_content=final_state.results,
            persona_results={persona.id: result.get("analysis", "") 
                           for persona, result in final_state.results.items()},
            metadata={
                **final_state.metadata,
                "end_time": datetime.now().isoformat(),
                "errors": final_state.errors,
                "user_id": user_id
            },
            created_at=datetime.now().isoformat()
        )
        
        self.analysis_results[analysis_result.id] = analysis_result
        return analysis_result
    
    def get_analysis_result(self, analysis_id: str) -> AnalysisResult:
        """Get an analysis result by ID"""
        return self.analysis_results.get(analysis_id)
    
    def get_user_analyses(self, user_id: str) -> List[AnalysisResult]:
        """Get all analyses for a user"""
        return [result for result in self.analysis_results.values() 
                if result.metadata.get("user_id") == user_id]


# Global workflow engine instance
workflow_engine = WorkflowEngine()