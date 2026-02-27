from datetime import datetime
from zoneinfo import ZoneInfo


class TZClock:
    def __init__(self, tz_name: str):
        self.tz = ZoneInfo(tz_name)

    def now(self) -> datetime:
        return datetime.now(self.tz)
