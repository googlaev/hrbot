from __future__ import annotations
from typing import Protocol
from domain.entities.quiz_session import QuizSession, QuizAnswer
from domain.entities.quiz import Question


class QuizSessionRepoPort(Protocol):
    # Sessions
    async def create_session(self, user_id: int, quiz_id: int) -> QuizSession | None:
        ...
    
    async def get_session(self, session_id: int) -> QuizSession | None:
        ...

    async def get_active_session(self, user_id: int, quiz_id: int) -> QuizSession | None:
        ...

    async def get_completed_sessions(self, quiz_id: int) -> list[QuizSession]:
        ...
    
    async def complete_session(self, session_id: int) -> None:
        ...

    # Questions
    async def get_current_question(self, session_id: int) -> Question | None:
        ...

    async def advance_question(self, session_id: int) -> bool:
        ...

    # Answers
    async def add_answer(self, answer: QuizAnswer) -> None:
        ...

    async def get_answers(self, session_id: int) -> list[QuizAnswer]:
        ...

    async def get_score(self, session_id: int) -> tuple[int, int] | None:
        ...


