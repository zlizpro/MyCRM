"""
MiniCRM TTK表格分页和筛选组件测试

测试TablePaginationTTK和TableFilterTTK组件的功能，
确保分页和筛选功能正常工作。
"""

import tkinter as tk
import unittest
from unittest.mock import Mock

from src.minicrm.ui.ttk_base.table_filter_ttk import (
    FilterCondition,
    FilterOperator,
    TableFilterTTK,
)
from src.minicrm.ui.ttk_base.table_pagination_ttk import TablePaginationTTK


class TestTablePaginationTTK(unittest.TestCase):
    """测试TablePaginationTTK组件"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.pagination = TablePaginationTTK(
            self.root,
            page_size=10,
            page_size_options=[5, 10, 20, 50],
            show_page_size_selector=True,
            show_page_jumper=True,
            show_total_info=True,
        )

    def tearDown(self):
        """测试清理"""
        self.pagination.destroy()
        self.root.destroy()

    def test_pagination_initialization(self):
        """测试分页组件初始化"""
        self.assertEqual(self.pagination.page_size, 10)
        self.assertEqual(self.pagination.current_page, 1)
        self.assertEqual(self.pagination.total_pages, 1)
        self.assertEqual(self.pagination.total_records, 0)

    def test_update_pagination(self):
        """测试更新分页信息"""
        # 测试100条记录，每页10条
        self.pagination.update_pagination(100)

        self.assertEqual(self.pagination.total_records, 100)
        self.assertEqual(self.pagination.total_pages, 10)
        self.assertEqual(self.pagination.current_page, 1)

    def test_page_navigation(self):
        """测试页面导航"""
        self.pagination.update_pagination(50)  # 5页数据

        # 测试下一页
        self.pagination._go_next_page()
        self.assertEqual(self.pagination.current_page, 2)

        # 测试上一页
        self.pagination._go_prev_page()
        self.assertEqual(self.pagination.current_page, 1)

        # 测试末页
        self.pagination._go_last_page()
        self.assertEqual(self.pagination.current_page, 5)

        # 测试首页
        self.pagination._go_first_page()
        self.assertEqual(self.pagination.current_page, 1)

    def test_page_size_change(self):
        """测试页面大小变化"""
        self.pagination.update_pagination(100)

        # 模拟页面大小变化
        self.pagination.set_page_size(20)

        self.assertEqual(self.pagination.page_size, 20)
        self.assertEqual(self.pagination.total_pages, 5)  # 100/20 = 5页

    def test_get_current_page_range(self):
        """测试获取当前页数据范围"""
        self.pagination.update_pagination(100)

        # 第1页
        start, end = self.pagination.get_current_page_range()
        self.assertEqual(start, 0)
        self.assertEqual(end, 10)

        # 第2页
        self.pagination._go_next_page()
        start, end = self.pagination.get_current_page_range()
        self.assertEqual(start, 10)
        self.assertEqual(end, 20)

    def test_pagination_callbacks(self):
        """测试分页回调函数"""
        page_changed_mock = Mock()
        page_size_changed_mock = Mock()

        self.pagination.on_page_changed = page_changed_mock
        self.pagination.on_page_size_changed = page_size_changed_mock

        self.pagination.update_pagination(50)

        # 测试页面变化回调
        self.pagination._go_next_page()
        page_changed_mock.assert_called_with(2, 10)

        # 测试页面大小变化回调
        self.pagination.set_page_size(20)
        page_size_changed_mock.assert_called_with(20)

    def test_pagination_info(self):
        """测试分页信息获取"""
        self.pagination.update_pagination(100)
        self.pagination._go_next_page()  # 第2页

        info = self.pagination.get_pagination_info()

        expected_info = {
            "current_page": 2,
            "total_pages": 10,
            "page_size": 10,
            "total_records": 100,
            "start_record": 11,
            "end_record": 20,
        }

        self.assertEqual(info, expected_info)


class TestFilterCondition(unittest.TestCase):
    """测试FilterCondition类"""

    def test_equals_filter(self):
        """测试等于筛选"""
        condition = FilterCondition("name", FilterOperator.EQUALS, "张三")

        self.assertTrue(condition.apply({"name": "张三"}))
        self.assertFalse(condition.apply({"name": "李四"}))

    def test_contains_filter(self):
        """测试包含筛选"""
        condition = FilterCondition("name", FilterOperator.CONTAINS, "张")

        self.assertTrue(condition.apply({"name": "张三"}))
        self.assertTrue(condition.apply({"name": "小张"}))
        self.assertFalse(condition.apply({"name": "李四"}))

    def test_numeric_filters(self):
        """测试数值筛选"""
        # 大于筛选
        condition = FilterCondition("age", FilterOperator.GREATER_THAN, "30")
        self.assertTrue(condition.apply({"age": "35"}))
        self.assertFalse(condition.apply({"age": "25"}))

        # 小于等于筛选
        condition = FilterCondition("age", FilterOperator.LESS_EQUAL, "30")
        self.assertTrue(condition.apply({"age": "30"}))
        self.assertTrue(condition.apply({"age": "25"}))
        self.assertFalse(condition.apply({"age": "35"}))

    def test_between_filter(self):
        """测试区间筛选"""
        condition = FilterCondition("age", FilterOperator.BETWEEN, "20", "40")

        self.assertTrue(condition.apply({"age": "25"}))
        self.assertTrue(condition.apply({"age": "20"}))
        self.assertTrue(condition.apply({"age": "40"}))
        self.assertFalse(condition.apply({"age": "15"}))
        self.assertFalse(condition.apply({"age": "45"}))

    def test_empty_filters(self):
        """测试空值筛选"""
        # 为空筛选
        condition = FilterCondition("description", FilterOperator.IS_EMPTY)
        self.assertTrue(condition.apply({"description": ""}))
        self.assertTrue(condition.apply({"description": None}))
        self.assertTrue(condition.apply({}))  # 字段不存在
        self.assertFalse(condition.apply({"description": "有内容"}))

        # 不为空筛选
        condition = FilterCondition("description", FilterOperator.IS_NOT_EMPTY)
        self.assertFalse(condition.apply({"description": ""}))
        self.assertFalse(condition.apply({"description": None}))
        self.assertTrue(condition.apply({"description": "有内容"}))

    def test_case_sensitivity(self):
        """测试大小写敏感性"""
        # 大小写不敏感（默认）
        condition = FilterCondition("name", FilterOperator.CONTAINS, "ZHANG")
        self.assertTrue(condition.apply({"name": "zhang san"}))

        # 大小写敏感
        condition = FilterCondition(
            "name", FilterOperator.CONTAINS, "ZHANG", case_sensitive=True
        )
        self.assertFalse(condition.apply({"name": "zhang san"}))
        self.assertTrue(condition.apply({"name": "ZHANG SAN"}))


class TestTableFilterTTK(unittest.TestCase):
    """测试TableFilterTTK组件"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.columns = [
            {"id": "name", "text": "姓名"},
            {"id": "age", "text": "年龄"},
            {"id": "city", "text": "城市"},
            {"id": "phone", "text": "电话"},
        ]

        self.filter_widget = TableFilterTTK(
            self.root,
            columns=self.columns,
            show_quick_search=True,
            show_advanced_filter=True,
        )

        # 测试数据
        self.test_data = [
            {"name": "张三", "age": "25", "city": "北京", "phone": "13800138000"},
            {"name": "李四", "age": "30", "city": "上海", "phone": "13800138001"},
            {"name": "王五", "age": "35", "city": "广州", "phone": "13800138002"},
            {"name": "赵六", "age": "28", "city": "深圳", "phone": "13800138003"},
            {"name": "小张", "age": "22", "city": "北京", "phone": "13800138004"},
        ]

    def tearDown(self):
        """测试清理"""
        self.filter_widget.destroy()
        self.root.destroy()

    def test_filter_initialization(self):
        """测试筛选组件初始化"""
        self.assertEqual(len(self.filter_widget.columns), 4)
        self.assertEqual(len(self.filter_widget.filter_conditions), 0)
        self.assertEqual(self.filter_widget.quick_search_text, "")

    def test_quick_search(self):
        """测试快速搜索功能"""
        # 模拟快速搜索
        if self.filter_widget.search_entry:
            self.filter_widget.search_entry.insert(0, "张")
            self.filter_widget._apply_quick_search()

            # 应用筛选
            filtered_data = self.filter_widget.apply_filters(self.test_data)

            # 应该找到包含"张"的记录
            expected_names = ["张三", "小张"]
            actual_names = [row["name"] for row in filtered_data]

            for name in expected_names:
                self.assertIn(name, actual_names)

    def test_apply_filters_no_conditions(self):
        """测试无筛选条件时的数据筛选"""
        filtered_data = self.filter_widget.apply_filters(self.test_data)
        self.assertEqual(len(filtered_data), len(self.test_data))
        self.assertEqual(filtered_data, self.test_data)

    def test_apply_filters_with_conditions(self):
        """测试有筛选条件时的数据筛选"""
        # 添加筛选条件：年龄大于25
        condition = FilterCondition("age", FilterOperator.GREATER_THAN, "25")
        self.filter_widget.filter_conditions.append(condition)

        filtered_data = self.filter_widget.apply_filters(self.test_data)

        # 应该筛选出年龄大于25的记录
        for row in filtered_data:
            self.assertGreater(int(row["age"]), 25)

    def test_multiple_filter_conditions(self):
        """测试多个筛选条件"""
        # 添加多个筛选条件
        condition1 = FilterCondition("age", FilterOperator.GREATER_THAN, "25")
        condition2 = FilterCondition("city", FilterOperator.EQUALS, "北京")

        self.filter_widget.filter_conditions.extend([condition1, condition2])

        filtered_data = self.filter_widget.apply_filters(self.test_data)

        # 应该没有记录满足条件（年龄>25且城市=北京）
        self.assertEqual(len(filtered_data), 0)

    def test_clear_filters(self):
        """测试清除筛选"""
        # 添加筛选条件
        condition = FilterCondition("name", FilterOperator.CONTAINS, "张")
        self.filter_widget.filter_conditions.append(condition)

        # 设置快速搜索
        self.filter_widget.quick_search_text = "test"

        # 清除所有筛选
        self.filter_widget._clear_all_filters()

        self.assertEqual(len(self.filter_widget.filter_conditions), 0)
        self.assertEqual(self.filter_widget.quick_search_text, "")

    def test_get_current_filters(self):
        """测试获取当前筛选条件"""
        # 添加筛选条件
        condition = FilterCondition("name", FilterOperator.CONTAINS, "张")
        self.filter_widget.filter_conditions.append(condition)
        self.filter_widget.quick_search_text = "张"

        filters_info = self.filter_widget.get_current_filters()

        expected_info = {
            "quick_search": "张",
            "conditions_count": 1,
            "has_filters": True,
        }

        self.assertEqual(filters_info, expected_info)

    def test_filter_callback(self):
        """测试筛选变化回调"""
        callback_mock = Mock()
        self.filter_widget.on_filter_changed = callback_mock

        # 触发筛选变化
        self.filter_widget._emit_filter_changed()

        callback_mock.assert_called_once()


class TestIntegratedPaginationAndFilter(unittest.TestCase):
    """测试分页和筛选的集成功能"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建大量测试数据
        self.test_data = []
        for i in range(100):
            self.test_data.append(
                {
                    "id": str(i),
                    "name": f"用户{i}",
                    "age": str(20 + (i % 40)),  # 年龄20-59
                    "city": ["北京", "上海", "广州", "深圳"][i % 4],
                    "status": "活跃" if i % 2 == 0 else "非活跃",
                }
            )

        self.columns = [
            {"id": "id", "text": "ID"},
            {"id": "name", "text": "姓名"},
            {"id": "age", "text": "年龄"},
            {"id": "city", "text": "城市"},
            {"id": "status", "text": "状态"},
        ]

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_pagination_with_filtered_data(self):
        """测试筛选数据的分页"""
        # 创建筛选组件
        filter_widget = TableFilterTTK(self.root, columns=self.columns)

        # 添加筛选条件：城市=北京
        condition = FilterCondition("city", FilterOperator.EQUALS, "北京")
        filter_widget.filter_conditions.append(condition)

        # 应用筛选
        filtered_data = filter_widget.apply_filters(self.test_data)

        # 创建分页组件
        pagination = TablePaginationTTK(self.root, page_size=10)
        pagination.update_pagination(len(filtered_data))

        # 验证分页信息
        self.assertEqual(len(filtered_data), 25)  # 100条数据中有25条城市=北京
        self.assertEqual(pagination.total_pages, 3)  # 25条数据，每页10条，共3页

        # 测试获取第一页数据
        start, end = pagination.get_current_page_range()
        page_data = filtered_data[start:end]
        self.assertEqual(len(page_data), 10)

        # 测试获取最后一页数据
        pagination._go_last_page()
        start, end = pagination.get_current_page_range()
        page_data = filtered_data[start:end]
        self.assertEqual(len(page_data), 5)  # 最后一页只有5条数据

        filter_widget.destroy()
        pagination.destroy()


if __name__ == "__main__":
    unittest.main()
