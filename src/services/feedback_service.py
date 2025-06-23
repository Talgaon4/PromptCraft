# src/services/feedback_service.py
from typing import List, Tuple
from src.models.models import Feedback, Response
from src.services.base_service import BaseService
import json

class FeedbackService(BaseService):
    # ---------- submit ---------- #
    def add_score(self, response_id: str, score: float) -> Feedback:
        if not (0.0 <= score <= 1.0):
            raise ValueError("Score must be between 0.0 and 1.0")
        with self.session_scope() as s:
            fb = Feedback(response_id=response_id, score=score)
            s.add(fb)
            s.flush()
            s.refresh(fb)
            return fb
        
    def add_feedback(self, response_id: str, score: float) -> Feedback:
        """
        Convenience wrapper – routers expect this name.
        """
        return self.add_score(response_id, score)
    
    # ---------- queries ---------- #
    def list_for_prompt(
        self, prompt_id: str, offset: int, limit: int
    ) -> Tuple[List[Feedback], int]:
        from src.models.models import PromptInstance  # local import to avoid cycles
        with self.session_scope() as s:
            q = (
                s.query(Feedback)
                .join(Response, Feedback.response_id == Response.id)
                .join(PromptInstance, Response.prompt_instance_id == PromptInstance.id)
                .filter(PromptInstance.prompt_id == prompt_id)
                .order_by(Feedback.created_at.desc())
            )
            total = q.count()
            return q.offset(offset).limit(limit).all(), total
    
    # ---------- responses ---------- #
    def add_response(
        self,
        instance_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> Response:
        """
        Creates a Response row for the given PromptInstance and returns it.
        """
        with self.session_scope() as s:
            resp = Response(
                prompt_instance_id=instance_id,
                content=content,
                response_metadata=json.dumps(metadata) if metadata else None,
            )
            s.add(resp)
            s.flush()
            s.refresh(resp)
            return resp

    def list_by_prompt(self, prompt_id: str, offset: int, limit: int):
        return self.list_for_prompt(prompt_id, offset, limit)

    def stats(self, prompt_id: str) -> dict:

        items, total = self.list_for_prompt(prompt_id, 0, 10_000_000)
        avg = float(sum(f.score for f in items) / total) if total else 0.0
        return {
            "prompt_id": prompt_id,
            "total_feedback": total,
            "avg_score": avg,
        }