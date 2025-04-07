from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from ..models.database_session import get_db
from ..models.schemas import Podcast, PodcastCreate, Episode, SearchWeights
from ..services import podcast_service
from pydantic import BaseModel

router = APIRouter()


class RssUrlInput(BaseModel):
    rss_url: str


@router.post("/podcasts/validate")
def validate_rss_feed(
    input_data: RssUrlInput,
):
    is_valid, message, homepage_url, image_url, description = (
        podcast_service.validate_rss_feed(input_data.rss_url)
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    return {
        "title": message,
        "description": description,
        "homepage_url": (
            homepage_url
            if homepage_url and homepage_url.startswith(("http://", "https://"))
            else None
        ),
        "image_url": (
            image_url
            if image_url and image_url.startswith(("http://", "https://"))
            else None
        ),
    }


@router.post("/podcasts/", response_model=Podcast)
def create_podcast(podcast: PodcastCreate, db: Session = Depends(get_db)):
    db_podcast = podcast_service.get_podcast_by_rss(db, str(podcast.rss_url))
    if db_podcast:
        raise HTTPException(
            status_code=400, detail="Podcast with this RSS feed already exists"
        )
    return podcast_service.create_podcast(db=db, podcast=podcast)


@router.get("/podcasts/", response_model=List[Podcast])
def read_podcasts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    podcasts = podcast_service.get_podcasts(db, skip=skip, limit=limit)
    return podcasts


@router.get("/podcasts/with_counts", response_model=List[Dict])
def get_podcasts_with_counts(db: Session = Depends(get_db)):
    return podcast_service.get_podcast_with_episode_count(db)


@router.post("/podcasts/{podcast_id}/refresh")
def refresh_podcast(podcast_id: int, db: Session = Depends(get_db)):
    podcast = podcast_service.get_podcast(db, podcast_id)
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    new_episodes = podcast_service.update_podcast_episodes(db, podcast)
    return {"message": f"Added {len(new_episodes)} new episodes"}


@router.post("/episodes/delete")
def delete_episodes(podcast_ids: List[int] = Body(...), db: Session = Depends(get_db)):
    podcast_service.delete_all_episodes(db, podcast_ids)
    return {"message": "Episodes deleted successfully"}


@router.get("/episodes", response_model=List[Episode])
def get_episodes(
    podcast_ids: List[int] = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return podcast_service.get_episodes_for_podcasts(db, podcast_ids, skip, limit)


@router.post("/episodes/search")
def search_episodes(
    query: str = Body(""),
    podcast_ids: List[int] = Body(...),
    title_weight: int = Body(50),
    description_weight: int = Body(50),
    cap_n_matches: int = Body(10),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    episodes = podcast_service.search_episodes(
        db,
        query,
        podcast_ids,
        title_weight,
        description_weight,
        cap_n_matches,
        skip,
        limit,
    )
    return episodes


@router.get("/status_db")
def get_db_status(db: Session = Depends(get_db)):
    """Get the number of rows in each database table."""
    return podcast_service.get_db_stats(db)


@router.delete("/podcasts/{podcast_id}")
def delete_podcast(podcast_id: int, db: Session = Depends(get_db)):
    podcast = podcast_service.get_podcast(db, podcast_id)
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    podcast_service.delete_podcast(db, podcast_id)
    return {"message": "Podcast deleted successfully"}
