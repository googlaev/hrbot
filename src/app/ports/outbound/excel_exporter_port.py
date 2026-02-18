from typing import Protocol
from app.dtos.quiz_session_result import QuizSessionResultDto


class ExcelExporterPort(Protocol):
    def export_quiz_results(self, results: list[QuizSessionResultDto]) -> bytes:
        ...