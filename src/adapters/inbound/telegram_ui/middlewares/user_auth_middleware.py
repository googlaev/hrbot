from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any
from app.dtos.tg_auth_dto import TelegramAuthDTO
from app.app_actions import AppActions
from app.ports.outbound.logger_port import LoggerPort


class UserAuthMiddleware(BaseMiddleware):
    def __init__(self, app_actions: AppActions, logger: LoggerPort):
        self.app_actions = app_actions
        self.logger = logger

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            telegram_id = event.from_user.id
            username = event.from_user.username
            language = event.from_user.language_code

            auth_uc = self.app_actions.auth_by_telegram

            user_id = await auth_uc.execute(
                TelegramAuthDTO(
                    telegram_id=telegram_id,
                    username=username,
                    language=language
                )
            )

            data["user_id"] = user_id
            data["actions"] = self.app_actions

            return await handler(event, data)
