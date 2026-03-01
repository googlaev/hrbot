from typing import Any
import random
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from domain.entities.quiz_session import QuizSession


class StartQuizUC:
    def __init__(self, users_repo: UsersRepoPort, quiz_session_repo: QuizSessionRepoPort, quiz_repo: QuizRepoPort):
        self.users_repo = users_repo
        self.quiz_session_repo = quiz_session_repo
        self.quiz_repo = quiz_repo

    async def execute(self, user_id: int, quiz_id: int) -> dict[str, Any]:
        result: dict[str, Any] = {}

        user = await self.users_repo.get_user_by_id(user_id)
        if not user or not user.name:
            return { "requires_name": True }
        
        session = await self.quiz_session_repo.get_active_session(user_id, quiz_id)
        if session:
            result["quiz_session"] = session
            return result
        
        quiz = await self.quiz_repo.get_quiz_by_id(quiz_id)
        if quiz is None:
            raise
        
        if not user.can_access_admin_panel():
            attempts_today = await self.quiz_session_repo.count_sessions_today(user_id, quiz_id)
            if attempts_today >= quiz.daily_attempt_limit:
                return { "limit_reached": True }
        
        questions = await self.quiz_repo.get_questions(quiz_id)

        # TODO: Place in entity
        questions_cnt = quiz.question_count
        questions_cnt = min(len(questions), questions_cnt)
        
        random.shuffle(questions)
        reduced_questions = questions[:questions_cnt]
        question_ids = [q.id for q in reduced_questions]

        options_order: dict[int, list[int]] = {}

        for idx, question in enumerate(reduced_questions):
            base = [0] + list(range(1, len(question.wrong_answers) + 1))
            random.shuffle(base)
            options_order[idx] = base
        
        session = QuizSession(
            id=None,
            user_id=user_id,
            quiz_id=quiz_id,
            question_order=question_ids, # type: ignore
            question_options_order=options_order
        )

        session_id = await self.quiz_session_repo.add_session(session)

        session.id = session_id

        result["quiz_session"] = session
        return result
