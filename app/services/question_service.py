"""Question business logic service layer."""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.question import Question
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionCreate, QuestionUpdate


class QuestionService:
    """Service layer handling Question domain logic."""

    def __init__(self, db: Session):
        self.repository = QuestionRepository(db)

    def get_question(self, question_id: int) -> Question:
        question = self.repository.get_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found."
            )
        return question

    def list_questions(self, skip: int = 0, limit: int = 100) -> List[Question]:
        return self.repository.get_all(skip=skip, limit=limit)

    def create_question(self, question_in: QuestionCreate) -> Question:
        return self.repository.create(question_in)

    def update_question(self, question_id: int, question_in: QuestionUpdate) -> Question:
        """
        Updates a question.
        BUSINESS RULE: A question CANNOT be updated if users have already answered it.
        """
        question = self.get_question(question_id)

        # Check if question has any user answers
        if self.repository.has_answers(question_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Question ID {question_id} cannot be updated because users have already "
                    "submitted answers to it. All answers must be deleted before this question can be modified."
                ),
            )

        update_data = question_in.model_dump(exclude_unset=True)
        return self.repository.update(question, update_data)

    def delete_question(self, question_id: int) -> None:
        """
        Deletes a question.
        BUSINESS RULE: Cascades and deletes all answers associated with this question.
        """
        question = self.get_question(question_id)
        self.repository.delete(question)
