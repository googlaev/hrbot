from app.ports.outbound.repositories.users_repo_port import UsersRepoPort


class SetUserNameUC:
    def __init__(self, users_repo: UsersRepoPort):
        self.users_repo = users_repo

    async def execute(self, user_id: int, new_name: str):
        await self.users_repo.update_name(user_id, new_name)
