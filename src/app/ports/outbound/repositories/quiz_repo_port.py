from typing import List, Optional, Protocol
from domain.entities.quiz_entity import Quiz


class QuizRepoPort(Protocol):
    async def add(self, quiz: Quiz) -> Optional[int]:
        ...

    async def get(self, quiz_id: int) ->Optional[Quiz]:
        ...

    async def list(self) -> List[Quiz]:
        ...

    async def delete(self, quiz_id: int) -> None:
        ...