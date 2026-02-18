import io
import pandas as pd
from app.dtos.quiz_session_result import QuizSessionResultDto


class ExcelExporter:
    def export_quiz_results(self, results: list[QuizSessionResultDto]) -> bytes:
        df = pd.DataFrame([{
            "user_id": r.user_id,
            "session_id": r.session_id,
            "correct": r.correct,
            "total": r.total,
            "percent": r.percent,
            "started_at": r.started_at.strftime("%d %b %Y %H:%M"),
            "finished_at": r.finished_at.strftime("%d %b %Y %H:%M")
        } for r in results])

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)

        return buffer.getvalue()

