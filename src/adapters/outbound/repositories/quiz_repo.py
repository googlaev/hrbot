import json
from typing import List, Optional
from domain.entities.quiz_entity import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from infra.database.sqlite_db import SqliteDatabase


class QuizRepo(QuizRepoPort):
    def __init__(self, db: SqliteDatabase):
        self.db = db

    async def add(self, quiz: Quiz) -> Optional[int]:
        result = await self.db.execute(
            "INSERT INTO quiz (name) VALUES (?)",
            (quiz.name,),
            commit=True
        )

        quiz_id = result.lastrowid

        for q in quiz.questions:
            await self.db.execute(
                """
                INSERT INTO question
                (quiz_id, number, text, right_answer, wrong_answers_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    quiz_id,
                    q.number,
                    q.text,
                    q.right_answer,
                    json.dumps(q.wrong_answers)
                ),
                commit=True
            )
        
        return quiz_id

    async def get(self, quiz_id: int) -> Optional[Quiz]:
        row = await self.db.fetchone(
            "SELECT id, name FROM quiz WHERE id = ?",
            (quiz_id,)
        )
        if not row:
            return None

        question_rows = await self.db.fetchall(
            """
            SELECT number, text, right_answer, wrong_answers_json
            FROM question
            WHERE quiz_id = ?
            ORDER BY number ASC
            """,
            (quiz_id,)
        )

        questions = [
            Question(
                number=r["number"],
                text=r["text"],
                right_answer=r["right_answer"],
                wrong_answers=json.loads(r["wrong_answers_json"])
            )
            for r in question_rows
        ]

        return Quiz(id=row["id"], name=row["name"], questions=questions)

    async def list(self) -> List[Quiz]:
        quiz_rows = await self.db.fetchall("SELECT id, name FROM quiz")

        quizzes: List[Quiz] = []
        for qrow in quiz_rows:
            result = await self.get(qrow["id"])
            if result:
                quizzes.append(result)
        return quizzes

    async def delete(self, quiz_id: int) -> None:
        await self.db.execute(
            """
            DELETE FROM quiz WHERE id = ?
            """, 
            (quiz_id,)
        )
