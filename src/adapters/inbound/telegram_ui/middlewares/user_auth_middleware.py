from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Any
from collections.abc import Callable
from app.dtos.tg_auth_dto import TelegramAuthDTO
from app.app_actions import AppActions
from infra.logging import get_logger


class UserAuthMiddleware(BaseMiddleware):
    def __init__(self, app_actions: AppActions):
        self.app_actions = app_actions
        self.logger = get_logger(__class__.__name__)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Any],
        event: TelegramObject,
        data: dict[str, Any]
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

            self.logger.debug(f"user_id: {user_id}, username: {username}, lang: {language}")

            return await handler(event, data)
