from __future__ import annotations
from dataclasses import dataclass
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from domain.value_objects.option import Option
from infra.tz_clock import TZClock
from domain.entities.quiz_session import QuizAnswer
from domain.entities.quiz_session import QuizSession

@dataclass
class QuestionWithTimerDTO:
    question_text: str = ""
    question_index: int = 0
    total_questions: int = 0
    options: list[Option] | None = None
    remaining_seconds: int | None = None
    finished: bool = False

class GetCurrentQuestionUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort, clock: TZClock):
        self.quiz_session_repo = quiz_session_repo
        self.clock = clock

    async def execute(self, session_id: int) -> QuestionWithTimerDTO:
        session = await self.quiz_session_repo.get_session(session_id)
        if session is None:
            return QuestionWithTimerDTO(finished=True)
        
        question_id = session.get_current_question_id()
        if question_id is None:
            return QuestionWithTimerDTO(finished=True)

        question = await self.quiz_session_repo.get_question(question_id)

        session, finished = await self._process_question_timeout(session, question.time_to_answer) 
        if finished:
            return QuestionWithTimerDTO(finished=True)

        shuffled_indices = session.get_current_options_order()
        original_options = question.get_options()

        built_options = [
            Option(
                index=real_idx,            
                display_index=display_idx,
                text=original_options[real_idx]
            )
            for display_idx, real_idx in enumerate(shuffled_indices)
        ]

        now = self.clock.now()
        elapsed = (now - session.question_started_at).total_seconds() if session.question_started_at else 0
        remaining = max(int(question.time_to_answer - elapsed), 0)

        return QuestionWithTimerDTO(
            question_text=question.question_text,
            options=built_options,
            question_index=session.current_index + 1,
            total_questions=len(session.question_order),
            remaining_seconds=int(remaining),
            finished=False
        )

    async def _process_question_timeout(self, session: QuizSession, time_to_answer: int) -> tuple[QuizSession, bool]:
        now = self.clock.now()

        if session.id is None:
            raise

        if session.completed:
            return session, True

        if session.question_started_at is None:
            await self.quiz_session_repo.start_question(session.id)
            session.question_started_at = now
            return session, False

        elapsed = (now - session.question_started_at).total_seconds()
        remaining = time_to_answer - elapsed

        if remaining <= 0:
            question_id = session.get_current_question_id()
            if question_id is not None:
                await self.quiz_session_repo.add_answer(
                    QuizAnswer(
                        id=None,
                        session_id=session.id,
                        question_id=question_id,
                        answer_index=-1,
                        is_correct=False,
                        timestamp=now
                    )
                )
            
            await self.quiz_session_repo.advance_question(session.id)

            await self.quiz_session_repo.start_question(session.id)

            session = await self.quiz_session_repo.get_session(session.id)

        return session, False
