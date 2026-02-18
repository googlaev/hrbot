from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.dtos.quiz_session_result import QuizSessionResultDto
from app.ports.outbound.excel_exporter_port import ExcelExporterPort


class ExcelExportAttemptsUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort, excel_exporter: ExcelExporterPort):
        self.quiz_session_repo = quiz_session_repo
        self.excel_exporter = excel_exporter

    async def execute(self, quiz_id: int) -> bytes | None:
        sessions = await self.quiz_session_repo.get_completed_sessions(quiz_id)
        if not sessions:
            return

        results: list[QuizSessionResultDto] = []

        for session in sessions:
            score = await self.quiz_session_repo.get_score(session.id)
            correct, total = score if score else (0, 0)

            dto = QuizSessionResultDto(
                session_id=session.id,
                user_id=session.user_id,
                started_at=session.started_at,
                finished_at=session.finished_at,
                correct=correct,
                total=total
            )
            results.append(dto)

        return self.excel_exporter.export_quiz_results(results)
