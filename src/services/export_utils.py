# src/services/export_utils.py
"""
Tiny helper to dump whole tables to CSV / JSON for admins.
"""
import csv, json
from pathlib import Path
from typing import Sequence
from sqlalchemy.orm import Session
from src.models import models

def _rows(query) -> Sequence[dict]:
    return [row.to_dict() for row in query]

def export_table_csv(session: Session, model, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    rows = _rows(session.query(model))
    if not rows:
        return
    with dst.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def export_all_json(session: Session, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "prompts": _rows(session.query(models.Prompt)),
        "instances": _rows(session.query(models.PromptInstance)),
        "responses": _rows(session.query(models.Response)),
        "feedback": _rows(session.query(models.Feedback)),
    }
    dst.write_text(json.dumps(data, indent=2))
