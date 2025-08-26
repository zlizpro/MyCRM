"""
日志系统测试模块

测试MiniCRM日志系统的各种功能。
"""

import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.minicrm.core.exceptions import ConfigurationError
from src.minicrm.core.logging import (
    AuditLogger,
    JSONFormatter,
    LogManager,
    PerformanceLogger,
    get_audit_logger,
    get_logger,
    get_performance_logger,
    initialize_logging,
    shutdown_logging,
)


class TestJSONFormatter(unittest.TestCase):
    """测试JSON格式化器"""

    def setUp(self):
        """测试准备"""
        self.formatter = JSONFormatter()

    def test_format_basic_record(self):
        """测试基本日志记录格式化"""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"

        result = self.formatter.format(record)

        # 解析JSON结果
        log_data = json.loads(result)

        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["logger"], "test_logger")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["module"], "test")
        self.assertEqual(log_data["function"], "test_function")
        self.assertEqual(log_data["line"], 10)
        self.assertIn("timestamp", log_data)

    def test_format_record_with_extra_fields(self):
        """测试带额外字段的日志记录格式化"""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"
        record.extra_fields = {"user_id": 123, "operation": "test_op"}

        result = self.formatter.format(record)
        log_data = json.loads(result)

        self.assertEqual(log_data["user_id"], 123)
        self.assertEqual(log_data["operation"], "test_op")

    def test_format_record_with_performance_info(self):
        """测试带性能信息的日志记录格式化"""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.module = "test"
        record.funcName = "test_function"
        record.duration = 1.234
        record.operation = "test_operation"

        result = self.formatter.format(record)
        log_data = json.loads(result)

        self.assertEqual(log_data["duration"], 1.234)
        self.assertEqual(log_data["operation"], "test_operation")


class TestPerformanceLogger(unittest.TestCase):
    """测试性能日志记录器"""

    def setUp(self):
        """测试准备"""
        self.perf_logger = PerformanceLogger("test.performance")

    @patch("time.time")
    def test_start_and_end_operation(self, mock_time):
        """测试开始和结束操作记录"""
        # 模拟时间
        mock_time.side_effect = [1000.0, 1001.5]  # 开始时间和结束时间

        operation_id = "test_op_1"
        operation_name = "Test Operation"

        # 开始操作
        self.perf_logger.start_operation(operation_id, operation_name, user_id=123)

        # 结束操作
        duration = self.perf_logger.end_operation(
            operation_id, operation_name, True, result="success"
        )

        # 验证返回的耗时
        self.assertEqual(duration, 1.5)

    def test_log_slow_operation(self):
        """测试慢操作日志记录"""
        with self.assertLogs("test.performance", level="WARNING") as log:
            self.perf_logger.log_slow_operation("Slow Operation", 2.5, 1.0, user_id=456)

        # 验证日志记录
        self.assertIn("慢操作检测", log.output[0])
        self.assertIn("Slow Operation", log.output[0])
        self.assertIn("2.500秒", log.output[0])


class TestAuditLogger(unittest.TestCase):
    """测试审计日志记录器"""

    def setUp(self):
        """测试准备"""
        self.audit_logger = AuditLogger("test.audit")

    def test_log_user_action(self):
        """测试用户操作日志记录"""
        with self.assertLogs("test.audit", level="INFO") as log:
            self.audit_logger.log_user_action(
                action="CREATE",
                resource_type="CUSTOMER",
                resource_id="123",
                user_id="user456",
            )

        # 验证日志记录
        self.assertIn("用户操作: CREATE CUSTOMER", log.output[0])

    def test_log_system_event(self):
        """测试系统事件日志记录"""
        with self.assertLogs("test.audit", level="INFO") as log:
            self.audit_logger.log_system_event(
                event_type="STARTUP", event_name="Application Started", version="1.0.0"
            )

        # 验证日志记录
        self.assertIn("系统事件: STARTUP - Application Started", log.output[0])

    def test_log_security_event(self):
        """测试安全事件日志记录"""
        with self.assertLogs("test.audit", level="WARNING") as log:
            self.audit_logger.log_security_event(
                event_type="LOGIN_FAILURE",
                description="Invalid credentials",
                severity="WARNING",
                ip_address="192.168.1.1",
            )

        # 验证日志记录
        self.assertIn("安全事件: LOGIN_FAILURE - Invalid credentials", log.output[0])


class TestLogManager(unittest.TestCase):
    """测试日志管理器"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_manager = LogManager()

        # 测试配置
        self.test_config = {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "max_file_size": 1024 * 1024,  # 1MB
            "backup_count": 3,
            "encoding": "utf-8",
            "log_to_file": True,
            "log_to_console": False,  # 避免测试时输出到控制台
        }

    def tearDown(self):
        """测试清理"""
        # 关闭日志管理器
        self.log_manager.shutdown()

        # 清理临时目录
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("src.minicrm.core.logging.LOG_DIR")
    def test_initialize_success(self, mock_log_dir):
        """测试日志系统初始化成功"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        mock_log_dir.__truediv__ = lambda self, other: Path(self.temp_dir) / other

        # 初始化日志系统
        self.log_manager.initialize(self.test_config)

        # 验证初始化状态
        self.assertTrue(self.log_manager._is_initialized)
        self.assertIn("app", self.log_manager._loggers)

    def test_initialize_invalid_config(self):
        """测试无效配置初始化"""
        invalid_config = {
            "level": "INVALID_LEVEL"  # 无效的日志级别
        }

        with self.assertRaises(ConfigurationError):
            self.log_manager.initialize(invalid_config)

    @patch("src.minicrm.core.logging.LOG_DIR")
    def test_get_logger(self, mock_log_dir):
        """测试获取日志记录器"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        mock_log_dir.__truediv__ = lambda self, other: Path(self.temp_dir) / other

        self.log_manager.initialize(self.test_config)

        # 获取应用日志记录器
        app_logger = self.log_manager.get_logger("app")
        self.assertIsInstance(app_logger, logging.Logger)

        # 获取自定义日志记录器
        custom_logger = self.log_manager.get_logger("custom")
        self.assertIsInstance(custom_logger, logging.Logger)
        self.assertEqual(custom_logger.name, "minicrm.custom")

    @patch("src.minicrm.core.logging.LOG_DIR")
    def test_set_level(self, mock_log_dir):
        """测试设置日志级别"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        mock_log_dir.__truediv__ = lambda self, other: Path(self.temp_dir) / other

        self.log_manager.initialize(self.test_config)

        # 设置日志级别
        self.log_manager.set_level("app", "DEBUG")

        app_logger = self.log_manager.get_logger("app")
        self.assertEqual(app_logger.level, logging.DEBUG)

    @patch("src.minicrm.core.logging.LOG_DIR")
    def test_add_remove_handler(self, mock_log_dir):
        """测试添加和移除处理器"""
        mock_log_dir.__str__ = lambda: self.temp_dir
        mock_log_dir.__truediv__ = lambda self, other: Path(self.temp_dir) / other

        self.log_manager.initialize(self.test_config)

        # 创建测试处理器
        test_handler = logging.StreamHandler()

        # 添加处理器
        self.log_manager.add_handler("app", test_handler)

        app_logger = self.log_manager.get_logger("app")
        self.assertIn(test_handler, app_logger.handlers)

        # 移除处理器
        self.log_manager.remove_handler("app", test_handler)
        self.assertNotIn(test_handler, app_logger.handlers)

    def test_shutdown(self):
        """测试关闭日志系统"""
        # 初始化后关闭
        self.log_manager.initialize(self.test_config)
        self.assertTrue(self.log_manager._is_initialized)

        self.log_manager.shutdown()

        # 验证关闭状态
        self.assertFalse(self.log_manager._is_initialized)
        self.assertEqual(len(self.log_manager._handlers), 0)
        self.assertEqual(len(self.log_manager._loggers), 0)


class TestGlobalFunctions(unittest.TestCase):
    """测试全局日志函数"""

    def setUp(self):
        """测试准备"""
        # 重置全局日志管理器
        import src.minicrm.core.logging as logging_module

        logging_module.log_manager = LogManager()

    @patch("src.minicrm.core.logging.log_manager")
    def test_get_logger(self, mock_log_manager):
        """测试获取全局日志记录器"""
        mock_logger = MagicMock()
        mock_log_manager.get_logger.return_value = mock_logger

        result = get_logger("test")

        mock_log_manager.get_logger.assert_called_once_with("test")
        self.assertEqual(result, mock_logger)

    @patch("src.minicrm.core.logging.log_manager")
    def test_initialize_logging(self, mock_log_manager):
        """测试初始化全局日志系统"""
        test_config = {"level": "DEBUG"}

        initialize_logging(test_config)

        mock_log_manager.initialize.assert_called_once_with(test_config)

    @patch("src.minicrm.core.logging.log_manager")
    def test_shutdown_logging(self, mock_log_manager):
        """测试关闭全局日志系统"""
        shutdown_logging()

        mock_log_manager.shutdown.assert_called_once()

    @patch("src.minicrm.core.logging.log_manager")
    def test_get_performance_logger(self, mock_log_manager):
        """测试获取性能日志记录器"""
        mock_perf_logger = MagicMock()
        mock_log_manager.performance_logger = mock_perf_logger

        result = get_performance_logger()

        self.assertEqual(result, mock_perf_logger)

    @patch("src.minicrm.core.logging.log_manager")
    def test_get_audit_logger(self, mock_log_manager):
        """测试获取审计日志记录器"""
        mock_audit_logger = MagicMock()
        mock_log_manager.audit_logger = mock_audit_logger

        result = get_audit_logger()

        self.assertEqual(result, mock_audit_logger)


if __name__ == "__main__":
    unittest.main()
