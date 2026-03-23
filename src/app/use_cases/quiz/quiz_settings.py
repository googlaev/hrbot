from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort


class QuizSettingsUC:
    def __init__(self, quiz_repo: QuizRepoPort):
        self.quiz_repo = quiz_repo

    async def update_quiz_question_count(self, quiz_id: int, new_count: int):
        questions = await self.quiz_repo.get_questions(quiz_id)
        new_count = max(1, min(new_count, len(questions)))

        await self.quiz_repo.set_question_count(quiz_id, new_count)

    async def update_quiz_attempt_limit(self, quiz_id: int, new_limit: int):
        new_limit = max(1, min(new_limit, 100))

        await self.quiz_repo.set_attempt_limit(quiz_id, new_limit)

    async def toggle_quiz_visibility(self, quiz_id: int):
        quiz = await self.quiz_repo.get_quiz_by_id(quiz_id)
        if not quiz:
            return
        
        await self.quiz_repo.set_quiz_hidden(quiz_id, not quiz.is_hidden)
