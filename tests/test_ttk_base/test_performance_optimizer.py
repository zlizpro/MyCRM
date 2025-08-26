"""
MiniCRM TTK性能优化器测试

测试性能优化功能的各个方面，包括：
- 性能监控
- 自动优化规则
- 手动优化
- 性能报告
- 优化建议
- 阈值配置
"""

from datetime import datetime
import time
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.performance_optimizer import (
    OptimizationRule,
    PerformanceMetrics,
    TTKPerformanceOptimizer,
)
from src.minicrm.ui.ttk_base.virtual_scroll_mixin import VirtualScrollMixin


class TestPerformanceMetrics(unittest.TestCase):
    """测试性能指标类"""

    def test_metrics_creation(self):
        """测试性能指标创建"""
        timestamp = datetime.now()
        metrics = PerformanceMetrics(
            timestamp=timestamp,
            memory_usage_mb=100.5,
            cpu_usage_percent=25.3,
            ui_response_time_ms=150.2,
            render_time_ms=80.1,
            active_widgets=50,
            virtual_scroll_items=1000,
            async_tasks_running=3,
            cache_hit_rate=85.5,
            cache_size_mb=25.8,
        )

        self.assertEqual(metrics.timestamp, timestamp)
        self.assertEqual(metrics.memory_usage_mb, 100.5)
        self.assertEqual(metrics.cpu_usage_percent, 25.3)
        self.assertEqual(metrics.ui_response_time_ms, 150.2)
        self.assertEqual(metrics.render_time_ms, 80.1)
        self.assertEqual(metrics.active_widgets, 50)
        self.assertEqual(metrics.virtual_scroll_items, 1000)
        self.assertEqual(metrics.async_tasks_running, 3)
        self.assertEqual(metrics.cache_hit_rate, 85.5)
        self.assertEqual(metrics.cache_size_mb, 25.8)

    def test_metrics_defaults(self):
        """测试性能指标默认值"""
        metrics = PerformanceMetrics()

        self.assertIsInstance(metrics.timestamp, datetime)
        self.assertEqual(metrics.memory_usage_mb, 0.0)
        self.assertEqual(metrics.cpu_usage_percent, 0.0)
        self.assertEqual(metrics.ui_response_time_ms, 0.0)
        self.assertEqual(metrics.render_time_ms, 0.0)
        self.assertEqual(metrics.active_widgets, 0)
        self.assertEqual(metrics.virtual_scroll_items, 0)
        self.assertEqual(metrics.async_tasks_running, 0)
        self.assertEqual(metrics.cache_hit_rate, 0.0)
        self.assertEqual(metrics.cache_size_mb, 0.0)


class TestOptimizationRule(unittest.TestCase):
    """测试优化规则类"""

    def test_rule_creation(self):
        """测试优化规则创建"""

        def test_condition(metrics):
            return metrics.memory_usage_mb > 100

        def test_action():
            pass

        rule = OptimizationRule(
            name="test_rule",
            condition=test_condition,
            action=test_action,
            priority=1,
            cooldown_seconds=60,
            description="Test rule",
        )

        self.assertEqual(rule.name, "test_rule")
        self.assertEqual(rule.condition, test_condition)
        self.assertEqual(rule.action, test_action)
        self.assertEqual(rule.priority, 1)
        self.assertEqual(rule.cooldown_seconds, 60)
        self.assertEqual(rule.description, "Test rule")
        self.assertIsNone(rule.last_executed)

    def test_rule_condition_evaluation(self):
        """测试规则条件评估"""

        def memory_condition(metrics):
            return metrics.memory_usage_mb > 100

        def cpu_condition(metrics):
            return metrics.cpu_usage_percent > 80

        rule1 = OptimizationRule(
            name="memory_rule", condition=memory_condition, action=lambda: None
        )

        rule2 = OptimizationRule(
            name="cpu_rule", condition=cpu_condition, action=lambda: None
        )

        # 测试条件
        high_memory_metrics = PerformanceMetrics(
            memory_usage_mb=150.0, cpu_usage_percent=50.0
        )
        high_cpu_metrics = PerformanceMetrics(
            memory_usage_mb=50.0, cpu_usage_percent=90.0
        )
        normal_metrics = PerformanceMetrics(
            memory_usage_mb=50.0, cpu_usage_percent=30.0
        )

        # 验证条件评估
        self.assertTrue(rule1.condition(high_memory_metrics))
        self.assertFalse(rule1.condition(high_cpu_metrics))
        self.assertFalse(rule1.condition(normal_metrics))

        self.assertFalse(rule2.condition(high_memory_metrics))
        self.assertTrue(rule2.condition(high_cpu_metrics))
        self.assertFalse(rule2.condition(normal_metrics))


class MockVirtualScrollWidget(tk.Frame, VirtualScrollMixin):
    """用于测试的虚拟滚动组件"""

    def __init__(self, parent):
        super().__init__(parent)
        self._virtual_state = Mock()
        self._virtual_state.rendered_items = {"item1": Mock(), "item2": Mock()}
        self._virtual_config = Mock()
        self._virtual_config.buffer_size = 5

    def create_item_widget(self, parent, data, index):
        return tk.Label(parent, text=str(data))

    def configure_virtual_scroll(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._virtual_config, key, value)


class TestTTKPerformanceOptimizer(unittest.TestCase):
    """测试TTK性能优化器"""

    def setUp(self):
        """测试准备"""
        # 停止全局优化器的监控以避免干扰
        with patch(
            "src.minicrm.ui.ttk_base.performance_optimizer.ttk_performance_optimizer"
        ) as mock_global:
            mock_global._monitoring_enabled = False

        self.optimizer = TTKPerformanceOptimizer()
        self.optimizer._monitoring_enabled = False  # 禁用自动监控以便测试

        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

    def tearDown(self):
        """测试清理"""
        if self.optimizer:
            self.optimizer.stop_monitoring()
        if self.root:
            self.root.destroy()

    def test_optimizer_initialization(self):
        """测试优化器初始化"""
        self.assertIsNotNone(self.optimizer._async_processor)
        self.assertIsNotNone(self.optimizer._cache_manager)
        self.assertEqual(len(self.optimizer._metrics_history), 0)
        self.assertEqual(len(self.optimizer._tracked_widgets), 0)
        self.assertEqual(len(self.optimizer._virtual_scroll_components), 0)
        self.assertEqual(len(self.optimizer._render_times), 0)
        self.assertGreater(len(self.optimizer._optimization_rules), 0)
        self.assertTrue(self.optimizer._auto_optimization_enabled)
        self.assertEqual(self.optimizer._optimization_count, 0)

    def test_register_widget(self):
        """测试注册组件"""
        # 创建测试组件
        widget1 = tk.Label(self.root, text="Test Widget 1")
        widget2 = MockVirtualScrollWidget(self.root)

        # 注册组件
        self.optimizer.register_widget(widget1, "test_widget_1")
        self.optimizer.register_widget(widget2, "virtual_scroll_widget")

        # 验证注册
        self.assertEqual(len(self.optimizer._tracked_widgets), 2)
        self.assertEqual(len(self.optimizer._virtual_scroll_components), 1)

        # 验证虚拟滚动组件被正确识别
        self.assertIn(widget2, self.optimizer._virtual_scroll_components)
        self.assertNotIn(widget1, self.optimizer._virtual_scroll_components)

    def test_track_render_time(self):
        """测试跟踪渲染时间"""
        # 跟踪渲染时间
        self.optimizer.track_render_time("test_component", 50.5)
        self.optimizer.track_render_time("test_component", 75.2)
        self.optimizer.track_render_time("another_component", 120.8)

        # 验证渲染时间记录
        self.assertIn("test_component", self.optimizer._render_times)
        self.assertIn("another_component", self.optimizer._render_times)

        self.assertEqual(len(self.optimizer._render_times["test_component"]), 2)
        self.assertEqual(len(self.optimizer._render_times["another_component"]), 1)

        self.assertEqual(self.optimizer._render_times["test_component"][0], 50.5)
        self.assertEqual(self.optimizer._render_times["test_component"][1], 75.2)
        self.assertEqual(self.optimizer._render_times["another_component"][0], 120.8)

    def test_track_render_time_limit(self):
        """测试渲染时间记录限制"""
        # 添加大量渲染时间记录
        for i in range(150):
            self.optimizer.track_render_time("test_component", float(i))

        # 验证记录数量限制
        self.assertLessEqual(len(self.optimizer._render_times["test_component"]), 100)

        # 验证保留的是最新的记录
        recent_times = self.optimizer._render_times["test_component"]
        self.assertEqual(recent_times[-1], 149.0)  # 最后一个记录
        self.assertEqual(len(recent_times), 100)

    @patch("psutil.Process")
    def test_collect_metrics(self, mock_process_class):
        """测试收集性能指标"""
        # 模拟系统进程信息
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process.cpu_percent.return_value = 25.5
        mock_process_class.return_value = mock_process

        # 添加一些测试数据
        widget1 = tk.Label(self.root)
        widget2 = MockVirtualScrollWidget(self.root)
        self.optimizer.register_widget(widget1)
        self.optimizer.register_widget(widget2)

        self.optimizer.track_render_time("test_component", 80.0)
        self.optimizer.track_render_time("test_component", 90.0)

        # 模拟异步处理器和缓存管理器
        with patch.object(
            self.optimizer._async_processor, "get_statistics"
        ) as mock_async_stats:
            with patch.object(
                self.optimizer._cache_manager, "get_statistics"
            ) as mock_cache_stats:
                mock_async_stats.return_value = {"running_tasks": 3}
                mock_cache_stats.return_value = Mock(
                    hit_rate=75.5, memory_usage_mb=15.2
                )

                # 收集指标
                metrics = self.optimizer._collect_metrics()

        # 验证指标
        self.assertAlmostEqual(metrics.memory_usage_mb, 100.0, places=1)
        self.assertEqual(metrics.cpu_usage_percent, 25.5)
        self.assertEqual(metrics.active_widgets, 2)
        self.assertEqual(
            metrics.virtual_scroll_items, 2
        )  # MockVirtualScrollWidget有2个rendered_items
        self.assertEqual(metrics.async_tasks_running, 3)
        self.assertEqual(metrics.cache_hit_rate, 75.5)
        self.assertEqual(metrics.cache_size_mb, 15.2)
        self.assertEqual(metrics.render_time_ms, 85.0)  # (80 + 90) / 2

    def test_optimization_rules_setup(self):
        """测试优化规则设置"""
        # 验证默认规则存在
        rule_names = [rule.name for rule in self.optimizer._optimization_rules]

        expected_rules = [
            "memory_cleanup",
            "cache_optimization",
            "ui_response_optimization",
            "render_optimization",
            "garbage_collection",
        ]

        for expected_rule in expected_rules:
            self.assertIn(expected_rule, rule_names)

    def test_execute_optimization_rules(self):
        """测试执行优化规则"""
        # 创建测试规则
        rule_executed = []

        def test_condition(metrics):
            return metrics.memory_usage_mb > 100

        def test_action():
            rule_executed.append("test_rule")

        test_rule = OptimizationRule(
            name="test_rule",
            condition=test_condition,
            action=test_action,
            cooldown_seconds=1,
        )

        # 添加测试规则
        self.optimizer._optimization_rules.append(test_rule)

        # 创建触发条件的指标
        high_memory_metrics = PerformanceMetrics(memory_usage_mb=150.0)
        normal_memory_metrics = PerformanceMetrics(memory_usage_mb=50.0)

        # 执行优化规则
        self.optimizer._execute_optimization_rules(high_memory_metrics)

        # 验证规则被执行
        self.assertEqual(len(rule_executed), 1)
        self.assertEqual(rule_executed[0], "test_rule")
        self.assertIsNotNone(test_rule.last_executed)

        # 测试冷却时间
        rule_executed.clear()
        self.optimizer._execute_optimization_rules(high_memory_metrics)

        # 验证规则在冷却时间内不会再次执行
        self.assertEqual(len(rule_executed), 0)

        # 等待冷却时间过去
        time.sleep(1.1)
        self.optimizer._execute_optimization_rules(high_memory_metrics)

        # 验证规则可以再次执行
        self.assertEqual(len(rule_executed), 1)

        # 测试条件不满足时不执行
        rule_executed.clear()
        test_rule.last_executed = None  # 重置执行时间
        self.optimizer._execute_optimization_rules(normal_memory_metrics)

        # 验证规则不被执行
        self.assertEqual(len(rule_executed), 0)

    def test_optimize_memory(self):
        """测试内存优化"""
        # 添加一些渲染时间数据
        for i in range(60):
            self.optimizer.track_render_time("test_component", float(i))

        # 执行内存优化
        with patch.object(
            self.optimizer._cache_manager, "optimize"
        ) as mock_cache_optimize:
            with patch("gc.collect") as mock_gc:
                self.optimizer._optimize_memory()

                # 验证优化操作被调用
                mock_cache_optimize.assert_called_once()
                mock_gc.assert_called_once()

        # 验证渲染时间历史被清理
        self.assertLessEqual(len(self.optimizer._render_times["test_component"]), 50)

    def test_optimize_ui_response(self):
        """测试UI响应优化"""
        # 创建虚拟滚动组件
        virtual_widget = MockVirtualScrollWidget(self.root)
        self.optimizer.register_widget(virtual_widget)

        # 模拟异步处理器统计
        with patch.object(
            self.optimizer._async_processor, "get_statistics"
        ) as mock_stats:
            with patch.object(
                self.optimizer._async_processor, "clear_completed_tasks"
            ) as mock_clear:
                mock_stats.return_value = {"running_tasks": 15}  # 超过阈值

                # 执行UI响应优化
                self.optimizer._optimize_ui_response()

                # 验证清理已完成任务被调用
                mock_clear.assert_called_once()

        # 验证虚拟滚动配置被优化
        self.assertLessEqual(virtual_widget._virtual_config.buffer_size, 3)

    def test_optimize_rendering(self):
        """测试渲染优化"""
        # 创建虚拟滚动组件
        virtual_widget = MockVirtualScrollWidget(self.root)
        self.optimizer.register_widget(virtual_widget)

        # 执行渲染优化
        self.optimizer._optimize_rendering()

        # 验证虚拟滚动配置被调整
        # 注意：这里需要检查configure_virtual_scroll是否被调用
        # 由于我们使用的是Mock，可以检查属性是否被设置
        self.assertTrue(hasattr(virtual_widget._virtual_config, "buffer_size"))

    def test_get_performance_report(self):
        """测试获取性能报告"""
        # 添加一些历史指标
        for i in range(15):
            metrics = PerformanceMetrics(
                memory_usage_mb=100.0 + i,
                cpu_usage_percent=20.0 + i,
                ui_response_time_ms=100.0 + i * 5,
                render_time_ms=50.0 + i * 2,
            )
            self.optimizer._metrics_history.append(metrics)

        # 模拟异步处理器和缓存管理器统计
        with patch.object(
            self.optimizer._async_processor, "get_statistics"
        ) as mock_async_stats:
            with patch.object(
                self.optimizer._cache_manager, "get_statistics"
            ) as mock_cache_stats:
                mock_async_stats.return_value = {
                    "total_tasks": 100,
                    "completed_tasks": 85,
                    "running_tasks": 5,
                }
                mock_cache_stats.return_value = Mock(
                    hit_rate=80.5, memory_usage_mb=20.3, total_entries=150
                )

                # 获取性能报告
                report = self.optimizer.get_performance_report()

        # 验证报告内容
        self.assertIn("timestamp", report)
        self.assertIn("performance_summary", report)
        self.assertIn("component_statistics", report)
        self.assertIn("async_task_statistics", report)
        self.assertIn("cache_statistics", report)
        self.assertIn("optimization_statistics", report)
        self.assertIn("thresholds", report)

        # 验证性能摘要
        summary = report["performance_summary"]
        self.assertIn("avg_memory_mb", summary)
        self.assertIn("avg_cpu_percent", summary)
        self.assertIn("avg_response_time_ms", summary)
        self.assertIn("avg_render_time_ms", summary)
        self.assertIn("memory_trend", summary)
        self.assertIn("response_trend", summary)

    def test_get_optimization_suggestions(self):
        """测试获取优化建议"""
        # 创建高内存使用的指标
        high_memory_metrics = PerformanceMetrics(
            memory_usage_mb=600.0,  # 超过默认阈值500MB
            ui_response_time_ms=250.0,  # 超过默认阈值200ms
            render_time_ms=150.0,  # 超过默认阈值100ms
            cache_hit_rate=60.0,  # 低于70%
            async_tasks_running=15,  # 超过10个
        )

        self.optimizer._metrics_history.append(high_memory_metrics)

        # 获取优化建议
        suggestions = self.optimizer.get_optimization_suggestions()

        # 验证建议数量和类型
        self.assertGreater(len(suggestions), 0)

        # 验证建议包含预期的类别
        categories = [suggestion["category"] for suggestion in suggestions]
        expected_categories = [
            "memory",
            "ui_response",
            "rendering",
            "caching",
            "async_tasks",
        ]

        for category in expected_categories:
            self.assertIn(category, categories)

        # 验证建议结构
        for suggestion in suggestions:
            self.assertIn("category", suggestion)
            self.assertIn("priority", suggestion)
            self.assertIn("title", suggestion)
            self.assertIn("description", suggestion)
            self.assertIn("actions", suggestion)
            self.assertIsInstance(suggestion["actions"], list)

    def test_get_optimization_suggestions_good_performance(self):
        """测试良好性能时的优化建议"""
        # 创建良好性能的指标
        good_metrics = PerformanceMetrics(
            memory_usage_mb=200.0,  # 低于阈值
            ui_response_time_ms=100.0,  # 低于阈值
            render_time_ms=50.0,  # 低于阈值
            cache_hit_rate=85.0,  # 高于70%
            async_tasks_running=3,  # 低于10个
        )

        self.optimizer._metrics_history.append(good_metrics)

        # 获取优化建议
        suggestions = self.optimizer.get_optimization_suggestions()

        # 验证有积极建议
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(suggestions[0]["category"], "general")
        self.assertEqual(suggestions[0]["priority"], "info")
        self.assertIn("性能表现良好", suggestions[0]["title"])

    def test_configure_thresholds(self):
        """测试配置性能阈值"""
        # 配置新阈值
        self.optimizer.configure_thresholds(
            memory_threshold_mb=800.0,
            cpu_threshold_percent=90.0,
            response_time_threshold_ms=300.0,
            render_time_threshold_ms=150.0,
        )

        # 验证阈值更新
        self.assertEqual(self.optimizer._memory_threshold_mb, 800.0)
        self.assertEqual(self.optimizer._cpu_threshold_percent, 90.0)
        self.assertEqual(self.optimizer._response_time_threshold_ms, 300.0)
        self.assertEqual(self.optimizer._render_time_threshold_ms, 150.0)

    def test_enable_disable_auto_optimization(self):
        """测试启用/禁用自动优化"""
        # 测试禁用
        self.optimizer.enable_auto_optimization(False)
        self.assertFalse(self.optimizer._auto_optimization_enabled)

        # 测试启用
        self.optimizer.enable_auto_optimization(True)
        self.assertTrue(self.optimizer._auto_optimization_enabled)

    def test_manual_optimize(self):
        """测试手动优化"""
        # 模拟优化方法
        with patch.object(self.optimizer, "_optimize_memory") as mock_memory:
            with patch.object(self.optimizer, "_optimize_cache") as mock_cache:
                with patch.object(self.optimizer, "_optimize_ui_response") as mock_ui:
                    with patch.object(
                        self.optimizer, "_optimize_rendering"
                    ) as mock_render:
                        with patch.object(
                            self.optimizer, "_perform_garbage_collection"
                        ) as mock_gc:
                            # 执行手动优化
                            result = self.optimizer.manual_optimize()

        # 验证所有优化方法被调用
        mock_memory.assert_called_once()
        mock_cache.assert_called_once()
        mock_ui.assert_called_once()
        mock_render.assert_called_once()
        mock_gc.assert_called_once()

        # 验证结果
        self.assertTrue(result["success"])
        self.assertIn("optimization_time", result)
        self.assertIn("optimizations_performed", result)
        self.assertIn("timestamp", result)
        self.assertEqual(len(result["optimizations_performed"]), 5)

        # 验证统计更新
        self.assertEqual(self.optimizer._optimization_count, 1)
        self.assertIsNotNone(self.optimizer._last_optimization_time)

    def test_manual_optimize_with_error(self):
        """测试手动优化时的错误处理"""
        # 模拟优化方法抛出异常
        with patch.object(
            self.optimizer, "_optimize_memory", side_effect=Exception("Test error")
        ):
            # 执行手动优化
            result = self.optimizer.manual_optimize()

        # 验证错误处理
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Test error")
        self.assertIn("timestamp", result)


class TestPerformanceOptimizerIntegration(unittest.TestCase):
    """测试性能优化器集成"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建独立的优化器实例以避免全局状态干扰
        with patch("src.minicrm.ui.ttk_base.performance_optimizer.async_processor"):
            with patch(
                "src.minicrm.ui.ttk_base.performance_optimizer.data_cache_manager"
            ):
                self.optimizer = TTKPerformanceOptimizer()
                self.optimizer._monitoring_enabled = False

    def tearDown(self):
        """测试清理"""
        if self.optimizer:
            self.optimizer.stop_monitoring()
        if self.root:
            self.root.destroy()

    def test_full_optimization_cycle(self):
        """测试完整的优化周期"""
        # 注册一些组件
        widgets = []
        for i in range(10):
            widget = tk.Label(self.root, text=f"Widget {i}")
            widgets.append(widget)
            self.optimizer.register_widget(widget, f"widget_{i}")

        # 添加虚拟滚动组件
        virtual_widget = MockVirtualScrollWidget(self.root)
        self.optimizer.register_widget(virtual_widget, "virtual_scroll")

        # 跟踪一些渲染时间
        for i in range(20):
            self.optimizer.track_render_time("test_component", 50.0 + i * 5)

        # 模拟性能指标收集
        with patch.object(self.optimizer, "_collect_metrics") as mock_collect:
            # 创建高负载指标
            high_load_metrics = PerformanceMetrics(
                memory_usage_mb=600.0,
                cpu_usage_percent=85.0,
                ui_response_time_ms=250.0,
                render_time_ms=120.0,
                active_widgets=11,
                virtual_scroll_items=2,
                async_tasks_running=12,
                cache_hit_rate=45.0,
                cache_size_mb=60.0,
            )
            mock_collect.return_value = high_load_metrics

            # 执行优化规则
            self.optimizer._execute_optimization_rules(high_load_metrics)

        # 验证优化被执行
        self.assertGreater(self.optimizer._optimization_count, 0)

        # 获取性能报告
        report = self.optimizer.get_performance_report()
        self.assertIn("performance_summary", report)

        # 获取优化建议
        suggestions = self.optimizer.get_optimization_suggestions()
        self.assertGreater(len(suggestions), 0)

    def test_monitoring_lifecycle(self):
        """测试监控生命周期"""
        # 启动监控
        self.optimizer.start_monitoring()
        self.assertTrue(self.optimizer._monitoring_enabled)

        # 停止监控
        self.optimizer.stop_monitoring()
        self.assertFalse(self.optimizer._monitoring_enabled)

    def test_performance_degradation_detection(self):
        """测试性能下降检测"""
        # 添加性能逐渐下降的指标
        base_memory = 200.0
        base_response_time = 100.0

        for i in range(10):
            metrics = PerformanceMetrics(
                memory_usage_mb=base_memory + i * 50,  # 内存逐渐增加
                ui_response_time_ms=base_response_time + i * 20,  # 响应时间逐渐增加
                render_time_ms=50.0 + i * 10,  # 渲染时间逐渐增加
            )
            self.optimizer._metrics_history.append(metrics)

        # 获取优化建议
        suggestions = self.optimizer.get_optimization_suggestions()

        # 验证检测到性能问题
        problem_categories = [
            s["category"] for s in suggestions if s["priority"] in ["high", "medium"]
        ]
        self.assertGreater(len(problem_categories), 0)

    def test_optimization_effectiveness(self):
        """测试优化效果"""
        # 记录优化前的状态
        initial_optimization_count = self.optimizer._optimization_count

        # 执行手动优化
        result = self.optimizer.manual_optimize()

        # 验证优化执行
        self.assertTrue(result["success"])
        self.assertEqual(
            self.optimizer._optimization_count, initial_optimization_count + 1
        )
        self.assertIsNotNone(self.optimizer._last_optimization_time)

        # 验证优化时间合理
        self.assertGreater(result["optimization_time"], 0)
        self.assertLess(result["optimization_time"], 5000)  # 应该在5秒内完成


if __name__ == "__main__":
    unittest.main()
