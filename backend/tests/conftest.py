"""Shared test fixtures.

Every API test file used to build its own engine and assign
``app.dependency_overrides[get_db]`` at import time. Because pytest imports all
test modules before running any of them, the last import won for the whole
session and tests ran against another module's database — which its own
teardown then dropped. The fixtures below give each test a private in-memory
database and install/remove the override around that single test.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app

# Import every model so Base.metadata knows about all tables before create_all.
from backend.models.database import Base, Podcast, Episode  # noqa: F401
from backend.models.database_session import get_db


@pytest.fixture
def db_engine():
    """A private in-memory database, torn down after each test.

    StaticPool keeps every connection pointed at the same in-memory database;
    without it each connection would get its own empty one.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """A session bound to the test database."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """A TestClient whose requests run against the test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
