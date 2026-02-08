from typing import Protocol, Optional
from domain.entities.user import User


class UsersRepoPort(Protocol):
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        ...

    async def add_user(self, user: User) -> int:
        ...

