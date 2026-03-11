import pandas as pd
from io import StringIO
from app.dtos.quiz import ParsedQuiz, ParsedQuestion
from app.ports.outbound.csv_parser_port import CSVParserPort

class CSVParser(CSVParserPort):
    def parse_quiz(self, csv_bytes: bytes) -> tuple[ParsedQuiz | None, list[str]]:
        buffer = StringIO(csv_bytes.decode())
        df = pd.read_csv(buffer, header=None, dtype=str)

        errors: list[str] = []

        name = df.iloc[0, 0]  # type: ignore
        if not isinstance(name, str) or name.strip() == "":
            errors.append("Ошибка: отсутствует имя теста в первой строке")
            return None, errors

        questions: list[ParsedQuestion] = []

        for idx in range(2, len(df)):
            row = df.iloc[idx]
            number = row[0]
            question = row[1]
            time_to_answer = row[2]
            right = row[3]
            wrong = [str(x) for x in row[4:].tolist() if pd.notna(x)]

            if pd.isna(number) and pd.isna(question) and pd.isna(right): #type: ignore
                continue

            try:
                time_sec = int(time_to_answer)
            except (ValueError, TypeError):
                errors.append(
                    f"Ошибка в столбце 'Время на ответ (сек.)', строка {idx+1}: ожидается число секунд, найдено '{time_to_answer}'"
                )
                continue

            questions.append(
                ParsedQuestion(
                    number=int(number),
                    question=str(question),
                    time_to_answer=time_sec,
                    right_answer=str(right),
                    wrong_answers=wrong,
                )
            )

        if not questions:
            errors.append("Ошибка: нет валидных вопросов в тесте")
            return None, errors

        return ParsedQuiz(name=name, questions=questions), errors

    def get_template(self) -> bytes:
        columns = ["№", "Вопрос", "Время на ответ (сек.)", "Правильный ответ",
                   "Неправильный ответ 1", "Неправильный ответ 2", "Неправильный ответ 3"]

        buffer = StringIO()

        buffer.write(",".join(["Имя теста"] + [""]*(len(columns)-1)) + "\n")

        buffer.write(",".join(columns))

        buffer.seek(0)
        return buffer.getvalue().encode("utf-8-sig")