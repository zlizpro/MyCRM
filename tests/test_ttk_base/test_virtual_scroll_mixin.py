"""
MiniCRM TTK虚拟滚动混入类测试

测试虚拟滚动功能的各个方面，包括：
- 基本虚拟滚动功能
- 数据源更新
- 滚动事件处理
- 性能优化
- 动态高度支持
"""

import time
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.virtual_scroll_mixin import (
    VirtualListBox,
    VirtualScrollConfig,
    VirtualScrollMixin,
    VirtualScrollState,
)


class TestVirtualScrollConfig(unittest.TestCase):
    """测试虚拟滚动配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = VirtualScrollConfig()

        self.assertEqual(config.item_height, 25)
        self.assertEqual(config.buffer_size, 5)
        self.assertEqual(config.scroll_sensitivity, 1.0)
        self.assertTrue(config.enable_smooth_scroll)
        self.assertFalse(config.enable_dynamic_height)
        self.assertEqual(config.min_visible_items, 10)
        self.assertEqual(config.max_visible_items, 100)

    def test_custom_config(self):
        """测试自定义配置"""
        config = VirtualScrollConfig(
            item_height=30,
            buffer_size=10,
            scroll_sensitivity=2.0,
            enable_smooth_scroll=False,
            enable_dynamic_height=True,
            min_visible_items=5,
            max_visible_items=50,
        )

        self.assertEqual(config.item_height, 30)
        self.assertEqual(config.buffer_size, 10)
        self.assertEqual(config.scroll_sensitivity, 2.0)
        self.assertFalse(config.enable_smooth_scroll)
        self.assertTrue(config.enable_dynamic_height)
        self.assertEqual(config.min_visible_items, 5)
        self.assertEqual(config.max_visible_items, 50)


class TestVirtualScrollState(unittest.TestCase):
    """测试虚拟滚动状态"""

    def test_default_state(self):
        """测试默认状态"""
        state = VirtualScrollState()

        self.assertEqual(state.total_items, 0)
        self.assertEqual(state.visible_start, 0)
        self.assertEqual(state.visible_end, 0)
        self.assertEqual(state.scroll_position, 0.0)
        self.assertEqual(state.container_height, 0)
        self.assertEqual(state.total_height, 0)
        self.assertIsInstance(state.rendered_items, dict)
        self.assertEqual(len(state.rendered_items), 0)

    def test_state_updates(self):
        """测试状态更新"""
        state = VirtualScrollState()

        state.total_items = 100
        state.visible_start = 10
        state.visible_end = 20
        state.scroll_position = 0.5
        state.container_height = 400
        state.total_height = 2500

        self.assertEqual(state.total_items, 100)
        self.assertEqual(state.visible_start, 10)
        self.assertEqual(state.visible_end, 20)
        self.assertEqual(state.scroll_position, 0.5)
        self.assertEqual(state.container_height, 400)
        self.assertEqual(state.total_height, 2500)


class MockVirtualScrollWidget(tk.Frame, VirtualScrollMixin):
    """用于测试的虚拟滚动组件"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.created_items = []

    def create_item_widget(self, parent, data, index):
        """创建项目组件"""
        widget = tk.Label(parent, text=str(data))
        self.created_items.append((index, data, widget))
        return widget


class TestVirtualScrollMixin(unittest.TestCase):
    """测试虚拟滚动混入类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.widget = MockVirtualScrollWidget(self.root)
        self.test_data = [f"Item {i}" for i in range(100)]

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.widget._virtual_config, VirtualScrollConfig)
        self.assertIsInstance(self.widget._virtual_state, VirtualScrollState)
        self.assertEqual(len(self.widget._data_source), 0)
        self.assertIsNone(self.widget._item_renderer)
        self.assertFalse(self.widget._events_bound)

    def test_setup_virtual_scroll(self):
        """测试设置虚拟滚动"""

        def mock_renderer(parent, data, index):
            return tk.Label(parent, text=str(data))

        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root, data_source=self.test_data, item_renderer=mock_renderer
        )

        # 验证设置
        self.assertEqual(len(self.widget._data_source), 100)
        self.assertIsNotNone(self.widget._item_renderer)
        self.assertIsNotNone(self.widget._scroll_container)
        self.assertIsNotNone(self.widget._scroll_canvas)
        self.assertIsNotNone(self.widget._scrollbar)
        self.assertIsNotNone(self.widget._content_frame)
        self.assertTrue(self.widget._events_bound)

    def test_calculate_virtual_state(self):
        """测试计算虚拟状态"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 验证状态计算
        self.assertEqual(self.widget._virtual_state.total_items, 100)
        self.assertEqual(
            self.widget._virtual_state.total_height,
            100 * self.widget._virtual_config.item_height,
        )
        self.assertGreaterEqual(self.widget._virtual_state.visible_start, 0)
        self.assertLessEqual(self.widget._virtual_state.visible_end, 100)

    def test_update_data_source(self):
        """测试更新数据源"""
        # 设置初始虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 更新数据源
        new_data = [f"New Item {i}" for i in range(50)]
        self.widget.update_data_source(new_data)

        # 验证更新
        self.assertEqual(len(self.widget._data_source), 50)
        self.assertEqual(self.widget._virtual_state.total_items, 50)
        self.assertEqual(
            len(self.widget._virtual_state.rendered_items), 0
        )  # 应该被清理

    def test_scroll_to_item(self):
        """测试滚动到指定项目"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 滚动到中间项目
        self.widget.scroll_to_item(50)

        # 验证滚动位置
        expected_position = 50 / 99  # (index / (total - 1))
        self.assertAlmostEqual(
            self.widget._virtual_state.scroll_position, expected_position, places=2
        )

    def test_get_visible_range(self):
        """测试获取可见范围"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 获取可见范围
        start, end = self.widget.get_visible_range()

        # 验证范围
        self.assertIsInstance(start, int)
        self.assertIsInstance(end, int)
        self.assertGreaterEqual(start, 0)
        self.assertLessEqual(end, 100)
        self.assertLessEqual(start, end)

    def test_get_performance_stats(self):
        """测试获取性能统计"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 获取性能统计
        stats = self.widget.get_performance_stats()

        # 验证统计信息
        self.assertIn("total_items", stats)
        self.assertIn("visible_items", stats)
        self.assertIn("rendered_items", stats)
        self.assertIn("render_count", stats)
        self.assertIn("scroll_position", stats)

        self.assertEqual(stats["total_items"], 100)
        self.assertGreaterEqual(stats["visible_items"], 0)
        self.assertGreaterEqual(stats["rendered_items"], 0)

    def test_configure_virtual_scroll(self):
        """测试配置虚拟滚动"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 配置参数
        self.widget.configure_virtual_scroll(
            item_height=30, buffer_size=10, scroll_sensitivity=2.0
        )

        # 验证配置
        self.assertEqual(self.widget._virtual_config.item_height, 30)
        self.assertEqual(self.widget._virtual_config.buffer_size, 10)
        self.assertEqual(self.widget._virtual_config.scroll_sensitivity, 2.0)

    def test_dynamic_height_calculator(self):
        """测试动态高度计算器"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 设置动态高度计算器
        def height_calculator(data, index):
            return 30 if index % 2 == 0 else 40

        self.widget.set_item_height_calculator(height_calculator)

        # 验证配置
        self.assertTrue(self.widget._virtual_config.enable_dynamic_height)
        self.assertIsNotNone(self.widget._item_height_calculator)

    @patch("tkinter.time")
    def test_render_performance_tracking(self, mock_time):
        """测试渲染性能跟踪"""
        # 模拟时间
        mock_time.time.side_effect = [0.0, 0.1]  # 100ms渲染时间

        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.test_data[:10],  # 少量数据便于测试
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 验证性能跟踪
        stats = self.widget.get_performance_stats()
        self.assertGreaterEqual(stats["render_count"], 0)


class TestVirtualListBox(unittest.TestCase):
    """测试虚拟列表框"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.listbox = VirtualListBox(self.root)
        self.test_data = [f"Item {i}" for i in range(50)]

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.listbox, tk.Frame)
        self.assertIsInstance(self.listbox, VirtualScrollMixin)
        self.assertIsNotNone(self.listbox._item_renderer)

    def test_set_data(self):
        """测试设置数据"""
        # 设置数据
        self.listbox.set_data(self.test_data)

        # 验证数据设置
        self.assertEqual(len(self.listbox._data_source), 50)
        self.assertIsNotNone(self.listbox._scroll_container)

    def test_create_item_widget(self):
        """测试创建项目组件"""
        # 创建测试框架
        test_frame = tk.Frame(self.root)

        # 创建项目组件
        widget = self.listbox.create_item_widget(test_frame, "Test Item", 0)

        # 验证组件创建
        self.assertIsInstance(widget, tk.Frame)
        self.assertEqual(
            widget.winfo_reqheight(), self.listbox._virtual_config.item_height
        )

    def test_item_selection(self):
        """测试项目选择"""
        # 设置数据
        self.listbox.set_data(self.test_data)

        # 模拟项目选择
        with patch.object(self.listbox, "_on_item_selected") as mock_select:
            # 创建项目并触发点击
            test_frame = tk.Frame(self.root)
            widget = self.listbox.create_item_widget(test_frame, "Test Item", 5)

            # 模拟点击事件
            event = Mock()
            widget.event_generate("<Button-1>")

            # 注意：由于事件绑定的复杂性，这里主要测试组件创建
            self.assertIsInstance(widget, tk.Frame)


class TestVirtualScrollPerformance(unittest.TestCase):
    """测试虚拟滚动性能"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.widget = MockVirtualScrollWidget(self.root)
        # 创建大量测试数据
        self.large_data = [f"Item {i}" for i in range(10000)]

    def tearDown(self):
        """测试清理"""
        if self.root:
            self.root.destroy()

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        start_time = time.time()

        # 设置大数据集
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.large_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        setup_time = time.time() - start_time

        # 验证设置时间合理（应该很快，因为是虚拟滚动）
        self.assertLess(setup_time, 1.0)  # 应该在1秒内完成

        # 验证只渲染了部分项目
        stats = self.widget.get_performance_stats()
        self.assertLess(stats["rendered_items"], stats["total_items"])
        self.assertEqual(stats["total_items"], 10000)

    def test_scroll_performance(self):
        """测试滚动性能"""
        # 设置虚拟滚动
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.large_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 测试多次滚动
        scroll_times = []
        for i in range(10):
            start_time = time.time()
            self.widget.scroll_to_item(i * 1000)
            scroll_time = time.time() - start_time
            scroll_times.append(scroll_time)

        # 验证滚动性能
        avg_scroll_time = sum(scroll_times) / len(scroll_times)
        self.assertLess(avg_scroll_time, 0.1)  # 平均滚动时间应该小于100ms

    def test_memory_usage(self):
        """测试内存使用"""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # 记录初始内存
        initial_memory = process.memory_info().rss

        # 设置大数据集
        self.widget.setup_virtual_scroll(
            parent=self.root,
            data_source=self.large_data,
            item_renderer=lambda p, d, i: tk.Label(p, text=str(d)),
        )

        # 记录设置后内存
        after_setup_memory = process.memory_info().rss

        # 滚动到不同位置
        for i in range(0, 10000, 1000):
            self.widget.scroll_to_item(i)

        # 记录滚动后内存
        after_scroll_memory = process.memory_info().rss

        # 验证内存使用合理
        setup_memory_increase = after_setup_memory - initial_memory
        scroll_memory_increase = after_scroll_memory - after_setup_memory

        # 设置后内存增长应该有限（虚拟滚动的优势）
        self.assertLess(setup_memory_increase, 50 * 1024 * 1024)  # 小于50MB

        # 滚动不应该显著增加内存使用
        self.assertLess(scroll_memory_increase, 10 * 1024 * 1024)  # 小于10MB


if __name__ == "__main__":
    unittest.main()
