from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from backend.processor import process_file
from backend.analyzer import analyze_bmw_1pager
from backend.database import Database

router = APIRouter(prefix="/api", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    
    file_content = await file.read()
    file_type = "pdf" if file.filename.endswith('.pdf') else "docx"
    
    try:
        text = process_file(file_content, file_type)
        analysis = analyze_bmw_1pager(text)
        
        db = Database.get_db()
        document_record = {
            "filename": file.filename,
            "file_type": file_type,
            "upload_date": datetime.utcnow(),
            "analysis": analysis.model_dump()
        }
        
        result = db.documents.insert_one(document_record)
        
        return {
            "success": True,
            "document_id": str(result.inserted_id),
            "filename": file.filename,
            "analysis": analysis
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


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
