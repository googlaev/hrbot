from domain.entities.quiz_entity import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.ports.outbound.excel_parser_port import ExcelParserPort


class AddQuizFromExcel:
    def __init__(self, parser: ExcelParserPort, quiz_repo: QuizRepoPort):
        self.parser = parser
        self.quiz_repo = quiz_repo

    async def execute(self, excel_bytes: bytes):
        parsed_quiz = self.parser.parse_quiz(excel_bytes)

        questions = [
            Question(
                number=q.number,
                text=q.question,
                right_answer=q.right_answer,
                wrong_answers=q.wrong_answers
            )
            for q in parsed_quiz.questions
        ]

        quiz = Quiz(id=None, name=parsed_quiz.name, questions=questions)

        quiz_id = await self.quiz_repo.add(quiz)

        quiz.id = quiz_id

        return quiz

