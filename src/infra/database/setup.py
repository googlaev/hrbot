from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:   
    from .sqlite_db import SqliteDatabase

async def setup_database(db: SqliteDatabase) -> None:
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL
        );
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS telegram_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            telegram_id INTEGER NOT NULL UNIQUE,
            username TEXT,
            language TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            text TEXT NOT NULL,
            right_answer TEXT NOT NULL,
            wrong_answers_json TEXT NOT NULL,
            FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
        );
        """
    )

    
