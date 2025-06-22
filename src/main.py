from dotenv import load_dotenv
from fastapi import FastAPI
from src.api.routes.health import router as health_router
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.prompts import router as prompts_router
from src.api.error_handlers import add_error_handlers
from src.api.routes.instances import router as instances_router
from src.api.routes.feedback import router as feedback_router
load_dotenv()          
app = FastAPI(title="PromptCraft API", version="1.0.0")

app.include_router(health_router, prefix="/api/v1")
app.include_router(prompts_router, prefix="/api/v1")
app.include_router(instances_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update later for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
add_error_handlers(app)
@app.on_event("startup")
def startup_event():
    print("✅ FastAPI app is running.")
