from datetime import datetime
from dataclasses import dataclass


@dataclass
class QuizSession:
    id: int | None
    user_id: int
    quiz_id: int
    question_order: list[int]
    current_index: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    completed: bool = False


@dataclass
class QuizAnswer:
    id: int | None
    session_id: int
    question_id: int
    answer_index: int
    is_correct: bool
    timestamp: datetime | None = None

