from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime


class Persona(BaseModel):
    id: str
    name: str
    description: str
    prompt_template: str
    analysis_focus: List[str]
    is_custom: bool = False
    created_by: Optional[str] = None


class Workflow(BaseModel):
    id: str
    name: str
    description: str
    persona_ids: List[str]
    created_by: str
    created_at: str


class AnalysisResult(BaseModel):
    id: str
    workflow_id: str
    document_name: str
    results: Dict[str, str]  # persona_id -> analysis_result
    created_at: str


class DocumentInput(BaseModel):
    content: str
    filename: str


class ChatMessage(BaseModel):
    analysis_id: str
    message: str
    response: str
    timestamp: str