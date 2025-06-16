from fastapi import APIRouter, HTTPException
from src.database.database import Database
from src.api.schemas import InstanceCreate
from src.api.responses import OperationResult

router = APIRouter()

@router.post("/prompts/{prompt_id}/instances")
def create_instance(prompt_id: str, instance_data: InstanceCreate):
    """Record a new usage instance of a prompt"""
    try:
        # First verify the prompt exists
        db = Database()
        prompt = db.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Create the instance
        instance = db.create_instance(
            prompt_id=prompt_id,
            formatted_text=instance_data.formatted_text,
            context=instance_data.context
        )
        
        return OperationResult.success(
            data=instance.to_dict(),
            message="Prompt instance recorded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}")
def get_instance(instance_id: str):
    """Get a specific prompt instance"""
    try:
        db = Database()
        instance = db.get_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        return OperationResult.success(instance.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))