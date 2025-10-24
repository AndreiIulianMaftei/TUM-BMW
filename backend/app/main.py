from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.database import Database
from app.api import documents


app = FastAPI(title="Document Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)

if os.path.exists("../frontend"):
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    Database.connect()


@app.on_event("shutdown")
async def shutdown_event():
    Database.disconnect()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
