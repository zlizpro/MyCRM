"""供应商对比和评估TTK组件测试.

测试供应商对比功能的各个方面：
- 供应商选择和筛选
- 对比分析功能
- 图表生成和显示
- 评估报告生成
- 数据导出功能
"""

import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.models.supplier import QualityRating, SupplierLevel, SupplierType
from minicrm.ui.panels.supplier_comparison_ttk import SupplierComparisonTTK


class TestSupplierComparisonTTK(unittest.TestCase):
    """供应商对比TTK组件测试类."""

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
                "supplier_type": SupplierType.MANUFACTURER.value,
                "supplier_level": SupplierLevel.STRATEGIC.value,
                "quality_rating": QualityRating.EXCELLENT.value,
                "quality_score": 95.0,
                "delivery_rating": 90.0,
                "service_rating": 88.0,
                "cooperation_years": 5,
                "total_orders": 100,
                "total_amount": 1000000.0,
            },
            {
                "id": 2,
                "name": "供应商B",
                "company_name": "B公司",
                "supplier_type": SupplierType.DISTRIBUTOR.value,
                "supplier_level": SupplierLevel.IMPORTANT.value,
                "quality_rating": QualityRating.GOOD.value,
                "quality_score": 85.0,
                "delivery_rating": 92.0,
                "service_rating": 80.0,
                "cooperation_years": 3,
                "total_orders": 80,
                "total_amount": 800000.0,
            },
            {
                "id": 3,
                "name": "供应商C",
                "company_name": "C公司",
                "supplier_type": SupplierType.WHOLESALER.value,
                "supplier_level": SupplierLevel.NORMAL.value,
                "quality_rating": QualityRating.AVERAGE.value,
                "quality_score": 75.0,
                "delivery_rating": 78.0,
                "service_rating": 82.0,
                "cooperation_years": 2,
                "total_orders": 60,
                "total_amount": 600000.0,
            },
        ]

        # 配置模拟服务的返回值
        self.mock_supplier_service.search_suppliers.return_value = (
            self.mock_suppliers,
            len(self.mock_suppliers),
        )

        # 模拟评估数据
        self.mock_evaluation_data = {
            1: {
                "quality_score": 95.0,
                "delivery_score": 90.0,
                "service_score": 88.0,
                "price_competitiveness": 75.0,
                "innovation_capability": 80.0,
            },
            2: {
                "quality_score": 85.0,
                "delivery_score": 92.0,
                "service_score": 80.0,
                "price_competitiveness": 85.0,
                "innovation_capability": 70.0,
            },
            3: {
                "quality_score": 75.0,
                "delivery_score": 78.0,
                "service_score": 82.0,
                "price_competitiveness": 90.0,
                "innovation_capability": 65.0,
            },
        }

        # 模拟绩效数据
        self.mock_performance_data = {
            1: {
                "on_time_delivery_rate": 95.0,
                "quality_issues": 2,
                "customer_satisfaction": 90.0,
            },
            2: {
                "on_time_delivery_rate": 88.0,
                "quality_issues": 5,
                "customer_satisfaction": 85.0,
            },
            3: {
                "on_time_delivery_rate": 82.0,
                "quality_issues": 8,
                "customer_satisfaction": 78.0,
            },
        }

        def mock_evaluate_quality(supplier_id):
            return self.mock_evaluation_data.get(supplier_id, {})

        def mock_get_performance(supplier_id, time_period=90):
            return self.mock_performance_data.get(supplier_id, {})

        self.mock_supplier_service.evaluate_supplier_quality.side_effect = (
            mock_evaluate_quality
        )
        self.mock_supplier_service.get_supplier_performance_metrics.side_effect = (
            mock_get_performance
        )

        # 创建供应商对比组件
        self.comparison_widget = SupplierComparisonTTK(
            self.root, self.mock_supplier_service
        )

    def tearDown(self):
        """测试后清理."""
        if self.comparison_widget:
            self.comparison_widget.cleanup()
        self.root.destroy()

    def test_widget_initialization(self):
        """测试组件初始化."""
        # 验证组件创建成功
        self.assertIsNotNone(self.comparison_widget)
        self.assertEqual(
            self.comparison_widget._supplier_service, self.mock_supplier_service
        )

        # 验证UI组件存在
        self.assertIsNotNone(self.comparison_widget._search_entry)
        self.assertIsNotNone(self.comparison_widget._type_filter)
        self.assertIsNotNone(self.comparison_widget._quality_filter)
        self.assertIsNotNone(self.comparison_widget._available_listbox)
        self.assertIsNotNone(self.comparison_widget._selected_listbox)

        # 验证数据加载
        self.mock_supplier_service.search_suppliers.assert_called_once()
        self.assertEqual(
            len(self.comparison_widget._available_suppliers), len(self.mock_suppliers)
        )

    def test_supplier_filtering(self):
        """测试供应商筛选功能."""
        # 测试搜索筛选
        self.comparison_widget._search_entry.insert(0, "供应商A")
        self.comparison_widget._on_search_changed(None)

        # 验证筛选结果
        self.comparison_widget._update_available_listbox()
        # 由于是模拟测试，这里主要验证方法调用

        # 测试类型筛选
        self.comparison_widget._type_filter.set(SupplierType.MANUFACTURER.value)
        self.comparison_widget._on_filter_changed(None)

        # 测试质量等级筛选
        self.comparison_widget._quality_filter.set(QualityRating.EXCELLENT.value)
        self.comparison_widget._on_filter_changed(None)

    def test_supplier_selection(self):
        """测试供应商选择功能."""
        # 模拟选择供应商
        self.comparison_widget._filtered_suppliers = self.mock_suppliers[:2]

        # 模拟选择第一个供应商
        self.comparison_widget._available_listbox.selection_set(0)
        self.comparison_widget._add_suppliers()

        # 验证供应商被添加到选择列表
        self.assertEqual(len(self.comparison_widget._selected_suppliers), 1)
        self.assertEqual(
            self.comparison_widget._selected_suppliers[0]["id"],
            self.mock_suppliers[0]["id"],
        )

        # 测试移除供应商
        self.comparison_widget._selected_listbox.selection_set(0)
        self.comparison_widget._remove_suppliers()

        # 验证供应商被移除
        self.assertEqual(len(self.comparison_widget._selected_suppliers), 0)

    def test_supplier_selection_limit(self):
        """测试供应商选择数量限制."""
        # 添加4个供应商（达到限制）
        self.comparison_widget._selected_suppliers = self.mock_suppliers[:4]

        # 尝试添加第5个供应商
        self.comparison_widget._filtered_suppliers = [self.mock_suppliers[0]]
        self.comparison_widget._available_listbox.selection_set(0)

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.comparison_widget._add_suppliers()
            mock_warning.assert_called_once()

    def test_clear_selection(self):
        """测试清空选择功能."""
        # 先添加一些供应商
        self.comparison_widget._selected_suppliers = self.mock_suppliers[:2]

        # 清空选择
        self.comparison_widget._clear_selection()

        # 验证选择被清空
        self.assertEqual(len(self.comparison_widget._selected_suppliers), 0)

    def test_comparison_analysis(self):
        """测试对比分析功能."""
        # 设置选中的供应商
        self.comparison_widget._selected_suppliers = self.mock_suppliers[:2]

        # 执行对比分析
        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.comparison_widget._start_comparison()

            # 验证服务方法被调用
            self.assertTrue(self.mock_supplier_service.evaluate_supplier_quality.called)
            self.assertTrue(
                self.mock_supplier_service.get_supplier_performance_metrics.called
            )

            # 验证对比数据被设置
            self.assertIsNotNone(self.comparison_widget._comparison_data)
            self.assertEqual(len(self.comparison_widget._comparison_data), 2)

            # 验证成功消息
            mock_info.assert_called_once()

    def test_comparison_insufficient_suppliers(self):
        """测试供应商数量不足时的对比分析."""
        # 只选择一个供应商
        self.comparison_widget._selected_suppliers = [self.mock_suppliers[0]]

        with patch("tkinter.messagebox.showwarning") as mock_warning:
            self.comparison_widget._start_comparison()
            mock_warning.assert_called_once()

    def test_metric_value_extraction(self):
        """测试指标值提取功能."""
        # 准备测试数据
        supplier_data = {
            "basic_info": {"name": "测试供应商", "quality_score": 85.5},
            "evaluation": {"delivery_score": 90.0},
            "performance": {"customer_satisfaction": 88.0},
        }

        # 测试基本信息指标
        value = self.comparison_widget._get_metric_value(supplier_data, "name")
        self.assertEqual(value, "测试供应商")

        value = self.comparison_widget._get_metric_value(supplier_data, "quality_score")
        self.assertEqual(value, "85.50")

        # 测试评估指标
        value = self.comparison_widget._get_metric_value(
            supplier_data, "delivery_score"
        )
        self.assertEqual(value, "90.00")

        # 测试绩效指标
        value = self.comparison_widget._get_metric_value(
            supplier_data, "customer_satisfaction"
        )
        self.assertEqual(value, "88.00")

        # 测试不存在的指标
        value = self.comparison_widget._get_metric_value(supplier_data, "nonexistent")
        self.assertEqual(value, "-")

    def test_safe_float_conversion(self):
        """测试安全浮点数转换功能."""
        # 测试正常数值
        self.assertEqual(self.comparison_widget._safe_float(85.5), 85.5)
        self.assertEqual(self.comparison_widget._safe_float("90.0"), 90.0)
        self.assertEqual(self.comparison_widget._safe_float(100), 100.0)

        # 测试异常值
        self.assertEqual(self.comparison_widget._safe_float(""), 0.0)
        self.assertEqual(self.comparison_widget._safe_float(None), 0.0)
        self.assertEqual(self.comparison_widget._safe_float("abc"), 0.0)

        # 测试带单位的字符串
        self.assertEqual(self.comparison_widget._safe_float("85.5分"), 85.5)

    @patch("matplotlib.pyplot.subplots")
    def test_chart_creation(self, mock_subplots):
        """测试图表创建功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
                "performance": self.mock_performance_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
                "performance": self.mock_performance_data[2],
            },
        }

        # 模拟matplotlib组件
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # 创建图表组件的模拟
        self.comparison_widget._chart_widget = Mock()

        # 测试雷达图创建
        self.comparison_widget._chart_type = Mock()
        self.comparison_widget._chart_type.get.return_value = "雷达图"
        self.comparison_widget._create_radar_chart()

        # 验证matplotlib被调用
        mock_subplots.assert_called()

        # 测试柱状图创建
        self.comparison_widget._chart_type.get.return_value = "柱状图"
        self.comparison_widget._create_bar_chart()

        # 测试折线图创建
        self.comparison_widget._chart_type.get.return_value = "折线图"
        self.comparison_widget._create_line_chart()

        # 测试散点图创建
        self.comparison_widget._chart_type.get.return_value = "散点图"
        self.comparison_widget._create_scatter_chart()

    def test_best_supplier_finding(self):
        """测试最佳供应商查找功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 查找最佳供应商
        best_supplier = self.comparison_widget._find_best_supplier()

        # 验证结果
        self.assertIsNotNone(best_supplier)
        self.assertEqual(best_supplier["name"], "供应商A")  # 供应商A评分最高
        self.assertGreater(best_supplier["overall_score"], 0)

    def test_dimension_best_finding(self):
        """测试维度最佳供应商查找功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 查找质量评分最佳供应商
        best_quality = self.comparison_widget._find_best_in_dimension("quality_score")
        self.assertIsNotNone(best_quality)
        self.assertEqual(best_quality["name"], "供应商A")  # 供应商A质量评分最高

        # 查找交期评分最佳供应商
        best_delivery = self.comparison_widget._find_best_in_dimension("delivery_score")
        self.assertIsNotNone(best_delivery)
        self.assertEqual(best_delivery["name"], "供应商B")  # 供应商B交期评分最高

    def test_risk_assessment(self):
        """测试风险评估功能."""
        # 设置对比数据（包含低分供应商）
        low_score_evaluation = {
            "quality_score": 50.0,  # 低质量评分
            "delivery_score": 60.0,  # 低交期评分
            "service_score": 70.0,
        }

        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": {"name": "低分供应商", "cooperation_years": 0},
                "evaluation": low_score_evaluation,
            },
        }

        # 评估风险
        risks = self.comparison_widget._assess_risks()

        # 验证风险识别
        self.assertGreater(len(risks), 0)
        self.assertTrue(any("质量风险" in risk for risk in risks))
        self.assertTrue(any("交期" in risk for risk in risks))
        self.assertTrue(any("合作时间较短" in risk for risk in risks))

    def test_recommendations_generation(self):
        """测试建议生成功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 生成建议
        recommendations = self.comparison_widget._generate_recommendations()

        # 验证建议内容
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("建议优先选择" in rec for rec in recommendations))
        self.assertTrue(any("多供应商策略" in rec for rec in recommendations))
        self.assertTrue(any("定期重新评估" in rec for rec in recommendations))

    def test_evaluation_report_generation(self):
        """测试评估报告生成功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 创建报告文本组件的模拟
        self.comparison_widget._report_text = Mock()

        with patch("tkinter.messagebox.showinfo") as mock_info:
            self.comparison_widget._generate_evaluation_report()

            # 验证报告生成
            self.assertIsNotNone(self.comparison_widget._evaluation_results)
            self.assertIn("report_content", self.comparison_widget._evaluation_results)
            mock_info.assert_called_once()

    def test_report_content_building(self):
        """测试报告内容构建功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
        }

        # 构建报告内容
        report_content = self.comparison_widget._build_evaluation_report()

        # 验证报告内容
        self.assertIsInstance(report_content, str)
        self.assertIn("供应商对比评估报告", report_content)
        self.assertIn("执行摘要", report_content)
        self.assertIn("供应商详细分析", report_content)
        self.assertIn("对比分析结果", report_content)
        self.assertIn("风险评估", report_content)
        self.assertIn("建议和结论", report_content)

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_csv_export(self, mock_filedialog):
        """测试CSV导出功能."""
        # 设置对比数据
        self.comparison_widget._comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
        }

        # 模拟文件对话框
        mock_filedialog.return_value = "test_export.csv"

        with patch("builtins.open", create=True) as mock_open:
            with patch("csv.writer") as mock_writer:
                with patch("tkinter.messagebox.showinfo") as mock_info:
                    self.comparison_widget._export_to_csv()

                    # 验证文件操作
                    mock_open.assert_called_once()
                    mock_writer.assert_called_once()
                    mock_info.assert_called_once()

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_report_export(self, mock_filedialog):
        """测试报告导出功能."""
        # 设置评估结果
        self.comparison_widget._evaluation_results = {
            "report_content": "测试报告内容",
            "generated_at": "2024-01-01T00:00:00",
        }

        # 模拟文件对话框
        mock_filedialog.return_value = "test_report.txt"

        with patch("builtins.open", create=True) as mock_open:
            with patch("tkinter.messagebox.showinfo") as mock_info:
                self.comparison_widget._export_evaluation_report()

                # 验证文件操作
                mock_open.assert_called_once()
                mock_info.assert_called_once()

    def test_reset_comparison(self):
        """测试重置对比功能."""
        # 设置一些数据
        self.comparison_widget._selected_suppliers = self.mock_suppliers[:2]
        self.comparison_widget._comparison_data = {"test": "data"}
        self.comparison_widget._evaluation_results = {"test": "results"}

        # 创建UI组件的模拟
        self.comparison_widget._comparison_table = Mock()
        self.comparison_widget._chart_widget = Mock()
        self.comparison_widget._report_text = Mock()

        with patch("tkinter.messagebox.askyesno", return_value=True):
            with patch("tkinter.messagebox.showinfo") as mock_info:
                self.comparison_widget._reset_comparison()

                # 验证数据被清空
                self.assertEqual(len(self.comparison_widget._selected_suppliers), 0)
                self.assertEqual(len(self.comparison_widget._comparison_data), 0)
                self.assertEqual(len(self.comparison_widget._evaluation_results), 0)

                # 验证UI被重置
                self.comparison_widget._comparison_table.load_data.assert_called_with(
                    []
                )
                self.comparison_widget._chart_widget.clear.assert_called_once()
                self.comparison_widget._report_text.delete.assert_called_once()

                mock_info.assert_called_once()

    def test_public_interface_methods(self):
        """测试公共接口方法."""
        # 测试加载指定供应商进行对比
        supplier_ids = [1, 2]
        self.comparison_widget.load_suppliers_for_comparison(supplier_ids)

        # 验证供应商被加载
        self.assertEqual(len(self.comparison_widget._selected_suppliers), 2)
        self.assertEqual(self.comparison_widget._selected_suppliers[0]["id"], 1)
        self.assertEqual(self.comparison_widget._selected_suppliers[1]["id"], 2)

        # 测试获取对比结果
        results = self.comparison_widget.get_comparison_results()
        self.assertIn("selected_suppliers", results)
        self.assertIn("comparison_data", results)
        self.assertIn("evaluation_results", results)

    def test_error_handling(self):
        """测试错误处理."""
        # 测试服务异常处理
        self.mock_supplier_service.search_suppliers.side_effect = Exception("服务异常")

        with patch("tkinter.messagebox.showerror") as mock_error:
            # 重新创建组件以触发异常
            try:
                SupplierComparisonTTK(self.root, self.mock_supplier_service)
            except Exception:
                pass  # 预期的异常

            # 验证错误消息显示
            mock_error.assert_called()

    def test_widget_cleanup(self):
        """测试组件清理功能."""
        # 创建图表组件的模拟
        self.comparison_widget._chart_widget = Mock()

        # 执行清理
        self.comparison_widget.cleanup()

        # 验证图表组件被清理
        self.comparison_widget._chart_widget.cleanup.assert_called_once()


if __name__ == "__main__":
    unittest.main()
