from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from src.database.database import Database

# Import route modules
from src.api.routes import prompts, instances, responses, feedback

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(prompts.router, prefix="/api/v1", tags=["prompts"])
app.include_router(instances.router, prefix="/api/v1", tags=["instances"])  
app.include_router(responses.router, prefix="/api/v1", tags=["responses"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    db = Database()
    db.initialize()
    print("✅ FastAPI started and database initialized")

# Health check endpoint
@app.get("/health")
def health_check():
    try:
        db = Database()
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