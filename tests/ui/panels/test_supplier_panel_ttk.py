"""供应商管理面板TTK组件测试.

测试供应商管理面板的各个功能：
- 供应商列表显示和管理
- 搜索和筛选功能
- 供应商操作（新增、编辑、删除）
- 供应商详情预览
- 批量操作支持
- 供应商对比功能集成
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.models.supplier import QualityRating, SupplierLevel, SupplierType
from minicrm.ui.panels.supplier_panel_ttk import SupplierPanelTTK


class TestSupplierPanelTTK(unittest.TestCase):
    """供应商管理面板TTK组件测试类."""

    def setUp(self):
        """测试前准备."""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的供应商服务
        self.mock_supplier_service = Mock()

        # 模拟供应商数据
        self.mock_suppliers = [
            {
                "id": 1,
                "name": "供应商A",
                "company_name": "A公司",
                "contact_person": "张三",
                "phone": "13800138001",
                "email": "zhangsan@a.com",
                "address": "北京市朝阳区",
                "supplier_type": SupplierType.MANUFACTURER.value,
                "supplier_level": SupplierLevel.STRATEGIC.value,
                "quality_rating": QualityRating.EXCELLENT.value,
                "quality_score": 95.0,
                "delivery_rating": 90.0,
                "service_rating": 88.0,
                "cooperation_years": 5,
                "total_orders": 100,
                "total_amount": 1000000.0,
                "created_at": "2024-01-01 10:00:00",
            },
            {
                "id": 2,
                "name": "供应商B",
                "company_name": "B公司",
                "contact_person": "李四",
                "phone": "13800138002",
                "email": "lisi@b.com",
                "address": "上海市浦东新区",
                "supplier_type": SupplierType.DISTRIBUTOR.value,
                "supplier_level": SupplierLevel.IMPORTANT.value,
                "quality_rating": QualityRating.GOOD.value,
                "quality_score": 85.0,
                "delivery_rating": 92.0,
                "service_rating": 80.0,
                "cooperation_years": 3,
                "total_orders": 80,
                "total_amount": 800000.0,
                "created_at": "2024-01-02 11:00:00",
            },
            {
                "id": 3,
                "name": "供应商C",
                "company_name": "C公司",
                "contact_person": "王五",
                "phone": "13800138003",
                "email": "wangwu@c.com",
                "address": "广州市天河区",
                "supplier_type": SupplierType.WHOLESALER.value,
                "supplier_level": SupplierLevel.NORMAL.value,
                "quality_rating": QualityRating.AVERAGE.value,
                "quality_score": 75.0,
                "delivery_rating": 78.0,
                "service_rating": 82.0,
                "cooperation_years": 2,
                "total_orders": 60,
                "total_amount": 600000.0,
                "created_at": "2024-01-03 12:00:00",
            },
        ]

        # 配置模拟服务的返回值
        self.mock_supplier_service.search_suppliers.return_value = (
            self.mock_suppliers,
            len(self.mock_suppliers),
        )

        self.mock_supplier_service.delete_supplier.return_value = True

        # 创建供应商管理面板
        self.supplier_panel = SupplierPanelTTK(self.root, self.mock_supplier_service)

    def tearDown(self):
        """测试后清理."""
        if self.supplier_panel:
            self.supplier_panel.cleanup()
        self.root.destroy()

    def test_panel_initialization(self):
        """测试面板初始化."""
        # 验证面板创建成功
        self.assertIsNotNone(self.supplier_panel)
        self.assertEqual(
            self.supplier_panel._supplier_service, self.mock_supplier_service
        )

        # 验证UI组件存在
        self.assertIsNotNone(self.supplier_panel._search_entry)
        self.assertIsNotNone(self.supplier_panel._level_filter)
        self.assertIsNotNone(self.supplier_panel._type_filter)
        self.assertIsNotNone(self.supplier_panel._quality_filter)
        self.assertIsNotNone(self.supplier_panel._supplier_table)
        self.assertIsNotNone(self.supplier_panel._detail_panel)
        self.assertIsNotNone(self.supplier_panel._comparison_panel)
        self.assertIsNotNone(self.supplier_panel._notebook)

        # 验证数据加载
        self.mock_supplier_service.search_suppliers.assert_called_once()
        self.assertEqual(
            len(self.supplier_panel._current_suppliers), len(self.mock_suppliers)
        )

    def test_supplier_filtering(self):
        """测试供应商筛选功能."""
        # 测试搜索筛选
        self.supplier_panel._search_entry.insert(0, "供应商A")
        self.supplier_panel._on_search_changed(None)

        # 验证搜索查询被设置
        self.assertEqual(self.supplier_panel._search_query, "供应商A")

        # 测试等级筛选
        self.supplier_panel._level_filter.set(SupplierLevel.STRATEGIC.value)
        self.supplier_panel._on_filter_changed(None)

        # 测试类型筛选
        self.supplier_panel._type_filter.set(SupplierType.MANUFACTURER.value)
        self.supplier_panel._on_filter_changed(None)

        # 测试质量等级筛选
        self.supplier_panel._quality_filter.set(QualityRating.EXCELLENT.value)
        self.supplier_panel._on_filter_changed(None)

    def test_filter_building(self):
        """测试筛选条件构建."""
        # 设置筛选条件
        self.supplier_panel._level_filter.set(SupplierLevel.STRATEGIC.value)
        self.supplier_panel._type_filter.set(SupplierType.MANUFACTURER.value)
        self.supplier_panel._quality_filter.set(QualityRating.EXCELLENT.value)

        # 构建筛选条件
        filters = self.supplier_panel._build_filters()

        # 验证筛选条件
        expected_filters = {
            "supplier_level": SupplierLevel.STRATEGIC.value,
            "supplier_type": SupplierType.MANUFACTURER.value,
            "quality_rating": QualityRating.EXCELLENT.value,
        }
        self.assertEqual(filters, expected_filters)

        # 测试"全部"选项
        self.supplier_panel._level_filter.set("全部")
        filters = self.supplier_panel._build_filters()
        self.assertNotIn("supplier_level", filters)

    def test_supplier_selection(self):
        """测试供应商选择功能."""
        # 模拟选择供应商
        selected_data = [self.mock_suppliers[0]]
        self.supplier_panel._on_supplier_selected(selected_data)

        # 验证选择状态
        self.assertEqual(
            self.supplier_panel._selected_supplier_id, self.mock_suppliers[0]["id"]
        )

        # 验证按钮状态更新
        self.assertEqual(self.supplier_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.supplier_panel._delete_button.cget("state"), "normal")

        # 测试多选
        selected_data = self.mock_suppliers[:2]
        self.supplier_panel._on_supplier_selected(selected_data)

        # 验证批量操作按钮状态
        self.assertEqual(
            self.supplier_panel._batch_delete_button.cget("state"), "normal"
        )
        self.assertEqual(self.supplier_panel._compare_button.cget("state"), "normal")

        # 测试取消选择
        self.supplier_panel._on_supplier_selected([])

        # 验证状态重置
        self.assertIsNone(self.supplier_panel._selected_supplier_id)
        self.assertEqual(self.supplier_panel._edit_button.cget("state"), "disabled")
        self.assertEqual(self.supplier_panel._delete_button.cget("state"), "disabled")

    def test_button_state_updates(self):
        """测试按钮状态更新."""
        # 测试无选择状态
        self.supplier_panel._update_button_states(False, False)
        self.assertEqual(self.supplier_panel._edit_button.cget("state"), "disabled")
        self.assertEqual(self.supplier_panel._delete_button.cget("state"), "disabled")
        self.assertEqual(
            self.supplier_panel._batch_delete_button.cget("state"), "disabled"
        )
        self.assertEqual(self.supplier_panel._compare_button.cget("state"), "disabled")

        # 测试单选状态
        self.supplier_panel._update_button_states(True, False)
        self.assertEqual(self.supplier_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.supplier_panel._delete_button.cget("state"), "normal")
        self.assertEqual(
            self.supplier_panel._batch_delete_button.cget("state"), "disabled"
        )
        self.assertEqual(self.supplier_panel._compare_button.cget("state"), "disabled")

        # 测试多选状态
        self.supplier_panel._update_button_states(True, True)
        self.assertEqual(self.supplier_panel._edit_button.cget("state"), "normal")
        self.assertEqual(self.supplier_panel._delete_button.cget("state"), "normal")
        self.assertEqual(
            self.supplier_panel._batch_delete_button.cget("state"), "normal"
        )
        self.assertEqual(self.supplier_panel._compare_button.cget("state"), "normal")

    def test_supplier_detail_display(self):
        """测试供应商详情显示."""
        supplier_data = self.mock_suppliers[0]

        # 显示供应商详情
        self.supplier_panel._show_supplier_detail(supplier_data)

        # 验证详情内容被创建
        detail_widgets = self.supplier_panel._detail_content.winfo_children()
        self.assertGreater(len(detail_widgets), 0)

        # 验证包含基本信息框架
        frame_texts = []
        for widget in detail_widgets:
            if isinstance(widget, ttk.LabelFrame):
                frame_texts.append(widget.cget("text"))

        self.assertIn("基本信息", frame_texts)
        self.assertIn("分类信息", frame_texts)
        self.assertIn("质量信息", frame_texts)
        self.assertIn("合作信息", frame_texts)

    def test_detail_placeholder(self):
        """测试详情占位符显示."""
        # 显示占位符
        self.supplier_panel._show_detail_placeholder()

        # 验证占位符内容
        detail_widgets = self.supplier_panel._detail_content.winfo_children()
        self.assertEqual(len(detail_widgets), 1)

        placeholder_widget = detail_widgets[0]
        self.assertIsInstance(placeholder_widget, ttk.Label)
        self.assertIn("请选择", placeholder_widget.cget("text"))

    def test_status_bar_updates(self):
        """测试状态栏更新."""
        # 测试相等数量
        self.supplier_panel._update_status_bar(10, 10)
        self.assertEqual(
            self.supplier_panel._status_label.cget("text"), "共 10 个供应商"
        )

        # 测试不等数量
        self.supplier_panel._update_status_bar(5, 10)
        self.assertEqual(
            self.supplier_panel._status_label.cget("text"), "显示 5 / 10 个供应商"
        )

        # 测试选择状态
        self.supplier_panel._update_selection_status(0)
        self.assertEqual(self.supplier_panel._selection_label.cget("text"), "")

        self.supplier_panel._update_selection_status(1)
        self.assertEqual(
            self.supplier_panel._selection_label.cget("text"), "已选择 1 个供应商"
        )

        self.supplier_panel._update_selection_status(3)
        self.assertEqual(
            self.supplier_panel._selection_label.cget("text"), "已选择 3 个供应商"
        )

    def test_search_functionality(self):
        """测试搜索功能."""
        # 测试搜索输入变化
        self.supplier_panel._search_entry.insert(0, "测试搜索")
        self.supplier_panel._on_search_changed(None)

        # 验证搜索查询被设置
        self.assertEqual(self.supplier_panel._search_query, "测试搜索")

        # 测试清除搜索
        self.supplier_panel._clear_search()

        # 验证搜索被清除
        self.assertEqual(self.supplier_panel._search_query, "")
        self.assertEqual(self.supplier_panel._search_entry.get(), "")

    @patch("tkinter.messagebox.askyesno")
    def test_delete_supplier(self, mock_askyesno):
        """测试删除供应商功能."""
        # 设置选中的供应商
        self.supplier_panel._selected_supplier_id = 1

        # 模拟用户确认删除
        mock_askyesno.return_value = True

        with patch("tkinter.messagebox.showinfo") as mock_showinfo:
            self.supplier_panel._on_delete_supplier()

            # 验证服务方法被调用
            self.mock_supplier_service.delete_supplier.assert_called_with(1)

            # 验证成功消息
            mock_showinfo.assert_called_once()

        # 测试用户取消删除
        mock_askyesno.return_value = False
        self.mock_supplier_service.delete_supplier.reset_mock()

        self.supplier_panel._on_delete_supplier()

        # 验证服务方法未被调用
        self.mock_supplier_service.delete_supplier.assert_not_called()

    @patch("tkinter.messagebox.showwarning")
    def test_delete_supplier_no_selection(self, mock_showwarning):
        """测试未选择供应商时删除操作."""
        # 未选择供应商
        self.supplier_panel._selected_supplier_id = None

        self.supplier_panel._on_delete_supplier()

        # 验证警告消息
        mock_showwarning.assert_called_once()

    @patch("tkinter.messagebox.askyesno")
    def test_batch_delete_suppliers(self, mock_askyesno):
        """测试批量删除供应商功能."""
        # 模拟选中多个供应商
        selected_suppliers = self.mock_suppliers[:2]
        self.supplier_panel._supplier_table = Mock()
        self.supplier_panel._supplier_table.get_selected_data.return_value = (
            selected_suppliers
        )

        # 模拟用户确认删除
        mock_askyesno.return_value = True

        with patch("tkinter.messagebox.showinfo") as mock_showinfo:
            self.supplier_panel._on_batch_delete()

            # 验证服务方法被调用
            self.assertEqual(self.mock_supplier_service.delete_supplier.call_count, 2)

            # 验证成功消息
            mock_showinfo.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_batch_delete_insufficient_selection(self, mock_showwarning):
        """测试选择不足时的批量删除."""
        # 模拟选中少于2个供应商
        selected_suppliers = [self.mock_suppliers[0]]
        self.supplier_panel._supplier_table = Mock()
        self.supplier_panel._supplier_table.get_selected_data.return_value = (
            selected_suppliers
        )

        self.supplier_panel._on_batch_delete()

        # 验证警告消息
        mock_showwarning.assert_called_once()

    def test_supplier_comparison_integration(self):
        """测试供应商对比功能集成."""
        # 模拟选中多个供应商
        selected_suppliers = self.mock_suppliers[:3]
        self.supplier_panel._supplier_table = Mock()
        self.supplier_panel._supplier_table.get_selected_data.return_value = (
            selected_suppliers
        )

        # 模拟对比面板
        self.supplier_panel._comparison_panel = Mock()

        with patch("tkinter.messagebox.showinfo") as mock_showinfo:
            self.supplier_panel._on_compare_suppliers()

            # 验证对比面板方法被调用
            expected_ids = [1, 2, 3]
            self.supplier_panel._comparison_panel.load_suppliers_for_comparison.assert_called_with(
                expected_ids
            )

            # 验证成功消息
            mock_showinfo.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_comparison_insufficient_selection(self, mock_showwarning):
        """测试选择不足时的供应商对比."""
        # 模拟选中少于2个供应商
        selected_suppliers = [self.mock_suppliers[0]]
        self.supplier_panel._supplier_table = Mock()
        self.supplier_panel._supplier_table.get_selected_data.return_value = (
            selected_suppliers
        )

        self.supplier_panel._on_compare_suppliers()

        # 验证警告消息
        mock_showwarning.assert_called_once()

    @patch("tkinter.messagebox.showwarning")
    def test_comparison_too_many_selection(self, mock_showwarning):
        """测试选择过多时的供应商对比."""
        # 模拟选中超过4个供应商
        selected_suppliers = self.mock_suppliers + [
            {"id": 4, "name": "供应商D"},
            {"id": 5, "name": "供应商E"},
        ]
        self.supplier_panel._supplier_table = Mock()
        self.supplier_panel._supplier_table.get_selected_data.return_value = (
            selected_suppliers
        )

        self.supplier_panel._on_compare_suppliers()

        # 验证警告消息
        mock_showwarning.assert_called_once()

    def test_tab_switching(self):
        """测试标签页切换功能."""
        # 测试切换到对比标签页
        self.supplier_panel.switch_to_comparison_tab()
        # 由于是模拟环境，主要验证方法不会出错

        # 测试切换到列表标签页
        self.supplier_panel.switch_to_list_tab()
        # 由于是模拟环境，主要验证方法不会出错

    @patch("tkinter.messagebox.showinfo")
    def test_placeholder_operations(self, mock_showinfo):
        """测试占位符操作（未实现的功能）."""
        # 测试新增供应商
        self.supplier_panel._on_add_supplier()
        mock_showinfo.assert_called()

        # 重置mock
        mock_showinfo.reset_mock()

        # 测试编辑供应商（无选择）
        self.supplier_panel._selected_supplier_id = None
        with patch("tkinter.messagebox.showwarning"):
            self.supplier_panel._on_edit_supplier()

        # 测试编辑供应商（有选择）
        self.supplier_panel._selected_supplier_id = 1
        self.supplier_panel._on_edit_supplier()
        mock_showinfo.assert_called()

        # 重置mock
        mock_showinfo.reset_mock()

        # 测试导出功能
        self.supplier_panel._current_suppliers = self.mock_suppliers
        self.supplier_panel._on_export_suppliers()
        mock_showinfo.assert_called()

        # 重置mock
        mock_showinfo.reset_mock()

        # 测试查看历史
        self.supplier_panel._on_view_supplier_history(1)
        mock_showinfo.assert_called()

        # 重置mock
        mock_showinfo.reset_mock()

        # 测试刷新
        self.supplier_panel._on_refresh()
        mock_showinfo.assert_called()

    def test_public_interface_methods(self):
        """测试公共接口方法."""
        # 测试刷新数据
        self.supplier_panel.refresh_data()
        # 验证服务方法被调用
        self.assertGreater(self.mock_supplier_service.search_suppliers.call_count, 1)

        # 测试选中供应商
        self.supplier_panel.select_supplier(1)
        self.assertEqual(self.supplier_panel.get_selected_supplier_id(), 1)

        # 测试获取选中供应商ID
        supplier_id = self.supplier_panel.get_selected_supplier_id()
        self.assertEqual(supplier_id, 1)

    def test_error_handling(self):
        """测试错误处理."""
        # 测试服务异常处理
        self.mock_supplier_service.search_suppliers.side_effect = Exception("服务异常")

        with patch("tkinter.messagebox.showerror") as mock_error:
            # 重新创建面板以触发异常
            try:
                SupplierPanelTTK(self.root, self.mock_supplier_service)
            except Exception:
                pass  # 预期的异常

            # 验证错误消息显示
            mock_error.assert_called()

    def test_widget_cleanup(self):
        """测试组件清理功能."""
        # 创建对比面板的模拟
        self.supplier_panel._comparison_panel = Mock()

        # 执行清理
        self.supplier_panel.cleanup()

        # 验证对比面板被清理
        self.supplier_panel._comparison_panel.cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
