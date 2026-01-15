"""Integration tests for Projects API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
# Import all models BEFORE creating engine to ensure they're registered with Base
from backend.models.database import Base, Podcast, Episode  # noqa: F401 - register models
from backend.models.interview_models import (
    Project,
    Interview,
    Note,
    NoteItem,  # noqa: F401 - needed to register with Base
    CanvasBlock,  # noqa: F401 - needed to register with Base
)
from backend.models.database_session import get_db

# Test database setup - create AFTER importing models
# Use file-based DB to avoid in-memory isolation issues
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_projects.db"
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

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_project():
    """Test creating a new project."""
    response = client.post(
        "/api/projects",
        json={"title": "My Interview Project"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Interview Project"
    assert "id" in data
    assert data["stats"]["note_count"] == 0
    assert data["stats"]["has_context"] is False


def test_create_project_empty_title():
    """Test creating project with empty title fails."""
    response = client.post(
        "/api/projects",
        json={"title": ""},
    )
    assert response.status_code == 422  # Validation error


def test_list_projects_empty():
    """Test listing projects when none exist."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_list_projects():
    """Test listing multiple projects."""
    # Create projects
    client.post("/api/projects", json={"title": "Project 1"})
    client.post("/api/projects", json={"title": "Project 2"})
    client.post("/api/projects", json={"title": "Project 3"})

    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Projects should be ordered by last_modified descending (newest first)
    assert data[0]["title"] == "Project 3"
    assert data[1]["title"] == "Project 2"
    assert data[2]["title"] == "Project 1"


def test_list_projects_with_pagination():
    """Test listing projects with pagination."""
    # Create 5 projects
    for i in range(5):
        client.post("/api/projects", json={"title": f"Project {i+1}"})

    # Get first 2
    response = client.get("/api/projects?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Get next 2
    response = client.get("/api/projects?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_project():
    """Test getting a specific project."""
    # Create project
    create_response = client.post(
        "/api/projects",
        json={"title": "Test Project"},
    )
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["title"] == "Test Project"
    assert data["stats"]["note_count"] == 0


def test_get_project_not_found():
    """Test getting non-existent project."""
    response = client.get("/api/projects/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_project_with_stats():
    """Test that project stats are calculated correctly."""
    db = TestingSessionLocal()
    try:
        # Create project with interview and notes
        project = Project(title="Test Project")
        db.add(project)
        db.commit()
        db.refresh(project)

        interview = Interview(
            project_id=project.id,
            interview_title="Test Interview",
            background_context="Some context",
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        # Add notes
        note1 = Note(interview_id=interview.id, title="Note 1")
        note2 = Note(interview_id=interview.id, title="Note 2")
        db.add_all([note1, note2])
        db.commit()

        # Get project via API
        response = client.get(f"/api/projects/{project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["stats"]["note_count"] == 2
        assert data["stats"]["has_context"] is True
    finally:
        db.close()


def test_update_project():
    """Test updating a project title."""
    # Create project
    create_response = client.post(
        "/api/projects",
        json={"title": "Original Title"},
    )
    project_id = create_response.json()["id"]

    # Update project
    response = client.put(
        f"/api/projects/{project_id}",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["id"] == project_id


def test_update_project_not_found():
    """Test updating non-existent project."""
    response = client.put(
        "/api/projects/999",
        json={"title": "Updated Title"},
    )
    assert response.status_code == 404


def test_update_project_empty_title():
    """Test updating project with empty title fails."""
    # Create project
    create_response = client.post(
        "/api/projects",
        json={"title": "Original Title"},
    )
    project_id = create_response.json()["id"]

    # Try to update with empty title
    response = client.put(
        f"/api/projects/{project_id}",
        json={"title": ""},
    )
    assert response.status_code == 422  # Validation error


def test_delete_project():
    """Test deleting a project."""
    # Create project
    create_response = client.post(
        "/api/projects",
        json={"title": "To Delete"},
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 404


def test_delete_project_not_found():
    """Test deleting non-existent project."""
    response = client.delete("/api/projects/999")
    assert response.status_code == 404


def test_delete_project_cascades():
    """Test that deleting a project also deletes related data."""
    db = TestingSessionLocal()
    try:
        # Create project with interview and notes
        project = Project(title="Test Project")
        db.add(project)
        db.commit()
        db.refresh(project)

        interview = Interview(
            project_id=project.id,
            interview_title="Test Interview",
        )
        db.add(interview)
        db.commit()
        db.refresh(interview)

        note = Note(interview_id=interview.id, title="Note 1")
        db.add(note)
        db.commit()

        project_id = project.id
        interview_id = interview.id
        note_id = note.id

        # Delete project via API
        response = client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204

        # Verify cascading delete
        assert db.query(Project).filter_by(id=project_id).first() is None
        assert db.query(Interview).filter_by(id=interview_id).first() is None
        assert db.query(Note).filter_by(id=note_id).first() is None
    finally:
        db.close()
