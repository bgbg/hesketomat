"""API endpoints for Interview Prep Interviews (workspace)."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from backend.models.database_session import get_db
from backend.models.interview_schemas import (
    InterviewCreate,
    InterviewUpdate,
    InterviewFullUpdate,
    InterviewResponse,
    NoteResponse,
    NoteItemResponse,
    CanvasBlockResponse,
)
from backend.models.interview_models import (
    Interview,
    Note,
    NoteItem,
    CanvasBlock,
    Project,
    ItemType,
    ProvenanceType,
    BlockType,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/interviews", response_model=InterviewResponse, status_code=201)
def create_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
):
    """Create a new interview workspace with nested notes and canvas blocks."""
    logger.info(f"Creating new interview for project {interview.project_id}: {interview.interview_title}")
    try:
        # Verify project exists
        project = db.query(Project).filter(Project.id == interview.project_id).first()
        if not project:
            logger.warning(f"Project not found with ID: {interview.project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        # Create interview
        db_interview = Interview(
            project_id=interview.project_id,
            interview_title=interview.interview_title,
            background_context=interview.background_context,
        )
        db.add(db_interview)
        db.flush()  # Get interview ID without committing

        # Create notes with items
        for note_data in interview.notes:
            db_note = Note(
                interview_id=db_interview.id,
                title=note_data.title,
                order_index=note_data.order_index,
            )
            db.add(db_note)
            db.flush()  # Get note ID

            # Create note items
            for item_data in note_data.items:
                db_item = NoteItem(
                    note_id=db_note.id,
                    type=ItemType(item_data.type),
                    content=item_data.content,
                    provenance=ProvenanceType(item_data.provenance),
                    source_title=item_data.source_title,
                    source_domain=item_data.source_domain,
                    order_index=item_data.order_index,
                )
                db.add(db_item)

        # Create canvas blocks
        for block_data in interview.canvas_blocks:
            db_block = CanvasBlock(
                interview_id=db_interview.id,
                type=BlockType(block_data.type),
                text=block_data.text,
                order_index=block_data.order_index,
            )
            db.add(db_block)

        db.commit()
        db.refresh(db_interview)

        # Load with relationships for response
        db_interview = (
            db.query(Interview)
            .options(
                joinedload(Interview.notes).joinedload(Note.items),
                joinedload(Interview.canvas_blocks),
            )
            .filter(Interview.id == db_interview.id)
            .first()
        )

        logger.info(f"Successfully created interview with ID: {db_interview.id}")
        return InterviewResponse.model_validate(db_interview)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating interview for project {interview.project_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):
    """Get an interview workspace with all nested data."""
    logger.info(f"Retrieving interview with ID: {interview_id}")
    try:
        db_interview = (
            db.query(Interview)
            .options(
                joinedload(Interview.notes).joinedload(Note.items),
                joinedload(Interview.canvas_blocks),
            )
            .filter(Interview.id == interview_id)
            .first()
        )

        if not db_interview:
            logger.warning(f"Interview not found with ID: {interview_id}")
            raise HTTPException(status_code=404, detail="Interview not found")

        logger.info(f"Successfully retrieved interview: {db_interview.interview_title}")
        return InterviewResponse.model_validate(db_interview)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving interview with ID: {interview_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/interviews/{interview_id}", response_model=InterviewResponse)
def update_interview(
    interview_id: int,
    interview_update: InterviewUpdate,
    db: Session = Depends(get_db),
):
    """Update interview metadata (title and/or background context)."""
    logger.info(f"Updating interview with ID: {interview_id}")
    try:
        db_interview = db.query(Interview).filter(Interview.id == interview_id).first()

        if not db_interview:
            logger.warning(f"Interview not found with ID: {interview_id}")
            raise HTTPException(status_code=404, detail="Interview not found")

        # Update fields if provided
        if interview_update.interview_title is not None:
            db_interview.interview_title = interview_update.interview_title
        if interview_update.background_context is not None:
            db_interview.background_context = interview_update.background_context

        db.commit()

        # Reload with relationships
        db_interview = (
            db.query(Interview)
            .options(
                joinedload(Interview.notes).joinedload(Note.items),
                joinedload(Interview.canvas_blocks),
            )
            .filter(Interview.id == interview_id)
            .first()
        )

        logger.info(f"Successfully updated interview: {db_interview.interview_title}")
        return InterviewResponse.model_validate(db_interview)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview with ID: {interview_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/interviews/{interview_id}/autosave", response_model=InterviewResponse)
def autosave_interview(
    interview_id: int,
    interview_data: InterviewFullUpdate,
    db: Session = Depends(get_db),
):
    """Full save/autosave of interview state (replaces all nested entities)."""
    logger.info(f"Autosaving interview with ID: {interview_id}")
    try:
        db_interview = db.query(Interview).filter(Interview.id == interview_id).first()

        if not db_interview:
            logger.warning(f"Interview not found with ID: {interview_id}")
            raise HTTPException(status_code=404, detail="Interview not found")

        # Update interview fields
        db_interview.interview_title = interview_data.interview_title
        db_interview.background_context = interview_data.background_context

        # Delete existing notes and canvas blocks (cascade will delete items)
        db.query(Note).filter(Note.interview_id == interview_id).delete()
        db.query(CanvasBlock).filter(CanvasBlock.interview_id == interview_id).delete()
        db.flush()

        # Recreate notes with items
        for note_data in interview_data.notes:
            db_note = Note(
                interview_id=interview_id,
                title=note_data.title,
                order_index=note_data.order_index,
            )
            db.add(db_note)
            db.flush()

            for item_data in note_data.items:
                db_item = NoteItem(
                    note_id=db_note.id,
                    type=ItemType(item_data.type),
                    content=item_data.content,
                    provenance=ProvenanceType(item_data.provenance),
                    source_title=item_data.source_title,
                    source_domain=item_data.source_domain,
                    order_index=item_data.order_index,
                )
                db.add(db_item)

        # Recreate canvas blocks
        for block_data in interview_data.canvas_blocks:
            db_block = CanvasBlock(
                interview_id=interview_id,
                type=BlockType(block_data.type),
                text=block_data.text,
                order_index=block_data.order_index,
            )
            db.add(db_block)

        db.commit()

        # Reload with relationships
        db_interview = (
            db.query(Interview)
            .options(
                joinedload(Interview.notes).joinedload(Note.items),
                joinedload(Interview.canvas_blocks),
            )
            .filter(Interview.id == interview_id)
            .first()
        )

        logger.info(f"Successfully autosaved interview: {db_interview.interview_title}")
        return InterviewResponse.model_validate(db_interview)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error autosaving interview with ID: {interview_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/interviews/{interview_id}", status_code=204)
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):
    """Delete an interview and all associated data."""
    logger.info(f"Deleting interview with ID: {interview_id}")
    try:
        db_interview = db.query(Interview).filter(Interview.id == interview_id).first()

        if not db_interview:
            logger.warning(f"Interview not found with ID: {interview_id}")
            raise HTTPException(status_code=404, detail="Interview not found")

        interview_title = db_interview.interview_title
        db.delete(db_interview)
        db.commit()

        logger.info(f"Successfully deleted interview: {interview_title}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting interview with ID: {interview_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
