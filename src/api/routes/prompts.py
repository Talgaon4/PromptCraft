from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.database.database import Database
from src.api.schemas import PromptCreate
from src.api.responses import PromptResult, OperationResult

router = APIRouter()

@router.post("/prompts")
def create_prompt(prompt_data: PromptCreate):
    """Create a new prompt"""
    try:
        db = Database()
        prompt = db.create_prompt(prompt_data.text, prompt_data.description or "")
        
        print(f"DEBUG: create_prompt returned: {repr(prompt)}")
        print(f"DEBUG: type: {type(prompt)}")
        
        # Handle case where create_prompt returns a string (like "success")
        if isinstance(prompt, str):
            print(f"WARNING: create_prompt returned string: {prompt}")
            raise HTTPException(
                status_code=500, 
                detail=f"Database method returned string instead of Prompt object: {prompt}"
            )
        
        print("DEBUG: About to convert to dict...")
        # Ensure prompt is converted to dict format
        if hasattr(prompt, 'to_dict'):
            try:
                prompt_dict = prompt.to_dict()
                print(f"DEBUG: to_dict() successful: {prompt_dict}")
            except Exception as dict_error:
                print(f"DEBUG: to_dict() failed: {dict_error}")
                raise dict_error
        elif isinstance(prompt, dict):
            prompt_dict = prompt
            print(f"DEBUG: prompt was already a dict: {prompt_dict}")
        else:
            # If it's some other object, convert basic attributes
            prompt_dict = {
                "id": getattr(prompt, 'id', None),
                "text": getattr(prompt, 'text', prompt_data.text),
                "description": getattr(prompt, 'description', prompt_data.description or ""),
                "created_at": getattr(prompt, 'created_at', None)
            }
            print(f"DEBUG: manually created dict: {prompt_dict}")
        
        print("DEBUG: About to create PromptResult.success...")
        try:
            result = PromptResult.success_response(prompt_dict, "Prompt created successfully")
            print(f"DEBUG: PromptResult.success_response created: {result}")
            return result
        except Exception as result_error:
            print(f"DEBUG: PromptResult.success_response failed: {result_error}")
            raise result_error
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        print(f"Error creating prompt: {str(e)}")  # Debug logging
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create prompt: {str(e)}")

@router.get("/prompts/{prompt_id}")
def get_prompt(prompt_id: str):
    """Get a specific prompt by ID"""
    try:
        db = Database()
        prompt = db.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Ensure prompt is converted to dict format
        if hasattr(prompt, 'to_dict'):
            prompt_dict = prompt.to_dict()
        elif isinstance(prompt, dict):
            prompt_dict = prompt
        else:
            prompt_dict = {
                "id": getattr(prompt, 'id', None),
                "text": getattr(prompt, 'text', ''),
                "description": getattr(prompt, 'description', ''),
                "created_at": getattr(prompt, 'created_at', None)
            }
            
        return PromptResult.success(prompt_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting prompt: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")

@router.get("/prompts")
def list_prompts(
    limit: int = Query(50, ge=1, le=100, description="Number of prompts to return"),
    offset: int = Query(0, ge=0, description="Number of prompts to skip")
):
    """List all prompts with pagination"""
    try:
        db = Database()
        prompts = db.list_prompts(limit=limit, offset=offset)
        
        # Convert all prompts to dict format
        prompt_dicts = []
        for prompt in prompts:
            if hasattr(prompt, 'to_dict'):
                prompt_dicts.append(prompt.to_dict())
            elif isinstance(prompt, dict):
                prompt_dicts.append(prompt)
            else:
                prompt_dicts.append({
                    "id": getattr(prompt, 'id', None),
                    "text": getattr(prompt, 'text', ''),
                    "description": getattr(prompt, 'description', ''),
                    "created_at": getattr(prompt, 'created_at', None)
                })
        
        return OperationResult.success_response(
            data={
                "prompts": prompt_dicts,
                "count": len(prompt_dicts),
                "limit": limit,
                "offset": offset
            },
            message=f"Retrieved {len(prompt_dicts)} prompts"
        )
        
    except Exception as e:
        print(f"Error listing prompts: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")