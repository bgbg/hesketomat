"""Integration tests for Interviews API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.models.database import Base, Podcast, Episode  # noqa: F401
from backend.models.interview_models import (
    Project,
    Interview,
    Note,
    NoteItem,  # noqa: F401
    CanvasBlock,  # noqa: F401
)
from backend.models.database_session import get_db

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_interviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def project():
    """Create a test project."""
    response = client.post("/api/projects", json={"title": "Test Project"})
    return response.json()


def test_create_interview_minimal(project):
    """Test creating an interview with minimal data."""
    response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Interview with Expert",
            "background_context": "Expert in AI research",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["interview_title"] == "Interview with Expert"
    assert data["background_context"] == "Expert in AI research"
    assert data["project_id"] == project["id"]
    assert data["notes"] == []
    assert data["canvas_blocks"] == []


def test_create_interview_with_notes(project):
    """Test creating interview with notes and items."""
    response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Interview with Researcher",
            "background_context": "Background info",
            "notes": [
                {
                    "title": "Research Notes",
                    "order_index": 0,
                    "items": [
                        {
                            "type": "text",
                            "content": "Key finding from paper",
                            "provenance": "web",
                            "source_title": "Research Paper",
                            "source_domain": "arxiv.org",
                            "order_index": 0,
                        },
                        {
                            "type": "image",
                            "content": "https://example.com/chart.png",
                            "provenance": "web",
                            "source_domain": "example.com",
                            "order_index": 1,
                        },
                    ],
                },
                {
                    "title": "Questions",
                    "order_index": 1,
                    "items": [],
                },
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["notes"]) == 2
    assert data["notes"][0]["title"] == "Research Notes"
    assert len(data["notes"][0]["items"]) == 2
    assert data["notes"][0]["items"][0]["type"] == "text"
    assert data["notes"][0]["items"][1]["type"] == "image"


def test_create_interview_with_canvas_blocks(project):
    """Test creating interview with canvas blocks."""
    response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Interview Outline",
            "background_context": "",
            "canvas_blocks": [
                {"type": "heading", "text": "Introduction", "order_index": 0},
                {
                    "type": "paragraph",
                    "text": "Welcome and background questions",
                    "order_index": 1,
                },
                {"type": "heading", "text": "Main Topics", "order_index": 2},
            ],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["canvas_blocks"]) == 3
    assert data["canvas_blocks"][0]["type"] == "heading"
    assert data["canvas_blocks"][1]["type"] == "paragraph"


def test_create_interview_invalid_project():
    """Test creating interview with non-existent project."""
    response = client.post(
        "/api/interviews",
        json={
            "project_id": 999,
            "interview_title": "Test",
            "background_context": "",
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_interview(project):
    """Test retrieving an interview."""
    # Create interview
    create_response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Test Interview",
            "background_context": "Test context",
            "notes": [{"title": "Note 1", "order_index": 0, "items": []}],
        },
    )
    interview_id = create_response.json()["id"]

    # Get interview
    response = client.get(f"/api/interviews/{interview_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == interview_id
    assert data["interview_title"] == "Test Interview"
    assert len(data["notes"]) == 1


def test_get_interview_not_found():
    """Test getting non-existent interview."""
    response = client.get("/api/interviews/999")
    assert response.status_code == 404


def test_update_interview(project):
    """Test updating interview metadata."""
    # Create interview
    create_response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Original Title",
            "background_context": "Original context",
        },
    )
    interview_id = create_response.json()["id"]

    # Update interview
    response = client.put(
        f"/api/interviews/{interview_id}",
        json={
            "interview_title": "Updated Title",
            "background_context": "Updated context",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["interview_title"] == "Updated Title"
    assert data["background_context"] == "Updated context"


def test_autosave_interview(project):
    """Test autosave functionality (full replace)."""
    # Create interview with some data
    create_response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Original",
            "background_context": "Original",
            "notes": [{"title": "Old Note", "order_index": 0, "items": []}],
            "canvas_blocks": [
                {"type": "heading", "text": "Old Heading", "order_index": 0}
            ],
        },
    )
    interview_id = create_response.json()["id"]

    # Autosave with completely different data
    response = client.post(
        f"/api/interviews/{interview_id}/autosave",
        json={
            "interview_title": "Autosaved Title",
            "background_context": "Autosaved context",
            "notes": [
                {
                    "title": "New Note 1",
                    "order_index": 0,
                    "items": [
                        {
                            "type": "text",
                            "content": "New content",
                            "provenance": "manual",
                            "order_index": 0,
                        }
                    ],
                },
                {"title": "New Note 2", "order_index": 1, "items": []},
            ],
            "canvas_blocks": [
                {"type": "paragraph", "text": "New paragraph", "order_index": 0}
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["interview_title"] == "Autosaved Title"
    assert len(data["notes"]) == 2
    assert data["notes"][0]["title"] == "New Note 1"
    assert len(data["notes"][0]["items"]) == 1
    assert len(data["canvas_blocks"]) == 1
    assert data["canvas_blocks"][0]["text"] == "New paragraph"


def test_delete_interview(project):
    """Test deleting an interview."""
    # Create interview
    create_response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "To Delete",
            "background_context": "",
        },
    )
    interview_id = create_response.json()["id"]

    # Delete interview
    response = client.delete(f"/api/interviews/{interview_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/interviews/{interview_id}")
    assert response.status_code == 404


def test_delete_interview_cascades(project):
    """Test that deleting interview cascades to notes and blocks."""
    db = TestingSessionLocal()
    try:
        # Create interview with data
        proj = db.query(Project).filter_by(id=project["id"]).first()
        interview = Interview(
            project=proj,
            interview_title="Test",
            background_context="",
        )
        db.add(interview)
        db.flush()

        note = Note(interview_id=interview.id, title="Note")
        db.add(note)
        db.flush()

        item = NoteItem(note_id=note.id, type="text", content="Content")
        db.add(item)
        db.commit()

        interview_id = interview.id
        note_id = note.id
        item_id = item.id

        # Delete via API
        response = client.delete(f"/api/interviews/{interview_id}")
        assert response.status_code == 204

        # Verify cascading delete
        assert db.query(Interview).filter_by(id=interview_id).first() is None
        assert db.query(Note).filter_by(id=note_id).first() is None
        assert db.query(NoteItem).filter_by(id=item_id).first() is None
    finally:
        db.close()


def test_interview_ordering_preserved(project):
    """Test that note and block ordering is preserved."""
    response = client.post(
        "/api/interviews",
        json={
            "project_id": project["id"],
            "interview_title": "Order Test",
            "background_context": "",
            "notes": [
                {"title": "Third", "order_index": 2, "items": []},
                {"title": "First", "order_index": 0, "items": []},
                {"title": "Second", "order_index": 1, "items": []},
            ],
            "canvas_blocks": [
                {"type": "paragraph", "text": "Block 2", "order_index": 1},
                {"type": "heading", "text": "Block 1", "order_index": 0},
            ],
        },
    )
    data = response.json()

    # Notes should be ordered
    assert data["notes"][0]["title"] == "First"
    assert data["notes"][1]["title"] == "Second"
    assert data["notes"][2]["title"] == "Third"

    # Blocks should be ordered
    assert data["canvas_blocks"][0]["text"] == "Block 1"
    assert data["canvas_blocks"][1]["text"] == "Block 2"
