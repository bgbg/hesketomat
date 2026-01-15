"""API endpoints for Interview Prep Projects."""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from backend.models.database_session import get_db
from backend.models.interview_schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectStats,
)
from backend.models.interview_models import Project, Interview, Note

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    """Create a new interview preparation project."""
    logger.info(f"Creating new project: {project.title}")
    try:
        db_project = Project(title=project.title)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        logger.info(f"Successfully created project with ID: {db_project.id}")

        # Return with stats
        response = ProjectResponse.model_validate(db_project)
        response.stats = ProjectStats(note_count=0, has_context=False)
        return response
    except Exception as e:
        logger.error(f"Error creating project: {project.title}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects", response_model=List[ProjectResponse])
def list_projects(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
):
    """List all projects with pagination and statistics."""
    logger.info(f"Listing projects with skip={skip}, limit={limit}")
    try:
        # Query projects with stats
        projects_query = (
            db.query(
                Project,
                func.count(Note.id).label("note_count"),
                func.max(func.length(Interview.background_context) > 0).label("has_context"),
            )
            .outerjoin(Interview, Project.id == Interview.project_id)
            .outerjoin(Note, Interview.id == Note.interview_id)
            .group_by(Project.id)
            .order_by(Project.last_modified.desc())
            .offset(skip)
            .limit(limit)
        )

        results = []
        for project, note_count, has_context in projects_query:
            response = ProjectResponse.model_validate(project)
            response.stats = ProjectStats(
                note_count=note_count or 0,
                has_context=bool(has_context),
            )
            results.append(response)

        logger.info(f"Successfully retrieved {len(results)} projects")
        return results
    except Exception as e:
        logger.error("Error listing projects", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific project by ID with statistics."""
    logger.info(f"Retrieving project with ID: {project_id}")
    try:
        # Query project with stats
        result = (
            db.query(
                Project,
                func.count(Note.id).label("note_count"),
                func.max(func.length(Interview.background_context) > 0).label("has_context"),
            )
            .outerjoin(Interview, Project.id == Interview.project_id)
            .outerjoin(Note, Interview.id == Note.interview_id)
            .filter(Project.id == project_id)
            .group_by(Project.id)
            .first()
        )

        if not result:
            logger.warning(f"Project not found with ID: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        project, note_count, has_context = result
        response = ProjectResponse.model_validate(project)
        response.stats = ProjectStats(
            note_count=note_count or 0,
            has_context=bool(has_context),
        )

        logger.info(f"Successfully retrieved project: {project.title}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving project with ID: {project_id}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
):
    """Update a project's title."""
    logger.info(f"Updating project with ID: {project_id}")
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            logger.warning(f"Project not found with ID: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        # Update fields if provided
        if project_update.title is not None:
            db_project.title = project_update.title

        db.commit()
        db.refresh(db_project)

        # Get stats for response
        note_count = (
            db.query(func.count(Note.id))
            .join(Interview)
            .filter(Interview.project_id == project_id)
            .scalar() or 0
        )
        has_context = (
            db.query(Interview)
            .filter(
                Interview.project_id == project_id,
                func.length(Interview.background_context) > 0
            )
            .first() is not None
        )

        response = ProjectResponse.model_validate(db_project)
        response.stats = ProjectStats(note_count=note_count, has_context=has_context)

        logger.info(f"Successfully updated project: {db_project.title}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project with ID: {project_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    """Delete a project and all associated data (interviews, notes, etc.)."""
    logger.info(f"Deleting project with ID: {project_id}")
    try:
        db_project = db.query(Project).filter(Project.id == project_id).first()

        if not db_project:
            logger.warning(f"Project not found with ID: {project_id}")
            raise HTTPException(status_code=404, detail="Project not found")

        project_title = db_project.title
        db.delete(db_project)
        db.commit()

        logger.info(f"Successfully deleted project: {project_title}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project with ID: {project_id}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
