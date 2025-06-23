# src/services/health_service.py
from typing import Dict
from sqlalchemy import text
from src.services.base_service import BaseService

class HealthService(BaseService):
    def db_ping(self) -> Dict:
        """Lightweight health diagnostics."""
        with self.session_scope() as s:
            # trivial query
            s.execute(text("SELECT 1"))
            counts = {
                "prompts": s.execute(text("SELECT count(*) FROM prompts")).scalar(),
                "instances": s.execute(text("SELECT count(*) FROM prompt_instances")).scalar(),
                "responses": s.execute(text("SELECT count(*) FROM responses")).scalar(),
                "feedback": s.execute(text("SELECT count(*) FROM feedback")).scalar(),
            }
            return {
                "status": "ok",
                "table_counts": counts,
            }
