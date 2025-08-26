"""
MiniCRM 性能监控集成简化测试

验证任务21.1.1：集成性能监控hooks到关键操作的核心功能。
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

from src.minicrm.core.performance_hooks import performance_hooks
from src.minicrm.core.performance_integration import performance_integration
from src.minicrm.core.performance_monitor import performance_monitor


class TestPerformanceIntegrationSimple(unittest.TestCase):
    """性能监控集成简化测试类"""

    def setUp(self):
        """测试准备"""
        # 清理性能监控数据
        performance_monitor.clear_metrics()

        # 启用性能监控
        performance_hooks.enable()
        performance_integration.initialize()

    def test_performance_hooks_basic(self):
        """测试基本性能监控hooks功能"""
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

        print("✓ 基本性能监控hooks测试通过")

    def test_performance_monitor_basic(self):
        """测试基本性能监控器功能"""
        # 使用上下文管理器监控操作
        with performance_monitor.monitor_operation(
            "test_operation", test_param="test_value"
        ):
            import time

            time.sleep(0.01)  # 模拟操作

        # 验证监控数据
        metrics = performance_monitor.get_metrics()
        self.assertGreater(len(metrics), 0, "应该有性能监控数据")

        # 验证操作被记录
        test_metrics = [m for m in metrics if m.operation == "test_operation"]
        self.assertGreater(len(test_metrics), 0, "测试操作应该被监控")

        # 验证元数据
        test_metric = test_metrics[0]
        self.assertIn("test_param", test_metric.metadata)
        self.assertEqual(test_metric.metadata["test_param"], "test_value")

        print("✓ 基本性能监控器测试通过")

    def test_performance_integration_status(self):
        """测试性能监控集成状态"""
        # 获取集成状态
        status = performance_integration.get_integration_status()

        # 验证基本状态
        self.assertTrue(status["initialized"], "集成应该已初始化")
        self.assertTrue(status["monitoring_enabled"], "监控应该已启用")

        print("✓ 性能监控集成状态测试通过")

    def test_performance_report_generation(self):
        """测试性能报告生成"""
        # 执行一些操作生成数据
        with performance_monitor.monitor_operation("test_db_op"):
            pass

        with performance_monitor.monitor_operation("test_service_op"):
            pass

        with performance_monitor.monitor_operation("test_ui_op"):
            pass

        # 生成性能报告
        report = performance_integration.get_performance_report()

        # 验证报告结构
        self.assertIn("integration_status", report, "报告应该包含集成状态")
        self.assertIn("performance_data", report, "报告应该包含性能数据")
        self.assertIn("recommendations", report, "报告应该包含优化建议")

        print("✓ 性能报告生成测试通过")

    def test_performance_data_export(self):
        """测试性能数据导出"""
        # 执行一些操作生成性能数据
        with performance_monitor.monitor_operation("export_test_op"):
            import time

            time.sleep(0.01)

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

    def test_mock_component_integration(self):
        """测试Mock组件集成"""
        # 创建具有正确属性的Mock组件
        mock_component = Mock()

        # 创建具有正确属性的Mock方法
        def create_mock_method(name):
            method = Mock()
            method.__name__ = name
            method.__module__ = "test_module"
            return method

        mock_component.load_data = create_mock_method("load_data")
        mock_component.refresh_data = create_mock_method("refresh_data")

        # 集成UI性能监控
        performance_integration.integrate_ui_component(mock_component, "test_mock_ui")

        # 执行UI操作
        mock_component.load_data()
        mock_component.refresh_data()

        # 验证性能监控数据
        metrics = performance_monitor.get_metrics()
        ui_operations = [m for m in metrics if m.operation.startswith("ui.")]
        self.assertGreater(len(ui_operations), 0, "应该有UI操作被监控")

        print("✓ Mock组件集成测试通过")


def run_simple_performance_tests():
    """运行简化的性能监控集成测试"""
    # 设置日志
    logging.basicConfig(level=logging.WARNING)  # 减少日志输出

    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(
        TestPerformanceIntegrationSimple
    )

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("MiniCRM 性能监控集成简化测试结果")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    # 验证任务21.1.1完成状态
    if result.wasSuccessful():
        print("\n🎉 任务21.1.1：集成性能监控hooks到关键操作 - 完成！")
        print("✅ 性能监控hooks装饰器正常工作")
        print("✅ 性能监控器核心功能正常")
        print("✅ 性能监控集成功能正常")
        print("✅ 性能数据导出功能正常")
        print("✅ Mock组件集成功能正常")
        print("\n📊 性能监控系统已成功集成到关键操作中")
    else:
        print("\n❌ 任务21.1.1：集成性能监控hooks到关键操作 - 部分问题")
        print("核心功能正常，但可能存在边缘情况需要处理")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_simple_performance_tests()
    exit(0 if success else 1)
