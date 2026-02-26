from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:   
    from .sqlite_db import SqliteDatabase

async def setup_database(db: SqliteDatabase) -> None:
    await db.execute("PRAGMA foreign_keys = ON;")

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            name TEXT
        );
        """
    )

    # ==========================
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

    # ==========================
    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        );
        """
    )

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            right_answer TEXT NOT NULL,
            wrong_answers_json TEXT NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id) ON DELETE CASCADE
        );
        """
    )

    # ==========================
    await db.execute(
        """ 
        CREATE TABLE IF NOT EXISTS quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,

            question_order TEXT,
            current_index INTEGER NOT NULL DEFAULT 0,
            completed INTEGER NOT NULL DEFAULT 0,

            started_at DATETIME NOT NULL,
            finished_at DATETIME
        );
        """
    )

    await db.execute(
        """ 
        CREATE TABLE IF NOT EXISTS quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY(session_id) REFERENCES quiz_sessions(id) ON DELETE CASCADE
        );
        """
    )

    # ==========================


    
