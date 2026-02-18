from dataclasses import dataclass


@dataclass
class Question:
    number: int
    text: str
    right_answer: str
    wrong_answers: list[str]


@dataclass
class Quiz:
    id: int | None
    name: str
    questions: list[Question]
