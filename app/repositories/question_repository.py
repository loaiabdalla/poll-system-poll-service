"""Question repository for database queries."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.question import Question
from app.models.answer import Answer
from app.schemas.question import QuestionCreate


class QuestionRepository:
    """Repository handling CRUD operations for Questions."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: int) -> Optional[Question]:
        return self.db.query(Question).filter(Question.id == question_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Question]:
        return self.db.query(Question).offset(skip).limit(limit).all()

    def create(self, question_in: QuestionCreate) -> Question:
        question = Question(
            title=question_in.title,
            option_1=question_in.option_1,
            option_2=question_in.option_2,
            option_3=question_in.option_3,
            option_4=question_in.option_4,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, db_question: Question, update_data: dict) -> Question:
        for field, value in update_data.items():
            if hasattr(db_question, field) and value is not None:
                setattr(db_question, field, value)
        self.db.commit()
        self.db.refresh(db_question)
        return db_question

    def delete(self, db_question: Question) -> None:
        self.db.delete(db_question)
        self.db.commit()

    def has_answers(self, question_id: int) -> bool:
        """Checks if any user answers exist for this question."""
        count = self.db.query(Answer).filter(Answer.question_id == question_id).count()
        return count > 0

    def count_answers(self, question_id: int) -> int:
        return self.db.query(Answer).filter(Answer.question_id == question_id).count()
