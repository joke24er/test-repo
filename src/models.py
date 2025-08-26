from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


class PersonaType(str, Enum):
    PROMPT = "prompt"
    AGENT = "agent"


class Persona(BaseModel):
    id: str
    name: str
    description: str
    persona_type: PersonaType
    prompt_template: str
    analysis_focus: List[str]
    is_custom: bool = False
    created_by: Optional[str] = None


class Workflow(BaseModel):
    id: str
    name: str
    description: str
    personas: List[Persona]
    created_by: str
    created_at: str
    is_active: bool = True


class AnalysisResult(BaseModel):
    id: str
    workflow_id: str
    document_name: str
    analysis_content: Dict[str, Any]
    persona_results: Dict[str, str]
    metadata: Dict[str, Any]
    created_at: str


class ChatMessage(BaseModel):
    id: str
    analysis_id: str
    user_message: str
    assistant_response: str
    timestamp: str


class DocumentInput(BaseModel):
    content: str
    filename: str
    file_type: str


class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    document: DocumentInput
    user_id: str


class ChatRequest(BaseModel):
    analysis_id: str
    message: str
    user_id: str