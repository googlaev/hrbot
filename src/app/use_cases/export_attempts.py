from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.dtos.quiz_session_result import QuizSessionResultDto
from app.ports.outbound.excel_exporter_port import ExcelExporterPort
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort

class ExcelExportAttemptsUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort, users_repo: UsersRepoPort, quiz_repo: QuizRepoPort, excel_exporter: ExcelExporterPort):
        self.quiz_session_repo = quiz_session_repo
        self.users_repo = users_repo
        self.quiz_repo = quiz_repo
        self.excel_exporter = excel_exporter

    async def execute(self, quiz_id: int) -> bytes | None:
        quiz = await self.quiz_repo.get_quiz_by_id(quiz_id)

        sessions = await self.quiz_session_repo.get_completed_sessions(quiz_id)
        if not sessions:
            return

        results: list[QuizSessionResultDto] = []

        for session in sessions:
            score = await self.quiz_session_repo.get_score(session.id)
            correct, total = score if score else (0, 0)

            user = await self.users_repo.get_user_by_id(session.user_id)
            if not user or not user.name:
                continue
            
            mistakes = await self.quiz_session_repo.get_mistakes(session)

            dto = QuizSessionResultDto(
                quiz_name=quiz.title,
                name=user.name,
                correct=correct,
                total=total,
                session_id=session.id,
                user_id=user.id,
                started_at=session.started_at,
                finished_at=session.finished_at,
                mistakes=mistakes
            )
            results.append(dto)

        return self.excel_exporter.export_quiz_results(results)
