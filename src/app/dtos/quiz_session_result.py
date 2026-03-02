from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class QuizSessionResultDto:
    quiz_name: str
    session_id: int
    user_id: int
    name: str
    started_at: datetime
    finished_at: datetime
    correct: int
    total: int
    mistakes: list[dict[str, Any]] | None = None

    @property
    def percent(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0.0