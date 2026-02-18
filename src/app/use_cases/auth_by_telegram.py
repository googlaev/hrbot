from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from app.ports.outbound.repositories.telegram_auth_repo_port import TelegramAuthRepoPort
from app.dtos.tg_auth_dto import TelegramAuthDTO
from domain.entities.user import User


class AuthenticateByTelegramUC:
    def __init__(self, users_repo: UsersRepoPort, tg_auth_repo: TelegramAuthRepoPort):
        self.users_repo = users_repo
        self.tg_auth_repo = tg_auth_repo

    async def execute(self, tg_dto: TelegramAuthDTO) -> int:
        """
        Authenticate user by Telegram.
        Returns main user_id.
        """
        user_id = await self.tg_auth_repo.find_user_by_telegram_id(tg_dto.telegram_id)
        
        if user_id is None:
            # Create main user
            user_id = await self.users_repo.add_user(User())

            # Link Telegram account
            await self.tg_auth_repo.add_telegram_auth(user_id, tg_dto)
        
        return user_id
