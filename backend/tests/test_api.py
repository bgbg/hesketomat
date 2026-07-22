from datetime import datetime, timedelta

import pytest

from backend.models.database import Episode
from backend.services import podcast_service

# `client` and `db_session` come from conftest.py and share a per-test database.

PODCAST = {
    "title": "Test Podcast",
    "description": "Test Description",
    "rss_url": "https://example.com/feed.xml",
    "image_url": "https://example.com/image.jpg",
}


@pytest.fixture
def podcast_with_episodes(client, db_session):
    """A podcast with 150 episodes, newest first, to exercise pagination."""
    podcast_id = client.post("/api/podcasts/", json=PODCAST).json()["id"]
    base = datetime(2026, 1, 1)
    db_session.add_all(
        [
            Episode(
                podcast_id=podcast_id,
                title=f"Episode {i}",
                description=f"Description {i}",
                url=f"https://example.com/ep/{i}",
                publish_date=base - timedelta(days=i),
            )
            for i in range(150)
        ]
    )
    db_session.commit()
    return podcast_id


def test_validate_rss_feed_invalid(client, monkeypatch):
    # Stubbed so the test does not depend on network access.
    monkeypatch.setattr(
        podcast_service,
        "validate_rss_feed",
        lambda rss_url: (False, "Invalid RSS feed format", None, None, None),
    )
    response = client.post(
        "/api/podcasts/validate", json={"rss_url": "https://example.com/invalid.xml"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["error"] == "Invalid RSS feed format"


def test_validate_rss_feed_valid(client, monkeypatch):
    monkeypatch.setattr(
        podcast_service,
        "validate_rss_feed",
        lambda rss_url: (
            True,
            "Test Podcast",
            "https://example.com",
            "https://example.com/image.jpg",
            "Test Description",
        ),
    )
    response = client.post(
        "/api/podcasts/validate", json={"rss_url": "https://example.com/feed.xml"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["podcast"]["title"] == "Test Podcast"


def test_create_podcast(client):
    response = client.post("/api/podcasts/", json=PODCAST)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Podcast"
    assert data["description"] == "Test Description"


def test_create_duplicate_podcast(client):
    client.post("/api/podcasts/", json=PODCAST)

    # Same rss_url, different title
    response = client.post(
        "/api/podcasts/", json={**PODCAST, "title": "Test Podcast 2"}
    )
    assert response.status_code == 400


def test_get_podcasts(client):
    client.post("/api/podcasts/", json=PODCAST)

    response = client.get("/api/podcasts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Podcast"


def test_get_podcasts_with_counts(client):
    client.post("/api/podcasts/", json=PODCAST)

    response = client.get("/api/podcasts/with_counts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Test Podcast"
    assert data[0]["episode_count"] == 0


def test_search_episodes_empty(client):
    response = client.post(
        "/api/episodes/search", json={"query": "", "podcast_ids": []}
    )
    assert response.status_code == 200
    assert response.json() == []


def test_search_episodes_with_matches(client):
    podcast_id = client.post("/api/podcasts/", json=PODCAST).json()["id"]

    response = client.post(
        "/api/episodes/search", json={"query": "test", "podcast_ids": [podcast_id]}
    )
    assert response.status_code == 200
    for item in response.json():
        assert "episode" in item
        assert "matches" in item


def test_search_returns_all_episodes_when_no_limit_given(podcast_with_episodes, client):
    """No limit means no cap — the list used to be silently truncated at 100."""
    response = client.post(
        "/api/episodes/search",
        json={"query": "", "podcast_ids": [podcast_with_episodes]},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 150
    # Newest first
    assert data[0]["episode"]["title"] == "Episode 0"


def test_search_episodes_honours_skip_and_limit(podcast_with_episodes, client):
    response = client.post(
        "/api/episodes/search",
        json={
            "query": "",
            "podcast_ids": [podcast_with_episodes],
            "skip": 2,
            "limit": 3,
        },
    )
    assert response.status_code == 200
    titles = [item["episode"]["title"] for item in response.json()]
    assert titles == ["Episode 2", "Episode 3", "Episode 4"]


def test_get_episodes_returns_all_when_no_limit_given(podcast_with_episodes, client):
    response = client.get(
        "/api/episodes", params={"podcast_ids": [podcast_with_episodes]}
    )
    assert response.status_code == 200
    assert len(response.json()) == 150


def test_get_episodes_honours_limit(podcast_with_episodes, client):
    response = client.get(
        "/api/episodes",
        params={"podcast_ids": [podcast_with_episodes], "skip": 1, "limit": 5},
    )
    assert response.status_code == 200
    assert len(response.json()) == 5


def test_get_episodes(client):
    podcast_id = client.post("/api/podcasts/", json=PODCAST).json()["id"]

    response = client.get("/api/episodes", params={"podcast_ids": [podcast_id]})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_episodes(client):
    podcast_id = client.post("/api/podcasts/", json=PODCAST).json()["id"]

    response = client.post("/api/episodes/delete", json=[podcast_id])
    assert response.status_code == 200
    assert response.json()["message"] == "Episodes deleted successfully"


def test_get_db_status(client):
    client.post("/api/podcasts/", json=PODCAST)

    response = client.get("/api/status_db")
    assert response.status_code == 200
    data = response.json()
    assert data["podcasts"] == 1
    assert data["episodes"] == 0
