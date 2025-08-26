"""MiniCRM 数据库连接池模块.

轻量级SQLite连接池实现, 为桌面应用优化.
"""

from __future__ import annotations

import logging
from queue import Empty, Queue
import sqlite3
import threading
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


class ConnectionPool:
    """轻量级SQLite连接池.

    为桌面应用优化的简单连接池实现, 支持并发访问控制.
    """

    def __init__(self, db_path: Path, max_connections: int = 5):
        """初始化连接池.

        Args:
            db_path: 数据库文件路径
            max_connections: 最大连接数
        """
        self._db_path = db_path
        self._max_connections = max_connections
        self._pool: Queue = Queue(maxsize=max_connections)
        self._active_connections = 0
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)

    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接.

        Returns:
            sqlite3.Connection: 数据库连接对象
        """
        try:
            # 尝试从池中获取现有连接
            connection = self._pool.get_nowait()
        except Empty:
            # 池中无可用连接, 尝试创建新连接
            with self._lock:
                if self._active_connections < self._max_connections:
                    connection = self._create_connection()
                    self._active_connections += 1
                    self._logger.debug(
                        "创建新连接, 当前活跃连接数: %d", self._active_connections
                    )
                    return connection

            # 达到最大连接数, 等待可用连接
            self._logger.debug("等待可用连接")
            return self._pool.get(timeout=30)  # type: ignore[no-any-return]
        else:
            self._logger.debug("从连接池获取连接")
            return connection  # type: ignore[no-any-return]

    def return_connection(self, connection: sqlite3.Connection) -> None:
        """归还连接到池中.

        Args:
            connection: 要归还的连接
        """
        try:
            # 检查连接是否仍然有效
            connection.execute("SELECT 1")
            self._pool.put_nowait(connection)
            self._logger.debug("连接已归还到池中")
        except (sqlite3.Error, OSError, ValueError):
            # 连接已损坏, 关闭并减少计数
            with self._lock:
                connection.close()
                self._active_connections -= 1
                self._logger.warning("损坏的连接已关闭")

    def _create_connection(self) -> sqlite3.Connection:
        """创建新的数据库连接.

        Returns:
            sqlite3.Connection: 新的数据库连接
        """
        connection = sqlite3.connect(
            self._db_path, check_same_thread=False, timeout=30.0
        )

        # 配置连接
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")

        return connection

    def close_all(self) -> None:
        """关闭所有连接."""
        while not self._pool.empty():
            connection = self._pool.get_nowait()
            connection.close()

        with self._lock:
            self._active_connections = 0

        self._logger.info("所有数据库连接已关闭")
