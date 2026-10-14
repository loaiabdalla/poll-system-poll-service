"""Analytics Controller - REST API routes for Statistics and Reporting."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analytics import (
    GlobalStatsResponse,
    QuestionOptionDistributionResponse,
    QuestionTotalAnswersResponse,
    UserAnswersResponse,
    UserTotalAnsweredResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Statistics & Reporting"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


@router.get(
    "/questions/{question_id}/options-count",
    response_model=QuestionOptionDistributionResponse,
    summary="Pass Question ID -> Return option choice counts",
)
def get_question_options_distribution(
    question_id: int,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Requirement 1:
    Pass Question ID -> Return how many users choose each of the 4 question options.
    """
    return service.get_question_options_distribution(question_id)


@router.get(
    "/questions/{question_id}/total-answers",
    response_model=QuestionTotalAnswersResponse,
    summary="Pass Question ID -> Return total answers",
)
def get_question_total_answers(
    question_id: int,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Requirement 2:
    Pass Question ID -> Return how many users answer to this question in total.
    """
    return service.get_question_total_answers(question_id)


@router.get(
    "/users/{user_id}/answers",
    response_model=UserAnswersResponse,
    summary="Pass User ID -> Return user's answers for each question",
)
def get_user_answers(
    user_id: int,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Requirement 3:
    Pass User ID -> Return the user's answer to each question they submitted.
    """
    return service.get_user_answers(user_id)


@router.get(
    "/users/{user_id}/total-answers",
    response_model=UserTotalAnsweredResponse,
    summary="Pass User ID -> Return total questions answered by user",
)
def get_user_total_answers(
    user_id: int,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Requirement 4:
    Pass User ID -> Return how many questions this user answered to in total.
    """
    return service.get_user_total_answered(user_id)


@router.get(
    "/global-summary",
    response_model=GlobalStatsResponse,
    summary="Global Stats -> Return all questions, options, and user counts",
)
def get_global_statistics(
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Requirement 5:
    Return all questions and all possible options and for each question return
    how many users choose each of the question options.
    """
    return service.get_global_stats()
