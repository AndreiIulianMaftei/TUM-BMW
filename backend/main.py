from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Database
from backend.routes import router

app = FastAPI(
    title="BMW 1-Pager Analyzer",
    description="AI-powered Value | Market Potential Generator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "BMW 1-Pager Analyzer"}

# Include API routes
app.include_router(router)

# Mount static files (must be last!)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    Database.connect()


@app.on_event("shutdown")
async def shutdown_event():
    Database.disconnect()
