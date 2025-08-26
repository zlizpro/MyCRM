"""MiniCRM 完整仪表盘组件

实现任务5.2的完整仪表盘功能,包括:
- 关键指标卡片显示
- matplotlib图表集成
- 实时数据更新
- 交互功能

必须使用transfunctions函数:
- calculate_customer_value_score()
- format_currency()
- calculate_growth_rate()
- generate_dashboard_summary()
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict


# 可选的matplotlib导入
try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvasTkAgg = None
    Figure = None

# 导入transfunctions
from transfunctions import (
    format_currency,
    generate_dashboard_summary,
)


class DashboardComplete(ttk.Frame):
    """完整仪表盘组件

    实现需求10(数据仪表盘)的完整功能:
    - 关键指标卡片(客户总数、新增客户、待办任务、应收账款等)
    - 集成matplotlib图表显示(客户增长趋势、类型分布、互动频率等)
    - 实现实时数据更新和图表交互功能
    """

    def __init__(self, parent, app=None):
        """初始化完整仪表盘

        Args:
            parent: 父组件
            app: 应用程序实例
        """
        super().__init__(parent)
        self.app = app
        self.logger = logging.getLogger(__name__)

        # 数据服务
        self._customer_dao = None
        self._supplier_dao = None
        self._analytics_service = None

        # 仪表盘数据
        self._dashboard_data = {}
        self._update_timer = None

        # UI组件
        self._metrics_frame = None
        self._charts_frame = None
        self._alerts_frame = None
        self._chart_canvases = {}

        self._setup_services()
        self._setup_ui()
        self._load_dashboard_data()
        self._start_auto_refresh()

    def _setup_services(self):
        """设置数据服务"""
        try:
            if self.app:
                # 从应用程序获取服务实例
                self._customer_dao = getattr(self.app, "customer_dao", None)
                self._supplier_dao = getattr(self.app, "supplier_dao", None)
                self._analytics_service = getattr(self.app, "analytics_service", None)

            self.logger.info("仪表盘服务设置完成")
        except Exception as e:
            self.logger.error(f"设置仪表盘服务失败: {e}")

    def _setup_ui(self):
        """设置UI布局"""
        # 配置主框架
        self.configure(padding="10")

        # 创建标题
        self._create_title()

        # 创建关键指标区域
        self._create_metrics_section()

        # 创建图表区域
        self._create_charts_section()

        # 创建快速操作和预警区域
        self._create_actions_alerts_section()

    def _create_title(self):
        """创建标题区域"""
        title_frame = ttk.Frame(self)
        title_frame.pack(fill="x", pady=(0, 20))

        # 主标题
        title_label = ttk.Label(
            title_frame,
            text="MiniCRM 数据仪表盘",
            font=("Microsoft YaHei UI", 18, "bold"),
        )
        title_label.pack(side="left")

        # 刷新按钮
        refresh_btn = ttk.Button(
            title_frame, text="🔄 刷新数据", command=self._refresh_dashboard
        )
        refresh_btn.pack(side="right")

        # 最后更新时间
        self._update_time_label = ttk.Label(
            title_frame, text="", font=("Microsoft YaHei UI", 9), foreground="gray"
        )
        self._update_time_label.pack(side="right", padx=(0, 10))

    def _create_metrics_section(self):
        """创建关键指标区域"""
        # 指标区域标题
        metrics_title = ttk.Label(
            self, text="📊 关键指标", font=("Microsoft YaHei UI", 14, "bold")
        )
        metrics_title.pack(anchor="w", pady=(0, 10))

        # 指标卡片容器
        self._metrics_frame = ttk.Frame(self)
        self._metrics_frame.pack(fill="x", pady=(0, 20))

    def _create_charts_section(self):
        """创建图表区域"""
        # 图表区域标题
        charts_title = ttk.Label(
            self, text="📈 数据图表", font=("Microsoft YaHei UI", 14, "bold")
        )
        charts_title.pack(anchor="w", pady=(0, 10))

        # 图表容器
        self._charts_frame = ttk.Frame(self)
        self._charts_frame.pack(fill="both", expand=True, pady=(0, 20))

        # 创建图表网格
        self._create_chart_grid()

    def _create_chart_grid(self):
        """创建图表网格布局"""
        # 配置网格权重
        self._charts_frame.columnconfigure(0, weight=1)
        self._charts_frame.columnconfigure(1, weight=1)
        self._charts_frame.rowconfigure(0, weight=1)
        self._charts_frame.rowconfigure(1, weight=1)

        # 创建图表框架
        chart_frames = {}
        positions = [
            ("customer_growth_trend", 0, 0),
            ("customer_type_distribution", 0, 1),
            ("monthly_interaction_frequency", 1, 0),
            ("receivables_status", 1, 1),
        ]

        for chart_name, row, col in positions:
            frame = ttk.LabelFrame(
                self._charts_frame, text=self._get_chart_title(chart_name), padding="5"
            )
            frame.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            chart_frames[chart_name] = frame

        self._chart_frames = chart_frames

    def _create_actions_alerts_section(self):
        """创建快速操作和预警区域"""
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x")

        # 快速操作区域
        actions_frame = ttk.LabelFrame(bottom_frame, text="⚡ 快速操作", padding="10")
        actions_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self._actions_frame = actions_frame

        # 系统预警区域
        alerts_frame = ttk.LabelFrame(bottom_frame, text="⚠️ 系统预警", padding="10")
        alerts_frame.pack(side="right", fill="both", expand=True)

        self._alerts_frame = alerts_frame

    def _load_dashboard_data(self):
        """加载仪表盘数据"""

        def load_data():
            try:
                self.logger.info("开始加载仪表盘数据")

                # 使用transfunctions生成仪表盘数据
                if self._customer_dao and self._supplier_dao:
                    self._dashboard_data = generate_dashboard_summary(
                        self._customer_dao,
                        self._supplier_dao,
                        self._analytics_service,
                        include_charts=True,
                    )
                else:
                    # 使用模拟数据
                    self._dashboard_data = self._get_mock_dashboard_data()

                # 在主线程中更新UI
                self.after(0, self._update_ui_with_data)

            except Exception as e:
                self.logger.error(f"加载仪表盘数据失败: {e}")
                # 使用模拟数据作为后备
                self._dashboard_data = self._get_mock_dashboard_data()
                self.after(0, self._update_ui_with_data)

        # 在后台线程中加载数据
        threading.Thread(target=load_data, daemon=True).start()

    def _update_ui_with_data(self):
        """使用数据更新UI"""
        try:
            # 更新关键指标
            self._update_metrics()

            # 更新图表
            self._update_charts()

            # 更新快速操作
            self._update_quick_actions()

            # 更新系统预警
            self._update_alerts()

            # 更新时间戳
            self._update_timestamp()

            self.logger.info("仪表盘UI更新完成")

        except Exception as e:
            self.logger.error(f"更新仪表盘UI失败: {e}")

    def _update_metrics(self):
        """更新关键指标卡片"""
        # 清除现有指标
        for widget in self._metrics_frame.winfo_children():
            widget.destroy()

        metrics = self._dashboard_data.get("metrics", [])

        # 创建指标卡片网格
        cols = 3
        for i, metric in enumerate(metrics):
            row = i // cols
            col = i % cols

            card = self._create_metric_card(self._metrics_frame, metric)
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # 配置列权重
        for i in range(cols):
            self._metrics_frame.columnconfigure(i, weight=1)

    def _create_metric_card(self, parent, metric: Dict[str, Any]) -> ttk.Frame:
        """创建指标卡片"""
        card = ttk.LabelFrame(parent, padding="10")

        # 标题
        title_label = ttk.Label(
            card, text=metric.get("title", ""), font=("Microsoft YaHei UI", 10, "bold")
        )
        title_label.pack(anchor="w")

        # 数值
        value_text = str(metric.get("value", ""))
        unit = metric.get("unit", "")
        if unit:
            value_text += f" {unit}"

        value_label = ttk.Label(
            card,
            text=value_text,
            font=("Microsoft YaHei UI", 16, "bold"),
            foreground=self._get_color_for_metric(metric.get("color", "primary")),
        )
        value_label.pack(anchor="w")

        # 趋势信息
        trend = metric.get("trend")
        trend_value = metric.get("trend_value")
        if trend and trend_value is not None:
            trend_icon = "↗️" if trend == "up" else "↘️" if trend == "down" else "➡️"
            trend_text = f"{trend_icon} {trend_value:.1f}%"

            trend_label = ttk.Label(
                card,
                text=trend_text,
                font=("Microsoft YaHei UI", 9),
                foreground="green"
                if trend == "up"
                else "red"
                if trend == "down"
                else "gray",
            )
            trend_label.pack(anchor="w")

        return card

    def _update_charts(self):
        """更新图表"""
        charts_data = self._dashboard_data.get("charts", {})

        for chart_name, chart_data in charts_data.items():
            if chart_name in self._chart_frames:
                self._create_chart(chart_name, chart_data)

    def _create_chart(self, chart_name: str, chart_data: Dict[str, Any]):
        """创建单个图表"""
        try:
            frame = self._chart_frames[chart_name]

            # 清除现有图表
            for widget in frame.winfo_children():
                widget.destroy()

            # 检查matplotlib是否可用
            if not MATPLOTLIB_AVAILABLE:
                self._create_text_chart(frame, chart_data)
                return

            # 创建matplotlib图表
            fig = Figure(figsize=(4, 3), dpi=80, facecolor="white")
            ax = fig.add_subplot(111)

            chart_type = chart_data.get("type", "line")
            labels = chart_data.get("labels", [])
            datasets = chart_data.get("datasets", [])

            if not datasets:
                ax.text(
                    0.5,
                    0.5,
                    "暂无数据",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            else:
                dataset = datasets[0]  # 使用第一个数据集
                data = dataset.get("data", [])

                if chart_type == "line":
                    ax.plot(labels, data, marker="o", linewidth=2, markersize=4)
                    ax.set_xlabel("月份")
                    ax.set_ylabel("数量")

                elif chart_type == "bar":
                    bars = ax.bar(
                        labels, data, color=dataset.get("backgroundColor", "#007BFF")
                    )
                    ax.set_xlabel("月份")
                    ax.set_ylabel("次数")

                    # 在柱子上显示数值
                    for bar, value in zip(bars, data):
                        height = bar.get_height()
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.0,
                            height + 1,
                            f"{value}",
                            ha="center",
                            va="bottom",
                            fontsize=8,
                        )

                elif chart_type in ["pie", "doughnut"]:
                    colors = dataset.get("backgroundColor", plt.cm.Set3.colors)
                    wedges, texts, autotexts = ax.pie(
                        data,
                        labels=labels,
                        colors=colors,
                        autopct="%1.1f%%",
                        startangle=90,
                    )
                    # 调整文字大小
                    for text in texts:
                        text.set_fontsize(8)
                    for autotext in autotexts:
                        autotext.set_fontsize(7)
                        autotext.set_color("white")
                        autotext.set_weight("bold")

            # 设置标题
            ax.set_title(
                chart_data.get("title", ""), fontsize=10, fontweight="bold", pad=10
            )

            # 调整布局
            fig.tight_layout()

            # 创建画布
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # 保存画布引用
            self._chart_canvases[chart_name] = canvas

        except Exception as e:
            self.logger.error(f"创建图表 {chart_name} 失败: {e}")
            # 显示错误信息
            error_label = ttk.Label(frame, text=f"图表加载失败: {e!s}")
            error_label.pack(expand=True)

    def _create_text_chart(self, frame: ttk.Frame, chart_data: Dict[str, Any]):
        """创建文本版本的图表(matplotlib不可用时的替代方案)"""
        try:
            chart_type = chart_data.get("type", "line")
            title = chart_data.get("title", "图表")
            labels = chart_data.get("labels", [])
            datasets = chart_data.get("datasets", [])

            # 创建滚动文本框
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill="both", expand=True, padx=5, pady=5)

            # 创建文本显示
            text_widget = tk.Text(
                text_frame,
                height=8,
                width=30,
                wrap=tk.WORD,
                font=("Microsoft YaHei UI", 9),
            )

            # 添加滚动条
            scrollbar = ttk.Scrollbar(
                text_frame, orient="vertical", command=text_widget.yview
            )
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # 构建文本内容
            content = f"📊 {title}\n{'=' * 20}\n\n"

            if not datasets or not labels:
                content += "暂无数据显示\n"
            else:
                dataset = datasets[0]
                data = dataset.get("data", [])

                if chart_type in ["pie", "doughnut"]:
                    # 饼图数据显示
                    total = sum(data) if data else 1
                    for i, (label, value) in enumerate(zip(labels, data)):
                        percentage = (value / total * 100) if total > 0 else 0
                        content += f"• {label}: {value} ({percentage:.1f}%)\n"
                else:
                    # 线图/柱图数据显示
                    for i, (label, value) in enumerate(zip(labels, data)):
                        # 简单的条形图表示
                        bar_length = (
                            int(value / max(data) * 20) if data and max(data) > 0 else 0
                        )
                        bar = "█" * bar_length + "░" * (20 - bar_length)
                        content += f"{label}: {bar} {value}\n"

            content += f"\n图表类型: {chart_type}\n"
            content += "注: 安装matplotlib可显示完整图表"

            # 插入内容
            text_widget.insert("1.0", content)
            text_widget.config(state="disabled")  # 设为只读

        except Exception as e:
            self.logger.error(f"创建文本图表失败: {e}")
            error_label = ttk.Label(frame, text="图表数据加载失败")
            error_label.pack(expand=True)

    def _update_quick_actions(self):
        """更新快速操作按钮"""
        # 清除现有按钮
        for widget in self._actions_frame.winfo_children():
            widget.destroy()

        quick_actions = self._dashboard_data.get("quick_actions", [])

        # 创建按钮网格
        cols = 3
        for i, action in enumerate(quick_actions):
            row = i // cols
            col = i % cols

            btn = ttk.Button(
                self._actions_frame,
                text=action.get("title", ""),
                command=lambda a=action: self._handle_quick_action(a),
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        # 配置列权重
        for i in range(cols):
            self._actions_frame.columnconfigure(i, weight=1)

    def _update_alerts(self):
        """更新系统预警"""
        # 清除现有预警
        for widget in self._alerts_frame.winfo_children():
            widget.destroy()

        alerts = self._dashboard_data.get("alerts", [])

        if not alerts:
            no_alerts_label = ttk.Label(
                self._alerts_frame, text="✅ 暂无系统预警", foreground="green"
            )
            no_alerts_label.pack()
        else:
            for alert in alerts:
                alert_frame = ttk.Frame(self._alerts_frame)
                alert_frame.pack(fill="x", pady=2)

                # 预警图标和类型
                alert_type = alert.get("type", "info")
                icon = (
                    "⚠️"
                    if alert_type == "warning"
                    else "ℹ️"
                    if alert_type == "info"
                    else "❌"
                )

                icon_label = ttk.Label(alert_frame, text=icon)
                icon_label.pack(side="left")

                # 预警消息
                message_label = ttk.Label(
                    alert_frame,
                    text=alert.get("message", ""),
                    font=("Microsoft YaHei UI", 9),
                )
                message_label.pack(side="left", padx=(5, 0))

    def _update_timestamp(self):
        """更新时间戳"""
        generated_at = self._dashboard_data.get("generated_at", "")
        if generated_at:
            self._update_time_label.config(text=f"更新时间: {generated_at}")

    def _refresh_dashboard(self):
        """刷新仪表盘数据"""
        self.logger.info("手动刷新仪表盘数据")
        self._load_dashboard_data()

    def _start_auto_refresh(self):
        """启动自动刷新"""
        # 每5分钟自动刷新一次
        self._update_timer = self.after(300000, self._auto_refresh)

    def _auto_refresh(self):
        """自动刷新"""
        self.logger.info("自动刷新仪表盘数据")
        self._load_dashboard_data()
        self._start_auto_refresh()  # 重新设置定时器

    def _handle_quick_action(self, action: Dict[str, Any]):
        """处理快速操作"""
        action_name = action.get("action", "")
        self.logger.info(f"执行快速操作: {action_name}")

        # 这里可以集成具体的操作逻辑
        if self.app and hasattr(self.app, "handle_quick_action"):
            self.app.handle_quick_action(action_name)
        else:
            # 显示提示信息
            tk.messagebox.showinfo("快速操作", f"执行操作: {action.get('title', '')}")

    def _get_chart_title(self, chart_name: str) -> str:
        """获取图表标题"""
        titles = {
            "customer_growth_trend": "客户增长趋势",
            "customer_type_distribution": "客户类型分布",
            "monthly_interaction_frequency": "月度互动频率",
            "receivables_status": "应收账款状态",
        }
        return titles.get(chart_name, chart_name)

    def _get_color_for_metric(self, color: str) -> str:
        """获取指标颜色"""
        colors = {
            "primary": "#007BFF",
            "success": "#28A745",
            "warning": "#FFC107",
            "danger": "#DC3545",
            "info": "#17A2B8",
        }
        return colors.get(color, "#007BFF")

    def _get_mock_dashboard_data(self) -> Dict[str, Any]:
        """获取模拟仪表盘数据"""
        return {
            "metrics": [
                {
                    "title": "客户总数",
                    "value": 156,
                    "unit": "个",
                    "trend": "up",
                    "trend_value": 8.5,
                    "color": "primary",
                    "icon": "users",
                },
                {
                    "title": "本月新增客户",
                    "value": 12,
                    "unit": "个",
                    "color": "success",
                    "icon": "user-plus",
                },
                {
                    "title": "待办任务",
                    "value": 8,
                    "unit": "项",
                    "color": "primary",
                    "icon": "clipboard-list",
                },
                {
                    "title": "应收账款",
                    "value": format_currency(502000),
                    "color": "success",
                    "icon": "dollar-sign",
                },
                {
                    "title": "应付账款",
                    "value": format_currency(321000),
                    "color": "primary",
                    "icon": "credit-card",
                },
                {
                    "title": "供应商总数",
                    "value": 45,
                    "unit": "个",
                    "color": "primary",
                    "icon": "building",
                },
            ],
            "charts": {
                "customer_growth_trend": {
                    "type": "line",
                    "title": "客户增长趋势",
                    "labels": ["7月", "8月", "9月", "10月", "11月", "12月"],
                    "datasets": [
                        {
                            "label": "客户总数",
                            "data": [120, 135, 142, 148, 152, 156],
                            "borderColor": "#007BFF",
                            "backgroundColor": "rgba(0, 123, 255, 0.1)",
                        }
                    ],
                },
                "customer_type_distribution": {
                    "type": "pie",
                    "title": "客户类型分布",
                    "labels": ["生态板客户", "家具板客户", "阻燃板客户", "其他"],
                    "datasets": [
                        {
                            "data": [45, 35, 15, 5],
                            "backgroundColor": [
                                "#28A745",
                                "#007BFF",
                                "#FFC107",
                                "#6C757D",
                            ],
                        }
                    ],
                },
                "monthly_interaction_frequency": {
                    "type": "bar",
                    "title": "月度互动频率",
                    "labels": ["7月", "8月", "9月", "10月", "11月", "12月"],
                    "datasets": [
                        {
                            "label": "互动次数",
                            "data": [85, 92, 78, 105, 98, 112],
                            "backgroundColor": "#28A745",
                        }
                    ],
                },
                "receivables_status": {
                    "type": "doughnut",
                    "title": "应收账款状态",
                    "labels": ["正常", "逾期30天内", "逾期30-60天", "逾期60天以上"],
                    "datasets": [
                        {
                            "data": [70, 20, 7, 3],
                            "backgroundColor": [
                                "#28A745",
                                "#FFC107",
                                "#FD7E14",
                                "#DC3545",
                            ],
                        }
                    ],
                },
            },
            "quick_actions": [
                {"title": "新增客户", "icon": "user-plus", "action": "create_customer"},
                {
                    "title": "新增供应商",
                    "icon": "building-plus",
                    "action": "create_supplier",
                },
                {"title": "创建报价", "icon": "file-text", "action": "create_quote"},
                {
                    "title": "记录收款",
                    "icon": "dollar-sign",
                    "action": "record_payment",
                },
                {"title": "查看报表", "icon": "bar-chart", "action": "view_reports"},
            ],
            "alerts": [
                {
                    "type": "warning",
                    "title": "逾期应收账款提醒",
                    "message": "有3笔应收账款已逾期,请及时跟进",
                    "action": "view_overdue_receivables",
                },
                {
                    "type": "warning",
                    "title": "合同即将到期",
                    "message": "有2个合同即将到期,请及时续约",
                    "action": "view_expiring_contracts",
                },
            ],
            "generated_at": "2025-01-15 14:30:00",
        }

    def cleanup(self):
        """清理资源"""
        # 取消定时器
        if self._update_timer:
            self.after_cancel(self._update_timer)

        # 清理图表画布
        for canvas in self._chart_canvases.values():
            try:
                canvas.get_tk_widget().destroy()
            except:
                pass

        self.logger.info("仪表盘资源清理完成")
