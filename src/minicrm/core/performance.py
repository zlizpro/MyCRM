"""MiniCRM 性能优化核心模块
提供内存管理、缓存、性能监控等功能
"""

import gc
import threading
import time
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

import psutil


class MemoryManager:
    """内存管理器 - 监控和优化内存使用"""

    def __init__(
        self, warning_threshold_mb: int = 200, critical_threshold_mb: int = 400
    ):
        self.warning_threshold = warning_threshold_mb * 1024 * 1024  # 转换为字节
        self.critical_threshold = critical_threshold_mb * 1024 * 1024
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_usage()

    def get_memory_usage(self) -> dict[str, float]:
        """获取当前内存使用情况"""
        memory_info = self.process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": self.process.memory_percent(),
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }

    def check_memory_status(self) -> dict[str, Any]:
        """检查内存状态并返回建议"""
        current = self.get_memory_usage()
        rss_bytes = current["rss_mb"] * 1024 * 1024

        if rss_bytes > self.critical_threshold:
            status = "critical"
            suggestion = "立即执行垃圾回收和内存清理"
        elif rss_bytes > self.warning_threshold:
            status = "warning"
            suggestion = "建议执行垃圾回收"
        else:
            status = "good"
            suggestion = "内存使用正常"

        return {
            "status": status,
            "current_mb": current["rss_mb"],
            "suggestion": suggestion,
            "details": current,
        }

    def force_garbage_collection(self) -> dict[str, Any]:
        """强制执行垃圾回收"""
        before = self.get_memory_usage()

        # 执行垃圾回收
        collected = gc.collect()

        after = self.get_memory_usage()
        freed_mb = before["rss_mb"] - after["rss_mb"]

        return {
            "objects_collected": collected,
            "memory_freed_mb": freed_mb,
            "before_mb": before["rss_mb"],
            "after_mb": after["rss_mb"],
        }


class SmartCache:
    """智能缓存系统 - 支持TTL和LRU策略"""

    def __init__(self, max_size: int = 128, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: dict[str, Any] = {}
        self.access_times: dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        with self._lock:
            if key not in self.cache:
                self.miss_count += 1
                return None

            # 检查是否过期
            if time.time() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                self.miss_count += 1
                return None

            # 更新访问时间
            self.access_times[key] = time.time()
            self.hit_count += 1
            return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        with self._lock:
            # 清理过期项
            self._cleanup_expired()

            # 如果缓存满了，删除最旧的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                oldest_key = min(
                    self.access_times.keys(), key=lambda k: self.access_times[k]
                )
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = value
            self.access_times[key] = time.time()

    def _cleanup_expired(self) -> None:
        """清理过期的缓存项"""
        current_time = time.time()
        expired_keys = [
            key
            for key, access_time in self.access_times.items()
            if current_time - access_time > self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate_percent": hit_rate,
            "memory_usage_mb": self._estimate_memory_usage(),
        }

    def _estimate_memory_usage(self) -> float:
        """估算缓存内存使用量"""
        import sys

        total_size = 0
        for key, value in self.cache.items():
            total_size += sys.getsizeof(key) + sys.getsizeof(value)
        return total_size / 1024 / 1024  # 转换为MB


def performance_monitor(func_name: str | None = None):
    """性能监控装饰器"""

    def decorator(func: Callable) -> Callable:
        name = func_name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss

                execution_time = end_time - start_time
                memory_delta = (end_memory - start_memory) / 1024 / 1024  # MB

                # 记录性能数据
                PerformanceTracker.instance().record_execution(
                    name,
                    execution_time,
                    memory_delta,
                )

                # 如果执行时间过长，发出警告
                if execution_time > 1.0:  # 1秒
                    print(f"⚠️ 慢操作检测: {name} 耗时 {execution_time:.2f}秒")

        return wrapper

    return decorator


class PerformanceTracker:
    """性能跟踪器 - 单例模式"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.execution_times: dict[str, list] = {}
        self.memory_deltas: dict[str, list] = {}
        self._lock = threading.RLock()
        self._initialized = True

    @classmethod
    def instance(cls):
        return cls()

    def record_execution(
        self, func_name: str, execution_time: float, memory_delta: float
    ):
        """记录函数执行性能"""
        with self._lock:
            if func_name not in self.execution_times:
                self.execution_times[func_name] = []
                self.memory_deltas[func_name] = []

            self.execution_times[func_name].append(execution_time)
            self.memory_deltas[func_name].append(memory_delta)

            # 保持最近100次记录
            if len(self.execution_times[func_name]) > 100:
                self.execution_times[func_name] = self.execution_times[func_name][-100:]
                self.memory_deltas[func_name] = self.memory_deltas[func_name][-100:]

    def get_performance_summary(self) -> dict[str, dict[str, float]]:
        """获取性能摘要"""
        summary = {}

        with self._lock:
            for func_name in self.execution_times:
                times = self.execution_times[func_name]
                memories = self.memory_deltas[func_name]

                if times:
                    summary[func_name] = {
                        "avg_time": sum(times) / len(times),
                        "max_time": max(times),
                        "min_time": min(times),
                        "call_count": len(times),
                        "avg_memory_delta": sum(memories) / len(memories),
                        "max_memory_delta": max(memories),
                    }

        return summary

    def get_slowest_functions(self, top_n: int = 10) -> list:
        """获取最慢的函数"""
        summary = self.get_performance_summary()
        sorted_funcs = sorted(
            summary.items(), key=lambda x: x[1]["avg_time"], reverse=True
        )
        return sorted_funcs[:top_n]


@contextmanager
def memory_context(description: str = "操作"):
    """内存使用上下文管理器"""
    manager = MemoryManager()
    before = manager.get_memory_usage()

    print(f"🔍 开始{description} - 内存使用: {before['rss_mb']:.1f}MB")

    try:
        yield manager
    finally:
        after = manager.get_memory_usage()
        delta = after["rss_mb"] - before["rss_mb"]

        if delta > 10:  # 10MB
            print(f"⚠️ {description}完成 - 内存增加: {delta:.1f}MB")
        else:
            print(f"✅ {description}完成 - 内存变化: {delta:+.1f}MB")


# 全局实例
memory_manager = MemoryManager()
global_cache = SmartCache()
performance_tracker = PerformanceTracker.instance()
