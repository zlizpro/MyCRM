"""
MiniCRM 数据库管理器核心

负责数据库连接管理和基本操作。
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from ...core.exceptions import DatabaseError


class DatabaseManager:
    """
    数据库管理器核心类

    负责数据库连接、事务管理和基本CRUD操作。
    """

    def __init__(self, db_path: Path):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self._db_path = Path(db_path)
        self._connection: sqlite3.Connection | None = None
        self._logger = logging.getLogger(__name__)

        # 确保数据库目录存在
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._logger.debug(f"数据库管理器初始化: {self._db_path}")

    def initialize_database(self) -> None:
        """初始化数据库"""
        try:
            self._connect()

            # 导入其他模块来完成初始化
            from .database_initializer import DatabaseInitializer
            from .database_schema import DatabaseSchema

            schema = DatabaseSchema()
            initializer = DatabaseInitializer(self._connection)

            # 创建表结构
            schema.create_tables(self._connection)

            # 创建索引
            schema.create_indexes(self._connection)

            # 插入初始数据
            initializer.insert_initial_data()

            self._connection.commit()
            self._logger.info("数据库初始化完成")

        except Exception as e:
            if self._connection:
                self._connection.rollback()
            raise DatabaseError(f"数据库初始化失败: {e}") from e

    def _connect(self) -> None:
        """创建数据库连接"""
        try:
            self._connection = sqlite3.connect(
                self._db_path, check_same_thread=False, timeout=30.0
            )

            # 设置行工厂，使查询结果可以通过列名访问
            self._connection.row_factory = sqlite3.Row

            # 启用外键约束
            self._connection.execute("PRAGMA foreign_keys = ON")

            # 设置WAL模式以提高并发性能
            self._connection.execute("PRAGMA journal_mode = WAL")

            self._logger.debug("数据库连接已建立")

        except Exception as e:
            raise DatabaseError(f"数据库连接失败: {e}") from e

    @contextmanager
    def transaction(self):
        """
        事务上下文管理器

        使用方法:
            with db_manager.transaction():
                # 执行数据库操作
                pass
        """
        if not self._connection:
            self._connect()

        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            raise DatabaseError(f"事务执行失败: {e}") from e

    def execute_query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        执行查询语句

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            查询结果列表
        """
        if not self._connection:
            self._connect()

        try:
            cursor = self._connection.execute(sql, params)
            results = cursor.fetchall()
            self._logger.debug(f"查询执行成功，返回 {len(results)} 条记录")
            return results
        except Exception as e:
            self._logger.error(f"查询执行失败: {sql}, 参数: {params}, 错误: {e}")
            raise DatabaseError(f"查询执行失败: {e}", sql) from e

    def execute_insert(self, sql: str, params: tuple = ()) -> int:
        """
        执行插入语句

        Args:
            sql: SQL插入语句
            params: 插入参数

        Returns:
            新插入记录的ID
        """
        if not self._connection:
            self._connect()

        try:
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            record_id = cursor.lastrowid
            self._logger.debug(f"插入执行成功，新记录ID: {record_id}")
            return record_id
        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"插入执行失败: {sql}, 参数: {params}, 错误: {e}")
            raise DatabaseError(f"插入执行失败: {e}", sql) from e

    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """
        执行更新语句

        Args:
            sql: SQL更新语句
            params: 更新参数

        Returns:
            受影响的行数
        """
        if not self._connection:
            self._connect()

        try:
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            affected_rows = cursor.rowcount
            self._logger.debug(f"更新执行成功，影响 {affected_rows} 行")
            return affected_rows
        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"更新执行失败: {sql}, 参数: {params}, 错误: {e}")
            raise DatabaseError(f"更新执行失败: {e}", sql) from e

    def execute_delete(self, sql: str, params: tuple = ()) -> int:
        """
        执行删除语句

        Args:
            sql: SQL删除语句
            params: 删除参数

        Returns:
            删除的行数
        """
        if not self._connection:
            self._connect()

        try:
            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            deleted_rows = cursor.rowcount
            self._logger.debug(f"删除执行成功，删除 {deleted_rows} 行")
            return deleted_rows
        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"删除执行失败: {sql}, 参数: {params}, 错误: {e}")
            raise DatabaseError(f"删除执行失败: {e}", sql) from e

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            表结构信息列表
        """
        try:
            sql = "PRAGMA table_info(?)"
            rows = self.execute_query(sql, (table_name,))

            return [
                {
                    "column_id": row["cid"],
                    "name": row["name"],
                    "type": row["type"],
                    "not_null": bool(row["notnull"]),
                    "default_value": row["dflt_value"],
                    "primary_key": bool(row["pk"]),
                }
                for row in rows
            ]
        except Exception as e:
            raise DatabaseError(f"获取表信息失败: {e}") from e

    def backup_database(self, backup_path: Path) -> bool:
        """
        备份数据库

        Args:
            backup_path: 备份文件路径

        Returns:
            备份是否成功
        """
        try:
            if not self._connection:
                self._connect()

            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建备份连接
            backup_conn = sqlite3.connect(backup_path)

            # 执行备份
            self._connection.backup(backup_conn)
            backup_conn.close()

            self._logger.info(f"数据库备份成功: {backup_path}")
            return True

        except Exception as e:
            self._logger.error(f"数据库备份失败: {e}")
            return False

    def close(self) -> None:
        """关闭数据库连接"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                self._logger.debug("数据库连接已关闭")
        except Exception as e:
            self._logger.error(f"关闭数据库连接时出错: {e}")

    @property
    def is_connected(self) -> bool:
        """检查是否已连接到数据库"""
        return self._connection is not None

    @property
    def database_path(self) -> Path:
        """获取数据库文件路径"""
        return self._db_path

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()
