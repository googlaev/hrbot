from domain.entities.user import User
from app.ports.outbound.repositories.users_repo_port import UsersRepoPort
from infra.database.sqlite_db import SqliteDatabase


class UsersRepo(UsersRepoPort):
    def __init__(self, db: SqliteDatabase):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        row = await self.db.fetchone(
            """
            SELECT id, role, name FROM users WHERE id = ?
            """,
            (user_id,)
        )

        if not row:
            return None

        return User(
            id=row["id"],
            role=row["role"],
            name=row["name"]
        )

    async def add_user(self, user: User) -> int:
        new_id = await self.db.execute(
            """
            INSERT INTO users (role)
            VALUES (?)
            """,
            (user.role.value,),
            commit=True
        )

        last_row_id = new_id.lastrowid

        if not last_row_id:
            raise Exception("Failed to insert user into database")

        return last_row_id
    
    async def update_name(self, user_id: int, new_name: str):
        await self.db.execute(
            "UPDATE users SET name = ? WHERE id = ?",
            (new_name, user_id),
            commit=True
        )

