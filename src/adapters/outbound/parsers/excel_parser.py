import pandas as pd
from io import BytesIO
from app.dtos.quiz import ParsedQuiz, ParsedQuestion
from app.ports.outbound.excel_parser_port import ExcelParserPort


class ExcelParser(ExcelParserPort):
    def parse_quiz(self, excel_bytes: bytes) -> tuple[ParsedQuiz | None, list[str]]:
        buffer = BytesIO(excel_bytes)
        df = pd.read_excel(buffer, header=None, dtype=str)  # type: ignore

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

            if pd.isna(number) or pd.isna(question) or pd.isna(right):  # type: ignore
                continue

            try:
                number_int = int(number)
            except (ValueError, TypeError):
                errors.append(
                    f"Ошибка в столбце '№', строка {idx+1}: ожидается номер вопроса (целое число)"
                )
                continue

            try:
                time_int = int(time_to_answer)
            except (ValueError, TypeError):
                errors.append(
                    f"Ошибка в столбце 'Время на ответ (сек.)', строка {idx+1}: "
                    f"ожидается число секунд, найдено '{time_to_answer}'"
                )
                continue

            questions.append(
                ParsedQuestion(
                    number=number_int,
                    question=str(question),
                    time_to_answer=time_int,
                    right_answer=str(right),
                    wrong_answers=wrong,
                )
            )

        if errors:
            return None, errors

        if not questions:
            errors.append("Ошибка: в файле нет корректных вопросов")
            return None, errors

        return ParsedQuiz(name=name, questions=questions), []

    def get_template(self) -> bytes:
        columns = ["№", "Вопрос", "Время на ответ (сек.)", "Правильный ответ", "Неправильный ответ 1", "Неправильный ответ 2", "Неправильный ответ 3"]
        data = []

        df = pd.DataFrame(data, columns=columns) # type: ignore
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            pd.DataFrame([["Имя теста"]]).to_excel(writer, index=False, header=False, startrow=0, startcol=0) #type: ignore
            df.to_excel(writer, index=False, startrow=1) #type: ignore
        buffer.seek(0)
        return buffer.read()