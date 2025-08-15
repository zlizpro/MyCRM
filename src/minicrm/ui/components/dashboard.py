"""
MiniCRM 仪表盘组件

严格遵循UI层职责：
- 只负责界面展示和用户交互
- 通过依赖注入使用Services
- 不包含业务逻辑和数据加载逻辑
- 实现IDashboard接口

提供功能：
- 关键指标卡片显示
- 图表数据可视化
- 实时数据更新
- 响应式布局
- 交互式图表
"""

import logging
from typing import Any

from PySide6.QtCore import Qt, QThread, QTimer, Signal
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

from minicrm.core.interfaces.ui_interfaces import IDashboard
from minicrm.ui.components.base_widget import BaseWidget
from minicrm.ui.components.chart_widget import ChartWidget
from minicrm.ui.components.metric_card import MetricCard


class Dashboard(BaseWidget, IDashboard):
    """
    仪表盘主组件

    严格遵循UI层职责：
    - 只负责界面展示和用户交互
    - 通过依赖注入使用AnalyticsService
    - 实现IDashboard接口
    - 不包含业务逻辑

    显示系统的关键指标和数据可视化图表，包括：
    - 关键业务指标卡片
    - 客户增长趋势图
    - 客户类型分布图
    - 财务状况图表
    - 业务活动统计

    Signals:
        data_refreshed: 数据刷新完成信号
        metric_clicked: 指标卡片点击信号 (metric_name: str)
    """

    # Qt信号定义
    data_refreshed = Signal()
    metric_clicked = Signal(str)

    def __init__(self, app: Any, parent: QWidget | None = None):
        """
        初始化仪表盘

        Args:
            app: MiniCRM应用程序实例
            parent: 父组件
        """
        super().__init__(parent)

        self._app = app
        self._logger = logging.getLogger(__name__)

        # UI组件
        self._scroll_area: QScrollArea | None = None
        self._content_widget: QWidget | None = None
        self._metrics_layout: QGridLayout | None = None
        self._charts_layout: QGridLayout | None = None

        # 指标卡片
        self._metric_cards: dict[str, MetricCard] = {}

        # 图表组件
        self._chart_widgets: dict[str, ChartWidget] = {}

        # 数据加载器
        self._data_loader: QThread | None = None

        # 自动刷新定时器
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self.refresh_data)

        # 当前数据
        self._current_data: dict[str, Any] = {}

        # 设置组件
        self._setup_ui()
        self._setup_connections()

        # 初始数据加载
        self.refresh_data()

        # 启动自动刷新（每5分钟）
        self._refresh_timer.start(300000)

        self._logger.debug("仪表盘初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 设置主布局
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)

            # 创建标题
            self._create_title(main_layout)

            # 创建滚动区域
            self._create_scroll_area(main_layout)

            # 创建内容区域
            self._create_content_area()

            # 应用样式
            self._apply_styles()

        except Exception as e:
            self._logger.error(f"仪表盘UI设置失败: {e}")
            raise

    def _create_title(self, layout: QVBoxLayout) -> None:
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
        refresh_button.clicked.connect(self.refresh_data)

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
        self._metrics_layout = QGridLayout(metrics_frame)
        self._metrics_layout.setSpacing(15)

        # 创建指标卡片
        self._create_metric_cards()

        layout.addWidget(metrics_frame)

    def _create_metric_cards(self) -> None:
        """创建指标卡片"""
        # 定义指标卡片配置
        metrics_config = [
            {
                "name": "total_customers",
                "title": "客户总数",
                "icon": "👥",
                "color": "#007bff",
                "format": "number",
                "row": 0,
                "col": 0,
            },
            {
                "name": "new_customers_this_month",
                "title": "本月新增客户",
                "icon": "📈",
                "color": "#28a745",
                "format": "number",
                "suffix": "个",
                "row": 0,
                "col": 1,
            },
            {
                "name": "pending_tasks",
                "title": "待办任务",
                "icon": "📋",
                "color": "#ffc107",
                "format": "number",
                "suffix": "项",
                "row": 0,
                "col": 2,
            },
            {
                "name": "total_receivables",
                "title": "应收账款",
                "icon": "💰",
                "color": "#17a2b8",
                "format": "currency",
                "row": 0,
                "col": 3,
            },
            {
                "name": "total_payables",
                "title": "应付账款",
                "icon": "💳",
                "color": "#6f42c1",
                "format": "currency",
                "row": 1,
                "col": 0,
            },
            {
                "name": "active_contracts",
                "title": "活跃合同",
                "icon": "📄",
                "color": "#fd7e14",
                "format": "number",
                "suffix": "个",
                "row": 1,
                "col": 1,
            },
            {
                "name": "overdue_receivables",
                "title": "逾期应收",
                "icon": "⚠️",
                "color": "#dc3545",
                "format": "currency",
                "row": 1,
                "col": 2,
            },
            {
                "name": "customer_satisfaction",
                "title": "客户满意度",
                "icon": "⭐",
                "color": "#20c997",
                "format": "rating",
                "suffix": "/5.0",
                "row": 1,
                "col": 3,
            },
        ]

        # 创建卡片
        for config in metrics_config:
            card = MetricCard(
                title=str(config["title"]),
                icon=str(config["icon"]),
                color=str(config["color"]),
                value_format=str(config.get("format", "number")),
                suffix=str(config.get("suffix", "")),
            )

            # 连接点击信号
            card.clicked.connect(
                lambda name=str(config["name"]): self.metric_clicked.emit(name)
            )

            # 存储卡片
            self._metric_cards[str(config["name"])] = card

            # 添加到布局
            row = config["row"] if isinstance(config["row"], int) else 0
            col = config["col"] if isinstance(config["col"], int) else 0
            self._metrics_layout.addWidget(card, row, col)

    def _create_charts_section(self, layout: QVBoxLayout) -> None:
        """创建图表区域"""
        # 区域标题
        charts_title = QLabel("数据分析")
        charts_title.setObjectName("sectionTitle")

        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        charts_title.setFont(title_font)

        layout.addWidget(charts_title)

        # 图表网格
        charts_frame = QFrame()
        self._charts_layout = QGridLayout(charts_frame)
        self._charts_layout.setSpacing(20)

        # 创建图表
        self._create_chart_widgets()

        layout.addWidget(charts_frame)

    def _create_chart_widgets(self) -> None:
        """创建图表组件"""
        # 客户增长趋势图
        customer_growth_chart = ChartWidget(title="客户增长趋势", chart_type="line")
        self._chart_widgets["customer_growth"] = customer_growth_chart
        self._charts_layout.addWidget(customer_growth_chart, 0, 0)

        # 客户类型分布图
        customer_types_chart = ChartWidget(title="客户类型分布", chart_type="pie")
        self._chart_widgets["customer_types"] = customer_types_chart
        self._charts_layout.addWidget(customer_types_chart, 0, 1)

        # 月度互动频率图
        interactions_chart = ChartWidget(title="月度互动频率", chart_type="bar")
        self._chart_widgets["monthly_interactions"] = interactions_chart
        self._charts_layout.addWidget(interactions_chart, 1, 0)

        # 应收账款状态图
        receivables_chart = ChartWidget(title="应收账款状态", chart_type="stacked_bar")
        self._chart_widgets["receivables_status"] = receivables_chart
        self._charts_layout.addWidget(receivables_chart, 1, 1)

    def _setup_connections(self) -> None:
        """设置信号连接"""
        # 应用程序信号连接
        self._app.startup_completed.connect(self._on_app_ready)

    def _apply_styles(self) -> None:
        """应用样式"""
        self.setStyleSheet("""
            QLabel#dashboardTitle {
                color: #212529;
                margin-bottom: 10px;
            }

            QLabel#sectionTitle {
                color: #495057;
                margin: 20px 0 10px 0;
                padding-bottom: 5px;
                border-bottom: 2px solid #007bff;
            }

            QPushButton#refreshButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton#refreshButton:hover {
                background-color: #0056b3;
            }

            QPushButton#refreshButton:pressed {
                background-color: #004085;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def refresh_data(self) -> None:
        """刷新数据"""
        try:
            self._logger.debug("开始刷新仪表盘数据...")

            # 如果数据加载器正在运行，先停止它
            if self._data_loader and self._data_loader.isRunning():
                self._data_loader.quit()
                self._data_loader.wait()

            # 创建新的数据加载器
            # TODO: 实现具体的DataLoader类
            # self._data_loader = DataLoader(self._app)
            self._data_loader.data_loaded.connect(self._on_data_loaded)
            self._data_loader.error_occurred.connect(self._on_data_error)

            # 启动数据加载
            self._data_loader.start()

        except Exception as e:
            self._logger.error(f"数据刷新启动失败: {e}")

    def _on_data_loaded(self, data: dict[str, Any]) -> None:
        """处理数据加载完成"""
        try:
            self._current_data = data

            # 更新指标卡片
            self._update_metric_cards(data.get("metrics", {}))

            # 更新图表
            self._update_charts(data.get("charts", {}))

            # 发送刷新完成信号
            self.data_refreshed.emit()

            self._logger.debug("仪表盘数据更新完成")

        except Exception as e:
            self._logger.error(f"数据更新失败: {e}")

    def _on_data_error(self, error_message: str) -> None:
        """处理数据加载错误"""
        self._logger.error(f"数据加载错误: {error_message}")
        # TODO: 显示错误提示给用户

    def _update_metric_cards(self, metrics_data: dict[str, Any]) -> None:
        """更新指标卡片"""
        for metric_name, value in metrics_data.items():
            if metric_name in self._metric_cards:
                card = self._metric_cards[metric_name]
                card.set_value(value)

    def _update_charts(self, charts_data: dict[str, Any]) -> None:
        """更新图表"""
        for chart_name, chart_data in charts_data.items():
            if chart_name in self._chart_widgets:
                chart_widget = self._chart_widgets[chart_name]
                chart_widget.update_data(
                    labels=chart_data.get("labels", []), data=chart_data.get("data", [])
                )

    def _on_app_ready(self) -> None:
        """应用程序就绪处理"""
        self._logger.debug("应用程序就绪，刷新仪表盘数据")
        self.refresh_data()

    def get_current_data(self) -> dict[str, Any]:
        """获取当前数据"""
        return self._current_data.copy()

    def set_auto_refresh_interval(self, minutes: int) -> None:
        """
        设置自动刷新间隔

        Args:
            minutes: 刷新间隔（分钟）
        """
        if minutes > 0:
            self._refresh_timer.start(minutes * 60 * 1000)
        else:
            self._refresh_timer.stop()

    def export_data(self, file_path: str) -> bool:
        """
        导出仪表盘数据

        Args:
            file_path: 导出文件路径

        Returns:
            bool: 是否导出成功
        """
        try:
            # TODO: 实现数据导出功能
            self._logger.info(f"导出仪表盘数据到: {file_path}")
            return True

        except Exception as e:
            self._logger.error(f"数据导出失败: {e}")
            return False

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止定时器
            self._refresh_timer.stop()

            # 停止数据加载器
            if self._data_loader and self._data_loader.isRunning():
                self._data_loader.quit()
                self._data_loader.wait()

            self._logger.debug("仪表盘资源清理完成")

        except Exception as e:
            self._logger.error(f"仪表盘资源清理失败: {e}")

    def closeEvent(self, event) -> None:  # noqa: N802
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)
