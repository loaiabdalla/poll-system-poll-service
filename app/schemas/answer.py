"""Pydantic schemas for Answer request and response validation."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AnswerCreate(BaseModel):
    """Schema for submitting an answer to a question."""
    question_id: int = Field(..., gt=0, description="Target question ID")
    user_id: int = Field(..., gt=0, description="User ID submitting the answer")
    selected_option: int = Field(
        ...,
        ge=1,
        le=4,
        description="Selected option number (must be 1, 2, 3, or 4)",
    )


class AnswerUpdate(BaseModel):
    """Schema for updating an existing answer by its ID."""
    selected_option: int = Field(
        ...,
        ge=1,
        le=4,
        description="New option selection (must be 1, 2, 3, or 4)",
    )


class AnswerResponse(BaseModel):
    """Schema for returning answer details."""
    id: int
    question_id: int
    user_id: int
    selected_option: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerDeleteSummary(BaseModel):
    """Schema for response when deleting answers by user."""
    deleted_count: int
    user_id: int
