from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from app.app_actions import AppActions


class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, actions: AppActions, user_id: int) -> bool:
        result = await actions.check_admin_access.execute(user_id)
        
        # Only admins
        return result
