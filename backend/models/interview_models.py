from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.models.database import Base
import enum


class Project(Base):
    """Project metadata for interview preparation sessions."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interviews = relationship(
        "Interview", back_populates="project", cascade="all, delete-orphan"
    )


class Interview(Base):
    """Interview workspace containing notes, context, and outline."""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    interview_title = Column(String, nullable=False)
    background_context = Column(Text, default="")
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="interviews")
    notes = relationship(
        "Note", back_populates="interview", cascade="all, delete-orphan", order_by="Note.order_index"
    )
    canvas_blocks = relationship(
        "CanvasBlock", back_populates="interview", cascade="all, delete-orphan", order_by="CanvasBlock.order_index"
    )


class Note(Base):
    """Note bucket containing items (text snippets or images)."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    order_index = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="notes")
    items = relationship(
        "NoteItem", back_populates="note", cascade="all, delete-orphan", order_by="NoteItem.order_index"
    )


class ItemType(str, enum.Enum):
    """Type of note item content."""
    TEXT = "text"
    IMAGE = "image"


class ProvenanceType(str, enum.Enum):
    """Source of note item."""
    WEB = "web"
    MANUAL = "manual"


class NoteItem(Base):
    """Individual item within a note (text snippet or image)."""
    __tablename__ = "note_items"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False, index=True)
    type = Column(Enum(ItemType), nullable=False)
    content = Column(Text, nullable=False)  # text content or image URL
    provenance = Column(Enum(ProvenanceType), default=ProvenanceType.MANUAL)
    source_title = Column(String, nullable=True)  # for web provenance
    source_domain = Column(String, nullable=True)  # for web provenance
    order_index = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    note = relationship("Note", back_populates="items")


class BlockType(str, enum.Enum):
    """Type of canvas block."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"


class CanvasBlock(Base):
    """Block in the outline canvas (heading or paragraph)."""
    __tablename__ = "canvas_blocks"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False, index=True)
    type = Column(Enum(BlockType), nullable=False)
    text = Column(Text, nullable=False)
    order_index = Column(Integer, default=0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    interview = relationship("Interview", back_populates="canvas_blocks")
