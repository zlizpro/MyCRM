"""MiniCRM TTK财务分析组件.

提供财务分析功能的TTK组件, 包括:
- 财务数据分析和计算
- 财务报表生成和展示
- Excel和PDF格式导出
- 图表可视化展示
- 数据同步和自动计算

设计特点:
- 基于BaseWidget提供标准TTK组件功能
- 集成ChartContainerTTK进行数据可视化
- 使用FinanceService处理业务逻辑
- 支持多种导出格式和自定义报表
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any, Callable


if TYPE_CHECKING:
    from minicrm.services.finance_service import FinanceService
    from minicrm.ui.ttk_base.chart_widget import ChartData

from minicrm.core.exceptions import ServiceError
from minicrm.services.excel_export.financial_excel_exporter import (
    FinancialExcelExporter,
)
from minicrm.services.pdf_export_service import QuotePDFExportService
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.chart_widget import (
    ChartContainerTTK,
    ChartType,
    create_chart_data,
)


class FinancialAnalysisTTK(BaseWidget):
    """TTK财务分析组件.

    提供完整的财务分析功能, 包括数据分析、图表展示、报表导出等.
    """

    def __init__(
        self, parent: tk.Widget, finance_service: FinanceService, **kwargs: Any
    ) -> None:
        """初始化财务分析组件.

        Args:
            parent: 父组件
            finance_service: 财务服务实例
            **kwargs: 其他参数
        """
        self.finance_service = finance_service
        self.excel_exporter = FinancialExcelExporter()
        self.pdf_exporter = QuotePDFExportService()

        # 数据存储
        self.financial_data: dict[str, Any] = {}
        self.analysis_results: dict[str, Any] = {}
        self.chart_data: dict[str, ChartData] = {}

        # UI组件
        self.notebook: ttk.Notebook | None = None
        self.summary_frame: ttk.Frame | None = None
        self.charts_frame: ttk.Frame | None = None
        self.export_frame: ttk.Frame | None = None

        # 图表组件
        self.summary_chart: ChartContainerTTK | None = None
        self.trend_chart: ChartContainerTTK | None = None
        self.comparison_chart: ChartContainerTTK | None = None

        # 数据同步
        self.auto_refresh = True
        self.refresh_interval = 300  # 5分钟
        self.refresh_timer: threading.Timer | None = None

        # 事件回调
        self.on_data_updated: Callable[[dict[str, Any]], None] | None = None
        self.on_export_completed: Callable[[dict[str, bool]], None] | None = None

        super().__init__(parent, **kwargs)

        # 初始化数据
        self._load_financial_data()

        # 启动自动刷新
        if self.auto_refresh:
            self._start_auto_refresh()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建工具栏
        self._create_toolbar(main_container)

        # 创建标签页
        self._create_notebook(main_container)

        # 创建各个标签页内容
        self._create_summary_tab()
        self._create_charts_tab()
        self._create_export_tab()

    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """创建工具栏."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧: 标题和状态
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        title_label = ttk.Label(
            left_frame, text="财务分析", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        self.status_label = ttk.Label(left_frame, text="准备就绪", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # 右侧: 操作按钮
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)

        # 刷新按钮
        refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新数据", command=self._refresh_data
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 自动刷新开关
        self.auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        auto_refresh_cb = ttk.Checkbutton(
            right_frame,
            text="自动刷新",
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh,
        )
        auto_refresh_cb.pack(side=tk.LEFT, padx=(0, 5))

        # 导出按钮
        export_btn = ttk.Button(
            right_frame, text="📤 快速导出", command=self._quick_export
        )
        export_btn.pack(side=tk.LEFT)

    def _create_notebook(self, parent: ttk.Frame) -> None:
        """创建标签页容器."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def _create_summary_tab(self) -> None:
        """创建财务概览标签页."""
        self.summary_frame = ttk.Frame(self.notebook)
        if self.notebook is not None:
            self.notebook.add(self.summary_frame, text="财务概览")

        # 创建滚动容器
        canvas = tk.Canvas(self.summary_frame)
        scrollbar = ttk.Scrollbar(
            self.summary_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 创建概览内容
        self._create_summary_content(scrollable_frame)

    def _create_summary_content(self, parent: ttk.Frame) -> None:
        """创建财务概览内容."""
        # 关键指标区域
        metrics_frame = ttk.LabelFrame(parent, text="关键财务指标", padding=10)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)

        # 创建指标网格
        self.metrics_labels = {}
        metrics = [
            ("total_receivables", "应收账款总额", "¥0.00"),
            ("total_payables", "应付账款总额", "¥0.00"),
            ("net_position", "净头寸", "¥0.00"),
            ("overdue_receivables", "逾期应收", "¥0.00"),
            ("receivables_overdue_rate", "应收逾期率", "0.0%"),
            ("cash_flow", "现金流", "¥0.00"),
        ]

        for i, (key, label, default) in enumerate(metrics):
            row, col = divmod(i, 2)

            # 标签
            ttk.Label(metrics_frame, text=f"{label}:").grid(
                row=row, column=col * 2, sticky="w", padx=(0, 5), pady=2
            )

            # 值标签
            value_label = ttk.Label(
                metrics_frame, text=default, font=("Microsoft YaHei UI", 10, "bold")
            )
            value_label.grid(
                row=row, column=col * 2 + 1, sticky="w", padx=(0, 20), pady=2
            )

            self.metrics_labels[key] = value_label

        # 风险预警区域
        risk_frame = ttk.LabelFrame(parent, text="风险预警", padding=10)
        risk_frame.pack(fill=tk.X, padx=10, pady=5)

        self.risk_text = tk.Text(risk_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.risk_text.pack(fill=tk.BOTH, expand=True)

        # 趋势分析区域
        trend_frame = ttk.LabelFrame(parent, text="趋势分析", padding=10)
        trend_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建小型图表
        self.summary_chart = ChartContainerTTK(trend_frame)
        self.summary_chart.pack(fill=tk.BOTH, expand=True)

    def _create_charts_tab(self) -> None:
        """创建图表分析标签页."""
        self.charts_frame = ttk.Frame(self.notebook)
        if self.notebook is not None:
            self.notebook.add(self.charts_frame, text="图表分析")

        # 创建图表控制面板
        control_frame = ttk.Frame(self.charts_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 图表类型选择
        ttk.Label(control_frame, text="图表类型:").pack(side=tk.LEFT)

        self.chart_type_var = tk.StringVar(value="bar")
        chart_type_combo = ttk.Combobox(
            control_frame,
            textvariable=self.chart_type_var,
            values=["bar", "line", "pie"],
            state="readonly",
            width=10,
        )
        chart_type_combo.pack(side=tk.LEFT, padx=(5, 20))
        chart_type_combo.bind("<<ComboboxSelected>>", self._on_chart_type_changed)

        # 时间范围选择
        ttk.Label(control_frame, text="时间范围:").pack(side=tk.LEFT)

        self.time_range_var = tk.StringVar(value="30")
        time_range_combo = ttk.Combobox(
            control_frame,
            textvariable=self.time_range_var,
            values=["7", "30", "90", "365"],
            state="readonly",
            width=8,
        )
        time_range_combo.pack(side=tk.LEFT, padx=(5, 20))
        time_range_combo.bind("<<ComboboxSelected>>", self._on_time_range_changed)

        # 更新按钮
        update_btn = ttk.Button(
            control_frame, text="更新图表", command=self._update_charts
        )
        update_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 图表容器
        charts_container = ttk.Frame(self.charts_frame)
        charts_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建图表网格
        self._create_chart_grid(charts_container)

    def _create_chart_grid(self, parent: ttk.Frame) -> None:
        """创建图表网格布局."""
        # 上半部分: 趋势图表
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.trend_chart = ChartContainerTTK(top_frame)
        self.trend_chart.pack(fill=tk.BOTH, expand=True)

        # 下半部分: 对比图表
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.comparison_chart = ChartContainerTTK(bottom_frame)
        self.comparison_chart.pack(fill=tk.BOTH, expand=True)

    def _create_export_tab(self) -> None:
        """创建导出设置标签页."""
        self.export_frame = ttk.Frame(self.notebook)
        if self.notebook is not None:
            self.notebook.add(self.export_frame, text="导出设置")

        # 导出格式选择
        format_frame = ttk.LabelFrame(self.export_frame, text="导出格式", padding=10)
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.export_formats = {
            "excel": tk.BooleanVar(value=True),
            "pdf": tk.BooleanVar(value=False),
            "csv": tk.BooleanVar(value=False),
        }

        for fmt, var in self.export_formats.items():
            ttk.Checkbutton(format_frame, text=fmt.upper(), variable=var).pack(
                side=tk.LEFT, padx=(0, 20)
            )

        # 导出内容选择
        content_frame = ttk.LabelFrame(self.export_frame, text="导出内容", padding=10)
        content_frame.pack(fill=tk.X, padx=10, pady=5)

        self.export_contents = {
            "summary": tk.BooleanVar(value=True),
            "charts": tk.BooleanVar(value=True),
            "raw_data": tk.BooleanVar(value=False),
            "analysis": tk.BooleanVar(value=True),
        }

        content_labels = {
            "summary": "财务概览",
            "charts": "图表分析",
            "raw_data": "原始数据",
            "analysis": "分析报告",
        }

        for key, var in self.export_contents.items():
            ttk.Checkbutton(content_frame, text=content_labels[key], variable=var).pack(
                anchor=tk.W, pady=2
            )

        # 导出选项
        options_frame = ttk.LabelFrame(self.export_frame, text="导出选项", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        # 文件名模板
        ttk.Label(options_frame, text="文件名模板:").pack(anchor=tk.W)
        self.filename_var = tk.StringVar(value="财务分析报告_{date}")
        filename_entry = ttk.Entry(
            options_frame, textvariable=self.filename_var, width=40
        )
        filename_entry.pack(fill=tk.X, pady=(2, 10))

        # 包含时间戳
        self.include_timestamp = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame, text="包含时间戳", variable=self.include_timestamp
        ).pack(anchor=tk.W)

        # 导出按钮区域
        button_frame = ttk.Frame(self.export_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=20)

        # 选择目录按钮
        select_dir_btn = ttk.Button(
            button_frame, text="📁 选择导出目录", command=self._select_export_directory
        )
        select_dir_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 开始导出按钮
        export_btn = ttk.Button(
            button_frame, text="🚀 开始导出", command=self._start_export
        )
        export_btn.pack(side=tk.LEFT)

        # 导出进度
        self.export_progress = ttk.Progressbar(self.export_frame, mode="indeterminate")
        self.export_progress.pack(fill=tk.X, padx=10, pady=(10, 0))

        # 导出状态
        self.export_status_label = ttk.Label(
            self.export_frame, text="准备导出", foreground="gray"
        )
        self.export_status_label.pack(pady=(5, 0))

    def _load_financial_data(self) -> None:
        """加载财务数据."""
        try:
            self._update_status("正在加载财务数据...")

            # 获取财务汇总数据
            self.financial_data = self.finance_service.get_financial_summary()

            # 进行财务分析
            self._perform_analysis()

            # 更新UI显示
            self._update_summary_display()
            self._update_charts()

            self._update_status("数据加载完成")

            # 触发数据更新事件
            if self.on_data_updated:
                self.on_data_updated(self.financial_data)

        except ServiceError as e:
            self.logger.exception("加载财务数据失败", exc_info=e)
            self._update_status(f"加载失败: {e}")
            messagebox.showerror("错误", f"加载财务数据失败: {e}")
        except Exception as e:
            self.logger.exception("加载财务数据时发生未知错误", exc_info=e)
            self._update_status("加载失败")
            messagebox.showerror("错误", f"加载财务数据时发生未知错误: {e}")

    def _perform_analysis(self) -> None:
        """执行财务分析."""
        try:
            # 计算关键指标
            total_receivables = self.financial_data.get("total_receivables", 0)
            total_payables = self.financial_data.get("total_payables", 0)
            overdue_receivables = self.financial_data.get("overdue_receivables", 0)

            # 计算净头寸
            net_position = total_receivables - total_payables

            # 计算逾期率
            receivables_overdue_rate = (
                (overdue_receivables / total_receivables * 100)
                if total_receivables > 0
                else 0
            )

            # 估算现金流(简化计算)
            cash_flow = net_position * 0.8  # 假设80%的净头寸为现金流

            # 存储分析结果
            self.analysis_results = {
                "total_receivables": total_receivables,
                "total_payables": total_payables,
                "net_position": net_position,
                "overdue_receivables": overdue_receivables,
                "receivables_overdue_rate": receivables_overdue_rate,
                "cash_flow": cash_flow,
                "analysis_date": datetime.now(tz=timezone.utc).isoformat(),
            }

            # 生成风险预警
            self._generate_risk_warnings()

        except Exception as e:
            error_msg = f"财务分析失败: {e}"
            self.logger.exception("财务分析失败", exc_info=e)
            raise ServiceError(error_msg) from e

    def _generate_risk_warnings(self) -> None:
        """生成风险预警."""
        warnings = []

        overdue_rate = self.analysis_results.get("receivables_overdue_rate", 0)
        net_position = self.analysis_results.get("net_position", 0)
        overdue_amount = self.analysis_results.get("overdue_receivables", 0)

        # 逾期率预警
        if overdue_rate > 20:
            warnings.append(f"⚠️ 应收账款逾期率过高: {overdue_rate:.1f}%")
        elif overdue_rate > 10:
            warnings.append(f"⚡ 应收账款逾期率偏高: {overdue_rate:.1f}%")

        # 净头寸预警
        if net_position < 0:
            warnings.append(f"🔴 净头寸为负: ¥{abs(net_position):,.2f}")

        # 逾期金额预警
        if overdue_amount > 100000:  # 10万以上
            warnings.append(f"💰 逾期应收金额较大: ¥{overdue_amount:,.2f}")

        # 如果没有预警, 显示正常状态
        if not warnings:
            warnings.append("✅ 财务状况良好, 无重大风险预警")

        self.analysis_results["risk_warnings"] = warnings

    def _update_summary_display(self) -> None:
        """更新财务概览显示."""
        try:
            # 更新关键指标
            for key, label_widget in self.metrics_labels.items():
                value = self.analysis_results.get(key, 0)

                if key.endswith("_rate"):
                    # 百分比格式
                    formatted_value = f"{value:.1f}%"
                    # 根据数值设置颜色
                    if value > 15:
                        label_widget.config(foreground="red")
                    elif value > 8:
                        label_widget.config(foreground="orange")
                    else:
                        label_widget.config(foreground="green")
                else:
                    # 货币格式
                    formatted_value = f"¥{value:,.2f}"
                    # 根据正负设置颜色
                    if key == "net_position":
                        if value < 0:
                            label_widget.config(foreground="red")
                        else:
                            label_widget.config(foreground="green")
                    else:
                        label_widget.config(foreground="black")

                label_widget.config(text=formatted_value)

            # 更新风险预警
            self.risk_text.config(state=tk.NORMAL)
            self.risk_text.delete(1.0, tk.END)

            warnings = self.analysis_results.get("risk_warnings", [])
            for warning in warnings:
                self.risk_text.insert(tk.END, warning + "\n")

            self.risk_text.config(state=tk.DISABLED)

        except Exception as e:
            self.logger.exception("更新概览显示失败", exc_info=e)

    def _update_charts(self) -> None:
        """更新图表显示."""
        try:
            # 更新概览图表
            if self.summary_chart:
                self._update_summary_chart()

            # 更新趋势图表
            if self.trend_chart:
                self._update_trend_chart()

            # 更新对比图表
            if self.comparison_chart:
                self._update_comparison_chart()

        except Exception as e:
            self.logger.exception("更新图表失败", exc_info=e)

    def _update_summary_chart(self) -> None:
        """更新概览图表."""
        # 创建财务概览饼图数据
        labels = ["应收账款", "应付账款"]
        values = [
            self.analysis_results.get("total_receivables", 0),
            self.analysis_results.get("total_payables", 0),
        ]

        chart_data = create_chart_data(
            x_data=labels, y_data=values, title="财务概览", labels=labels
        )

        if self.summary_chart is not None:
            self.summary_chart.set_chart_type(ChartType.PIE)
            self.summary_chart.set_data(chart_data)

    def _update_trend_chart(self) -> None:
        """更新趋势图表."""
        # 模拟趋势数据(实际应该从数据库获取历史数据)
        days = int(self.time_range_var.get())
        dates = [
            (datetime.now(tz=timezone.utc) - timedelta(days=i)).strftime("%m-%d")
            for i in range(days, 0, -1)
        ]

        # 模拟应收账款趋势

        base_value = self.analysis_results.get("total_receivables", 100000)
        receivables_trend = [
            base_value + random.randint(-10000, 10000) for _ in range(len(dates))
        ]

        chart_data = create_chart_data(
            x_data=dates,
            y_data=receivables_trend,
            title=f"应收账款趋势 (近{days}天)",
            x_label="日期",
            y_label="金额 (¥)",
        )

        if self.trend_chart is not None:
            chart_type = ChartType(self.chart_type_var.get())
            self.trend_chart.set_chart_type(chart_type)
            self.trend_chart.set_data(chart_data)

    def _update_comparison_chart(self) -> None:
        """更新对比图表."""
        # 创建应收应付对比图
        categories = ["本月", "上月", "上上月"]
        receivables = [
            self.analysis_results.get("total_receivables", 0),
            self.analysis_results.get("total_receivables", 0) * 0.9,
            self.analysis_results.get("total_receivables", 0) * 0.8,
        ]
        # TODO: 添加应付账款数据到图表中, 需要支持多系列数据

        # 这里简化处理, 实际应该支持多系列数据
        chart_data = create_chart_data(
            x_data=categories,
            y_data=receivables,
            title="应收应付对比",
            x_label="时间",
            y_label="金额 (¥)",
        )

        if self.comparison_chart is not None:
            self.comparison_chart.set_chart_type(ChartType.BAR)
            self.comparison_chart.set_data(chart_data)

    def _refresh_data(self) -> None:
        """刷新数据."""
        self._load_financial_data()

    def _toggle_auto_refresh(self) -> None:
        """切换自动刷新."""
        self.auto_refresh = self.auto_refresh_var.get()

        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _start_auto_refresh(self) -> None:
        """启动自动刷新."""
        if self.refresh_timer:
            self.refresh_timer.cancel()

        self.refresh_timer = threading.Timer(
            self.refresh_interval, self._auto_refresh_callback
        )
        self.refresh_timer.start()

    def _stop_auto_refresh(self) -> None:
        """停止自动刷新."""
        if self.refresh_timer:
            self.refresh_timer.cancel()
            self.refresh_timer = None

    def _auto_refresh_callback(self) -> None:
        """自动刷新回调."""
        try:
            self._refresh_data()
        except Exception as e:
            self.logger.exception("自动刷新失败", exc_info=e)
        finally:
            # 重新启动定时器
            if self.auto_refresh:
                self._start_auto_refresh()

    def _on_chart_type_changed(self, _event: Any) -> None:
        """图表类型变化事件."""
        self._update_charts()

    def _on_time_range_changed(self, _event: Any) -> None:
        """时间范围变化事件."""
        self._update_charts()

    def _quick_export(self) -> None:
        """快速导出."""
        try:
            # 使用默认设置快速导出Excel
            filename = f"财务分析报告_{datetime.now(tz=timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=filename,
            )

            if filepath:
                success = self._export_to_excel(filepath)
                if success:
                    messagebox.showinfo("导出成功", f"财务报表已导出到:\n{filepath}")
                else:
                    messagebox.showerror("导出失败", "导出过程中发生错误")

        except Exception as e:
            self.logger.exception("快速导出失败", exc_info=e)
            messagebox.showerror("导出失败", f"导出失败: {e}")

    def _select_export_directory(self) -> None:
        """选择导出目录."""
        directory = filedialog.askdirectory()
        if directory:
            self.export_directory = directory
            self.export_status_label.config(text=f"导出目录: {directory}")

    def _start_export(self) -> None:
        """开始导出."""
        try:
            # 检查导出设置
            selected_formats = [
                fmt for fmt, var in self.export_formats.items() if var.get()
            ]

            if not selected_formats:
                messagebox.showwarning("导出警告", "请至少选择一种导出格式")
                return

            # 获取导出目录
            if not hasattr(self, "export_directory"):
                self._select_export_directory()
                if not hasattr(self, "export_directory"):
                    return

            # 开始导出进度
            self.export_progress.start()
            self.export_status_label.config(text="正在导出...")

            # 在后台线程执行导出
            export_thread = threading.Thread(
                target=self._perform_export, args=(selected_formats,)
            )
            export_thread.daemon = True
            export_thread.start()

        except Exception as e:
            self.logger.exception("启动导出失败", exc_info=e)
            messagebox.showerror("导出失败", f"启动导出失败: {e}")

    def _perform_export(self, formats: list[str]) -> None:
        """执行导出操作."""
        try:
            # 生成文件名
            timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
            base_filename = self.filename_var.get().format(date=timestamp)

            results = {}

            for fmt in formats:
                filename = f"{base_filename}.{fmt}"
                filepath = f"{self.export_directory}/{filename}"

                if fmt in {"excel", "csv"}:
                    success = self._export_to_excel(filepath)
                elif fmt == "pdf":
                    success = self._export_to_pdf(filepath)
                else:
                    success = False

                results[fmt] = success

            # 更新UI(需要在主线程中执行)
            self.after(0, self._export_completed, results)

        except Exception as e:
            self.logger.exception("导出执行失败", exc_info=e)
            self.after(0, self._export_failed, str(e))

    def _export_to_excel(self, filepath: str) -> bool:
        """导出到Excel."""
        try:
            # 准备导出数据
            export_data = {
                "financial_summary": self.financial_data,
                "analysis_results": self.analysis_results,
                "export_time": datetime.now(tz=timezone.utc).isoformat(),
            }

            return self.excel_exporter.export_financial_report(export_data, filepath)

        except Exception as e:
            self.logger.exception("Excel导出失败", exc_info=e)
            return False

    def _export_to_pdf(self, _filepath: str) -> bool:
        """导出到PDF."""
        try:
            # 由于QuotePDFExportService是专门用于报价单的,
            # 这里暂时返回False, 表示PDF导出功能需要专门的财务报表PDF服务
            self.logger.warning("PDF导出功能需要专门的财务报表PDF服务, 当前暂不支持")
        except Exception as e:
            self.logger.exception("PDF导出失败", exc_info=e)
        return False

    def _get_chart_images(self) -> dict[str, str]:
        """获取图表图片."""
        # 这里应该实现图表的图片导出
        # 返回图表名称到图片路径的映射
        return {}

    def _export_completed(self, results: dict[str, bool]) -> None:
        """导出完成回调."""
        self.export_progress.stop()

        success_count = sum(results.values())
        total_count = len(results)

        if success_count == total_count:
            self.export_status_label.config(text="导出完成")
            messagebox.showinfo(
                "导出成功", f"所有格式导出成功 ({success_count}/{total_count})"
            )
        else:
            self.export_status_label.config(text="部分导出失败")
            failed_formats = [fmt for fmt, success in results.items() if not success]
            failed_list = ", ".join(failed_formats)
            messagebox.showwarning(
                "部分导出失败",
                f"成功: {success_count}/{total_count}\n失败格式: {failed_list}",
            )

        # 触发导出完成事件
        if self.on_export_completed:
            self.on_export_completed(results)

    def _export_failed(self, error_msg: str) -> None:
        """导出失败回调."""
        self.export_progress.stop()
        self.export_status_label.config(text="导出失败")
        messagebox.showerror("导出失败", f"导出过程中发生错误: {error_msg}")

    def _update_status(self, status: str) -> None:
        """更新状态显示."""
        self.status_label.config(text=status)
        self.update_idletasks()

    def get_financial_data(self) -> dict[str, Any]:
        """获取财务数据."""
        return self.financial_data.copy()

    def get_analysis_results(self) -> dict[str, Any]:
        """获取分析结果."""
        return self.analysis_results.copy()

    def set_refresh_interval(self, interval: int) -> None:
        """设置刷新间隔.

        Args:
            interval: 刷新间隔(秒)
        """
        self.refresh_interval = interval
        if self.auto_refresh:
            self._stop_auto_refresh()
            self._start_auto_refresh()

    def cleanup(self) -> None:
        """清理资源."""
        try:
            # 停止自动刷新
            self._stop_auto_refresh()

            # 清理图表组件
            if self.summary_chart:
                self.summary_chart.cleanup()
            if self.trend_chart:
                self.trend_chart.cleanup()
            if self.comparison_chart:
                self.comparison_chart.cleanup()

            # 调用父类清理
            super().cleanup()

        except Exception as e:
            self.logger.exception("清理财务分析组件失败", exc_info=e)
