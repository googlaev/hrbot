from typing import Optional
from dataclasses import dataclass

@dataclass
class TelegramAuthDTO:
    telegram_id: int
    username: Optional[str]
    language: Optional[str]
