from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import json
import uuid
from datetime import datetime

from .models import (
    Persona, Workflow, AnalysisResult, ChatMessage, 
    DocumentInput, WorkflowExecutionRequest, ChatRequest
)
from .personas import persona_manager
from .workflow_engine import workflow_engine
from .chat_system import chat_system

app = FastAPI(
    title="Document Analysis Workflow API",
    description="API for creating and executing document analysis workflows with selectable personas",
    version="1.0.0"
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
    """Root endpoint"""
    return {
        "message": "Document Analysis Workflow API",
        "version": "1.0.0",
        "endpoints": {
            "personas": "/personas",
            "workflows": "/workflows",
            "analysis": "/analysis",
            "chat": "/chat"
        }
    }


# Persona Management Endpoints
@app.get("/personas", response_model=List[Persona])
async def get_personas():
    """Get all available personas"""
    return persona_manager.get_all_personas()


@app.get("/personas/{persona_id}", response_model=Persona)
async def get_persona(persona_id: str):
    """Get a specific persona by ID"""
    persona = persona_manager.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@app.post("/personas", response_model=Persona)
async def create_persona(
    name: str = Form(...),
    description: str = Form(...),
    prompt_template: str = Form(...),
    analysis_focus: str = Form(...),  # JSON string
    created_by: str = Form(...)
):
    """Create a custom persona"""
    try:
        focus_list = json.loads(analysis_focus)
        if not isinstance(focus_list, list):
            raise ValueError("analysis_focus must be a JSON array")
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
    """Delete a custom persona"""
    success = persona_manager.delete_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found or not deletable")
    return {"message": "Persona deleted successfully"}


# Workflow Management Endpoints
@app.get("/workflows", response_model=List[Workflow])
async def get_workflows():
    """Get all workflows"""
    return workflow_engine.get_all_workflows()


@app.get("/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID"""
    workflow = workflow_engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@app.post("/workflows", response_model=Workflow)
async def create_workflow(
    name: str = Form(...),
    description: str = Form(...),
    persona_ids: str = Form(...),  # JSON string
    created_by: str = Form(...)
):
    """Create a new workflow"""
    try:
        persona_id_list = json.loads(persona_ids)
        if not isinstance(persona_id_list, list):
            raise ValueError("persona_ids must be a JSON array")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in persona_ids")
    
    workflow = workflow_engine.create_workflow(
        name=name,
        description=description,
        persona_ids=persona_id_list,
        created_by=created_by
    )
    return workflow


# Document Analysis Endpoints
@app.post("/analysis/execute", response_model=AnalysisResult)
async def execute_workflow(
    workflow_id: str = Form(...),
    document_content: str = Form(...),
    filename: str = Form(...),
    file_type: str = Form(...),
    user_id: str = Form(...)
):
    """Execute a workflow with a document"""
    try:
        document = DocumentInput(
            content=document_content,
            filename=filename,
            file_type=file_type
        )
        
        analysis_result = workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            document=document,
            user_id=user_id
        )
        return analysis_result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/analysis/{analysis_id}", response_model=AnalysisResult)
async def get_analysis(analysis_id: str):
    """Get analysis result by ID"""
    analysis = workflow_engine.get_analysis_result(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@app.get("/analysis/user/{user_id}", response_model=List[AnalysisResult])
async def get_user_analyses(user_id: str):
    """Get all analyses for a user"""
    return workflow_engine.get_user_analyses(user_id)


# Chat Endpoints
@app.post("/chat/send", response_model=ChatMessage)
async def send_chat_message(
    analysis_id: str = Form(...),
    message: str = Form(...),
    user_id: str = Form(...)
):
    """Send a chat message for an analysis"""
    try:
        chat_request = ChatRequest(
            analysis_id=analysis_id,
            message=message,
            user_id=user_id
        )
        
        chat_message = chat_system.send_message(chat_request)
        return chat_message
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.get("/chat/{analysis_id}/history", response_model=List[ChatMessage])
async def get_chat_history(analysis_id: str):
    """Get chat history for an analysis"""
    return chat_system.get_chat_history(analysis_id)


@app.delete("/chat/{analysis_id}/history")
async def clear_chat_history(analysis_id: str):
    """Clear chat history for an analysis"""
    success = chat_system.clear_chat_history(analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"message": "Chat history cleared successfully"}


@app.get("/chat/{analysis_id}/summary")
async def get_analysis_summary(analysis_id: str):
    """Get a summary of the analysis"""
    try:
        summary = chat_system.get_analysis_summary(analysis_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/chat/compare")
async def compare_analyses(analysis_ids: str = Form(...)):  # JSON string
    """Compare multiple analyses"""
    try:
        analysis_id_list = json.loads(analysis_ids)
        if not isinstance(analysis_id_list, list) or len(analysis_id_list) < 2:
            raise ValueError("analysis_ids must be a JSON array with at least 2 items")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in analysis_ids")
    
    try:
        comparison = chat_system.get_comparative_analysis(analysis_id_list)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# File Upload Endpoint
@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document file"""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        return {
            "filename": file.filename,
            "content": content_str,
            "file_type": file.content_type,
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File upload failed: {str(e)}")


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "persona_manager": "active",
            "workflow_engine": "active",
            "chat_system": "active"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)