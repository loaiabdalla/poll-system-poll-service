"""Analytics and reporting business logic service layer."""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.analytics import (
    GlobalQuestionStatItem,
    GlobalStatsResponse,
    OptionCountItem,
    QuestionOptionDistributionResponse,
    QuestionTotalAnswersResponse,
    UserAnswerItem,
    UserAnswersResponse,
    UserTotalAnsweredResponse,
)


class AnalyticsService:
    """Service handling data aggregations and statistical calculations."""

    def __init__(self, db: Session):
        self.analytics_repo = AnalyticsRepository(db)
        self.question_repo = QuestionRepository(db)

    def get_question_options_distribution(self, question_id: int) -> QuestionOptionDistributionResponse:
        """
        Requirement 1: Pass Question ID -> Return how many users chose each of the 4 options.
        """
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found.",
            )

        counts = self.analytics_repo.get_option_counts_for_question(question_id)
        options_list = [
            OptionCountItem(
                option_number=1,
                option_text=question.option_1,
                count=counts.get(1, 0),
            ),
            OptionCountItem(
                option_number=2,
                option_text=question.option_2,
                count=counts.get(2, 0),
            ),
            OptionCountItem(
                option_number=3,
                option_text=question.option_3,
                count=counts.get(3, 0),
            ),
            OptionCountItem(
                option_number=4,
                option_text=question.option_4,
                count=counts.get(4, 0),
            ),
        ]

        return QuestionOptionDistributionResponse(
            question_id=question.id,
            question_title=question.title,
            options=options_list,
        )

    def get_question_total_answers(self, question_id: int) -> QuestionTotalAnswersResponse:
        """
        Requirement 2: Pass Question ID -> Return total number of users who answered this question.
        """
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with ID {question_id} not found.",
            )

        total = self.analytics_repo.get_total_answers_for_question(question_id)
        return QuestionTotalAnswersResponse(
            question_id=question.id,
            question_title=question.title,
            total_answers=total,
        )

    def get_user_answers(self, user_id: int) -> UserAnswersResponse:
        """
        Requirement 3: Pass User ID -> Return the user's answer to each question they submitted.
        """
        answers = self.analytics_repo.get_user_answers(user_id)
        answer_items: List[UserAnswerItem] = []

        for ans in answers:
            q = ans.question
            selected_text = q.get_option_text(ans.selected_option) if q else ""
            title = q.title if q else "Question deleted"

            answer_items.append(
                UserAnswerItem(
                    answer_id=ans.id,
                    question_id=ans.question_id,
                    question_title=title,
                    selected_option=ans.selected_option,
                    selected_option_text=selected_text,
                    submitted_at=ans.created_at,
                )
            )

        return UserAnswersResponse(
            user_id=user_id,
            answers=answer_items,
        )

    def get_user_total_answered(self, user_id: int) -> UserTotalAnsweredResponse:
        """
        Requirement 4: Pass User ID -> Return how many questions this user answered in total.
        """
        total = self.analytics_repo.get_total_questions_answered_by_user(user_id)
        return UserTotalAnsweredResponse(
            user_id=user_id,
            total_questions_answered=total,
        )

    def get_global_stats(self) -> GlobalStatsResponse:
        """
        Requirement 5: Return all questions and all possible options and for each question
        return how many users choose each of the question options.
        """
        questions = self.analytics_repo.get_all_questions_with_answers()
        stat_items: List[GlobalQuestionStatItem] = []

        for q in questions:
            counts = {1: 0, 2: 0, 3: 0, 4: 0}
            for ans in q.answers:
                if ans.selected_option in counts:
                    counts[ans.selected_option] += 1

            total_answers = len(q.answers)
            options = [
                OptionCountItem(option_number=1, option_text=q.option_1, count=counts[1]),
                OptionCountItem(option_number=2, option_text=q.option_2, count=counts[2]),
                OptionCountItem(option_number=3, option_text=q.option_3, count=counts[3]),
                OptionCountItem(option_number=4, option_text=q.option_4, count=counts[4]),
            ]

            stat_items.append(
                GlobalQuestionStatItem(
                    question_id=q.id,
                    question_title=q.title,
                    total_answers=total_answers,
                    options=options,
                )
            )

        return GlobalStatsResponse(
            total_questions=len(stat_items),
            questions=stat_items,
        )
