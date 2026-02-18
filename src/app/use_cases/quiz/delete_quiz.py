from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort


class DeleteQuizUC:
    def __init__(self, quiz_repo: QuizRepoPort):
        self.repo = quiz_repo

    async def execute(self, quiz_id: int) -> None:
        await self.repo.delete_quiz(quiz_id)
