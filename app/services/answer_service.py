"""Answer business logic service layer."""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.answer import Answer
from app.repositories.answer_repository import AnswerRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.answer import AnswerCreate, AnswerUpdate
from app.services.user_client import UserClient


class AnswerService:
    """Service layer handling user answers, cross-service user verification, and integrity."""

    def __init__(
        self,
        db: Session,
        user_client: Optional[UserClient] = None,
    ):
        self.repository = AnswerRepository(db)
        self.question_repository = QuestionRepository(db)
        self.user_client = user_client or UserClient()

    async def submit_answer(self, answer_in: AnswerCreate) -> Answer:
        """
        Submits an answer for a poll question.
        BUSINESS RULES:
        1. User must exist in the User Service.
        2. User must be registered (is_registered == True).
        3. Question must exist.
        4. User can answer only once to each question.
        """
        # Step 1: Inter-service check: Verify user is registered
        user_data = await self.user_client.get_user(answer_in.user_id)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {answer_in.user_id} was not found in the User Service.",
            )

        if not user_data.get("is_registered", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User with ID {answer_in.user_id} is not registered. "
                    "Only registered users are permitted to answer poll questions."
                ),
            )

        # Step 2: Verify question exists
        question = self.question_repository.get_by_id(answer_in.question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {answer_in.question_id} does not exist.",
            )

        # Step 3: Verify user hasn't already answered this question
        existing_answer = self.repository.get_by_user_and_question(
            user_id=answer_in.user_id,
            question_id=answer_in.question_id,
        )
        if existing_answer:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"User with ID {answer_in.user_id} has already answered question {answer_in.question_id}. "
                    "Each user can answer only once. Use the update endpoint to change your response."
                ),
            )

        # Step 4: Persist answer
        return self.repository.create(answer_in)

    def update_answer(self, answer_id: int, answer_in: AnswerUpdate) -> Answer:
        """
        Update an existing answer by its answer ID.
        """
        answer = self.repository.get_by_id(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer with ID {answer_id} not found.",
            )

        return self.repository.update_selected_option(answer, answer_in.selected_option)

    def delete_answer(self, answer_id: int) -> None:
        """
        Delete a single answer by its ID.
        """
        answer = self.repository.get_by_id(answer_id)
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer with ID {answer_id} not found.",
            )
        self.repository.delete(answer)

    def delete_user_answers(self, user_id: int) -> int:
        """
        Delete all answers submitted by user_id across all questions.
        Called by User Service when a user deletes their profile.
        """
        return self.repository.delete_by_user_id(user_id)
