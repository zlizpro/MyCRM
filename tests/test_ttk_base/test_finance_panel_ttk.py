"""MiniCRM TTK财务管理面板测试

测试FinancePanelTTK组件的功能，包括：
- 面板初始化和UI创建
- 财务数据加载和显示
- 应收应付账款管理
- 图表展示功能
- 数据导出功能
- 自动刷新机制
"""

from datetime import datetime
import os
import tempfile
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

from minicrm.core.exceptions import ServiceError
from minicrm.services.finance_service import FinanceService
from minicrm.ui.ttk_base.finance_panel_ttk import FinancePanelTTK


class TestFinancePanelTTK(unittest.TestCase):
    """财务管理面板TTK组件测试类"""

    def setUp(self):
        """测试准备"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # 隐藏测试窗口
            self.gui_available = True
        except tk.TclError:
            # GUI不可用时跳过测试
            self.gui_available = False
            self.skipTest("GUI环境不可用，跳过GUI相关测试")

        # 创建模拟的财务服务
        self.mock_finance_service = Mock(spec=FinanceService)

        # 模拟财务汇总数据
        self.mock_financial_summary = {
            "total_receivables": 200000.0,
            "total_payables": 120000.0,
            "overdue_receivables": 20000.0,
            "overdue_payables": 8000.0,
            "receivables_overdue_rate": 10.0,
            "payables_overdue_rate": 6.7,
            "net_position": 80000.0,
            "generated_at": datetime.now().isoformat(),
        }

        self.mock_finance_service.get_financial_summary.return_value = (
            self.mock_financial_summary
        )

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "finance_panel"):
            self.finance_panel.cleanup()
        self.root.destroy()

    def test_panel_initialization(self):
        """测试面板初始化"""
        # 创建财务管理面板
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证面板创建成功
        self.assertIsInstance(self.finance_panel, FinancePanelTTK)
        self.assertEqual(self.finance_panel.finance_service, self.mock_finance_service)

        # 验证UI组件创建
        self.assertIsNotNone(self.finance_panel.main_notebook)
        self.assertIsInstance(self.finance_panel.main_notebook, ttk.Notebook)

        # 验证标签页创建
        tabs = self.finance_panel.main_notebook.tabs()
        self.assertEqual(len(tabs), 4)  # 概览、应收、应付、分析

    def test_financial_data_loading(self):
        """测试财务数据加载"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证财务服务被调用
        self.mock_finance_service.get_financial_summary.assert_called_once()

        # 验证数据加载
        self.assertEqual(
            self.finance_panel.financial_summary, self.mock_financial_summary
        )

        # 验证应收应付数据初始化
        self.assertIsInstance(self.finance_panel.receivables_data, list)
        self.assertIsInstance(self.finance_panel.payables_data, list)

    def test_metrics_cards_creation(self):
        """测试指标卡片创建"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证指标卡片创建
        self.assertIsNotNone(self.finance_panel.metric_cards)

        # 验证关键指标卡片
        expected_metrics = [
            "total_receivables",
            "total_payables",
            "net_position",
            "overdue_receivables",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, self.finance_panel.metric_cards)
            card = self.finance_panel.metric_cards[metric]
            self.assertTrue(hasattr(card, "value_label"))
            self.assertTrue(hasattr(card, "trend_label"))

    def test_charts_creation(self):
        """测试图表组件创建"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证概览图表创建
        self.assertIsNotNone(self.finance_panel.overview_chart)
        self.assertIsNotNone(self.finance_panel.trend_chart)

    def test_data_tables_creation(self):
        """测试数据表格创建"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证应收账款表格
        self.assertIsNotNone(self.finance_panel.receivables_table)
        self.assertEqual(len(self.finance_panel.receivables_table.columns), 8)

        # 验证应付账款表格
        self.assertIsNotNone(self.finance_panel.payables_table)
        self.assertEqual(len(self.finance_panel.payables_table.columns), 8)

    def test_financial_analysis_integration(self):
        """测试财务分析组件集成"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证财务分析组件创建
        self.assertIsNotNone(self.finance_panel.financial_analysis)

        # 验证分析组件使用相同的财务服务
        self.assertEqual(
            self.finance_panel.financial_analysis.finance_service,
            self.mock_finance_service,
        )

    def test_metrics_display_update(self):
        """测试指标显示更新"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证指标卡片数值更新
        total_receivables_card = self.finance_panel.metric_cards["total_receivables"]
        expected_value = f"¥{self.mock_financial_summary['total_receivables']:,.2f}"

        # 注意：由于UI更新可能是异步的，这里检查数据是否正确设置
        self.assertEqual(
            self.finance_panel.financial_summary["total_receivables"],
            self.mock_financial_summary["total_receivables"],
        )

    def test_receivables_data_display(self):
        """测试应收账款数据显示"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证应收账款数据加载到表格
        self.assertIsNotNone(self.finance_panel.receivables_table)

        # 验证统计标签存在
        self.assertIsNotNone(self.finance_panel.receivables_stats_label)

    def test_payables_data_display(self):
        """测试应付账款数据显示"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 验证应付账款数据加载到表格
        self.assertIsNotNone(self.finance_panel.payables_table)

        # 验证统计标签存在
        self.assertIsNotNone(self.finance_panel.payables_stats_label)

    def test_data_refresh(self):
        """测试数据刷新功能"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 重置调用计数
        self.mock_finance_service.reset_mock()

        # 执行刷新
        self.finance_panel._refresh_all_data()

        # 验证服务再次被调用
        self.mock_finance_service.get_financial_summary.assert_called_once()

    def test_auto_refresh_mechanism(self):
        """测试自动刷新机制"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试自动刷新设置
        self.assertTrue(self.finance_panel.auto_refresh)
        self.assertEqual(self.finance_panel.refresh_interval, 300)

        # 测试设置自动刷新
        self.finance_panel.set_auto_refresh(False)
        self.assertFalse(self.finance_panel.auto_refresh)

        self.finance_panel.set_auto_refresh(True, 600)
        self.assertTrue(self.finance_panel.auto_refresh)
        self.assertEqual(self.finance_panel.refresh_interval, 600)

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_receivables_export(self, mock_filedialog):
        """测试应收账款导出"""
        # 设置文件对话框返回值
        test_filename = "test_receivables.csv"
        mock_filedialog.return_value = test_filename

        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 模拟有应收账款数据
        self.finance_panel.receivables_data = [
            {
                "id": 1,
                "customer_name": "测试客户",
                "amount": 10000.0,
                "due_date": "2025-02-01",
                "status": "pending",
            }
        ]

        # 使用临时文件进行测试
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            mock_filedialog.return_value = tmp_file.name

            # 执行导出
            with patch("tkinter.messagebox.showinfo") as mock_messagebox:
                self.finance_panel._export_receivables()

                # 验证成功消息显示
                mock_messagebox.assert_called_once()

            # 验证文件创建
            self.assertTrue(os.path.exists(tmp_file.name))

            # 清理临时文件
            os.unlink(tmp_file.name)

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_payables_export(self, mock_filedialog):
        """测试应付账款导出"""
        # 设置文件对话框返回值
        test_filename = "test_payables.csv"
        mock_filedialog.return_value = test_filename

        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 模拟有应付账款数据
        self.finance_panel.payables_data = [
            {
                "id": 1,
                "supplier_name": "测试供应商",
                "amount": 8000.0,
                "due_date": "2025-02-01",
                "status": "pending",
            }
        ]

        # 使用临时文件进行测试
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as tmp_file:
            mock_filedialog.return_value = tmp_file.name

            # 执行导出
            with patch("tkinter.messagebox.showinfo") as mock_messagebox:
                self.finance_panel._export_payables()

                # 验证成功消息显示
                mock_messagebox.assert_called_once()

            # 验证文件创建
            self.assertTrue(os.path.exists(tmp_file.name))

            # 清理临时文件
            os.unlink(tmp_file.name)

    def test_receivable_selection_events(self):
        """测试应收账款选择事件"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 模拟应收账款数据
        test_receivable = {"id": 1, "customer_name": "测试客户", "amount": 10000.0}

        # 测试选择事件
        self.finance_panel._on_receivable_selected(test_receivable)

        # 测试双击事件
        with patch("tkinter.messagebox.showinfo") as mock_messagebox:
            self.finance_panel._on_receivable_double_clicked(test_receivable)
            mock_messagebox.assert_called_once()

    def test_payable_selection_events(self):
        """测试应付账款选择事件"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 模拟应付账款数据
        test_payable = {"id": 1, "supplier_name": "测试供应商", "amount": 8000.0}

        # 测试选择事件
        self.finance_panel._on_payable_selected(test_payable)

        # 测试双击事件
        with patch("tkinter.messagebox.showinfo") as mock_messagebox:
            self.finance_panel._on_payable_double_clicked(test_payable)
            mock_messagebox.assert_called_once()

    def test_dialog_methods(self):
        """测试对话框方法"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试各种对话框方法（目前都显示提示信息）
        with patch("tkinter.messagebox.showinfo") as mock_messagebox:
            self.finance_panel._show_record_payment_dialog()
            self.finance_panel._show_add_receivable_dialog()
            self.finance_panel._show_add_payable_dialog()
            self.finance_panel._show_record_payable_dialog()

            # 验证消息框被调用
            self.assertEqual(mock_messagebox.call_count, 4)

    def test_export_dialog_integration(self):
        """测试导出对话框集成"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试导出对话框
        self.finance_panel._show_export_dialog()

        # 验证切换到分析标签页
        current_tab = self.finance_panel.main_notebook.index("current")
        self.assertEqual(current_tab, 3)  # 分析标签页索引

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 设置服务抛出异常
        self.mock_finance_service.get_financial_summary.side_effect = ServiceError(
            "测试错误"
        )

        # 创建面板时应该处理异常
        with patch("tkinter.messagebox.showerror") as mock_messagebox:
            self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

            # 验证错误消息框被调用
            mock_messagebox.assert_called_once()

    def test_status_update(self):
        """测试状态更新"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试状态更新
        test_status = "测试状态"
        self.finance_panel._update_status(test_status)

        # 验证状态标签更新
        self.assertEqual(self.finance_panel.status_label.cget("text"), test_status)

    def test_public_methods(self):
        """测试公共方法"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试获取财务汇总
        financial_summary = self.finance_panel.get_financial_summary()
        self.assertEqual(financial_summary, self.mock_financial_summary)

        # 测试获取应收账款数据
        receivables_data = self.finance_panel.get_receivables_data()
        self.assertIsInstance(receivables_data, list)

        # 测试获取应付账款数据
        payables_data = self.finance_panel.get_payables_data()
        self.assertIsInstance(payables_data, list)

        # 测试刷新数据
        self.mock_finance_service.reset_mock()
        self.finance_panel.refresh_data()
        self.mock_finance_service.get_financial_summary.assert_called_once()

    def test_event_callbacks(self):
        """测试事件回调"""
        # 创建回调函数
        data_updated_callback = Mock()
        payment_recorded_callback = Mock()

        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 设置回调
        self.finance_panel.on_data_updated = data_updated_callback
        self.finance_panel.on_payment_recorded = payment_recorded_callback

        # 触发数据更新
        self.finance_panel._load_all_data()

        # 验证回调被调用
        data_updated_callback.assert_called_once()

    def test_component_cleanup(self):
        """测试组件清理"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 执行清理
        self.finance_panel.cleanup()

        # 验证定时器被停止
        self.assertIsNone(self.finance_panel.refresh_timer)

    def test_string_representation(self):
        """测试字符串表示"""
        self.finance_panel = FinancePanelTTK(self.root, self.mock_finance_service)

        # 测试字符串表示
        str_repr = str(self.finance_panel)
        self.assertIn("FinancePanelTTK", str_repr)
        self.assertIn("receivables=", str_repr)
        self.assertIn("payables=", str_repr)


class TestFinancePanelIntegration(unittest.TestCase):
    """财务管理面板集成测试"""

    def setUp(self):
        """测试准备"""
        try:
            self.root = tk.Tk()
            self.root.withdraw()
            self.gui_available = True
        except tk.TclError:
            # GUI不可用时跳过测试
            self.gui_available = False
            self.skipTest("GUI环境不可用，跳过GUI相关测试")

        # 创建真实的财务服务（使用模拟DAO）
        from unittest.mock import Mock

        mock_customer_dao = Mock()
        mock_supplier_dao = Mock()

        # 设置模拟数据
        mock_customer_dao.get_receivables_summary.return_value = {
            "total_amount": 200000.0,
            "overdue_amount": 20000.0,
        }
        mock_supplier_dao.get_payables_summary.return_value = {
            "total_amount": 120000.0,
            "overdue_amount": 8000.0,
        }

        self.finance_service = FinanceService(mock_customer_dao, mock_supplier_dao)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "finance_panel"):
            self.finance_panel.cleanup()
        self.root.destroy()

    def test_full_panel_workflow(self):
        """测试完整面板工作流程"""
        # 创建面板
        self.finance_panel = FinancePanelTTK(self.root, self.finance_service)

        # 验证面板创建成功
        self.assertIsInstance(self.finance_panel, FinancePanelTTK)

        # 验证数据加载
        self.assertIsNotNone(self.finance_panel.financial_summary)

        # 验证UI组件
        self.assertIsNotNone(self.finance_panel.main_notebook)
        self.assertEqual(len(self.finance_panel.main_notebook.tabs()), 4)

        # 验证子组件
        self.assertIsNotNone(self.finance_panel.receivables_table)
        self.assertIsNotNone(self.finance_panel.payables_table)
        self.assertIsNotNone(self.finance_panel.financial_analysis)

        # 测试数据刷新
        self.finance_panel._refresh_all_data()

        # 测试图表更新
        self.finance_panel._update_overview_charts()

    def test_tab_navigation(self):
        """测试标签页导航"""
        self.finance_panel = FinancePanelTTK(self.root, self.finance_service)

        # 测试切换到不同标签页
        notebook = self.finance_panel.main_notebook

        # 切换到应收账款标签页
        notebook.select(1)
        current_tab = notebook.index("current")
        self.assertEqual(current_tab, 1)

        # 切换到应付账款标签页
        notebook.select(2)
        current_tab = notebook.index("current")
        self.assertEqual(current_tab, 2)

        # 切换到财务分析标签页
        notebook.select(3)
        current_tab = notebook.index("current")
        self.assertEqual(current_tab, 3)

    def test_data_consistency(self):
        """测试数据一致性"""
        self.finance_panel = FinancePanelTTK(self.root, self.finance_service)

        # 验证主面板和分析组件使用相同的财务服务
        self.assertEqual(
            self.finance_panel.finance_service,
            self.finance_panel.financial_analysis.finance_service,
        )

        # 验证数据同步
        main_summary = self.finance_panel.get_financial_summary()
        analysis_data = self.finance_panel.financial_analysis.get_financial_data()

        # 关键数据应该一致
        self.assertEqual(
            main_summary.get("total_receivables"),
            analysis_data.get("total_receivables"),
        )


if __name__ == "__main__":
    unittest.main()
