"""API endpoints for AI text refinement."""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.models.interview_schemas import (
    TextRefinementRequest,
    TextRefinementResponse,
)
from backend.models.interview_models import CanvasBlock
from backend.models.database_session import get_db
from backend.services.llm_service import llm_service
from backend.services.prompt_loader import prompt_loader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/canvas/refine", response_model=TextRefinementResponse)
def refine_text(
    request: TextRefinementRequest,
    db: Session = Depends(get_db),
):
    """
    Refine text from a canvas block using AI.

    Actions:
    - improve: Enhance clarity and professionalism
    - shorten: Reduce length while keeping key points
    - change_tone: Make more conversational for podcast format
    """
    logger.info(
        f"Text refinement request: block_id={request.block_id}, "
        f"action={request.action}, provider={request.llm_provider}"
    )

    try:
        # Get the canvas block
        block = db.query(CanvasBlock).filter(CanvasBlock.id == request.block_id).first()

        if not block:
            logger.warning(f"Canvas block not found with ID: {request.block_id}")
            raise HTTPException(status_code=404, detail="Canvas block not found")

        original_text = block.text

        # Get prompts for the requested action
        system_prompt, user_prompt = prompt_loader.get_text_refinement_prompts(
            action=request.action.value,
            text=original_text,
        )

        # Generate refined text using LLM
        refined_text = llm_service.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            provider=request.llm_provider.value,
            max_tokens=500,
            temperature=0.7,
        )

        logger.info(
            f"Text refinement completed: {len(original_text)} -> {len(refined_text)} chars"
        )

        return TextRefinementResponse(
            original_text=original_text,
            refined_text=refined_text,
            action=request.action,
        )

    except HTTPException:
        raise
    except ValueError as e:
        # Configuration or validation errors
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(
            f"Text refinement error for block {request.block_id}: {e}",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Text refinement failed. Please try again.")
