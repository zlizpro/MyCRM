"""
布局管理器单元测试

测试LayoutManager及其相关助手类的功能，包括：
- 网格布局功能测试
- 包装布局功能测试
- 表单布局功能测试
- 响应式布局功能测试
- 边界条件和异常处理测试

作者: MiniCRM开发团队
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.minicrm.ui.ttk_base.layout_manager import (
    Alignment,
    FormLayoutHelper,
    GridLayoutHelper,
    LayoutManager,
    LayoutType,
    PackLayoutHelper,
    calculate_optimal_grid_size,
    create_responsive_layout,
)


class TestLayoutManager(unittest.TestCase):
    """布局管理器测试类"""

    def setUp(self):
        """测试准备"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏测试窗口
            self.frame = ttk.Frame(self.root)
            self.layout_manager = LayoutManager(self.frame)
            self.has_display = True
        except tk.TclError:
            # 无头环境，跳过需要显示的测试
            self.has_display = False
            self.root = None
            self.frame = None
            self.layout_manager = None

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_layout_manager_initialization(self):
        """测试布局管理器初始化"""
        self.assertIsNotNone(self.layout_manager)
        self.assertEqual(self.layout_manager.parent, self.frame)
        self.assertIsInstance(self.layout_manager._layouts, dict)
        self.assertIsInstance(self.layout_manager._responsive_callbacks, list)

    def test_create_grid_layout(self):
        """测试创建网格布局"""
        grid_layout = self.layout_manager.create_grid_layout(3, 4)

        self.assertIsInstance(grid_layout, GridLayoutHelper)
        self.assertEqual(grid_layout.rows, 3)
        self.assertEqual(grid_layout.cols, 4)
        self.assertEqual(len(self.layout_manager._layouts), 1)

    def test_create_pack_layout(self):
        """测试创建包装布局"""
        pack_layout = self.layout_manager.create_pack_layout(
            side="left", fill="x", expand=True
        )

        self.assertIsInstance(pack_layout, PackLayoutHelper)
        self.assertEqual(pack_layout.side, "left")
        self.assertEqual(pack_layout.fill, "x")
        self.assertTrue(pack_layout.expand)

    def test_create_form_layout(self):
        """测试创建表单布局"""
        fields = [
            {"id": "name", "label": "姓名", "type": "entry", "required": True},
            {"id": "age", "label": "年龄", "type": "spinbox", "from_": 0, "to": 120},
            {
                "id": "gender",
                "label": "性别",
                "type": "combobox",
                "options": ["男", "女"],
            },
        ]

        form_layout = self.layout_manager.create_form_layout(fields)

        self.assertIsInstance(form_layout, FormLayoutHelper)
        self.assertEqual(len(form_layout.widgets), 3)
        self.assertEqual(len(form_layout.labels), 3)

    def test_add_responsive_callback(self):
        """测试添加响应式回调"""
        callback = Mock()
        self.layout_manager.add_responsive_callback(callback)

        self.assertIn(callback, self.layout_manager._responsive_callbacks)

    def test_clear_layouts(self):
        """测试清理布局"""
        # 创建几个布局
        self.layout_manager.create_grid_layout(2, 2)
        self.layout_manager.create_pack_layout()

        self.assertEqual(len(self.layout_manager._layouts), 2)

        # 清理布局
        self.layout_manager.clear_layouts()

        self.assertEqual(len(self.layout_manager._layouts), 0)


class TestGridLayoutHelper(unittest.TestCase):
    """网格布局助手测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.frame = ttk.Frame(self.root)
        self.grid_helper = GridLayoutHelper(self.frame, 3, 3, (5, 5), False, False)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_grid_helper_initialization(self):
        """测试网格助手初始化"""
        self.assertEqual(self.grid_helper.rows, 3)
        self.assertEqual(self.grid_helper.cols, 3)
        self.assertEqual(self.grid_helper.padding, (5, 5))
        self.assertIsInstance(self.grid_helper._widgets, dict)

    def test_add_widget_to_grid(self):
        """测试添加组件到网格"""
        widget = ttk.Label(self.frame, text="测试标签")

        self.grid_helper.add_widget(widget, 1, 1)

        self.assertEqual(self.grid_helper.get_widget(1, 1), widget)
        self.assertIn((1, 1), self.grid_helper._widgets)

    def test_add_widget_with_span(self):
        """测试添加跨行跨列组件"""
        widget = ttk.Label(self.frame, text="跨行跨列")

        self.grid_helper.add_widget(widget, 0, 0, rowspan=2, columnspan=2)

        self.assertEqual(self.grid_helper.get_widget(0, 0), widget)

    def test_add_widget_out_of_bounds(self):
        """测试添加组件到超出范围的位置"""
        widget = ttk.Label(self.frame, text="超出范围")

        with self.assertRaises(ValueError):
            self.grid_helper.add_widget(widget, 5, 5)

    def test_remove_widget_from_grid(self):
        """测试从网格移除组件"""
        widget = ttk.Label(self.frame, text="待移除")
        self.grid_helper.add_widget(widget, 1, 1)

        self.grid_helper.remove_widget(1, 1)

        self.assertIsNone(self.grid_helper.get_widget(1, 1))
        self.assertNotIn((1, 1), self.grid_helper._widgets)

    def test_clear_grid(self):
        """测试清理网格"""
        # 添加几个组件
        for i in range(3):
            widget = ttk.Label(self.frame, text=f"标签{i}")
            self.grid_helper.add_widget(widget, 0, i)

        self.assertEqual(len(self.grid_helper._widgets), 3)

        # 清理网格
        self.grid_helper.clear()

        self.assertEqual(len(self.grid_helper._widgets), 0)


class TestPackLayoutHelper(unittest.TestCase):
    """包装布局助手测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.frame = ttk.Frame(self.root)
        self.pack_helper = PackLayoutHelper(self.frame, "top", "x", True, (5, 5))

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_pack_helper_initialization(self):
        """测试包装助手初始化"""
        self.assertEqual(self.pack_helper.side, "top")
        self.assertEqual(self.pack_helper.fill, "x")
        self.assertTrue(self.pack_helper.expand)
        self.assertEqual(self.pack_helper.padding, (5, 5))

    def test_add_widget_to_pack(self):
        """测试添加组件到包装布局"""
        widget = ttk.Label(self.frame, text="测试标签")

        self.pack_helper.add_widget(widget)

        self.assertIn(widget, self.pack_helper._widgets)

    def test_add_widget_with_custom_options(self):
        """测试使用自定义选项添加组件"""
        widget = ttk.Label(self.frame, text="自定义选项")

        self.pack_helper.add_widget(widget, side="left", fill="y", expand=False)

        self.assertIn(widget, self.pack_helper._widgets)

    def test_remove_widget_from_pack(self):
        """测试从包装布局移除组件"""
        widget = ttk.Label(self.frame, text="待移除")
        self.pack_helper.add_widget(widget)

        self.pack_helper.remove_widget(widget)

        self.assertNotIn(widget, self.pack_helper._widgets)

    def test_clear_pack(self):
        """测试清理包装布局"""
        # 添加几个组件
        for i in range(3):
            widget = ttk.Label(self.frame, text=f"标签{i}")
            self.pack_helper.add_widget(widget)

        self.assertEqual(len(self.pack_helper._widgets), 3)

        # 清理布局
        self.pack_helper.clear()

        self.assertEqual(len(self.pack_helper._widgets), 0)


class TestFormLayoutHelper(unittest.TestCase):
    """表单布局助手测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.frame = ttk.Frame(self.root)

        self.fields = [
            {"id": "name", "label": "姓名", "type": "entry", "required": True},
            {"id": "age", "label": "年龄", "type": "spinbox", "from_": 0, "to": 120},
            {
                "id": "gender",
                "label": "性别",
                "type": "combobox",
                "options": ["男", "女"],
            },
            {"id": "description", "label": "描述", "type": "text"},
            {"id": "active", "label": "激活", "type": "checkbox"},
        ]

        self.form_helper = FormLayoutHelper(self.frame, self.fields, 100, 200, (5, 2))

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_form_helper_initialization(self):
        """测试表单助手初始化"""
        self.assertEqual(len(self.form_helper.widgets), 5)
        self.assertEqual(len(self.form_helper.labels), 5)

        # 检查必填字段标签是否有星号
        name_label = self.form_helper.labels["name"]
        self.assertIn("*", name_label["text"])

    def test_create_different_widget_types(self):
        """测试创建不同类型的输入组件"""
        # Entry组件
        self.assertIsInstance(self.form_helper.widgets["name"], ttk.Entry)

        # Spinbox组件
        self.assertIsInstance(self.form_helper.widgets["age"], ttk.Spinbox)

        # Combobox组件
        self.assertIsInstance(self.form_helper.widgets["gender"], ttk.Combobox)

        # Text组件
        self.assertIsInstance(self.form_helper.widgets["description"], tk.Text)

        # Checkbutton组件
        self.assertIsInstance(self.form_helper.widgets["active"], ttk.Checkbutton)

    def test_get_form_values(self):
        """测试获取表单值"""
        # 设置一些值
        self.form_helper.widgets["name"].insert(0, "张三")
        self.form_helper.widgets["age"].set("25")
        self.form_helper.widgets["gender"].set("男")
        self.form_helper.widgets["description"].insert("1.0", "测试描述")

        values = self.form_helper.get_values()

        self.assertEqual(values["name"], "张三")
        self.assertEqual(values["age"], "25")
        self.assertEqual(values["gender"], "男")
        self.assertEqual(values["description"], "测试描述")

    def test_set_form_values(self):
        """测试设置表单值"""
        values = {
            "name": "李四",
            "age": "30",
            "gender": "女",
            "description": "新的描述",
            "active": True,
        }

        self.form_helper.set_values(values)

        self.assertEqual(self.form_helper.widgets["name"].get(), "李四")
        self.assertEqual(self.form_helper.widgets["age"].get(), "30")
        self.assertEqual(self.form_helper.widgets["gender"].get(), "女")
        self.assertEqual(
            self.form_helper.widgets["description"].get("1.0", tk.END).strip(),
            "新的描述",
        )

    def test_clear_form(self):
        """测试清理表单"""
        # 先添加一些内容
        self.form_helper.widgets["name"].insert(0, "测试")

        # 清理表单
        self.form_helper.clear()

        self.assertEqual(len(self.form_helper.widgets), 0)
        self.assertEqual(len(self.form_helper.labels), 0)


class TestResponsiveLayout(unittest.TestCase):
    """响应式布局测试类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.frame = ttk.Frame(self.root)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_create_responsive_layout(self):
        """测试创建响应式布局"""
        mobile_layout = Mock()
        tablet_layout = Mock()
        desktop_layout = Mock()

        breakpoints = {
            0: mobile_layout,  # 0-767px
            768: tablet_layout,  # 768-1023px
            1024: desktop_layout,  # 1024px+
        }

        responsive_handler = create_responsive_layout(self.frame, breakpoints)

        # 测试不同宽度下的布局选择
        responsive_handler(500, 400)  # 应该选择mobile_layout
        mobile_layout.assert_called_once_with(self.frame, 500, 400)

        responsive_handler(800, 600)  # 应该选择tablet_layout
        tablet_layout.assert_called_once_with(self.frame, 800, 600)

        responsive_handler(1200, 800)  # 应该选择desktop_layout
        desktop_layout.assert_called_once_with(self.frame, 1200, 800)

    def test_calculate_optimal_grid_size(self):
        """测试计算最优网格大小"""
        # 测试基本情况
        rows, cols = calculate_optimal_grid_size(
            item_count=10, container_width=400, item_width=100
        )
        self.assertEqual(cols, 4)  # 400 / 100 = 4
        self.assertEqual(rows, 3)  # ceil(10 / 4) = 3

        # 测试最小列数限制
        rows, cols = calculate_optimal_grid_size(
            item_count=5, container_width=50, item_width=100, min_cols=2
        )
        self.assertEqual(cols, 2)  # 应用最小列数限制
        self.assertEqual(rows, 3)  # ceil(5 / 2) = 3

        # 测试最大列数限制
        rows, cols = calculate_optimal_grid_size(
            item_count=20, container_width=1000, item_width=50, max_cols=5
        )
        self.assertEqual(cols, 5)  # 应用最大列数限制
        self.assertEqual(rows, 4)  # ceil(20 / 5) = 4


class TestLayoutEnums(unittest.TestCase):
    """布局枚举测试类"""

    def test_layout_type_enum(self):
        """测试布局类型枚举"""
        self.assertEqual(LayoutType.GRID.value, "grid")
        self.assertEqual(LayoutType.PACK.value, "pack")
        self.assertEqual(LayoutType.FORM.value, "form")
        self.assertEqual(LayoutType.RESPONSIVE.value, "responsive")

    def test_alignment_enum(self):
        """测试对齐方式枚举"""
        self.assertEqual(Alignment.LEFT.value, "w")
        self.assertEqual(Alignment.RIGHT.value, "e")
        self.assertEqual(Alignment.CENTER.value, "center")
        self.assertEqual(Alignment.TOP.value, "n")
        self.assertEqual(Alignment.BOTTOM.value, "s")
        self.assertEqual(Alignment.FILL.value, "fill")


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
