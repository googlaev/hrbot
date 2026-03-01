from dataclasses import dataclass


@dataclass
class Question:
    id: int | None
    quiz_id: int | None
    number: int
    question_text: str
    right_answer: str
    wrong_answers: list[str]

    def get_options(self):
        opts = [self.right_answer] + self.wrong_answers

        return opts
    
    def check_answer(self, index: int) -> bool:
        return index == 0

@dataclass
class Quiz:
    id: int | None
    title: str
    daily_attempt_limit: int = 1
    question_count: int = 5
