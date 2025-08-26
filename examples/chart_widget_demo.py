"""TTK图表组件演示

演示ChartContainerTTK组件的各种功能，包括：
- 不同类型的图表展示
- 交互功能演示
- 主题集成演示
- 实际业务数据示例

运行此文件可以看到图表组件的完整功能演示。

作者: MiniCRM开发团队
"""

from datetime import datetime, timedelta
import os
import random
import sys
import tkinter as tk
from tkinter import messagebox, ttk


# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
    from minicrm.ui.ttk_base.base_window import BaseWindow
    from minicrm.ui.ttk_base.chart_widget import (
        MATPLOTLIB_AVAILABLE,
        ChartContainerTTK,
        ChartData,
        ChartStyle,
        ChartType,
        create_chart_data,
        create_chart_style,
    )
    from minicrm.ui.ttk_base.style_manager import StyleManager, ThemeType
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保已安装所需依赖: pip install matplotlib")
    sys.exit(1)


class ChartDemoWindow(BaseWindow):
    """图表演示窗口"""

    def __init__(self):
        """初始化演示窗口"""
        super().__init__(title="MiniCRM 图表组件演示", size=(1200, 800))

        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror(
                "错误", "matplotlib不可用，请安装: pip install matplotlib"
            )
            self.destroy()
            return

        # 样式管理器
        self.style_manager = StyleManager(self)

        # 演示数据
        self.demo_data = self._generate_demo_data()

        # 当前图表索引
        self.current_chart_index = 0

        # 设置UI
        self._setup_demo_ui()

        # 显示第一个图表
        self._show_current_chart()

    def _setup_ui(self) -> None:
        """设置UI布局（重写基类方法）"""
        # 在_setup_demo_ui中实现

    def _setup_demo_ui(self) -> None:
        """设置演示UI"""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建控制面板
        self._create_control_panel(main_frame)

        # 创建图表区域
        self._create_chart_area(main_frame)

        # 创建信息面板
        self._create_info_panel(main_frame)

    def _create_control_panel(self, parent) -> None:
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 图表选择
        ttk.Label(control_frame, text="选择图表:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5)
        )

        self.chart_var = tk.StringVar()
        chart_combo = ttk.Combobox(
            control_frame,
            textvariable=self.chart_var,
            values=[
                "销售趋势 (折线图)",
                "产品销量 (柱状图)",
                "市场份额 (饼图)",
                "客户分布 (散点图)",
                "月度对比 (柱状图)",
                "季度增长 (折线图)",
            ],
            state="readonly",
            width=20,
        )
        chart_combo.grid(row=0, column=1, padx=5)
        chart_combo.bind("<<ComboboxSelected>>", self._on_chart_selected)
        chart_combo.current(0)

        # 主题选择
        ttk.Label(control_frame, text="选择主题:").grid(
            row=0, column=2, sticky=tk.W, padx=(20, 5)
        )

        self.theme_var = tk.StringVar(value="default")
        theme_combo = ttk.Combobox(
            control_frame,
            textvariable=self.theme_var,
            values=["default", "dark", "light", "high_contrast"],
            state="readonly",
            width=15,
        )
        theme_combo.grid(row=0, column=3, padx=5)
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)

        # 操作按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=4, padx=(20, 0))

        ttk.Button(button_frame, text="刷新数据", command=self._refresh_data).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(button_frame, text="保存图表", command=self._save_chart).pack(
            side=tk.LEFT, padx=2
        )

        ttk.Button(button_frame, text="重置视图", command=self._reset_view).pack(
            side=tk.LEFT, padx=2
        )

    def _create_chart_area(self, parent) -> None:
        """创建图表区域"""
        chart_frame = ttk.LabelFrame(parent, text="图表显示", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建图表容器
        self.chart_container = ChartContainerTTK(chart_frame)
        self.chart_container.pack(fill=tk.BOTH, expand=True)

    def _create_info_panel(self, parent) -> None:
        """创建信息面板"""
        info_frame = ttk.LabelFrame(parent, text="使用说明", padding=10)
        info_frame.pack(fill=tk.X)

        info_text = """
        图表交互说明:
        • 鼠标滚轮: 缩放图表
        • 中键拖拽 或 Ctrl+左键拖拽: 平移图表
        • R键: 重置视图
        • G键: 切换网格显示
        • 鼠标悬停: 显示数据点信息（部分图表类型）

        功能演示:
        • 切换不同的图表类型查看效果
        • 尝试不同的主题风格
        • 使用刷新数据按钮生成新的随机数据
        • 使用保存图表功能导出图表
        """

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

    def _generate_demo_data(self) -> dict:
        """生成演示数据"""
        # 生成日期序列
        start_date = datetime.now() - timedelta(days=365)
        dates = [start_date + timedelta(days=i * 30) for i in range(12)]
        date_labels = [d.strftime("%Y-%m") for d in dates]

        return {
            "sales_trend": {
                "data": create_chart_data(
                    x_data=date_labels,
                    y_data=[120, 135, 148, 162, 158, 175, 189, 201, 195, 210, 225, 240],
                    title="月度销售趋势",
                    x_label="月份",
                    y_label="销售额（万元）",
                ),
                "type": ChartType.LINE,
            },
            "product_sales": {
                "data": create_chart_data(
                    x_data=["生态板", "家具板", "阻燃板", "装饰板", "结构板"],
                    y_data=[450, 320, 280, 180, 150],
                    title="产品销量对比",
                    x_label="产品类型",
                    y_label="销量（立方米）",
                    colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
                ),
                "type": ChartType.BAR,
            },
            "market_share": {
                "data": create_chart_data(
                    x_data=[],
                    y_data=[35, 25, 20, 12, 8],
                    labels=["华东地区", "华南地区", "华北地区", "西南地区", "其他地区"],
                    title="市场份额分布",
                    colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"],
                ),
                "type": ChartType.PIE,
            },
            "customer_distribution": {
                "data": create_chart_data(
                    x_data=[random.randint(10, 100) for _ in range(50)],
                    y_data=[random.randint(5, 50) for _ in range(50)],
                    title="客户订单分布",
                    x_label="订单数量",
                    y_label="客户价值（万元）",
                ),
                "type": ChartType.SCATTER,
            },
            "monthly_comparison": {
                "data": create_chart_data(
                    x_data=["1月", "2月", "3月", "4月", "5月", "6月"],
                    y_data=[180, 165, 195, 210, 225, 240],
                    title="上半年月度销售对比",
                    x_label="月份",
                    y_label="销售额（万元）",
                    colors=[
                        "#667eea",
                        "#764ba2",
                        "#f093fb",
                        "#f5576c",
                        "#4facfe",
                        "#00f2fe",
                    ],
                ),
                "type": ChartType.BAR,
            },
            "quarterly_growth": {
                "data": create_chart_data(
                    x_data=["Q1", "Q2", "Q3", "Q4"],
                    y_data=[520, 580, 640, 720],
                    title="季度增长趋势",
                    x_label="季度",
                    y_label="销售额（万元）",
                ),
                "type": ChartType.LINE,
            },
        }

    def _show_current_chart(self) -> None:
        """显示当前选中的图表"""
        chart_names = list(self.demo_data.keys())
        if 0 <= self.current_chart_index < len(chart_names):
            chart_name = chart_names[self.current_chart_index]
            chart_info = self.demo_data[chart_name]

            # 设置图表类型和数据
            self.chart_container.set_chart_type(chart_info["type"])
            self.chart_container.set_data(chart_info["data"])

    def _on_chart_selected(self, event) -> None:
        """图表选择事件处理"""
        selection = self.chart_var.get()
        chart_mapping = {
            "销售趋势 (折线图)": 0,
            "产品销量 (柱状图)": 1,
            "市场份额 (饼图)": 2,
            "客户分布 (散点图)": 3,
            "月度对比 (柱状图)": 4,
            "季度增长 (折线图)": 5,
        }

        if selection in chart_mapping:
            self.current_chart_index = chart_mapping[selection]
            self._show_current_chart()

    def _on_theme_changed(self, event) -> None:
        """主题变化事件处理"""
        theme_name = self.theme_var.get()

        # 应用主题
        success = self.style_manager.apply_theme(theme_name)
        if success:
            # 重新应用主题样式到图表
            self.chart_container._apply_theme_style()
            self.chart_container.refresh_chart()

            messagebox.showinfo("主题切换", f"已切换到 {theme_name} 主题")
        else:
            messagebox.showerror("错误", f"切换主题失败: {theme_name}")

    def _refresh_data(self) -> None:
        """刷新数据"""
        # 重新生成随机数据
        self.demo_data = self._generate_demo_data()
        self._show_current_chart()
        messagebox.showinfo("数据刷新", "图表数据已刷新")

    def _save_chart(self) -> None:
        """保存图表"""
        self.chart_container.save_chart()

    def _reset_view(self) -> None:
        """重置视图"""
        self.chart_container.reset_view()
        messagebox.showinfo("视图重置", "图表视图已重置")


class SimpleChartDemo:
    """简单图表演示类"""

    def __init__(self):
        """初始化简单演示"""
        self.root = tk.Tk()
        self.root.title("简单图表演示")
        self.root.geometry("800x600")

        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror(
                "错误", "matplotlib不可用，请安装: pip install matplotlib"
            )
            self.root.destroy()
            return

        self._create_simple_demo()

    def _create_simple_demo(self) -> None:
        """创建简单演示"""
        # 创建图表容器
        chart_container = ChartContainerTTK(self.root)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建示例数据
        sample_data = create_chart_data(
            x_data=["生态板", "家具板", "阻燃板", "装饰板"],
            y_data=[450, 320, 280, 180],
            title="产品销量统计",
            x_label="产品类型",
            y_label="销量（立方米）",
            colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
        )

        # 设置数据和图表类型
        chart_container.set_data(sample_data)
        chart_container.set_chart_type(ChartType.BAR)

        # 创建控制按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(
            button_frame,
            text="柱状图",
            command=lambda: chart_container.set_chart_type(ChartType.BAR),
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="折线图",
            command=lambda: chart_container.set_chart_type(ChartType.LINE),
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            button_frame,
            text="饼图",
            command=lambda: self._show_pie_chart(chart_container),
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(button_frame, text="保存", command=chart_container.save_chart).pack(
            side=tk.RIGHT, padx=2
        )

    def _show_pie_chart(self, chart_container) -> None:
        """显示饼图"""
        pie_data = create_chart_data(
            x_data=[],
            y_data=[450, 320, 280, 180],
            labels=["生态板", "家具板", "阻燃板", "装饰板"],
            title="产品销量分布",
            colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
        )
        chart_container.set_data(pie_data)
        chart_container.set_chart_type(ChartType.PIE)

    def run(self) -> None:
        """运行演示"""
        self.root.mainloop()


def main():
    """主函数"""
    print("MiniCRM 图表组件演示")
    print("=" * 50)

    if not MATPLOTLIB_AVAILABLE:
        print("错误: matplotlib不可用")
        print("请安装matplotlib: pip install matplotlib")
        return

    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--simple":
        print("启动简单演示...")
        demo = SimpleChartDemo()
        demo.run()
    else:
        print("启动完整演示...")
        print("\n使用说明:")
        print("- 使用 --simple 参数启动简单演示")
        print("- 不带参数启动完整功能演示")
        print("\n启动中...")

        try:
            demo_window = ChartDemoWindow()
            demo_window.mainloop()
        except Exception as e:
            print(f"启动演示失败: {e}")
            print("尝试简单演示...")
            demo = SimpleChartDemo()
            demo.run()


if __name__ == "__main__":
    main()
