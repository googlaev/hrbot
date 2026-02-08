from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import Union
from app.app_actions import AppActions


class UserFilter(BaseFilter):
    async def __call__(self, event: Union[Message, CallbackQuery], actions: AppActions, user_id: int) -> bool:
        result = await actions.check_admin_access.execute(user_id)

        # Only non admin
        return not result
