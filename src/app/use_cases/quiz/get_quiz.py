from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from domain.entities.quiz import Quiz


class GetQuizUC:
    def __init__(self, quiz_repo: QuizRepoPort):
        self.quiz_repo = quiz_repo

    async def execute(self, quiz_id: int) -> Quiz | None:
        quiz = await self.quiz_repo.get_quiz_by_id(quiz_id)
        return quiz
