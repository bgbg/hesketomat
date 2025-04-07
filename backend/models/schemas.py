from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class PodcastBase(BaseModel):
    title: str
    description: str
    rss_url: HttpUrl
    image_url: Optional[HttpUrl] = None
    homepage_url: Optional[HttpUrl] = None

class PodcastCreate(PodcastBase):
    pass

class Podcast(PodcastBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class EpisodeBase(BaseModel):
    title: str
    description: str
    url: HttpUrl
    image_url: Optional[HttpUrl] = None
    publish_date: datetime

class EpisodeCreate(EpisodeBase):
    podcast_id: int

class Episode(EpisodeBase):
    id: int
    podcast_id: int

    class Config:
        from_attributes = True

class SearchWeights(BaseModel):
    title_weight: int
    description_weight: int 