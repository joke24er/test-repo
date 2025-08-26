from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
import json
import uuid
from datetime import datetime

from .models import AnalysisResult, ChatMessage, ChatRequest
from .workflow_engine import workflow_engine


class ChatSystem:
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0.7)
        self.conversation_memories: Dict[str, ConversationBufferMemory] = {}
        self.chat_history: Dict[str, List[ChatMessage]] = {}
    
    def _create_context_prompt(self, analysis_result: AnalysisResult) -> str:
        """Create a context prompt from analysis results"""
        context_parts = []
        
        # Add workflow information
        workflow = workflow_engine.get_workflow(analysis_result.workflow_id)
        if workflow:
            context_parts.append(f"Workflow: {workflow.name}")
            context_parts.append(f"Description: {workflow.description}")
            context_parts.append("Personas used:")
            for persona in workflow.personas:
                context_parts.append(f"- {persona.name}: {persona.description}")
        
        # Add analysis results
        context_parts.append("\nAnalysis Results:")
        for persona_id, result in analysis_result.analysis_content.items():
            persona_name = result.get("persona_name", "Unknown")
            analysis_content = result.get("analysis", "")
            
            if isinstance(analysis_content, dict):
                # Format JSON analysis nicely
                formatted_analysis = json.dumps(analysis_content, indent=2)
            else:
                formatted_analysis = str(analysis_content)
            
            context_parts.append(f"\n{persona_name} Analysis:")
            context_parts.append(formatted_analysis)
        
        return "\n".join(context_parts)
    
    def _get_conversation_memory(self, analysis_id: str) -> ConversationBufferMemory:
        """Get or create conversation memory for an analysis"""
        if analysis_id not in self.conversation_memories:
            self.conversation_memories[analysis_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        return self.conversation_memories[analysis_id]
    
    def send_message(self, chat_request: ChatRequest) -> ChatMessage:
        """Send a message and get response for a specific analysis"""
        analysis_result = workflow_engine.get_analysis_result(chat_request.analysis_id)
        if not analysis_result:
            raise ValueError(f"Analysis {chat_request.analysis_id} not found")
        
        # Get conversation memory
        memory = self._get_conversation_memory(chat_request.analysis_id)
        
        # Create context from analysis
        context = self._create_context_prompt(analysis_result)
        
        # Create system message with context
        system_message = f"""You are an AI assistant helping a user understand and explore their document analysis results.

The user has run a document analysis workflow with the following results:

{context}

Your role is to:
1. Help the user understand the analysis results
2. Answer questions about specific findings
3. Provide additional insights based on the analysis
4. Help interpret complex findings
5. Suggest follow-up actions or additional analysis

Be conversational, helpful, and provide detailed explanations when needed. If the user asks about something not covered in the analysis, let them know and suggest how they might get that information.

Previous conversation context:
{memory.buffer if memory.buffer else "This is the start of the conversation."}"""
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=chat_request.message)
        ]
        
        # Get response from LLM
        response = self.llm.invoke(messages)
        
        # Create chat message
        chat_message = ChatMessage(
            id=str(uuid.uuid4()),
            analysis_id=chat_request.analysis_id,
            user_message=chat_request.message,
            assistant_response=response.content,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in memory
        memory.chat_memory.add_user_message(chat_request.message)
        memory.chat_memory.add_ai_message(response.content)
        
        # Store in chat history
        if chat_request.analysis_id not in self.chat_history:
            self.chat_history[chat_request.analysis_id] = []
        self.chat_history[chat_request.analysis_id].append(chat_message)
        
        return chat_message
    
    def get_chat_history(self, analysis_id: str) -> List[ChatMessage]:
        """Get chat history for a specific analysis"""
        return self.chat_history.get(analysis_id, [])
    
    def clear_chat_history(self, analysis_id: str) -> bool:
        """Clear chat history for a specific analysis"""
        if analysis_id in self.chat_history:
            del self.chat_history[analysis_id]
        if analysis_id in self.conversation_memories:
            del self.conversation_memories[analysis_id]
        return True
    
    def get_analysis_summary(self, analysis_id: str) -> Dict[str, Any]:
        """Get a summary of the analysis with key insights"""
        analysis_result = workflow_engine.get_analysis_result(analysis_id)
        if not analysis_result:
            raise ValueError(f"Analysis {analysis_id} not found")
        
        summary_prompt = f"""Based on the following analysis results, provide a concise summary with key insights:

{self._create_context_prompt(analysis_result)}

Provide the summary in JSON format with the following structure:
{{
    "executive_summary": "Brief overview of key findings",
    "key_insights": ["list of most important insights"],
    "critical_findings": ["list of critical findings that need attention"],
    "recommendations": ["list of actionable recommendations"],
    "risk_level": "overall risk assessment (low/medium/high)",
    "next_steps": ["suggested next steps"]
}}"""
        
        messages = [
            SystemMessage(content="You are an expert analyst. Provide a structured summary in JSON format."),
            HumanMessage(content=summary_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            summary_data = json.loads(response.content)
        except:
            summary_data = {
                "executive_summary": "Analysis completed successfully",
                "key_insights": ["Analysis results available for review"],
                "critical_findings": [],
                "recommendations": ["Review the detailed analysis results"],
                "risk_level": "unknown",
                "next_steps": ["Engage with the analysis through chat"]
            }
        
        return {
            "analysis_id": analysis_id,
            "document_name": analysis_result.document_name,
            "workflow_id": analysis_result.workflow_id,
            "created_at": analysis_result.created_at,
            "summary": summary_data
        }
    
    def get_comparative_analysis(self, analysis_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple analyses and provide insights"""
        if len(analysis_ids) < 2:
            raise ValueError("At least 2 analysis IDs required for comparison")
        
        analyses = []
        for analysis_id in analysis_ids:
            analysis_result = workflow_engine.get_analysis_result(analysis_id)
            if analysis_result:
                analyses.append(analysis_result)
        
        if len(analyses) < 2:
            raise ValueError("Could not find at least 2 valid analyses for comparison")
        
        # Create comparison context
        comparison_context = "Comparing the following analyses:\n\n"
        for i, analysis in enumerate(analyses, 1):
            comparison_context += f"Analysis {i}:\n"
            comparison_context += f"Document: {analysis.document_name}\n"
            comparison_context += f"Workflow: {workflow_engine.get_workflow(analysis.workflow_id).name if workflow_engine.get_workflow(analysis.workflow_id) else 'Unknown'}\n"
            comparison_context += f"Results: {json.dumps(analysis.analysis_content, indent=2)}\n\n"
        
        comparison_prompt = f"""Compare the following analyses and provide insights:

{comparison_context}

Provide the comparison in JSON format with the following structure:
{{
    "overview": "Brief comparison overview",
    "similarities": ["key similarities between analyses"],
    "differences": ["key differences between analyses"],
    "trends": ["any trends or patterns identified"],
    "insights": ["comparative insights"],
    "recommendations": ["recommendations based on comparison"]
}}"""
        
        messages = [
            SystemMessage(content="You are an expert analyst. Provide a structured comparison in JSON format."),
            HumanMessage(content=comparison_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        try:
            comparison_data = json.loads(response.content)
        except:
            comparison_data = {
                "overview": "Multiple analyses compared",
                "similarities": ["All analyses completed successfully"],
                "differences": ["Different documents and workflows analyzed"],
                "trends": ["No clear trends identified"],
                "insights": ["Each analysis provides unique insights"],
                "recommendations": ["Review each analysis individually"]
            }
        
        return {
            "analysis_ids": analysis_ids,
            "comparison": comparison_data,
            "timestamp": datetime.now().isoformat()
        }


# Global chat system instance
chat_system = ChatSystem()