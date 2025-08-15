"""
MiniCRM 基础对话框类

提供所有对话框组件的基础功能，包括：
- 标准对话框布局
- 按钮管理（确定、取消、应用等）
- 数据验证机制
- 模态/非模态支持
- 居中显示
- 键盘快捷键支持
"""

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from minicrm.core.exceptions import UIError


class DialogResult(Enum):
    """对话框结果枚举"""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    APPLIED = "applied"
    CANCELLED = "cancelled"


class BaseDialog(QDialog, ABC):
    """
    基础对话框类

    所有自定义对话框的基类，提供：
    - 标准对话框布局和按钮
    - 数据验证和提交机制
    - 键盘快捷键支持
    - 居中显示和大小管理
    - 模态/非模态支持
    - 统一的错误处理

    Signals:
        data_validated: 数据验证完成信号 (is_valid: bool)
        data_submitted: 数据提交信号 (data: Dict[str, Any])
        dialog_applied: 应用按钮点击信号
    """

    # Qt信号定义
    data_validated = Signal(bool)
    data_submitted = Signal(dict)
    dialog_applied = Signal()

    def __init__(
        self, title: str = "", modal: bool = True, parent: QWidget | None = None
    ):
        """
        初始化基础对话框

        Args:
            title: 对话框标题
            modal: 是否为模态对话框
            parent: 父组件
        """
        super().__init__(parent)

        # 对话框属性
        self._title = title
        self._modal = modal
        self._component_name = self.__class__.__name__

        # 日志记录器
        self._logger = logging.getLogger(f"{__name__}.{self._component_name}")

        # UI组件
        self._main_layout: QVBoxLayout | None = None
        self._content_layout: QVBoxLayout | None = None
        self._button_box: QDialogButtonBox | None = None

        # 数据管理
        self._form_data: dict[str, Any] = {}
        self._validation_errors: dict[str, str] = {}
        self._is_data_dirty = False

        # 快捷键
        self._shortcuts: list[QShortcut] = []

        try:
            # 执行初始化
            self._initialize_dialog()

        except Exception as e:
            self._handle_error(f"对话框初始化失败: {e}", e)

    def _initialize_dialog(self) -> None:
        """执行对话框初始化流程"""
        try:
            self._logger.debug(f"开始初始化对话框: {self._component_name}")

            # 1. 设置基础属性
            self._setup_base_properties()

            # 2. 创建布局
            self._create_layout()

            # 3. 设置用户界面
            self.setup_ui()

            # 4. 创建按钮
            self._create_buttons()

            # 5. 设置快捷键
            self._setup_shortcuts()

            # 6. 设置信号连接
            self.setup_connections()

            # 7. 应用样式
            self.apply_styles()

            # 8. 调整大小和位置
            self._adjust_size_and_position()

            self._logger.debug(f"对话框初始化完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"对话框初始化失败: {e}")
            raise UIError(f"对话框初始化失败: {e}", self._component_name) from e

    def _setup_base_properties(self) -> None:
        """设置基础属性"""
        # 设置标题
        if self._title:
            self.setWindowTitle(self._title)

        # 设置模态性
        self.setModal(self._modal)

        # 设置对象名称
        self.setObjectName(self._component_name)

        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint
        )

    def _create_layout(self) -> None:
        """创建布局结构"""
        # 主布局
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

        # 内容布局
        self._content_layout = QVBoxLayout()
        self._content_layout.setSpacing(15)
        self._main_layout.addLayout(self._content_layout)

    @abstractmethod
    def setup_ui(self) -> None:
        """
        设置用户界面

        子类必须实现此方法来创建对话框的具体内容。
        使用 self._content_layout 来添加内容组件。
        """
        pass

    def _create_buttons(self) -> None:
        """创建标准按钮"""
        # 创建按钮框
        self._button_box = QDialogButtonBox()

        # 添加标准按钮
        buttons = self.get_standard_buttons()
        self._button_box.setStandardButtons(buttons)

        # 连接信号
        self._button_box.accepted.connect(self._on_accepted)
        self._button_box.rejected.connect(self._on_rejected)

        # 如果有应用按钮，连接信号
        apply_button = self._button_box.button(QDialogButtonBox.StandardButton.Apply)
        if apply_button:
            apply_button.clicked.connect(self._on_applied)

        # 添加到主布局
        self._main_layout.addWidget(self._button_box)

    def get_standard_buttons(self) -> QDialogButtonBox.StandardButton:
        """
        获取标准按钮配置

        子类可以重写此方法来自定义按钮。
        默认返回确定和取消按钮。

        Returns:
            标准按钮配置
        """
        return (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

    def _setup_shortcuts(self) -> None:
        """设置快捷键"""
        # ESC键关闭对话框
        esc_shortcut = QShortcut(QKeySequence.StandardKey.Cancel, self)
        esc_shortcut.activated.connect(self.reject)
        self._shortcuts.append(esc_shortcut)

        # Enter键确认（如果有确定按钮）
        ok_button = self._button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            enter_shortcut = QShortcut(
                QKeySequence.StandardKey.InsertParagraphSeparator, self
            )
            enter_shortcut.activated.connect(self._try_accept)
            self._shortcuts.append(enter_shortcut)

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
            QDialog {
                background-color: #ffffff;
            }

            QDialogButtonBox {
                border-top: 1px solid #e9ecef;
                padding-top: 15px;
            }

            QPushButton {
                min-width: 80px;
                padding: 8px 16px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #f8f9fa;
            }

            QPushButton:hover {
                background-color: #e9ecef;
            }

            QPushButton:pressed {
                background-color: #dee2e6;
            }

            QPushButton:default {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }

            QPushButton:default:hover {
                background-color: #0056b3;
            }
        """)

    def _adjust_size_and_position(self) -> None:
        """调整大小和位置"""
        # 调整大小
        self.adjustSize()

        # 设置最小大小
        min_size = self.get_minimum_size()
        if min_size:
            self.setMinimumSize(min_size[0], min_size[1])

        # 居中显示
        self._center_on_parent()

    def get_minimum_size(self) -> tuple[int, int] | None:
        """
        获取最小大小

        子类可以重写此方法来设置最小大小。

        Returns:
            最小大小元组 (width, height) 或 None
        """
        return (400, 300)

    def _center_on_parent(self) -> None:
        """在父窗口中居中显示"""
        parent = self.parent()
        if parent and isinstance(parent, QWidget):
            parent_geometry = parent.geometry()
            dialog_geometry = self.geometry()

            x = (
                parent_geometry.x()
                + (parent_geometry.width() - dialog_geometry.width()) // 2
            )
            y = (
                parent_geometry.y()
                + (parent_geometry.height() - dialog_geometry.height()) // 2
            )

            self.move(x, y)

    def set_form_data(self, data: dict[str, Any]) -> None:
        """
        设置表单数据

        Args:
            data: 表单数据字典
        """
        self._form_data = data.copy()
        self._is_data_dirty = False
        self.load_data(data)

    def get_form_data(self) -> dict[str, Any]:
        """
        获取表单数据

        Returns:
            表单数据字典
        """
        return self._form_data.copy()

    @abstractmethod
    def load_data(self, data: dict[str, Any]) -> None:
        """
        加载数据到界面

        子类必须实现此方法来将数据加载到界面组件。

        Args:
            data: 要加载的数据
        """
        pass

    @abstractmethod
    def collect_data(self) -> dict[str, Any]:
        """
        从界面收集数据

        子类必须实现此方法来从界面组件收集数据。

        Returns:
            收集到的数据字典
        """
        pass

    def validate_data(self, data: dict[str, Any]) -> dict[str, str]:
        """
        验证数据

        子类可以重写此方法来实现自定义验证逻辑。

        Args:
            data: 要验证的数据

        Returns:
            验证错误字典，键为字段名，值为错误消息
        """
        return {}

    def _try_accept(self) -> None:
        """尝试接受对话框"""
        try:
            # 收集数据
            data = self.collect_data()

            # 验证数据
            errors = self.validate_data(data)

            if errors:
                # 显示验证错误
                self._show_validation_errors(errors)
                self.data_validated.emit(False)
                return

            # 验证通过，接受对话框
            self._form_data = data
            self.data_validated.emit(True)
            self.accept()

        except Exception as e:
            self._handle_error(f"数据处理失败: {e}", e)

    def _show_validation_errors(self, errors: dict[str, str]) -> None:
        """
        显示验证错误

        Args:
            errors: 错误字典
        """
        error_messages = []
        for field, message in errors.items():
            error_messages.append(f"• {field}: {message}")

        error_text = "数据验证失败：\n\n" + "\n".join(error_messages)
        QMessageBox.warning(self, "验证错误", error_text)

    def _on_accepted(self) -> None:
        """确定按钮点击处理"""
        self._try_accept()

    def _on_rejected(self) -> None:
        """取消按钮点击处理"""
        if self._is_data_dirty and not self._confirm_discard_changes():
            return

        self.reject()

    def _on_applied(self) -> None:
        """应用按钮点击处理"""
        try:
            # 收集和验证数据
            data = self.collect_data()
            errors = self.validate_data(data)

            if errors:
                self._show_validation_errors(errors)
                return

            # 应用数据
            self._form_data = data
            self._is_data_dirty = False
            self.data_submitted.emit(data)
            self.dialog_applied.emit()

        except Exception as e:
            self._handle_error(f"应用数据失败: {e}", e)

    def _confirm_discard_changes(self) -> bool:
        """确认丢弃更改"""
        reply = QMessageBox.question(
            self,
            "确认",
            "数据已修改，确定要丢弃更改吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return reply == QMessageBox.StandardButton.Yes

    def mark_data_dirty(self) -> None:
        """标记数据为已修改"""
        self._is_data_dirty = True

    def _handle_error(self, message: str, exception: Exception) -> None:
        """
        处理错误

        Args:
            message: 错误消息
            exception: 异常对象
        """
        self._logger.error(f"{message}: {exception}")
        QMessageBox.critical(self, "错误", message)

    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 清理快捷键
            for shortcut in self._shortcuts:
                shortcut.deleteLater()
            self._shortcuts.clear()

            self._logger.debug(f"对话框资源清理完成: {self._component_name}")

        except Exception as e:
            self._logger.error(f"资源清理失败: {e}")

    def closeEvent(self, event) -> None:  # noqa: N802
        """窗口关闭事件"""
        if self._is_data_dirty and not self._confirm_discard_changes():
            event.ignore()
            return

        self.cleanup()
        super().closeEvent(event)

    def __str__(self) -> str:
        """返回对话框的字符串表示"""
        return f"{self._component_name}(title='{self._title}', modal={self._modal})"
