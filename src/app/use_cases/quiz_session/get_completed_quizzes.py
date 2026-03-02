from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.dtos.quiz_session_result import QuizSessionResultDto


class GetCompletedQuizzesUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort, users_repo: UsersRepoPort, quiz_repo: QuizRepoPort):
        self.quiz_session_repo = quiz_session_repo
        self.users_repo = users_repo
        self.quiz_repo = quiz_repo

    async def execute(self, quiz_id: int) -> list[QuizSessionResultDto]:
        quiz = await self.quiz_repo.get_quiz_by_id(quiz_id)

        sessions = await self.quiz_session_repo.get_completed_sessions(quiz_id)

        results: list[QuizSessionResultDto] = []

        for session in sessions:
            score = await self.quiz_session_repo.get_score(session.id)
            correct, total = score if score else (0, 0)

            user = await self.users_repo.get_user_by_id(session.user_id)
            if not user or not user.name:
                continue

            dto = QuizSessionResultDto(
                quiz_name=quiz.title,
                name=user.name,
                correct=correct,
                total=total,
                session_id=session.id,
                user_id=user.id,
                started_at=session.started_at,
                finished_at=session.finished_at,
            )
            results.append(dto)

        return results
