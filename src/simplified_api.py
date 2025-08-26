from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import uuid
from datetime import datetime

from .simplified_models import (
    Persona, Workflow, AnalysisResult, ChatMessage, DocumentInput
)
from .simplified_personas import persona_manager
from .simplified_workflow import workflow_engine
from .simplified_chat import chat_system

app = FastAPI(
    title="Simplified Document Analysis API",
    description="Simplified API for document analysis workflows",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Simplified Document Analysis API",
        "version": "2.0.0"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Persona endpoints
@app.get("/personas", response_model=List[Persona])
async def get_personas():
    return persona_manager.get_all_personas()


@app.get("/personas/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str):
    persona = persona_manager.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@app.post("/personas", response_model=Persona)
async def create_persona(
    name: str = Form(...),
    description: str = Form(...),
    prompt_template: str = Form(...),
    analysis_focus: str = Form(...),
    created_by: str = Form(...)
):
    try:
        focus_list = json.loads(analysis_focus)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in analysis_focus")
    
    persona = persona_manager.create_custom_persona(
        name=name,
        description=description,
        prompt_template=prompt_template,
        analysis_focus=focus_list,
        created_by=created_by
    )
    return persona


@app.delete("/personas/{persona_id}")
async def delete_persona(persona_id: str):
    success = persona_manager.delete_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found or not deletable")
    return {"message": "Persona deleted successfully"}


# Workflow endpoints
@app.get("/workflows", response_model=List[Workflow])
async def get_workflows():
    return workflow_engine.get_all_workflows()


@app.get("/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.post("/workflows", response_model=Workflow)
async def create_workflow(
    name: str = Form(...),
    description: str = Form(...),
    persona_ids: str = Form(...),
    created_by: str = Form(...)
):
    try:
        persona_id_list = json.loads(persona_ids)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in persona_ids")
    
    workflow = workflow_engine.create_workflow(
        name=name,
        description=description,
        persona_ids=persona_id_list,
        created_by=created_by
    )
    return workflow


# Analysis endpoints
@app.post("/analysis/execute", response_model=AnalysisResult)
async def execute_analysis(
    workflow_id: str = Form(...),
    document_content: str = Form(...),
    filename: str = Form(...),
    user_id: str = Form(...)
):
    document = DocumentInput(content=document_content, filename=filename)
    
    try:
        result = workflow_engine.execute_workflow(workflow_id, document, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    result = workflow_engine.get_analysis_result(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return result


@app.get("/analysis/user/{user_id}", response_model=List[AnalysisResult])
async def get_user_analyses(user_id: str):
    return workflow_engine.get_user_analyses(user_id)


# Chat endpoints
@app.post("/chat/send", response_model=ChatMessage)
async def send_chat_message(
    analysis_id: str = Form(...),
    message: str = Form(...),
    user_id: str = Form(...)
):
    try:
        chat_message = chat_system.send_message(analysis_id, message, user_id)
        return chat_message
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/chat/{analysis_id}/history", response_model=List[ChatMessage])
async def get_chat_history(analysis_id: str):
    return chat_system.get_chat_history(analysis_id)


@app.delete("/chat/{analysis_id}/history")
async def clear_chat_history(analysis_id: str):
    success = chat_system.clear_chat_history(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Chat history cleared successfully"}