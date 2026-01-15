"""Tests for interview preparation database models."""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.database import Base
from backend.models.interview_models import (
    Project,
    Interview,
    Note,
    NoteItem,
    CanvasBlock,
    ItemType,
    ProvenanceType,
    BlockType,
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_project(db_session):
    """Test creating a project."""
    project = Project(title="Test Interview Project")
    db_session.add(project)
    db_session.commit()

    assert project.id is not None
    assert project.title == "Test Interview Project"
    assert isinstance(project.last_modified, datetime)
    assert isinstance(project.created_at, datetime)


def test_create_interview(db_session):
    """Test creating an interview with project relationship."""
    project = Project(title="Test Project")
    db_session.add(project)
    db_session.commit()

    interview = Interview(
        project_id=project.id,
        interview_title="Interview with Guest",
        background_context="Background information about the guest",
    )
    db_session.add(interview)
    db_session.commit()

    assert interview.id is not None
    assert interview.project_id == project.id
    assert interview.interview_title == "Interview with Guest"
    assert interview.background_context == "Background information about the guest"
    assert interview.project.title == "Test Project"


def test_create_note_with_items(db_session):
    """Test creating notes with items."""
    project = Project(title="Test Project")
    interview = Interview(
        project=project,
        interview_title="Test Interview",
    )
    note = Note(
        interview=interview,
        title="Research Notes",
        order_index=0,
    )
    db_session.add(project)
    db_session.commit()

    # Add text item
    text_item = NoteItem(
        note=note,
        type=ItemType.TEXT,
        content="Important fact from research",
        provenance=ProvenanceType.WEB,
        source_title="Source Article",
        source_domain="example.com",
        order_index=0,
    )
    # Add image item
    image_item = NoteItem(
        note=note,
        type=ItemType.IMAGE,
        content="https://example.com/image.jpg",
        provenance=ProvenanceType.WEB,
        source_domain="example.com",
        order_index=1,
    )
    db_session.add_all([text_item, image_item])
    db_session.commit()

    assert note.id is not None
    assert len(note.items) == 2
    assert note.items[0].type == ItemType.TEXT
    assert note.items[1].type == ItemType.IMAGE
    assert note.items[0].provenance == ProvenanceType.WEB


def test_create_canvas_blocks(db_session):
    """Test creating canvas blocks for outline."""
    project = Project(title="Test Project")
    interview = Interview(
        project=project,
        interview_title="Test Interview",
    )
    db_session.add(project)
    db_session.commit()

    heading = CanvasBlock(
        interview=interview,
        type=BlockType.HEADING,
        text="Introduction",
        order_index=0,
    )
    paragraph = CanvasBlock(
        interview=interview,
        type=BlockType.PARAGRAPH,
        text="This is the introduction paragraph.",
        order_index=1,
    )
    db_session.add_all([heading, paragraph])
    db_session.commit()

    assert len(interview.canvas_blocks) == 2
    assert interview.canvas_blocks[0].type == BlockType.HEADING
    assert interview.canvas_blocks[1].type == BlockType.PARAGRAPH


def test_cascade_delete_project(db_session):
    """Test that deleting a project cascades to interviews and related entities."""
    project = Project(title="Test Project")
    interview = Interview(
        project=project,
        interview_title="Test Interview",
    )
    note = Note(
        interview=interview,
        title="Notes",
    )
    item = NoteItem(
        note=note,
        type=ItemType.TEXT,
        content="Test content",
    )
    db_session.add(project)
    db_session.commit()

    project_id = project.id
    interview_id = interview.id

    # Delete project
    db_session.delete(project)
    db_session.commit()

    # Verify cascading delete
    assert db_session.query(Project).filter_by(id=project_id).first() is None
    assert db_session.query(Interview).filter_by(id=interview_id).first() is None


def test_note_ordering(db_session):
    """Test that notes are ordered by order_index."""
    project = Project(title="Test Project")
    interview = Interview(
        project=project,
        interview_title="Test Interview",
    )
    note1 = Note(interview=interview, title="Note 1", order_index=2)
    note2 = Note(interview=interview, title="Note 2", order_index=0)
    note3 = Note(interview=interview, title="Note 3", order_index=1)
    db_session.add(project)
    db_session.commit()

    # Notes should be ordered by order_index
    notes = interview.notes
    assert notes[0].title == "Note 2"  # order_index=0
    assert notes[1].title == "Note 3"  # order_index=1
    assert notes[2].title == "Note 1"  # order_index=2


def test_item_ordering(db_session):
    """Test that items within a note are ordered by order_index."""
    project = Project(title="Test Project")
    interview = Interview(project=project, interview_title="Test Interview")
    note = Note(interview=interview, title="Notes")
    item1 = NoteItem(note=note, type=ItemType.TEXT, content="Item 1", order_index=2)
    item2 = NoteItem(note=note, type=ItemType.TEXT, content="Item 2", order_index=0)
    item3 = NoteItem(note=note, type=ItemType.TEXT, content="Item 3", order_index=1)
    db_session.add(project)
    db_session.commit()

    # Items should be ordered by order_index
    items = note.items
    assert items[0].content == "Item 2"  # order_index=0
    assert items[1].content == "Item 3"  # order_index=1
    assert items[2].content == "Item 1"  # order_index=2
