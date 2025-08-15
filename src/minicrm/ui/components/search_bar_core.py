"""
MiniCRM 搜索栏核心组件

重构后的精简版搜索栏，符合200行代码限制。
将复杂功能委托给专门的管理器类。
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
from minicrm.ui.components.search_styles import SearchBarStyles


class SearchBar(BaseWidget):
    """
    搜索栏核心组件

    提供基础搜索功能，复杂功能委托给管理器类：
    - SearchFilterManager: 筛选器管理
    - SearchHistoryManager: 历史记录和建议
    - SearchBarStyles: 样式管理

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
        super().__init__(parent)

        # 配置 - 重新定义类型以覆盖基类的dict类型
        self._config: SearchBarConfig = config or SearchBarConfig()  # type: ignore[assignment]

        # UI组件
        self._search_input: QLineEdit | None = None
        self._advanced_frame: QFrame | None = None

        # 搜索定时器（防抖）
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

        # 管理器
        self._filter_manager = SearchFilterManager(self)
        self._history_manager = SearchHistoryManager(self._config, self)

        # 调用父类初始化
        super().__init__(parent)

        # 设置管理器连接
        self._setup_managers()

        self._logger.debug("搜索栏组件初始化完成")

    def setup_ui(self) -> None:
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # 创建搜索栏
        self._create_search_bar(layout)

        # 创建高级搜索区域
        if self._config.show_advanced:
            self._create_advanced_search(layout)

    def _create_search_bar(self, layout: QVBoxLayout) -> None:
        """创建搜索栏"""
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # 搜索输入框
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._config.placeholder)
        self._search_input.setMinimumHeight(36)
        search_layout.addWidget(self._search_input)

        # 按钮组
        self._create_buttons(search_layout)

        layout.addWidget(search_frame)

    def _create_buttons(self, layout: QHBoxLayout) -> None:
        """创建按钮组"""
        # 搜索按钮
        search_btn = QPushButton(self._config.search_button_text)
        search_btn.setFixedSize(36, 36)
        search_btn.setToolTip("搜索")
        search_btn.clicked.connect(self._perform_search)
        layout.addWidget(search_btn)

        # 清除按钮
        clear_btn = QPushButton(self._config.clear_button_text)
        clear_btn.setFixedSize(36, 36)
        clear_btn.setToolTip("清除搜索")
        clear_btn.clicked.connect(self.clear_search)
        layout.addWidget(clear_btn)

        # 高级搜索按钮
        if self._config.show_advanced:
            advanced_btn = QPushButton(self._config.advanced_button_text)
            advanced_btn.setFixedSize(36, 36)
            advanced_btn.setToolTip("高级搜索")
            advanced_btn.setCheckable(True)
            advanced_btn.toggled.connect(self._toggle_advanced)
            layout.addWidget(advanced_btn)

    def _create_advanced_search(self, layout: QVBoxLayout) -> None:
        """创建高级搜索区域"""
        self._advanced_frame = QFrame()
        self._advanced_frame.setObjectName("advancedFrame")
        self._advanced_frame.hide()

        advanced_layout = QVBoxLayout(self._advanced_frame)
        advanced_layout.setContentsMargins(10, 10, 10, 10)
        advanced_layout.setSpacing(10)

        # 标题
        title_label = QLabel(self._config.advanced_title)
        title_label.setObjectName("advancedTitle")
        advanced_layout.addWidget(title_label)

        # 筛选器容器
        filter_container = QVBoxLayout()
        advanced_layout.addLayout(filter_container)
        self._filter_manager.set_container(filter_container)

        # 操作按钮
        self._create_advanced_buttons(advanced_layout)

        layout.addWidget(self._advanced_frame)

    def _create_advanced_buttons(self, layout: QVBoxLayout) -> None:
        """创建高级搜索按钮"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton(self._config.apply_button_text)
        apply_btn.clicked.connect(self._perform_search)
        button_layout.addWidget(apply_btn)

        reset_btn = QPushButton(self._config.reset_button_text)
        reset_btn.clicked.connect(self._reset_filters)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

    def _setup_managers(self) -> None:
        """设置管理器"""
        # 设置历史管理器的自动完成功能
        if self._search_input and self._config.enable_suggestions:
            self._history_manager.setup_completer(self._search_input)

        # 连接筛选器管理器信号
        self._filter_manager.filter_changed.connect(self.filter_changed.emit)

    def setup_connections(self) -> None:
        """设置信号连接"""
        if self._search_input:
            if self._config.enable_real_time:
                self._search_input.textChanged.connect(self._on_text_changed)
            self._search_input.returnPressed.connect(self._perform_search)

    def apply_styles(self) -> None:
        """应用样式"""
        stylesheet = SearchBarStyles.get_search_bar_stylesheet()
        self.setStyleSheet(stylesheet)

    # 公共API方法
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
        if self._search_input:
            self._search_input.clear()
        self._filter_manager.reset_filters()
        self.search_cleared.emit()

    def show_advanced(self) -> None:
        """显示高级搜索"""
        if self._advanced_frame:
            self._advanced_frame.show()

    def hide_advanced(self) -> None:
        """隐藏高级搜索"""
        if self._advanced_frame:
            self._advanced_frame.hide()

    # 内部事件处理方法
    def _on_text_changed(self) -> None:
        """处理文本变化（实时搜索）"""
        if self._config.search_delay > 0:
            self._search_timer.start(self._config.search_delay)
        else:
            self._perform_search()

    def _perform_search(self) -> None:
        """执行搜索"""
        query = self.get_current_query()
        filters = self.get_current_filters()

        # 添加到历史记录
        if query.strip():
            self._history_manager.add_to_history(query)

        # 发送搜索信号
        self.search_requested.emit(query, filters)

        self._logger.debug(f"执行搜索: query='{query}', filters={filters}")

    def _reset_filters(self) -> None:
        """重置筛选"""
        self._filter_manager.reset_filters()

    def _toggle_advanced(self, checked: bool) -> None:
        """切换高级搜索显示"""
        if self._advanced_frame:
            self._advanced_frame.setVisible(checked)

    def cleanup_resources(self) -> None:
        """清理资源"""
        if self._search_timer.isActive():
            self._search_timer.stop()
        self._history_manager.cleanup_resources()
        self._logger.debug("搜索栏资源清理完成")

    def __str__(self) -> str:
        """返回搜索栏的字符串表示"""
        return f"SearchBar(config={self._config})"
