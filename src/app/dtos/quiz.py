from dataclasses import dataclass
from typing import List

@dataclass
class ParsedQuestion:
    number: int
    question: str
    right_answer: str
    wrong_answers: List[str]

@dataclass
class ParsedQuiz:
    name: str
    questions: List[ParsedQuestion]
