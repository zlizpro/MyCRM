"""业务流程模块迁移 v1.2.0.

创建业务流程相关的表结构,包括:
- quotes: 报价信息
- quote_items: 报价明细
- contracts: 合同信息
- service_tickets: 售后工单
- tasks: 任务管理
"""

from __future__ import annotations


def get_migration_sql() -> list[str]:
    """获取迁移SQL语句列表.

    Returns:
        list[str]: SQL语句列表
    """
    return [
        # 报价表
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            supplier_id INTEGER,
            quote_number TEXT NOT NULL UNIQUE,
            quote_date TEXT NOT NULL,
            valid_until TEXT NOT NULL,
            total_amount REAL DEFAULT 0 CHECK(total_amount >= 0),
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'sent', 'accepted', 'rejected', 'expired')),
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
        """,
        # 报价明细表
        """
        CREATE TABLE IF NOT EXISTS quote_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quote_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            product_spec TEXT,
            quantity REAL NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            total_price REAL NOT NULL CHECK(total_price >= 0),
            notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
        )
        """,
        # 合同表
        """
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            supplier_id INTEGER,
            quote_id INTEGER,
            contract_number TEXT NOT NULL UNIQUE,
            contract_date TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            contract_amount REAL NOT NULL CHECK(contract_amount >= 0),
            status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'signed', 'active', 'completed', 'terminated')),
            terms TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (quote_id) REFERENCES quotes(id)
        )
        """,
        # 售后工单表
        """
        CREATE TABLE IF NOT EXISTS service_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            supplier_id INTEGER,
            contract_id INTEGER,
            ticket_number TEXT NOT NULL UNIQUE,
            issue_type TEXT NOT NULL CHECK(issue_type IN ('quality', 'delivery', 'installation', 'maintenance', 'other')),
            description TEXT NOT NULL,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'closed')),
            assigned_to TEXT,
            resolution TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (contract_id) REFERENCES contracts(id)
        )
        """,
        # 任务管理表
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            customer_id INTEGER,
            supplier_id INTEGER,
            assigned_to TEXT,
            due_date TEXT,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
            task_type TEXT DEFAULT 'general' CHECK(task_type IN ('general', 'follow_up', 'reminder', 'meeting')),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            deleted_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
        )
        """,
        # 创建索引
        "CREATE INDEX IF NOT EXISTS idx_quotes_customer_id ON quotes(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_supplier_id ON quotes(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_number ON quotes(quote_number)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(quote_date)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status)",
        "CREATE INDEX IF NOT EXISTS idx_quotes_deleted_at ON quotes(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_quote_items_quote_id ON quote_items(quote_id)",
        "CREATE INDEX IF NOT EXISTS idx_quote_items_product_name ON quote_items(product_name)",
        "CREATE INDEX IF NOT EXISTS idx_quote_items_deleted_at ON quote_items(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_customer_id ON contracts(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_supplier_id ON contracts(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_quote_id ON contracts(quote_id)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_number ON contracts(contract_number)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_date ON contracts(contract_date)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)",
        "CREATE INDEX IF NOT EXISTS idx_contracts_deleted_at ON contracts(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_customer_id ON service_tickets(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_supplier_id ON service_tickets(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_contract_id ON service_tickets(contract_id)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_number ON service_tickets(ticket_number)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_type ON service_tickets(issue_type)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_status ON service_tickets(status)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_priority ON service_tickets(priority)",
        "CREATE INDEX IF NOT EXISTS idx_service_tickets_deleted_at ON service_tickets(deleted_at)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_customer_id ON tasks(customer_id)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_supplier_id ON tasks(supplier_id)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type)",
        "CREATE INDEX IF NOT EXISTS idx_tasks_deleted_at ON tasks(deleted_at)",
    ]


def get_rollback_sql() -> list[str]:
    """获取回滚SQL语句列表.

    Returns:
        list[str]: 回滚SQL语句列表
    """
    return [
        # 删除索引
        "DROP INDEX IF EXISTS idx_tasks_deleted_at",
        "DROP INDEX IF EXISTS idx_tasks_type",
        "DROP INDEX IF EXISTS idx_tasks_status",
        "DROP INDEX IF EXISTS idx_tasks_due_date",
        "DROP INDEX IF EXISTS idx_tasks_assigned_to",
        "DROP INDEX IF EXISTS idx_tasks_supplier_id",
        "DROP INDEX IF EXISTS idx_tasks_customer_id",
        "DROP INDEX IF EXISTS idx_service_tickets_deleted_at",
        "DROP INDEX IF EXISTS idx_service_tickets_priority",
        "DROP INDEX IF EXISTS idx_service_tickets_status",
        "DROP INDEX IF EXISTS idx_service_tickets_type",
        "DROP INDEX IF EXISTS idx_service_tickets_number",
        "DROP INDEX IF EXISTS idx_service_tickets_contract_id",
        "DROP INDEX IF EXISTS idx_service_tickets_supplier_id",
        "DROP INDEX IF EXISTS idx_service_tickets_customer_id",
        "DROP INDEX IF EXISTS idx_contracts_deleted_at",
        "DROP INDEX IF EXISTS idx_contracts_status",
        "DROP INDEX IF EXISTS idx_contracts_date",
        "DROP INDEX IF EXISTS idx_contracts_number",
        "DROP INDEX IF EXISTS idx_contracts_quote_id",
        "DROP INDEX IF EXISTS idx_contracts_supplier_id",
        "DROP INDEX IF EXISTS idx_contracts_customer_id",
        "DROP INDEX IF EXISTS idx_quote_items_deleted_at",
        "DROP INDEX IF EXISTS idx_quote_items_product_name",
        "DROP INDEX IF EXISTS idx_quote_items_quote_id",
        "DROP INDEX IF EXISTS idx_quotes_deleted_at",
        "DROP INDEX IF EXISTS idx_quotes_status",
        "DROP INDEX IF EXISTS idx_quotes_date",
        "DROP INDEX IF EXISTS idx_quotes_number",
        "DROP INDEX IF EXISTS idx_quotes_supplier_id",
        "DROP INDEX IF EXISTS idx_quotes_customer_id",
        # 删除表
        "DROP TABLE IF EXISTS tasks",
        "DROP TABLE IF EXISTS service_tickets",
        "DROP TABLE IF EXISTS contracts",
        "DROP TABLE IF EXISTS quote_items",
        "DROP TABLE IF EXISTS quotes",
    ]


def get_initial_data() -> list[tuple]:
    """获取初始数据.

    Returns:
        list[tuple]: (table_name, data_list) 的列表
    """
    # 业务流程表通常不需要初始数据
    return []


# 迁移元数据
MIGRATION_INFO = {
    "version": "1.2.0",
    "description": "业务流程模块 - 报价、合同、售后工单等表",
    "dependencies": ["1.0.0", "1.1.0"],
    "created_at": "2025-01-19T12:00:00",
}
