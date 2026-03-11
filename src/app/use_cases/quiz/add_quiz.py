from domain.entities.quiz import Quiz, Question
from app.ports.outbound.repositories.quiz_repo_port import QuizRepoPort
from app.ports.outbound.excel_parser_port import ExcelParserPort
from app.ports.outbound.csv_parser_port import CSVParserPort


class AddQuizUC:
    def __init__(self, ep: ExcelParserPort, cp: CSVParserPort, qr: QuizRepoPort):
        self.excel_parser = ep
        self.csv_parser = cp
        self.quiz_repo = qr

    async def from_excel(self, excel_bytes: bytes, user_id: int) -> Quiz | list[str] | None:
        parsed_quiz, errors = self.excel_parser.parse_quiz(excel_bytes)

        if errors or parsed_quiz is None:
            return errors

        questions = [
            Question(
                id=None,
                quiz_id=None,
                number=q.number,
                time_to_answer=q.time_to_answer,
                question_text=q.question,
                right_answer=q.right_answer,
                wrong_answers=q.wrong_answers
            )
            for q in parsed_quiz.questions
        ]

        quiz = Quiz(id=None, questions_len=len(questions), title=parsed_quiz.name, question_count=len(questions))
        quiz_id = await self.quiz_repo.add_quiz(quiz, questions)
        quiz.id = quiz_id

        return quiz

    async def from_csv(self, csv_bytes: bytes, user_id: int) -> Quiz | list[str] | None:
        parsed_quiz, errors = self.csv_parser.parse_quiz(csv_bytes) 

        if errors:
            return errors

        questions = [
            Question(
                id=None,
                quiz_id=None,
                number=q.number,
                time_to_answer=q.time_to_answer,
                question_text=q.question,
                right_answer=q.right_answer,
                wrong_answers=q.wrong_answers
            )
            for q in parsed_quiz.questions
        ]

        quiz = Quiz(id=None, questions_len=len(questions), title=parsed_quiz.name)
        quiz_id = await self.quiz_repo.add_quiz(quiz, questions)
        quiz.id = quiz_id

        return quiz

