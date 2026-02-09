import pytest
import pandas as pd
from io import BytesIO
from typing import Dict, Any, List

@pytest.fixture
def make_excel_bytes():
    def _factory(name: str, questions: List[Dict[str, Any]]) -> bytes:
        """
        questions example:
        [
            {
                "number": 1,
                "question": "What is 2+2?",
                "right": "4",
                "wrong": ["3", "5", "2"]
            }
        ]
        """

        # Row 1: A1 = assessment name
        name_row = pd.DataFrame([[name, None, None]])

        # Rows 2... = questions
        rows: List[Any] = []
        for q in questions:
            rows.append(
                [q["number"], q["question"], q["right"], *q["wrong"]]
            )

        df_questions = pd.DataFrame(rows)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            name_row.to_excel(writer, index=False, header=False, startrow=0) # type: ignore
            df_questions.to_excel(writer, index=False, header=False, startrow=1) # type: ignore

        return buffer.getvalue()

    return _factory
