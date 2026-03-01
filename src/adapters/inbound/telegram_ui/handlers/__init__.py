from .user_handlers import user_router
from .admin_handlers import admin_router
from .quiz_handlers import quiz_router

__all__ = [
    "user_router",
    "admin_router",
    "quiz_router"
]