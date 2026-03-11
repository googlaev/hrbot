from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort


class QuizRatingUC:
    def __init__(self, quiz_session_repo: QuizSessionRepoPort):
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, quiz_id: int):
        rating = await self.quiz_session_repo.get_quiz_rating(quiz_id)
        return rating