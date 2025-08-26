"""MiniCRM TTK性能优化器

整合所有TTK性能优化功能,包括:
- 虚拟滚动优化
- 异步处理管理
- 内存使用优化
- UI响应性优化
- 性能监控和分析
- 自动优化建议
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import gc
import logging
import threading
import time
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional
from weakref import WeakSet

import psutil

from ...core.data_cache_manager import data_cache_manager
from .async_processor import async_processor
from .virtual_scroll_mixin import VirtualScrollMixin


@dataclass
class PerformanceMetrics:
    """性能指标"""

    timestamp: datetime = field(default_factory=datetime.now)
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    ui_response_time_ms: float = 0.0
    render_time_ms: float = 0.0
    active_widgets: int = 0
    virtual_scroll_items: int = 0
    async_tasks_running: int = 0
    cache_hit_rate: float = 0.0
    cache_size_mb: float = 0.0


@dataclass
class OptimizationRule:
    """优化规则"""

    name: str
    condition: Callable[[PerformanceMetrics], bool]
    action: Callable[[], None]
    priority: int = 1  # 1=高, 2=中, 3=低
    cooldown_seconds: int = 60  # 冷却时间
    last_executed: Optional[datetime] = None
    description: str = ""


class TTKPerformanceOptimizer:
    """TTK性能优化器

    提供全面的TTK界面性能优化和监控功能.
    """

    def __init__(self):
        """初始化TTK性能优化器"""
        self._logger = logging.getLogger(__name__)

        # 组件引用
        self._async_processor = async_processor
        self._cache_manager = data_cache_manager

        # 性能监控
        self._metrics_history: List[PerformanceMetrics] = []
        self._max_history_size = 1000
        self._monitoring_enabled = True
        self._monitoring_interval = 5.0  # 秒

        # 组件跟踪
        self._tracked_widgets: WeakSet = WeakSet()
        self._virtual_scroll_components: WeakSet = WeakSet()
        self._render_times: Dict[str, List[float]] = {}

        # 优化规则
        self._optimization_rules: List[OptimizationRule] = []
        self._auto_optimization_enabled = True

        # 性能阈值
        self._memory_threshold_mb = 500.0
        self._cpu_threshold_percent = 80.0
        self._response_time_threshold_ms = 200.0
        self._render_time_threshold_ms = 100.0

        # 统计信息
        self._optimization_count = 0
        self._last_optimization_time: Optional[datetime] = None

        # 初始化优化规则
        self._setup_optimization_rules()

        # 启动监控线程
        self._start_monitoring()

        self._logger.debug("TTK性能优化器初始化完成")

    def _setup_optimization_rules(self) -> None:
        """设置优化规则"""
        # 内存优化规则
        self._optimization_rules.append(
            OptimizationRule(
                name="memory_cleanup",
                condition=lambda m: m.memory_usage_mb > self._memory_threshold_mb,
                action=self._optimize_memory,
                priority=1,
                cooldown_seconds=30,
                description="内存使用过高时执行内存清理",
            )
        )

        # 缓存优化规则
        self._optimization_rules.append(
            OptimizationRule(
                name="cache_optimization",
                condition=lambda m: m.cache_hit_rate < 50.0 and m.cache_size_mb > 50.0,
                action=self._optimize_cache,
                priority=2,
                cooldown_seconds=60,
                description="缓存命中率低时优化缓存策略",
            )
        )

        # UI响应优化规则
        self._optimization_rules.append(
            OptimizationRule(
                name="ui_response_optimization",
                condition=lambda m: m.ui_response_time_ms
                > self._response_time_threshold_ms,
                action=self._optimize_ui_response,
                priority=1,
                cooldown_seconds=45,
                description="UI响应时间过长时优化响应性",
            )
        )

        # 渲染优化规则
        self._optimization_rules.append(
            OptimizationRule(
                name="render_optimization",
                condition=lambda m: m.render_time_ms > self._render_time_threshold_ms,
                action=self._optimize_rendering,
                priority=2,
                cooldown_seconds=30,
                description="渲染时间过长时优化渲染性能",
            )
        )

        # 垃圾回收规则
        self._optimization_rules.append(
            OptimizationRule(
                name="garbage_collection",
                condition=lambda m: len(self._metrics_history) > 0
                and len(self._metrics_history) % 20 == 0,  # 每20次监控执行一次
                action=self._perform_garbage_collection,
                priority=3,
                cooldown_seconds=120,
                description="定期执行垃圾回收",
            )
        )

    def register_widget(self, widget: tk.Widget, widget_name: str = "") -> None:
        """注册需要监控的组件

        Args:
            widget: 要监控的组件
            widget_name: 组件名称
        """
        try:
            self._tracked_widgets.add(widget)

            # 如果是虚拟滚动组件,特别跟踪
            if isinstance(widget, VirtualScrollMixin):
                self._virtual_scroll_components.add(widget)

            self._logger.debug(f"注册组件: {widget_name or widget.__class__.__name__}")

        except Exception as e:
            self._logger.error(f"注册组件失败: {e}")

    def track_render_time(self, component_name: str, render_time_ms: float) -> None:
        """跟踪组件渲染时间

        Args:
            component_name: 组件名称
            render_time_ms: 渲染时间(毫秒)
        """
        try:
            if component_name not in self._render_times:
                self._render_times[component_name] = []

            self._render_times[component_name].append(render_time_ms)

            # 限制历史记录大小
            if len(self._render_times[component_name]) > 100:
                self._render_times[component_name] = self._render_times[component_name][
                    -100:
                ]

            # 如果渲染时间过长,记录警告
            if render_time_ms > self._render_time_threshold_ms:
                self._logger.warning(
                    f"组件 {component_name} 渲染时间过长: {render_time_ms:.2f}ms"
                )

        except Exception as e:
            self._logger.error(f"跟踪渲染时间失败: {e}")

    def _start_monitoring(self) -> None:
        """启动性能监控"""

        def monitor_loop():
            while self._monitoring_enabled:
                try:
                    # 收集性能指标
                    metrics = self._collect_metrics()

                    # 添加到历史记录
                    self._metrics_history.append(metrics)

                    # 限制历史记录大小
                    if len(self._metrics_history) > self._max_history_size:
                        self._metrics_history = self._metrics_history[
                            -self._max_history_size :
                        ]

                    # 执行自动优化
                    if self._auto_optimization_enabled:
                        self._execute_optimization_rules(metrics)

                except Exception as e:
                    self._logger.error(f"性能监控失败: {e}")

                # 等待下次监控
                time.sleep(self._monitoring_interval)

        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        self._logger.info("性能监控已启动")

    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        try:
            # 系统指标
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / 1024 / 1024
            cpu_usage_percent = process.cpu_percent()

            # UI指标
            active_widgets = len(self._tracked_widgets)
            virtual_scroll_items = sum(
                len(getattr(comp, "_virtual_state", {}).get("rendered_items", {}))
                for comp in self._virtual_scroll_components
                if hasattr(comp, "_virtual_state")
            )

            # 异步任务指标
            async_stats = self._async_processor.get_statistics()
            async_tasks_running = async_stats.get("running_tasks", 0)

            # 缓存指标
            cache_stats = self._cache_manager.get_statistics()
            cache_hit_rate = cache_stats.hit_rate
            cache_size_mb = cache_stats.memory_usage_mb

            # 渲染时间指标
            avg_render_time_ms = 0.0
            if self._render_times:
                all_times = []
                for times in self._render_times.values():
                    all_times.extend(times[-10:])  # 最近10次
                if all_times:
                    avg_render_time_ms = sum(all_times) / len(all_times)

            # UI响应时间(简化测量)
            ui_response_time_ms = self._measure_ui_response_time()

            return PerformanceMetrics(
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                ui_response_time_ms=ui_response_time_ms,
                render_time_ms=avg_render_time_ms,
                active_widgets=active_widgets,
                virtual_scroll_items=virtual_scroll_items,
                async_tasks_running=async_tasks_running,
                cache_hit_rate=cache_hit_rate,
                cache_size_mb=cache_size_mb,
            )

        except Exception as e:
            self._logger.error(f"收集性能指标失败: {e}")
            return PerformanceMetrics()

    def _measure_ui_response_time(self) -> float:
        """测量UI响应时间"""
        try:
            # 简化的UI响应时间测量
            # 在实际应用中,可以通过测量事件处理时间来获得更准确的数据
            start_time = time.perf_counter()

            # 模拟UI操作
            root = tk._default_root
            if root:
                root.update_idletasks()

            end_time = time.perf_counter()
            return (end_time - start_time) * 1000  # 转换为毫秒

        except Exception:
            return 0.0

    def _execute_optimization_rules(self, metrics: PerformanceMetrics) -> None:
        """执行优化规则"""
        try:
            current_time = datetime.now()

            for rule in self._optimization_rules:
                # 检查冷却时间
                if rule.last_executed and current_time - rule.last_executed < timedelta(
                    seconds=rule.cooldown_seconds
                ):
                    continue

                # 检查条件
                if rule.condition(metrics):
                    try:
                        # 执行优化动作
                        rule.action()
                        rule.last_executed = current_time
                        self._optimization_count += 1
                        self._last_optimization_time = current_time

                        self._logger.info(
                            f"执行优化规则: {rule.name} - {rule.description}"
                        )

                    except Exception as e:
                        self._logger.error(f"执行优化规则失败: {rule.name}, 错误: {e}")

        except Exception as e:
            self._logger.error(f"执行优化规则失败: {e}")

    def _optimize_memory(self) -> None:
        """优化内存使用"""
        try:
            # 清理缓存
            self._cache_manager.optimize()

            # 清理组件引用
            # WeakSet会自动清理无效引用
            list(self._tracked_widgets)
            list(self._virtual_scroll_components)

            # 清理渲染时间历史
            for component_name in list(self._render_times.keys()):
                if len(self._render_times[component_name]) > 50:
                    self._render_times[component_name] = self._render_times[
                        component_name
                    ][-50:]

            # 执行垃圾回收
            gc.collect()

            self._logger.debug("内存优化完成")

        except Exception as e:
            self._logger.error(f"内存优化失败: {e}")

    def _optimize_cache(self) -> None:
        """优化缓存策略"""
        try:
            # 优化数据缓存
            self._cache_manager.optimize()

            # 清理过期缓存
            self._cache_manager.clear()

            self._logger.debug("缓存优化完成")

        except Exception as e:
            self._logger.error(f"缓存优化失败: {e}")

    def _optimize_ui_response(self) -> None:
        """优化UI响应性"""
        try:
            # 检查是否有过多的异步任务
            stats = self._async_processor.get_statistics()
            if stats["running_tasks"] > 10:
                # 清理已完成的任务
                self._async_processor.clear_completed_tasks()

            # 优化虚拟滚动组件
            for component in self._virtual_scroll_components:
                if hasattr(component, "_virtual_config"):
                    # 减少缓冲区大小以提高响应性
                    component._virtual_config.buffer_size = min(
                        component._virtual_config.buffer_size, 3
                    )

            self._logger.debug("UI响应优化完成")

        except Exception as e:
            self._logger.error(f"UI响应优化失败: {e}")

    def _optimize_rendering(self) -> None:
        """优化渲染性能"""
        try:
            # 优化虚拟滚动组件的渲染
            for component in self._virtual_scroll_components:
                if hasattr(component, "configure_virtual_scroll"):
                    # 调整虚拟滚动参数以提高渲染性能
                    component.configure_virtual_scroll(
                        buffer_size=2,  # 减少缓冲区
                        enable_smooth_scroll=False,  # 禁用平滑滚动
                    )

            self._logger.debug("渲染优化完成")

        except Exception as e:
            self._logger.error(f"渲染优化失败: {e}")

    def _perform_garbage_collection(self) -> None:
        """执行垃圾回收"""
        try:
            collected = gc.collect()
            self._logger.debug(f"垃圾回收完成,回收对象: {collected} 个")

        except Exception as e:
            self._logger.error(f"垃圾回收失败: {e}")

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告

        Returns:
            Dict[str, Any]: 性能报告
        """
        try:
            if not self._metrics_history:
                return {"error": "暂无性能数据"}

            # 计算统计信息
            recent_metrics = self._metrics_history[-10:]  # 最近10次

            avg_memory = sum(m.memory_usage_mb for m in recent_metrics) / len(
                recent_metrics
            )
            avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(
                recent_metrics
            )
            avg_response_time = sum(
                m.ui_response_time_ms for m in recent_metrics
            ) / len(recent_metrics)
            avg_render_time = sum(m.render_time_ms for m in recent_metrics) / len(
                recent_metrics
            )

            # 性能趋势
            if len(self._metrics_history) >= 2:
                memory_trend = (
                    "上升"
                    if recent_metrics[-1].memory_usage_mb
                    > recent_metrics[0].memory_usage_mb
                    else "下降"
                )
                response_trend = (
                    "上升"
                    if recent_metrics[-1].ui_response_time_ms
                    > recent_metrics[0].ui_response_time_ms
                    else "下降"
                )
            else:
                memory_trend = "稳定"
                response_trend = "稳定"

            # 组件统计
            component_stats = {
                "tracked_widgets": len(self._tracked_widgets),
                "virtual_scroll_components": len(self._virtual_scroll_components),
                "render_time_records": sum(
                    len(times) for times in self._render_times.values()
                ),
            }

            # 异步任务统计
            async_stats = self._async_processor.get_statistics()

            # 缓存统计
            cache_stats = self._cache_manager.get_statistics()

            return {
                "timestamp": datetime.now().isoformat(),
                "performance_summary": {
                    "avg_memory_mb": round(avg_memory, 2),
                    "avg_cpu_percent": round(avg_cpu, 2),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "avg_render_time_ms": round(avg_render_time, 2),
                    "memory_trend": memory_trend,
                    "response_trend": response_trend,
                },
                "component_statistics": component_stats,
                "async_task_statistics": async_stats,
                "cache_statistics": {
                    "hit_rate": cache_stats.hit_rate,
                    "memory_usage_mb": cache_stats.memory_usage_mb,
                    "total_entries": cache_stats.total_entries,
                },
                "optimization_statistics": {
                    "optimization_count": self._optimization_count,
                    "last_optimization": self._last_optimization_time.isoformat()
                    if self._last_optimization_time
                    else None,
                    "auto_optimization_enabled": self._auto_optimization_enabled,
                },
                "thresholds": {
                    "memory_threshold_mb": self._memory_threshold_mb,
                    "cpu_threshold_percent": self._cpu_threshold_percent,
                    "response_time_threshold_ms": self._response_time_threshold_ms,
                    "render_time_threshold_ms": self._render_time_threshold_ms,
                },
            }

        except Exception as e:
            self._logger.error(f"获取性能报告失败: {e}")
            return {"error": str(e)}

    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取优化建议

        Returns:
            List[Dict[str, Any]]: 优化建议列表
        """
        suggestions = []

        try:
            if not self._metrics_history:
                return suggestions

            latest_metrics = self._metrics_history[-1]

            # 内存优化建议
            if latest_metrics.memory_usage_mb > self._memory_threshold_mb:
                suggestions.append(
                    {
                        "category": "memory",
                        "priority": "high",
                        "title": "内存使用过高",
                        "description": f"当前内存使用: {latest_metrics.memory_usage_mb:.1f}MB,超过阈值 {self._memory_threshold_mb}MB",
                        "actions": [
                            "执行内存清理",
                            "优化数据缓存",
                            "减少同时显示的组件数量",
                        ],
                    }
                )

            # UI响应优化建议
            if latest_metrics.ui_response_time_ms > self._response_time_threshold_ms:
                suggestions.append(
                    {
                        "category": "ui_response",
                        "priority": "high",
                        "title": "UI响应时间过长",
                        "description": f"当前响应时间: {latest_metrics.ui_response_time_ms:.1f}ms,超过阈值 {self._response_time_threshold_ms}ms",
                        "actions": [
                            "启用异步处理",
                            "优化虚拟滚动配置",
                            "减少UI更新频率",
                        ],
                    }
                )

            # 渲染性能建议
            if latest_metrics.render_time_ms > self._render_time_threshold_ms:
                suggestions.append(
                    {
                        "category": "rendering",
                        "priority": "medium",
                        "title": "渲染性能需要优化",
                        "description": f"平均渲染时间: {latest_metrics.render_time_ms:.1f}ms,超过阈值 {self._render_time_threshold_ms}ms",
                        "actions": [
                            "启用虚拟滚动",
                            "优化组件渲染逻辑",
                            "使用缓存减少重复渲染",
                        ],
                    }
                )

            # 缓存优化建议
            if latest_metrics.cache_hit_rate < 70.0:
                suggestions.append(
                    {
                        "category": "caching",
                        "priority": "medium",
                        "title": "缓存命中率较低",
                        "description": f"当前缓存命中率: {latest_metrics.cache_hit_rate:.1f}%,建议优化缓存策略",
                        "actions": ["调整缓存大小", "优化缓存键设计", "实现预加载机制"],
                    }
                )

            # 异步任务建议
            if latest_metrics.async_tasks_running > 10:
                suggestions.append(
                    {
                        "category": "async_tasks",
                        "priority": "low",
                        "title": "异步任务数量较多",
                        "description": f"当前运行任务: {latest_metrics.async_tasks_running} 个,可能影响性能",
                        "actions": [
                            "限制并发任务数量",
                            "优化任务执行顺序",
                            "清理已完成的任务",
                        ],
                    }
                )

            # 如果没有问题,给出积极建议
            if not suggestions:
                suggestions.append(
                    {
                        "category": "general",
                        "priority": "info",
                        "title": "性能表现良好",
                        "description": "当前系统性能指标均在正常范围内",
                        "actions": [
                            "继续保持当前优化策略",
                            "定期监控性能指标",
                            "考虑进一步的性能优化",
                        ],
                    }
                )

        except Exception as e:
            self._logger.error(f"获取优化建议失败: {e}")
            suggestions.append(
                {
                    "category": "error",
                    "priority": "high",
                    "title": "性能分析异常",
                    "description": f"无法分析性能数据: {e!s}",
                    "actions": ["检查系统状态", "重启性能监控"],
                }
            )

        return suggestions

    def configure_thresholds(
        self,
        memory_threshold_mb: Optional[float] = None,
        cpu_threshold_percent: Optional[float] = None,
        response_time_threshold_ms: Optional[float] = None,
        render_time_threshold_ms: Optional[float] = None,
    ) -> None:
        """配置性能阈值

        Args:
            memory_threshold_mb: 内存阈值(MB)
            cpu_threshold_percent: CPU阈值(百分比)
            response_time_threshold_ms: 响应时间阈值(毫秒)
            render_time_threshold_ms: 渲染时间阈值(毫秒)
        """
        if memory_threshold_mb is not None:
            self._memory_threshold_mb = memory_threshold_mb

        if cpu_threshold_percent is not None:
            self._cpu_threshold_percent = cpu_threshold_percent

        if response_time_threshold_ms is not None:
            self._response_time_threshold_ms = response_time_threshold_ms

        if render_time_threshold_ms is not None:
            self._render_time_threshold_ms = render_time_threshold_ms

        self._logger.info("性能阈值已更新")

    def enable_auto_optimization(self, enabled: bool = True) -> None:
        """启用/禁用自动优化

        Args:
            enabled: 是否启用自动优化
        """
        self._auto_optimization_enabled = enabled
        self._logger.info(f"自动优化已{'启用' if enabled else '禁用'}")

    def manual_optimize(self) -> Dict[str, Any]:
        """手动执行优化

        Returns:
            Dict[str, Any]: 优化结果
        """
        try:
            start_time = time.time()

            # 执行所有优化动作
            self._optimize_memory()
            self._optimize_cache()
            self._optimize_ui_response()
            self._optimize_rendering()
            self._perform_garbage_collection()

            end_time = time.time()

            self._optimization_count += 1
            self._last_optimization_time = datetime.now()

            result = {
                "success": True,
                "optimization_time": round((end_time - start_time) * 1000, 2),  # 毫秒
                "optimizations_performed": [
                    "内存清理",
                    "缓存优化",
                    "UI响应优化",
                    "渲染优化",
                    "垃圾回收",
                ],
                "timestamp": self._last_optimization_time.isoformat(),
            }

            self._logger.info(f"手动优化完成,耗时: {result['optimization_time']}ms")
            return result

        except Exception as e:
            self._logger.error(f"手动优化失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def stop_monitoring(self) -> None:
        """停止性能监控"""
        self._monitoring_enabled = False
        self._logger.info("性能监控已停止")

    def start_monitoring(self) -> None:
        """启动性能监控"""
        if not self._monitoring_enabled:
            self._monitoring_enabled = True
            self._start_monitoring()


# 全局TTK性能优化器实例
ttk_performance_optimizer = TTKPerformanceOptimizer()
