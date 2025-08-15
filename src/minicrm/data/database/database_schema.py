"""
MiniCRM 数据库模式定义

定义数据库表结构和索引。
"""

import sqlite3

from ...core.exceptions import DatabaseError


class DatabaseSchema:
    """
    数据库模式管理器

    负责创建和管理数据库表结构和索引。
    """

    def create_tables(self, connection: sqlite3.Connection) -> None:
        """创建数据库表结构"""
        try:
            # 客户类型表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS customer_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 客户表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    customer_type_id INTEGER,
                    contact_person TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_type_id) REFERENCES customer_types (id)
                )
            """)

            # 供应商表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    contact_person TEXT,
                    quality_rating REAL DEFAULT 0.0,
                    cooperation_years INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 报价状态表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS quote_statuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 报价表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    customer_name TEXT NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    quote_date DATE,
                    valid_until DATE,
                    quote_status_id INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (quote_status_id) REFERENCES quote_statuses (id)
                )
            """)

            # 报价项目表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS quote_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    specification TEXT,
                    unit TEXT,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(10,2) NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (quote_id) REFERENCES quotes (id) ON DELETE CASCADE
                )
            """)

            # 合同表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    quote_id INTEGER,
                    contract_amount DECIMAL(10,2) NOT NULL,
                    start_date DATE,
                    end_date DATE,
                    status TEXT DEFAULT 'active',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (quote_id) REFERENCES quotes (id)
                )
            """)

            # 互动类型表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS interaction_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 客户互动记录表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS customer_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    interaction_type_id INTEGER,
                    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subject TEXT,
                    content TEXT,
                    follow_up_required BOOLEAN DEFAULT FALSE,
                    follow_up_date DATE,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (interaction_type_id) REFERENCES interaction_types (id)
                )
            """)

            # 供应商互动记录表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS supplier_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    interaction_type_id INTEGER,
                    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    subject TEXT,
                    content TEXT,
                    follow_up_required BOOLEAN DEFAULT FALSE,
                    follow_up_date DATE,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                    FOREIGN KEY (interaction_type_id) REFERENCES interaction_types (id)
                )
            """)

            # 财务记录表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS financial_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    contract_id INTEGER,
                    record_type TEXT NOT NULL, -- 'receivable', 'payable', 'payment', 'receipt'
                    amount DECIMAL(10,2) NOT NULL,
                    due_date DATE,
                    paid_date DATE,
                    status TEXT DEFAULT 'pending', -- 'pending', 'paid', 'overdue'
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                    FOREIGN KEY (contract_id) REFERENCES contracts (id)
                )
            """)

            # 任务表
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    due_date DATE,
                    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
                    status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed', 'cancelled'
                    assigned_to TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            """)

        except Exception as e:
            raise DatabaseError(f"创建表结构失败: {e}") from e

    def create_indexes(self, connection: sqlite3.Connection) -> None:
        """创建数据库索引以提高查询性能"""
        indexes = [
            # 客户表索引
            "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)",
            "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)",
            "CREATE INDEX IF NOT EXISTS idx_customers_type ON customers(customer_type_id)",
            "CREATE INDEX IF NOT EXISTS idx_customers_created ON customers(created_at)",
            # 供应商表索引
            "CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name)",
            "CREATE INDEX IF NOT EXISTS idx_suppliers_phone ON suppliers(phone)",
            "CREATE INDEX IF NOT EXISTS idx_suppliers_rating ON suppliers(quality_rating)",
            # 报价表索引
            "CREATE INDEX IF NOT EXISTS idx_quotes_number ON quotes(quote_number)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_customer ON quotes(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_date ON quotes(quote_date)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(quote_status_id)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_valid_until ON quotes(valid_until)",
            # 报价项目表索引
            "CREATE INDEX IF NOT EXISTS idx_quote_items_quote ON quote_items(quote_id)",
            "CREATE INDEX IF NOT EXISTS idx_quote_items_product ON quote_items(product_name)",
            # 合同表索引
            "CREATE INDEX IF NOT EXISTS idx_contracts_number ON contracts(contract_number)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_customer ON contracts(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_dates ON contracts(start_date, end_date)",
            # 互动记录表索引
            "CREATE INDEX IF NOT EXISTS idx_customer_interactions_customer ON customer_interactions(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_customer_interactions_date ON customer_interactions(interaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_customer_interactions_type ON customer_interactions(interaction_type_id)",
            "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_supplier ON supplier_interactions(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_supplier_interactions_date ON supplier_interactions(interaction_date)",
            # 财务记录表索引
            "CREATE INDEX IF NOT EXISTS idx_financial_records_customer ON financial_records(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_financial_records_supplier ON financial_records(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_financial_records_type ON financial_records(record_type)",
            "CREATE INDEX IF NOT EXISTS idx_financial_records_status ON financial_records(status)",
            "CREATE INDEX IF NOT EXISTS idx_financial_records_due_date ON financial_records(due_date)",
            # 任务表索引
            "CREATE INDEX IF NOT EXISTS idx_tasks_customer ON tasks(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_supplier ON tasks(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to)",
        ]

        for index_sql in indexes:
            connection.execute(index_sql)
