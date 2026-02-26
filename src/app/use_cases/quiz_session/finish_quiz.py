from dataclasses import dataclass
from datetime import datetime
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort

@dataclass
class FinishQuizResult:
    correct: int
    total: int
    started_at: datetime
    finished_at: datetime


class FinishQuizUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort):
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, session_id: int) -> FinishQuizResult:
        # Complete session
        await self.quiz_session_repo.complete_session(session_id)

        # Get session after finish
        session = await self.quiz_session_repo.get_session(session_id)
        correct, total = await self.quiz_session_repo.get_score(session_id)

        return FinishQuizResult(
            correct=correct,
            total=total,
            started_at=session.started_at,
            finished_at=session.finished_at
        )