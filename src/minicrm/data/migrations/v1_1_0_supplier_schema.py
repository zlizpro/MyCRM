"""供应商管理模块迁移 v1.1.0.

创建供应商相关的表结构,包括:
- supplier_types: 供应商类型定义
- suppliers: 供应商基本信息
- supplier_interactions: 供应商互动记录
"""

from __future__ import annotations

from datetime import datetime, timezone


def get_migration_sql() -> list[str]:
    """获取迁移SQL语句列表.

    Returns:
        list[str]: SQL语句列表
    """
    return [
        # 供应商类型表
        """
        CREATE TABLE IF NOT EXISTS supplier_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            color_code TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT
        )
        """,
        # 供应商表
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            company TEXT,
            address TEXT,
            supplier_type_id INTEGER,
            level TEXT DEFAULT 'normal' CHECK(level IN ('strategic', 'important', 'normal', 'backup')),
            business_license TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (supplier_type_id) REFERENCES supplier_types(id)
        )
        """,
        # 供应商互动记录表
        """
        CREATE TABLE IF NOT EXISTS supplier_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL CHECK(interaction_type IN ('call', 'email', 'meeting', 'visit', 'inquiry', 'other')),
            subject TEXT,
            content TEXT,
            interaction_date TEXT NOT NULL,
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
        )
        """,
        # 创建索引
        "CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_phone ON suppliers(phone)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_company ON suppliers(company)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_contact_person ON suppliers(contact_person)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_type ON suppliers(supplier_type_id)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_level ON suppliers(level)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_created_at ON suppliers(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_suppliers_deleted_at ON suppliers(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_types_name ON supplier_types(name)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_types_deleted_at ON supplier_types(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_supplier_id ON supplier_interactions(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_type ON supplier_interactions(interaction_type)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_date ON supplier_interactions(interaction_date)",
        "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_deleted_at ON supplier_interactions(deleted_at)",
    ]


def get_rollback_sql() -> list[str]:
    """获取回滚SQL语句列表.

    Returns:
        list[str]: 回滚SQL语句列表
    """
    return [
        "DROP INDEX IF EXISTS idx_supplier_interactions_deleted_at",
        "DROP INDEX IF EXISTS idx_supplier_interactions_date",
        "DROP INDEX IF EXISTS idx_supplier_interactions_type",
        "DROP INDEX IF EXISTS idx_supplier_interactions_supplier_id",
        "DROP INDEX IF EXISTS idx_supplier_types_deleted_at",
        "DROP INDEX IF EXISTS idx_supplier_types_name",
        "DROP INDEX IF EXISTS idx_suppliers_deleted_at",
        "DROP INDEX IF EXISTS idx_suppliers_created_at",
        "DROP INDEX IF EXISTS idx_suppliers_level",
        "DROP INDEX IF EXISTS idx_suppliers_type",
        "DROP INDEX IF EXISTS idx_suppliers_contact_person",
        "DROP INDEX IF EXISTS idx_suppliers_company",
        "DROP INDEX IF EXISTS idx_suppliers_phone",
        "DROP INDEX IF EXISTS idx_suppliers_name",
        "DROP TABLE IF EXISTS supplier_interactions",
        "DROP TABLE IF EXISTS suppliers",
        "DROP TABLE IF EXISTS supplier_types",
    ]


def get_initial_data() -> list[tuple]:
    """获取初始数据.

    Returns:
        list[tuple]: (table_name, data_list) 的列表
    """
    now = datetime.now(timezone.utc).isoformat()

    return [
        # 默认供应商类型
        (
            "supplier_types",
            [
                {
                    "name": "板材供应商",
                    "description": "提供各类板材产品的供应商",
                    "color_code": "#2196F3",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "五金供应商",
                    "description": "提供五金配件的供应商",
                    "color_code": "#4CAF50",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "胶水供应商",
                    "description": "提供胶水粘合剂的供应商",
                    "color_code": "#FF9800",
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "name": "设备供应商",
                    "description": "提供生产设备的供应商",
                    "color_code": "#9C27B0",
                    "created_at": now,
                    "updated_at": now,
                },
            ],
        )
    ]


# 迁移元数据
MIGRATION_INFO = {
    "version": "1.1.0",
    "description": "供应商管理模块 - 供应商相关表",
    "dependencies": ["1.0.0"],
    "created_at": "2025-01-19T11:00:00",
}
