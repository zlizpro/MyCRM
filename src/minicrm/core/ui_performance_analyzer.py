"""
MiniCRM UI性能分析器

专门用于UI操作响应时间监控和分析,包括:
- UI操作响应时间统计
- 界面渲染性能监控
- 用户交互延迟分析
- UI组件加载时间监控
- 界面卡顿检测和报告
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class UIOperationMetric:
    """UI操作性能指标"""

    operation_id: str
    operation_type: str  # render, load, click, refresh, etc.
    component_name: str
    response_time: float = 0.0  # 毫秒
    render_time: float = 0.0  # 毫秒
    data_load_time: float = 0.0  # 毫秒
    user_wait_time: float = 0.0  # 毫秒
    timestamp: datetime = field(default_factory=datetime.now)
    is_slow_operation: bool = False
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UIComponentMetric:
    """UI组件性能指标"""

    component_name: str
    component_type: str  # panel, dialog, widget, etc.
    total_operations: int = 0
    avg_response_time: float = 0.0  # 毫秒
    max_response_time: float = 0.0  # 毫秒
    min_response_time: float = 0.0  # 毫秒
    slow_operations_count: int = 0
    error_operations_count: int = 0
    last_operation_time: datetime | None = None


class UIPerformanceAnalyzer:
    """
    UI性能分析器

    提供全面的UI性能监控和分析功能,包括响应时间统计、
    渲染性能监控、用户交互延迟分析等.
    """

    def __init__(
        self,
        slow_operation_threshold: float = 500.0,
        render_threshold: float = 100.0,
        data_load_threshold: float = 1000.0,
    ):
        """
        初始化UI性能分析器

        Args:
            slow_operation_threshold: 慢操作阈值(毫秒),默认500ms
            render_threshold: 渲染阈值(毫秒),默认100ms
            data_load_threshold: 数据加载阈值(毫秒),默认1000ms
        """
        self._logger = logging.getLogger(__name__)
        self._slow_operation_threshold = slow_operation_threshold
        self._render_threshold = render_threshold
        self._data_load_threshold = data_load_threshold

        self._operation_metrics: list[UIOperationMetric] = []
        self._component_metrics: dict[str, UIComponentMetric] = {}
        self._operation_patterns: dict[str, list[UIOperationMetric]] = defaultdict(list)
        self._enabled = True
        self._max_metrics = 3000  # 最大保存的操作指标数量

        self._logger.debug("UI性能分析器初始化完成")

    def enable(self) -> None:
        """启用UI性能分析"""
        self._enabled = True
        self._logger.info("UI性能分析已启用")

    def disable(self) -> None:
        """禁用UI性能分析"""
        self._enabled = False
        self._logger.info("UI性能分析已禁用")

    def is_enabled(self) -> bool:
        """检查是否启用了UI性能分析"""
        return self._enabled

    def record_operation(
        self,
        operation_type: str,
        component_name: str,
        response_time: float = 0.0,
        render_time: float = 0.0,
        data_load_time: float = 0.0,
        user_wait_time: float = 0.0,
        error_message: str | None = None,
        **metadata,
    ) -> str:
        """
        记录UI操作性能指标

        Args:
            operation_type: 操作类型
            component_name: 组件名称
            response_time: 响应时间(毫秒)
            render_time: 渲染时间(毫秒)
            data_load_time: 数据加载时间(毫秒)
            user_wait_time: 用户等待时间(毫秒)
            error_message: 错误信息
            **metadata: 额外的元数据

        Returns:
            str: 操作ID
        """
        if not self._enabled:
            return ""

        try:
            # 生成操作ID
            operation_id = self._generate_operation_id(operation_type, component_name)

            # 检查是否为慢操作
            is_slow_operation = (
                response_time >= self._slow_operation_threshold
                or render_time >= self._render_threshold
                or data_load_time >= self._data_load_threshold
            )

            # 创建操作指标
            metric = UIOperationMetric(
                operation_id=operation_id,
                operation_type=operation_type,
                component_name=component_name,
                response_time=response_time,
                render_time=render_time,
                data_load_time=data_load_time,
                user_wait_time=user_wait_time,
                is_slow_operation=is_slow_operation,
                error_message=error_message,
                metadata=metadata,
            )

            # 保存指标
            self._add_operation_metric(metric)

            # 更新组件统计
            self._update_component_metrics(metric)

            # 记录慢操作日志
            if is_slow_operation:
                self._logger.warning(
                    f"慢UI操作检测 [{operation_id}]: "
                    f"响应时间 {response_time:.2f}ms, "
                    f"渲染时间 {render_time:.2f}ms, "
                    f"数据加载时间 {data_load_time:.2f}ms - "
                    f"{component_name}.{operation_type}"
                )

            return operation_id

        except Exception as e:
            self._logger.error(f"记录UI操作指标失败: {e}")
            return ""

    def start_operation_timing(self, operation_type: str, component_name: str) -> str:
        """
        开始UI操作计时

        Args:
            operation_type: 操作类型
            component_name: 组件名称

        Returns:
            str: 计时ID
        """
        timing_id = f"{component_name}_{operation_type}_{time.time()}"

        # 存储开始时间
        if not hasattr(self, "_timing_data"):
            self._timing_data = {}

        self._timing_data[timing_id] = {
            "start_time": time.perf_counter(),
            "operation_type": operation_type,
            "component_name": component_name,
        }

        return timing_id

    def end_operation_timing(
        self,
        timing_id: str,
        render_time: float = 0.0,
        data_load_time: float = 0.0,
        error_message: str | None = None,
        **metadata,
    ) -> str | None:
        """
        结束UI操作计时并记录指标

        Args:
            timing_id: 计时ID
            render_time: 渲染时间(毫秒)
            data_load_time: 数据加载时间(毫秒)
            error_message: 错误信息
            **metadata: 额外的元数据

        Returns:
            Optional[str]: 操作ID
        """
        if not hasattr(self, "_timing_data") or timing_id not in self._timing_data:
            self._logger.warning(f"未找到计时数据: {timing_id}")
            return None

        try:
            timing_data = self._timing_data[timing_id]
            end_time = time.perf_counter()

            # 计算总响应时间
            response_time = (end_time - timing_data["start_time"]) * 1000

            # 计算用户等待时间(总时间减去渲染和数据加载时间)
            user_wait_time = max(0, response_time - render_time - data_load_time)

            # 记录操作指标
            operation_id = self.record_operation(
                operation_type=timing_data["operation_type"],
                component_name=timing_data["component_name"],
                response_time=response_time,
                render_time=render_time,
                data_load_time=data_load_time,
                user_wait_time=user_wait_time,
                error_message=error_message,
                **metadata,
            )

            # 清理计时数据
            del self._timing_data[timing_id]

            return operation_id

        except Exception as e:
            self._logger.error(f"结束UI操作计时失败: {e}")
            return None

    def get_slow_operations(
        self, limit: int = 50, time_range: timedelta | None = None
    ) -> list[UIOperationMetric]:
        """
        获取慢操作列表

        Args:
            limit: 返回数量限制
            time_range: 时间范围过滤

        Returns:
            List[UIOperationMetric]: 慢操作列表
        """
        slow_operations = [m for m in self._operation_metrics if m.is_slow_operation]

        # 时间范围过滤
        if time_range:
            cutoff_time = datetime.now() - time_range
            slow_operations = [
                op for op in slow_operations if op.timestamp >= cutoff_time
            ]

        # 按响应时间倒序排列
        slow_operations.sort(key=lambda op: op.response_time, reverse=True)

        return slow_operations[:limit]

    def get_component_statistics(
        self, component_name: str | None = None
    ) -> dict[str, Any]:
        """
        获取组件性能统计

        Args:
            component_name: 组件名称过滤

        Returns:
            Dict[str, Any]: 组件性能统计
        """
        if component_name:
            if component_name in self._component_metrics:
                metric = self._component_metrics[component_name]
                return {
                    "component_name": metric.component_name,
                    "component_type": metric.component_type,
                    "total_operations": metric.total_operations,
                    "avg_response_time_ms": metric.avg_response_time,
                    "max_response_time_ms": metric.max_response_time,
                    "min_response_time_ms": metric.min_response_time,
                    "slow_operations_count": metric.slow_operations_count,
                    "error_operations_count": metric.error_operations_count,
                    "slow_operation_percentage": (
                        (metric.slow_operations_count / metric.total_operations) * 100
                        if metric.total_operations > 0
                        else 0
                    ),
                    "last_operation_time": (
                        metric.last_operation_time.isoformat()
                        if metric.last_operation_time
                        else None
                    ),
                }
            else:
                return {"error": f"组件 {component_name} 未找到"}

        # 返回所有组件的统计
        all_stats = {}
        for name, metric in self._component_metrics.items():
            all_stats[name] = {
                "total_operations": metric.total_operations,
                "avg_response_time_ms": metric.avg_response_time,
                "slow_operations_count": metric.slow_operations_count,
                "error_operations_count": metric.error_operations_count,
            }

        return all_stats

    def get_operation_statistics(
        self, operation_type: str | None = None
    ) -> dict[str, Any]:
        """
        获取操作类型统计

        Args:
            operation_type: 操作类型过滤

        Returns:
            Dict[str, Any]: 操作统计信息
        """
        metrics = self._operation_metrics

        # 应用过滤条件
        if operation_type:
            metrics = [m for m in metrics if m.operation_type == operation_type]

        if not metrics:
            return {
                "total_operations": 0,
                "avg_response_time_ms": 0.0,
                "avg_render_time_ms": 0.0,
                "avg_data_load_time_ms": 0.0,
                "slow_operations_count": 0,
                "error_operations_count": 0,
            }

        response_times = [m.response_time for m in metrics]
        render_times = [m.render_time for m in metrics if m.render_time > 0]
        data_load_times = [m.data_load_time for m in metrics if m.data_load_time > 0]
        slow_operations = [m for m in metrics if m.is_slow_operation]
        error_operations = [m for m in metrics if m.error_message]

        return {
            "total_operations": len(metrics),
            "avg_response_time_ms": sum(response_times) / len(response_times),
            "max_response_time_ms": max(response_times),
            "min_response_time_ms": min(response_times),
            "avg_render_time_ms": (
                sum(render_times) / len(render_times) if render_times else 0.0
            ),
            "avg_data_load_time_ms": (
                sum(data_load_times) / len(data_load_times) if data_load_times else 0.0
            ),
            "slow_operations_count": len(slow_operations),
            "error_operations_count": len(error_operations),
            "slow_operation_percentage": (len(slow_operations) / len(metrics)) * 100,
        }

    def detect_ui_lag(self, threshold: float = 100.0) -> list[dict[str, Any]]:
        """
        检测UI卡顿

        Args:
            threshold: 卡顿阈值(毫秒)

        Returns:
            List[Dict[str, Any]]: 卡顿检测结果
        """
        lag_events = []

        for metric in self._operation_metrics:
            # 检测渲染卡顿
            if metric.render_time > threshold:
                lag_events.append(
                    {
                        "type": "render_lag",
                        "component": metric.component_name,
                        "operation": metric.operation_type,
                        "duration_ms": metric.render_time,
                        "timestamp": metric.timestamp.isoformat(),
                    }
                )

            # 检测数据加载卡顿
            if metric.data_load_time > threshold * 2:  # 数据加载阈值更高
                lag_events.append(
                    {
                        "type": "data_load_lag",
                        "component": metric.component_name,
                        "operation": metric.operation_type,
                        "duration_ms": metric.data_load_time,
                        "timestamp": metric.timestamp.isoformat(),
                    }
                )

            # 检测总体响应卡顿
            if metric.response_time > threshold * 3:  # 总响应时间阈值最高
                lag_events.append(
                    {
                        "type": "response_lag",
                        "component": metric.component_name,
                        "operation": metric.operation_type,
                        "duration_ms": metric.response_time,
                        "timestamp": metric.timestamp.isoformat(),
                    }
                )

        # 按时间排序
        lag_events.sort(key=lambda x: x["timestamp"], reverse=True)

        return lag_events

    def generate_performance_report(self) -> dict[str, Any]:
        """
        生成UI性能报告

        Returns:
            Dict[str, Any]: 完整的UI性能报告
        """
        try:
            # 基础统计
            overall_stats = self.get_operation_statistics()
            component_stats = self.get_component_statistics()

            # 慢操作分析
            slow_operations = self.get_slow_operations(limit=10)
            slow_operation_summary = [
                {
                    "operation_id": op.operation_id,
                    "component": op.component_name,
                    "operation_type": op.operation_type,
                    "response_time_ms": op.response_time,
                    "render_time_ms": op.render_time,
                    "data_load_time_ms": op.data_load_time,
                    "timestamp": op.timestamp.isoformat(),
                }
                for op in slow_operations
            ]

            # 卡顿检测
            lag_events = self.detect_ui_lag()

            # 性能建议
            recommendations = self._generate_performance_recommendations(overall_stats)

            return {
                "report_timestamp": datetime.now().isoformat(),
                "overall_statistics": overall_stats,
                "component_statistics": component_stats,
                "slow_operations": slow_operation_summary,
                "lag_events": lag_events[:20],  # 最近20个卡顿事件
                "recommendations": recommendations,
                "analyzer_config": {
                    "slow_operation_threshold_ms": self._slow_operation_threshold,
                    "render_threshold_ms": self._render_threshold,
                    "data_load_threshold_ms": self._data_load_threshold,
                    "enabled": self._enabled,
                },
            }

        except Exception as e:
            self._logger.error(f"生成UI性能报告失败: {e}")
            return {"error": str(e)}

    def _add_operation_metric(self, metric: UIOperationMetric) -> None:
        """添加操作指标"""
        self._operation_metrics.append(metric)

        # 按操作模式分组
        pattern = f"{metric.component_name}.{metric.operation_type}"
        self._operation_patterns[pattern].append(metric)

        # 限制指标数量
        if len(self._operation_metrics) > self._max_metrics:
            # 删除最旧的指标
            self._operation_metrics = sorted(
                self._operation_metrics, key=lambda m: m.timestamp, reverse=True
            )[: self._max_metrics]

    def _update_component_metrics(self, metric: UIOperationMetric) -> None:
        """更新组件统计指标"""
        component_name = metric.component_name

        if component_name not in self._component_metrics:
            self._component_metrics[component_name] = UIComponentMetric(
                component_name=component_name,
                component_type=metric.metadata.get("component_type", "unknown"),
            )

        comp_metric = self._component_metrics[component_name]
        comp_metric.total_operations += 1
        comp_metric.last_operation_time = metric.timestamp

        # 更新响应时间统计
        if comp_metric.total_operations == 1:
            comp_metric.avg_response_time = metric.response_time
            comp_metric.max_response_time = metric.response_time
            comp_metric.min_response_time = metric.response_time
        else:
            # 计算新的平均值
            total_time = (
                comp_metric.avg_response_time * (comp_metric.total_operations - 1)
                + metric.response_time
            )
            comp_metric.avg_response_time = total_time / comp_metric.total_operations
            comp_metric.max_response_time = max(
                comp_metric.max_response_time, metric.response_time
            )
            comp_metric.min_response_time = min(
                comp_metric.min_response_time, metric.response_time
            )

        # 更新慢操作和错误计数
        if metric.is_slow_operation:
            comp_metric.slow_operations_count += 1
        if metric.error_message:
            comp_metric.error_operations_count += 1

    def _generate_operation_id(self, operation_type: str, component_name: str) -> str:
        """生成操作ID"""
        import hashlib

        content = f"{component_name}_{operation_type}_{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _generate_performance_recommendations(self, stats: dict[str, Any]) -> list[str]:
        """生成UI性能优化建议"""
        recommendations = []

        try:
            # 慢操作建议
            if stats.get("slow_operation_percentage", 0) > 15:
                recommendations.append(
                    f"慢UI操作比例较高({stats['slow_operation_percentage']:.1f}%),"
                    "建议优化界面渲染或使用异步加载"
                )

            # 平均响应时间建议
            avg_response = stats.get("avg_response_time_ms", 0)
            if avg_response > 300:
                recommendations.append(
                    f"平均UI响应时间较长({avg_response:.1f}ms),建议优化界面逻辑"
                )

            # 渲染时间建议
            avg_render = stats.get("avg_render_time_ms", 0)
            if avg_render > 50:
                recommendations.append(
                    f"平均渲染时间较长({avg_render:.1f}ms),建议优化界面绘制"
                )

            # 数据加载时间建议
            avg_data_load = stats.get("avg_data_load_time_ms", 0)
            if avg_data_load > 500:
                recommendations.append(
                    f"平均数据加载时间较长({avg_data_load:.1f}ms),建议使用缓存或分页"
                )

            # 错误操作建议
            error_count = stats.get("error_operations_count", 0)
            if error_count > 0:
                recommendations.append(
                    f"发现{error_count}个UI操作错误,建议检查异常处理"
                )

            if not recommendations:
                recommendations.append("UI性能表现良好")

        except Exception as e:
            self._logger.warning(f"生成UI性能建议时出错: {e}")
            recommendations.append("UI性能分析出现异常,建议检查监控数据")

        return recommendations

    def clear_metrics(self) -> None:
        """清空所有性能指标"""
        self._operation_metrics.clear()
        self._component_metrics.clear()
        self._operation_patterns.clear()
        if hasattr(self, "_timing_data"):
            self._timing_data.clear()
        self._logger.info("UI性能指标已清空")


# 全局UI性能分析器实例
ui_performance_analyzer = UIPerformanceAnalyzer()
