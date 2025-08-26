from typing import List, Dict
import uuid
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from .simplified_models import AnalysisResult, ChatMessage
from .simplified_workflow import workflow_engine
from .simplified_personas import persona_manager


class SimpleChatSystem:
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.7)
        self.chat_history: Dict[str, List[ChatMessage]] = {}
    
    def _build_context(self, analysis_result: AnalysisResult) -> str:
        """Build simple context from analysis results"""
        workflow = workflow_engine.get_workflow(analysis_result.workflow_id)
        
        context_parts = [f"Document: {analysis_result.document_name}"]
        
        if workflow:
            context_parts.append(f"Workflow: {workflow.name}")
            context_parts.append("Analysis Results:")
            
            for persona_id, result in analysis_result.results.items():
                persona = persona_manager.get_persona_by_id(persona_id)
                persona_name = persona.name if persona else "Unknown"
                context_parts.append(f"\n{persona_name}: {result}")
        
        return "\n".join(context_parts)
    
    def send_message(self, analysis_id: str, message: str, user_id: str = "default") -> ChatMessage:
        """Send a message and get response"""
        analysis_result = workflow_engine.get_analysis_result(analysis_id)
        if not analysis_result:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        # Build simple context
        context = self._build_context(analysis_result)
        
        # Create system message
        system_message = f"""You are an AI assistant helping a user understand their document analysis results.

Analysis Context:
{context}

Help the user understand the results, answer questions, and provide insights. Be conversational and helpful."""

        # Get response
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=message)
        ]
        
        response = self.llm.invoke(messages)
        
        # Create chat message
        chat_message = ChatMessage(
            analysis_id=analysis_id,
            message=message,
            response=response.content,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in history
        if analysis_id not in self.chat_history:
            self.chat_history[analysis_id] = []
        self.chat_history[analysis_id].append(chat_message)
        
        return chat_message
    
    def get_chat_history(self, analysis_id: str) -> List[ChatMessage]:
        """Get chat history for an analysis"""
        return self.chat_history.get(analysis_id, [])
    
    def clear_chat_history(self, analysis_id: str) -> bool:
        """Clear chat history for an analysis"""
        if analysis_id in self.chat_history:
            del self.chat_history[analysis_id]
            return True
        return False


# Global instance
chat_system = SimpleChatSystem()