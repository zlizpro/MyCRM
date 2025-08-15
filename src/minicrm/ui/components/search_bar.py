"""
MiniCRM 搜索栏简化版本

符合200行代码限制的精简搜索栏组件。
"""

from typing import Any

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from minicrm.ui.components.base_widget import BaseWidget
from minicrm.ui.components.search_config import FilterConfig, SearchBarConfig
from minicrm.ui.components.search_filter_manager import SearchFilterManager
from minicrm.ui.components.search_history_manager import SearchHistoryManager
from minicrm.ui.components.search_styles import SearchBarStyles


class SearchBar(BaseWidget):
    """
    简化版搜索栏组件

    核心功能：
    - 基础搜索输入
    - 搜索历史管理
    - 筛选器支持
    - 样式管理

    复杂功能委托给管理器类处理。
    """

    # 信号定义
    search_requested = Signal(str, dict)
    search_cleared = Signal()
    filter_changed = Signal(dict)

    def __init__(
        self,
        config: SearchBarConfig | None = None,
        parent: QWidget | None = None,
    ):
        """初始化搜索栏"""
        self._search_config: SearchBarConfig = config or SearchBarConfig()
        self._search_input: QLineEdit | None = None

        # 搜索定时器
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

        # 管理器
        self._filter_manager = SearchFilterManager(self)
        self._history_manager = SearchHistoryManager(self._search_config, self)

        super().__init__(parent)
        self._setup_managers()

    def setup_ui(self) -> None:
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 搜索栏
        search_layout = QHBoxLayout()

        # 输入框
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._search_config.placeholder)
        search_layout.addWidget(self._search_input)

        # 搜索按钮
        search_btn = QPushButton(self._search_config.search_button_text)
        search_btn.clicked.connect(self._perform_search)
        search_layout.addWidget(search_btn)

        # 清除按钮
        clear_btn = QPushButton(self._search_config.clear_button_text)
        clear_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_btn)

        layout.addLayout(search_layout)

        # 高级搜索区域（如果启用）
        if self._search_config.show_advanced:
            filter_layout = QVBoxLayout()
            self._filter_manager.set_container(filter_layout)
            layout.addLayout(filter_layout)

    def setup_connections(self) -> None:
        """设置信号连接"""
        if self._search_input and self._search_config.enable_real_time:
            self._search_input.textChanged.connect(self._on_text_changed)
        if self._search_input:
            self._search_input.returnPressed.connect(self._perform_search)

    def apply_styles(self) -> None:
        """应用样式"""
        stylesheet = SearchBarStyles.get_search_bar_stylesheet()
        self.setStyleSheet(stylesheet)

    def _setup_managers(self) -> None:
        """设置管理器"""
        if self._search_input and self._search_config.enable_suggestions:
            self._history_manager.setup_completer(self._search_input)
        self._filter_manager.filter_changed.connect(self.filter_changed.emit)

    # 公共API
    def add_filter(self, filter_config: FilterConfig) -> None:
        """添加筛选器"""
        self._filter_manager.add_filter(filter_config)

    def set_suggestions(self, suggestions: list[str]) -> None:
        """设置搜索建议"""
        self._history_manager.set_suggestions(suggestions)

    def get_current_query(self) -> str:
        """获取当前查询"""
        return self._search_input.text() if self._search_input else ""

    def get_current_filters(self) -> dict[str, Any]:
        """获取当前筛选条件"""
        return self._filter_manager.get_current_filters()

    def set_query(self, query: str) -> None:
        """设置查询"""
        if self._search_input:
            self._search_input.setText(query)

    def clear_search(self) -> None:
        """清除搜索"""
        if self._search_input:
            self._search_input.clear()
        self._filter_manager.reset_filters()
        self.search_cleared.emit()

    # 事件处理
    def _on_text_changed(self) -> None:
        """文本变化处理"""
        if self._search_config.search_delay > 0:
            self._search_timer.start(self._search_config.search_delay)
        else:
            self._perform_search()

    def _perform_search(self) -> None:
        """执行搜索"""
        query = self.get_current_query()
        filters = self.get_current_filters()

        if query.strip():
            self._history_manager.add_to_history(query)

        self.search_requested.emit(query, filters)

    def cleanup_resources(self) -> None:
        """清理资源"""
        if self._search_timer.isActive():
            self._search_timer.stop()
        self._history_manager.cleanup_resources()

    def __str__(self) -> str:
        return f"SearchBar(config={self._search_config})"
