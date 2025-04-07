import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.models.database import Base
from backend.models.database_session import get_db

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_validate_rss_feed_invalid():
    response = client.post("/api/podcasts/validate", params={"rss_url": "https://example.com/invalid.xml"})
    assert response.status_code == 400

def test_create_podcast():
    response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Podcast"
    assert data["description"] == "Test Description"

def test_create_duplicate_podcast():
    # Create first podcast
    client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    
    # Try to create duplicate
    response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast 2",
            "description": "Test Description 2",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image2.jpg"
        }
    )
    assert response.status_code == 400

def test_get_podcasts():
    # Create a podcast
    client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    
    response = client.get("/api/podcasts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Podcast"

def test_get_podcasts_with_counts():
    # Create a podcast
    response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    
    response = client.get("/api/podcasts/with_counts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Podcast"
    assert "episode_count" in data[0]
    assert data[0]["episode_count"] == 0

def test_search_episodes_empty():
    response = client.get("/api/episodes/search")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_search_episodes_with_matches():
    # Create a podcast first
    podcast_response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    podcast_id = podcast_response.json()["id"]
    
    # Search episodes
    response = client.get("/api/episodes/search", params={
        "query": "test",
        "podcast_ids": [podcast_id]
    })
    assert response.status_code == 200
    data = response.json()
    for item in data:
        assert "episode" in item
        assert "matches" in item

def test_get_episodes():
    # Create a podcast first
    podcast_response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    podcast_id = podcast_response.json()["id"]
    
    # Get episodes
    response = client.get("/api/episodes", params={"podcast_ids": [podcast_id]})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_episodes():
    # Create a podcast first
    podcast_response = client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    podcast_id = podcast_response.json()["id"]
    
    # Delete episodes
    response = client.post(
        "/api/episodes/delete",
        json=[podcast_id]
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Episodes deleted successfully" 

def test_get_db_status():
    # Create a podcast first
    client.post(
        "/api/podcasts/",
        json={
            "title": "Test Podcast",
            "description": "Test Description",
            "rss_url": "https://example.com/feed.xml",
            "image_url": "https://example.com/image.jpg"
        }
    )
    
    response = client.get("/api/status_db")
    assert response.status_code == 200
    data = response.json()
    assert "podcasts" in data
    assert "episodes" in data
    assert data["podcasts"] == 1
    assert data["episodes"] == 0 