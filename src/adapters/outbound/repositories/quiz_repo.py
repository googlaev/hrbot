import json
from domain.entities.quiz import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from infra.database.sqlite_db import SqliteDatabase


class QuizRepo(QuizRepoPort):
    def __init__(self, db: SqliteDatabase):
        self.db = db

    async def list_all(self) -> list[Quiz]:
        rows = await self.db.fetchall("SELECT id, title FROM quizzes")

        return [Quiz(id=r["id"], title=r["title"]) for r in rows]

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
            "INSERT INTO quizzes (title) VALUES (?)",
            (quiz.title,),
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