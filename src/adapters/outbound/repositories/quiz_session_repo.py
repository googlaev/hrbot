import json
from datetime import datetime
from domain.entities.quiz_session import QuizSession, QuizAnswer
from domain.entities.quiz import Question
from app.ports.outbound.repositories.quiz_session_repo_port import QuizSessionRepoPort
from infra.database.sqlite_db import SqliteDatabase
from infra.tz_clock import TZClock
from infra.logging import get_logger


class QuizSessionRepo(QuizSessionRepoPort):
    def __init__(self, db: SqliteDatabase, tz_clock: TZClock):
        self.db = db
        self.tz_clock = tz_clock
        self.logger = get_logger(__class__.__name__)

    # Sessions
    async def create_session(self, user_id: int, quiz_id: int) -> QuizSession | None:
        cursor = await self.db.execute(
            """
            INSERT INTO quiz_sessions (user_id, quiz_id, started_at)
            VALUES (?, ?, ?)
            """,
            (user_id, quiz_id, self.tz_clock.now()),
            commit=True
        )

        session_id = cursor.lastrowid

        if session_id is None:
            self.logger.warning("session_id is None in create_session")
            return

        return await self.get_session(session_id)

    async def get_session(self, session_id: int) -> QuizSession | None:
        row = await self.db.fetchone(
            "SELECT * FROM quiz_sessions WHERE id = ?",
            (session_id, )
        )

        if not row:
            return None
        
        return QuizSession(
            id=row["id"],
            user_id=row["user_id"],
            quiz_id=row["quiz_id"],

            started_at=row["started_at"],
            finished_at=row["finished_at"],

            current_question=row["current_question"],
            completed=bool(row["completed"])
        )
    
    async def get_active_session(self, user_id: int, quiz_id: int) -> QuizSession | None:
        row = await self.db.fetchone(
            """
            SELECT *
            FROM quiz_sessions
            WHERE user_id = ? AND quiz_id = ? AND completed = 0
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, quiz_id)
        )

        if not row:
            return None

        return QuizSession(
            id=row["id"],
            user_id=row["user_id"],
            quiz_id=row["quiz_id"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
            current_question=row["current_question"],
            completed=bool(row["completed"])
        )

        # Sessions
    
    async def get_completed_sessions(self, quiz_id: int) -> list[QuizSession]:
        rows = await self.db.fetchall(
            """
            SELECT *
            FROM quiz_sessions
            WHERE quiz_id = ? AND completed = 1
            ORDER BY finished_at DESC
            """,
            (quiz_id,)
        )

        return [
            QuizSession(
                id=row["id"],
                user_id=row["user_id"],
                quiz_id=row["quiz_id"],
                started_at=datetime.fromisoformat(row["started_at"]),
                finished_at=datetime.fromisoformat(row["finished_at"]),
                current_question=row["current_question"],
                completed=True
            )
            for row in rows
        ]

    async def complete_session(self, session_id: int) -> None:
        await self.db.execute(
            "UPDATE quiz_sessions SET completed = 1, finished_at = ? WHERE id = ?",
            (self.tz_clock.now(), session_id),
            commit=True
        )

    # Questions
    async def get_current_question(self, session_id: int) -> Question | None:
        row = await self.db.fetchone(
            """
            SELECT q.*
            FROM quiz_sessions ts
            JOIN questions q ON q.quiz_id = ts.quiz_id AND q.number = ts.current_question + 1
            WHERE ts.id = ?
            """,
            (session_id,)
        )

        if not row:
            return None
        
        return Question(
            id=row["id"],
            quiz_id=row["quiz_id"],
            number=row["number"],
            question_text=row["question_text"],
            right_answer=row["right_answer"],
            wrong_answers=json.loads(row["wrong_answers_json"])
        )

    async def advance_question(self, session_id: int) -> bool:
        """
        returns true - next question exists
        returns false - finish
        """

        await self.db.execute(
            "UPDATE quiz_sessions SET current_question = current_question + 1 WHERE id = ?",
            (session_id, ),
            commit=True
        )

        row = await self.db.fetchone(
            """
            SELECT q.id FROM 
            quiz_sessions s
            JOIN questions q
                ON q.quiz_id = s.quiz_id
                AND q.number = s.current_question + 1
            WHERE s.id = ?
            """,
            (session_id, )
        )

        return row is not None

    # Answers
    async def add_answer(self, answer: QuizAnswer) -> None:
        await self.db.execute(
            """
            INSERT INTO quiz_answers (session_id, question_id, selected_answer, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (answer.session_id, answer.question_id, answer.selected_answer, int(answer.is_correct), self.tz_clock.now()),
            commit=True
        )

    async def get_answers(self, session_id: int) -> list[QuizAnswer]:
        rows = await self.db.fetchall(
            "SELECT * FROM quiz_answers WHERE session_id = ?",
            (session_id,)
        )

        return [
            QuizAnswer(
                id=row["id"],
                session_id=row["session_id"],
                question_id=row["question_id"],
                selected_answer=row["selected_answer"],
                is_correct=bool(row["is_correct"]),
                timestamp=row["timestamp"]
            )
            for row in rows
        ]

    async def get_score(self, session_id: int) -> tuple[int, int] | None:
        row = await self.db.fetchone(
            """
            SELECT 
                SUM(is_correct) AS correct,
                COUNT(*) AS total
            FROM quiz_answers
            WHERE session_id = ?
            """,
            (session_id,)
        )

        if row is None:
            return None

        return (row["correct"] or 0, row["total"] or 0)


