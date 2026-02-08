from dataclasses import dataclass
from domain.enums.user_role import UserRole


@dataclass
class User:
    id: int | None = None
    role: UserRole = UserRole.USER

    def can_access_admin_panel(self) -> bool:
        return self.role == UserRole.ADMIN