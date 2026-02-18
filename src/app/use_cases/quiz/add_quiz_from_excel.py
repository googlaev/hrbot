from domain.entities.quiz import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.ports.outbound.excel_parser_port import ExcelParserPort


class AddQuizFromExcelUC:
    def __init__(self, parser: ExcelParserPort, quiz_repo: QuizRepoPort):
        self.parser = parser
        self.quiz_repo = quiz_repo

    async def execute(self, excel_bytes: bytes, user_id: int) -> Quiz | None:
        parsed_quiz = self.parser.parse_quiz(excel_bytes)

        if parsed_quiz is None:
            return

        questions = [
            Question(
                id=None,
                quiz_id=None,
                number=q.number,
                question_text=q.question,
                right_answer=q.right_answer,
                wrong_answers=q.wrong_answers
            )
            for q in parsed_quiz.questions
        ]

        quiz = Quiz(id=None, title=parsed_quiz.name)

        quiz_id = await self.quiz_repo.add_quiz(quiz, questions)

        quiz.id = quiz_id

        return quiz

