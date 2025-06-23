# src/services/base_service.py
"""
Common functionality shared by all service classes.
Keeps an internal DB session-scope context-manager so callers don’t
have to juggle sessions manually.
"""
from contextlib import contextmanager
from typing import Generator
from src.database.database import Database

class BaseService:
    def __init__(self, db: Database):
        self.db = db

    @contextmanager
    def session_scope(self) -> Generator:
        with self.db.db_manager.get_session() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
