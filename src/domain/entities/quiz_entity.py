from dataclasses import dataclass
from typing import List

@dataclass
class Question:
    number: int
    text: str
    right_answer: str
    wrong_answers: List[str]


@dataclass
class Quiz:
    id: int | None
    name: str
    questions: List[Question]
