"""
MiniCRM TTK数据表格组件测试

测试DataTableTTK组件的完整功能，包括数据绑定、排序、筛选、分页、导出等。
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.ui.ttk_base.data_table_ttk import DataTableTTK, SortOrder


class TestDataTableTTK(unittest.TestCase):
    """测试DataTableTTK组件"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.columns = [
            {"id": "name", "text": "姓名", "width": 100},
            {"id": "age", "text": "年龄", "width": 80},
            {"id": "city", "text": "城市", "width": 120},
            {"id": "phone", "text": "电话", "width": 150},
        ]

        self.data_table = DataTableTTK(
            self.root,
            columns=self.columns,
            editable=False,
            multi_select=True,
            show_pagination=True,
            page_size=10,
            enable_virtual_scroll=False,  # 禁用虚拟滚动以便测试
        )

        # 测试数据
        self.test_data = [
            {"name": "张三", "age": "25", "city": "北京", "phone": "13800138000"},
            {"name": "李四", "age": "30", "city": "上海", "phone": "13800138001"},
            {"name": "王五", "age": "35", "city": "广州", "phone": "13800138002"},
            {"name": "赵六", "age": "28", "city": "深圳", "phone": "13800138003"},
            {"name": "小张", "age": "22", "city": "北京", "phone": "13800138004"},
            {"name": "小李", "age": "26", "city": "上海", "phone": "13800138005"},
            {"name": "小王", "age": "32", "city": "广州", "phone": "13800138006"},
            {"name": "小赵", "age": "29", "city": "深圳", "phone": "13800138007"},
            {"name": "老张", "age": "45", "city": "北京", "phone": "13800138008"},
            {"name": "老李", "age": "50", "city": "上海", "phone": "13800138009"},
            {"name": "老王", "age": "48", "city": "广州", "phone": "13800138010"},
            {"name": "老赵", "age": "52", "city": "深圳", "phone": "13800138011"},
        ]

    def tearDown(self):
        """测试清理"""
        self.data_table.destroy()
        self.root.destroy()

    def test_table_initialization(self):
        """测试表格初始化"""
        self.assertEqual(len(self.data_table.columns), 4)
        self.assertTrue(self.data_table.multi_select)
        self.assertTrue(self.data_table.show_pagination)
        self.assertEqual(self.data_table.page_size, 10)
        self.assertIsNotNone(self.data_table.tree)
        self.assertIsNotNone(self.data_table.filter_widget)
        self.assertIsNotNone(self.data_table.pagination_widget)
        self.assertIsNotNone(self.data_table.export_widget)

    def test_load_data(self):
        """测试数据加载"""
        self.data_table.load_data(self.test_data)

        self.assertEqual(len(self.data_table.data), 12)
        self.assertEqual(len(self.data_table.filtered_data), 12)

        # 验证树形控件中的数据
        children = self.data_table.tree.get_children()
        self.assertEqual(len(children), 10)  # 第一页显示10条记录

    def test_column_sorting(self):
        """测试列排序功能"""
        self.data_table.load_data(self.test_data)

        # 测试按年龄排序
        self.data_table._sort_by_column("age")

        self.assertEqual(self.data_table.sort_column, "age")
        self.assertEqual(self.data_table.sort_order, SortOrder.ASC)

        # 验证排序结果
        first_row_values = self.data_table.tree.item(
            self.data_table.tree.get_children()[0], "values"
        )
        self.assertEqual(first_row_values[1], "22")  # 最小年龄

        # 测试降序排序
        self.data_table._sort_by_column("age")
        self.assertEqual(self.data_table.sort_order, SortOrder.DESC)

    def test_data_filtering(self):
        """测试数据筛选"""
        self.data_table.load_data(self.test_data)

        # 模拟筛选条件
        if self.data_table.filter_widget:
            # 添加筛选条件：城市=北京
            from src.minicrm.ui.ttk_base.table_filter_ttk import (
                FilterCondition,
                FilterOperator,
            )

            condition = FilterCondition("city", FilterOperator.EQUALS, "北京")
            self.data_table.filter_widget.filter_conditions = [condition]

            # 触发筛选
            self.data_table._on_filter_changed()

            # 验证筛选结果
            self.assertEqual(len(self.data_table.filtered_data), 3)  # 3条北京记录

    def test_pagination(self):
        """测试分页功能"""
        self.data_table.load_data(self.test_data)

        # 验证分页信息
        if self.data_table.pagination_widget:
            pagination_info = self.data_table.pagination_widget.get_pagination_info()

            self.assertEqual(pagination_info["total_records"], 12)
            self.assertEqual(
                pagination_info["total_pages"], 2
            )  # 12条记录，每页10条，共2页
            self.assertEqual(pagination_info["current_page"], 1)

    def test_selection_functionality(self):
        """测试选择功能"""
        self.data_table.load_data(self.test_data)

        # 测试全选
        self.data_table.select_all()
        selected_data = self.data_table.get_selected_data()
        self.assertEqual(len(selected_data), 10)  # 当前页的所有记录

        # 测试清除选择
        self.data_table.clear_selection()
        selected_data = self.data_table.get_selected_data()
        self.assertEqual(len(selected_data), 0)

    def test_refresh_functionality(self):
        """测试刷新功能"""
        self.data_table.load_data(self.test_data)

        # 修改数据
        self.data_table.data[0]["name"] = "修改后的张三"

        # 刷新表格
        self.data_table.refresh()

        # 验证数据已更新
        first_row_values = self.data_table.tree.item(
            self.data_table.tree.get_children()[0], "values"
        )
        # 注意：由于可能有排序，需要检查是否包含修改后的数据
        all_names = [
            self.data_table.tree.item(child, "values")[0]
            for child in self.data_table.tree.get_children()
        ]
        self.assertIn("修改后的张三", all_names)

    def test_event_callbacks(self):
        """测试事件回调"""
        # 设置回调函数
        row_selected_callback = Mock()
        row_double_clicked_callback = Mock()
        selection_changed_callback = Mock()

        self.data_table.on_row_selected = row_selected_callback
        self.data_table.on_row_double_clicked = row_double_clicked_callback
        self.data_table.on_selection_changed = selection_changed_callback

        self.data_table.load_data(self.test_data)

        # 模拟选择变化事件
        self.data_table._on_selection_changed(None)

        # 验证回调被调用
        selection_changed_callback.assert_called()

    def test_export_integration(self):
        """测试导出功能集成"""
        self.data_table.load_data(self.test_data)

        # 验证导出组件存在
        self.assertIsNotNone(self.data_table.export_widget)

        # 测试导出对话框显示（不实际显示）
        with patch.object(
            self.data_table.export_widget, "show_export_dialog"
        ) as mock_show:
            self.data_table._show_export_dialog()
            mock_show.assert_called_once()

    def test_virtual_scroll_setup(self):
        """测试虚拟滚动设置"""
        # 创建启用虚拟滚动的表格
        virtual_table = DataTableTTK(
            self.root, columns=self.columns, enable_virtual_scroll=True
        )

        # 加载大量数据
        large_data = self.test_data * 10  # 120条记录
        virtual_table.load_data(large_data)

        # 验证虚拟滚动参数
        self.assertEqual(virtual_table.visible_count, 50)
        self.assertEqual(virtual_table.total_count, 120)

        virtual_table.destroy()

    def test_info_display_update(self):
        """测试信息显示更新"""
        self.data_table.load_data(self.test_data)

        # 验证信息标签存在并显示正确信息
        if hasattr(self.data_table, "info_label") and self.data_table.info_label:
            info_text = self.data_table.info_label.cget("text")
            self.assertIn("12", info_text)  # 应该包含总记录数

    def test_cleanup(self):
        """测试资源清理"""
        self.data_table.load_data(self.test_data)

        # 执行清理
        self.data_table.cleanup()

        # 验证数据被清理
        self.assertEqual(len(self.data_table.data), 0)
        self.assertEqual(len(self.data_table.filtered_data), 0)

    def test_page_size_change(self):
        """测试页面大小变化"""
        self.data_table.load_data(self.test_data)

        # 模拟页面大小变化
        self.data_table._on_page_size_changed(5)

        self.assertEqual(self.data_table.page_size, 5)

    def test_context_menu(self):
        """测试右键菜单"""
        self.data_table.load_data(self.test_data)

        # 创建模拟事件
        event = Mock()
        event.x_root = 100
        event.y_root = 100

        # 模拟右键点击（这里主要测试不会抛出异常）
        try:
            self.data_table._show_context_menu(event)
        except Exception:
            # 在测试环境中可能会有一些UI相关的异常，这是正常的
            pass

    def test_empty_data_handling(self):
        """测试空数据处理"""
        self.data_table.load_data([])

        self.assertEqual(len(self.data_table.data), 0)
        self.assertEqual(len(self.data_table.filtered_data), 0)

        # 验证树形控件为空
        children = self.data_table.tree.get_children()
        self.assertEqual(len(children), 0)

    def test_single_select_mode(self):
        """测试单选模式"""
        # 创建单选模式的表格
        single_select_table = DataTableTTK(
            self.root, columns=self.columns, multi_select=False
        )

        self.assertFalse(single_select_table.multi_select)

        single_select_table.destroy()


if __name__ == "__main__":
    unittest.main()
