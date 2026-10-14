"""Answer Controller - REST API routes for Answers."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.answer import (
    AnswerCreate,
    AnswerDeleteSummary,
    AnswerResponse,
    AnswerUpdate,
)
from app.services.answer_service import AnswerService

router = APIRouter(prefix="/answers", tags=["Answers"])


def get_answer_service(db: Session = Depends(get_db)) -> AnswerService:
    return AnswerService(db)


@router.post(
    "",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer to a poll question",
)
async def answer_question(
    answer_in: AnswerCreate,
    service: AnswerService = Depends(get_answer_service),
):
    """
    Answer a poll question.
    Requirements:
    - User must be a registered user in User Service (is_registered = True).
    - User can only answer once per question.
    """
    return await service.submit_answer(answer_in)


@router.put(
    "/{answer_id}",
    response_model=AnswerResponse,
    summary="Update a question answer by answer ID",
)
def update_answer(
    answer_id: int,
    answer_in: AnswerUpdate,
    service: AnswerService = Depends(get_answer_service),
):
    """
    Update an existing answer by its ID.
    Allows changing the selected option (1..4).
    """
    return service.update_answer(answer_id, answer_in)


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a poll question answer by answer ID",
)
def delete_answer(
    answer_id: int,
    service: AnswerService = Depends(get_answer_service),
):
    """Delete a specific answer by its ID."""
    service.delete_answer(answer_id)
    return None


@router.delete(
    "/user/{user_id}",
    response_model=AnswerDeleteSummary,
    summary="Inter-service: Delete all answers for a specific user",
)
def delete_all_answers_by_user(
    user_id: int,
    service: AnswerService = Depends(get_answer_service),
):
    """
    Internal endpoint called by User Service when a user deletes their profile.
    Cascades and deletes all answers submitted by this user across all questions.
    """
    count = service.delete_user_answers(user_id)
    return AnswerDeleteSummary(deleted_count=count, user_id=user_id)
