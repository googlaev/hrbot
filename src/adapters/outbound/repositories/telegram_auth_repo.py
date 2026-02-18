from app.ports.outbound.repositories.telegram_auth_repo_port import TelegramAuthRepoPort
from infra.database.sqlite_db import SqliteDatabase
from app.dtos.tg_auth_dto import TelegramAuthDTO


class TelegramAuthRepo(TelegramAuthRepoPort):
    def __init__(self, db: SqliteDatabase):
        self.db = db

    async def find_user_by_telegram_id(self, telegram_id: int) -> int | None:
        row = await self.db.fetchone(
            "SELECT user_id FROM telegram_auth WHERE telegram_id = ?",
            (telegram_id,)
        )
        return row["user_id"] if row else None

    async def add_telegram_auth(self, user_id: int, tg_dto: TelegramAuthDTO):
        await self.db.execute(
            "INSERT INTO telegram_auth (user_id, telegram_id, username, language) VALUES (?, ?, ?, ?)",
            (user_id, tg_dto.telegram_id, tg_dto.username, tg_dto.language),
            commit=True
        )
