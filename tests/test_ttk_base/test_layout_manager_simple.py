"""
布局管理器简化测试

专门用于无头环境的布局管理器测试，主要测试逻辑功能而不依赖GUI显示。

作者: MiniCRM开发团队
"""

import os
import sys
import unittest
from unittest.mock import Mock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.minicrm.ui.ttk_base.layout_manager import (
    Alignment,
    LayoutType,
    calculate_optimal_grid_size,
    create_responsive_layout,
)


class TestLayoutManagerLogic(unittest.TestCase):
    """布局管理器逻辑测试类（无需GUI）"""

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

        # 测试边界情况
        rows, cols = calculate_optimal_grid_size(
            item_count=0, container_width=100, item_width=50
        )
        self.assertEqual(rows, 0)
        self.assertEqual(cols, 2)  # 100 / 50 = 2

    def test_create_responsive_layout(self):
        """测试创建响应式布局"""
        mock_parent = Mock()
        mobile_layout = Mock()
        tablet_layout = Mock()
        desktop_layout = Mock()

        breakpoints = {
            0: mobile_layout,  # 0-767px
            768: tablet_layout,  # 768-1023px
            1024: desktop_layout,  # 1024px+
        }

        responsive_handler = create_responsive_layout(mock_parent, breakpoints)

        # 测试不同宽度下的布局选择
        responsive_handler(500, 400)  # 应该选择mobile_layout
        mobile_layout.assert_called_once_with(mock_parent, 500, 400)

        responsive_handler(800, 600)  # 应该选择tablet_layout
        tablet_layout.assert_called_once_with(mock_parent, 800, 600)

        responsive_handler(1200, 800)  # 应该选择desktop_layout
        desktop_layout.assert_called_once_with(mock_parent, 1200, 800)

        # 测试没有合适断点的情况
        responsive_handler(50, 50)  # 应该选择mobile_layout（最小断点）
        self.assertEqual(mobile_layout.call_count, 2)

    def test_responsive_layout_edge_cases(self):
        """测试响应式布局边界情况"""
        mock_parent = Mock()

        # 空断点配置
        empty_breakpoints = {}
        responsive_handler = create_responsive_layout(mock_parent, empty_breakpoints)

        # 不应该抛出异常
        responsive_handler(800, 600)

        # 单一断点配置
        single_breakpoint = {0: Mock()}
        responsive_handler = create_responsive_layout(mock_parent, single_breakpoint)
        responsive_handler(1000, 800)
        single_breakpoint[0].assert_called_once_with(mock_parent, 1000, 800)


class TestLayoutHelperLogic(unittest.TestCase):
    """布局助手逻辑测试类"""

    def test_grid_size_validation(self):
        """测试网格大小验证逻辑"""
        # 测试有效的网格配置
        self.assertTrue(self._is_valid_grid_config(3, 3, 1, 1))
        self.assertTrue(self._is_valid_grid_config(5, 5, 2, 2))

        # 测试无效的网格配置
        self.assertFalse(self._is_valid_grid_config(3, 3, 5, 1))  # 行超出范围
        self.assertFalse(self._is_valid_grid_config(3, 3, 1, 5))  # 列超出范围
        self.assertFalse(self._is_valid_grid_config(3, 3, -1, 1))  # 负数行
        self.assertFalse(self._is_valid_grid_config(3, 3, 1, -1))  # 负数列

    def _is_valid_grid_config(self, rows, cols, row, col):
        """验证网格配置是否有效"""
        return 0 <= row < rows and 0 <= col < cols and row >= 0 and col >= 0

    def test_form_field_validation(self):
        """测试表单字段配置验证"""
        # 有效的字段配置
        valid_field = {"id": "name", "label": "姓名", "type": "entry", "required": True}
        self.assertTrue(self._is_valid_field_config(valid_field))

        # 无效的字段配置
        invalid_field = {
            "label": "姓名",  # 缺少id
            "type": "entry",
        }
        self.assertFalse(self._is_valid_field_config(invalid_field))

        # 无效的字段类型
        invalid_type_field = {"id": "test", "label": "测试", "type": "invalid_type"}
        self.assertFalse(self._is_valid_field_config(invalid_type_field))

    def _is_valid_field_config(self, field):
        """验证字段配置是否有效"""
        if not isinstance(field, dict):
            return False

        # 必须有id
        if "id" not in field:
            return False

        # 验证字段类型
        valid_types = ["entry", "text", "combobox", "checkbox", "spinbox", "date"]
        field_type = field.get("type", "entry")
        if field_type not in valid_types:
            return False

        return True

    def test_layout_padding_calculation(self):
        """测试布局内边距计算"""
        # 测试默认内边距
        default_padding = self._calculate_padding()
        self.assertEqual(default_padding, (5, 5))

        # 测试自定义内边距
        custom_padding = self._calculate_padding(10, 15)
        self.assertEqual(custom_padding, (10, 15))

        # 测试单一值内边距
        single_padding = self._calculate_padding(8)
        self.assertEqual(single_padding, (8, 8))

    def _calculate_padding(self, padx=5, pady=None):
        """计算内边距"""
        if pady is None:
            pady = padx
        return (padx, pady)


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
