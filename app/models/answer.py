"""Answer model definition."""
from datetime import datetime, timezone
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Answer(Base):
    """SQLAlchemy model for User Poll Answers."""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, nullable=False, index=True)
    selected_option = Column(Integer, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    question = relationship("Question", back_populates="answers")

    __table_args__ = (
        # User can only answer once per question
        UniqueConstraint("question_id", "user_id", name="uq_question_user"),
        # Option must be between 1 and 4
        CheckConstraint("selected_option BETWEEN 1 AND 4", name="check_valid_option"),
    )

    def __repr__(self) -> str:
        return f"<Answer(id={self.id}, question_id={self.question_id}, user_id={self.user_id}, selected_option={self.selected_option})>"
