"""Question model definition."""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    """SQLAlchemy model for Poll Questions."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(Text, nullable=False)
    option_1 = Column(String(255), nullable=False)
    option_2 = Column(String(255), nullable=False)
    option_3 = Column(String(255), nullable=False)
    option_4 = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Deleting a question cascades and deletes all associated answers
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def get_option_text(self, option_number: int) -> str:
        """Helper to get text for an option number (1-4)."""
        options = {
            1: self.option_1,
            2: self.option_2,
            3: self.option_3,
            4: self.option_4,
        }
        return options.get(option_number, "")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, title='{self.title[:30]}...')>"
