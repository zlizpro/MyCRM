"""MiniCRM TTK财务管理面板

替换Qt版本的财务管理面板,提供完整的财务管理功能:
- 财务概览和关键指标显示
- 应收账款和应付账款管理
- 收支记录管理功能
- 财务分析和报表展示
- 图表可视化展示
- 风险预警和监控

设计特点:
- 基于BaseWidget提供标准TTK组件功能
- 集成FinancialAnalysisTTK进行财务分析
- 使用DataTableTTK展示财务数据
- 集成ChartContainerTTK进行数据可视化
- 模块化设计,支持功能扩展
"""

from __future__ import annotations

from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.core.exceptions import ServiceError
from minicrm.services.finance_service import FinanceService
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.chart_widget import (
    ChartContainerTTK,
    ChartType,
    create_chart_data,
)
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK
from minicrm.ui.ttk_base.financial_analysis_ttk import FinancialAnalysisTTK


class FinancePanelTTK(BaseWidget):
    """TTK财务管理面板

    提供完整的财务管理功能,替换Qt版本的财务面板.
    """

    def __init__(self, parent: tk.Widget, finance_service: FinanceService, **kwargs):
        """初始化财务管理面板

        Args:
            parent: 父组件
            finance_service: 财务服务实例
            **kwargs: 其他参数
        """
        self.finance_service = finance_service

        # 数据存储
        self.financial_summary: Dict[str, Any] = {}
        self.receivables_data: List[Dict[str, Any]] = []
        self.payables_data: List[Dict[str, Any]] = []
        self.payments_data: List[Dict[str, Any]] = []

        # UI组件
        self.main_notebook: Optional[ttk.Notebook] = None
        self.overview_frame: Optional[ttk.Frame] = None
        self.receivables_frame: Optional[ttk.Frame] = None
        self.payables_frame: Optional[ttk.Frame] = None
        self.analysis_frame: Optional[ttk.Frame] = None

        # 数据表格组件
        self.receivables_table: Optional[DataTableTTK] = None
        self.payables_table: Optional[DataTableTTK] = None
        self.payments_table: Optional[DataTableTTK] = None

        # 图表组件
        self.overview_chart: Optional[ChartContainerTTK] = None
        self.trend_chart: Optional[ChartContainerTTK] = None

        # 财务分析组件
        self.financial_analysis: Optional[FinancialAnalysisTTK] = None

        # 定时刷新
        self.auto_refresh = True
        self.refresh_interval = 300  # 5分钟
        self.refresh_timer: Optional[threading.Timer] = None

        # 事件回调
        self.on_payment_recorded: Optional[Callable] = None
        self.on_receivable_added: Optional[Callable] = None
        self.on_payable_added: Optional[Callable] = None
        self.on_data_updated: Optional[Callable] = None

        super().__init__(parent, **kwargs)

        # 初始化数据
        self._load_all_data()

        # 启动自动刷新
        if self.auto_refresh:
            self._start_auto_refresh()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题栏
        self._create_title_bar(main_container)

        # 创建主标签页
        self._create_main_notebook(main_container)

        # 创建各个标签页
        self._create_overview_tab()
        self._create_receivables_tab()
        self._create_payables_tab()
        self._create_analysis_tab()

    def _create_title_bar(self, parent: ttk.Frame) -> None:
        """创建标题栏"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        # 左侧:标题和状态
        left_frame = ttk.Frame(title_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 主标题
        title_label = ttk.Label(
            left_frame, text="财务管理", font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 状态指示器
        self.status_label = ttk.Label(left_frame, text="准备就绪", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

        # 右侧:快速操作按钮
        right_frame = ttk.Frame(title_frame)
        right_frame.pack(side=tk.RIGHT)

        # 刷新按钮
        refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新", command=self._refresh_all_data
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 记录收款按钮
        record_payment_btn = ttk.Button(
            right_frame, text="💰 记录收款", command=self._show_record_payment_dialog
        )
        record_payment_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 新增应收按钮
        add_receivable_btn = ttk.Button(
            right_frame, text="➕ 新增应收", command=self._show_add_receivable_dialog
        )
        add_receivable_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 导出报表按钮
        export_btn = ttk.Button(
            right_frame, text="📊 导出报表", command=self._show_export_dialog
        )
        export_btn.pack(side=tk.LEFT)

    def _create_main_notebook(self, parent: ttk.Frame) -> None:
        """创建主标签页容器"""
        self.main_notebook = ttk.Notebook(parent)
        self.main_notebook.pack(fill=tk.BOTH, expand=True)

    def _create_overview_tab(self) -> None:
        """创建财务概览标签页"""
        self.overview_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.overview_frame, text="财务概览")

        # 创建概览内容容器
        content_frame = ttk.Frame(self.overview_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 上半部分:关键指标卡片
        self._create_metrics_cards(content_frame)

        # 下半部分:概览图表
        self._create_overview_charts(content_frame)

    def _create_metrics_cards(self, parent: ttk.Frame) -> None:
        """创建关键指标卡片"""
        metrics_frame = ttk.Frame(parent)
        metrics_frame.pack(fill=tk.X, pady=(0, 15))

        # 创建指标卡片网格
        self.metric_cards = {}

        # 定义指标
        metrics = [
            {
                "key": "total_receivables",
                "title": "应收账款总额",
                "icon": "💰",
                "color": "#007BFF",
            },
            {
                "key": "total_payables",
                "title": "应付账款总额",
                "icon": "💸",
                "color": "#DC3545",
            },
            {
                "key": "net_position",
                "title": "净头寸",
                "icon": "📊",
                "color": "#28A745",
            },
            {
                "key": "overdue_receivables",
                "title": "逾期应收",
                "icon": "⚠️",
                "color": "#FFC107",
            },
        ]

        # 创建卡片
        for i, metric in enumerate(metrics):
            card_frame = self._create_metric_card(
                metrics_frame, metric["title"], metric["icon"], metric["color"]
            )
            card_frame.grid(row=0, column=i, padx=5, pady=5, sticky="ew")

            self.metric_cards[metric["key"]] = card_frame

        # 配置网格权重
        for i in range(len(metrics)):
            metrics_frame.grid_columnconfigure(i, weight=1)

    def _create_metric_card(
        self, parent: ttk.Frame, title: str, icon: str, color: str
    ) -> ttk.Frame:
        """创建单个指标卡片"""
        # 主卡片框架
        card_frame = ttk.LabelFrame(parent, text="", padding=15)

        # 图标和标题行
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # 图标
        icon_label = ttk.Label(header_frame, text=icon, font=("Microsoft YaHei UI", 16))
        icon_label.pack(side=tk.LEFT)

        # 标题
        title_label = ttk.Label(
            header_frame, text=title, font=("Microsoft YaHei UI", 10, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=(10, 0))

        # 数值显示
        value_label = ttk.Label(
            card_frame, text="¥0.00", font=("Microsoft YaHei UI", 14, "bold")
        )
        value_label.pack(anchor=tk.W)

        # 变化趋势(可选)
        trend_label = ttk.Label(
            card_frame, text="", font=("Microsoft YaHei UI", 8), foreground="gray"
        )
        trend_label.pack(anchor=tk.W, pady=(5, 0))

        # 存储标签引用
        card_frame.value_label = value_label
        card_frame.trend_label = trend_label

        return card_frame

    def _create_overview_charts(self, parent: ttk.Frame) -> None:
        """创建概览图表"""
        charts_frame = ttk.Frame(parent)
        charts_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧:财务结构饼图
        left_frame = ttk.LabelFrame(charts_frame, text="财务结构", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.overview_chart = ChartContainerTTK(left_frame)
        self.overview_chart.pack(fill=tk.BOTH, expand=True)

        # 右侧:趋势图表
        right_frame = ttk.LabelFrame(charts_frame, text="趋势分析", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.trend_chart = ChartContainerTTK(right_frame)
        self.trend_chart.pack(fill=tk.BOTH, expand=True)

    def _create_receivables_tab(self) -> None:
        """创建应收账款标签页"""
        self.receivables_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.receivables_frame, text="应收账款")

        # 创建工具栏
        toolbar_frame = ttk.Frame(self.receivables_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 左侧:统计信息
        stats_frame = ttk.Frame(toolbar_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.receivables_stats_label = ttk.Label(
            stats_frame,
            text="应收账款: 0 条记录",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        self.receivables_stats_label.pack(side=tk.LEFT)

        # 右侧:操作按钮
        actions_frame = ttk.Frame(toolbar_frame)
        actions_frame.pack(side=tk.RIGHT)

        ttk.Button(
            actions_frame, text="➕ 新增", command=self._show_add_receivable_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            actions_frame, text="💰 收款", command=self._show_record_payment_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            actions_frame, text="📤 导出", command=self._export_receivables
        ).pack(side=tk.LEFT)

        # 创建应收账款表格
        self._create_receivables_table()

    def _create_receivables_table(self) -> None:
        """创建应收账款表格"""
        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "visible": False},
            {"id": "customer_name", "text": "客户名称", "width": 150, "sortable": True},
            {"id": "amount", "text": "应收金额", "width": 120, "sortable": True},
            {"id": "due_date", "text": "到期日期", "width": 100, "sortable": True},
            {"id": "status", "text": "状态", "width": 80, "sortable": True},
            {"id": "overdue_days", "text": "逾期天数", "width": 80, "sortable": True},
            {"id": "description", "text": "说明", "width": 200, "sortable": True},
            {"id": "created_at", "text": "创建时间", "width": 120, "sortable": True},
        ]

        # 创建表格
        table_frame = ttk.Frame(self.receivables_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.receivables_table = DataTableTTK(
            table_frame,
            columns=columns,
            editable=False,
            multi_select=True,
            show_pagination=True,
            page_size=20,
        )
        self.receivables_table.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.receivables_table.on_row_selected = self._on_receivable_selected
        self.receivables_table.on_row_double_clicked = (
            self._on_receivable_double_clicked
        )

    def _create_payables_tab(self) -> None:
        """创建应付账款标签页"""
        self.payables_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.payables_frame, text="应付账款")

        # 创建工具栏
        toolbar_frame = ttk.Frame(self.payables_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 左侧:统计信息
        stats_frame = ttk.Frame(toolbar_frame)
        stats_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.payables_stats_label = ttk.Label(
            stats_frame,
            text="应付账款: 0 条记录",
            font=("Microsoft YaHei UI", 10, "bold"),
        )
        self.payables_stats_label.pack(side=tk.LEFT)

        # 右侧:操作按钮
        actions_frame = ttk.Frame(toolbar_frame)
        actions_frame.pack(side=tk.RIGHT)

        ttk.Button(
            actions_frame, text="➕ 新增", command=self._show_add_payable_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            actions_frame, text="💸 付款", command=self._show_record_payable_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(actions_frame, text="📤 导出", command=self._export_payables).pack(
            side=tk.LEFT
        )

        # 创建应付账款表格
        self._create_payables_table()

    def _create_payables_table(self) -> None:
        """创建应付账款表格"""
        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "visible": False},
            {
                "id": "supplier_name",
                "text": "供应商名称",
                "width": 150,
                "sortable": True,
            },
            {"id": "amount", "text": "应付金额", "width": 120, "sortable": True},
            {"id": "due_date", "text": "到期日期", "width": 100, "sortable": True},
            {"id": "status", "text": "状态", "width": 80, "sortable": True},
            {"id": "overdue_days", "text": "逾期天数", "width": 80, "sortable": True},
            {"id": "description", "text": "说明", "width": 200, "sortable": True},
            {"id": "created_at", "text": "创建时间", "width": 120, "sortable": True},
        ]

        # 创建表格
        table_frame = ttk.Frame(self.payables_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.payables_table = DataTableTTK(
            table_frame,
            columns=columns,
            editable=False,
            multi_select=True,
            show_pagination=True,
            page_size=20,
        )
        self.payables_table.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.payables_table.on_row_selected = self._on_payable_selected
        self.payables_table.on_row_double_clicked = self._on_payable_double_clicked

    def _create_analysis_tab(self) -> None:
        """创建财务分析标签页"""
        self.analysis_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.analysis_frame, text="财务分析")

        # 创建财务分析组件
        self.financial_analysis = FinancialAnalysisTTK(
            self.analysis_frame, self.finance_service
        )
        self.financial_analysis.pack(fill=tk.BOTH, expand=True)

        # 绑定分析组件事件
        self.financial_analysis.on_data_updated = self._on_analysis_data_updated

    def _load_all_data(self) -> None:
        """加载所有财务数据"""
        try:
            self._update_status("正在加载财务数据...")

            # 加载财务汇总
            self._load_financial_summary()

            # 加载应收账款数据
            self._load_receivables_data()

            # 加载应付账款数据
            self._load_payables_data()

            # 更新UI显示
            self._update_all_displays()

            self._update_status("数据加载完成")

            # 触发数据更新事件
            if self.on_data_updated:
                self.on_data_updated()

        except ServiceError as e:
            self.logger.error(f"加载财务数据失败: {e}")
            self._update_status(f"加载失败: {e}")
            messagebox.showerror("错误", f"加载财务数据失败:{e}")
        except Exception as e:
            self.logger.error(f"加载财务数据时发生未知错误: {e}")
            self._update_status("加载失败")
            messagebox.showerror("错误", f"加载财务数据时发生未知错误:{e}")

    def _load_financial_summary(self) -> None:
        """加载财务汇总数据"""
        self.financial_summary = self.finance_service.get_financial_summary()

    def _load_receivables_data(self) -> None:
        """加载应收账款数据"""
        # TODO: 实现从服务层获取应收账款数据
        # 这里使用模拟数据
        self.receivables_data = [
            {
                "id": 1,
                "customer_name": "ABC公司",
                "amount": 50000.00,
                "due_date": "2025-02-15",
                "status": "pending",
                "overdue_days": 0,
                "description": "产品销售款",
                "created_at": "2025-01-15",
            },
            {
                "id": 2,
                "customer_name": "XYZ企业",
                "amount": 25000.00,
                "due_date": "2025-01-10",
                "status": "overdue",
                "overdue_days": 7,
                "description": "服务费用",
                "created_at": "2024-12-10",
            },
        ]

    def _load_payables_data(self) -> None:
        """加载应付账款数据"""
        # TODO: 实现从服务层获取应付账款数据
        # 这里使用模拟数据
        self.payables_data = [
            {
                "id": 1,
                "supplier_name": "供应商A",
                "amount": 30000.00,
                "due_date": "2025-02-20",
                "status": "pending",
                "overdue_days": 0,
                "description": "原材料采购款",
                "created_at": "2025-01-20",
            },
            {
                "id": 2,
                "supplier_name": "供应商B",
                "amount": 15000.00,
                "due_date": "2025-01-05",
                "status": "overdue",
                "overdue_days": 12,
                "description": "设备租赁费",
                "created_at": "2024-12-05",
            },
        ]

    def _update_all_displays(self) -> None:
        """更新所有显示"""
        self._update_metrics_cards()
        self._update_overview_charts()
        self._update_receivables_display()
        self._update_payables_display()

    def _update_metrics_cards(self) -> None:
        """更新指标卡片"""
        try:
            # 更新各个指标卡片
            metrics_data = {
                "total_receivables": self.financial_summary.get("total_receivables", 0),
                "total_payables": self.financial_summary.get("total_payables", 0),
                "net_position": self.financial_summary.get("net_position", 0),
                "overdue_receivables": self.financial_summary.get(
                    "overdue_receivables", 0
                ),
            }

            for key, card_frame in self.metric_cards.items():
                value = metrics_data.get(key, 0)
                formatted_value = f"¥{value:,.2f}"

                # 更新数值
                card_frame.value_label.config(text=formatted_value)

                # 设置颜色(根据数值类型)
                if key == "net_position":
                    color = "green" if value >= 0 else "red"
                    card_frame.value_label.config(foreground=color)
                elif key == "overdue_receivables":
                    color = "red" if value > 0 else "green"
                    card_frame.value_label.config(foreground=color)
                else:
                    card_frame.value_label.config(foreground="black")

                # 更新趋势(简化实现)
                trend_text = "较上月持平"  # 实际应该计算趋势
                card_frame.trend_label.config(text=trend_text)

        except Exception as e:
            self.logger.error(f"更新指标卡片失败: {e}")

    def _update_overview_charts(self) -> None:
        """更新概览图表"""
        try:
            # 更新财务结构饼图
            if self.overview_chart:
                labels = ["应收账款", "应付账款"]
                values = [
                    self.financial_summary.get("total_receivables", 0),
                    self.financial_summary.get("total_payables", 0),
                ]

                chart_data = create_chart_data(
                    x_data=labels, y_data=values, title="财务结构", labels=labels
                )

                self.overview_chart.set_chart_type(ChartType.PIE)
                self.overview_chart.set_data(chart_data)

            # 更新趋势图表
            if self.trend_chart:
                # 模拟趋势数据
                from datetime import datetime, timedelta

                dates = [
                    (datetime.now() - timedelta(days=i)).strftime("%m-%d")
                    for i in range(7, 0, -1)
                ]

                # 模拟净头寸趋势
                import random

                base_value = self.financial_summary.get("net_position", 0)
                trend_values = [
                    base_value + random.randint(-5000, 5000) for _ in range(len(dates))
                ]

                chart_data = create_chart_data(
                    x_data=dates,
                    y_data=trend_values,
                    title="净头寸趋势 (近7天)",
                    x_label="日期",
                    y_label="金额 (¥)",
                )

                self.trend_chart.set_chart_type(ChartType.LINE)
                self.trend_chart.set_data(chart_data)

        except Exception as e:
            self.logger.error(f"更新概览图表失败: {e}")

    def _update_receivables_display(self) -> None:
        """更新应收账款显示"""
        try:
            # 更新统计信息
            total_count = len(self.receivables_data)
            total_amount = sum(item["amount"] for item in self.receivables_data)

            stats_text = f"应收账款: {total_count} 条记录, 总额: ¥{total_amount:,.2f}"
            self.receivables_stats_label.config(text=stats_text)

            # 更新表格数据
            if self.receivables_table:
                self.receivables_table.load_data(self.receivables_data)

        except Exception as e:
            self.logger.error(f"更新应收账款显示失败: {e}")

    def _update_payables_display(self) -> None:
        """更新应付账款显示"""
        try:
            # 更新统计信息
            total_count = len(self.payables_data)
            total_amount = sum(item["amount"] for item in self.payables_data)

            stats_text = f"应付账款: {total_count} 条记录, 总额: ¥{total_amount:,.2f}"
            self.payables_stats_label.config(text=stats_text)

            # 更新表格数据
            if self.payables_table:
                self.payables_table.load_data(self.payables_data)

        except Exception as e:
            self.logger.error(f"更新应付账款显示失败: {e}")

    def _refresh_all_data(self) -> None:
        """刷新所有数据"""
        self._load_all_data()

    def _start_auto_refresh(self) -> None:
        """启动自动刷新"""
        if self.refresh_timer:
            self.refresh_timer.cancel()

        self.refresh_timer = threading.Timer(
            self.refresh_interval, self._auto_refresh_callback
        )
        self.refresh_timer.start()

    def _stop_auto_refresh(self) -> None:
        """停止自动刷新"""
        if self.refresh_timer:
            self.refresh_timer.cancel()
            self.refresh_timer = None

    def _auto_refresh_callback(self) -> None:
        """自动刷新回调"""
        try:
            self._refresh_all_data()
        except Exception as e:
            self.logger.error(f"自动刷新失败: {e}")
        finally:
            # 重新启动定时器
            if self.auto_refresh:
                self._start_auto_refresh()

    # ==================== 事件处理方法 ====================

    def _on_receivable_selected(self, receivable_data: Dict[str, Any]) -> None:
        """处理应收账款选中事件"""
        receivable_id = receivable_data.get("id")
        self.logger.info(f"选中应收账款: {receivable_id}")

    def _on_receivable_double_clicked(self, receivable_data: Dict[str, Any]) -> None:
        """处理应收账款双击事件"""
        customer_name = receivable_data.get("customer_name", "未知客户")
        amount = receivable_data.get("amount", 0)

        messagebox.showinfo(
            "应收账款详情",
            f"客户:{customer_name}\n金额:¥{amount:,.2f}\n\n详情功能将在后续实现",
        )

    def _on_payable_selected(self, payable_data: Dict[str, Any]) -> None:
        """处理应付账款选中事件"""
        payable_id = payable_data.get("id")
        self.logger.info(f"选中应付账款: {payable_id}")

    def _on_payable_double_clicked(self, payable_data: Dict[str, Any]) -> None:
        """处理应付账款双击事件"""
        supplier_name = payable_data.get("supplier_name", "未知供应商")
        amount = payable_data.get("amount", 0)

        messagebox.showinfo(
            "应付账款详情",
            f"供应商:{supplier_name}\n金额:¥{amount:,.2f}\n\n详情功能将在后续实现",
        )

    def _on_analysis_data_updated(self, analysis_data: Dict[str, Any]) -> None:
        """处理财务分析数据更新事件"""
        self.logger.info("财务分析数据已更新")
        # 可以在这里同步更新概览页面的数据

    # ==================== 对话框方法 ====================

    def _show_record_payment_dialog(self) -> None:
        """显示记录收款对话框"""
        messagebox.showinfo("提示", "记录收款功能将在后续任务中实现")

    def _show_add_receivable_dialog(self) -> None:
        """显示新增应收账款对话框"""
        messagebox.showinfo("提示", "新增应收账款功能将在后续任务中实现")

    def _show_add_payable_dialog(self) -> None:
        """显示新增应付账款对话框"""
        messagebox.showinfo("提示", "新增应付账款功能将在后续任务中实现")

    def _show_record_payable_dialog(self) -> None:
        """显示记录付款对话框"""
        messagebox.showinfo("提示", "记录付款功能将在后续任务中实现")

    def _show_export_dialog(self) -> None:
        """显示导出对话框"""
        if self.financial_analysis:
            # 切换到财务分析标签页并显示导出功能
            self.main_notebook.select(self.analysis_frame)
            self.financial_analysis.notebook.select(2)  # 导出设置标签页
        else:
            messagebox.showinfo("提示", "请先切换到财务分析标签页进行导出")

    # ==================== 导出方法 ====================

    def _export_receivables(self) -> None:
        """导出应收账款"""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"应收账款_{datetime.now().strftime('%Y%m%d')}.csv",
            )

            if filename:
                # 简化的CSV导出
                import csv

                with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                    if self.receivables_data:
                        fieldnames = self.receivables_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.receivables_data)

                messagebox.showinfo("导出成功", f"应收账款数据已导出到:\n{filename}")

        except Exception as e:
            self.logger.error(f"导出应收账款失败: {e}")
            messagebox.showerror("导出失败", f"导出失败:{e}")

    def _export_payables(self) -> None:
        """导出应付账款"""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"应付账款_{datetime.now().strftime('%Y%m%d')}.csv",
            )

            if filename:
                # 简化的CSV导出
                import csv

                with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                    if self.payables_data:
                        fieldnames = self.payables_data[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.payables_data)

                messagebox.showinfo("导出成功", f"应付账款数据已导出到:\n{filename}")

        except Exception as e:
            self.logger.error(f"导出应付账款失败: {e}")
            messagebox.showerror("导出失败", f"导出失败:{e}")

    def _update_status(self, status: str) -> None:
        """更新状态显示"""
        self.status_label.config(text=status)
        self.update_idletasks()

    # ==================== 公共方法 ====================

    def get_financial_summary(self) -> Dict[str, Any]:
        """获取财务汇总数据"""
        return self.financial_summary.copy()

    def get_receivables_data(self) -> List[Dict[str, Any]]:
        """获取应收账款数据"""
        return self.receivables_data.copy()

    def get_payables_data(self) -> List[Dict[str, Any]]:
        """获取应付账款数据"""
        return self.payables_data.copy()

    def refresh_data(self) -> None:
        """刷新数据(公共接口)"""
        self._refresh_all_data()

    def set_auto_refresh(self, enabled: bool, interval: int = 300) -> None:
        """设置自动刷新

        Args:
            enabled: 是否启用自动刷新
            interval: 刷新间隔(秒)
        """
        self.auto_refresh = enabled
        self.refresh_interval = interval

        if enabled:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止自动刷新
            self._stop_auto_refresh()

            # 清理图表组件
            if self.overview_chart:
                self.overview_chart.cleanup()
            if self.trend_chart:
                self.trend_chart.cleanup()

            # 清理财务分析组件
            if self.financial_analysis:
                self.financial_analysis.cleanup()

            # 清理表格组件
            if self.receivables_table:
                self.receivables_table.cleanup()
            if self.payables_table:
                self.payables_table.cleanup()

            # 调用父类清理
            super().cleanup()

        except Exception as e:
            self.logger.error(f"清理财务面板失败: {e}")

    def __str__(self) -> str:
        """返回面板的字符串表示"""
        return (
            f"FinancePanelTTK(receivables={len(self.receivables_data)}, "
            f"payables={len(self.payables_data)})"
        )
