from typing import Protocol
from app.dtos.quiz import ParsedQuiz


class ExcelParserPort(Protocol):
    def parse_quiz(self, excel_bytes: bytes) -> ParsedQuiz | None:
        ...
