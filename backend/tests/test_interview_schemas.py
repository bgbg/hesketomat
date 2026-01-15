"""Tests for interview preparation Pydantic schemas."""
import pytest
from pydantic import ValidationError
from backend.models.interview_schemas import (
    ProjectCreate,
    NoteCreate,
    NoteItemCreate,
    CanvasBlockCreate,
    InterviewCreate,
    SearchRequest,
    TextRefinementRequest,
    ReorderRequest,
    LLMProvider,
    ItemType,
    ProvenanceType,
    BlockType,
    RefinementAction,
)


def test_project_create_valid():
    """Test valid project creation schema."""
    project = ProjectCreate(title="My Interview Project")
    assert project.title == "My Interview Project"


def test_project_create_empty_title():
    """Test project creation with empty title fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(title="")
    assert "at least 1 character" in str(exc_info.value) or "string_too_short" in str(exc_info.value)


def test_project_create_long_title():
    """Test project creation with too long title fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        ProjectCreate(title="a" * 501)
    assert "at most 500 characters" in str(exc_info.value) or "string_too_long" in str(exc_info.value)


def test_note_item_create_valid():
    """Test valid note item creation."""
    item = NoteItemCreate(
        type=ItemType.TEXT,
        content="This is a text snippet from research",
        provenance=ProvenanceType.WEB,
        source_title="Research Article",
        source_domain="example.com",
        order_index=0,
    )
    assert item.type == ItemType.TEXT
    assert item.provenance == ProvenanceType.WEB
    assert item.order_index == 0


def test_note_item_create_image():
    """Test creating an image note item."""
    item = NoteItemCreate(
        type=ItemType.IMAGE,
        content="https://example.com/image.jpg",
        provenance=ProvenanceType.WEB,
        source_domain="example.com",
    )
    assert item.type == ItemType.IMAGE
    assert "image.jpg" in item.content


def test_note_item_negative_order():
    """Test note item with negative order_index fails validation."""
    with pytest.raises(ValidationError) as exc_info:
        NoteItemCreate(
            type=ItemType.TEXT,
            content="Test",
            order_index=-1,
        )
    assert "greater_than_equal" in str(exc_info.value)


def test_note_create_with_items():
    """Test creating a note with items."""
    note = NoteCreate(
        title="Research Notes",
        order_index=0,
        items=[
            NoteItemCreate(
                type=ItemType.TEXT,
                content="Fact 1",
            ),
            NoteItemCreate(
                type=ItemType.TEXT,
                content="Fact 2",
            ),
        ],
    )
    assert note.title == "Research Notes"
    assert len(note.items) == 2


def test_canvas_block_create_heading():
    """Test creating a heading canvas block."""
    block = CanvasBlockCreate(
        type=BlockType.HEADING,
        text="Introduction",
        order_index=0,
    )
    assert block.type == BlockType.HEADING
    assert block.text == "Introduction"


def test_canvas_block_create_paragraph():
    """Test creating a paragraph canvas block."""
    block = CanvasBlockCreate(
        type=BlockType.PARAGRAPH,
        text="This is the introduction paragraph with detailed information.",
        order_index=1,
    )
    assert block.type == BlockType.PARAGRAPH


def test_interview_create_valid():
    """Test valid interview creation."""
    interview = InterviewCreate(
        project_id=1,
        interview_title="Interview with John Doe",
        background_context="John is an expert in AI research",
        notes=[
            NoteCreate(title="Background", order_index=0),
            NoteCreate(title="Questions", order_index=1),
        ],
        canvas_blocks=[
            CanvasBlockCreate(type=BlockType.HEADING, text="Intro", order_index=0),
        ],
    )
    assert interview.project_id == 1
    assert len(interview.notes) == 2
    assert len(interview.canvas_blocks) == 1


def test_interview_create_invalid_project_id():
    """Test interview creation with invalid project_id fails."""
    with pytest.raises(ValidationError) as exc_info:
        InterviewCreate(
            project_id=0,  # Must be > 0
            interview_title="Test Interview",
        )
    assert "greater_than" in str(exc_info.value)


def test_search_request_valid():
    """Test valid search request."""
    search = SearchRequest(
        query="AI research trends",
        llm_provider=LLMProvider.OPENAI,
    )
    assert search.query == "AI research trends"
    assert search.llm_provider == LLMProvider.OPENAI


def test_search_request_with_context():
    """Test search request with background context."""
    search = SearchRequest(
        query="recent publications",
        background_context="Interviewing an AI researcher about neural networks",
        llm_provider=LLMProvider.DEEPSEEK,
    )
    assert search.background_context is not None
    assert search.llm_provider == LLMProvider.DEEPSEEK


def test_search_request_empty_query():
    """Test search request with empty query fails."""
    with pytest.raises(ValidationError) as exc_info:
        SearchRequest(query="")
    assert "at least 1 character" in str(exc_info.value) or "string_too_short" in str(exc_info.value)


def test_text_refinement_request_valid():
    """Test valid text refinement request."""
    request = TextRefinementRequest(
        block_id=42,
        action=RefinementAction.IMPROVE,
        llm_provider=LLMProvider.OPENAI,
    )
    assert request.block_id == 42
    assert request.action == RefinementAction.IMPROVE


def test_text_refinement_all_actions():
    """Test all refinement actions."""
    actions = [
        RefinementAction.IMPROVE,
        RefinementAction.SHORTEN,
        RefinementAction.CHANGE_TONE,
    ]
    for action in actions:
        request = TextRefinementRequest(
            block_id=1,
            action=action,
        )
        assert request.action == action


def test_reorder_request_valid():
    """Test valid reorder request."""
    reorder = ReorderRequest(item_ids=[3, 1, 2, 5, 4])
    assert reorder.item_ids == [3, 1, 2, 5, 4]


def test_reorder_request_empty():
    """Test reorder request with empty list fails."""
    with pytest.raises(ValidationError) as exc_info:
        ReorderRequest(item_ids=[])
    assert "at least 1 item" in str(exc_info.value) or "too_short" in str(exc_info.value)


def test_reorder_request_duplicate_ids():
    """Test reorder request with duplicate IDs fails."""
    with pytest.raises(ValidationError) as exc_info:
        ReorderRequest(item_ids=[1, 2, 3, 2, 4])
    assert "unique" in str(exc_info.value).lower()


def test_llm_provider_enum():
    """Test LLM provider enum values."""
    assert LLMProvider.OPENAI.value == "openai"
    assert LLMProvider.DEEPSEEK.value == "deepseek"


def test_item_type_enum():
    """Test item type enum values."""
    assert ItemType.TEXT.value == "text"
    assert ItemType.IMAGE.value == "image"


def test_block_type_enum():
    """Test block type enum values."""
    assert BlockType.HEADING.value == "heading"
    assert BlockType.PARAGRAPH.value == "paragraph"
