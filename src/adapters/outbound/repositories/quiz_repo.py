import json
from domain.entities.quiz import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from infra.database.sqlite_db import SqliteDatabase


class QuizRepo(QuizRepoPort):
    def __init__(self, db: SqliteDatabase):
        self.db = db

    async def list_all(self) -> list[Quiz]:
        rows = await self.db.fetchall("SELECT * FROM quizzes")

        return [
            Quiz(
                id=row["id"], 
                title=row["title"], 
                daily_attempt_limit=row["daily_attempt_limit"],
                question_count=row["question_count"]
            ) for row in rows
        ]
    
    async def get_quiz_by_id(self, quiz_id: int) -> Quiz | None:
        row = await self.db.fetchone(
            """
            SELECT * 
            FROM quizzes
            WHERE id=?
            """,
            (quiz_id,)
        )

        if row is None:
            return

        return Quiz(
            id=row["id"], 
            title=row["title"],
            daily_attempt_limit=row["daily_attempt_limit"],
            question_count=row["question_count"]
        )
    
    async def set_question_count(self, quiz_id: int, new_count: int):
        await self.db.execute(
            "UPDATE quizzes SET question_count=? WHERE id=?",
            (new_count, quiz_id),
            commit=True
        )

    async def set_attempt_limit(self, quiz_id: int, new_limit: int):
        await self.db.execute(
            "UPDATE quizzes SET daily_attempt_limit=? WHERE id=?",
            (new_limit, quiz_id),
            commit=True
        )

    async def get_questions(self, quiz_id: int) -> list[Question]:
        rows = await self.db.fetchall(
            """
            SELECT id, quiz_id, number, question_text, right_answer, wrong_answers_json
            FROM questions WHERE quiz_id=? ORDER BY id
            """,
            (quiz_id,)
        )

        return [
            Question(
                id=r["id"],
                quiz_id=r["quiz_id"],
                number=r["number"],
                question_text=r["question_text"],
                right_answer=r["right_answer"],
                wrong_answers=json.loads(r["wrong_answers_json"])
            )
            for r in rows
        ]

    async def add_quiz(self, quiz: Quiz, questions: list[Question]) -> int | None:
        quiz_id = await self.db.execute(
            """
            INSERT INTO quizzes 
            (title, daily_attempt_limit, question_count) 
            VALUES (?, ?, ?)
            """,
            (quiz.title, quiz.daily_attempt_limit, quiz.question_count),
            commit=True
        )

        for q in questions:
            await self.db.execute(
                """
                INSERT INTO questions
                (quiz_id, number, question_text, right_answer, wrong_answers_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    quiz_id.lastrowid,
                    q.number,
                    q.question_text,
                    q.right_answer,
                    json.dumps(q.wrong_answers)
                ),
                commit=True
            )

        return quiz_id.lastrowid

    async def delete_quiz(self, quiz_id: int) -> None:
        await self.db.execute(
            "DELETE FROM quizzes WHERE id=?",
            (quiz_id,),
            commit=True
        )