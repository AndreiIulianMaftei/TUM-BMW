from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from datetime import datetime
from backend.processor import process_file
from backend.analyzer import analyze_bmw_1pager
from backend.chat_analyzer import process_chat_request
from backend.database import Database
from backend.models import (
    TextAnalysisRequest, ChatRequest, ChatResponse,
    AnalysisSettings, ChatMessage
)
from typing import Optional
import json

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    provider: Optional[str] = Form("gemini"),
    settings_json: Optional[str] = Form(None)
):
    """Upload and analyze a document (PDF/DOCX)"""
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    
    # Validate provider
    if provider not in ["gemini", "openai"]:
        raise HTTPException(status_code=400, detail="Provider must be either 'gemini' or 'openai'")
    
    # Parse settings if provided
    settings = None
    if settings_json:
        try:
            settings_dict = json.loads(settings_json)
            settings = AnalysisSettings(**settings_dict)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid settings: {str(e)}")
    
    file_content = await file.read()
    file_type = "pdf" if file.filename.endswith('.pdf') else "docx"
    
    try:
        text = process_file(file_content, file_type)
        analysis = analyze_bmw_1pager(text, provider=provider, settings=settings)
        
        db = Database.get_db()
        document_record = {
            "filename": file.filename,
            "file_type": file_type,
            "input_type": "file",
            "llm_provider": provider,
            "upload_date": datetime.utcnow(),
            "settings": settings.model_dump() if settings else None,
            "analysis": analysis.model_dump()
        }
        
        result = db.documents.insert_one(document_record)
        
        return {
            "success": True,
            "document_id": str(result.inserted_id),
            "filename": file.filename,
            "provider": provider,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/analyze-text")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text input directly (no file upload)"""
    if request.provider not in ["gemini", "openai"]:
        raise HTTPException(status_code=400, detail="Provider must be either 'gemini' or 'openai'")
    
    try:
        analysis = analyze_bmw_1pager(
            text=request.text,
            provider=request.provider,
            settings=request.settings
        )
        
        db = Database.get_db()
        document_record = {
            "filename": "text_input",
            "file_type": "text",
            "input_type": "text",
            "llm_provider": request.provider,
            "upload_date": datetime.utcnow(),
            "input_text": request.text[:500],  # Store first 500 chars for reference
            "settings": request.settings.model_dump() if request.settings else None,
            "analysis": analysis.model_dump()
        }
        
        result = db.documents.insert_one(document_record)
        
        return {
            "success": True,
            "document_id": str(result.inserted_id),
            "provider": request.provider,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")


@router.post("/chat")
async def chat(request: ChatRequest):
    """Live chat with AI about analyzed documents"""
    if request.provider not in ["gemini", "openai"]:
        raise HTTPException(status_code=400, detail="Provider must be either 'gemini' or 'openai'")
    
    try:
        # Get document context if document_id provided
        document_context = None
        if request.document_id:
            from bson import ObjectId
            db = Database.get_db()
            document = db.documents.find_one({"_id": ObjectId(request.document_id)})
            if document and "analysis" in document:
                # Create concise context from analysis
                analysis = document["analysis"]
                document_context = f"""
Document: {document.get('filename', 'Unknown')}
Executive Summary: {analysis.get('executive_summary', 'N/A')}
TAM: {analysis.get('tam', {}).get('insight', 'N/A')}
Key Recommendation: {analysis.get('improvement_recommendations', ['N/A'])[0] if analysis.get('improvement_recommendations') else 'N/A'}
"""
        
        # Process chat
        response = process_chat_request(
            message=request.message,
            provider=request.provider,
            conversation_history=request.conversation_history,
            document_context=document_context
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/documents")
async def get_documents():
    db = Database.get_db()
    documents = list(db.documents.find().sort("upload_date", -1).limit(50))
    
    for doc in documents:
        doc["_id"] = str(doc["_id"])
    
    return {"documents": documents}


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    from bson import ObjectId
    
    db = Database.get_db()
    document = db.documents.find_one({"_id": ObjectId(document_id)})
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document["_id"] = str(document["_id"])
    return document
