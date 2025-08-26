"""MiniCRM TTK财务分析组件测试

测试FinancialAnalysisTTK组件的功能，包括：
- 组件初始化和UI创建
- 财务数据加载和分析
- 图表更新和显示
- 导出功能测试
- 自动刷新机制测试
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
from minicrm.ui.ttk_base.financial_analysis_ttk import FinancialAnalysisTTK


class TestFinancialAnalysisTTK(unittest.TestCase):
    """财务分析TTK组件测试类"""

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

        # 模拟财务数据
        self.mock_financial_data = {
            "total_receivables": 150000.0,
            "total_payables": 80000.0,
            "overdue_receivables": 15000.0,
            "receivables_overdue_rate": 10.0,
            "payables_overdue_rate": 5.0,
            "net_position": 70000.0,
            "generated_at": datetime.now().isoformat(),
        }

        self.mock_finance_service.get_financial_summary.return_value = (
            self.mock_financial_data
        )

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "financial_analysis"):
            self.financial_analysis.cleanup()
        self.root.destroy()

    def test_component_initialization(self):
        """测试组件初始化"""
        # 创建财务分析组件
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 验证组件创建成功
        self.assertIsInstance(self.financial_analysis, FinancialAnalysisTTK)
        self.assertEqual(
            self.financial_analysis.finance_service, self.mock_finance_service
        )

        # 验证UI组件创建
        self.assertIsNotNone(self.financial_analysis.notebook)
        self.assertIsInstance(self.financial_analysis.notebook, ttk.Notebook)

        # 验证标签页创建
        tabs = self.financial_analysis.notebook.tabs()
        self.assertEqual(len(tabs), 3)  # 概览、图表、导出

    def test_financial_data_loading(self):
        """测试财务数据加载"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 验证财务服务被调用
        self.mock_finance_service.get_financial_summary.assert_called_once()

        # 验证数据加载
        self.assertEqual(
            self.financial_analysis.financial_data, self.mock_financial_data
        )

        # 验证分析结果生成
        self.assertIsNotNone(self.financial_analysis.analysis_results)
        self.assertIn("total_receivables", self.financial_analysis.analysis_results)
        self.assertIn("net_position", self.financial_analysis.analysis_results)

    def test_financial_analysis_calculation(self):
        """测试财务分析计算"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        analysis = self.financial_analysis.analysis_results

        # 验证关键指标计算
        self.assertEqual(analysis["total_receivables"], 150000.0)
        self.assertEqual(analysis["total_payables"], 80000.0)
        self.assertEqual(analysis["net_position"], 70000.0)
        self.assertEqual(analysis["overdue_receivables"], 15000.0)

        # 验证逾期率计算
        expected_rate = (15000.0 / 150000.0) * 100
        self.assertAlmostEqual(
            analysis["receivables_overdue_rate"], expected_rate, places=1
        )

        # 验证现金流估算
        expected_cash_flow = 70000.0 * 0.8
        self.assertEqual(analysis["cash_flow"], expected_cash_flow)

    def test_risk_warning_generation(self):
        """测试风险预警生成"""
        # 测试高风险情况
        high_risk_data = self.mock_financial_data.copy()
        high_risk_data["receivables_overdue_rate"] = 25.0  # 高逾期率
        high_risk_data["net_position"] = -50000.0  # 负净头寸
        high_risk_data["overdue_receivables"] = 200000.0  # 大额逾期

        self.mock_finance_service.get_financial_summary.return_value = high_risk_data

        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        warnings = self.financial_analysis.analysis_results.get("risk_warnings", [])

        # 验证风险预警生成
        self.assertTrue(len(warnings) > 0)

        # 检查特定预警
        warning_text = " ".join(warnings)
        self.assertIn("逾期率过高", warning_text)
        self.assertIn("净头寸为负", warning_text)
        self.assertIn("逾期应收金额较大", warning_text)

    def test_chart_data_creation(self):
        """测试图表数据创建"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 验证图表组件创建
        self.assertIsNotNone(self.financial_analysis.summary_chart)
        self.assertIsNotNone(self.financial_analysis.trend_chart)
        self.assertIsNotNone(self.financial_analysis.comparison_chart)

    @patch("minicrm.ui.ttk_base.financial_analysis_ttk.FinancialExcelExporter")
    def test_excel_export(self, mock_excel_exporter_class):
        """测试Excel导出功能"""
        # 设置模拟导出器
        mock_exporter = Mock()
        mock_exporter.export_financial_report.return_value = True
        mock_excel_exporter_class.return_value = mock_exporter

        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 测试导出
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_file:
            success = self.financial_analysis._export_to_excel(tmp_file.name)

            # 验证导出成功
            self.assertTrue(success)

            # 验证导出器被调用
            mock_exporter.export_financial_report.assert_called_once()

            # 清理临时文件
            os.unlink(tmp_file.name)

    @patch("minicrm.ui.ttk_base.financial_analysis_ttk.QuotePDFExportService")
    def test_pdf_export(self, mock_pdf_service_class):
        """测试PDF导出功能"""
        # 设置模拟PDF服务
        mock_pdf_service = Mock()
        mock_pdf_service.export_financial_report.return_value = True
        mock_pdf_service_class.return_value = mock_pdf_service

        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 测试PDF导出
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            success = self.financial_analysis._export_to_pdf(tmp_file.name)

            # 验证导出成功
            self.assertTrue(success)

            # 验证PDF服务被调用
            mock_pdf_service.export_financial_report.assert_called_once()

            # 清理临时文件
            os.unlink(tmp_file.name)

    def test_data_refresh(self):
        """测试数据刷新功能"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 重置调用计数
        self.mock_finance_service.reset_mock()

        # 执行刷新
        self.financial_analysis._refresh_data()

        # 验证服务再次被调用
        self.mock_finance_service.get_financial_summary.assert_called_once()

    def test_auto_refresh_toggle(self):
        """测试自动刷新开关"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 测试关闭自动刷新
        self.financial_analysis.auto_refresh_var.set(False)
        self.financial_analysis._toggle_auto_refresh()

        self.assertFalse(self.financial_analysis.auto_refresh)

        # 测试开启自动刷新
        self.financial_analysis.auto_refresh_var.set(True)
        self.financial_analysis._toggle_auto_refresh()

        self.assertTrue(self.financial_analysis.auto_refresh)

    def test_chart_type_change(self):
        """测试图表类型变化"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 模拟图表类型变化事件
        self.financial_analysis.chart_type_var.set("line")

        # 创建模拟事件
        mock_event = Mock()

        # 调用事件处理器
        self.financial_analysis._on_chart_type_changed(mock_event)

        # 验证图表类型更新
        self.assertEqual(self.financial_analysis.chart_type_var.get(), "line")

    def test_time_range_change(self):
        """测试时间范围变化"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 模拟时间范围变化
        self.financial_analysis.time_range_var.set("90")

        # 创建模拟事件
        mock_event = Mock()

        # 调用事件处理器
        self.financial_analysis._on_time_range_changed(mock_event)

        # 验证时间范围更新
        self.assertEqual(self.financial_analysis.time_range_var.get(), "90")

    def test_export_format_selection(self):
        """测试导出格式选择"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 设置导出格式
        self.financial_analysis.export_formats["excel"].set(True)
        self.financial_analysis.export_formats["pdf"].set(True)
        self.financial_analysis.export_formats["csv"].set(False)

        # 获取选中的格式
        selected_formats = [
            fmt
            for fmt, var in self.financial_analysis.export_formats.items()
            if var.get()
        ]

        # 验证格式选择
        self.assertIn("excel", selected_formats)
        self.assertIn("pdf", selected_formats)
        self.assertNotIn("csv", selected_formats)

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 设置服务抛出异常
        self.mock_finance_service.get_financial_summary.side_effect = ServiceError(
            "测试错误"
        )

        # 创建组件时应该处理异常
        with patch("tkinter.messagebox.showerror") as mock_messagebox:
            self.financial_analysis = FinancialAnalysisTTK(
                self.root, self.mock_finance_service
            )

            # 验证错误消息框被调用
            mock_messagebox.assert_called_once()

    def test_status_update(self):
        """测试状态更新"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 测试状态更新
        test_status = "测试状态"
        self.financial_analysis._update_status(test_status)

        # 验证状态标签更新
        self.assertEqual(self.financial_analysis.status_label.cget("text"), test_status)

    def test_data_getter_methods(self):
        """测试数据获取方法"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 测试获取财务数据
        financial_data = self.financial_analysis.get_financial_data()
        self.assertEqual(financial_data, self.mock_financial_data)

        # 测试获取分析结果
        analysis_results = self.financial_analysis.get_analysis_results()
        self.assertIsInstance(analysis_results, dict)
        self.assertIn("total_receivables", analysis_results)

    def test_refresh_interval_setting(self):
        """测试刷新间隔设置"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 设置新的刷新间隔
        new_interval = 600  # 10分钟
        self.financial_analysis.set_refresh_interval(new_interval)

        # 验证间隔更新
        self.assertEqual(self.financial_analysis.refresh_interval, new_interval)

    def test_component_cleanup(self):
        """测试组件清理"""
        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 执行清理
        self.financial_analysis.cleanup()

        # 验证定时器被停止
        self.assertIsNone(self.financial_analysis.refresh_timer)

    def test_event_callbacks(self):
        """测试事件回调"""
        # 创建回调函数
        data_updated_callback = Mock()
        export_completed_callback = Mock()

        self.financial_analysis = FinancialAnalysisTTK(
            self.root, self.mock_finance_service
        )

        # 设置回调
        self.financial_analysis.on_data_updated = data_updated_callback
        self.financial_analysis.on_export_completed = export_completed_callback

        # 触发数据更新
        self.financial_analysis._load_financial_data()

        # 验证回调被调用
        data_updated_callback.assert_called_once_with(self.mock_financial_data)

        # 触发导出完成
        test_results = {"excel": True, "pdf": False}
        self.financial_analysis._export_completed(test_results)

        # 验证导出回调被调用
        export_completed_callback.assert_called_once_with(test_results)


class TestFinancialAnalysisIntegration(unittest.TestCase):
    """财务分析组件集成测试"""

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
            "total_amount": 150000.0,
            "overdue_amount": 15000.0,
        }
        mock_supplier_dao.get_payables_summary.return_value = {
            "total_amount": 80000.0,
            "overdue_amount": 4000.0,
        }

        self.finance_service = FinanceService(mock_customer_dao, mock_supplier_dao)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "financial_analysis"):
            self.financial_analysis.cleanup()
        self.root.destroy()

    def test_full_component_workflow(self):
        """测试完整组件工作流程"""
        # 创建组件
        self.financial_analysis = FinancialAnalysisTTK(self.root, self.finance_service)

        # 验证组件创建成功
        self.assertIsInstance(self.financial_analysis, FinancialAnalysisTTK)

        # 验证数据加载
        self.assertIsNotNone(self.financial_analysis.financial_data)
        self.assertIsNotNone(self.financial_analysis.analysis_results)

        # 验证UI组件
        self.assertIsNotNone(self.financial_analysis.notebook)
        self.assertEqual(len(self.financial_analysis.notebook.tabs()), 3)

        # 测试数据刷新
        self.financial_analysis._refresh_data()

        # 测试图表更新
        self.financial_analysis._update_charts()

        # 验证组件状态
        self.assertTrue(hasattr(self.financial_analysis, "metrics_labels"))
        self.assertTrue(hasattr(self.financial_analysis, "risk_text"))


if __name__ == "__main__":
    unittest.main()
