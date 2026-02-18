import asyncio
from src.infra.database.sqlite_db import SqliteDatabase


DB_PATH = "data/app.db"


async def list_users(db: SqliteDatabase):
    rows = await db.fetchall("SELECT id, role FROM users")
    if not rows:
        print("Пользователи не найдены")
        return
    for row in rows:
        print(f"ID: {row['id']} | role: {row['role']}")


async def set_role(db: SqliteDatabase, user_id: int, role: str):
    await db.execute(
        "UPDATE users SET role = ? WHERE id = ?",
        (role, user_id)
    )
    print(f"Роль пользователя {user_id} изменена на: {role}")


async def main():
    db = SqliteDatabase(DB_PATH)
    await db.connect()

    print("Команды:")
    print("  list                    — показать всех пользователей")
    print("  set <id> <role>         — изменить роль")
    print("  exit                    — закрыть программу")
    print()

    while True:
        try:
            cmd = input("> ").strip().split()

            if not cmd:
                continue

            match cmd[0]:
                case "list":
                    await list_users(db)

                case "set" if len(cmd) == 3:
                    await set_role(db, int(cmd[1]), cmd[2])

                case "exit":
                    break

                case _:
                    print("Неверная команда.")
        except EOFError:
            print("\nEOF received — exiting.")
            break

    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
