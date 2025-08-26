from typing import List, Dict
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .simplified_models import Workflow, AnalysisResult, DocumentInput
from .simplified_personas import persona_manager


class SimpleWorkflowEngine:
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.1)
        self.workflows: Dict[str, Workflow] = {}
        self.analysis_results: Dict[str, AnalysisResult] = {}
    
    def create_workflow(self, name: str, description: str, 
                       persona_ids: List[str], created_by: str) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            persona_ids=persona_ids,
            created_by=created_by,
            created_at=datetime.now().isoformat()
        )
        
        self.workflows[workflow.id] = workflow
        return workflow
    
    def get_workflow(self, workflow_id: str) -> Workflow:
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Workflow]:
        return list(self.workflows.values())
    
    def _analyze_with_persona(self, persona, document_content: str) -> str:
        """Simple analysis using a persona's prompt template"""
        prompt = persona.prompt_template.format(content=document_content)
        
        messages = [
            SystemMessage(content="You are an expert document analyst. Provide clear, structured analysis."),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def execute_workflow(self, workflow_id: str, document: DocumentInput, user_id: str) -> AnalysisResult:
        """Execute a workflow - simplified sequential processing"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        results = {}
        
        # Simple sequential processing - no complex state management
        for persona_id in workflow.persona_ids:
            persona = persona_manager.get_persona_by_id(persona_id)
            if persona:
                try:
                    analysis_result = self._analyze_with_persona(persona, document.content)
                    results[persona_id] = analysis_result
                except Exception as e:
                    results[persona_id] = f"Error: {str(e)}"
        
        # Create analysis result
        analysis_result = AnalysisResult(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            document_name=document.filename,
            results=results,
            created_at=datetime.now().isoformat()
        )
        
        self.analysis_results[analysis_result.id] = analysis_result
        return analysis_result
    
    def get_analysis_result(self, analysis_id: str) -> AnalysisResult:
        return self.analysis_results.get(analysis_id)
    
    def get_user_analyses(self, user_id: str) -> List[AnalysisResult]:
        # Simplified - no user tracking in this version
        return list(self.analysis_results.values())


# Global instance
workflow_engine = SimpleWorkflowEngine()