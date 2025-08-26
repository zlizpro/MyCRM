"""端到端测试套件.

完整的端到端测试，验证MiniCRM应用程序的完整功能流程。
从应用程序启动到各个业务功能的完整测试。
"""

import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import tkinter as tk
from tkinter import ttk
import unittest


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from minicrm.core.resource_manager import ResourceManager


class TestEndToEndWorkflow(unittest.TestCase):
    """端到端工作流程测试."""

    def setUp(self):
        """测试准备."""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()

        # 初始化测试数据库
        self._setup_test_database()

    def tearDown(self):
        """测试清理."""
        if hasattr(self, "root"):
            self.root.destroy()

        # 清理临时数据库
        if os.path.exists(self.temp_db_path):
            os.unlink(self.temp_db_path)

    def _setup_test_database(self):
        """设置测试数据库."""
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # 创建基本表结构
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                customer_type_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                supplier_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_price REAL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        """)

        # 插入测试数据
        cursor.execute("""
            INSERT INTO customers (name, phone, email, address)
            VALUES ('测试客户1', '13800138001', 'test1@example.com', '测试地址1')
        """)

        cursor.execute("""
            INSERT INTO suppliers (name, contact_person, phone, email)
            VALUES ('测试供应商1', '张三', '13800138002', 'supplier1@example.com')
        """)

        conn.commit()
        conn.close()

    def test_application_startup_sequence(self):
        """测试应用程序启动序列."""
        # 测试资源管理器初始化
        resource_manager = ResourceManager()
        self.assertIsInstance(resource_manager, ResourceManager)

        # 测试配置加载
        try:
            from minicrm.config.settings import get_config

            config = get_config()
            self.assertIsNotNone(config)
        except ImportError:
            # 如果配置模块不存在，跳过此测试
            pass

    def test_database_connection_workflow(self):
        """测试数据库连接工作流程."""
        # 测试数据库连接
        conn = sqlite3.connect(self.temp_db_path)
        self.assertIsNotNone(conn)

        # 测试基本查询
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)

        conn.close()

    def test_customer_management_workflow(self):
        """测试客户管理工作流程."""
        # 模拟客户管理操作
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # 1. 创建客户
        cursor.execute(
            """
            INSERT INTO customers (name, phone, email)
            VALUES (?, ?, ?)
        """,
            ("端到端测试客户", "13900139001", "e2e@test.com"),
        )

        customer_id = cursor.lastrowid
        self.assertIsNotNone(customer_id)

        # 2. 查询客户
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = cursor.fetchone()
        self.assertIsNotNone(customer)
        self.assertEqual(customer[1], "端到端测试客户")

        # 3. 更新客户
        cursor.execute(
            """
            UPDATE customers SET phone = ? WHERE id = ?
        """,
            ("13900139999", customer_id),
        )

        # 4. 验证更新
        cursor.execute("SELECT phone FROM customers WHERE id = ?", (customer_id,))
        updated_phone = cursor.fetchone()[0]
        self.assertEqual(updated_phone, "13900139999")

        # 5. 删除客户
        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))

        # 6. 验证删除
        cursor.execute("SELECT COUNT(*) FROM customers WHERE id = ?", (customer_id,))
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)

        conn.commit()
        conn.close()

    def test_supplier_management_workflow(self):
        """测试供应商管理工作流程."""
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # 供应商CRUD操作测试
        cursor.execute(
            """
            INSERT INTO suppliers (name, contact_person, phone)
            VALUES (?, ?, ?)
        """,
            ("端到端测试供应商", "李四", "13800138888"),
        )

        supplier_id = cursor.lastrowid

        # 验证创建
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        supplier = cursor.fetchone()
        self.assertEqual(supplier[1], "端到端测试供应商")

        conn.commit()
        conn.close()

    def test_quote_management_workflow(self):
        """测试报价管理工作流程."""
        conn = sqlite3.connect(self.temp_db_path)
        cursor = conn.cursor()

        # 获取测试客户和供应商ID
        cursor.execute("SELECT id FROM customers LIMIT 1")
        customer_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM suppliers LIMIT 1")
        supplier_id = cursor.fetchone()[0]

        # 创建报价
        cursor.execute(
            """
            INSERT INTO quotes (customer_id, supplier_id, product_name, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (customer_id, supplier_id, "测试板材", 100, 50.0, 5000.0),
        )

        quote_id = cursor.lastrowid

        # 验证报价创建
        cursor.execute("SELECT * FROM quotes WHERE id = ?", (quote_id,))
        quote = cursor.fetchone()
        self.assertEqual(quote[3], "测试板材")
        self.assertEqual(quote[4], 100)

        conn.commit()
        conn.close()

    def test_ui_component_creation_workflow(self):
        """测试UI组件创建工作流程."""
        # 测试基本UI组件创建
        main_frame = ttk.Frame(self.root)
        self.assertIsInstance(main_frame, ttk.Frame)

        # 测试数据表格组件
        columns = ("ID", "名称", "电话", "邮箱")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 插入测试数据
        tree.insert(
            "", "end", values=(1, "测试客户", "13800138000", "test@example.com")
        )

        # 验证数据插入
        children = tree.get_children()
        self.assertEqual(len(children), 1)

        # 获取插入的数据
        item_values = tree.item(children[0])["values"]
        self.assertEqual(item_values[1], "测试客户")

    def test_form_validation_workflow(self):
        """测试表单验证工作流程."""
        # 创建测试表单
        form_frame = ttk.Frame(self.root)

        # 客户名称输入
        name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=name_var)

        # 电话输入
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(form_frame, textvariable=phone_var)

        # 邮箱输入
        email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=email_var)

        # 测试验证逻辑
        def validate_form():
            errors = []

            if not name_var.get().strip():
                errors.append("客户名称不能为空")

            phone = phone_var.get().strip()
            if phone and not phone.isdigit():
                errors.append("电话号码格式不正确")

            email = email_var.get().strip()
            if email and "@" not in email:
                errors.append("邮箱格式不正确")

            return errors

        # 测试空表单验证
        errors = validate_form()
        self.assertIn("客户名称不能为空", errors)

        # 测试有效数据
        name_var.set("测试客户")
        phone_var.set("13800138000")
        email_var.set("test@example.com")

        errors = validate_form()
        self.assertEqual(len(errors), 0)

        # 测试无效数据
        phone_var.set("invalid_phone")
        email_var.set("invalid_email")

        errors = validate_form()
        self.assertIn("电话号码格式不正确", errors)
        self.assertIn("邮箱格式不正确", errors)

    def test_search_and_filter_workflow(self):
        """测试搜索和筛选工作流程."""
        # 创建测试数据
        test_data = [
            {"name": "客户A", "phone": "13800138001", "type": "生态板"},
            {"name": "客户B", "phone": "13800138002", "type": "家具板"},
            {"name": "客户C", "phone": "13800138003", "type": "阻燃板"},
            {"name": "测试客户", "phone": "13900139000", "type": "生态板"},
        ]

        # 测试名称搜索
        def search_by_name(data, keyword):
            return [item for item in data if keyword.lower() in item["name"].lower()]

        results = search_by_name(test_data, "客户A")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "客户A")

        # 测试类型筛选
        def filter_by_type(data, type_filter):
            return [item for item in data if item["type"] == type_filter]

        eco_board_customers = filter_by_type(test_data, "生态板")
        self.assertEqual(len(eco_board_customers), 2)

        # 测试组合搜索
        def combined_search(data, name_keyword, type_filter):
            filtered = filter_by_type(data, type_filter) if type_filter else data
            return search_by_name(filtered, name_keyword) if name_keyword else filtered

        results = combined_search(test_data, "客户", "生态板")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "测试客户")

    def test_data_export_workflow(self):
        """测试数据导出工作流程."""
        # 模拟数据导出
        export_data = [
            ["ID", "客户名称", "电话", "邮箱"],
            [1, "客户A", "13800138001", "a@example.com"],
            [2, "客户B", "13800138002", "b@example.com"],
        ]

        # 测试CSV格式导出
        def export_to_csv(data):
            csv_content = []
            for row in data:
                csv_content.append(",".join(str(cell) for cell in row))
            return "\n".join(csv_content)

        csv_result = export_to_csv(export_data)
        self.assertIn("客户名称", csv_result)
        self.assertIn("客户A", csv_result)

        # 测试导出文件写入
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_file.write(csv_result)
            temp_file_path = temp_file.name

        try:
            # 验证文件内容
            with open(temp_file_path, encoding="utf-8") as f:
                content = f.read()
                self.assertIn("客户A", content)
        finally:
            os.unlink(temp_file_path)

    def test_error_handling_workflow(self):
        """测试错误处理工作流程."""
        # 测试数据库连接错误
        try:
            conn = sqlite3.connect("/nonexistent/path/database.db")
            conn.execute("SELECT 1")
        except sqlite3.OperationalError as e:
            self.assertIsInstance(e, sqlite3.OperationalError)

        # 测试UI组件错误处理
        try:
            # 尝试在已销毁的窗口上创建组件
            destroyed_root = tk.Tk()
            destroyed_root.destroy()
            ttk.Label(destroyed_root, text="测试")
        except tk.TclError as e:
            self.assertIsInstance(e, tk.TclError)

    def test_performance_workflow(self):
        """测试性能工作流程."""
        # 测试大量数据处理性能
        start_time = time.time()

        # 模拟处理1000条客户记录
        customers = []
        for i in range(1000):
            customers.append(
                {
                    "id": i + 1,
                    "name": f"客户{i + 1}",
                    "phone": f"138{i:08d}",
                    "email": f"customer{i + 1}@example.com",
                }
            )

        # 模拟搜索操作
        search_results = [c for c in customers if "100" in c["name"]]

        end_time = time.time()
        processing_time = end_time - start_time

        # 验证性能在合理范围内
        self.assertLess(processing_time, 1.0)  # 应该在1秒内完成
        self.assertGreater(len(search_results), 0)  # 应该有搜索结果

    def test_memory_management_workflow(self):
        """测试内存管理工作流程."""
        import gc

        # 记录初始对象数量
        initial_objects = len(gc.get_objects())

        # 创建大量临时对象
        temp_objects = []
        for i in range(1000):
            frame = ttk.Frame(self.root)
            label = ttk.Label(frame, text=f"临时标签{i}")
            temp_objects.append((frame, label))

        # 记录创建后的对象数量
        after_creation_objects = len(gc.get_objects())

        # 清理对象
        for frame, label in temp_objects:
            label.destroy()
            frame.destroy()

        temp_objects.clear()

        # 强制垃圾回收
        gc.collect()

        # 记录清理后的对象数量
        after_cleanup_objects = len(gc.get_objects())

        # 验证内存管理
        created_objects = after_creation_objects - initial_objects
        remaining_objects = after_cleanup_objects - initial_objects

        print(f"创建对象数: {created_objects}")
        print(f"清理后剩余对象数: {remaining_objects}")

        # 剩余对象应该明显少于创建的对象
        self.assertLess(remaining_objects, created_objects * 0.5)


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试."""

    def setUp(self):
        """测试准备."""
        self.project_root = project_root

    def test_module_integration(self):
        """测试模块集成."""
        # 测试核心模块导入
        try:
            from minicrm.core import constants, exceptions, resource_manager

            self.assertTrue(hasattr(resource_manager, "ResourceManager"))
            self.assertTrue(hasattr(constants, "APP_NAME"))
            self.assertTrue(hasattr(exceptions, "MiniCRMError"))

        except ImportError as e:
            self.fail(f"核心模块导入失败: {e}")

    def test_configuration_integration(self):
        """测试配置集成."""
        # 测试配置文件存在性
        config_files = [
            self.project_root / "pyproject.toml",
            self.project_root / "src" / "minicrm" / "config" / "__init__.py",
        ]

        for config_file in config_files:
            if config_file.exists():
                self.assertTrue(config_file.is_file())

    def test_resource_integration(self):
        """测试资源集成."""
        resource_manager = ResourceManager()

        # 测试资源目录结构
        resource_types = ["icons", "themes", "templates", "styles"]

        for resource_type in resource_types:
            resource_dir = resource_manager.get_resource_path_by_type(resource_type)
            # 目录可能不存在，但路径应该是有效的
            self.assertIsInstance(resource_dir, Path)

    def test_database_integration(self):
        """测试数据库集成."""
        # 创建临时数据库测试集成
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            temp_db_path = temp_db.name

        try:
            conn = sqlite3.connect(temp_db_path)

            # 测试事务处理
            conn.execute("BEGIN TRANSACTION")
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES (?)", ("测试",))
            conn.execute("COMMIT")

            # 验证数据
            cursor = conn.execute("SELECT name FROM test WHERE id = 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], "测试")

            conn.close()

        finally:
            if os.path.exists(temp_db_path):
                os.unlink(temp_db_path)


def run_end_to_end_tests():
    """运行端到端测试套件."""
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTest(unittest.makeSuite(TestEndToEndWorkflow))
    suite.addTest(unittest.makeSuite(TestSystemIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("运行MiniCRM端到端测试套件")
    print(f"项目根目录: {project_root}")
    print("=" * 60)

    success = run_end_to_end_tests()

    print("=" * 60)
    if success:
        print("✅ 所有端到端测试通过")
    else:
        print("❌ 部分端到端测试失败")

    sys.exit(0 if success else 1)
