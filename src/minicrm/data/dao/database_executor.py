"""
MiniCRM 数据库执行器

负责执行数据库操作和事务管理
"""

import logging
import sqlite3
from contextlib import contextmanager
from typing import Any

from ...core import DatabaseError


class DatabaseExecutor:
    """数据库执行器"""

    def __init__(self, database_manager=None):
        """
        初始化数据库执行器

        Args:
            database_manager: 数据库管理器实例
        """
        self._db_manager = database_manager
        self._logger = logging.getLogger(__name__)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        try:
            if self._db_manager:
                return self._db_manager.get_connection()
            else:
                # 如果没有数据库管理器，使用默认连接
                return sqlite3.connect("minicrm.db")

        except Exception as e:
            self._logger.error(f"获取数据库连接失败: {e}")
            raise DatabaseError(f"数据库连接失败: {e}") from e

    @contextmanager
    def _transaction(self):
        """事务上下文管理器"""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self._logger.error(f"事务回滚: {e}")
            raise
        finally:
            conn.close()

    def execute_query(
        self,
        sql: str,
        params: tuple = None,
        fetch_one: bool = False,
        fetch_all: bool = True,
    ) -> Any:
        """
        执行查询SQL（SELECT）

        Args:
            sql: SQL语句
            params: 参数元组
            fetch_one: 是否只获取一条记录
            fetch_all: 是否获取所有记录

        Returns:
            查询结果
        """
        try:
            with self._transaction() as conn:
                conn.row_factory = sqlite3.Row  # 使用Row工厂，支持字典式访问
                cursor = conn.cursor()

                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch_all:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    return cursor

        except sqlite3.Error as e:
            error_msg = f"SQL查询执行失败: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e
        except Exception as e:
            error_msg = f"查询执行异常: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e

    def execute_update(self, sql: str, params: tuple = None) -> int:
        """
        执行更新SQL（INSERT, UPDATE, DELETE）

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            int: 受影响的行数或新插入记录的ID
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()

                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)

                # 对于INSERT操作，返回新插入记录的ID
                if sql.strip().upper().startswith("INSERT"):
                    return cursor.lastrowid
                else:
                    # 对于UPDATE和DELETE操作，返回受影响的行数
                    return cursor.rowcount

        except sqlite3.Error as e:
            error_msg = f"SQL更新执行失败: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e
        except Exception as e:
            error_msg = f"更新执行异常: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e

    def execute_batch(self, sql: str, params_list: list[tuple]) -> int:
        """
        批量执行SQL

        Args:
            sql: SQL语句
            params_list: 参数列表

        Returns:
            int: 受影响的总行数
        """
        try:
            with self._transaction() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, params_list)
                return cursor.rowcount

        except sqlite3.Error as e:
            error_msg = f"批量SQL执行失败: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e
        except Exception as e:
            error_msg = f"批量执行异常: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, sql) from e

    def execute_script(self, script: str) -> None:
        """
        执行SQL脚本

        Args:
            script: SQL脚本内容
        """
        try:
            with self._transaction() as conn:
                conn.executescript(script)

        except sqlite3.Error as e:
            error_msg = f"SQL脚本执行失败: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, script) from e
        except Exception as e:
            error_msg = f"脚本执行异常: {e}"
            self._logger.error(error_msg)
            raise DatabaseError(error_msg, script) from e
