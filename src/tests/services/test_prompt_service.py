from src.services.prompt_service import PromptService
from uuid import uuid4
import pytest
def test_prompt_stats(db):
    svc = PromptService(db)
    pid = svc.create("Ping", "")
    svc.add_feedback(pid, 0.8)
    svc.add_feedback(pid, 0.6)
    stats = svc.feedback_stats(pid)
    assert stats["total_feedback"] == 2
    assert stats["avg_score"] == pytest.approx(0.7)
