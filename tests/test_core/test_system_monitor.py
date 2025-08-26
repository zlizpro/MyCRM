"""
系统监控器测试

测试系统监控器的各项功能，包括：
- 系统指标收集
- 应用程序性能监控
- 健康检查功能
- 性能报告生成
"""

from collections import deque
from datetime import datetime, timedelta
import time
import unittest
from unittest.mock import Mock, patch

from src.minicrm.core.system_monitor import (
    ApplicationMetrics,
    HealthCheckResult,
    SystemMetrics,
    SystemMonitor,
    generate_performance_report,
    get_system_monitor,
    run_health_check,
    start_system_monitoring,
    stop_system_monitoring,
)


class TestSystemMetrics(unittest.TestCase):
    """系统指标数据类测试"""

    def test_system_metrics_creation(self):
        """测试系统指标创建"""
        timestamp = datetime.now()
        metrics = SystemMetrics(
            timestamp=timestamp,
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_mb=1024.0,
            memory_available_mb=2048.0,
            disk_usage_percent=70.0,
            disk_free_gb=100.0,
            process_count=150,
            thread_count=20,
        )

        self.assertEqual(metrics.timestamp, timestamp)
        self.assertEqual(metrics.cpu_percent, 50.0)
        self.assertEqual(metrics.memory_percent, 60.0)
        self.assertEqual(metrics.memory_used_mb, 1024.0)
        self.assertEqual(metrics.memory_available_mb, 2048.0)
        self.assertEqual(metrics.disk_usage_percent, 70.0)
        self.assertEqual(metrics.disk_free_gb, 100.0)
        self.assertEqual(metrics.process_count, 150)
        self.assertEqual(metrics.thread_count, 20)

    def test_system_metrics_to_dict(self):
        """测试系统指标转换为字典"""
        timestamp = datetime.now()
        metrics = SystemMetrics(
            timestamp=timestamp,
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_mb=1024.0,
            memory_available_mb=2048.0,
            disk_usage_percent=70.0,
            disk_free_gb=100.0,
            process_count=150,
            thread_count=20,
        )

        result = metrics.to_dict()

        self.assertEqual(result["timestamp"], timestamp.isoformat())
        self.assertEqual(result["cpu_percent"], 50.0)
        self.assertEqual(result["memory_percent"], 60.0)
        self.assertEqual(result["memory_used_mb"], 1024.0)
        self.assertEqual(result["memory_available_mb"], 2048.0)
        self.assertEqual(result["disk_usage_percent"], 70.0)
        self.assertEqual(result["disk_free_gb"], 100.0)
        self.assertEqual(result["process_count"], 150)
        self.assertEqual(result["thread_count"], 20)


class TestApplicationMetrics(unittest.TestCase):
    """应用程序指标数据类测试"""

    def test_application_metrics_creation(self):
        """测试应用程序指标创建"""
        timestamp = datetime.now()
        metrics = ApplicationMetrics(
            timestamp=timestamp,
            app_memory_mb=256.0,
            app_cpu_percent=10.0,
            ui_response_time_ms=100.0,
            database_response_time_ms=50.0,
            active_windows=3,
            active_threads=10,
            error_count=2,
        )

        self.assertEqual(metrics.timestamp, timestamp)
        self.assertEqual(metrics.app_memory_mb, 256.0)
        self.assertEqual(metrics.app_cpu_percent, 10.0)
        self.assertEqual(metrics.ui_response_time_ms, 100.0)
        self.assertEqual(metrics.database_response_time_ms, 50.0)
        self.assertEqual(metrics.active_windows, 3)
        self.assertEqual(metrics.active_threads, 10)
        self.assertEqual(metrics.error_count, 2)

    def test_application_metrics_to_dict(self):
        """测试应用程序指标转换为字典"""
        timestamp = datetime.now()
        metrics = ApplicationMetrics(
            timestamp=timestamp,
            app_memory_mb=256.0,
            app_cpu_percent=10.0,
            ui_response_time_ms=100.0,
            database_response_time_ms=50.0,
            active_windows=3,
            active_threads=10,
            error_count=2,
        )

        result = metrics.to_dict()

        self.assertEqual(result["timestamp"], timestamp.isoformat())
        self.assertEqual(result["app_memory_mb"], 256.0)
        self.assertEqual(result["app_cpu_percent"], 10.0)
        self.assertEqual(result["ui_response_time_ms"], 100.0)
        self.assertEqual(result["database_response_time_ms"], 50.0)
        self.assertEqual(result["active_windows"], 3)
        self.assertEqual(result["active_threads"], 10)
        self.assertEqual(result["error_count"], 2)


class TestHealthCheckResult(unittest.TestCase):
    """健康检查结果数据类测试"""

    def test_health_check_result_creation(self):
        """测试健康检查结果创建"""
        timestamp = datetime.now()
        result = HealthCheckResult(
            check_name="test_check",
            status="healthy",
            message="测试检查通过",
            details={"key": "value"},
            timestamp=timestamp,
        )

        self.assertEqual(result.check_name, "test_check")
        self.assertEqual(result.status, "healthy")
        self.assertEqual(result.message, "测试检查通过")
        self.assertEqual(result.details, {"key": "value"})
        self.assertEqual(result.timestamp, timestamp)

    def test_health_check_result_to_dict(self):
        """测试健康检查结果转换为字典"""
        timestamp = datetime.now()
        result = HealthCheckResult(
            check_name="test_check",
            status="healthy",
            message="测试检查通过",
            details={"key": "value"},
            timestamp=timestamp,
        )

        dict_result = result.to_dict()

        self.assertEqual(dict_result["check_name"], "test_check")
        self.assertEqual(dict_result["status"], "healthy")
        self.assertEqual(dict_result["message"], "测试检查通过")
        self.assertEqual(dict_result["details"], {"key": "value"})
        self.assertEqual(dict_result["timestamp"], timestamp.isoformat())


class TestSystemMonitor(unittest.TestCase):
    """系统监控器测试类"""

    def setUp(self):
        """测试准备"""
        self.monitor = SystemMonitor(max_history_size=100)
        self.monitor._logger = Mock()

    def tearDown(self):
        """测试清理"""
        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()

    def test_initialization(self):
        """测试初始化"""
        monitor = SystemMonitor()

        self.assertIsNotNone(monitor._logger)
        self.assertFalse(monitor._monitoring_enabled)
        self.assertEqual(monitor._monitoring_interval, 5.0)
        self.assertIsInstance(monitor._system_metrics, deque)
        self.assertIsInstance(monitor._app_metrics, deque)
        self.assertIsInstance(monitor._health_checks, list)
        self.assertIsInstance(monitor._thresholds, dict)
        self.assertIsInstance(monitor._health_check_functions, dict)

    def test_set_app_reference(self):
        """测试设置应用程序引用"""
        mock_app = Mock()

        self.monitor.set_app_reference(mock_app)

        self.assertEqual(self.monitor._app_reference, mock_app)

    def test_set_monitoring_interval(self):
        """测试设置监控间隔"""
        self.monitor.set_monitoring_interval(10.0)
        self.assertEqual(self.monitor._monitoring_interval, 10.0)

        # 测试最小值限制
        self.monitor.set_monitoring_interval(0.5)
        self.assertEqual(self.monitor._monitoring_interval, 1.0)

    def test_set_threshold(self):
        """测试设置阈值"""
        self.monitor.set_threshold("cpu_warning", 80.0)
        self.assertEqual(self.monitor._thresholds["cpu_warning"], 80.0)

        # 测试不存在的阈值
        original_count = len(self.monitor._thresholds)
        self.monitor.set_threshold("nonexistent_threshold", 50.0)
        self.assertEqual(len(self.monitor._thresholds), original_count)

    @patch("src.minicrm.core.system_monitor.psutil")
    def test_start_monitoring_without_psutil(self, mock_psutil):
        """测试在没有psutil的情况下启动监控"""
        mock_psutil = None

        self.monitor.start_monitoring()

        self.assertFalse(self.monitor.is_monitoring())

    @patch("src.minicrm.core.system_monitor.psutil")
    def test_start_monitoring_with_psutil(self, mock_psutil):
        """测试在有psutil的情况下启动监控"""
        # 模拟psutil可用
        mock_psutil.cpu_percent.return_value = 50.0
        mock_psutil.virtual_memory.return_value = Mock(
            percent=60.0, used=1024 * 1024 * 1024, available=2048 * 1024 * 1024
        )
        mock_psutil.disk_usage.return_value = Mock(
            percent=70.0, free=100 * 1024 * 1024 * 1024
        )
        mock_psutil.pids.return_value = list(range(100))
        mock_psutil.Process.return_value.num_threads.return_value = 10

        self.monitor.start_monitoring()

        self.assertTrue(self.monitor.is_monitoring())

        # 等待一小段时间让监控线程运行
        time.sleep(0.1)

        self.monitor.stop_monitoring()

    def test_stop_monitoring(self):
        """测试停止监控"""
        # 先启动监控
        with patch("src.minicrm.core.system_monitor.psutil"):
            self.monitor.start_monitoring()

        # 停止监控
        self.monitor.stop_monitoring()

        self.assertFalse(self.monitor.is_monitoring())

    @patch("src.minicrm.core.system_monitor.psutil")
    def test_collect_system_metrics(self, mock_psutil):
        """测试收集系统指标"""
        # 模拟psutil返回值
        mock_psutil.cpu_percent.return_value = 50.0
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_memory.used = 1024 * 1024 * 1024  # 1GB
        mock_memory.available = 2048 * 1024 * 1024  # 2GB
        mock_psutil.virtual_memory.return_value = mock_memory

        mock_disk = Mock()
        mock_disk.percent = 70.0
        mock_disk.free = 100 * 1024 * 1024 * 1024  # 100GB
        mock_psutil.disk_usage.return_value = mock_disk

        mock_psutil.pids.return_value = list(range(150))

        mock_process = Mock()
        mock_process.num_threads.return_value = 20
        mock_psutil.Process.return_value = mock_process

        # 调用收集方法
        metrics = self.monitor._collect_system_metrics()

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.cpu_percent, 50.0)
        self.assertEqual(metrics.memory_percent, 60.0)
        self.assertEqual(metrics.memory_used_mb, 1024.0)
        self.assertEqual(metrics.memory_available_mb, 2048.0)
        self.assertEqual(metrics.disk_usage_percent, 70.0)
        self.assertEqual(metrics.disk_free_gb, 100.0)
        self.assertEqual(metrics.process_count, 150)
        self.assertEqual(metrics.thread_count, 20)

    @patch("src.minicrm.core.system_monitor.psutil")
    def test_collect_system_metrics_without_psutil(self, mock_psutil):
        """测试在没有psutil的情况下收集系统指标"""
        mock_psutil = None

        metrics = self.monitor._collect_system_metrics()

        self.assertIsNone(metrics)

    @patch("src.minicrm.core.system_monitor.performance_monitor")
    @patch("src.minicrm.core.system_monitor.threading.active_count")
    @patch("src.minicrm.core.system_monitor.psutil")
    def test_collect_app_metrics(
        self, mock_psutil, mock_active_count, mock_perf_monitor
    ):
        """测试收集应用程序指标"""
        # 模拟psutil
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 256 * 1024 * 1024  # 256MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.cpu_percent.return_value = 10.0
        mock_psutil.Process.return_value = mock_process

        # 模拟性能监控器
        mock_perf_monitor.get_all_operations.return_value = [
            "ui_operation",
            "database_query",
        ]
        mock_perf_monitor.get_operation_stats.side_effect = [
            {"count": 10, "avg_duration_ms": 100.0},
            {"count": 5, "avg_duration_ms": 50.0},
        ]

        # 模拟线程计数
        mock_active_count.return_value = 15

        # 模拟窗口计数
        self.monitor._count_active_windows = Mock(return_value=3)

        # 模拟错误计数
        self.monitor._get_recent_error_count = Mock(return_value=2)

        # 调用收集方法
        metrics = self.monitor._collect_app_metrics()

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.app_memory_mb, 256.0)
        self.assertEqual(metrics.app_cpu_percent, 10.0)
        self.assertEqual(metrics.ui_response_time_ms, 100.0)
        self.assertEqual(metrics.database_response_time_ms, 50.0)
        self.assertEqual(metrics.active_windows, 3)
        self.assertEqual(metrics.active_threads, 15)
        self.assertEqual(metrics.error_count, 2)

    def test_register_health_check(self):
        """测试注册健康检查"""

        def test_check():
            return HealthCheckResult("test", "healthy", "测试通过")

        self.monitor.register_health_check("test_check", test_check)

        self.assertIn("test_check", self.monitor._health_check_functions)
        self.assertEqual(self.monitor._health_check_functions["test_check"], test_check)

    def test_run_health_check(self):
        """测试运行健康检查"""

        # 注册测试检查函数
        def healthy_check():
            return HealthCheckResult("healthy_check", "healthy", "检查通过")

        def warning_check():
            return HealthCheckResult("warning_check", "warning", "检查警告")

        def failing_check():
            raise Exception("检查失败")

        self.monitor.register_health_check("healthy", healthy_check)
        self.monitor.register_health_check("warning", warning_check)
        self.monitor.register_health_check("failing", failing_check)

        # 运行健康检查
        results = self.monitor.run_health_check()

        self.assertEqual(len(results), 6)  # 3个自定义 + 3个默认检查

        # 检查结果
        result_names = [r.check_name for r in results]
        self.assertIn("healthy", result_names)
        self.assertIn("warning", result_names)
        self.assertIn("failing", result_names)

        # 检查失败的检查结果
        failing_result = next(r for r in results if r.check_name == "failing")
        self.assertEqual(failing_result.status, "critical")

    def test_get_system_metrics(self):
        """测试获取系统指标"""
        # 添加一些测试数据
        for i in range(10):
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=float(i * 10),
                memory_percent=50.0,
                memory_used_mb=1024.0,
                memory_available_mb=2048.0,
                disk_usage_percent=70.0,
                disk_free_gb=100.0,
                process_count=150,
                thread_count=20,
            )
            self.monitor._system_metrics.append(metrics)

        # 获取所有指标
        all_metrics = self.monitor.get_system_metrics()
        self.assertEqual(len(all_metrics), 10)

        # 获取限制数量的指标
        limited_metrics = self.monitor.get_system_metrics(limit=5)
        self.assertEqual(len(limited_metrics), 5)

    def test_get_app_metrics(self):
        """测试获取应用程序指标"""
        # 添加一些测试数据
        for i in range(10):
            metrics = ApplicationMetrics(
                timestamp=datetime.now(),
                app_memory_mb=256.0,
                app_cpu_percent=10.0,
                ui_response_time_ms=float(i * 10),
                database_response_time_ms=50.0,
                active_windows=3,
                active_threads=10,
                error_count=2,
            )
            self.monitor._app_metrics.append(metrics)

        # 获取所有指标
        all_metrics = self.monitor.get_app_metrics()
        self.assertEqual(len(all_metrics), 10)

        # 获取限制数量的指标
        limited_metrics = self.monitor.get_app_metrics(limit=5)
        self.assertEqual(len(limited_metrics), 5)

    def test_generate_performance_report(self):
        """测试生成性能报告"""
        # 添加一些测试数据
        now = datetime.now()

        # 系统指标
        for i in range(5):
            metrics = SystemMetrics(
                timestamp=now - timedelta(hours=i),
                cpu_percent=float(50 + i * 5),
                memory_percent=float(60 + i * 2),
                memory_used_mb=1024.0,
                memory_available_mb=2048.0,
                disk_usage_percent=70.0,
                disk_free_gb=100.0,
                process_count=150,
                thread_count=20,
            )
            self.monitor._system_metrics.append(metrics)

        # 应用程序指标
        for i in range(5):
            metrics = ApplicationMetrics(
                timestamp=now - timedelta(hours=i),
                app_memory_mb=256.0,
                app_cpu_percent=10.0,
                ui_response_time_ms=float(100 + i * 10),
                database_response_time_ms=float(50 + i * 5),
                active_windows=3,
                active_threads=10,
                error_count=2,
            )
            self.monitor._app_metrics.append(metrics)

        # 健康检查结果
        self.monitor._health_checks = [
            HealthCheckResult("test1", "healthy", "正常"),
            HealthCheckResult("test2", "warning", "警告"),
        ]

        # 生成报告
        report = self.monitor.generate_performance_report(hours=24)

        self.assertIn("report_time", report)
        self.assertIn("time_range_hours", report)
        self.assertIn("data_points", report)
        self.assertIn("system_performance", report)
        self.assertIn("application_performance", report)
        self.assertIn("health_status", report)
        self.assertIn("recommendations", report)

        # 检查系统性能数据
        sys_perf = report["system_performance"]
        self.assertIn("cpu", sys_perf)
        self.assertIn("memory", sys_perf)
        self.assertIn("disk_free_gb", sys_perf)

        # 检查应用程序性能数据
        app_perf = report["application_performance"]
        self.assertIn("ui_response_time", app_perf)
        self.assertIn("database_response_time", app_perf)
        self.assertIn("memory_usage_mb", app_perf)

        # 检查健康状态
        health_status = report["health_status"]
        self.assertEqual(health_status["test1"], "healthy")
        self.assertEqual(health_status["test2"], "warning")

    def test_generate_recommendations(self):
        """测试生成建议"""
        # 创建高CPU使用率的系统数据
        high_cpu_metrics = [
            SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=85.0,
                memory_percent=50.0,
                memory_used_mb=1024.0,
                memory_available_mb=2048.0,
                disk_usage_percent=70.0,
                disk_free_gb=100.0,
                process_count=150,
                thread_count=20,
            )
        ]

        # 创建高响应时间的应用数据
        slow_app_metrics = [
            ApplicationMetrics(
                timestamp=datetime.now(),
                app_memory_mb=256.0,
                app_cpu_percent=10.0,
                ui_response_time_ms=1500.0,
                database_response_time_ms=2500.0,
                active_windows=3,
                active_threads=10,
                error_count=2,
            )
        ]

        recommendations = self.monitor._generate_recommendations(
            high_cpu_metrics, slow_app_metrics
        )

        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)

        # 检查是否包含CPU相关建议
        cpu_recommendation_found = any("CPU" in rec for rec in recommendations)
        self.assertTrue(cpu_recommendation_found)

        # 检查是否包含UI响应时间建议
        ui_recommendation_found = any("UI响应时间" in rec for rec in recommendations)
        self.assertTrue(ui_recommendation_found)

    @patch("builtins.open")
    @patch("json.dump")
    def test_export_report(self, mock_json_dump, mock_open):
        """测试导出报告"""
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        self.monitor.export_report("test_report.json", hours=24)

        mock_open.assert_called_once_with("test_report.json", "w", encoding="utf-8")
        mock_json_dump.assert_called_once()

    def test_clear_history(self):
        """测试清除历史数据"""
        # 添加一些测试数据
        self.monitor._system_metrics.append(Mock())
        self.monitor._app_metrics.append(Mock())
        self.monitor._health_checks.append(Mock())

        # 清除历史
        self.monitor.clear_history()

        self.assertEqual(len(self.monitor._system_metrics), 0)
        self.assertEqual(len(self.monitor._app_metrics), 0)
        self.assertEqual(len(self.monitor._health_checks), 0)

    def test_get_monitoring_status(self):
        """测试获取监控状态"""
        status = self.monitor.get_monitoring_status()

        self.assertIn("monitoring_enabled", status)
        self.assertIn("monitoring_interval", status)
        self.assertIn("system_metrics_count", status)
        self.assertIn("app_metrics_count", status)
        self.assertIn("health_checks_count", status)
        self.assertIn("registered_health_checks", status)
        self.assertIn("psutil_available", status)

        self.assertEqual(status["monitoring_enabled"], False)
        self.assertEqual(status["monitoring_interval"], 5.0)


class TestGlobalFunctions(unittest.TestCase):
    """测试全局函数"""

    def test_get_system_monitor(self):
        """测试获取系统监控器"""
        monitor1 = get_system_monitor()
        monitor2 = get_system_monitor()

        # 应该返回同一个实例
        self.assertIs(monitor1, monitor2)
        self.assertIsInstance(monitor1, SystemMonitor)

    @patch("src.minicrm.core.system_monitor.get_system_monitor")
    def test_start_system_monitoring(self, mock_get_monitor):
        """测试启动系统监控"""
        mock_monitor = Mock()
        mock_get_monitor.return_value = mock_monitor

        start_system_monitoring()

        mock_monitor.start_monitoring.assert_called_once()

    @patch("src.minicrm.core.system_monitor.get_system_monitor")
    def test_stop_system_monitoring(self, mock_get_monitor):
        """测试停止系统监控"""
        mock_monitor = Mock()
        mock_get_monitor.return_value = mock_monitor

        stop_system_monitoring()

        mock_monitor.stop_monitoring.assert_called_once()

    @patch("src.minicrm.core.system_monitor.get_system_monitor")
    def test_run_health_check(self, mock_get_monitor):
        """测试运行健康检查"""
        mock_monitor = Mock()
        mock_results = [Mock(), Mock()]
        mock_monitor.run_health_check.return_value = mock_results
        mock_get_monitor.return_value = mock_monitor

        results = run_health_check()

        self.assertEqual(results, mock_results)
        mock_monitor.run_health_check.assert_called_once()

    @patch("src.minicrm.core.system_monitor.get_system_monitor")
    def test_generate_performance_report(self, mock_get_monitor):
        """测试生成性能报告"""
        mock_monitor = Mock()
        mock_report = {"test": "report"}
        mock_monitor.generate_performance_report.return_value = mock_report
        mock_get_monitor.return_value = mock_monitor

        report = generate_performance_report(hours=12)

        self.assertEqual(report, mock_report)
        mock_monitor.generate_performance_report.assert_called_once_with(12)


class TestPerformanceThresholds(unittest.TestCase):
    """测试性能阈值检查"""

    def setUp(self):
        """测试准备"""
        self.monitor = SystemMonitor()
        self.monitor._logger = Mock()

    def test_check_performance_thresholds_normal(self):
        """测试正常性能阈值检查"""
        system_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=50.0,
            memory_percent=60.0,
            memory_used_mb=1024.0,
            memory_available_mb=2048.0,
            disk_usage_percent=70.0,
            disk_free_gb=100.0,
            process_count=150,
            thread_count=20,
        )

        app_metrics = ApplicationMetrics(
            timestamp=datetime.now(),
            app_memory_mb=256.0,
            app_cpu_percent=10.0,
            ui_response_time_ms=500.0,
            database_response_time_ms=100.0,
            active_windows=3,
            active_threads=10,
            error_count=2,
        )

        # 不应该有警告或错误日志
        self.monitor._check_performance_thresholds(system_metrics, app_metrics)

        # 验证没有调用警告或错误日志
        self.monitor._logger.warning.assert_not_called()
        self.monitor._logger.critical.assert_not_called()

    def test_check_performance_thresholds_high_cpu(self):
        """测试高CPU使用率阈值检查"""
        system_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=95.0,  # 超过critical阈值
            memory_percent=60.0,
            memory_used_mb=1024.0,
            memory_available_mb=2048.0,
            disk_usage_percent=70.0,
            disk_free_gb=100.0,
            process_count=150,
            thread_count=20,
        )

        self.monitor._check_performance_thresholds(system_metrics, None)

        # 应该记录critical日志
        self.monitor._logger.critical.assert_called()
        call_args = self.monitor._logger.critical.call_args[0][0]
        self.assertIn("CPU使用率过高", call_args)

    def test_check_performance_thresholds_high_memory(self):
        """测试高内存使用率阈值检查"""
        system_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=50.0,
            memory_percent=98.0,  # 超过critical阈值
            memory_used_mb=1024.0,
            memory_available_mb=2048.0,
            disk_usage_percent=70.0,
            disk_free_gb=100.0,
            process_count=150,
            thread_count=20,
        )

        self.monitor._check_performance_thresholds(system_metrics, None)

        # 应该记录critical日志
        self.monitor._logger.critical.assert_called()
        call_args = self.monitor._logger.critical.call_args[0][0]
        self.assertIn("内存使用率过高", call_args)

    def test_check_performance_thresholds_slow_ui(self):
        """测试UI响应时间过长阈值检查"""
        app_metrics = ApplicationMetrics(
            timestamp=datetime.now(),
            app_memory_mb=256.0,
            app_cpu_percent=10.0,
            ui_response_time_ms=3500.0,  # 超过critical阈值
            database_response_time_ms=100.0,
            active_windows=3,
            active_threads=10,
            error_count=2,
        )

        self.monitor._check_performance_thresholds(None, app_metrics)

        # 应该记录critical日志
        self.monitor._logger.critical.assert_called()
        call_args = self.monitor._logger.critical.call_args[0][0]
        self.assertIn("UI响应时间过长", call_args)


if __name__ == "__main__":
    unittest.main()
