from datetime import datetime
from dataclasses import dataclass


@dataclass
class QuizSession:
    id: int | None
    user_id: int
    quiz_id: int
    question_order: list[int]
    question_options_order: dict[str, list[int]]
    
    current_index: int = 0
    question_started_at: datetime | None = None

    started_at: datetime | None = None
    finished_at: datetime | None = None
    completed: bool = False
    
    def get_current_question_id(self) -> int | None:
        if self.current_index >= len(self.question_order):
            return None 
        
        return self.question_order[self.current_index]
    
    def get_current_options_order(self) -> list[int] | None:
        if self.current_index >= len(self.question_options_order):
            return None 
        
        shuffled_indices = self.question_options_order[str(self.current_index)]

        return shuffled_indices


@dataclass
class QuizAnswer:
    id: int | None
    session_id: int
    question_id: int
    answer_index: int
    is_correct: bool
    timestamp: datetime | None = None

