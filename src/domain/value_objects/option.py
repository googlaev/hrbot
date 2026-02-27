from dataclasses import dataclass


@dataclass
class Option:
    index: int          # real index
    display_index: int  # shuffled index
    text: str