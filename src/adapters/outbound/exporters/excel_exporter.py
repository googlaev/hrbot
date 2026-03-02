import io
import pandas as pd
from typing import Any
from app.dtos.quiz_session_result import QuizSessionResultDto


class ExcelExporter:
    def export_quiz_results(self, results: list[QuizSessionResultDto]) -> bytes:
        df = pd.DataFrame([{
            "quiz_name": r.quiz_name,
            "name": r.name,
            "result": f"{r.correct}/{r.total}",
            "percent": r.percent,
            "mistakes": format_mistakes(r.mistakes)
        } for r in results])

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        return buffer.getvalue()

def format_mistakes(mistakes: list[dict[str, Any]]) -> str:
    if not mistakes:
        return ""
    parts = []
    for m in mistakes:
        parts.append(
            f"{m['question_number']}) {m['question_text']} | "
            f"Ответ: {m['user_answer']} | "
            f"Правильный: {m['correct_answer']}"
        )
    return "\n".join(parts)
