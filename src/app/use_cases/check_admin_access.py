from app.ports.outbound.repositories.users_repo_port import UsersRepoPort


class CheckAdminAccess:
    def __init__(self, users_repo: UsersRepoPort):
        self.users_repo = users_repo

    async def execute(self, user_id: int) -> bool:
        user = await self.users_repo.get_user_by_id(user_id)
        if not user:
            return False 

        return user.can_access_admin_panel()
