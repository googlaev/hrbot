from dataclasses import dataclass
from datetime import datetime
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort


@dataclass
class QuizSessionResultDto:
    session_id: int
    user_id: int
    started_at: datetime
    finished_at: datetime
    correct: int
    total: int

    @property
    def percent(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0.0


class GetCompletedQuizzesUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort):
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, quiz_id: int) -> list[QuizSessionResultDto]:
        sessions = await self.quiz_session_repo.get_completed_sessions(quiz_id)

        results: list[QuizSessionResultDto] = []

        for session in sessions:
            score = await self.quiz_session_repo.get_score(session.id)
            correct, total = score if score else (0, 0)

            dto = QuizSessionResultDto(
                session_id=session.id,
                user_id=session.user_id,
                started_at=session.started_at,
                finished_at=session.finished_at,
                correct=correct,
                total=total
            )
            results.append(dto)

        return results
