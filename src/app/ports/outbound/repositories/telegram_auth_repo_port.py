from typing import Optional, Protocol
from app.dtos.tg_auth_dto import TelegramAuthDTO


class TelegramAuthRepoPort(Protocol):
    async def find_user_by_telegram_id(self, telegram_id: int) -> Optional[int]:
        ...

    async def add_telegram_auth(
        self, 
        user_id: int, 
        tg_dto: TelegramAuthDTO
    ):
        ...
