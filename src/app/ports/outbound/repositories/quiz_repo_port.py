from typing import Protocol
from domain.entities.quiz import Quiz, Question


class QuizRepoPort(Protocol):
    async def list_all(self) -> list[Quiz]:
        ...

    async def get_quiz_by_id(self, quiz_id: int) -> Quiz | None:
        ...

    async def get_questions(self, quiz_id: int) -> list[Question]:
        ...

    async def set_question_count(self, quiz_id: int, new_count: int):
        ...

    async def add_quiz(self, quiz: Quiz, questions: list[Question]) -> int | None:
        ...

    async def set_attempt_limit(self, quiz_id: int, new_limit: int):
        ...

    async def delete_quiz(self, quiz_id: int) -> None:
        ...