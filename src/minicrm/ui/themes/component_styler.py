"""
MiniCRM 组件样式应用器

提供统一的组件样式应用机制，确保所有组件都能正确应用主题样式。
"""

import logging
from enum import Enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QTreeWidget,
    QWidget,
)

from .styles import (
    ComponentSize,
    ComponentStyleGenerator,
    ComponentVariant,
    StyleTokens,
)


class StyleClass(Enum):
    """样式类枚举"""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    OUTLINE = "outline"
    GHOST = "ghost"
    LINK = "link"


class ComponentStyler:
    """
    组件样式应用器

    提供统一的组件样式应用接口，支持：
    - 按钮样式应用
    - 输入框样式应用
    - 容器样式应用
    - 表格样式应用
    - 自定义样式应用
    """

    def __init__(
        self, style_tokens: StyleTokens, style_generator: ComponentStyleGenerator
    ):
        """
        初始化组件样式应用器

        Args:
            style_tokens: 样式令牌管理器
            style_generator: 组件样式生成器
        """
        self._logger = logging.getLogger(__name__)
        self.tokens = style_tokens
        self.generator = style_generator

    def apply_button_style(
        self,
        button: QPushButton,
        variant: ComponentVariant = ComponentVariant.PRIMARY,
        size: ComponentSize = ComponentSize.MEDIUM,
        style_class: StyleClass | None = None,
    ) -> None:
        """
        应用按钮样式

        Args:
            button: 按钮组件
            variant: 按钮变体
            size: 按钮尺寸
            style_class: 样式类
        """
        try:
            # 生成基础样式
            base_style = self.generator.generate_button_style(variant, size)

            # 应用样式类
            if style_class:
                button.setProperty("class", style_class.value)

            # 设置样式
            button.setStyleSheet(base_style)

            # 设置可访问性属性
            button.setAccessibleName(f"{variant.value} button")

            self._logger.debug(f"按钮样式已应用: {variant.value}, {size.value}")

        except Exception as e:
            self._logger.error(f"应用按钮样式失败: {e}")

    def apply_input_style(
        self,
        input_widget: QLineEdit | QTextEdit | QPlainTextEdit | QComboBox,
        size: ComponentSize = ComponentSize.MEDIUM,
        state: str | None = None,
    ) -> None:
        """
        应用输入框样式

        Args:
            input_widget: 输入框组件
            size: 输入框尺寸
            state: 状态（error, success, warning等）
        """
        try:
            # 生成基础样式
            base_style = self.generator.generate_input_style(size)

            # 应用状态样式
            if state:
                input_widget.setProperty("state", state)
                base_style += f"\n/* State: {state} */"

            # 设置样式
            input_widget.setStyleSheet(base_style)

            # 设置可访问性属性
            input_widget.setAccessibleName("input field")

            self._logger.debug(f"输入框样式已应用: {size.value}")

        except Exception as e:
            self._logger.error(f"应用输入框样式失败: {e}")

    def apply_card_style(
        self, widget: QWidget, elevated: bool = False, interactive: bool = False
    ) -> None:
        """
        应用卡片样式

        Args:
            widget: 组件
            elevated: 是否有阴影
            interactive: 是否可交互
        """
        try:
            # 生成基础样式
            base_style = self.generator.generate_card_style()

            # 添加阴影效果
            if elevated:
                shadow = self.tokens.get_shadow("medium")
                base_style += f"\nbox-shadow: {shadow};"

            # 添加交互效果
            if interactive:
                hover_color = self.tokens.get_semantic_color("hover")
                base_style += f"""
                QWidget:hover {{
                    background-color: {hover_color};
                }}
                """

            # 设置样式
            widget.setStyleSheet(base_style)

            self._logger.debug("卡片样式已应用")

        except Exception as e:
            self._logger.error(f"应用卡片样式失败: {e}")

    def apply_table_style(
        self,
        table: QTableWidget | QTreeWidget | QListWidget,
        striped: bool = True,
        hoverable: bool = True,
    ) -> None:
        """
        应用表格样式

        Args:
            table: 表格组件
            striped: 是否显示斑马纹
            hoverable: 是否支持悬停效果
        """
        try:
            # 生成基础样式
            base_style = self.generator.generate_table_style()

            # 添加斑马纹效果
            if striped:
                alternate_color = self.tokens.get_semantic_color("surface")
                base_style += f"""
                QTableWidget::item:alternate {{
                    background-color: {alternate_color};
                }}
                """
                table.setAlternatingRowColors(True)

            # 添加悬停效果
            if hoverable:
                hover_color = self.tokens.get_semantic_color("hover")
                base_style += f"""
                QTableWidget::item:hover {{
                    background-color: {hover_color};
                }}
                """

            # 设置样式
            table.setStyleSheet(base_style)

            # 设置表格属性
            table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
            table.setSelectionMode(table.SelectionMode.SingleSelection)

            self._logger.debug("表格样式已应用")

        except Exception as e:
            self._logger.error(f"应用表格样式失败: {e}")

    def apply_dialog_style(
        self, dialog: QDialog | QMessageBox, modal: bool = True
    ) -> None:
        """
        应用对话框样式

        Args:
            dialog: 对话框组件
            modal: 是否为模态对话框
        """
        try:
            # 生成基础样式
            base_style = self.generator.generate_dialog_style()

            # 设置样式
            dialog.setStyleSheet(base_style)

            # 设置对话框属性
            if modal:
                dialog.setModal(True)

            # 设置窗口标志
            dialog.setWindowFlags(
                Qt.WindowType.Dialog
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowCloseButtonHint
            )

            self._logger.debug("对话框样式已应用")

        except Exception as e:
            self._logger.error(f"应用对话框样式失败: {e}")

    def apply_container_style(
        self,
        container: QWidget,
        padding: str | None = None,
        margin: str | None = None,
        border: bool = False,
    ) -> None:
        """
        应用容器样式

        Args:
            container: 容器组件
            padding: 内边距
            margin: 外边距
            border: 是否显示边框
        """
        try:
            styles = []

            # 背景色
            bg_color = self.tokens.get_semantic_color("background")
            styles.append(f"background-color: {bg_color};")

            # 内边距
            if padding:
                styles.append(f"padding: {padding};")
            else:
                default_padding = self.tokens.get_spacing("md")
                styles.append(f"padding: {default_padding};")

            # 外边距
            if margin:
                styles.append(f"margin: {margin};")

            # 边框
            if border:
                border_color = self.tokens.get_semantic_color("border")
                border_radius = self.tokens.get_border_radius("medium")
                styles.append(f"border: 1px solid {border_color};")
                styles.append(f"border-radius: {border_radius};")

            # 设置样式
            container.setStyleSheet(" ".join(styles))

            self._logger.debug("容器样式已应用")

        except Exception as e:
            self._logger.error(f"应用容器样式失败: {e}")

    def apply_text_style(
        self,
        label: QLabel,
        variant: str = "body",
        color: str | None = None,
        weight: str | None = None,
    ) -> None:
        """
        应用文本样式

        Args:
            label: 文本标签
            variant: 文本变体（heading, title, body, caption等）
            color: 文本颜色
            weight: 字体粗细
        """
        try:
            styles = []

            # 字体族
            font_family = self.tokens.get_font_family()
            styles.append(f"font-family: {font_family};")

            # 字体大小和粗细（根据变体）
            variant_styles = {
                "title": (
                    self.tokens.get_font_size("heading"),
                    self.tokens.get_font_weight("bold"),
                ),
                "heading": (
                    self.tokens.get_font_size("large"),
                    self.tokens.get_font_weight("medium"),
                ),
                "body": (
                    self.tokens.get_font_size("normal"),
                    self.tokens.get_font_weight("normal"),
                ),
                "caption": (
                    self.tokens.get_font_size("small"),
                    self.tokens.get_font_weight("normal"),
                ),
                "small": (
                    self.tokens.get_font_size("small"),
                    self.tokens.get_font_weight("normal"),
                ),
            }

            if variant in variant_styles:
                font_size, font_weight = variant_styles[variant]
                styles.append(f"font-size: {font_size};")
                styles.append(f"font-weight: {weight or font_weight};")

            # 文本颜色
            if color:
                text_color = self.tokens.get_semantic_color(color)
                styles.append(f"color: {text_color};")
            else:
                default_color = self.tokens.get_semantic_color("text")
                styles.append(f"color: {default_color};")

            # 设置样式
            label.setStyleSheet(" ".join(styles))

            self._logger.debug(f"文本样式已应用: {variant}")

        except Exception as e:
            self._logger.error(f"应用文本样式失败: {e}")

    def apply_custom_style(self, widget: QWidget, style_dict: dict[str, str]) -> None:
        """
        应用自定义样式

        Args:
            widget: 组件
            style_dict: 样式字典
        """
        try:
            styles = []

            for property_name, value in style_dict.items():
                # 转换属性名（从camelCase到kebab-case）
                css_property = property_name.replace("_", "-")
                styles.append(f"{css_property}: {value};")

            # 设置样式
            widget.setStyleSheet(" ".join(styles))

            self._logger.debug("自定义样式已应用")

        except Exception as e:
            self._logger.error(f"应用自定义样式失败: {e}")

    def remove_style(self, widget: QWidget) -> None:
        """
        移除组件样式

        Args:
            widget: 组件
        """
        try:
            widget.setStyleSheet("")
            self._logger.debug("组件样式已移除")

        except Exception as e:
            self._logger.error(f"移除组件样式失败: {e}")


# 导出的公共接口
__all__ = [
    "StyleClass",
    "ComponentStyler",
]
