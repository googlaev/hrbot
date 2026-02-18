from typing import Any
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort


class StartQuizUC:
    def __init__(self, users_repo: UsersRepoPort, quiz_session_repo: QuizSessionRepoPort):
        self.users_repo = users_repo
        self.quiz_session_repo = quiz_session_repo

    async def execute(self, user_id: int, quiz_id: int) -> dict[str, Any]:
        result: dict[str, Any] = {}

        user = await self.users_repo.get_user_by_id(user_id)
        
        if not user or not user.name:
            return {
                "requires_name": True
            }
        
        session = await self.quiz_session_repo.get_active_session(user_id, quiz_id)
        if session:
            result["quiz_session"] = session
            return result

        session = await self.quiz_session_repo.create_session(user_id, quiz_id)
        result["quiz_session"] = session
        return result
