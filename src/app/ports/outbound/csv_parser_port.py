from typing import Protocol
from app.dtos.quiz import ParsedQuiz

class CSVParserPort(Protocol):
    def parse_quiz(self, csv_bytes: bytes) -> tuple[ParsedQuiz | None, list[str]]:
        ...

    def get_template(self) -> bytes:
        ...