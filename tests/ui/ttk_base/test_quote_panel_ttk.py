"""MiniCRM TTK报价管理面板测试

测试TTK报价管理面板的功能，包括：
- 面板初始化和UI创建
- 报价列表加载和显示
- 报价CRUD操作
- 搜索和筛选功能
- 比较和模板集成
- 事件处理

遵循MiniCRM开发标准和测试规范。
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.core.exceptions import ServiceError
from src.minicrm.services.quote_service import QuoteServiceRefactored
from src.minicrm.services.quote_template_service import QuoteTemplateService
from src.minicrm.ui.ttk_base.quote_panel_ttk import QuotePanelTTK


class TestQuotePanelTTK(unittest.TestCase):
    """TTK报价管理面板测试类"""

    def setUp(self):
        """测试准备"""
        # 创建模拟父组件
        self.mock_parent = Mock()

        # 创建模拟服务
        self.mock_quote_service = Mock(spec=QuoteServiceRefactored)
        self.mock_template_service = Mock(spec=QuoteTemplateService)

        # 模拟报价数据
        self.mock_quotes = [
            Mock(
                to_dict=Mock(
                    return_value={
                        "id": 1,
                        "quote_number": "Q20240101001",
                        "customer_name": "测试客户1",
                        "contact_person": "联系人1",
                        "status_display": "已发送",
                        "quote_type_display": "标准报价",
                        "formatted_total": "¥10,000.00",
                        "formatted_quote_date": "2024-01-01",
                        "formatted_valid_until": "2024-01-31",
                        "remaining_days": 15,
                    }
                )
            ),
            Mock(
                to_dict=Mock(
                    return_value={
                        "id": 2,
                        "quote_number": "Q20240101002",
                        "customer_name": "测试客户2",
                        "contact_person": "联系人2",
                        "status_display": "草稿",
                        "quote_type_display": "定制报价",
                        "formatted_total": "¥20,000.00",
                        "formatted_quote_date": "2024-01-02",
                        "formatted_valid_until": "2024-02-01",
                        "remaining_days": 20,
                    }
                )
            ),
        ]

        self.mock_quote_service.list_all.return_value = self.mock_quotes

        # 模拟TTK组件创建，避免实际创建Tkinter窗口
        with (
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Frame"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Notebook"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Label"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Button"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Entry"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.tk.StringVar"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.DataTableTTK"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteComparisonTTK"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteTemplateTTK"),
            patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteExportTTK"),
        ):
            # 创建测试组件
            self.quote_panel = QuotePanelTTK(
                self.mock_parent, self.mock_quote_service, self.mock_template_service
            )

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "quote_panel"):
            self.quote_panel.cleanup()

    def test_initialization(self):
        """测试面板初始化"""
        # 验证基本属性
        self.assertIsNotNone(self.quote_panel._quote_service)
        self.assertIsNotNone(self.quote_panel._template_service)

        # 验证数据加载
        self.mock_quote_service.list_all.assert_called_once()
        self.assertEqual(len(self.quote_panel._quotes), 2)

        # 验证UI组件创建
        self.assertIsNotNone(self.quote_panel._notebook)

    def test_load_quotes_success(self):
        """测试成功加载报价"""
        # 验证报价数据加载
        self.assertEqual(len(self.quote_panel._quotes), 2)
        self.assertEqual(len(self.quote_panel._filtered_quotes), 2)

        # 验证数据格式
        first_quote = self.quote_panel._quotes[0]
        self.assertEqual(first_quote["quote_number"], "Q20240101001")
        self.assertEqual(first_quote["customer_name"], "测试客户1")

    def test_load_quotes_service_error(self):
        """测试加载报价服务错误"""
        # 创建新的面板，模拟服务错误
        mock_service = Mock(spec=QuoteServiceRefactored)
        mock_service.list_all.side_effect = ServiceError("加载失败")

        with patch("tkinter.messagebox.showerror") as mock_error:
            with (
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Frame"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Notebook"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Label"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Button"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.ttk.Entry"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.tk.StringVar"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.DataTableTTK"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteComparisonTTK"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteTemplateTTK"),
                patch("src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteExportTTK"),
            ):
                panel = QuotePanelTTK(self.mock_parent, mock_service)

                # 验证错误处理
                mock_error.assert_called_once()
                self.assertEqual(len(panel._quotes), 0)
                panel.cleanup()

    def test_search_functionality(self):
        """测试搜索功能"""
        # 设置搜索变量
        self.quote_panel._search_var = Mock()
        self.quote_panel._search_var.get.return_value = "客户1"

        # 执行搜索
        self.quote_panel._perform_search()

        # 验证搜索结果
        self.assertEqual(len(self.quote_panel._filtered_quotes), 1)
        self.assertEqual(
            self.quote_panel._filtered_quotes[0]["customer_name"], "测试客户1"
        )

    def test_clear_search(self):
        """测试清空搜索"""
        # 先执行搜索
        self.quote_panel._search_var = Mock()
        self.quote_panel._search_var.get.return_value = "客户1"
        self.quote_panel._perform_search()

        # 清空搜索
        self.quote_panel._search_var.set = Mock()
        self.quote_panel._clear_search()

        # 验证搜索被清空
        self.quote_panel._search_var.set.assert_called_once_with("")
        self.assertEqual(len(self.quote_panel._filtered_quotes), 2)

    def test_quote_selection(self):
        """测试报价选择"""
        # 模拟选择报价
        quote_data = self.quote_panel._quotes[0]

        # 设置回调函数
        mock_callback = Mock()
        self.quote_panel.on_quote_selected = mock_callback

        # 执行选择
        self.quote_panel._on_quote_selected(quote_data)

        # 验证选择结果
        self.assertEqual(self.quote_panel._selected_quote, quote_data)
        mock_callback.assert_called_once_with(quote_data)

    def test_delete_quote_success(self):
        """测试成功删除报价"""
        # 模拟表格选择
        selected_data = [{"id": 1, "quote_number": "Q20240101001"}]

        # 模拟表格组件
        self.quote_panel._quote_table = Mock()
        self.quote_panel._quote_table.get_selected_data.return_value = selected_data

        # 模拟服务成功
        self.mock_quote_service.delete.return_value = True

        # 模拟用户确认
        with patch("tkinter.messagebox.askyesno", return_value=True):
            with patch("tkinter.messagebox.showinfo") as mock_info:
                with patch.object(self.quote_panel, "_refresh_quotes") as mock_refresh:
                    self.quote_panel._delete_quote()

                    # 验证服务调用
                    self.mock_quote_service.delete.assert_called_once_with(1)
                    mock_info.assert_called_once()
                    mock_refresh.assert_called_once()

    def test_delete_quote_no_selection(self):
        """测试没有选择时删除报价"""
        # 模拟没有选择
        self.quote_panel._quote_table = Mock()
        self.quote_panel._quote_table.get_selected_data.return_value = []

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.quote_panel._delete_quote()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_delete_quote_cancelled(self):
        """测试取消删除报价"""
        # 模拟表格选择
        selected_data = [{"id": 1, "quote_number": "Q20240101001"}]

        self.quote_panel._quote_table = Mock()
        self.quote_panel._quote_table.get_selected_data.return_value = selected_data

        # 模拟用户取消
        with patch("tkinter.messagebox.askyesno", return_value=False):
            self.quote_panel._delete_quote()

            # 验证服务未被调用
            self.mock_quote_service.delete.assert_not_called()

    def test_add_quote_to_comparison(self):
        """测试添加报价到比较"""
        # 模拟比较组件
        self.quote_panel._comparison_widget = Mock()
        self.quote_panel._comparison_widget.add_quote_for_comparison.return_value = True

        # 模拟标签页
        self.quote_panel._notebook = Mock()

        # 执行添加
        quote_data = {"id": 1, "quote_number": "Q001"}
        result = self.quote_panel.add_quote_to_comparison(quote_data)

        # 验证结果
        self.assertTrue(result)
        self.quote_panel._notebook.select.assert_called_once_with(1)
        self.quote_panel._comparison_widget.add_quote_for_comparison.assert_called_once_with(
            quote_data
        )

    def test_export_quotes(self):
        """测试导出报价"""
        # 模拟选中的报价
        selected_quotes = [{"id": 1, "quote_number": "Q001"}]

        # 模拟表格组件
        self.quote_panel._quote_table = Mock()
        self.quote_panel._quote_table.get_selected_data.return_value = selected_quotes

        # 模拟导出组件
        mock_export_widget = Mock()

        with patch(
            "src.minicrm.ui.ttk_base.quote_panel_ttk.QuoteExportTTK",
            return_value=mock_export_widget,
        ):
            self.quote_panel.export_quotes()

            # 验证导出组件创建和调用
            mock_export_widget.show_export_dialog.assert_called_once_with(
                selected_quotes
            )

    def test_export_quotes_no_selection(self):
        """测试没有选择时导出报价"""
        # 模拟没有选择
        self.quote_panel._quote_table = Mock()
        self.quote_panel._quote_table.get_selected_data.return_value = []

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.quote_panel.export_quotes()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_get_selected_quote(self):
        """测试获取选中报价"""
        # 初始状态
        self.assertIsNone(self.quote_panel.get_selected_quote())

        # 设置选中报价
        quote_data = {"id": 1, "quote_number": "Q001"}
        self.quote_panel._selected_quote = quote_data

        # 验证获取结果
        self.assertEqual(self.quote_panel.get_selected_quote(), quote_data)

    def test_get_all_quotes(self):
        """测试获取所有报价"""
        all_quotes = self.quote_panel.get_all_quotes()

        # 验证返回副本
        self.assertEqual(len(all_quotes), 2)
        self.assertIsNot(all_quotes, self.quote_panel._quotes)

    def test_get_filtered_quotes(self):
        """测试获取筛选后的报价"""
        filtered_quotes = self.quote_panel.get_filtered_quotes()

        # 验证返回副本
        self.assertEqual(len(filtered_quotes), 2)
        self.assertIsNot(filtered_quotes, self.quote_panel._filtered_quotes)

    def test_event_callbacks(self):
        """测试事件回调"""
        # 设置回调函数
        mock_selected = Mock()
        mock_created = Mock()
        mock_updated = Mock()
        mock_deleted = Mock()

        self.quote_panel.on_quote_selected = mock_selected
        self.quote_panel.on_quote_created = mock_created
        self.quote_panel.on_quote_updated = mock_updated
        self.quote_panel.on_quote_deleted = mock_deleted

        # 触发选择事件
        quote_data = {"id": 1, "quote_number": "Q001"}
        self.quote_panel._on_quote_selected(quote_data)

        # 验证回调调用
        mock_selected.assert_called_once_with(quote_data)

    def test_comparison_completed_callback(self):
        """测试比较完成回调"""
        comparison_result = {"quotes": [], "statistics": {}}

        # 执行回调
        self.quote_panel._on_comparison_completed(comparison_result)

        # 验证日志记录（通过不抛出异常来验证）

    def test_template_applied_callback(self):
        """测试模板应用回调"""
        template_data = {"name": "测试模板", "id": "test_template"}

        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.quote_panel._on_template_applied(template_data)

            # 验证信息显示
            mock_info.assert_called_once()

    def test_cleanup(self):
        """测试资源清理"""
        # 设置一些数据
        self.quote_panel._selected_quote = {"id": 1}

        # 模拟子组件
        self.quote_panel._quote_table = Mock()
        self.quote_panel._comparison_widget = Mock()
        self.quote_panel._template_widget = Mock()
        self.quote_panel._export_widget = Mock()

        # 执行清理
        self.quote_panel.cleanup()

        # 验证清理结果
        self.assertEqual(len(self.quote_panel._quotes), 0)
        self.assertEqual(len(self.quote_panel._filtered_quotes), 0)
        self.assertIsNone(self.quote_panel._selected_quote)

        # 验证子组件清理
        self.quote_panel._quote_table.cleanup.assert_called_once()
        self.quote_panel._comparison_widget.cleanup.assert_called_once()
        self.quote_panel._template_widget.cleanup.assert_called_once()
        self.quote_panel._export_widget.cleanup.assert_called_once()

    def test_button_states_update(self):
        """测试按钮状态更新"""
        # 模拟按钮
        self.quote_panel._edit_btn = Mock()
        self.quote_panel._delete_btn = Mock()

        # 初始状态 - 没有选择
        self.quote_panel._selected_quote = None
        self.quote_panel._update_button_states()

        # 验证按钮状态
        self.quote_panel._edit_btn.config.assert_called_with(state=tk.DISABLED)
        self.quote_panel._delete_btn.config.assert_called_with(state=tk.DISABLED)

        # 有选择状态
        self.quote_panel._selected_quote = {"id": 1}
        self.quote_panel._update_button_states()

        # 验证按钮状态
        self.quote_panel._edit_btn.config.assert_called_with(state=tk.NORMAL)
        self.quote_panel._delete_btn.config.assert_called_with(state=tk.NORMAL)


if __name__ == "__main__":
    unittest.main()
