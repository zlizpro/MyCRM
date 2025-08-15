"""
MiniCRM 仪表盘组件 - 重构版本

严格遵循分层架构和SOLID原则：
- 只负责界面展示和用户交互
- 通过依赖注入使用Services
- 不包含业务逻辑和数据加载逻辑
- 实现IDashboard接口
- 遵循单一职责原则
"""

from typing import Any

from PySide6.QtCore import Qt, QTimer, Signal, pyqtSlot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from minicrm.core.interfaces.service_interfaces import IAnalyticsService
from minicrm.core.interfaces.ui_interfaces import IDashboard
from minicrm.ui.components.base_widget import BaseWidget
from minicrm.ui.components.chart_widget import ChartWidget
from minicrm.ui.components.loading_widget import LoadingWidget
from minicrm.ui.components.metric_card import MetricCard


class Dashboard(BaseWidget, IDashboard):
    """
    仪表盘主组件

    严格遵循UI层职责：
    - 只负责界面展示和用户交互
    - 通过依赖注入使用AnalyticsService
    - 实现IDashboard接口
    - 不包含业务逻辑

    职责：
    - 显示关键指标卡片
    - 显示数据可视化图表
    - 处理用户交互事件
    - 管理UI状态和布局
    """

    # Qt信号定义
    refresh_requested = Signal()
    metric_clicked = Signal(str)
    chart_clicked = Signal(str)

    def __init__(self, analytics_service: IAnalyticsService, parent: QWidget = None):
        """
        初始化仪表盘组件

        Args:
            analytics_service: 分析服务接口
            parent: 父组件
        """
        super().__init__(parent)

        # 依赖注入的服务
        self._analytics_service = analytics_service

        # UI组件
        self._scroll_area: QScrollArea = None
        self._content_widget: QWidget = None
        self._metrics_grid: QGridLayout = None
        self._charts_layout: QVBoxLayout = None
        self._loading_widget: LoadingWidget = None

        # 数据存储
        self._metric_cards: dict[str, MetricCard] = {}
        self._chart_widgets: dict[str, ChartWidget] = {}

        # 自动刷新定时器
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._on_auto_refresh)

        # 初始化UI
        self.setup_ui()

        # 连接信号
        self._connect_signals()

        # 启动自动刷新（每5分钟）
        self._refresh_timer.start(300000)

        self._logger.debug("仪表盘初始化完成")

    def setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置主布局
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)

            # 创建标题区域
            self._create_title_section(main_layout)

            # 创建加载组件
            self._loading_widget = LoadingWidget()
            main_layout.addWidget(self._loading_widget)

            # 创建滚动区域
            self._create_scroll_area(main_layout)

            # 创建内容区域
            self._create_content_area()

            # 应用样式
            self._apply_styles()

        except Exception as e:
            self._logger.error(f"仪表盘UI设置失败: {e}")
            self.show_message(f"界面初始化失败: {e}", "error")

    def _create_title_section(self, layout: QVBoxLayout) -> None:
        """创建标题区域"""
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # 标题标签
        title_label = QLabel("数据仪表盘")
        title_label.setObjectName("dashboardTitle")

        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # 刷新按钮
        refresh_button = QPushButton("🔄 刷新")
        refresh_button.setObjectName("refreshButton")
        refresh_button.clicked.connect(self._on_refresh_clicked)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(refresh_button)

        layout.addWidget(title_frame)

    def _create_scroll_area(self, layout: QVBoxLayout) -> None:
        """创建滚动区域"""
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.hide()  # 初始隐藏，加载完成后显示

        layout.addWidget(self._scroll_area)

    def _create_content_area(self) -> None:
        """创建内容区域"""
        self._content_widget = QWidget()
        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(30)

        # 创建指标卡片区域
        self._create_metrics_section(content_layout)

        # 创建图表区域
        self._create_charts_section(content_layout)

        # 添加弹性空间
        content_layout.addStretch()

        self._scroll_area.setWidget(self._content_widget)

    def _create_metrics_section(self, layout: QVBoxLayout) -> None:
        """创建指标卡片区域"""
        # 区域标题
        metrics_title = QLabel("关键指标")
        metrics_title.setObjectName("sectionTitle")

        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        metrics_title.setFont(title_font)

        layout.addWidget(metrics_title)

        # 指标卡片网格
        metrics_frame = QFrame()
        self._metrics_grid = QGridLayout(metrics_frame)
        self._metrics_grid.setSpacing(15)

        layout.addWidget(metrics_frame)

    def _create_charts_section(self, layout: QVBoxLayout) -> None:
        """创建图表区域"""
        # 区域标题
        charts_title = QLabel("数据图表")
        charts_title.setObjectName("sectionTitle")

        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        charts_title.setFont(title_font)

        layout.addWidget(charts_title)

        # 图表容器
        charts_frame = QFrame()
        self._charts_layout = QVBoxLayout(charts_frame)
        self._charts_layout.setSpacing(20)

        layout.addWidget(charts_frame)

    def _connect_signals(self) -> None:
        """连接信号"""
        self.refresh_requested.connect(self._handle_refresh_request)

    def _apply_styles(self) -> None:
        """应用样式"""
        self.setStyleSheet("""
            QLabel#dashboardTitle {
                color: #2c3e50;
                margin-bottom: 10px;
            }

            QLabel#sectionTitle {
                color: #34495e;
                margin: 10px 0px;
                padding: 5px 0px;
                border-bottom: 2px solid #3498db;
            }

            QPushButton#refreshButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton#refreshButton:hover {
                background-color: #2980b9;
            }

            QPushButton#refreshButton:pressed {
                background-color: #21618c;
            }
        """)

    # IDashboard接口实现
    def update_metrics(self, metrics: dict[str, Any]) -> None:
        """
        更新关键指标

        Args:
            metrics: 指标数据字典
        """
        try:
            # 清除现有指标卡片
            self._clear_metrics()

            # 创建新的指标卡片
            row, col = 0, 0
            max_cols = 4

            for key, value in metrics.items():
                metric_card = self._create_metric_card(key, value)
                self._metrics_grid.addWidget(metric_card, row, col)
                self._metric_cards[key] = metric_card

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            self._logger.debug(f"更新了 {len(metrics)} 个指标")

        except Exception as e:
            self._logger.error(f"更新指标失败: {e}")
            self.show_message(f"更新指标失败: {e}", "error")

    def update_charts(self, chart_data: dict[str, Any]) -> None:
        """
        更新图表数据

        Args:
            chart_data: 图表数据字典
        """
        try:
            # 清除现有图表
            self._clear_charts()

            # 创建新的图表
            for chart_name, data in chart_data.items():
                chart_widget = self._create_chart_widget(chart_name, data)
                self._charts_layout.addWidget(chart_widget)
                self._chart_widgets[chart_name] = chart_widget

            self._logger.debug(f"更新了 {len(chart_data)} 个图表")

        except Exception as e:
            self._logger.error(f"更新图表失败: {e}")
            self.show_message(f"更新图表失败: {e}", "error")

    def refresh_all(self) -> None:
        """刷新所有仪表盘数据"""
        self.refresh_requested.emit()

    def set_loading(self, loading: bool) -> None:
        """
        设置加载状态

        Args:
            loading: 是否正在加载
        """
        if loading:
            self._loading_widget.show()
            self._scroll_area.hide()
        else:
            self._loading_widget.hide()
            self._scroll_area.show()

    # 私有方法
    def _create_metric_card(self, key: str, value: Any) -> MetricCard:
        """
        创建指标卡片

        Args:
            key: 指标键名
            value: 指标值

        Returns:
            MetricCard: 指标卡片组件
        """
        metric_card = MetricCard()
        metric_card.set_title(self._format_metric_title(key))
        metric_card.set_value(str(value))
        metric_card.set_icon(self._get_metric_icon(key))

        # 连接点击信号
        metric_card.clicked.connect(lambda: self.metric_clicked.emit(key))

        return metric_card

    def _create_chart_widget(
        self, chart_name: str, data: dict[str, Any]
    ) -> ChartWidget:
        """
        创建图表组件

        Args:
            chart_name: 图表名称
            data: 图表数据

        Returns:
            ChartWidget: 图表组件
        """
        chart_widget = ChartWidget()
        chart_widget.set_title(self._format_chart_title(chart_name))
        chart_widget.set_data(data)

        # 连接点击信号
        chart_widget.clicked.connect(lambda: self.chart_clicked.emit(chart_name))

        return chart_widget

    def _clear_metrics(self) -> None:
        """清除现有指标卡片"""
        for card in self._metric_cards.values():
            card.deleteLater()
        self._metric_cards.clear()

    def _clear_charts(self) -> None:
        """清除现有图表"""
        for chart in self._chart_widgets.values():
            chart.deleteLater()
        self._chart_widgets.clear()

    def _format_metric_title(self, key: str) -> str:
        """格式化指标标题"""
        title_map = {
            "total_customers": "客户总数",
            "new_customers_this_month": "本月新增客户",
            "pending_tasks": "待办任务",
            "total_receivables": "应收账款",
            "total_payables": "应付账款",
        }
        return title_map.get(key, key.replace("_", " ").title())

    def _format_chart_title(self, chart_name: str) -> str:
        """格式化图表标题"""
        title_map = {
            "customer_growth": "客户增长趋势",
            "customer_types": "客户类型分布",
            "monthly_interactions": "月度互动频率",
            "receivables_status": "应收账款状态",
        }
        return title_map.get(chart_name, chart_name.replace("_", " ").title())

    def _get_metric_icon(self, key: str) -> str:
        """获取指标图标"""
        icon_map = {
            "total_customers": "👥",
            "new_customers_this_month": "📈",
            "pending_tasks": "📋",
            "total_receivables": "💰",
            "total_payables": "💳",
        }
        return icon_map.get(key, "📊")

    # 事件处理
    @pyqtSlot()
    def _on_refresh_clicked(self) -> None:
        """处理刷新按钮点击"""
        self.refresh_all()

    @pyqtSlot()
    def _on_auto_refresh(self) -> None:
        """处理自动刷新"""
        self.refresh_all()

    @pyqtSlot()
    def _handle_refresh_request(self) -> None:
        """处理刷新请求"""
        try:
            self.set_loading(True)

            # 通过服务获取数据
            dashboard_data = self._analytics_service.get_dashboard_data()

            # 更新UI
            if "metrics" in dashboard_data:
                self.update_metrics(dashboard_data["metrics"])

            if "charts" in dashboard_data:
                self.update_charts(dashboard_data["charts"])

            self.set_loading(False)

        except Exception as e:
            self.set_loading(False)
            self._logger.error(f"刷新数据失败: {e}")
            self.show_message(f"刷新数据失败: {e}", "error")

    def cleanup(self) -> None:
        """清理资源"""
        if self._refresh_timer:
            self._refresh_timer.stop()

        self._clear_metrics()
        self._clear_charts()

        super().cleanup()
        self._logger.debug("仪表盘资源清理完成")
