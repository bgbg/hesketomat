from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import os

Base = declarative_base()


class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    rss_url = Column(String, unique=True)
    image_url = Column(String)
    homepage_url = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    episodes = relationship(
        "Episode", back_populates="podcast", cascade="all, delete-orphan"
    )


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"))
    title = Column(String, index=True)
    description = Column(String)
    url = Column(String)
    image_url = Column(String)
    publish_date = Column(DateTime)
    podcast = relationship("Podcast", back_populates="episodes")


# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Database URL will be loaded from environment variables
SQLALCHEMY_DATABASE_URL = "sqlite:///data/podcasts.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


def create_tables():
    # Import interview models to ensure they're registered with Base
    from backend.models import interview_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
