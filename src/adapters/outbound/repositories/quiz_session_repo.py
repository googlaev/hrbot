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
    async def add_session(self, session: QuizSession) -> int | None:
        cursor = await self.db.execute(
            """
            INSERT INTO quiz_sessions (user_id, quiz_id, question_timeout, started_at, question_order, question_options_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session.user_id,
                session.quiz_id,
                session.question_timeout,
                session.started_at or self.tz_clock.now(),
                json.dumps(session.question_order),
                json.dumps(session.question_options_order)
            ),
            commit=True
        )

        session_id = cursor.lastrowid
        if session_id is None:
            self.logger.warning("session_id is None in add_session")
            return

        return session_id

    async def get_session(self, session_id: int) -> QuizSession | None:
        row = await self.db.fetchone(
            """
            SELECT * 
            FROM quiz_sessions 
            WHERE id = ?
            """,
            (session_id, )
        )

        if not row:
            return None
        
        return QuizSession(
            id=row["id"],
            user_id=row["user_id"],
            quiz_id=row["quiz_id"],
            question_order=json.loads(row["question_order"]),
            question_options_order=json.loads(row["question_options_order"]),
            current_index=row["current_index"],
            question_timeout=row["question_timeout"],
            question_started_at=datetime.fromisoformat(row["question_started_at"]) if row["question_started_at"] else None,
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
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
            question_order=json.loads(row["question_order"]),
            question_options_order=json.loads(row["question_options_order"]),
            current_index=row["current_index"],
            question_timeout=row["question_timeout"],
            question_started_at=datetime.fromisoformat(row["question_started_at"]) if row["question_started_at"] else None,
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            finished_at=datetime.fromisoformat(row["finished_at"]) if row["finished_at"] else None,
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
                question_order=json.loads(row["question_order"]) if row["question_order"] else [],
                current_index=row["current_index"],
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

    async def count_sessions_today(self, user_id: int, quiz_id: int) -> int:
        row = await self.db.fetchone(
            """
            SELECT COUNT(*) AS cnt
            FROM quiz_sessions
            WHERE user_id = ?
              AND quiz_id = ?
              AND started_at >= DATE('now', 'start of day')
            """,
            (user_id, quiz_id, )
        )

        if row is None:
            raise

        return row["cnt"] or 0

    # Questions
    async def get_question(self, question_id: int) -> Question | None:
        row = await self.db.fetchone(
            """
            SELECT id, quiz_id, number, question_text, right_answer, wrong_answers_json
            FROM questions
            WHERE id = ?
            """,
            (question_id,)
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

    async def start_question(self, session_id: int):
        now = self.tz_clock.now()
        await self.db.execute(
            "UPDATE quiz_sessions SET question_started_at = ? WHERE id = ?",
            (now, session_id),
            commit=True
        )

    async def advance_question(self, session_id: int):
        await self.db.execute(
            """
            UPDATE quiz_sessions
            SET current_index = current_index + 1
            WHERE id = ?
            """,
            (session_id,),
            commit=True
        )

    # Answers
    async def add_answer(self, answer: QuizAnswer) -> None:
        await self.db.execute(
            """
            INSERT INTO quiz_answers (session_id, question_id, answer_index, is_correct, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (answer.session_id, answer.question_id, answer.answer_index, int(answer.is_correct), self.tz_clock.now()),
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
                answer_index=row["answer_index"],
                is_correct=bool(row["is_correct"]),
                timestamp=row["timestamp"]
            )
            for row in rows
        ]

    async def get_score(self, session_id: int) -> tuple[int, int]:
        session = await self.get_session(session_id)
        if not session:
            return (0, 0)
        
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
            return (0, 0)

        return (row["correct"] or 0, len(session.question_order) or 0)


