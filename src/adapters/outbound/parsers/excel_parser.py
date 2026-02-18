import pandas as pd
from io import BytesIO
from app.dtos.quiz import ParsedQuiz, ParsedQuestion
from app.ports.outbound.excel_parser_port import ExcelParserPort


class ExcelParser(ExcelParserPort):
    def parse_quiz(self, excel_bytes: bytes) -> ParsedQuiz:
        buffer = BytesIO(excel_bytes)
        df = pd.read_excel(buffer, header=None, dtype=str) # type: ignore

        # First row: name in A1
        name = df.iloc[0, 0] # type: ignore
        if not isinstance(name, str) or name.strip() == "":
            raise ValueError("Invalid or missing quiz name")

        # Remaining rows: questions
        questions: list[ParsedQuestion] = []

        for idx in range(2, len(df)):
            row = df.iloc[idx]

            number = row[0]
            question = row[1]
            right = row[2]
            wrong = [str(x) for x in row[3:].tolist() if pd.notna(x)]

            # skip incomplete rows
            if pd.isna(number) or pd.isna(question) or pd.isna(right): # type: ignore
                continue  

            questions.append(
                ParsedQuestion(
                    number=int(number),
                    question=str(question),
                    right_answer=str(right),
                    wrong_answers=wrong,
                )
            )

        return ParsedQuiz(name=name, questions=questions)