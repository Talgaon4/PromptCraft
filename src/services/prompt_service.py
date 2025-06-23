# src/services/prompt_service.py
from datetime import datetime
from typing import List, Tuple
from sqlalchemy import func
from src.models.models import Prompt, PromptInstance, Response, Feedback
from src.services.base_service import BaseService

# Thresholds used elsewhere (could be moved to settings)
MIN_FEEDBACK_SAMPLES = 5
MIN_AVG_SCORE = 0.7

class PromptService(BaseService):
    # ---------- CRUD ---------- #
    def create(self, text: str, description: str = "") -> str:
        with self.session_scope() as s:
            p = Prompt(text=text, description=description)
            s.add(p)
            s.flush()
            s.refresh(p)
            return p.id

    def get(self, prompt_id: str) -> Prompt | None:
        with self.session_scope() as s:
            return s.get(Prompt, prompt_id)

    def list_paginated(self, offset: int, limit: int) -> Tuple[List[Prompt], int]:
        with self.session_scope() as s:
            q = s.query(Prompt).order_by(Prompt.created_at.desc())
            total = q.count()
            return q.offset(offset).limit(limit).all(), total

    def update(self, prompt_id: str, **fields) -> Prompt | None:
        with self.session_scope() as s:
            p: Prompt | None = s.get(Prompt, prompt_id)
            if not p:
                return None
            # business rule: bump version on *any* text change
            fields = {k: v for k, v in fields.items() if v is not None}
            # business rule: bump version on *any* text change
            if "text" in fields and fields["text"] != p.text:
                p.version += 1
            for k, v in fields.items():
                setattr(p, k, v)
            p.updated_at = datetime.utcnow()
            return p
        
    # ---------- instances / responses ---------- #
    def add_instance(
        self,
        prompt_id: str,
        formatted_text: str,
        context: str | None = None,
    ) -> PromptInstance:
        """
        Creates a PromptInstance for the given prompt and returns the ORM
        object (already persistent).
        """
        with self.session_scope() as s:
            inst = PromptInstance(
                prompt_id=prompt_id,
                formatted_text=formatted_text,
                context=context,
            )
            s.add(inst)
            s.flush()
            s.refresh(inst)
            return inst
        
    # ---------- analytics ---------- #
    def feedback_stats(self, prompt_id: str) -> dict:
        """
        Returns total feedback, avg score, last_score and last_5 trend list.
        """
        with self.session_scope() as s:
            # join Feedback → Response → PromptInstance to filter by prompt
            q = (
                s.query(Feedback.score)
                .join(Response, Feedback.response_id == Response.id)
                .join(PromptInstance, Response.prompt_instance_id == PromptInstance.id)
                .filter(PromptInstance.prompt_id == prompt_id)
                .order_by(Feedback.created_at.desc())
            )
            total = q.count()
            avg_score = q.with_entities(func.avg(Feedback.score)).scalar() or 0
            last_scores = [float(row[0]) for row in q.limit(5).all()]
            return {
                "total_feedback": total,
                "avg_score": float(avg_score),
                "last_scores": last_scores,
                "last_score": last_scores[0] if last_scores else None,
            }

    def ready_for_optimization(self, prompt_id: str) -> dict:
        stats = self.feedback_stats(prompt_id)
        ready = stats["total_feedback"] >= MIN_FEEDBACK_SAMPLES
        return {
            "ready": ready,
            "reason": (
                "Not enough feedback yet"
                if stats["total_feedback"] < MIN_FEEDBACK_SAMPLES
                else "Average score already high"
                if stats["avg_score"] >= MIN_AVG_SCORE
                else "Meets criteria"
            ),
            "stats": stats,
            "thresholds": {
                "min_samples": MIN_FEEDBACK_SAMPLES,
                "max_avg_score": MIN_AVG_SCORE,
            },
        }
    def add_feedback(self, prompt_id: str, score: float) -> Feedback:
        """Create auto-instance + response + feedback in one shot."""
        with self.session_scope() as s:
            inst = PromptInstance(prompt_id=prompt_id,
                                  formatted_text="auto")
            s.add(inst); s.flush()

            resp = Response(prompt_instance_id=inst.id, content="auto")
            s.add(resp); s.flush()

            fb   = Feedback(response_id=resp.id, score=score)
            s.add(fb); s.flush()
            s.refresh(fb)
            return fb
