"""Pydantic schemas for Interview Prep API."""
from pydantic import BaseModel, Field, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class LLMProvider(str, Enum):
    """LLM provider options for user selection."""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"


class ItemType(str, Enum):
    """Type of note item content."""
    TEXT = "text"
    IMAGE = "image"


class ProvenanceType(str, Enum):
    """Source of note item."""
    WEB = "web"
    MANUAL = "manual"


class BlockType(str, Enum):
    """Type of canvas block."""
    HEADING = "heading"
    PARAGRAPH = "paragraph"


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    """Base project schema."""
    title: str = Field(..., min_length=1, max_length=500, description="Project title")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)


class ProjectStats(BaseModel):
    """Project statistics."""
    note_count: int = Field(default=0, description="Number of notes in the project")
    has_context: bool = Field(default=False, description="Whether background context exists")


class ProjectResponse(ProjectBase):
    """Response schema for project."""
    id: int
    last_modified: datetime
    created_at: datetime
    stats: Optional[ProjectStats] = None

    class Config:
        from_attributes = True


# ==================== NoteItem Schemas ====================

class NoteItemBase(BaseModel):
    """Base note item schema."""
    type: ItemType
    content: str = Field(..., min_length=1, max_length=50000, description="Item content (text or image URL)")
    provenance: ProvenanceType = ProvenanceType.MANUAL
    source_title: Optional[str] = Field(None, max_length=500)
    source_domain: Optional[str] = Field(None, max_length=255)


class NoteItemCreate(NoteItemBase):
    """Schema for creating a note item."""
    order_index: int = Field(default=0, ge=0)


class NoteItemUpdate(BaseModel):
    """Schema for updating a note item."""
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    order_index: Optional[int] = Field(None, ge=0)


class NoteItemResponse(NoteItemBase):
    """Response schema for note item."""
    id: int
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Note Schemas ====================

class NoteBase(BaseModel):
    """Base note schema."""
    title: str = Field(..., min_length=1, max_length=500, description="Note title")


class NoteCreate(NoteBase):
    """Schema for creating a note."""
    order_index: int = Field(default=0, ge=0)
    items: List[NoteItemCreate] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    """Schema for updating a note."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    order_index: Optional[int] = Field(None, ge=0)


class NoteResponse(NoteBase):
    """Response schema for note."""
    id: int
    order_index: int
    created_at: datetime
    items: List[NoteItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== CanvasBlock Schemas ====================

class CanvasBlockBase(BaseModel):
    """Base canvas block schema."""
    type: BlockType
    text: str = Field(..., min_length=1, max_length=50000, description="Block text content")


class CanvasBlockCreate(CanvasBlockBase):
    """Schema for creating a canvas block."""
    order_index: int = Field(default=0, ge=0)


class CanvasBlockUpdate(BaseModel):
    """Schema for updating a canvas block."""
    text: Optional[str] = Field(None, min_length=1, max_length=50000)
    order_index: Optional[int] = Field(None, ge=0)


class CanvasBlockResponse(CanvasBlockBase):
    """Response schema for canvas block."""
    id: int
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Interview Schemas ====================

class InterviewBase(BaseModel):
    """Base interview schema."""
    interview_title: str = Field(..., min_length=1, max_length=500, description="Interview title")
    background_context: str = Field(default="", max_length=50000, description="Background context for the interview")


class InterviewCreate(InterviewBase):
    """Schema for creating an interview."""
    project_id: int = Field(..., gt=0)
    notes: List[NoteCreate] = Field(default_factory=list)
    canvas_blocks: List[CanvasBlockCreate] = Field(default_factory=list)


class InterviewUpdate(BaseModel):
    """Schema for updating an interview."""
    interview_title: Optional[str] = Field(None, min_length=1, max_length=500)
    background_context: Optional[str] = Field(None, max_length=50000)


class InterviewFullUpdate(InterviewBase):
    """Schema for full interview update (including nested entities)."""
    notes: List[NoteCreate] = Field(default_factory=list)
    canvas_blocks: List[CanvasBlockCreate] = Field(default_factory=list)


class InterviewResponse(InterviewBase):
    """Response schema for interview."""
    id: int
    project_id: int
    timestamp: datetime
    notes: List[NoteResponse] = Field(default_factory=list)
    canvas_blocks: List[CanvasBlockResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ==================== Search Schemas ====================

class SearchRequest(BaseModel):
    """Request schema for search endpoint."""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider for summary generation")
    background_context: Optional[str] = Field(None, max_length=50000, description="Optional interview context for better search results")


class WebSearchResult(BaseModel):
    """Individual web search result."""
    title: str
    url: HttpUrl
    snippet: str
    domain: str


class ImageSearchResult(BaseModel):
    """Individual image search result."""
    url: HttpUrl
    thumbnail_url: Optional[HttpUrl] = None
    title: Optional[str] = None
    source_url: Optional[HttpUrl] = None


class SearchCitation(BaseModel):
    """Citation from search summary."""
    number: int
    title: str
    url: HttpUrl


class SearchResponse(BaseModel):
    """Response schema for search endpoint."""
    summary: str = Field(..., description="AI-generated summary of search results")
    citations: List[SearchCitation] = Field(default_factory=list)
    web_results: List[WebSearchResult] = Field(default_factory=list)
    image_results: List[ImageSearchResult] = Field(default_factory=list)


# ==================== Text Refinement Schemas ====================

class RefinementAction(str, Enum):
    """Available text refinement actions."""
    IMPROVE = "improve"
    SHORTEN = "shorten"
    CHANGE_TONE = "change_tone"


class TextRefinementRequest(BaseModel):
    """Request schema for text refinement."""
    block_id: int = Field(..., gt=0, description="ID of the canvas block to refine")
    action: RefinementAction = Field(..., description="Refinement action to perform")
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider for refinement")


class TextRefinementResponse(BaseModel):
    """Response schema for text refinement."""
    original_text: str
    refined_text: str
    action: RefinementAction


# ==================== Reorder Schemas ====================

class ReorderRequest(BaseModel):
    """Request schema for reordering items."""
    item_ids: List[int] = Field(..., min_length=1, description="Ordered list of item IDs")

    @field_validator('item_ids')
    @classmethod
    def validate_unique_ids(cls, v):
        """Ensure all IDs are unique."""
        if len(v) != len(set(v)):
            raise ValueError('item_ids must contain unique values')
        return v


# ==================== Error Response Schemas ====================

class ErrorDetail(BaseModel):
    """Error detail schema."""
    field: Optional[str] = None
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    errors: Optional[List[ErrorDetail]] = None
