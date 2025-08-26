"""MiniCRM 数据库版本迁移管理器.

管理数据库schema的版本化升级和回滚.
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from pathlib import Path
import sqlite3
from typing import TYPE_CHECKING

from minicrm.core.exceptions import DatabaseError


if TYPE_CHECKING:
    from .database_manager_enhanced import EnhancedDatabaseManager


class DatabaseMigration:
    """数据库版本迁移管理器.

    管理数据库schema的版本化升级和回滚.
    """

    def __init__(self, db_manager: EnhancedDatabaseManager):
        """初始化迁移管理器.

        Args:
            db_manager: 数据库管理器实例
        """
        self._db_manager = db_manager
        self._logger = logging.getLogger(__name__)
        self._migrations_path = Path(__file__).parent / "migrations"

    def get_current_version(self) -> str:
        """获取当前数据库版本.

        Returns:
            str: 当前版本号
        """
        try:
            # 首先检查版本表是否存在
            table_check = self._db_manager.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='database_versions'"
            )

            if not table_check:
                # 版本表不存在, 返回初始版本
                return "0.0.0"

            result = self._db_manager.execute_query(
                "SELECT version FROM database_versions ORDER BY created_at DESC LIMIT 1"
            )
            return result[0]["version"] if result else "0.0.0"
        except (sqlite3.Error, KeyError, IndexError):
            # 任何错误都返回初始版本
            return "0.0.0"

    def migrate_to_version(self, target_version: str) -> bool:
        """迁移到指定版本.

        Args:
            target_version: 目标版本号

        Returns:
            bool: 迁移是否成功
        """
        current_version = self.get_current_version()

        if current_version == target_version:
            self._logger.info("数据库已是目标版本: %s", target_version)
            return True

        try:
            # 获取需要执行的迁移脚本
            migrations = self._get_migration_scripts(current_version, target_version)

            with self._db_manager.transaction():
                for migration in migrations:
                    self._execute_migration(migration)

                # 更新版本记录
                self._update_version_record(target_version)

            self._logger.info(
                "数据库迁移成功: %s -> %s", current_version, target_version
            )
        except (sqlite3.Error, DatabaseError):
            self._logger.exception("数据库迁移失败")
            return False
        else:
            return True

    def _get_migration_scripts(self, from_version: str, to_version: str) -> list[dict]:
        """获取迁移脚本列表.

        Args:
            from_version: 起始版本
            to_version: 目标版本

        Returns:
            list[dict]: 迁移脚本信息列表
        """
        # 这里应该实现版本比较和脚本选择逻辑
        # 简化实现, 返回基础迁移脚本
        _ = from_version, to_version  # 标记参数已使用
        return [
            {
                "version": "1.0.0",
                "description": "初始数据库结构",
                "script": self._get_initial_schema_script(),
            }
        ]

    def _execute_migration(self, migration: dict) -> None:
        """执行单个迁移脚本.

        Args:
            migration: 迁移脚本信息
        """
        self._logger.info(
            "执行迁移: %s - %s", migration["version"], migration["description"]
        )

        # 执行迁移脚本中的SQL语句
        for sql in migration["script"]:
            self._db_manager.execute_update(sql)

    def _update_version_record(self, version: str) -> None:
        """更新版本记录.

        Args:
            version: 新版本号
        """
        sql = """
        INSERT INTO database_versions (version, created_at, description)
        VALUES (?, ?, ?)
        """
        description = f"迁移到版本 {version}"
        self._db_manager.execute_insert(
            sql, (version, datetime.now(timezone.utc).isoformat(), description)
        )

    def _get_initial_schema_script(self) -> list[str]:
        """获取初始数据库结构脚本.

        Returns:
            list[str]: SQL语句列表
        """
        return [
            # 版本管理表
            """
            CREATE TABLE IF NOT EXISTS database_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                description TEXT
            )
            """,
            # 客户类型表
            """
            CREATE TABLE IF NOT EXISTS customer_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color_code TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT
            )
            """,
            # 客户表
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                company TEXT,
                address TEXT,
                customer_type_id INTEGER,
                level TEXT DEFAULT 'normal',
                credit_limit REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT,
                FOREIGN KEY (customer_type_id) REFERENCES customer_types(id)
            )
            """,
        ]
