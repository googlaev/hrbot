from typing import Callable
import pytest
from io import BytesIO
import pandas as pd
from adapters.outbound.parsers.excel_parser import ExcelParser

def test_excel_parser_basic(make_excel_bytes: Callable[..., bytes]):
    excel_bytes = make_excel_bytes(
        name="Math Test",
        questions=[
            {
                "number": 1,
                "question": "What is 2+2?",
                "right": "4",
                "wrong": ["3", "5", "2"]
            },
            {
                "number": 2,
                "question": "What is 10/2?",
                "right": "5",
                "wrong": ["1", "2"]
            }
        ]
    )

    parser = ExcelParser()
    result = parser.parse_quiz(excel_bytes)

    assert result.name == "Math Test"
    assert len(result.questions) == 2

    q1 = result.questions[0]
    assert q1.number == 1
    assert q1.question == "What is 2+2?"
    assert q1.right_answer == "4"
    assert q1.wrong_answers == ["3", "5", "2"]

def test_parser_handles_missing_wrong_answers(make_excel_bytes: Callable[..., bytes]):
    excel_bytes = make_excel_bytes(
        name="Quick Test",
        questions=[
            {
                "number": 1,
                "question": "Sky color?",
                "right": "Blue",
                "wrong": []
            }
        ]
    )

    parser = ExcelParser()
    result = parser.parse_quiz(excel_bytes)

    q = result.questions[0]
    assert q.wrong_answers == []


def test_parser_invalid_format():
    # Excel with no name row
    df = pd.DataFrame([["", "Bad", "File"]])
    buffer = BytesIO()
    
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, header=False) # type: ignore

    parser = ExcelParser()

    with pytest.raises(ValueError):
        parser.parse_quiz(buffer.getvalue())