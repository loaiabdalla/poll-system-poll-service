"""Schemas module."""
from app.schemas.question import QuestionBase, QuestionCreate, QuestionUpdate, QuestionResponse
from app.schemas.answer import AnswerCreate, AnswerUpdate, AnswerResponse, AnswerDeleteSummary
from app.schemas.analytics import (
    OptionCountItem,
    QuestionOptionDistributionResponse,
    QuestionTotalAnswersResponse,
    UserAnswerItem,
    UserAnswersResponse,
    UserTotalAnsweredResponse,
    GlobalQuestionStatItem,
    GlobalStatsResponse,
)

__all__ = [
    "QuestionBase",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    "AnswerCreate",
    "AnswerUpdate",
    "AnswerResponse",
    "AnswerDeleteSummary",
    "OptionCountItem",
    "QuestionOptionDistributionResponse",
    "QuestionTotalAnswersResponse",
    "UserAnswerItem",
    "UserAnswersResponse",
    "UserTotalAnsweredResponse",
    "GlobalQuestionStatItem",
    "GlobalStatsResponse",
]
