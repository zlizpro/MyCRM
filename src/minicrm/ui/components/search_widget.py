"""
MiniCRM 搜索组件

实现通用的搜索组件，提供：
- 关键词搜索
- 高级筛选
- 搜索历史
- 搜索建议
- 实时搜索
"""

import logging
from datetime import datetime
from typing import Any

from PySide6.QtCore import QDate, QStringListModel, Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class SearchWidget(QWidget):
    """
    通用搜索组件

    提供完整的搜索功能，包括：
    - 关键词搜索
    - 高级筛选
    - 搜索历史
    - 搜索建议
    - 实时搜索

    Signals:
        search_requested: 搜索请求信号 (query: str, filters: Dict[str, Any])
        search_cleared: 搜索清除信号
        filter_changed: 筛选变化信号 (filters: Dict[str, Any])
    """

    # Qt信号定义
    search_requested = Signal(str, dict)
    search_cleared = Signal()
    filter_changed = Signal(dict)

    def __init__(
        self,
        placeholder: str = "输入关键词搜索...",
        show_advanced: bool = True,
        enable_history: bool = True,
        enable_suggestions: bool = True,
        search_delay: int = 300,
        parent: QWidget | None = None,
    ):
        """
        初始化搜索组件

        Args:
            placeholder: 搜索框占位符
            show_advanced: 是否显示高级搜索
            enable_history: 是否启用搜索历史
            enable_suggestions: 是否启用搜索建议
            search_delay: 搜索延迟（毫秒）
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 搜索配置
        self._placeholder = placeholder
        self._show_advanced = show_advanced
        self._enable_history = enable_history
        self._enable_suggestions = enable_suggestions
        self._search_delay = search_delay

        # 搜索数据
        self._search_history: list[str] = []
        self._suggestions: list[str] = []
        self._current_filters: dict[str, Any] = {}
        self._filter_configs: list[dict[str, Any]] = []

        # UI组件
        self._search_input: QLineEdit | None = None
        self._search_button: QPushButton | None = None
        self._clear_button: QPushButton | None = None
        self._advanced_button: QPushButton | None = None
        self._advanced_frame: QFrame | None = None
        self._filter_widgets: dict[str, QWidget] = {}

        # 搜索定时器（防抖）
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._perform_search)

        # 自动完成器
        self._completer: QCompleter | None = None

        # 设置组件
        self._setup_ui()
        self._setup_connections()

        self._logger.debug("搜索组件初始化完成")

    def _setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 主布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)

            # 创建搜索栏
            self._create_search_bar(layout)

            # 创建高级搜索区域
            if self._show_advanced:
                self._create_advanced_search(layout)

            # 应用样式
            self._apply_styles()

        except Exception as e:
            self._logger.error(f"搜索组件UI设置失败: {e}")
            raise

    def _create_search_bar(self, layout: QVBoxLayout) -> None:
        """创建搜索栏"""
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        # 搜索输入框
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(self._placeholder)
        self._search_input.setMinimumHeight(36)

        # 设置自动完成
        if self._enable_suggestions:
            self._setup_completer()

        search_layout.addWidget(self._search_input)

        # 搜索按钮
        self._search_button = QPushButton("🔍")
        self._search_button.setFixedSize(36, 36)
        self._search_button.setToolTip("搜索")
        search_layout.addWidget(self._search_button)

        # 清除按钮
        self._clear_button = QPushButton("✖️")
        self._clear_button.setFixedSize(36, 36)
        self._clear_button.setToolTip("清除搜索")
        search_layout.addWidget(self._clear_button)

        # 高级搜索按钮
        if self._show_advanced:
            self._advanced_button = QPushButton("⚙️")
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
        title_label = QLabel("高级搜索")
        title_label.setObjectName("advancedTitle")
        advanced_layout.addWidget(title_label)

        # 筛选器容器（动态添加）
        self._filter_container = QVBoxLayout()
        advanced_layout.addLayout(self._filter_container)

        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        apply_btn = QPushButton("应用筛选")
        apply_btn.clicked.connect(self._apply_filters)
        button_layout.addWidget(apply_btn)

        reset_btn = QPushButton("重置筛选")
        reset_btn.clicked.connect(self._reset_filters)
        button_layout.addWidget(reset_btn)

        advanced_layout.addLayout(button_layout)

        layout.addWidget(self._advanced_frame)

    def _setup_completer(self) -> None:
        """设置自动完成器"""
        try:
            self._completer = QCompleter()
            self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self._completer.setFilterMode(Qt.MatchFlag.MatchContains)

            # 设置模型
            model = QStringListModel()
            self._completer.setModel(model)

            # 关联到输入框
            self._search_input.setCompleter(self._completer)

        except Exception as e:
            self._logger.error(f"设置自动完成器失败: {e}")

    def _setup_connections(self) -> None:
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

    def _apply_styles(self) -> None:
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

            QComboBox, QDateEdit, QSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }

            QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #007bff;
            }
        """)

    def add_filter(self, filter_config: dict[str, Any]) -> None:
        """
        添加筛选器

        Args:
            filter_config: 筛选器配置
                {
                    'key': 'field_name',
                    'title': '显示标题',
                    'type': 'combo|date|number|text',
                    'options': [...],  # combo类型时使用
                    'default': 默认值
                }
        """
        try:
            self._filter_configs.append(filter_config)

            if self._advanced_frame:
                self._create_filter_widget(filter_config)

        except Exception as e:
            self._logger.error(f"添加筛选器失败: {e}")

    def _create_filter_widget(self, config: dict[str, Any]) -> None:
        """创建筛选器组件"""
        try:
            filter_key = config["key"]
            filter_type = config.get("type", "text")
            filter_title = config.get("title", filter_key)

            # 创建筛选器行
            filter_layout = QHBoxLayout()

            # 标签
            label = QLabel(f"{filter_title}:")
            label.setMinimumWidth(80)
            filter_layout.addWidget(label)

            # 筛选器组件
            filter_widget: QWidget | None = None

            if filter_type == "combo":
                filter_widget = QComboBox()
                filter_widget.addItem("全部", None)

                options = config.get("options", [])
                for option in options:
                    if isinstance(option, dict):
                        filter_widget.addItem(option["label"], option["value"])
                    else:
                        filter_widget.addItem(str(option), option)

            elif filter_type == "date":
                filter_widget = QDateEdit()
                filter_widget.setCalendarPopup(True)
                filter_widget.setSpecialValueText("选择日期")

            elif filter_type == "number":
                filter_widget = QSpinBox()
                filter_widget.setMinimum(config.get("min", 0))
                filter_widget.setMaximum(config.get("max", 999999))
                filter_widget.setSpecialValueText("不限")

            elif filter_type == "text":
                filter_widget = QLineEdit()
                filter_widget.setPlaceholderText(f"筛选{filter_title}...")

            elif filter_type == "checkbox":
                filter_widget = QCheckBox(config.get("text", ""))

            if filter_widget:
                # 设置默认值
                default_value = config.get("default")
                if default_value is not None:
                    self._set_filter_value(filter_widget, filter_type, default_value)

                # 连接信号
                self._connect_filter_widget(filter_widget, filter_type)

                # 存储组件
                self._filter_widgets[filter_key] = filter_widget

                filter_layout.addWidget(filter_widget)
                filter_layout.addStretch()

                # 添加到容器
                self._filter_container.addLayout(filter_layout)

        except Exception as e:
            self._logger.error(f"创建筛选器组件失败: {e}")

    def _set_filter_value(self, widget: QWidget, filter_type: str, value: Any) -> None:
        """设置筛选器值"""
        try:
            if filter_type == "combo" and isinstance(widget, QComboBox):
                index = widget.findData(value)
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif filter_type == "date" and isinstance(widget, QDateEdit):
                if isinstance(value, datetime):
                    date_val = value.date()
                    widget.setDate(QDate(date_val.year, date_val.month, date_val.day))
            elif filter_type == "number" and isinstance(widget, QSpinBox):
                widget.setValue(value)
            elif filter_type == "text" and isinstance(widget, QLineEdit):
                widget.setText(str(value))
            elif filter_type == "checkbox" and isinstance(widget, QCheckBox):
                widget.setChecked(bool(value))

        except Exception as e:
            self._logger.error(f"设置筛选器值失败: {e}")

    def _connect_filter_widget(self, widget: QWidget, filter_type: str) -> None:
        """连接筛选器组件信号"""
        try:
            if filter_type == "combo" and isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._on_filter_changed)
            elif filter_type == "date" and isinstance(widget, QDateEdit):
                widget.dateChanged.connect(self._on_filter_changed)
            elif filter_type == "number" and isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self._on_filter_changed)
            elif filter_type == "text" and isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_filter_changed)
            elif filter_type == "checkbox" and isinstance(widget, QCheckBox):
                widget.toggled.connect(self._on_filter_changed)

        except Exception as e:
            self._logger.error(f"连接筛选器信号失败: {e}")

    def set_suggestions(self, suggestions: list[str]) -> None:
        """
        设置搜索建议

        Args:
            suggestions: 建议列表
        """
        try:
            self._suggestions = suggestions

            if self._completer:
                model = self._completer.model()
                if isinstance(model, QStringListModel):
                    # 合并历史记录和建议
                    all_suggestions = list(set(self._search_history + suggestions))
                    model.setStringList(all_suggestions)

        except Exception as e:
            self._logger.error(f"设置搜索建议失败: {e}")

    def add_to_history(self, query: str) -> None:
        """
        添加到搜索历史

        Args:
            query: 搜索查询
        """
        try:
            if not self._enable_history or not query.strip():
                return

            # 移除重复项并添加到开头
            if query in self._search_history:
                self._search_history.remove(query)

            self._search_history.insert(0, query)

            # 限制历史记录数量
            if len(self._search_history) > 20:
                self._search_history = self._search_history[:20]

            # 更新自动完成
            if self._completer:
                model = self._completer.model()
                if isinstance(model, QStringListModel):
                    all_suggestions = list(
                        set(self._search_history + self._suggestions)
                    )
                    model.setStringList(all_suggestions)

        except Exception as e:
            self._logger.error(f"添加搜索历史失败: {e}")

    def get_current_query(self) -> str:
        """
        获取当前搜索查询

        Returns:
            str: 当前查询
        """
        return self._search_input.text() if self._search_input else ""

    def get_current_filters(self) -> dict[str, Any]:
        """
        获取当前筛选条件

        Returns:
            Dict[str, Any]: 当前筛选条件
        """
        return self._current_filters.copy()

    def set_query(self, query: str) -> None:
        """
        设置搜索查询

        Args:
            query: 搜索查询
        """
        if self._search_input:
            self._search_input.setText(query)

    def clear_search(self) -> None:
        """清除搜索"""
        try:
            if self._search_input:
                self._search_input.clear()

            self._current_filters.clear()
            self._reset_filters()

            # 发送清除信号
            self.search_cleared.emit()

            self._logger.debug("搜索已清除")

        except Exception as e:
            self._logger.error(f"清除搜索失败: {e}")

    def _on_text_changed(self) -> None:
        """处理文本变化（实时搜索）"""
        if self._search_delay > 0:
            self._search_timer.start(self._search_delay)
        else:
            self._perform_search()

    def _perform_search(self) -> None:
        """执行搜索"""
        try:
            query = self.get_current_query()
            filters = self.get_current_filters()

            # 添加到历史记录
            if query.strip():
                self.add_to_history(query)

            # 发送搜索信号
            self.search_requested.emit(query, filters)

            self._logger.debug(f"执行搜索: query='{query}', filters={filters}")

        except Exception as e:
            self._logger.error(f"执行搜索失败: {e}")

    def _on_filter_changed(self) -> None:
        """处理筛选变化"""
        try:
            self._update_current_filters()

            # 发送筛选变化信号
            self.filter_changed.emit(self._current_filters)

        except Exception as e:
            self._logger.error(f"处理筛选变化失败: {e}")

    def _update_current_filters(self) -> None:
        """更新当前筛选条件"""
        try:
            self._current_filters.clear()

            for config in self._filter_configs:
                filter_key = config["key"]
                filter_type = config.get("type", "text")

                if filter_key in self._filter_widgets:
                    widget = self._filter_widgets[filter_key]
                    value = self._get_filter_value(widget, filter_type)

                    if value is not None and value != "":
                        self._current_filters[filter_key] = value

        except Exception as e:
            self._logger.error(f"更新筛选条件失败: {e}")

    def _get_filter_value(self, widget: QWidget, filter_type: str) -> Any:
        """获取筛选器值"""
        try:
            if filter_type == "combo" and isinstance(widget, QComboBox):
                return widget.currentData()
            elif filter_type == "date" and isinstance(widget, QDateEdit):
                return widget.date().toPython()
            elif filter_type == "number" and isinstance(widget, QSpinBox):
                return widget.value() if widget.value() > widget.minimum() else None
            elif filter_type == "text" and isinstance(widget, QLineEdit):
                return widget.text().strip() or None
            elif filter_type == "checkbox" and isinstance(widget, QCheckBox):
                return widget.isChecked()

            return None

        except Exception as e:
            self._logger.error(f"获取筛选器值失败: {e}")
            return None

    def _apply_filters(self) -> None:
        """应用筛选"""
        try:
            self._update_current_filters()
            self._perform_search()

        except Exception as e:
            self._logger.error(f"应用筛选失败: {e}")

    def _reset_filters(self) -> None:
        """重置筛选"""
        try:
            for config in self._filter_configs:
                filter_key = config["key"]
                filter_type = config.get("type", "text")

                if filter_key in self._filter_widgets:
                    widget = self._filter_widgets[filter_key]

                    if filter_type == "combo" and isinstance(widget, QComboBox):
                        widget.setCurrentIndex(0)  # 选择"全部"
                    elif filter_type == "date" and isinstance(widget, QDateEdit):
                        widget.clear()
                    elif filter_type == "number" and isinstance(widget, QSpinBox):
                        widget.setValue(widget.minimum())
                    elif filter_type == "text" and isinstance(widget, QLineEdit):
                        widget.clear()
                    elif filter_type == "checkbox" and isinstance(widget, QCheckBox):
                        widget.setChecked(False)

            self._current_filters.clear()

        except Exception as e:
            self._logger.error(f"重置筛选失败: {e}")

    def _toggle_advanced(self, checked: bool) -> None:
        """切换高级搜索显示"""
        if self._advanced_frame:
            self._advanced_frame.setVisible(checked)

    def show_advanced(self) -> None:
        """显示高级搜索"""
        if self._advanced_button:
            self._advanced_button.setChecked(True)

    def hide_advanced(self) -> None:
        """隐藏高级搜索"""
        if self._advanced_button:
            self._advanced_button.setChecked(False)

    def __str__(self) -> str:
        """返回搜索组件的字符串表示"""
        return f"SearchWidget(filters={len(self._filter_configs)}, history={len(self._search_history)})"
