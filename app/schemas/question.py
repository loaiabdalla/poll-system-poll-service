"""Pydantic schemas for Question request and response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    title: str = Field(..., min_length=3, description="The question text itself")
    option_1: str = Field(..., min_length=1, max_length=255, description="First answer option")
    option_2: str = Field(..., min_length=1, max_length=255, description="Second answer option")
    option_3: str = Field(..., min_length=1, max_length=255, description="Third answer option")
    option_4: str = Field(..., min_length=1, max_length=255, description="Fourth answer option")


class QuestionCreate(QuestionBase):
    """Schema for creating a poll question."""
    pass


class QuestionUpdate(BaseModel):
    """Schema for updating an existing question (allowed only if unanswered)."""
    title: Optional[str] = Field(None, min_length=3)
    option_1: Optional[str] = Field(None, min_length=1, max_length=255)
    option_2: Optional[str] = Field(None, min_length=1, max_length=255)
    option_3: Optional[str] = Field(None, min_length=1, max_length=255)
    option_4: Optional[str] = Field(None, min_length=1, max_length=255)


class QuestionResponse(QuestionBase):
    """Schema for returning question data."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
