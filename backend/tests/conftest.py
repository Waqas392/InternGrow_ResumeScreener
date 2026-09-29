import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_interngrow.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ALLOWED_ORIGINS"] = '["http://localhost:5173"]'
os.environ["SEED_EMAIL"] = ""
os.environ["SEED_PASSWORD"] = ""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
