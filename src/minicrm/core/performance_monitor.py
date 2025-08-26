"""
MiniCRM 性能监控系统

提供应用程序性能监控功能,包括:
- 操作执行时间监控
- 数据库查询性能监控
- 内存使用监控
- 性能数据收集和分析
"""

import functools
import logging
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import psutil


@dataclass
class PerformanceMetric:
    """性能指标数据类"""

    operation: str
    start_time: datetime
    end_time: datetime
    duration: float  # 毫秒
    memory_before: float  # MB
    memory_after: float  # MB
    memory_delta: float  # MB
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """获取持续时间(毫秒)"""
        return self.duration * 1000


class PerformanceMonitor:
    """
    性能监控器

    提供性能监控的核心功能,包括时间测量、内存监控和数据收集.
    """

    _instance: Optional["PerformanceMonitor"] = None

    def __new__(cls) -> "PerformanceMonitor":
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化性能监控器"""
        if hasattr(self, "_initialized"):
            return

        self._logger = logging.getLogger(__name__)
        self._metrics: list[PerformanceMetric] = []
        self._enabled = True
        self._max_metrics = 1000  # 最大保存的指标数量
        self._initialized = True

        self._logger.debug("性能监控器初始化完成")

    def enable(self) -> None:
        """启用性能监控"""
        self._enabled = True
        self._logger.info("性能监控已启用")

    def disable(self) -> None:
        """禁用性能监控"""
        self._enabled = False
        self._logger.info("性能监控已禁用")

    def is_enabled(self) -> bool:
        """检查是否启用了性能监控"""
        return self._enabled

    @contextmanager
    def monitor_operation(self, operation_name: str, **metadata):
        """
        监控操作的上下文管理器

        Args:
            operation_name: 操作名称
            **metadata: 额外的元数据

        Example:
            with monitor.monitor_operation("database_query", table="customers"):
                # 执行数据库查询
                pass
        """
        if not self._enabled:
            yield
            return

        # 记录开始状态
        start_time = datetime.now()
        start_timestamp = time.perf_counter()
        memory_before = self._get_memory_usage()

        try:
            yield
        finally:
            # 记录结束状态
            end_time = datetime.now()
            end_timestamp = time.perf_counter()
            memory_after = self._get_memory_usage()

            # 计算性能指标
            duration = end_timestamp - start_timestamp
            memory_delta = memory_after - memory_before

            # 创建性能指标
            metric = PerformanceMetric(
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                memory_before=memory_before,
                memory_after=memory_after,
                memory_delta=memory_delta,
                metadata=metadata,
            )

            # 保存指标
            self._add_metric(metric)

            # 记录日志
            self._logger.debug(
                f"性能监控 [{operation_name}]: "
                f"耗时 {duration * 1000:.2f}ms, "
                f"内存变化 {memory_delta:+.2f}MB"
            )

    def monitor_function(self, operation_name: str = None, **metadata):
        """
        函数装饰器,用于监控函数性能

        Args:
            operation_name: 操作名称,默认使用函数名
            **metadata: 额外的元数据

        Example:
            @monitor.monitor_function("customer_creation")
            def create_customer(data):
                # 创建客户逻辑
                pass
        """

        def decorator(func: Callable) -> Callable:
            op_name = (
                operation_name
                or f"{getattr(func, '__module__', 'unknown')}.{getattr(func, '__name__', 'unknown')}"
            )

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.monitor_operation(op_name, **metadata):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def record_metric(
        self, operation: str, duration: float, memory_delta: float = 0.0, **metadata
    ) -> None:
        """
        手动记录性能指标

        Args:
            operation: 操作名称
            duration: 持续时间(秒)
            memory_delta: 内存变化(MB)
            **metadata: 额外的元数据
        """
        if not self._enabled:
            return

        now = datetime.now()
        metric = PerformanceMetric(
            operation=operation,
            start_time=now,
            end_time=now,
            duration=duration,
            memory_before=0.0,
            memory_after=memory_delta,
            memory_delta=memory_delta,
            metadata=metadata,
        )

        self._add_metric(metric)

    def get_metrics(
        self, operation: str = None, limit: int = None
    ) -> list[PerformanceMetric]:
        """
        获取性能指标

        Args:
            operation: 操作名称过滤器
            limit: 返回数量限制

        Returns:
            List[PerformanceMetric]: 性能指标列表
        """
        metrics = self._metrics

        # 按操作名称过滤
        if operation:
            metrics = [m for m in metrics if m.operation == operation]

        # 按时间倒序排列
        metrics = sorted(metrics, key=lambda m: m.start_time, reverse=True)

        # 限制数量
        if limit:
            metrics = metrics[:limit]

        return metrics

    def get_operation_stats(self, operation: str) -> dict[str, Any]:
        """
        获取操作的统计信息

        Args:
            operation: 操作名称

        Returns:
            Dict[str, Any]: 统计信息
        """
        metrics = self.get_metrics(operation)

        if not metrics:
            return {
                "operation": operation,
                "count": 0,
                "avg_duration_ms": 0.0,
                "min_duration_ms": 0.0,
                "max_duration_ms": 0.0,
                "total_duration_ms": 0.0,
                "avg_memory_delta_mb": 0.0,
            }

        durations = [m.duration_ms for m in metrics]
        memory_deltas = [m.memory_delta for m in metrics]

        return {
            "operation": operation,
            "count": len(metrics),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "total_duration_ms": sum(durations),
            "avg_memory_delta_mb": sum(memory_deltas) / len(memory_deltas),
            "last_execution": metrics[0].start_time.isoformat(),
        }

    def get_all_operations(self) -> list[str]:
        """获取所有监控的操作名称"""
        operations = set(m.operation for m in self._metrics)
        return sorted(operations)

    def get_summary(self) -> dict[str, Any]:
        """
        获取性能监控摘要

        Returns:
            Dict[str, Any]: 摘要信息
        """
        if not self._metrics:
            return {
                "total_operations": 0,
                "unique_operations": 0,
                "total_duration_ms": 0.0,
                "avg_duration_ms": 0.0,
                "current_memory_mb": self._get_memory_usage(),
                "monitoring_enabled": self._enabled,
            }

        durations = [m.duration_ms for m in self._metrics]

        return {
            "total_operations": len(self._metrics),
            "unique_operations": len(self.get_all_operations()),
            "total_duration_ms": sum(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "current_memory_mb": self._get_memory_usage(),
            "monitoring_enabled": self._enabled,
            "oldest_metric": min(
                self._metrics, key=lambda m: m.start_time
            ).start_time.isoformat(),
            "newest_metric": max(
                self._metrics, key=lambda m: m.start_time
            ).start_time.isoformat(),
        }

    def clear_metrics(self) -> None:
        """清空所有性能指标"""
        self._metrics.clear()
        self._logger.info("性能指标已清空")

    def export_metrics(self, file_path: str) -> None:
        """
        导出性能指标到文件

        Args:
            file_path: 导出文件路径
        """
        import json
        from pathlib import Path

        try:
            # 准备导出数据
            export_data = {
                "export_time": datetime.now().isoformat(),
                "summary": self.get_summary(),
                "metrics": [
                    {
                        "operation": m.operation,
                        "start_time": m.start_time.isoformat(),
                        "end_time": m.end_time.isoformat(),
                        "duration_ms": m.duration_ms,
                        "memory_before_mb": m.memory_before,
                        "memory_after_mb": m.memory_after,
                        "memory_delta_mb": m.memory_delta,
                        "metadata": self._serialize_metadata(m.metadata),
                    }
                    for m in self._metrics
                ],
            }

            # 写入文件
            Path(file_path).write_text(
                json.dumps(export_data, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            self._logger.info(f"性能指标已导出到: {file_path}")

        except Exception as e:
            self._logger.error(f"导出性能指标失败: {e}")
            raise

    def _add_metric(self, metric: PerformanceMetric) -> None:
        """添加性能指标"""
        self._metrics.append(metric)

        # 限制指标数量
        if len(self._metrics) > self._max_metrics:
            # 删除最旧的指标
            self._metrics = sorted(
                self._metrics, key=lambda m: m.start_time, reverse=True
            )[: self._max_metrics]

    def _get_memory_usage(self) -> float:
        """获取当前内存使用量(MB)"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # 转换为MB
        except Exception as e:
            self._logger.warning(f"获取内存使用量失败: {e}")
            return 0.0

    def _serialize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """序列化元数据,确保JSON兼容"""
        serialized = {}
        for key, value in metadata.items():
            try:
                if isinstance(value, datetime):
                    serialized[key] = value.isoformat()
                elif hasattr(value, "__dict__"):
                    # 对象类型,转换为字符串
                    serialized[key] = str(value)
                else:
                    # 尝试JSON序列化测试
                    import json

                    json.dumps(value)
                    serialized[key] = value
            except (TypeError, ValueError):
                # 无法序列化的值转换为字符串
                serialized[key] = str(value)
        return serialized

    @classmethod
    def get_instance(cls) -> "PerformanceMonitor":
        """获取单例实例"""
        return cls()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


# 便捷函数
def monitor_operation(operation_name: str, **metadata):
    """监控操作的上下文管理器"""
    return performance_monitor.monitor_operation(operation_name, **metadata)


def monitor_function(operation_name: str = None, **metadata):
    """函数性能监控装饰器"""
    return performance_monitor.monitor_function(operation_name, **metadata)


def get_performance_summary() -> dict[str, Any]:
    """获取性能监控摘要"""
    return performance_monitor.get_summary()


def enable_monitoring() -> None:
    """启用性能监控"""
    performance_monitor.enable()


def disable_monitoring() -> None:
    """禁用性能监控"""
    performance_monitor.disable()
