"""增强版数据库管理器集成测试.

测试数据库连接池、事务管理、版本迁移、错误重试等功能.
"""

from datetime import datetime
from pathlib import Path
import shutil
import tempfile
import unittest

from minicrm.core.exceptions import DatabaseError
from minicrm.data.database_manager_enhanced import create_database_manager


class TestRollbackError(Exception):
    """测试回滚专用异常."""


class TestEnhancedDatabaseManager(unittest.TestCase):
    """增强版数据库管理器测试类."""

    def setUp(self):
        """测试准备."""
        # 创建临时数据库目录
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_minicrm.db"

        # 创建数据库管理器实例
        self.db_manager = create_database_manager(self.db_path, max_connections=3)

    def tearDown(self):
        """测试清理."""
        # 关闭数据库连接
        self.db_manager.close()

        # 删除临时目录
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_database_initialization(self):
        """测试数据库初始化."""
        # 初始化数据库
        self.db_manager.initialize_database()

        # 验证数据库文件已创建
        assert self.db_path.exists()

        # 验证连接状态
        assert self.db_manager.is_connected

    def test_connection_pool(self):
        """测试连接池功能."""
        self.db_manager.initialize_database()

        # 测试获取多个连接
        connections = []
        for _ in range(3):
            with self.db_manager.get_connection() as conn:
                connections.append(conn)
                # 验证连接可用
                result = conn.execute("SELECT 1").fetchone()
                assert result[0] == 1

    def test_transaction_management(self):
        """测试事务管理."""
        self.db_manager.initialize_database()

        # 测试成功事务
        with self.db_manager.transaction() as conn:
            conn.execute(
                """
                INSERT INTO database_versions (version, created_at, description)
                VALUES (?, ?, ?)
            """,
                ("test_1.0.0", datetime.now(timezone.utc).isoformat(), "测试版本"),
            )

        # 验证数据已提交
        results = self.db_manager.execute_query(
            "SELECT * FROM database_versions WHERE version = ?", ("test_1.0.0",)
        )
        assert len(results) == 1

        # 测试回滚事务
        def _test_rollback():
            """内部函数用于测试回滚."""
            error_msg = "测试回滚"
            raise TestRollbackError(error_msg)

        try:
            with self.db_manager.transaction() as conn:
                conn.execute(
                    """
                    INSERT INTO database_versions (version, created_at, description)
                    VALUES (?, ?, ?)
                """,
                    ("test_2.0.0", datetime.now(timezone.utc).isoformat(), "测试版本2"),
                )

                # 故意引发异常
                _test_rollback()
        except TestRollbackError:
            # 预期的异常,用于测试回滚
            pass

        # 验证数据已回滚
        results = self.db_manager.execute_query(
            "SELECT * FROM database_versions WHERE version = ?", ("test_2.0.0",)
        )
        assert len(results) == 0

    def test_crud_operations(self):
        """测试CRUD操作."""
        self.db_manager.initialize_database()

        # 测试插入
        now = datetime.now(timezone.utc).isoformat()
        customer_id = self.db_manager.execute_insert(
            """
            INSERT INTO customers (name, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                "测试客户",
                "13812345678",
                now,
                now,
            ),
            table_name="customers",
        )
        assert isinstance(customer_id, int)
        assert customer_id > 0

        # 测试查询
        results = self.db_manager.execute_query(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        )
        assert len(results) == 1
        assert results[0]["name"] == "测试客户"

        # 测试更新
        affected_rows = self.db_manager.execute_update(
            "UPDATE customers SET name = ?, updated_at = ? WHERE id = ?",
            ("更新后的客户", datetime.now(timezone.utc).isoformat(), customer_id),
            table_name="customers",
        )
        assert affected_rows == 1

        # 验证更新结果
        results = self.db_manager.execute_query(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        )
        assert results[0]["name"] == "更新后的客户"

        # 测试删除
        deleted_rows = self.db_manager.execute_delete(
            "DELETE FROM customers WHERE id = ?", (customer_id,), table_name="customers"
        )
        assert deleted_rows == 1

        # 验证删除结果
        results = self.db_manager.execute_query(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        )
        assert len(results) == 0

    def test_hooks_system(self):
        """测试Hooks系统."""
        self.db_manager.initialize_database()

        # 注册测试Hook
        hook_called = []

        def test_before_hook(**_kwargs):
            """测试前置Hook."""
            hook_called.append("before")
            return _kwargs

        def test_after_hook(**_kwargs):
            """测试后置Hook."""
            hook_called.append("after")

        self.db_manager.register_hook("insert", "before", test_before_hook)
        self.db_manager.register_hook("insert", "after", test_after_hook)

        # 执行插入操作
        now = datetime.now(timezone.utc).isoformat()
        self.db_manager.execute_insert(
            """
            INSERT INTO customers (name, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                "Hook测试客户",
                "13812345678",
                now,
                now,
            ),
            table_name="customers",
        )

        # 验证Hook被调用
        assert "before" in hook_called
        assert "after" in hook_called

    def test_database_backup(self):
        """测试数据库备份."""
        self.db_manager.initialize_database()

        # 插入测试数据
        now = datetime.now(timezone.utc).isoformat()
        self.db_manager.execute_insert(
            """
            INSERT INTO customers (name, phone, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                "备份测试客户",
                "13812345678",
                now,
                now,
            ),
        )

        # 执行备份
        backup_path = self.temp_dir / "backup.db"
        success = self.db_manager.backup_database(backup_path)

        assert success
        assert backup_path.exists()

        # 验证备份文件内容
        backup_manager = create_database_manager(backup_path)
        results = backup_manager.execute_query(
            "SELECT * FROM customers WHERE name = ?", ("备份测试客户",)
        )
        assert len(results) == 1
        backup_manager.close()

    def test_migration_system(self):
        """测试迁移系统."""
        self.db_manager.initialize_database()

        # 获取迁移管理器
        migration_manager = self.db_manager.get_migration_manager()

        # 测试获取当前版本
        current_version = migration_manager.get_current_version()
        assert current_version == "1.0.0"

        # 测试迁移到相同版本
        success = migration_manager.migrate_to_version("1.0.0")
        assert success

    def test_table_info(self):
        """测试获取表信息."""
        self.db_manager.initialize_database()

        # 获取customers表信息
        table_info = self.db_manager.get_table_info("customers")

        assert isinstance(table_info, list)
        assert len(table_info) > 0

        # 验证包含必要字段
        field_names = [field["name"] for field in table_info]
        assert "id" in field_names
        assert "name" in field_names
        assert "phone" in field_names

    def test_error_handling(self):
        """测试错误处理."""
        self.db_manager.initialize_database()

        # 测试SQL语法错误
        try:
            self.db_manager.execute_query("INVALID SQL STATEMENT")
            assert False, "应该抛出DatabaseError异常"
        except DatabaseError:
            pass  # 预期的异常

        # 测试外键约束错误
        try:
            now = datetime.now(timezone.utc).isoformat()
            self.db_manager.execute_insert(
                "INSERT INTO customers (customer_type_id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (
                    999,
                    "测试客户",
                    now,
                    now,
                ),
            )
            assert False, "应该抛出DatabaseError异常"
        except DatabaseError:
            pass  # 预期的异常


if __name__ == "__main__":
    unittest.main()
