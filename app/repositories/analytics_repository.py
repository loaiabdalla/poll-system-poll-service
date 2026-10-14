"""Analytics repository for aggregate statistics queries."""
from typing import Dict, List, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.models.answer import Answer
from app.models.question import Question


class AnalyticsRepository:
    """Repository handling SQL aggregations and reporting metrics."""

    def __init__(self, db: Session):
        self.db = db

    def get_option_counts_for_question(self, question_id: int) -> Dict[int, int]:
        """
        Returns a dictionary mapping option_number (1..4) to the number of users who chose it.
        Initializes missing options to 0.
        """
        results = (
            self.db.query(Answer.selected_option, func.count(Answer.id))
            .filter(Answer.question_id == question_id)
            .group_by(Answer.selected_option)
            .all()
        )
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for opt_num, count in results:
            if opt_num in counts:
                counts[opt_num] = count
        return counts

    def get_total_answers_for_question(self, question_id: int) -> int:
        """Returns the total number of answers submitted for a specific question."""
        total = (
            self.db.query(func.count(Answer.id))
            .filter(Answer.question_id == question_id)
            .scalar()
        )
        return total or 0

    def get_user_answers(self, user_id: int) -> List[Answer]:
        """
        Returns all answers submitted by user_id, eager-loading the associated Question.
        """
        return (
            self.db.query(Answer)
            .options(joinedload(Answer.question))
            .filter(Answer.user_id == user_id)
            .order_by(Answer.created_at.asc())
            .all()
        )

    def get_total_questions_answered_by_user(self, user_id: int) -> int:
        """Returns total number of questions answered by a specific user."""
        total = (
            self.db.query(func.count(Answer.id))
            .filter(Answer.user_id == user_id)
            .scalar()
        )
        return total or 0

    def get_all_questions_with_answers(self) -> List[Question]:
        """Returns all questions with their answers eager loaded for global summary."""
        return self.db.query(Question).options(joinedload(Question.answers)).all()
