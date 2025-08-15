"""
Transfunctions - 数据库异步操作

提供统一的数据库操作接口。
"""

from typing import Any

from .base import AsyncPatternMixin


class UnifiedDatabaseOperations(AsyncPatternMixin):
    """统一的数据库操作接口

    提供同步和异步数据库操作的统一接口。
    """

    def __init__(self, sync_connection, async_connection=None):
        super().__init__()
        self.sync_connection = sync_connection
        self.async_connection = async_connection

    def query(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        """统一的查询接口"""

        def sync_query():
            cursor = self.sync_connection.execute(sql, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]

        async def async_query():
            if self.async_connection:
                # 如果有异步连接，使用异步操作
                cursor = await self.async_connection.execute(sql, params)
                columns = [description[0] for description in cursor.description]
                rows = await cursor.fetchall()
                return [dict(zip(columns, row, strict=False)) for row in rows]
            else:
                # 否则在线程池中执行同步操作
                return await self._wrap_sync_to_async(sync_query)()

        return self.sync_or_async(sync_query, async_query)()

    def execute(self, sql: str, params: tuple = ()) -> int:
        """统一的执行接口"""

        def sync_execute():
            cursor = self.sync_connection.execute(sql, params)
            self.sync_connection.commit()
            return cursor.rowcount

        async def async_execute():
            if self.async_connection:
                cursor = await self.async_connection.execute(sql, params)
                await self.async_connection.commit()
                return cursor.rowcount
            else:
                return await self._wrap_sync_to_async(sync_execute)()

        return self.sync_or_async(sync_execute, async_execute)()


def create_unified_database(sync_connection, async_connection=None):
    """创建统一数据库操作实例"""
    return UnifiedDatabaseOperations(sync_connection, async_connection)
