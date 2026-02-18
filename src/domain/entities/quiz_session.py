from datetime import datetime
from dataclasses import dataclass


@dataclass
class QuizSession:
    id: int | None
    user_id: int
    quiz_id: int
    started_at: datetime
    finished_at: datetime | None = None
    current_question: int = 0
    completed: bool = False


@dataclass
class QuizAnswer:
    id: int | None
    session_id: int
    question_id: int
    selected_answer: str
    is_correct: bool
    timestamp: datetime | None = None

