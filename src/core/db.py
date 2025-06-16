from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from src.database.database import Database

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="PromptCraft API",
    description="REST API for automated prompt optimization",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    db = Database()
    db.initialize()
    print("✅ FastAPI started and database initialized")

# Health check endpoint (your first endpoint!)
@app.get("/health")
def health_check():
    try:
        db = Database()
        # Test database connection
        return {
            "status": "healthy",
            "message": "PromptCraft API is running",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)