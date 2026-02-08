import aiosqlite
from typing import Optional, Iterable, Any
from pathlib import Path


class SqliteDatabase:
    def __init__(self, db_path: str):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True) 
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self._db_path)
        self._conn.row_factory = aiosqlite.Row

        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    # ---------- low-level ----------

    async def _execute(
        self,
        query: str,
        params: Iterable[Any] | None = None,
    ) -> aiosqlite.Cursor:
        assert self._conn is not None, "Database not connected"
        return await self._conn.execute(query, params or ())

    # ---------- public API ----------

    async def execute(
        self,
        query: str,
        params: Iterable[Any] | None = None,
        *,
        commit: bool = False,
    ) -> aiosqlite.Cursor:
        """
        Выполняет SQL-запрос, не возвращая результат запроса (rows)
        
        :param query: SQL-запрос
        :param params: Параметры запроса
        :param commit: Автоматически коммитить изменения
        :return: None
        """
        assert self._conn is not None, "Database not connected"
        cursor = await self._execute(query, params)
        if commit:
            await self.commit()
        return cursor

    async def executemany(
        self,
        query: str,
        params: Iterable[Iterable[Any]],
        *,
        commit: bool = False,
    ) -> None:
        """
        Выполняет SQL-запрос для набора параметров без возврата результата
        
        :param query: SQL-запрос
        :param params: Параметры запроса
        :param commit: Автоматически коммитить изменения
        :return: None
        """
        assert self._conn is not None, "Database not connected"
        await self._conn.executemany(query, params)
        if commit:
            await self.commit()

    async def fetchone(
        self,
        query: str,
        params: Iterable[Any] | None = None,
    ) -> Optional[aiosqlite.Row]:
        """
        Возвращает первую строку результата запроса или None
        
        :param query: SQL-запрос
        :param params: Параметры запроса
        :return: aiosqlite.Row или None
        """
        assert self._conn is not None, "Database not connected"
        cursor = await self._execute(query, params)
        return await cursor.fetchone()

    async def fetchall(
        self,
        query: str,
        params: Iterable[Any] | None = None,
    ) -> Iterable[aiosqlite.Row]:
        """
        Возвращает все строки результата запроса
        
        :param query: SQL-запрос
        :param params: Параметры запроса
        :return: aiosqlite.Row
        """
        assert self._conn is not None, "Database not connected"
        cursor = await self._execute(query, params)
        return await cursor.fetchall()

    # ---------- transactions ----------

    async def begin(self) -> None:
        """
        Начинает транзакцию вручную.

        Для конкурентного доступа к деньгам нужно использовать
        BEGIN IMMEDIATE, чтобы сразу взять write-lock.
        Это предотвращает состояние гонки.
        """
        assert self._conn is not None, "Database not connected"
        await self._conn.execute("BEGIN IMMEDIATE")

    async def commit(self) -> None:
        """Фиксирует текущую транзакцию"""
        assert self._conn is not None, "Database not connected"
        await self._conn.commit()

    async def rollback(self) -> None:
        """Откатывает изменения в базе данных"""
        assert self._conn is not None, "Database not connected"
        await self._conn.rollback()
