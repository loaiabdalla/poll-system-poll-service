"""Answer repository for database queries."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.answer import Answer
from app.schemas.answer import AnswerCreate


class AnswerRepository:
    """Repository handling CRUD operations for User Answers."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, answer_id: int) -> Optional[Answer]:
        return self.db.query(Answer).filter(Answer.id == answer_id).first()

    def get_by_user_and_question(self, user_id: int, question_id: int) -> Optional[Answer]:
        return (
            self.db.query(Answer)
            .filter(Answer.user_id == user_id, Answer.question_id == question_id)
            .first()
        )

    def create(self, answer_in: AnswerCreate) -> Answer:
        answer = Answer(
            question_id=answer_in.question_id,
            user_id=answer_in.user_id,
            selected_option=answer_in.selected_option,
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        return answer

    def update_selected_option(self, db_answer: Answer, new_option: int) -> Answer:
        db_answer.selected_option = new_option
        self.db.commit()
        self.db.refresh(db_answer)
        return db_answer

    def delete(self, db_answer: Answer) -> None:
        self.db.delete(db_answer)
        self.db.commit()

    def delete_by_user_id(self, user_id: int) -> int:
        """
        Delete all answers submitted by user_id across all questions.
        Returns the number of deleted records.
        """
        deleted_count = (
            self.db.query(Answer)
            .filter(Answer.user_id == user_id)
            .delete(synchronize_session="fetch")
        )
        self.db.commit()
        return deleted_count
