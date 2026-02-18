import sys
from pathlib import Path
from logging import FileHandler, StreamHandler, Logger, Formatter, getLogger, basicConfig, DEBUG, INFO, ERROR
from typing import Protocol

_root_logger: Logger | None = None


class ClockPort(Protocol):
    def now(self) -> ...: ...


def setup_logger(name: str, log_dir: str, clock: ClockPort, debug_enabled: bool = False) -> None:
    global _root_logger
    _root_logger = getLogger(name)

    Path(log_dir).mkdir(exist_ok=True)
    base_level = DEBUG if debug_enabled else INFO

    formatter = Formatter(
        '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    formatter.converter = lambda ts: clock.now().timetuple()

    ch = StreamHandler(sys.stdout)
    ch.setLevel(base_level)
    ch.setFormatter(formatter)

    fh = FileHandler(Path(log_dir) / "app.log", encoding="utf-8")
    fh.setLevel(base_level)
    fh.setFormatter(formatter)

    efh = FileHandler(Path(log_dir) / "app_errors.log", encoding="utf-8")
    efh.setLevel(ERROR)
    efh.setFormatter(formatter)
    
    basicConfig(
        level=base_level,
        handlers=[ch, fh, efh]
    )


def get_logger(name: str | None = None) -> Logger:
    if _root_logger is None:
        raise RuntimeError("setup_logger() must be called before get_logger()")

    if name is None:
        return _root_logger

    return _root_logger.getChild(name)


