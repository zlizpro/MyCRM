"""
MiniCRM 数据库管理器

负责数据库连接、初始化和基本操作，提供：
- SQLite数据库连接管理
- 数据库初始化和迁移
- 事务管理
- 连接池管理
- 错误处理和重试
"""

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from minicrm.core.exceptions import DatabaseError


class DatabaseManager:
    """
    数据库管理器

    负责管理SQLite数据库的所有操作，包括：
    - 连接管理
    - 数据库初始化
    - 事务处理
    - 错误处理
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
        """
        初始化数据库

        创建必要的表结构和初始数据。
        """
        try:
            self._logger.info("开始初始化数据库...")

            # 创建连接
            self._connect()

            # 创建表结构
            self._create_tables()

            # 插入初始数据
            self._insert_initial_data()

            self._logger.info("数据库初始化完成")

        except Exception as e:
            self._logger.error(f"数据库初始化失败: {e}")
            raise DatabaseError(f"数据库初始化失败: {e}") from e

    def _connect(self) -> None:
        """创建数据库连接"""
        try:
            self._connection = sqlite3.connect(
                str(self._db_path), check_same_thread=False, timeout=30.0
            )

            # 设置行工厂，使查询结果可以通过列名访问
            self._connection.row_factory = sqlite3.Row

            # 启用外键约束
            self._connection.execute("PRAGMA foreign_keys = ON")

            # 设置WAL模式以提高并发性能
            self._connection.execute("PRAGMA journal_mode = WAL")

            self._logger.debug("数据库连接创建成功")

        except Exception as e:
            self._logger.error(f"数据库连接失败: {e}")
            raise DatabaseError(f"数据库连接失败: {e}") from e

    def _create_tables(self) -> None:
        """创建数据库表结构"""
        try:
            # 客户类型表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS customer_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 客户表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    company TEXT,
                    address TEXT,
                    customer_type_id INTEGER,
                    level TEXT DEFAULT 'normal',
                    credit_limit DECIMAL(15,2) DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_type_id) REFERENCES customer_types(id)
                )
            """)

            # 供应商类型表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS supplier_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 供应商表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    business_license TEXT,
                    supplier_type_id INTEGER,
                    level TEXT DEFAULT 'normal',
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_type_id) REFERENCES supplier_types(id)
                )
            """)

            # 产品表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    model TEXT,
                    category TEXT,
                    specification TEXT,
                    unit_price DECIMAL(15,2),
                    unit TEXT DEFAULT '件',
                    description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 客户互动记录表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS customer_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    interaction_type TEXT NOT NULL,
                    content TEXT,
                    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    follow_up_required BOOLEAN DEFAULT 0,
                    follow_up_date TIMESTAMP,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)

            # 任务表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    task_type TEXT DEFAULT 'general',
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    due_date TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            """)

            # 报价表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER NOT NULL,
                    total_amount DECIMAL(15,2) NOT NULL,
                    status TEXT DEFAULT 'draft',
                    valid_until TIMESTAMP,
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
            """)

            # 报价明细表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS quote_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote_id INTEGER NOT NULL,
                    product_id INTEGER,
                    product_name TEXT NOT NULL,
                    specification TEXT,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit_price DECIMAL(15,2) NOT NULL,
                    total_price DECIMAL(15,2) NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)

            # 合同表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contract_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    contract_type TEXT DEFAULT 'sales',
                    total_amount DECIMAL(15,2),
                    status TEXT DEFAULT 'draft',
                    signed_date TIMESTAMP,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    terms TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            """)

            # 订单表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    order_type TEXT DEFAULT 'sales',
                    total_amount DECIMAL(15,2) NOT NULL,
                    status TEXT DEFAULT 'pending',
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    delivery_date TIMESTAMP,
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
                )
            """)

            # 订单明细表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER,
                    product_name TEXT NOT NULL,
                    specification TEXT,
                    quantity DECIMAL(10,2) NOT NULL,
                    unit_price DECIMAL(15,2) NOT NULL,
                    total_price DECIMAL(15,2) NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
                )
            """)

            # 付款记录表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER,
                    supplier_id INTEGER,
                    order_id INTEGER,
                    payment_type TEXT NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    payment_method TEXT,
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    notes TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
                )
            """)

            # 产品售后记录表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS after_sales_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    product_id INTEGER,
                    order_id INTEGER,
                    issue_type TEXT NOT NULL,
                    issue_description TEXT,
                    resolution TEXT,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'medium',
                    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_date TIMESTAMP,
                    satisfaction_rating INTEGER,
                    created_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
                )
            """)

            # 供应商质量评级表
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS supplier_quality_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER NOT NULL,
                    rating_period TEXT NOT NULL,
                    quality_score INTEGER DEFAULT 0,
                    delivery_score INTEGER DEFAULT 0,
                    service_score INTEGER DEFAULT 0,
                    overall_score INTEGER DEFAULT 0,
                    comments TEXT,
                    rated_by TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
                )
            """)

            # 创建索引以提高查询性能
            self._create_indexes()

            # 提交事务
            self._connection.commit()

            self._logger.debug("数据库表结构创建完成")

        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"创建表结构失败: {e}")
            raise DatabaseError(f"创建表结构失败: {e}") from e

    def _create_indexes(self) -> None:
        """创建数据库索引以提高查询性能"""
        indexes = [
            # 客户表索引
            "CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name)",
            "CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)",
            "CREATE INDEX IF NOT EXISTS idx_customers_level ON customers(level)",
            "CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status)",
            # 供应商表索引
            "CREATE INDEX IF NOT EXISTS idx_suppliers_name ON suppliers(name)",
            "CREATE INDEX IF NOT EXISTS idx_suppliers_phone ON suppliers(phone)",
            "CREATE INDEX IF NOT EXISTS idx_suppliers_level ON suppliers(level)",
            # 互动记录索引
            "CREATE INDEX IF NOT EXISTS idx_interactions_customer ON customer_interactions(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_date ON customer_interactions(interaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_interactions_type ON customer_interactions(interaction_type)",
            # 任务索引
            "CREATE INDEX IF NOT EXISTS idx_tasks_customer ON tasks(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_supplier ON tasks(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)",
            "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)",
            # 报价索引
            "CREATE INDEX IF NOT EXISTS idx_quotes_customer ON quotes(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_number ON quotes(quote_number)",
            "CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status)",
            # 合同索引
            "CREATE INDEX IF NOT EXISTS idx_contracts_customer ON contracts(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_supplier ON contracts(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_number ON contracts(contract_number)",
            "CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)",
            # 订单索引
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_supplier ON orders(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_orders_number ON orders(order_number)",
            "CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)",
            "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)",
            # 付款记录索引
            "CREATE INDEX IF NOT EXISTS idx_payments_customer ON payments(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_supplier ON payments(supplier_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_order ON payments(order_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)",
            # 售后记录索引
            "CREATE INDEX IF NOT EXISTS idx_after_sales_customer ON after_sales_records(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_after_sales_product ON after_sales_records(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_after_sales_status ON after_sales_records(status)",
            "CREATE INDEX IF NOT EXISTS idx_after_sales_date ON after_sales_records(reported_date)",
        ]

        for index_sql in indexes:
            self._connection.execute(index_sql)

    def _insert_initial_data(self) -> None:
        """插入初始数据"""
        try:
            # 插入默认客户类型
            customer_types = [
                ("生态板客户", "主要采购生态板产品的客户"),
                ("家具板客户", "主要采购家具板产品的客户"),
                ("阻燃板客户", "主要采购阻燃板产品的客户"),
                ("综合客户", "采购多种板材产品的客户"),
            ]

            for name, description in customer_types:
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO customer_types (name, description)
                    VALUES (?, ?)
                """,
                    (name, description),
                )

            # 插入默认供应商类型
            supplier_types = [
                ("原材料供应商", "提供原材料的供应商"),
                ("设备供应商", "提供生产设备的供应商"),
                ("服务供应商", "提供各类服务的供应商"),
                ("物流供应商", "提供物流运输服务的供应商"),
            ]

            for name, description in supplier_types:
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO supplier_types (name, description)
                    VALUES (?, ?)
                """,
                    (name, description),
                )

            # 插入默认产品数据
            products = [
                (
                    "生态板E0级",
                    "E0-1220-2440",
                    "生态板",
                    "1220*2440*18mm",
                    120.00,
                    "张",
                ),
                (
                    "生态板E1级",
                    "E1-1220-2440",
                    "生态板",
                    "1220*2440*18mm",
                    100.00,
                    "张",
                ),
                ("家具板", "JJ-1220-2440", "家具板", "1220*2440*15mm", 85.00, "张"),
                (
                    "阻燃板B1级",
                    "ZR-1220-2440",
                    "阻燃板",
                    "1220*2440*18mm",
                    150.00,
                    "张",
                ),
                ("多层板", "DC-1220-2440", "多层板", "1220*2440*12mm", 75.00, "张"),
            ]

            for name, model, category, spec, price, unit in products:
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO products (name, model, category, specification, unit_price, unit)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (name, model, category, spec, price, unit),
                )

            # 提交事务
            self._connection.commit()

            self._logger.debug("初始数据插入完成")

        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"插入初始数据失败: {e}")
            raise DatabaseError(f"插入初始数据失败: {e}") from e

    @contextmanager
    def transaction(self):
        """
        事务上下文管理器

        使用方法:
        with db_manager.transaction():
            # 数据库操作
            pass
        """
        if not self._connection:
            self._connect()

        try:
            yield self._connection
            self._connection.commit()
        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"事务执行失败: {e}")
            raise DatabaseError(f"事务执行失败: {e}") from e

    def execute_query(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        执行查询语句

        Args:
            sql: SQL查询语句
            params: 查询参数

        Returns:
            List[sqlite3.Row]: 查询结果
        """
        try:
            if not self._connection:
                self._connect()

            cursor = self._connection.execute(sql, params)
            return cursor.fetchall()

        except Exception as e:
            self._logger.error(f"查询执行失败: {e}, SQL: {sql}")
            raise DatabaseError(f"查询执行失败: {e}", sql) from e

    def execute_insert(self, sql: str, params: tuple = ()) -> int:
        """
        执行插入语句

        Args:
            sql: SQL插入语句
            params: 插入参数

        Returns:
            int: 插入记录的ID
        """
        try:
            if not self._connection:
                self._connect()

            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            return cursor.lastrowid

        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"插入执行失败: {e}, SQL: {sql}")
            raise DatabaseError(f"插入执行失败: {e}", sql) from e

    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """
        执行更新语句

        Args:
            sql: SQL更新语句
            params: 更新参数

        Returns:
            int: 受影响的行数
        """
        try:
            if not self._connection:
                self._connect()

            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            return cursor.rowcount

        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"更新执行失败: {e}, SQL: {sql}")
            raise DatabaseError(f"更新执行失败: {e}", sql) from e

    def execute_delete(self, sql: str, params: tuple = ()) -> int:
        """
        执行删除语句

        Args:
            sql: SQL删除语句
            params: 删除参数

        Returns:
            int: 删除的行数
        """
        try:
            if not self._connection:
                self._connect()

            cursor = self._connection.execute(sql, params)
            self._connection.commit()
            return cursor.rowcount

        except Exception as e:
            self._connection.rollback()
            self._logger.error(f"删除执行失败: {e}, SQL: {sql}")
            raise DatabaseError(f"删除执行失败: {e}", sql) from e

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            List[Dict[str, Any]]: 表结构信息
        """
        try:
            sql = f"PRAGMA table_info({table_name})"
            rows = self.execute_query(sql)

            return [dict(row) for row in rows]

        except Exception as e:
            self._logger.error(f"获取表信息失败: {e}")
            raise DatabaseError(f"获取表信息失败: {e}") from e

    def backup_database(self, backup_path: Path) -> bool:
        """
        备份数据库

        Args:
            backup_path: 备份文件路径

        Returns:
            bool: 是否备份成功
        """
        try:
            if not self._connection:
                self._connect()

            # 确保备份目录存在
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # 创建备份连接
            backup_conn = sqlite3.connect(str(backup_path))

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
            self._logger.error(f"关闭数据库连接失败: {e}")

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
