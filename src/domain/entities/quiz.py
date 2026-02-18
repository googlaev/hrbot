import random
from dataclasses import dataclass


@dataclass
class Question:
    id: int | None
    quiz_id: int | None
    number: int
    question_text: str
    right_answer: str
    wrong_answers: list[str]

    @property
    def options(self) -> list[str]:
        opts = self.wrong_answers + [self.right_answer]
        random.shuffle(opts)
        return opts


@dataclass
class Quiz:
    id: int | None
    title: str
