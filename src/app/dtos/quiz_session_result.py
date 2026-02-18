from dataclasses import dataclass
from datetime import datetime


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