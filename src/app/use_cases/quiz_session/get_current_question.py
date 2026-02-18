from __future__ import annotations
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from domain.entities.quiz import Question


class GetCurrentQuestionUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort):
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, session_id: int) -> Question | None:
        question = await self.quiz_session_repo.get_current_question(session_id)
        return question
