"""
MiniCRM 基础面板类

提供所有面板组件的基础功能，包括：
- 标准面板布局
- 标题栏和工具栏支持
- 可折叠/展开功能
- 内容区域管理
- 滚动支持
- 响应式布局
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum

from PySide6.QtCore import QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from minicrm.core.exceptions import UIError


class PanelState(Enum):
    """面板状态枚举"""

    EXPANDED = "expanded"
    COLLAPSED = "collapsed"
    HIDDEN = "hidden"


class BasePanel(QFrame, ABC):
    """
    基础面板类

    所有面板组件的基类，提供：
    - 标准面板布局（标题栏、工具栏、内容区域）
    - 可折叠/展开功能
    - 滚动支持
    - 工具按钮管理
    - 响应式布局
    - 状态管理

    Signals:
        state_changed: 面板状态改变信号 (state: PanelState)
        title_clicked: 标题点击信号
        tool_button_clicked: 工具按钮点击信号 (button_name: str)
        content_updated: 内容更新信号
    """

    # Qt信号定义
    state_changed = Signal(PanelState)
    title_clicked = Signal()
    tool_button_clicked = Signal(str)
    content_updated = Signal()

    def __init__(
        self,
        title: str = "",
        collapsible: bool = True,
        scrollable: bool = False,
        parent: QWidget | None = None,
    ):
        """
        初始化基础面板

        Args:
            title: 面板标题
            collapsible: 是否可折叠
            scrollable: 是否支持滚动
            parent: 父组件
        """
        super().__init__(parent)

        # 面板属性
        self._title = title
        self._collapsible = collapsible
        self._scrollable = scrollable
        self._component_name = self.__class__.__name__

        # 日志记录器
        self._logger = logging.getLogger(f"{__name__}.{self._component_name}")

        # 面板状态
        self._current_state = PanelState.EXPANDED
        self._previous_state = PanelState.EXPANDED

        # UI组件
        self._main_layout: QVBoxLayout | None = None
        self._header_frame: QFrame | None = None
        self._header_layout: QHBoxLayout | None = None
        self._title_label: QLabel | None = None
        self._collapse_button: QToolButton | None = None
        self._tool_buttons: dict[str, QPushButton] = {}

        self._content_frame: QFrame | None = None
        self._content_layout: QVBoxLayout | None = None
        self._scroll_area: QScrollArea | None = None

        # 动画
        self._collapse_animation: QPropertyAnimation | None = None

        try:
            # 执行初始化
            self._initialize_panel()

        except Exception as e:
            self._handle_error(f"面板初始化失败: {e}", e)

    def _initialize_panel(self) -> None:
        """执行面板初始化流程"""
        try:
            self._logger.debug(f"开始初始化面板: {self._component_name}")

            # 1. 设置基础属性
            self._setup_base_properties()

            # 2. 创建布局结构
            self._create_layout_structure()

            # 3. 创建标题栏
            self._create_header()

            # 4. 创建内容区域
            self._create_content_area()

            # 5. 设置用户界面
            self.setup_ui()

            # 6. 设置动画
            self._setup_animations()

            # 7. 设置信号连接
            self.setup_connections()

            # 8. 应用样式
            self.apply_styles()

            self._logger.debug(f"面板初始化完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"面板初始化失败: {e}")
            raise UIError(f"面板初始化失败: {e}", self._component_name) from e

    def _setup_base_properties(self) -> None:
        """设置基础属性"""
        # 设置对象名称
        self.setObjectName(self._component_name)

        # 设置框架样式
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    def _create_layout_structure(self) -> None:
        """创建布局结构"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

    def _create_header(self) -> None:
        """创建标题栏"""
        if not self._title and not self._collapsible:
            return

        # 标题栏框架
        self._header_frame = QFrame()
        self._header_frame.setObjectName("headerFrame")
        self._header_frame.setFixedHeight(40)

        # 标题栏布局
        self._header_layout = QHBoxLayout(self._header_frame)
        self._header_layout.setContentsMargins(10, 5, 10, 5)
        self._header_layout.setSpacing(10)

        # 折叠按钮
        if self._collapsible:
            self._collapse_button = QToolButton()
            self._collapse_button.setObjectName("collapseButton")
            self._collapse_button.setText("▼")
            self._collapse_button.setFixedSize(20, 20)
            self._collapse_button.clicked.connect(self._toggle_collapse)
            self._header_layout.addWidget(self._collapse_button)

        # 标题标签
        if self._title:
            self._title_label = QLabel(self._title)
            self._title_label.setObjectName("titleLabel")

            title_font = QFont()
            title_font.setBold(True)
            title_font.setPointSize(10)
            self._title_label.setFont(title_font)

            # TODO: 实现可点击的标题标签
            # 需要创建自定义的可点击标签类来避免类型错误
            self._header_layout.addWidget(self._title_label)

        # 弹性空间
        self._header_layout.addStretch()

        # 添加到主布局
        self._main_layout.addWidget(self._header_frame)

    def _create_content_area(self) -> None:
        """创建内容区域"""
        if self._scrollable:
            # 创建滚动区域
            self._scroll_area = QScrollArea()
            self._scroll_area.setWidgetResizable(True)
            self._scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self._scroll_area.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )

            # 内容框架
            self._content_frame = QFrame()
            self._content_frame.setObjectName("contentFrame")

            # 内容布局
            self._content_layout = QVBoxLayout(self._content_frame)
            self._content_layout.setContentsMargins(10, 10, 10, 10)
            self._content_layout.setSpacing(10)

            # 设置滚动区域的内容
            self._scroll_area.setWidget(self._content_frame)
            self._main_layout.addWidget(self._scroll_area)

        else:
            # 直接创建内容框架
            self._content_frame = QFrame()
            self._content_frame.setObjectName("contentFrame")

            # 内容布局
            self._content_layout = QVBoxLayout(self._content_frame)
            self._content_layout.setContentsMargins(10, 10, 10, 10)
            self._content_layout.setSpacing(10)

            self._main_layout.addWidget(self._content_frame)

    @abstractmethod
    def setup_ui(self) -> None:
        """
        设置用户界面

        子类必须实现此方法来创建面板的具体内容。
        使用 self._content_layout 来添加内容组件。
        """
        pass

    def _setup_animations(self) -> None:
        """设置动画效果"""
        if not self._collapsible:
            return

        try:
            # 折叠/展开动画
            self._collapse_animation = QPropertyAnimation(
                self._content_frame, b"maximumHeight"
            )
            self._collapse_animation.setDuration(300)

        except Exception as e:
            self._logger.error(f"动画设置失败: {e}")

    def setup_connections(self) -> None:
        """
        设置信号连接

        子类可以重写此方法来设置额外的信号连接。
        """
        pass

    def apply_styles(self) -> None:
        """
        应用样式

        子类可以重写此方法来应用自定义样式。
        """
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 4px;
            }

            QFrame#headerFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
                border-radius: 4px 4px 0 0;
            }

            QFrame#contentFrame {
                border: none;
                border-radius: 0 0 4px 4px;
            }

            QLabel#titleLabel {
                color: #495057;
                font-weight: bold;
            }

            QToolButton#collapseButton {
                border: none;
                background-color: transparent;
                color: #6c757d;
                font-weight: bold;
            }

            QToolButton#collapseButton:hover {
                background-color: #e9ecef;
                border-radius: 2px;
            }

            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def add_tool_button(self, name: str, text: str, tooltip: str = "") -> QPushButton:
        """
        添加工具按钮到标题栏

        Args:
            name: 按钮名称（用于信号识别）
            text: 按钮文本
            tooltip: 工具提示

        Returns:
            创建的按钮对象
        """
        if not self._header_layout:
            raise UIError("标题栏未创建，无法添加工具按钮", self._component_name)

        button = QPushButton(text)
        button.setObjectName(f"toolButton_{name}")
        button.setFixedHeight(25)

        if tooltip:
            button.setToolTip(tooltip)

        # 连接信号
        button.clicked.connect(lambda: self.tool_button_clicked.emit(name))

        # 添加到布局（在弹性空间之前）
        self._header_layout.insertWidget(self._header_layout.count() - 1, button)

        # 存储按钮引用
        self._tool_buttons[name] = button

        return button

    def remove_tool_button(self, name: str) -> None:
        """
        移除工具按钮

        Args:
            name: 按钮名称
        """
        if name in self._tool_buttons:
            button = self._tool_buttons[name]
            self._header_layout.removeWidget(button)
            button.deleteLater()
            del self._tool_buttons[name]

    def get_tool_button(self, name: str) -> QPushButton | None:
        """
        获取工具按钮

        Args:
            name: 按钮名称

        Returns:
            按钮对象或None
        """
        return self._tool_buttons.get(name)

    def set_title(self, title: str) -> None:
        """
        设置面板标题

        Args:
            title: 新标题
        """
        self._title = title
        if self._title_label:
            self._title_label.setText(title)

    def get_title(self) -> str:
        """获取面板标题"""
        return self._title

    def set_state(self, state: PanelState) -> None:
        """
        设置面板状态

        Args:
            state: 新状态
        """
        if state == self._current_state:
            return

        self._previous_state = self._current_state
        self._current_state = state

        if state == PanelState.COLLAPSED:
            self._collapse_panel()
        elif state == PanelState.EXPANDED:
            self._expand_panel()
        elif state == PanelState.HIDDEN:
            self.hide()

        self.state_changed.emit(state)

    def get_state(self) -> PanelState:
        """获取当前面板状态"""
        return self._current_state

    def _toggle_collapse(self) -> None:
        """切换折叠状态"""
        if self._current_state == PanelState.COLLAPSED:
            self.set_state(PanelState.EXPANDED)
        else:
            self.set_state(PanelState.COLLAPSED)

    def _collapse_panel(self) -> None:
        """折叠面板"""
        if not self._collapsible or not self._content_frame:
            return

        try:
            if self._collapse_animation:
                self._collapse_animation.setStartValue(self._content_frame.height())
                self._collapse_animation.setEndValue(0)
                self._collapse_animation.start()
            else:
                self._content_frame.hide()

            # 更新折叠按钮
            if self._collapse_button:
                self._collapse_button.setText("▶")

        except Exception as e:
            self._logger.error(f"面板折叠失败: {e}")

    def _expand_panel(self) -> None:
        """展开面板"""
        if not self._collapsible or not self._content_frame:
            return

        try:
            if self._collapse_animation:
                self._collapse_animation.setStartValue(0)
                self._collapse_animation.setEndValue(
                    self._content_frame.sizeHint().height()
                )
                self._collapse_animation.start()
            else:
                self._content_frame.show()

            # 更新折叠按钮
            if self._collapse_button:
                self._collapse_button.setText("▼")

        except Exception as e:
            self._logger.error(f"面板展开失败: {e}")

    def add_content_widget(self, widget: QWidget) -> None:
        """
        添加内容组件

        Args:
            widget: 要添加的组件
        """
        if self._content_layout:
            self._content_layout.addWidget(widget)
            self.content_updated.emit()

    def remove_content_widget(self, widget: QWidget) -> None:
        """
        移除内容组件

        Args:
            widget: 要移除的组件
        """
        if self._content_layout:
            self._content_layout.removeWidget(widget)
            widget.deleteLater()
            self.content_updated.emit()

    def clear_content(self) -> None:
        """清空内容区域"""
        if self._content_layout:
            while self._content_layout.count():
                child = self._content_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.content_updated.emit()

    def _handle_error(self, message: str, exception: Exception) -> None:
        """
        处理错误

        Args:
            message: 错误消息
            exception: 异常对象
        """
        self._logger.error(f"{message}: {exception}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止动画
            if (
                self._collapse_animation
                and self._collapse_animation.state() != QPropertyAnimation.State.Stopped
            ):
                self._collapse_animation.stop()

            # 清理工具按钮
            for button in self._tool_buttons.values():
                button.deleteLater()
            self._tool_buttons.clear()

            self._logger.debug(f"面板资源清理完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"资源清理失败: {e}")

    def closeEvent(self, event) -> None:  # noqa: N802
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)

    def __str__(self) -> str:
        """返回面板的字符串表示"""
        return f"{self._component_name}(title='{self._title}', " \
               f"state={self._current_state.value})"
