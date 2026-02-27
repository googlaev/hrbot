from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from domain.entities.quiz import Quiz

class QuizListUC:
    def __init__(self, quiz_repo: QuizRepoPort):
        self.quiz_repo = quiz_repo

    async def execute(self) -> list[Quiz]:
        quizzes = await self.quiz_repo.list_all()
        return quizzes
