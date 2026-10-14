"""Controllers module."""
from app.controllers.question_controller import router as question_router
from app.controllers.answer_controller import router as answer_router
from app.controllers.analytics_controller import router as analytics_router

__all__ = [
    "question_router",
    "answer_router",
    "analytics_router",
]
