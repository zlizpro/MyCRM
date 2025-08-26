"""
MiniCRM 性能监控集成测试

测试任务21.1.1：集成性能监控hooks到关键操作的实现。
验证性能监控系统是否正确集成到数据库、服务和UI操作中。
"""

import logging

# 设置测试环境
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.minicrm.core.performance_bootstrap import performance_bootstrap
from src.minicrm.core.performance_hooks import performance_hooks
from src.minicrm.core.performance_integration import performance_integration
from src.minicrm.core.performance_monitor import performance_monitor
from src.minicrm.data.dao.customer_dao import CustomerDAO
from src.minicrm.data.database.database_manager import DatabaseManager
from src.minicrm.services.customer_service import CustomerService


class TestPerformanceIntegration(unittest.TestCase):
    """性能监控集成测试类"""

    def setUp(self):
        """测试准备"""
        # 清理性能监控数据
        performance_monitor.clear_metrics()

        # 启用性能监控
        performance_hooks.enable()
        performance_integration.initialize()

        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = Path(self.temp_db.name)

        # 创建测试组件
        self.database_manager = DatabaseManager(self.db_path)
        self.customer_dao = CustomerDAO(self.database_manager)
        self.customer_service = CustomerService(self.customer_dao)

        # 创建模拟UI组件
        self.mock_ui_component = Mock()

        # 创建具有正确属性的Mock方法
        load_data_mock = Mock()
        load_data_mock.__name__ = "load_data"
        load_data_mock.__module__ = "test_module"
        self.mock_ui_component.load_data = load_data_mock

        refresh_data_mock = Mock()
        refresh_data_mock.__name__ = "refresh_data"
        refresh_data_mock.__module__ = "test_module"
        self.mock_ui_component.refresh_data = refresh_data_mock

    def tearDown(self):
        """测试清理"""
        try:
            self.database_manager.close()
            if self.db_path.exists():
                self.db_path.unlink()
        except Exception:
            pass

    def test_database_performance_integration(self):
        """测试数据库性能监控集成"""
        # 集成数据库性能监控
        performance_integration.integrate_database_manager(self.database_manager)

        # 执行数据库操作
        self.database_manager.initialize_database()

        # 验证性能监控数据
        metrics = performance_monitor.get_metrics()
        self.assertGreater(len(metrics), 0, "应该有性能监控数据")

        # 验证数据库操作被监控
        db_operations = [m for m in metrics if m.operation.startswith("db.")]
        self.assertGreater(len(db_operations), 0, "应该有数据库操作被监控")

        print(f"✓ 数据库性能监控集成测试通过，监控到 {len(db_operations)} 个数据库操作")

    def test_service_performance_integration(self):
        """测试服务性能监控集成"""
        # 集成服务性能监控
        performance_integration.integrate_service(
            self.customer_service, "customer_service"
        )

        # 执行服务操作
        try:
            test_customer_data = {
                "name": "测试客户",
                "phone": "13812345678",
                "customer_type": "生态板客户",
            }

            # 这个操作会被性能监控捕获
            customer_id = self.customer_service.create_customer(test_customer_data)
            self.assertIsNotNone(customer_id, "客户创建应该成功")

        except Exception as e:
            # 即使业务逻辑失败，性能监控也应该工作
            print(f"服务操作失败（预期）: {e}")

        # 验证性能监控数据
        metrics = performance_monitor.get_metrics()
        service_operations = [m for m in metrics if m.operation.startswith("service.")]
        self.assertGreater(len(service_operations), 0, "应该有服务操作被监控")

        print(
            f"✓ 服务性能监控集成测试通过，监控到 {len(service_operations)} 个服务操作"
        )

    def test_ui_performance_integration(self):
        """测试UI性能监控集成"""
        # 集成UI性能监控
        performance_integration.integrate_ui_component(
            self.mock_ui_component, "test_ui"
        )

        # 执行UI操作
        self.mock_ui_component.load_data()
        self.mock_ui_component.refresh_data()

        # 验证性能监控数据
        metrics = performance_monitor.get_metrics()
        ui_operations = [m for m in metrics if m.operation.startswith("ui.")]
        self.assertGreater(len(ui_operations), 0, "应该有UI操作被监控")

        print(f"✓ UI性能监控集成测试通过，监控到 {len(ui_operations)} 个UI操作")

    def test_bootstrap_integration(self):
        """测试启动集成功能"""
        # 准备应用程序组件
        app_components = {
            "database_manager": self.database_manager,
            "services": {
                "customer_service": self.customer_service,
            },
            "ui_components": {
                "test_ui": self.mock_ui_component,
            },
        }

        # 执行启动集成
        performance_bootstrap.load_config()
        performance_bootstrap.bootstrap_application(app_components)

        # 验证集成状态
        status = performance_bootstrap.get_bootstrap_status()
        self.assertTrue(status["bootstrap_completed"], "启动集成应该完成")
        self.assertTrue(status["performance_enabled"], "性能监控应该启用")

        # 验证组件集成
        integration_status = status["integration_status"]
        self.assertGreater(
            integration_status["integrated_services_count"], 0, "应该有服务被集成"
        )
        self.assertGreater(
            integration_status["integrated_daos_count"], 0, "应该有数据库组件被集成"
        )
        self.assertGreater(
            integration_status["integrated_ui_components_count"],
            0,
            "应该有UI组件被集成",
        )

        print("✓ 启动集成测试通过")

    def test_performance_report_generation(self):
        """测试性能报告生成"""
        # 集成所有组件
        app_components = {
            "database_manager": self.database_manager,
            "services": {"customer_service": self.customer_service},
            "ui_components": {"test_ui": self.mock_ui_component},
        }

        performance_bootstrap.bootstrap_application(app_components)

        # 执行一些操作
        self.database_manager.initialize_database()
        self.mock_ui_component.load_data()

        # 生成性能报告
        report = performance_integration.get_performance_report()

        # 验证报告结构
        self.assertIn("integration_status", report, "报告应该包含集成状态")
        self.assertIn("performance_data", report, "报告应该包含性能数据")
        self.assertIn("recommendations", report, "报告应该包含优化建议")

        # 验证性能数据
        perf_data = report["performance_data"]
        self.assertIn("summary", perf_data, "性能数据应该包含摘要")
        self.assertIn("database", perf_data, "性能数据应该包含数据库统计")
        self.assertIn("services", perf_data, "性能数据应该包含服务统计")
        self.assertIn("ui", perf_data, "性能数据应该包含UI统计")

        print("✓ 性能报告生成测试通过")

    def test_performance_data_export(self):
        """测试性能数据导出"""
        # 执行一些操作生成性能数据
        performance_integration.integrate_database_manager(self.database_manager)
        self.database_manager.initialize_database()

        # 导出性能数据
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            export_path = temp_file.name

        try:
            success = performance_integration.export_performance_data(export_path)
            self.assertTrue(success, "性能数据导出应该成功")

            # 验证导出文件存在
            export_file = Path(export_path)
            self.assertTrue(export_file.exists(), "导出文件应该存在")

            # 验证导出文件内容
            import json

            with open(export_file, encoding="utf-8") as f:
                exported_data = json.load(f)

            self.assertIn("export_time", exported_data, "导出数据应该包含导出时间")
            self.assertIn("summary", exported_data, "导出数据应该包含摘要")
            self.assertIn("metrics", exported_data, "导出数据应该包含指标")

            print("✓ 性能数据导出测试通过")

        finally:
            # 清理导出文件
            if Path(export_path).exists():
                Path(export_path).unlink()

    def test_performance_hooks_decorators(self):
        """测试性能监控装饰器"""
        from src.minicrm.core.performance_hooks import (
            monitor_db_query,
            monitor_service_method,
            monitor_ui_operation,
        )

        # 测试数据库查询装饰器
        @monitor_db_query("test_query")
        def test_db_operation():
            import time

            time.sleep(0.01)  # 模拟数据库操作
            return "db_result"

        # 测试服务方法装饰器
        @monitor_service_method("test_service")
        def test_service_operation():
            import time

            time.sleep(0.01)  # 模拟服务操作
            return "service_result"

        # 测试UI操作装饰器
        @monitor_ui_operation("test_ui_op")
        def test_ui_operation():
            import time

            time.sleep(0.01)  # 模拟UI操作
            return "ui_result"

        # 执行被装饰的函数
        db_result = test_db_operation()
        service_result = test_service_operation()
        ui_result = test_ui_operation()

        # 验证函数正常执行
        self.assertEqual(db_result, "db_result")
        self.assertEqual(service_result, "service_result")
        self.assertEqual(ui_result, "ui_result")

        # 验证性能监控数据
        metrics = performance_monitor.get_metrics()

        # 验证各类型操作都被监控
        db_metrics = [m for m in metrics if m.operation.startswith("db.test_query")]
        service_metrics = [
            m for m in metrics if m.operation.startswith("service.test_service")
        ]
        ui_metrics = [m for m in metrics if m.operation.startswith("ui.test_ui_op")]

        self.assertGreater(len(db_metrics), 0, "数据库操作应该被监控")
        self.assertGreater(len(service_metrics), 0, "服务操作应该被监控")
        self.assertGreater(len(ui_metrics), 0, "UI操作应该被监控")

        print("✓ 性能监控装饰器测试通过")

    def test_integration_status_reporting(self):
        """测试集成状态报告"""
        # 执行集成
        app_components = {
            "database_manager": self.database_manager,
            "services": {"customer_service": self.customer_service},
            "ui_components": {"test_ui": self.mock_ui_component},
        }

        performance_bootstrap.bootstrap_application(app_components)

        # 获取集成状态
        status = performance_integration.get_integration_status()

        # 验证状态信息
        self.assertTrue(status["initialized"], "集成应该已初始化")
        self.assertTrue(status["monitoring_enabled"], "监控应该已启用")
        self.assertGreater(status["integrated_services_count"], 0, "应该有服务被集成")
        self.assertGreater(status["integrated_daos_count"], 0, "应该有DAO被集成")
        self.assertGreater(
            status["integrated_ui_components_count"], 0, "应该有UI组件被集成"
        )

        # 验证组件列表
        self.assertIn("customer_service", status["integrated_services"])
        self.assertIn("database_manager", status["integrated_daos"])
        self.assertIn("test_ui", status["integrated_ui_components"])

        print("✓ 集成状态报告测试通过")


def run_performance_integration_tests():
    """运行性能监控集成测试"""
    # 设置日志
    logging.basicConfig(level=logging.INFO)

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceIntegration)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("MiniCRM 性能监控集成测试结果摘要")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    # 验证任务21.1.1完成状态
    if result.wasSuccessful():
        print("\n🎉 任务21.1.1：集成性能监控hooks到关键操作 - 完成！")
        print("✅ 所有性能监控集成测试通过")
        print("✅ 数据库操作性能监控已集成")
        print("✅ 服务层操作性能监控已集成")
        print("✅ UI操作性能监控已集成")
        print("✅ 自动化集成和报告功能正常")
    else:
        print("\n❌ 任务21.1.1：集成性能监控hooks到关键操作 - 未完成")
        print("需要修复失败的测试")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_integration_tests()
    exit(0 if success else 1)
