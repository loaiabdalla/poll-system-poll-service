"""Question Controller - REST API routes for Questions."""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


def get_question_service(db: Session = Depends(get_db)) -> QuestionService:
    return QuestionService(db)


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new poll question with 4 options",
)
def create_question(
    question_in: QuestionCreate,
    service: QuestionService = Depends(get_question_service),
):
    """Creates a new poll question with exactly 4 answer options."""
    return service.create_question(question_in)


@router.get(
    "",
    response_model=List[QuestionResponse],
    summary="Get all poll questions",
)
def list_questions(
    skip: int = Query(0, ge=0, description="Offset"),
    limit: int = Query(100, ge=1, le=500, description="Page limit"),
    service: QuestionService = Depends(get_question_service),
):
    """Retrieve all available poll questions."""
    return service.list_questions(skip=skip, limit=limit)


@router.get(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Get question by ID",
)
def get_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
):
    """Retrieve details for a specific question."""
    return service.get_question(question_id)


@router.put(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question (Only permitted if unanswered)",
)
def update_question(
    question_id: int,
    question_in: QuestionUpdate,
    service: QuestionService = Depends(get_question_service),
):
    """
    Update a question.
    NOTE: If users have already answered this question, updating will be rejected (400 Bad Request)
    until those answers are deleted.
    """
    return service.update_question(question_id, question_in)


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question (cascades all answers)",
)
def delete_question(
    question_id: int,
    service: QuestionService = Depends(get_question_service),
):
    """
    Delete a question.
    NOTE: Deleting a question will automatically cascade and delete all user answers associated with it.
    """
    service.delete_question(question_id)
    return None
