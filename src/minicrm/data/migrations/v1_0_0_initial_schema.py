"""数据库初始结构迁移 v1.0.0.

创建客户相关的基础表结构,包括:
- database_versions: 数据库版本管理
- customer_types: 客户类型定义
- customers: 客户基本信息
- customer_interactions: 客户互动记录
"""

from __future__ import annotations

from datetime import datetime, timezone


def get_migration_sql() -> list[str]:
    """获取迁移SQL语句列表.

    Returns:
        list[str]: SQL语句列表
    """
    return [
        # 数据库版本管理表
        """
        CREATE TABLE IF NOT EXISTS database_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            created_at TEXT NOT NULL,
            description TEXT,
            UNIQUE(version)
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
            level TEXT DEFAULT 'normal' CHECK(level IN ('vip', 'important', 'normal', 'potential')),
            credit_limit REAL DEFAULT 0 CHECK(credit_limit >= 0),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_type_id) REFERENCES customer_types(id)
        )
        """,
        # 客户互动记录表
        """
        CREATE TABLE IF NOT EXISTS customer_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL CHECK(interaction_type IN ('call', 'email', 'meeting', 'visit', 'other')),
            subject TEXT,
            content TEXT,
            interaction_date TEXT NOT NULL,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
        """,
        # 创建索引以提高查询性能
        "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)",
        "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)",
        "CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company)",
        "CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(customer_type_id)",
        "CREATE INDEX IF NOT EXISTS idx_customers_level ON customers(level)",
        "CREATE INDEX IF NOT EXISTS idx_customers_created_at ON customers(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_customers_deleted_at ON customers(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_customer_types_name ON customer_types(name)",
        "CREATE INDEX IF NOT EXISTS idx_customer_types_deleted_at ON customer_types(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_customer_interactions_customer_id ON customer_interactions(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_customer_interactions_type ON customer_interactions(interaction_type)",
        "CREATE INDEX IF NOT EXISTS idx_customer_interactions_date ON customer_interactions(interaction_date)",
        "CREATE INDEX IF NOT EXISTS idx_customer_interactions_deleted_at ON customer_interactions(deleted_at)",
    ]


def get_rollback_sql() -> list[str]:
    """获取回滚SQL语句列表.

    Returns:
        list[str]: 回滚SQL语句列表
    """
    return [
        "DROP INDEX IF EXISTS idx_customer_interactions_deleted_at",
        "DROP INDEX IF EXISTS idx_customer_interactions_date",
        "DROP INDEX IF EXISTS idx_customer_interactions_type",
        "DROP INDEX IF EXISTS idx_customer_interactions_customer_id",
        "DROP INDEX IF EXISTS idx_customer_types_deleted_at",
        "DROP INDEX IF EXISTS idx_customer_types_name",
        "DROP INDEX IF EXISTS idx_customers_deleted_at",
        "DROP INDEX IF EXISTS idx_customers_created_at",
        "DROP INDEX IF EXISTS idx_customers_level",
        "DROP INDEX IF EXISTS idx_customers_type",
        "DROP INDEX IF EXISTS idx_customers_company",
        "DROP INDEX IF EXISTS idx_customers_phone",
        "DROP INDEX IF EXISTS idx_customers_name",
        "DROP TABLE IF EXISTS customer_interactions",
        "DROP TABLE IF EXISTS customers",
        "DROP TABLE IF EXISTS customer_types",
        "DROP TABLE IF EXISTS database_versions",
    ]


def get_initial_data() -> list[tuple]:
    """获取初始数据.

    Returns:
        list[tuple]: (table_name, data_list) 的列表
    """
    now = datetime.now(timezone.utc).isoformat()

    return [
        # 默认客户类型
        (
            "customer_types",
            [
                {
                    "name": "制造企业",
                    "description": "生产制造类企业客户",
                    "color_code": "#2196F3",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "贸易公司",
                    "description": "贸易流通类企业客户",
                    "color_code": "#4CAF50",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "装修公司",
                    "description": "装修装饰类企业客户",
                    "color_code": "#FF9800",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "个人客户",
                    "description": "个人消费者客户",
                    "color_code": "#9C27B0",
                    "created_at": now,
                    "updated_at": now,
                },
            ],
        )
    ]


# 迁移元数据
MIGRATION_INFO = {
    "version": "1.0.0",
    "description": "初始数据库结构 - 客户管理相关表",
    "dependencies": [],
    "created_at": "2025-01-19T10:00:00",
}
