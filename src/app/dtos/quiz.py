from dataclasses import dataclass

@dataclass
class ParsedQuestion:
    number: int
    question: str
    time_to_answer: int
    right_answer: str
    wrong_answers: list[str]

@dataclass
class ParsedQuiz:
    name: str
    questions: list[ParsedQuestion]
