"""MiniCRM TTK报价比较组件测试

测试TTK报价比较组件的功能，包括：
- 组件初始化和UI创建
- 报价添加和移除
- 比较功能执行
- 结果显示和导出
- 事件处理

遵循MiniCRM开发标准和测试规范。
"""

from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

from src.minicrm.core.exceptions import ServiceError
from src.minicrm.services.quote_service import QuoteServiceRefactored
from src.minicrm.ui.ttk_base.quote_comparison_ttk import QuoteComparisonTTK


class TestQuoteComparisonTTK(unittest.TestCase):
    """TTK报价比较组件测试类"""

    def setUp(self):
        """测试准备"""
        # 创建模拟父组件
        self.mock_parent = Mock()

        # 创建模拟服务
        self.mock_quote_service = Mock(spec=QuoteServiceRefactored)

        # 模拟TTK组件创建，避免实际创建Tkinter窗口
        with (
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.ttk.Frame"),
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.ttk.Notebook"),
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.ttk.Label"),
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.ttk.Button"),
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.ttk.Combobox"),
            patch("src.minicrm.ui.ttk_base.quote_comparison_ttk.tk.StringVar"),
        ):
            # 创建测试组件
            self.comparison_widget = QuoteComparisonTTK(
                self.mock_parent,
                self.mock_quote_service,
                comparison_mode="detailed",
                max_quotes=4,
            )

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "comparison_widget"):
            self.comparison_widget.cleanup()

    def test_initialization(self):
        """测试组件初始化"""
        # 验证基本属性
        self.assertEqual(self.comparison_widget.comparison_mode, "detailed")
        self.assertEqual(self.comparison_widget.max_quotes, 4)
        self.assertIsNotNone(self.comparison_widget._quote_service)

        # 验证数据初始化
        self.assertEqual(len(self.comparison_widget._quotes_to_compare), 0)
        self.assertIsNone(self.comparison_widget._comparison_result)

        # 验证UI组件创建
        self.assertIsNotNone(self.comparison_widget._notebook)
        self.assertIsNotNone(self.comparison_widget._comparison_frame)
        self.assertIsNotNone(self.comparison_widget._statistics_frame)
        self.assertIsNotNone(self.comparison_widget._chart_frame)

    def test_add_quote_for_comparison_success(self):
        """测试成功添加报价到比较列表"""
        # 准备测试数据
        quote_data = {
            "id": 1,
            "quote_number": "Q20240101001",
            "customer_name": "测试客户",
            "formatted_total": "¥10,000.00",
        }

        # 执行添加操作
        result = self.comparison_widget.add_quote_for_comparison(quote_data)

        # 验证结果
        self.assertTrue(result)
        self.assertEqual(len(self.comparison_widget._quotes_to_compare), 1)
        self.assertEqual(self.comparison_widget._quotes_to_compare[0], quote_data)

    def test_add_quote_for_comparison_duplicate(self):
        """测试添加重复报价"""
        # 准备测试数据
        quote_data = {
            "id": 1,
            "quote_number": "Q20240101001",
            "customer_name": "测试客户",
            "formatted_total": "¥10,000.00",
        }

        # 先添加一次
        self.comparison_widget.add_quote_for_comparison(quote_data)

        # 再次添加相同报价
        with patch("tkinter.messagebox.showwarning") as mock_warning:
            result = self.comparison_widget.add_quote_for_comparison(quote_data)

            # 验证结果
            self.assertFalse(result)
            self.assertEqual(len(self.comparison_widget._quotes_to_compare), 1)
            mock_warning.assert_called_once()

    def test_add_quote_for_comparison_max_limit(self):
        """测试达到最大比较数量限制"""
        # 添加最大数量的报价
        for i in range(self.comparison_widget.max_quotes):
            quote_data = {
                "id": i + 1,
                "quote_number": f"Q20240101{i + 1:03d}",
                "customer_name": f"测试客户{i + 1}",
                "formatted_total": f"¥{(i + 1) * 1000}.00",
            }
            self.comparison_widget.add_quote_for_comparison(quote_data)

        # 尝试添加超出限制的报价
        extra_quote = {
            "id": 999,
            "quote_number": "Q20240101999",
            "customer_name": "额外客户",
            "formatted_total": "¥999.00",
        }

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            result = self.comparison_widget.add_quote_for_comparison(extra_quote)

            # 验证结果
            self.assertFalse(result)
            self.assertEqual(
                len(self.comparison_widget._quotes_to_compare),
                self.comparison_widget.max_quotes,
            )
            mock_warning.assert_called_once()

    def test_remove_quote_from_comparison(self):
        """测试从比较列表中移除报价"""
        # 准备测试数据
        quote_data1 = {"id": 1, "quote_number": "Q001", "customer_name": "客户1"}
        quote_data2 = {"id": 2, "quote_number": "Q002", "customer_name": "客户2"}

        # 添加报价
        self.comparison_widget.add_quote_for_comparison(quote_data1)
        self.comparison_widget.add_quote_for_comparison(quote_data2)

        # 移除第一个报价
        self.comparison_widget._remove_quote_from_comparison(0)

        # 验证结果
        self.assertEqual(len(self.comparison_widget._quotes_to_compare), 1)
        self.assertEqual(self.comparison_widget._quotes_to_compare[0]["id"], 2)

    def test_clear_comparison(self):
        """测试清空比较"""
        # 添加一些报价
        for i in range(3):
            quote_data = {"id": i + 1, "quote_number": f"Q{i + 1:03d}"}
            self.comparison_widget.add_quote_for_comparison(quote_data)

        # 清空比较
        self.comparison_widget._clear_comparison()

        # 验证结果
        self.assertEqual(len(self.comparison_widget._quotes_to_compare), 0)
        self.assertIsNone(self.comparison_widget._comparison_result)

    def test_start_comparison_success(self):
        """测试成功开始比较"""
        # 准备测试数据
        quote_data1 = {"id": 1, "quote_number": "Q001"}
        quote_data2 = {"id": 2, "quote_number": "Q002"}

        self.comparison_widget.add_quote_for_comparison(quote_data1)
        self.comparison_widget.add_quote_for_comparison(quote_data2)

        # 模拟服务返回
        mock_comparison_result = {
            "quotes": [quote_data1, quote_data2],
            "differences": {"total_amount": {"description": "金额不同"}},
            "statistics": {"average_amount": "¥5,000.00"},
        }
        self.mock_quote_service.compare_quotes.return_value = mock_comparison_result

        # 执行比较
        self.comparison_widget._start_comparison()

        # 验证服务调用
        self.mock_quote_service.compare_quotes.assert_called_once_with(
            [1, 2], "detailed"
        )

        # 验证结果存储
        self.assertEqual(
            self.comparison_widget._comparison_result, mock_comparison_result
        )

    def test_start_comparison_insufficient_quotes(self):
        """测试报价数量不足时的比较"""
        # 只添加一个报价
        quote_data = {"id": 1, "quote_number": "Q001"}
        self.comparison_widget.add_quote_for_comparison(quote_data)

        # 尝试开始比较
        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.comparison_widget._start_comparison()

            # 验证警告显示
            mock_warning.assert_called_once()

            # 验证服务未被调用
            self.mock_quote_service.compare_quotes.assert_not_called()

    def test_start_comparison_service_error(self):
        """测试比较服务错误处理"""
        # 准备测试数据
        quote_data1 = {"id": 1, "quote_number": "Q001"}
        quote_data2 = {"id": 2, "quote_number": "Q002"}

        self.comparison_widget.add_quote_for_comparison(quote_data1)
        self.comparison_widget.add_quote_for_comparison(quote_data2)

        # 模拟服务错误
        self.mock_quote_service.compare_quotes.side_effect = ServiceError("比较失败")

        # 执行比较
        with patch("tkinter.messagebox.showerror") as mock_error:
            self.comparison_widget._start_comparison()

            # 验证错误处理
            mock_error.assert_called_once()
            self.assertIsNone(self.comparison_widget._comparison_result)

    def test_mode_change(self):
        """测试比较模式变化"""
        # 设置初始模式
        self.assertEqual(self.comparison_widget.comparison_mode, "detailed")

        # 模拟模式变化
        self.comparison_widget._mode_var.set("summary")
        self.comparison_widget._on_mode_changed()

        # 验证模式更新
        self.assertEqual(self.comparison_widget.comparison_mode, "summary")

    def test_export_comparison_no_result(self):
        """测试没有比较结果时的导出"""
        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.comparison_widget._export_comparison()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_export_comparison_json_success(self):
        """测试成功导出JSON格式"""
        # 设置比较结果
        self.comparison_widget._comparison_result = {
            "quotes": [{"id": 1, "quote_number": "Q001"}],
            "statistics": {"average_amount": "¥1,000.00"},
        }

        # 模拟文件选择
        mock_file_path = "/test/path/comparison.json"

        with (
            patch("tkinter.filedialog.asksaveasfilename", return_value=mock_file_path),
            patch("builtins.open", create=True) as mock_open,
            patch("json.dump") as mock_json_dump,
            patch("tkinter.messagebox.showinfo") as mock_info,
        ):
            self.comparison_widget._export_comparison()

            # 验证文件操作
            mock_open.assert_called_once()
            mock_json_dump.assert_called_once()
            mock_info.assert_called_once()

    def test_export_comparison_text_success(self):
        """测试成功导出文本格式"""
        # 设置比较结果
        self.comparison_widget._comparison_result = {
            "quotes": [
                {
                    "id": 1,
                    "quote_number": "Q001",
                    "customer_name": "客户1",
                    "formatted_total": "¥1,000.00",
                    "status_display": "已发送",
                }
            ],
            "statistics": {"average_amount": "¥1,000.00"},
        }

        # 模拟文件选择
        mock_file_path = "/test/path/comparison.txt"

        with (
            patch("tkinter.filedialog.asksaveasfilename", return_value=mock_file_path),
            patch("builtins.open", create=True) as mock_open,
            patch("tkinter.messagebox.showinfo") as mock_info,
        ):
            self.comparison_widget._export_comparison()

            # 验证文件操作
            mock_open.assert_called_once()
            mock_info.assert_called_once()

    def test_export_comparison_cancelled(self):
        """测试取消导出"""
        # 设置比较结果
        self.comparison_widget._comparison_result = {"quotes": []}

        # 模拟取消文件选择
        with patch("tkinter.filedialog.asksaveasfilename", return_value=""):
            self.comparison_widget._export_comparison()

            # 验证没有进一步操作

    def test_print_comparison(self):
        """测试打印比较结果"""
        # 设置比较结果
        self.comparison_widget._comparison_result = {"quotes": []}

        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.comparison_widget._print_comparison()

            # 验证显示提示信息
            mock_info.assert_called_once()

    def test_print_comparison_no_result(self):
        """测试没有比较结果时的打印"""
        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.comparison_widget._print_comparison()

            # 验证警告显示
            mock_warning.assert_called_once()

    def test_get_comparison_result(self):
        """测试获取比较结果"""
        # 初始状态
        self.assertIsNone(self.comparison_widget.get_comparison_result())

        # 设置比较结果
        test_result = {"quotes": [], "statistics": {}}
        self.comparison_widget._comparison_result = test_result

        # 验证获取结果
        self.assertEqual(self.comparison_widget.get_comparison_result(), test_result)

    def test_get_selected_quotes(self):
        """测试获取选中的报价列表"""
        # 初始状态
        self.assertEqual(len(self.comparison_widget.get_selected_quotes()), 0)

        # 添加报价
        quote_data = {"id": 1, "quote_number": "Q001"}
        self.comparison_widget.add_quote_for_comparison(quote_data)

        # 验证获取结果
        selected_quotes = self.comparison_widget.get_selected_quotes()
        self.assertEqual(len(selected_quotes), 1)
        self.assertEqual(selected_quotes[0], quote_data)

    def test_event_callbacks(self):
        """测试事件回调"""
        # 设置回调函数
        mock_comparison_completed = Mock()
        mock_quote_selected = Mock()

        self.comparison_widget.on_comparison_completed = mock_comparison_completed
        self.comparison_widget.on_quote_selected = mock_quote_selected

        # 准备测试数据
        quote_data1 = {"id": 1, "quote_number": "Q001"}
        quote_data2 = {"id": 2, "quote_number": "Q002"}

        self.comparison_widget.add_quote_for_comparison(quote_data1)
        self.comparison_widget.add_quote_for_comparison(quote_data2)

        # 模拟比较完成
        mock_result = {"quotes": [quote_data1, quote_data2]}
        self.mock_quote_service.compare_quotes.return_value = mock_result

        self.comparison_widget._start_comparison()

        # 验证回调调用
        mock_comparison_completed.assert_called_once_with(mock_result)

    def test_cleanup(self):
        """测试资源清理"""
        # 添加一些数据
        quote_data = {"id": 1, "quote_number": "Q001"}
        self.comparison_widget.add_quote_for_comparison(quote_data)
        self.comparison_widget._comparison_result = {"test": "data"}

        # 执行清理
        self.comparison_widget.cleanup()

        # 验证清理结果
        self.assertEqual(len(self.comparison_widget._quotes_to_compare), 0)
        self.assertIsNone(self.comparison_widget._comparison_result)

    def test_ui_button_states(self):
        """测试UI按钮状态更新"""
        # 初始状态 - 比较按钮应该禁用
        self.assertEqual(self.comparison_widget._compare_btn.cget("state"), "disabled")

        # 添加一个报价 - 比较按钮仍应禁用
        quote_data1 = {"id": 1, "quote_number": "Q001"}
        self.comparison_widget.add_quote_for_comparison(quote_data1)
        self.assertEqual(self.comparison_widget._compare_btn.cget("state"), "disabled")

        # 添加第二个报价 - 比较按钮应该启用
        quote_data2 = {"id": 2, "quote_number": "Q002"}
        self.comparison_widget.add_quote_for_comparison(quote_data2)
        self.assertEqual(self.comparison_widget._compare_btn.cget("state"), "normal")

    def test_comparison_table_creation(self):
        """测试比较表格创建"""
        # 设置比较结果
        self.comparison_widget._comparison_result = {
            "quotes": [
                {
                    "quote_number": "Q001",
                    "customer_name": "客户1",
                    "formatted_total": "¥1,000.00",
                },
                {
                    "quote_number": "Q002",
                    "customer_name": "客户2",
                    "formatted_total": "¥2,000.00",
                },
            ],
            "differences": {"formatted_total": {"description": "金额不同"}},
        }

        # 创建比较表格
        test_frame = ttk.Frame(self.root)
        self.comparison_widget._create_comparison_table(test_frame)

        # 验证表格创建（基本验证）
        children = test_frame.winfo_children()
        self.assertGreater(len(children), 0)


if __name__ == "__main__":
    unittest.main()
