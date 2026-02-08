from __future__ import annotations

from .middlewares.user_auth_middleware import UserAuthMiddleware
from .filters.admin_filter import AdminFilter
from .filters.user_filter import UserFilter

from .handlers import user_router, admin_router

from app.app_actions import AppActions
from app.ports.outbound.logger_port import LoggerPort
from infra.telegram.bot import TelegramBotInfra


class TelegramUI:
    def __init__(self, bot_infra: TelegramBotInfra, actions: AppActions, logger: LoggerPort):
        self.bot_infra = bot_infra 
        self.logger = logger

        self.middleware = UserAuthMiddleware(actions, logger)

        self.bot = bot_infra.bot
        self.dp = bot_infra.dp

        # Auth users
        self.dp.message.outer_middleware(self.middleware)
        self.dp.callback_query.outer_middleware(self.middleware)

        user_router.message.filter(UserFilter())
        user_router.callback_query.filter(UserFilter())
        self.dp.include_router(user_router)

        admin_router.message.filter(AdminFilter())
        admin_router.callback_query.filter(AdminFilter())
        self.dp.include_router(admin_router)

