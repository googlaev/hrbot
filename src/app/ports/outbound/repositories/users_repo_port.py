from typing import Protocol
from domain.entities.user import User


class UsersRepoPort(Protocol):
    async def get_user_by_id(self, user_id: int) -> User | None:
        ...

    async def add_user(self, user: User) -> int:
        ...

    async def update_name(self, user_id: int, new_name: str):
        ...
