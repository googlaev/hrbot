import random
from dataclasses import dataclass
from domain.value_objects.option import Option


@dataclass
class Question:
    id: int | None
    quiz_id: int | None
    number: int
    question_text: str
    right_answer: str
    wrong_answers: list[str]

    def build_options(self):
        # create base list with real indexes
        opts = [
            Option(index=i, display_index=i, text=text)
            for i, text in enumerate([self.right_answer] + self.wrong_answers)
        ]

        # shuffle display order only
        random.shuffle(opts)

        for di, opt in enumerate(opts):
            opt.display_index = di

        return opts
    
    def check_answer(self, index: int) -> bool:
        return index == 0

@dataclass
class Quiz:
    id: int | None
    title: str
