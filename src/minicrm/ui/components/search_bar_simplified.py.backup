"""
MiniCRM 搜索栏组件 - 简化版本

实现通用的搜索栏组件，使用模块化设计：
- 关键词搜索
- 高级筛选（委托给SearchFilterManager）
- 搜索历史（委托给SearchHistoryManager）
- 搜索建议
- 实时搜索

这是重构后的简化版本，符合200行代码限制。
"""

from typing import Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from minicrm.ui.components.base_widget import BaseWidget
from minicrm.ui.components.search_config import FilterConfig, SearchBarConfig
from minicrm.ui.components.search_filter_manager import SearchFilterManager
from minicrm.ui.components.search_history_manager import SearchHistoryManager


class SearchBar(BaseWidget):
    """
    通用搜索栏组件

    提供完整的搜索功能，使用模块化设计：
    - 关键词搜索
    - 高级筛选（委托给管理器）
    - 搜索历史（委托给管理器）
    - 搜索建议
    - 实时搜索

    Signals:
        search_requested: 搜索请求信号 (query: str, filters: dict[str, Any])
        search_cleared: 搜索清除信号
        filter_changed: 筛选变化信号 (filters: dict[str, Any])
    """

    # Qt信号定义
    search_requested = Signal(str, dict)
    search_cleared = Signal()
    filter_changed = Signal(dict)

    def __init__(
        self,
        config: SearchBarConfig | None = None,
        parent: QWidget | None = None,
    ):
        """
        初始化搜索栏组件

        Args:
            config: 搜索栏配置，如果为None则使用默认配置
            parent: 父组件
        """
        # 搜索配置
        self._search_config: SearchBarConfig = config or SearchBarConfig()

        # UI组件
        self._search_input: QLineEdit | None = None
        self._search_button: QPushButton | None = None
        self._clear_button: QPushButton | None = None
        self._advanced_button: QPushButton | None = None
        self._advanced_frame: QFrame | None = None

        # 搜索定时器（防抖）
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

        # 管理器
        self._filter_manager = SearchFilterManager(self)
        self._history_manager = SearchHistoryManager(self._search_config, self)

        # 调用父类初始化
        super().__init__(parent)

        # 设置管理器连接
        self._setup_managers()

        self._logger.debug("搜索栏组件初始化完成")

    def setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 主布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            # 创建搜索栏
            self._create_search_bar(layout)

            # 创建高级搜索区域
            if self._search_config.show_advanced:
                self._create_advanced_search(layout)

        except Exception as e:
            self._logger.error(f"搜索栏UI设置失败: {e}")
            raise

    def _create_search_bar(self, layout: QVBoxLayout) -> None:
        """创建搜索栏"""
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # 搜索输入框
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._search_config.placeholder)
        self._search_input.setMinimumHeight(36)
        search_layout.addWidget(self._search_input)

        # 搜索按钮
        self._search_button = QPushButton(self._search_config.search_button_text)
        self._search_button.setFixedSize(36, 36)
        self._search_button.setToolTip("搜索")
        search_layout.addWidget(self._search_button)

        # 清除按钮
        self._clear_button = QPushButton(self._search_config.clear_button_text)
        self._clear_button.setFixedSize(36, 36)
        self._clear_button.setToolTip("清除搜索")
        search_layout.addWidget(self._clear_button)

        # 高级搜索按钮
        if self._search_config.show_advanced:
            self._advanced_button = QPushButton(
                self._search_config.advanced_button_text
            )
            self._advanced_button.setFixedSize(36, 36)
            self._advanced_button.setToolTip("高级搜索")
            self._advanced_button.setCheckable(True)
            search_layout.addWidget(self._advanced_button)

        layout.addWidget(search_frame)

    def _create_advanced_search(self, layout: QVBoxLayout) -> None:
        """创建高级搜索区域"""
        self._advanced_frame = QFrame()
        self._advanced_frame.setObjectName("advancedFrame")
        self._advanced_frame.hide()  # 默认隐藏

        advanced_layout = QVBoxLayout(self._advanced_frame)
        advanced_layout.setContentsMargins(10, 10, 10, 10)
        advanced_layout.setSpacing(10)

        # 标题
        title_label = QLabel(self._search_config.advanced_title)
        title_label.setObjectName("advancedTitle")
        advanced_layout.addWidget(title_label)

        # 设置筛选器管理器容器
        self._filter_manager.set_container(advanced_layout)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton(self._search_config.apply_button_text)
        apply_btn.clicked.connect(self._apply_filters)
        button_layout.addWidget(apply_btn)

        reset_btn = QPushButton(self._search_config.reset_button_text)
        reset_btn.clicked.connect(self._reset_filters)
        button_layout.addWidget(reset_btn)

        advanced_layout.addLayout(button_layout)
        layout.addWidget(self._advanced_frame)

    def _setup_managers(self) -> None:
        """设置管理器连接"""
        # 设置历史管理器
        if self._search_input and self._search_config.enable_suggestions:
            self._history_manager.setup_completer(self._search_input)

        # 连接筛选管理器信号
        self._filter_manager.filter_changed.connect(self.filter_changed.emit)

    def setup_connections(self) -> None:
        """设置信号连接"""
        if self._search_input:
            self._search_input.textChanged.connect(self._on_text_changed)
            self._search_input.returnPressed.connect(self._perform_search)

        if self._search_button:
            self._search_button.clicked.connect(self._perform_search)

        if self._clear_button:
            self._clear_button.clicked.connect(self.clear_search)

        if self._advanced_button:
            self._advanced_button.toggled.connect(self._toggle_advanced)

    def apply_styles(self) -> None:
        """应用样式"""
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }

            QLineEdit:focus {
                border-color: #007bff;
                outline: none;
            }

            QPushButton {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #e9ecef;
            }

            QPushButton:pressed {
                background-color: #dee2e6;
            }

            QPushButton:checked {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }

            QFrame#advancedFrame {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
            }

            QLabel#advancedTitle {
                font-weight: bold;
                font-size: 14px;
                color: #495057;
            }
        """)

    # 公共接口方法
    def add_filter(self, filter_config: FilterConfig) -> None:
        """添加筛选器"""
        self._filter_manager.add_filter(filter_config)

    def set_suggestions(self, suggestions: list[str]) -> None:
        """设置搜索建议"""
        self._history_manager.set_suggestions(suggestions)

    def get_current_query(self) -> str:
        """获取当前搜索查询"""
        return self._search_input.text() if self._search_input else ""

    def get_current_filters(self) -> dict[str, Any]:
        """获取当前筛选条件"""
        return self._filter_manager.get_current_filters()

    def set_query(self, query: str) -> None:
        """设置搜索查询"""
        if self._search_input:
            self._search_input.setText(query)

    def clear_search(self) -> None:
        """清除搜索"""
        try:
            if self._search_input:
                self._search_input.clear()

            self._filter_manager.reset_filters()
            self.search_cleared.emit()

            self._logger.debug("搜索已清除")

        except Exception as e:
            self._logger.error(f"清除搜索失败: {e}")

    # 私有方法
    def _on_text_changed(self) -> None:
        """处理文本变化（实时搜索）"""
        if self._search_config.search_delay > 0:
            self._search_timer.start(self._search_config.search_delay)
        else:
            self._perform_search()

    def _perform_search(self) -> None:
        """执行搜索"""
        try:
            query = self.get_current_query()
            filters = self.get_current_filters()

            # 添加到历史记录
            if query.strip():
                self._history_manager.add_to_history(query)

            # 发送搜索信号
            self.search_requested.emit(query, filters)

            self._logger.debug(f"执行搜索: query='{query}', filters={filters}")

        except Exception as e:
            self._logger.error(f"执行搜索失败: {e}")

    def _apply_filters(self) -> None:
        """应用筛选"""
        self._perform_search()

    def _reset_filters(self) -> None:
        """重置筛选"""
        self._filter_manager.reset_filters()

    def _toggle_advanced(self, checked: bool) -> None:
        """切换高级搜索显示"""
        if self._advanced_frame:
            self._advanced_frame.setVisible(checked)

    def cleanup_resources(self) -> None:
        """清理资源"""
        try:
            # 停止搜索定时器
            if self._search_timer.isActive():
                self._search_timer.stop()

            # 清理管理器
            if hasattr(self._filter_manager, "cleanup_resources"):
                self._filter_manager.cleanup_resources()
            self._history_manager.cleanup_resources()

            self._logger.debug("搜索栏资源清理完成")

        except Exception as e:
            self._logger.error(f"搜索栏资源清理失败: {e}")

    def __str__(self) -> str:
        """返回搜索栏的字符串表示"""
        return f"SearchBar(config={self._config})"
