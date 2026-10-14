"""Pydantic schemas for Statistics and Reporting API."""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class OptionCountItem(BaseModel):
    """Counts per option for a question."""
    option_number: int = Field(..., ge=1, le=4)
    option_text: str
    count: int = Field(..., ge=0)


class QuestionOptionDistributionResponse(BaseModel):
    """Requirement 1: Pass Question ID -> Return how many users chose each of the 4 options."""
    question_id: int
    question_title: str
    options: List[OptionCountItem]


class QuestionTotalAnswersResponse(BaseModel):
    """Requirement 2: Pass Question ID -> Return total number of users who answered this question."""
    question_id: int
    question_title: str
    total_answers: int = Field(..., ge=0)


class UserAnswerItem(BaseModel):
    """Details of a single answer submitted by a user."""
    answer_id: int
    question_id: int
    question_title: str
    selected_option: int
    selected_option_text: str
    submitted_at: datetime


class UserAnswersResponse(BaseModel):
    """Requirement 3: Pass User ID -> Return the user's answer to each question submitted."""
    user_id: int
    answers: List[UserAnswerItem]


class UserTotalAnsweredResponse(BaseModel):
    """Requirement 4: Pass User ID -> Return total number of questions this user answered."""
    user_id: int
    total_questions_answered: int = Field(..., ge=0)


class GlobalQuestionStatItem(BaseModel):
    """Per-question statistics in the global report."""
    question_id: int
    question_title: str
    total_answers: int
    options: List[OptionCountItem]


class GlobalStatsResponse(BaseModel):
    """Requirement 5: Global stats for all questions and options."""
    total_questions: int
    questions: List[GlobalQuestionStatItem]
