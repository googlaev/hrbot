from dataclasses import dataclass
from datetime import datetime
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from domain.entities.quiz_session import QuizAnswer


@dataclass
class SubmitAnswerResult:
    is_finished: bool
    correct: int = 0
    total: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None


class SubmitAnswerUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort):
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, session_id: int, answer_index: int) -> SubmitAnswerResult:
        # session = await self.quiz_session_repo.get_session(session_id)

        question = await self.quiz_session_repo.get_current_question(session_id)
        if question is None or question.id is None:
            raise RuntimeError("No active question for session")

        is_correct = question.check_answer(answer_index)

        quiz_answer = QuizAnswer(
            id=None,
            session_id=session_id,
            question_id=question.id,
            answer_index=answer_index,
            is_correct=is_correct
        )

        await self.quiz_session_repo.add_answer(quiz_answer)

        has_next = await self.quiz_session_repo.advance_question(session_id)

        # if no next - finish session
        if not has_next:
            await self.quiz_session_repo.complete_session(session_id)
            correct, total = await self.quiz_session_repo.get_score(session_id)
            session = await self.quiz_session_repo.get_session(session_id)

            return SubmitAnswerResult(
                is_finished=True,
                correct=correct,
                total=total,
                started_at=session.started_at,
                finished_at=session.finished_at
            )

        return SubmitAnswerResult(
            is_finished=False
        )