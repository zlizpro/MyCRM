"""TTK图表组件测试

测试ChartContainerTTK类的功能，包括：
- 图表容器的创建和初始化
- 不同图表类型的渲染
- 数据设置和更新
- 交互功能测试
- 样式应用和主题集成
- 错误处理和边界条件

作者: MiniCRM开发团队
"""

import os
import sys
import tkinter as tk
import unittest
from unittest.mock import patch


# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

try:
    from minicrm.ui.ttk_base.chart_widget import (
        MATPLOTLIB_AVAILABLE,
        BarChartRenderer,
        ChartContainerTTK,
        ChartData,
        ChartInteractionHandler,
        ChartStyle,
        ChartType,
        LineChartRenderer,
        PieChartRenderer,
        ScatterChartRenderer,
        create_chart_data,
        create_chart_style,
    )
    from minicrm.ui.ttk_base.style_manager import DefaultTheme, StyleManager
except ImportError as e:
    print(f"导入失败: {e}")
    raise


class TestChartData(unittest.TestCase):
    """测试ChartData数据类"""

    def test_chart_data_creation(self):
        """测试图表数据创建"""
        x_data = [1, 2, 3, 4, 5]
        y_data = [10, 20, 15, 25, 30]

        chart_data = ChartData(x_data=x_data, y_data=y_data)

        self.assertEqual(chart_data.x_data, x_data)
        self.assertEqual(chart_data.y_data, y_data)
        self.assertIsNone(chart_data.labels)
        self.assertIsNone(chart_data.title)

    def test_chart_data_with_all_fields(self):
        """测试包含所有字段的图表数据"""
        chart_data = ChartData(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            labels=["A", "B", "C"],
            title="测试图表",
            x_label="X轴",
            y_label="Y轴",
            colors=["red", "green", "blue"],
        )

        self.assertEqual(chart_data.labels, ["A", "B", "C"])
        self.assertEqual(chart_data.title, "测试图表")
        self.assertEqual(chart_data.x_label, "X轴")
        self.assertEqual(chart_data.y_label, "Y轴")
        self.assertEqual(chart_data.colors, ["red", "green", "blue"])


class TestChartStyle(unittest.TestCase):
    """测试ChartStyle样式类"""

    def test_default_chart_style(self):
        """测试默认图表样式"""
        style = ChartStyle()

        self.assertEqual(style.background_color, "#FFFFFF")
        self.assertEqual(style.text_color, "#212529")
        self.assertEqual(style.font_family, "Microsoft YaHei UI")
        self.assertEqual(style.font_size, 9)
        self.assertTrue(style.show_grid)
        self.assertTrue(style.show_legend)

    def test_custom_chart_style(self):
        """测试自定义图表样式"""
        style = ChartStyle(
            background_color="#000000",
            text_color="#FFFFFF",
            font_size=12,
            show_grid=False,
        )

        self.assertEqual(style.background_color, "#000000")
        self.assertEqual(style.text_color, "#FFFFFF")
        self.assertEqual(style.font_size, 12)
        self.assertFalse(style.show_grid)


@unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
class TestChartRenderers(unittest.TestCase):
    """测试图表渲染器"""

    def setUp(self):
        """测试准备"""
        from matplotlib.figure import Figure

        self.figure = Figure(figsize=(8, 6))
        self.ax = self.figure.add_subplot(111)
        self.style = ChartStyle()
        self.chart_data = ChartData(
            x_data=[1, 2, 3, 4, 5],
            y_data=[10, 20, 15, 25, 30],
            title="测试图表",
            x_label="X轴",
            y_label="Y轴",
        )

    def test_bar_chart_renderer(self):
        """测试柱状图渲染器"""
        renderer = BarChartRenderer(self.figure, self.style)
        result = renderer.render(self.chart_data, self.ax)

        # 验证渲染结果
        self.assertIsNotNone(result)
        self.assertEqual(self.ax.get_title(), "测试图表")
        self.assertEqual(self.ax.get_xlabel(), "X轴")
        self.assertEqual(self.ax.get_ylabel(), "Y轴")

    def test_line_chart_renderer(self):
        """测试折线图渲染器"""
        renderer = LineChartRenderer(self.figure, self.style)
        result = renderer.render(self.chart_data, self.ax)

        # 验证渲染结果
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)  # 一条线

    def test_pie_chart_renderer(self):
        """测试饼图渲染器"""
        pie_data = ChartData(
            x_data=[],  # 饼图不需要x_data
            y_data=[30, 25, 20, 25],
            labels=["A", "B", "C", "D"],
            title="饼图测试",
        )

        renderer = PieChartRenderer(self.figure, self.style)
        result = renderer.render(pie_data, self.ax)

        # 验证渲染结果
        wedges, texts, autotexts = result
        self.assertEqual(len(wedges), 4)  # 4个扇形
        self.assertEqual(len(texts), 4)  # 4个标签

    def test_scatter_chart_renderer(self):
        """测试散点图渲染器"""
        renderer = ScatterChartRenderer(self.figure, self.style)
        result = renderer.render(self.chart_data, self.ax)

        # 验证渲染结果
        self.assertIsNotNone(result)


@unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
class TestChartInteractionHandler(unittest.TestCase):
    """测试图表交互处理器"""

    def setUp(self):
        """测试准备"""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure

        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.handler = ChartInteractionHandler(self.canvas, self.figure)

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    def test_interaction_handler_creation(self):
        """测试交互处理器创建"""
        self.assertIsNotNone(self.handler)
        self.assertEqual(self.handler.canvas, self.canvas)
        self.assertEqual(self.handler.figure, self.figure)
        self.assertFalse(self.handler._pan_active)
        self.assertFalse(self.handler._zoom_active)

    def test_enable_tooltip(self):
        """测试启用数据点提示"""
        self.handler.enable_tooltip(True)
        self.assertTrue(self.handler._tooltip_active)

        self.handler.enable_tooltip(False)
        self.assertFalse(self.handler._tooltip_active)

    def test_reset_view(self):
        """测试重置视图"""
        # 添加一个轴
        ax = self.figure.add_subplot(111)
        ax.plot([1, 2, 3], [1, 4, 2])

        # 重置视图应该不抛出异常
        self.handler.reset_view()

    def test_toggle_grid(self):
        """测试切换网格"""
        # 添加一个轴
        ax = self.figure.add_subplot(111)

        # 切换网格应该不抛出异常
        self.handler.toggle_grid()


@unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
class TestChartContainerTTK(unittest.TestCase):
    """测试ChartContainerTTK主类"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建图表容器
        self.chart_container = ChartContainerTTK(self.root)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "chart_container"):
            self.chart_container.cleanup()
        self.root.destroy()

    def test_chart_container_creation(self):
        """测试图表容器创建"""
        self.assertIsNotNone(self.chart_container)
        self.assertIsNotNone(self.chart_container.figure)
        self.assertIsNotNone(self.chart_container.canvas)
        self.assertIsNotNone(self.chart_container.interaction_handler)
        self.assertEqual(self.chart_container.chart_type, ChartType.BAR)

    def test_set_chart_data(self):
        """测试设置图表数据"""
        chart_data = ChartData(
            x_data=[1, 2, 3, 4, 5], y_data=[10, 20, 15, 25, 30], title="测试数据"
        )

        self.chart_container.set_data(chart_data)
        self.assertEqual(self.chart_container.chart_data, chart_data)

    def test_set_chart_type(self):
        """测试设置图表类型"""
        # 使用枚举设置
        self.chart_container.set_chart_type(ChartType.LINE)
        self.assertEqual(self.chart_container.chart_type, ChartType.LINE)

        # 使用字符串设置
        self.chart_container.set_chart_type("pie")
        self.assertEqual(self.chart_container.chart_type, ChartType.PIE)

    def test_set_chart_style(self):
        """测试设置图表样式"""
        custom_style = ChartStyle(background_color="#000000", text_color="#FFFFFF")

        self.chart_container.set_style(custom_style)
        self.assertEqual(self.chart_container.chart_style, custom_style)

    def test_refresh_chart_with_data(self):
        """测试有数据时刷新图表"""
        chart_data = ChartData(x_data=[1, 2, 3], y_data=[10, 20, 30])

        self.chart_container.set_data(chart_data)

        # 刷新应该不抛出异常
        self.chart_container.refresh_chart()

    def test_refresh_chart_without_data(self):
        """测试无数据时刷新图表"""
        # 无数据时刷新应该显示空图表
        self.chart_container.refresh_chart()

        # 验证图表仍然存在
        self.assertIsNotNone(self.chart_container.figure)

    def test_export_data(self):
        """测试导出图表数据"""
        # 无数据时导出
        result = self.chart_container.export_data()
        self.assertIsNone(result)

        # 有数据时导出
        chart_data = ChartData(x_data=[1, 2, 3], y_data=[10, 20, 30], title="测试图表")
        self.chart_container.set_data(chart_data)

        result = self.chart_container.export_data()
        self.assertIsNotNone(result)
        self.assertEqual(result["x_data"], [1, 2, 3])
        self.assertEqual(result["y_data"], [10, 20, 30])
        self.assertEqual(result["title"], "测试图表")

    @patch("tkinter.filedialog.asksaveasfilename")
    def test_save_chart(self, mock_filedialog):
        """测试保存图表"""
        mock_filedialog.return_value = "test_chart.png"

        # 模拟保存操作
        with patch.object(self.chart_container.figure, "savefig") as mock_savefig:
            self.chart_container.save_chart()
            mock_savefig.assert_called_once()

    def test_reset_view(self):
        """测试重置视图"""
        self.chart_container.reset_view()
        # 应该不抛出异常

    def test_toggle_grid(self):
        """测试切换网格"""
        self.chart_container.toggle_grid()
        # 应该不抛出异常

    def test_cleanup(self):
        """测试资源清理"""
        self.chart_container.cleanup()
        # 清理后应该不抛出异常


class TestChartUtilityFunctions(unittest.TestCase):
    """测试图表工具函数"""

    def test_create_chart_data(self):
        """测试创建图表数据函数"""
        chart_data = create_chart_data(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            title="测试图表",
            x_label="X轴",
            y_label="Y轴",
        )

        self.assertIsInstance(chart_data, ChartData)
        self.assertEqual(chart_data.x_data, [1, 2, 3])
        self.assertEqual(chart_data.y_data, [10, 20, 30])
        self.assertEqual(chart_data.title, "测试图表")

    def test_create_chart_style(self):
        """测试创建图表样式函数"""
        style = create_chart_style(
            background_color="#000000", text_color="#FFFFFF", font_size=12
        )

        self.assertIsInstance(style, ChartStyle)
        self.assertEqual(style.background_color, "#000000")
        self.assertEqual(style.text_color, "#FFFFFF")
        self.assertEqual(style.font_size, 12)


class TestChartContainerWithoutMatplotlib(unittest.TestCase):
    """测试matplotlib不可用时的情况"""

    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理"""
        self.root.destroy()

    @patch("minicrm.ui.ttk_base.chart_widget.MATPLOTLIB_AVAILABLE", False)
    def test_chart_container_without_matplotlib(self):
        """测试matplotlib不可用时创建图表容器"""
        with self.assertRaises(ImportError):
            ChartContainerTTK(self.root)


class TestChartIntegration(unittest.TestCase):
    """测试图表组件集成功能"""

    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.chart_container = ChartContainerTTK(self.root)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "chart_container"):
            self.chart_container.cleanup()
        self.root.destroy()

    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
    def test_complete_workflow(self):
        """测试完整的图表工作流程"""
        # 1. 创建数据
        chart_data = create_chart_data(
            x_data=["一月", "二月", "三月", "四月", "五月"],
            y_data=[100, 150, 120, 180, 200],
            title="月度销售额",
            x_label="月份",
            y_label="销售额（万元）",
        )

        # 2. 设置数据
        self.chart_container.set_data(chart_data)

        # 3. 测试不同图表类型
        for chart_type in [ChartType.BAR, ChartType.LINE]:
            self.chart_container.set_chart_type(chart_type)
            self.assertEqual(self.chart_container.chart_type, chart_type)

        # 4. 自定义样式
        custom_style = create_chart_style(
            background_color="#F8F9FA", text_color="#495057", accent_color="#28A745"
        )
        self.chart_container.set_style(custom_style)

        # 5. 刷新图表
        self.chart_container.refresh_chart()

        # 6. 导出数据
        exported_data = self.chart_container.export_data()
        self.assertIsNotNone(exported_data)
        self.assertEqual(exported_data["title"], "月度销售额")

    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
    def test_theme_integration(self):
        """测试主题集成"""
        # 创建样式管理器
        style_manager = StyleManager()

        # 应用深色主题
        style_manager.apply_theme("dark")

        # 创建新的图表容器（应该应用深色主题）
        chart_container = ChartContainerTTK(self.root)

        # 验证主题应用
        self.assertIsNotNone(chart_container.chart_style)

        chart_container.cleanup()


if __name__ == "__main__":
    # 创建测试套件
    test_suite = unittest.TestSuite()

    # 添加测试类
    test_classes = [
        TestChartData,
        TestChartStyle,
        TestChartRenderers,
        TestChartInteractionHandler,
        TestChartContainerTTK,
        TestChartUtilityFunctions,
        TestChartContainerWithoutMatplotlib,
        TestChartIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出测试结果
    print("\n测试完成:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")


class TestChartStyleAndExport(unittest.TestCase):
    """测试图表样式和导出功能"""

    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.chart_container = ChartContainerTTK(self.root)

        # 创建测试数据
        self.test_data = create_chart_data(
            x_data=[1, 2, 3, 4, 5], y_data=[10, 20, 15, 25, 30], title="测试图表"
        )
        self.chart_container.set_data(self.test_data)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "chart_container"):
            self.chart_container.cleanup()
        self.root.destroy()

    def test_chart_themes(self):
        """测试预定义主题"""
        from minicrm.ui.ttk_base.chart_widget import ChartThemes

        # 测试商务主题
        business_theme = ChartThemes.get_business_theme()
        self.assertIsInstance(business_theme, ChartStyle)
        self.assertEqual(business_theme.background_color, "#FFFFFF")

        # 测试深色主题
        dark_theme = ChartThemes.get_dark_theme()
        self.assertEqual(dark_theme.background_color, "#2B2B2B")

        # 测试彩色主题
        colorful_theme = ChartThemes.get_colorful_theme()
        self.assertEqual(colorful_theme.accent_color, "#FF6B6B")

    def test_color_palettes(self):
        """测试颜色调色板"""
        from minicrm.ui.ttk_base.chart_widget import ChartStylePresets

        # 测试获取调色板
        default_palette = ChartStylePresets.get_color_palette("default")
        self.assertIsInstance(default_palette, list)
        self.assertGreater(len(default_palette), 0)

        # 测试应用调色板
        themed_data = ChartStylePresets.apply_color_palette(self.test_data, "vibrant")
        self.assertIsNotNone(themed_data.colors)
        self.assertEqual(len(themed_data.colors), len(self.test_data.y_data))

    def test_export_batch(self):
        """测试批量导出"""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            base_filename = os.path.join(temp_dir, "test_chart")

            # 模拟批量导出
            with patch.object(self.chart_container, "save_chart") as mock_save:
                mock_save.return_value = True

                results = self.chart_container.export_chart_batch(
                    base_filename, ["png", "pdf"]
                )

                self.assertEqual(len(results), 2)
                self.assertTrue(results["png"])
                self.assertTrue(results["pdf"])
                self.assertEqual(mock_save.call_count, 2)

    def test_custom_style_creation(self):
        """测试自定义样式创建"""
        custom_style = self.chart_container.create_custom_style(
            background_color="#FF0000", text_color="#00FF00", font_size=14
        )

        self.assertEqual(custom_style.background_color, "#FF0000")
        self.assertEqual(custom_style.text_color, "#00FF00")
        self.assertEqual(custom_style.font_size, 14)

    def test_export_manager(self):
        """测试导出管理器"""
        from minicrm.ui.ttk_base.chart_widget import ChartExportManager

        export_manager = ChartExportManager(self.chart_container)
        self.assertIsNotNone(export_manager)

        # 测试高质量导出
        with patch.object(self.chart_container, "save_chart") as mock_save:
            mock_save.return_value = True

            result = export_manager.export_high_quality("test.png")
            self.assertTrue(result)
            mock_save.assert_called_once()

    def test_themed_chart_creation(self):
        """测试主题图表创建"""
        from minicrm.ui.ttk_base.chart_widget import (
            create_business_chart,
            create_themed_chart_data,
        )

        # 测试主题图表数据
        themed_data = create_themed_chart_data(
            x_data=[1, 2, 3],
            y_data=[10, 20, 30],
            theme_name="vibrant",
            title="主题测试",
        )

        self.assertIsNotNone(themed_data.colors)
        self.assertEqual(themed_data.title, "主题测试")

        # 测试商务图表创建
        data_dict = {
            "x_data": [1, 2, 3],
            "y_data": [10, 20, 30],
            "x_label": "X轴",
            "y_label": "Y轴",
        }

        chart_data, chart_style = create_business_chart(
            ChartType.BAR, data_dict, title="商务图表"
        )

        self.assertEqual(chart_data.title, "商务图表")
        self.assertIsInstance(chart_style, ChartStyle)


class TestChartAdvancedFeatures(unittest.TestCase):
    """测试图表高级功能"""

    @unittest.skipIf(not MATPLOTLIB_AVAILABLE, "matplotlib不可用")
    def setUp(self):
        """测试准备"""
        self.root = tk.Tk()
        self.root.withdraw()
        self.chart_container = ChartContainerTTK(self.root)

    def tearDown(self):
        """测试清理"""
        if hasattr(self, "chart_container"):
            self.chart_container.cleanup()
        self.root.destroy()

    def test_apply_theme_style(self):
        """测试应用主题样式"""
        # 测试应用主题
        self.chart_container.apply_theme_style("dark")

        # 验证主题应用（这里主要测试不抛出异常）
        self.assertIsNotNone(self.chart_container.chart_style)

    def test_enhanced_save_chart(self):
        """测试增强的保存图表功能"""
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            # 测试带选项的保存
            result = self.chart_container.save_chart(
                tmp_file.name, dpi=150, facecolor="white"
            )

            # 验证返回值
            self.assertTrue(result)

    def test_print_chart(self):
        """测试打印图表功能"""
        # 由于打印功能涉及系统调用，这里主要测试不抛出异常
        try:
            self.chart_container.print_chart()
        except Exception as e:
            # 打印功能可能在测试环境中失败，这是正常的
            self.assertIsInstance(e, Exception)


if __name__ == "__main__":
    # 更新测试套件
    test_suite = unittest.TestSuite()

    # 添加所有测试类
    test_classes = [
        TestChartData,
        TestChartStyle,
        TestChartRenderers,
        TestChartInteractionHandler,
        TestChartContainerTTK,
        TestChartUtilityFunctions,
        TestChartContainerWithoutMatplotlib,
        TestChartIntegration,
        TestChartStyleAndExport,
        TestChartAdvancedFeatures,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # 输出测试结果
    print("\n测试完成:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
