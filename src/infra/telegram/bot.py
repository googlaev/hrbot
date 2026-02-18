import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from typing import Any


class TelegramBotInfra:
    def __init__(
        self, 
        tg_bot_token: str,
        storage: MemoryStorage = MemoryStorage(),
        fsm_strategy: FSMStrategy = FSMStrategy.GLOBAL_USER
    ):
        self._bot = Bot(token=tg_bot_token)
        self._dp = Dispatcher(storage=storage, fsm_strategy=fsm_strategy)
        self._polling_task: asyncio.Task[Any] | None = None

    async def start_polling(self):
        if self._polling_task and not self._polling_task.done():
            return
        self._polling_task = asyncio.create_task(self._dp.start_polling(self._bot)) # type: ignore

    async def stop_polling(self):
        if self._polling_task:
            self._polling_task.cancel()
            await asyncio.gather(self._polling_task, return_exceptions=True)
            self._polling_task = None
        await self._bot.session.close()

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def dp(self) -> Dispatcher:
        return self._dp