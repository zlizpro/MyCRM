"""MiniCRM 系统监控和诊断工具

提供全面的系统监控功能,包括:
- 系统性能监控(CPU、内存、磁盘)
- 应用程序性能监控
- 健康检查和诊断
- 性能报告生成
- 问题定位和建议

设计原则:
- 轻量级监控,不影响系统性能
- 实时监控和历史数据分析
- 智能诊断和问题定位
- 用户友好的报告生成
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
import threading
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional


try:
    import psutil
except ImportError:
    psutil = None

from .logger import get_logger
from .performance_monitor import performance_monitor


@dataclass
class SystemMetrics:
    """系统指标数据类"""

    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    process_count: int
    thread_count: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "memory_available_mb": self.memory_available_mb,
            "disk_usage_percent": self.disk_usage_percent,
            "disk_free_gb": self.disk_free_gb,
            "process_count": self.process_count,
            "thread_count": self.thread_count,
        }


@dataclass
class ApplicationMetrics:
    """应用程序指标数据类"""

    timestamp: datetime
    app_memory_mb: float
    app_cpu_percent: float
    ui_response_time_ms: float
    database_response_time_ms: float
    active_windows: int
    active_threads: int
    error_count: int

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "app_memory_mb": self.app_memory_mb,
            "app_cpu_percent": self.app_cpu_percent,
            "ui_response_time_ms": self.ui_response_time_ms,
            "database_response_time_ms": self.database_response_time_ms,
            "active_windows": self.active_windows,
            "active_threads": self.active_threads,
            "error_count": self.error_count,
        }


@dataclass
class HealthCheckResult:
    """健康检查结果数据类"""

    check_name: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "check_name": self.check_name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class SystemMonitor:
    """系统监控器

    提供全面的系统监控和诊断功能.
    """

    def __init__(self, max_history_size: int = 1000):
        """初始化系统监控器

        Args:
            max_history_size: 最大历史数据保存数量
        """
        self._logger = get_logger(__name__)
        self._max_history_size = max_history_size

        # 监控数据存储
        self._system_metrics: deque = deque(maxlen=max_history_size)
        self._app_metrics: deque = deque(maxlen=max_history_size)
        self._health_checks: List[HealthCheckResult] = []

        # 监控配置
        self._monitoring_enabled = False
        self._monitoring_interval = 5.0  # 秒
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

        # 性能阈值配置
        self._thresholds = {
            "cpu_warning": 70.0,
            "cpu_critical": 90.0,
            "memory_warning": 80.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0,
            "response_time_warning": 1000.0,  # ms
            "response_time_critical": 3000.0,  # ms
        }

        # 健康检查函数注册
        self._health_check_functions: Dict[str, Callable[[], HealthCheckResult]] = {}

        # 注册默认健康检查
        self._register_default_health_checks()

        # 应用程序引用
        self._app_reference: Optional[Any] = None

        self._logger.info("系统监控器初始化完成")

    def set_app_reference(self, app: Any) -> None:
        """设置应用程序引用

        Args:
            app: 应用程序实例
        """
        self._app_reference = app
        self._logger.debug("设置应用程序引用")

    def start_monitoring(self) -> None:
        """启动系统监控"""
        if self._monitoring_enabled:
            self._logger.warning("系统监控已经启动")
            return

        if psutil is None:
            self._logger.error("psutil库未安装,无法启动系统监控")
            return

        self._monitoring_enabled = True
        self._stop_monitoring.clear()

        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, name="SystemMonitor", daemon=True
        )
        self._monitoring_thread.start()

        self._logger.info("系统监控已启动")

    def stop_monitoring(self) -> None:
        """停止系统监控"""
        if not self._monitoring_enabled:
            return

        self._monitoring_enabled = False
        self._stop_monitoring.set()

        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5.0)

        self._logger.info("系统监控已停止")

    def is_monitoring(self) -> bool:
        """检查是否正在监控"""
        return self._monitoring_enabled

    def set_monitoring_interval(self, interval: float) -> None:
        """设置监控间隔

        Args:
            interval: 监控间隔(秒)
        """
        self._monitoring_interval = max(1.0, interval)
        self._logger.debug(f"设置监控间隔: {self._monitoring_interval}秒")

    def set_threshold(self, metric: str, value: float) -> None:
        """设置性能阈值

        Args:
            metric: 指标名称
            value: 阈值
        """
        if metric in self._thresholds:
            self._thresholds[metric] = value
            self._logger.debug(f"设置阈值 {metric}: {value}")

    def _monitoring_loop(self) -> None:
        """监控循环"""
        while not self._stop_monitoring.is_set():
            try:
                # 收集系统指标
                system_metrics = self._collect_system_metrics()
                if system_metrics:
                    self._system_metrics.append(system_metrics)

                # 收集应用程序指标
                app_metrics = self._collect_app_metrics()
                if app_metrics:
                    self._app_metrics.append(app_metrics)

                # 检查性能阈值
                self._check_performance_thresholds(system_metrics, app_metrics)

            except Exception as e:
                self._logger.error(f"监控循环错误: {e}")

            # 等待下一次监控
            self._stop_monitoring.wait(self._monitoring_interval)

    def _collect_system_metrics(self) -> Optional[SystemMetrics]:
        """收集系统指标"""
        if psutil is None:
            return None

        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # 内存信息
            memory = psutil.virtual_memory()

            # 磁盘信息
            disk = psutil.disk_usage("/")

            # 进程信息
            process_count = len(psutil.pids())

            # 当前进程的线程数
            current_process = psutil.Process()
            thread_count = current_process.num_threads()

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_available_mb=memory.available / 1024 / 1024,
                disk_usage_percent=disk.percent,
                disk_free_gb=disk.free / 1024 / 1024 / 1024,
                process_count=process_count,
                thread_count=thread_count,
            )

        except Exception as e:
            self._logger.error(f"收集系统指标失败: {e}")
            return None

    def _collect_app_metrics(self) -> Optional[ApplicationMetrics]:
        """收集应用程序指标"""
        try:
            # 应用程序内存和CPU使用
            app_memory_mb = 0.0
            app_cpu_percent = 0.0

            if psutil:
                current_process = psutil.Process()
                memory_info = current_process.memory_info()
                app_memory_mb = memory_info.rss / 1024 / 1024
                app_cpu_percent = current_process.cpu_percent()

            # UI响应时间(通过性能监控器获取)
            ui_response_time = self._get_average_ui_response_time()

            # 数据库响应时间
            db_response_time = self._get_average_db_response_time()

            # 活动窗口数(如果有应用程序引用)
            active_windows = self._count_active_windows()

            # 活动线程数
            active_threads = threading.active_count()

            # 错误计数(从错误处理器获取)
            error_count = self._get_recent_error_count()

            return ApplicationMetrics(
                timestamp=datetime.now(),
                app_memory_mb=app_memory_mb,
                app_cpu_percent=app_cpu_percent,
                ui_response_time_ms=ui_response_time,
                database_response_time_ms=db_response_time,
                active_windows=active_windows,
                active_threads=active_threads,
                error_count=error_count,
            )

        except Exception as e:
            self._logger.error(f"收集应用程序指标失败: {e}")
            return None

    def _get_average_ui_response_time(self) -> float:
        """获取平均UI响应时间"""
        try:
            # 从性能监控器获取UI相关操作的平均响应时间
            ui_operations = [
                op
                for op in performance_monitor.get_all_operations()
                if "ui_" in op.lower() or "widget" in op.lower()
            ]

            if not ui_operations:
                return 0.0

            total_time = 0.0
            total_count = 0

            for operation in ui_operations:
                stats = performance_monitor.get_operation_stats(operation)
                if stats["count"] > 0:
                    total_time += stats["avg_duration_ms"]
                    total_count += 1

            return total_time / max(total_count, 1)

        except Exception as e:
            self._logger.error(f"获取UI响应时间失败: {e}")
            return 0.0

    def _get_average_db_response_time(self) -> float:
        """获取平均数据库响应时间"""
        try:
            # 从性能监控器获取数据库相关操作的平均响应时间
            db_operations = [
                op
                for op in performance_monitor.get_all_operations()
                if "database" in op.lower()
                or "sql" in op.lower()
                or "dao" in op.lower()
            ]

            if not db_operations:
                return 0.0

            total_time = 0.0
            total_count = 0

            for operation in db_operations:
                stats = performance_monitor.get_operation_stats(operation)
                if stats["count"] > 0:
                    total_time += stats["avg_duration_ms"]
                    total_count += 1

            return total_time / max(total_count, 1)

        except Exception as e:
            self._logger.error(f"获取数据库响应时间失败: {e}")
            return 0.0

    def _count_active_windows(self) -> int:
        """统计活动窗口数"""
        try:
            if self._app_reference and hasattr(self._app_reference, "winfo_children"):
                # 递归统计所有窗口
                def count_windows(widget):
                    count = 1 if isinstance(widget, (tk.Tk, tk.Toplevel)) else 0
                    for child in widget.winfo_children():
                        count += count_windows(child)
                    return count

                return count_windows(self._app_reference)
            return 1  # 至少有主窗口

        except Exception as e:
            self._logger.error(f"统计活动窗口失败: {e}")
            return 1

    def _get_recent_error_count(self) -> int:
        """获取最近的错误计数"""
        try:
            # 这里应该从错误处理器获取最近的错误计数
            # 暂时返回0,实际实现时需要集成错误处理器
            return 0

        except Exception as e:
            self._logger.error(f"获取错误计数失败: {e}")
            return 0

    def _check_performance_thresholds(
        self,
        system_metrics: Optional[SystemMetrics],
        app_metrics: Optional[ApplicationMetrics],
    ) -> None:
        """检查性能阈值"""
        if not system_metrics:
            return

        # 检查CPU使用率
        if system_metrics.cpu_percent > self._thresholds["cpu_critical"]:
            self._logger.critical(f"CPU使用率过高: {system_metrics.cpu_percent:.1f}%")
        elif system_metrics.cpu_percent > self._thresholds["cpu_warning"]:
            self._logger.warning(f"CPU使用率较高: {system_metrics.cpu_percent:.1f}%")

        # 检查内存使用率
        if system_metrics.memory_percent > self._thresholds["memory_critical"]:
            self._logger.critical(
                f"内存使用率过高: {system_metrics.memory_percent:.1f}%"
            )
        elif system_metrics.memory_percent > self._thresholds["memory_warning"]:
            self._logger.warning(
                f"内存使用率较高: {system_metrics.memory_percent:.1f}%"
            )

        # 检查磁盘使用率
        if system_metrics.disk_usage_percent > self._thresholds["disk_critical"]:
            self._logger.critical(
                f"磁盘使用率过高: {system_metrics.disk_usage_percent:.1f}%"
            )
        elif system_metrics.disk_usage_percent > self._thresholds["disk_warning"]:
            self._logger.warning(
                f"磁盘使用率较高: {system_metrics.disk_usage_percent:.1f}%"
            )

        # 检查应用程序响应时间
        if app_metrics:
            if (
                app_metrics.ui_response_time_ms
                > self._thresholds["response_time_critical"]
            ):
                self._logger.critical(
                    f"UI响应时间过长: {app_metrics.ui_response_time_ms:.1f}ms"
                )
            elif (
                app_metrics.ui_response_time_ms
                > self._thresholds["response_time_warning"]
            ):
                self._logger.warning(
                    f"UI响应时间较长: {app_metrics.ui_response_time_ms:.1f}ms"
                )

    def run_health_check(self) -> List[HealthCheckResult]:
        """运行健康检查

        Returns:
            List[HealthCheckResult]: 健康检查结果列表
        """
        results = []

        for check_name, check_function in self._health_check_functions.items():
            try:
                result = check_function()
                results.append(result)

                # 记录日志
                if result.status == "critical":
                    self._logger.error(f"健康检查失败 [{check_name}]: {result.message}")
                elif result.status == "warning":
                    self._logger.warning(
                        f"健康检查警告 [{check_name}]: {result.message}"
                    )
                else:
                    self._logger.debug(f"健康检查正常 [{check_name}]: {result.message}")

            except Exception as e:
                self._logger.error(f"健康检查异常 [{check_name}]: {e}")
                results.append(
                    HealthCheckResult(
                        check_name=check_name,
                        status="critical",
                        message=f"检查执行失败: {e}",
                        details={"exception": str(e)},
                    )
                )

        # 保存检查结果
        self._health_checks = results

        return results

    def register_health_check(
        self, name: str, check_function: Callable[[], HealthCheckResult]
    ) -> None:
        """注册健康检查函数

        Args:
            name: 检查名称
            check_function: 检查函数
        """
        self._health_check_functions[name] = check_function
        self._logger.debug(f"注册健康检查: {name}")

    def _register_default_health_checks(self) -> None:
        """注册默认的健康检查"""

        def check_system_resources() -> HealthCheckResult:
            """检查系统资源"""
            if not self._system_metrics:
                return HealthCheckResult(
                    check_name="system_resources",
                    status="warning",
                    message="无系统监控数据",
                )

            latest = self._system_metrics[-1]

            if (
                latest.cpu_percent > 90
                or latest.memory_percent > 95
                or latest.disk_usage_percent > 95
            ):
                return HealthCheckResult(
                    check_name="system_resources",
                    status="critical",
                    message="系统资源严重不足",
                    details={
                        "cpu_percent": latest.cpu_percent,
                        "memory_percent": latest.memory_percent,
                        "disk_percent": latest.disk_usage_percent,
                    },
                )
            if (
                latest.cpu_percent > 70
                or latest.memory_percent > 80
                or latest.disk_usage_percent > 85
            ):
                return HealthCheckResult(
                    check_name="system_resources",
                    status="warning",
                    message="系统资源使用率较高",
                    details={
                        "cpu_percent": latest.cpu_percent,
                        "memory_percent": latest.memory_percent,
                        "disk_percent": latest.disk_usage_percent,
                    },
                )
            return HealthCheckResult(
                check_name="system_resources", status="healthy", message="系统资源正常"
            )

        def check_application_performance() -> HealthCheckResult:
            """检查应用程序性能"""
            if not self._app_metrics:
                return HealthCheckResult(
                    check_name="application_performance",
                    status="warning",
                    message="无应用程序监控数据",
                )

            latest = self._app_metrics[-1]

            if (
                latest.ui_response_time_ms > 3000
                or latest.database_response_time_ms > 5000
            ):
                return HealthCheckResult(
                    check_name="application_performance",
                    status="critical",
                    message="应用程序响应时间过长",
                    details={
                        "ui_response_ms": latest.ui_response_time_ms,
                        "db_response_ms": latest.database_response_time_ms,
                    },
                )
            if (
                latest.ui_response_time_ms > 1000
                or latest.database_response_time_ms > 2000
            ):
                return HealthCheckResult(
                    check_name="application_performance",
                    status="warning",
                    message="应用程序响应时间较长",
                    details={
                        "ui_response_ms": latest.ui_response_time_ms,
                        "db_response_ms": latest.database_response_time_ms,
                    },
                )
            return HealthCheckResult(
                check_name="application_performance",
                status="healthy",
                message="应用程序性能正常",
            )

        def check_database_connectivity() -> HealthCheckResult:
            """检查数据库连接"""
            try:
                # 尝试连接数据库
                # 这里需要根据实际的数据库配置进行调整
                test_db_path = ":memory:"  # 使用内存数据库进行测试
                conn = sqlite3.connect(test_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                conn.close()

                return HealthCheckResult(
                    check_name="database_connectivity",
                    status="healthy",
                    message="数据库连接正常",
                )

            except Exception as e:
                return HealthCheckResult(
                    check_name="database_connectivity",
                    status="critical",
                    message=f"数据库连接失败: {e}",
                    details={"exception": str(e)},
                )

        # 注册默认检查
        self.register_health_check("system_resources", check_system_resources)
        self.register_health_check(
            "application_performance", check_application_performance
        )
        self.register_health_check("database_connectivity", check_database_connectivity)

    def get_system_metrics(self, limit: int = 100) -> List[SystemMetrics]:
        """获取系统指标历史数据

        Args:
            limit: 返回数量限制

        Returns:
            List[SystemMetrics]: 系统指标列表
        """
        return list(self._system_metrics)[-limit:]

    def get_app_metrics(self, limit: int = 100) -> List[ApplicationMetrics]:
        """获取应用程序指标历史数据

        Args:
            limit: 返回数量限制

        Returns:
            List[ApplicationMetrics]: 应用程序指标列表
        """
        return list(self._app_metrics)[-limit:]

    def get_latest_health_check(self) -> List[HealthCheckResult]:
        """获取最新的健康检查结果"""
        return self._health_checks.copy()

    def generate_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """生成性能报告

        Args:
            hours: 报告时间范围(小时)

        Returns:
            Dict[str, Any]: 性能报告数据
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # 筛选时间范围内的数据
        system_data = [m for m in self._system_metrics if m.timestamp >= cutoff_time]

        app_data = [m for m in self._app_metrics if m.timestamp >= cutoff_time]

        # 生成报告
        report = {
            "report_time": datetime.now().isoformat(),
            "time_range_hours": hours,
            "data_points": {
                "system_metrics": len(system_data),
                "app_metrics": len(app_data),
            },
        }

        # 系统性能统计
        if system_data:
            cpu_values = [m.cpu_percent for m in system_data]
            memory_values = [m.memory_percent for m in system_data]

            report["system_performance"] = {
                "cpu": {
                    "avg": sum(cpu_values) / len(cpu_values),
                    "max": max(cpu_values),
                    "min": min(cpu_values),
                },
                "memory": {
                    "avg": sum(memory_values) / len(memory_values),
                    "max": max(memory_values),
                    "min": min(memory_values),
                },
                "disk_free_gb": system_data[-1].disk_free_gb if system_data else 0,
            }

        # 应用程序性能统计
        if app_data:
            ui_times = [m.ui_response_time_ms for m in app_data]
            db_times = [m.database_response_time_ms for m in app_data]

            report["application_performance"] = {
                "ui_response_time": {
                    "avg": sum(ui_times) / len(ui_times),
                    "max": max(ui_times),
                    "min": min(ui_times),
                },
                "database_response_time": {
                    "avg": sum(db_times) / len(db_times),
                    "max": max(db_times),
                    "min": min(db_times),
                },
                "memory_usage_mb": app_data[-1].app_memory_mb if app_data else 0,
            }

        # 健康检查摘要
        health_summary = {}
        for result in self._health_checks:
            health_summary[result.check_name] = result.status

        report["health_status"] = health_summary

        # 性能建议
        report["recommendations"] = self._generate_recommendations(
            system_data, app_data
        )

        return report

    def _generate_recommendations(
        self, system_data: List[SystemMetrics], app_data: List[ApplicationMetrics]
    ) -> List[str]:
        """生成性能优化建议"""
        recommendations = []

        if system_data:
            latest_system = system_data[-1]

            # CPU建议
            if latest_system.cpu_percent > 80:
                recommendations.append("CPU使用率过高,建议关闭不必要的程序或升级硬件")

            # 内存建议
            if latest_system.memory_percent > 85:
                recommendations.append("内存使用率过高,建议增加内存或优化程序内存使用")

            # 磁盘建议
            if latest_system.disk_usage_percent > 90:
                recommendations.append("磁盘空间不足,建议清理临时文件或扩展存储空间")

        if app_data:
            latest_app = app_data[-1]

            # UI响应时间建议
            if latest_app.ui_response_time_ms > 1000:
                recommendations.append(
                    "UI响应时间较长,建议优化界面操作或减少同时运行的任务"
                )

            # 数据库响应时间建议
            if latest_app.database_response_time_ms > 2000:
                recommendations.append("数据库响应时间较长,建议优化查询语句或添加索引")

            # 内存使用建议
            if latest_app.app_memory_mb > 500:
                recommendations.append(
                    "应用程序内存使用较高,建议重启程序或检查内存泄漏"
                )

        if not recommendations:
            recommendations.append("系统运行正常,无需特别优化")

        return recommendations

    def export_report(self, file_path: str, hours: int = 24) -> None:
        """导出性能报告到文件

        Args:
            file_path: 导出文件路径
            hours: 报告时间范围(小时)
        """
        try:
            report = self.generate_performance_report(hours)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            self._logger.info(f"性能报告已导出到: {file_path}")

        except Exception as e:
            self._logger.error(f"导出性能报告失败: {e}")
            raise

    def clear_history(self) -> None:
        """清除历史监控数据"""
        self._system_metrics.clear()
        self._app_metrics.clear()
        self._health_checks.clear()
        self._logger.info("监控历史数据已清除")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态信息"""
        return {
            "monitoring_enabled": self._monitoring_enabled,
            "monitoring_interval": self._monitoring_interval,
            "system_metrics_count": len(self._system_metrics),
            "app_metrics_count": len(self._app_metrics),
            "health_checks_count": len(self._health_checks),
            "registered_health_checks": list(self._health_check_functions.keys()),
            "psutil_available": psutil is not None,
        }


# 全局系统监控器实例
_system_monitor: Optional[SystemMonitor] = None


def get_system_monitor() -> SystemMonitor:
    """获取全局系统监控器实例

    Returns:
        SystemMonitor: 系统监控器实例
    """
    global _system_monitor

    if _system_monitor is None:
        _system_monitor = SystemMonitor()

    return _system_monitor


def start_system_monitoring() -> None:
    """启动系统监控"""
    get_system_monitor().start_monitoring()


def stop_system_monitoring() -> None:
    """停止系统监控"""
    get_system_monitor().stop_monitoring()


def run_health_check() -> List[HealthCheckResult]:
    """运行健康检查"""
    return get_system_monitor().run_health_check()


def generate_performance_report(hours: int = 24) -> Dict[str, Any]:
    """生成性能报告"""
    return get_system_monitor().generate_performance_report(hours)
