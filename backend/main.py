from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from PyPDF2 import PdfReader
from docx import Document
from datetime import datetime
import io
import os
from config import Settings

settings = Settings()

app = FastAPI(title="Document Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
db = None


@app.on_event("startup")
async def startup_event():
    global client, db
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.database_name]


@app.on_event("shutdown")
async def shutdown_event():
    if client:
        client.close()


def analyze_text(text: str) -> dict:
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return {
        "sentence_count": len(sentences),
        "average_word_length": round(sum(len(word) for word in text.split()) / len(text.split()), 2) if text.split() else 0,
        "unique_words": len(set(word.lower() for word in text.split()))
    }


def extract_pdf(content: bytes) -> tuple:
    pdf_reader = PdfReader(io.BytesIO(content))
    pages = len(pdf_reader.pages)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text, pages


def extract_docx(content: bytes) -> tuple:
    doc = Document(io.BytesIO(content))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text, None


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        if file.filename.endswith('.pdf'):
            content = await file.read()
            text, pages = extract_pdf(content)
            file_type = "pdf"
        elif file.filename.endswith('.docx'):
            content = await file.read()
            text, pages = extract_docx(content)
            file_type = "docx"
        else:
            raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")

        word_count = len(text.split())
        analysis = analyze_text(text)

        doc_data = {
            "filename": file.filename,
            "file_type": file_type,
            "content": text,
            "word_count": word_count,
            "page_count": pages,
            "analysis_data": analysis,
            "created_at": datetime.utcnow()
        }

        result = db.documents.insert_one(doc_data)

        return {
            "message": "File processed successfully",
            "document_id": str(result.inserted_id),
            "data": doc_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    try:
        from bson import ObjectId
        doc = db.documents.find_one({"_id": ObjectId(document_id)})
        
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
