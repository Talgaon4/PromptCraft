from fastapi import APIRouter, HTTPException
from src.database.database import Database
from src.api.schemas import FeedbackCreate
from src.api.responses import OperationResult

router = APIRouter()

@router.post("/responses/{response_id}/feedback")
def submit_feedback(response_id: str, feedback_data: FeedbackCreate):
    """Submit feedback score for a response"""
    try:
        # Verify the response exists
        db = Database()
        response = db.get_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Response not found")
        
        # Create the feedback
        feedback = db.create_feedback(
            response_id=response_id,
            score=feedback_data.score
        )
        
        return OperationResult.success(
            data=feedback.to_dict(),
            message="Feedback submitted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts/{prompt_id}/feedback")
def get_prompt_feedback(prompt_id: str):
    """Get all feedback for a prompt with statistics"""
    try:
        db = Database()
        
        # Verify prompt exists
        prompt = db.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        # Get feedback data
        feedback_data = db.get_feedback_for_prompt(prompt_id)
        
        # Calculate statistics
        if feedback_data:
            scores = [item['feedback']['score'] for item in feedback_data]
            statistics = {
                "count": len(scores),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores)
            }
        else:
            statistics = {
                "count": 0,
                "average_score": 0.0,
                "min_score": 0.0,
                "max_score": 0.0
            }
        
        return OperationResult.success(
            data={
                "prompt_id": prompt_id,
                "statistics": statistics,
                "feedback": feedback_data
            },
            message=f"Retrieved {len(feedback_data)} feedback items"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))