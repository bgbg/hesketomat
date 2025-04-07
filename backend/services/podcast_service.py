import feedparser
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple
from ..models.database import Podcast, Episode
from ..models.schemas import PodcastCreate, EpisodeCreate
from sqlalchemy import or_, func
import re

def create_podcast(db: Session, podcast: PodcastCreate) -> Podcast:
    db_podcast = Podcast(
        title=podcast.title,
        description=podcast.description,
        rss_url=str(podcast.rss_url),
        image_url=str(podcast.image_url) if podcast.image_url else None,
        homepage_url=str(podcast.homepage_url) if podcast.homepage_url else None,
        last_updated=datetime.utcnow()
    )
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast

def get_podcast(db: Session, podcast_id: int) -> Optional[Podcast]:
    return db.query(Podcast).filter(Podcast.id == podcast_id).first()

def get_podcast_by_rss(db: Session, rss_url: str) -> Optional[Podcast]:
    return db.query(Podcast).filter(Podcast.rss_url == rss_url).first()

def get_podcasts(db: Session, skip: int = 0, limit: int = 100) -> List[Podcast]:
    return db.query(Podcast)\
        .order_by(Podcast.last_updated.asc())\
        .offset(skip).limit(limit).all()

def get_podcast_with_episode_count(db: Session) -> List[Dict]:
    results = db.query(
        Podcast,
        func.count(Episode.id).label('episode_count')
    ).outerjoin(Episode).group_by(Podcast.id).all()
    
    return [
        {
            "id": podcast.id,
            "title": podcast.title,
            "description": podcast.description,
            "rss_url": podcast.rss_url,
            "image_url": podcast.image_url,
            "homepage_url": podcast.homepage_url,
            "last_updated": podcast.last_updated,
            "episode_count": count
        }
        for podcast, count in results
    ]

def validate_rss_feed(rss_url: str) -> Tuple[bool, str, Optional[str], Optional[str], Optional[str]]:
    feed = feedparser.parse(rss_url)
    if feed.bozo:
        return False, "Invalid RSS feed format", None, None, None
    if not hasattr(feed, 'entries'):
        return False, "No entries found in feed", None, None, None
    if not hasattr(feed.feed, 'title'):
        return False, "No title found in feed", None, None, None
    if not hasattr(feed.feed, 'description'):
        return False, "No description found in feed", None, None, None
    
    # Try to get the homepage URL from the feed
    homepage_url = None
    if hasattr(feed.feed, 'link'):
        homepage_url = feed.feed.link
    
    # Try to get the image URL from the feed
    image_url = None
    if hasattr(feed.feed, 'image') and hasattr(feed.feed.image, 'href'):
        image_url = feed.feed.image.href
    
    description = feed.feed.description
    
    return True, feed.feed.title, homepage_url, image_url, description

def update_podcast_episodes(db: Session, podcast: Podcast) -> List[Episode]:
    feed = feedparser.parse(podcast.rss_url)
    new_episodes = []
    
    for entry in feed.entries:
        # Check if episode already exists
        existing = db.query(Episode).filter(
            Episode.url == entry.link,
            Episode.podcast_id == podcast.id
        ).first()
        
        if not existing:
            episode = Episode(
                podcast_id=podcast.id,
                title=entry.title,
                description=entry.description,
                url=entry.link,
                image_url=entry.get('image', {}).get('href', podcast.image_url),
                publish_date=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow()
            )
            db.add(episode)
            new_episodes.append(episode)
    
    podcast.last_updated = datetime.utcnow()
    db.commit()
    return new_episodes

def delete_all_episodes(db: Session, podcast_ids: List[int]) -> None:
    db.query(Episode).filter(Episode.podcast_id.in_(podcast_ids)).delete(synchronize_session=False)
    db.commit()

def get_episodes_for_podcasts(
    db: Session,
    podcast_ids: List[int],
    skip: int = 0,
    limit: int = 100
) -> List[Episode]:
    return db.query(Episode)\
        .filter(Episode.podcast_id.in_(podcast_ids))\
        .order_by(Episode.publish_date.desc())\
        .offset(skip).limit(limit).all()

def search_episodes(
    db: Session,
    query: str,
    podcast_ids: List[int],
    title_weight: int = 50,
    description_weight: int = 50,
    cap_n_matches: int = 10,
    skip: int = 0,
    limit: int = 100
) -> List[Dict]:
    if not query:
        episodes = db.query(Episode)\
            .filter(Episode.podcast_id.in_(podcast_ids))\
            .order_by(Episode.publish_date.desc())\
            .offset(skip).limit(limit).all()
        return [{"episode": episode, "matches": None} for episode in episodes]
    
    total = title_weight + description_weight
    if total <= 0:
        title_weight = 50
        description_weight = 50
        total = 100
    else:
        title_weight = title_weight / total * 100
        description_weight = description_weight / total * 100
    # Get all episodes for the selected podcasts
    episodes = db.query(Episode)\
        .filter(Episode.podcast_id.in_(podcast_ids))\
        .all()
    
    # Compile regex pattern once
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    
    # Calculate scores for each episode
    scored_episodes = []
    for episode in episodes:
        # Count matches in title and description
        title_matches = len(list(pattern.finditer(episode.title)))
        desc_matches = len(list(pattern.finditer(episode.description)))
        
        # Cap the number of matches
        title_matches = min(title_matches, cap_n_matches)
        desc_matches = min(desc_matches, cap_n_matches)
        
        score = title_matches * title_weight + desc_matches * description_weight
        
        if score > 0:
            scored_episodes.append({
                "episode": episode,
                "score": score,
                "matches": {
                    "title": [m.span() for m in pattern.finditer(episode.title)],
                    "description": [m.span() for m in pattern.finditer(episode.description)]
                }
            })
    
    # Sort by score (descending) and then by publish date (descending)
    sorted_episodes = sorted(
        scored_episodes,
        key=lambda x: (x["score"], x["episode"].publish_date),
        reverse=True
    )

    # Apply pagination
    paginated_episodes = sorted_episodes[skip:skip + limit]
    
    # Return results in the expected format
    return [{"episode": item["episode"], "matches": item["matches"]} for item in paginated_episodes]

def get_db_stats(db: Session) -> Dict[str, int]:
    """Get the number of rows in each database table."""
    return {
        "podcasts": db.query(func.count(Podcast.id)).scalar(),
        "episodes": db.query(func.count(Episode.id)).scalar()
    }

def delete_podcast(db: Session, podcast_id: int) -> None:
    podcast = db.query(Podcast).filter(Podcast.id == podcast_id).first()
    if podcast:
        db.delete(podcast)
        db.commit() 