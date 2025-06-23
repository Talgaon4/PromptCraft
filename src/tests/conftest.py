import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.database.database import Database  # Person A’s class


# ---------- TEST DATABASE ---------- #
@pytest.fixture(scope="session")
def test_db_url():
    # SQLite in a temp file ⇒ zero install, rolls back automatically
    tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3")
    return f"sqlite:///{tmp.name}"


@pytest.fixture(scope="session")
def db(test_db_url):
    """
    Create all tables once per test session against SQLite.
    """
    db = Database(test_db_url)
    db.initialize()          # calls Base.metadata.create_all()
    return db


# ---------- FASTAPI TEST CLIENT ---------- #
@pytest.fixture()
def client(db, monkeypatch):
    """
    Overrides DATABASE_URL env var so the app uses the test DB.
    Then returns FastAPI TestClient.
    """
    monkeypatch.setenv("DATABASE_URL", db.db_manager.engine.url.render_as_string(hide_password=False))
    return TestClient(app)
