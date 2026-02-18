from typing import Protocol
from domain.entities.quiz import Quiz, Question


class QuizRepoPort(Protocol):
    async def list_all(self) -> list[Quiz]:
        ...

    async def get_questions(self, quiz_id: int) -> list[Question]:
        ...

    async def add_quiz(self, quiz: Quiz, questions: list[Question]) -> int | None:
        ...
