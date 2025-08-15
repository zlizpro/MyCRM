"""
MiniCRM 主题应用器

负责将主题应用到应用程序
"""

import logging
from typing import Any

from PySide6.QtCore import QObject
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


class ThemeApplicator(QObject):
    """主题应用器"""

    def __init__(self):
        """初始化主题应用器"""
        super().__init__()
        self._logger = logging.getLogger(__name__)

    def apply_theme_to_application(
        self, theme_config: dict[str, Any], stylesheet: str
    ) -> None:
        """
        将主题应用到整个应用程序

        Args:
            theme_config: 主题配置
            stylesheet: 样式表
        """
        try:
            app = QApplication.instance()
            if not app:
                self._logger.warning("未找到QApplication实例")
                return

            # 应用样式表
            app.setStyleSheet(stylesheet)

            # 应用调色板
            self._apply_palette(app, theme_config)

            self._logger.info("主题应用成功")

        except Exception as e:
            self._logger.error(f"主题应用失败: {e}")

    def _apply_palette(self, app: QApplication, theme_config: dict[str, Any]) -> None:
        """应用调色板"""
        try:
            colors = theme_config.get("colors", {})

            palette = QPalette()

            # 设置基础颜色
            palette.setColor(
                QPalette.ColorRole.Window, QColor(colors.get("background", "#FFFFFF"))
            )
            palette.setColor(
                QPalette.ColorRole.WindowText,
                QColor(colors.get("text_primary", "#212529")),
            )
            palette.setColor(
                QPalette.ColorRole.Base, QColor(colors.get("card", "#FFFFFF"))
            )
            palette.setColor(
                QPalette.ColorRole.AlternateBase,
                QColor(colors.get("surface", "#F8F9FA")),
            )
            palette.setColor(
                QPalette.ColorRole.Text, QColor(colors.get("text_primary", "#212529"))
            )
            palette.setColor(
                QPalette.ColorRole.Button, QColor(colors.get("surface", "#F8F9FA"))
            )
            palette.setColor(
                QPalette.ColorRole.ButtonText,
                QColor(colors.get("text_primary", "#212529")),
            )
            palette.setColor(
                QPalette.ColorRole.Highlight, QColor(colors.get("primary", "#007BFF"))
            )
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

            # 设置禁用状态颜色
            palette.setColor(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.WindowText,
                QColor(colors.get("text_muted", "#ADB5BD")),
            )
            palette.setColor(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.Text,
                QColor(colors.get("text_muted", "#ADB5BD")),
            )
            palette.setColor(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.ButtonText,
                QColor(colors.get("text_muted", "#ADB5BD")),
            )
            palette.setColor(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.Base,
                QColor(colors.get("disabled", "#E9ECEF")),
            )
            palette.setColor(
                QPalette.ColorGroup.Disabled,
                QPalette.ColorRole.Button,
                QColor(colors.get("disabled", "#E9ECEF")),
            )

            app.setPalette(palette)

        except Exception as e:
            self._logger.error(f"调色板应用失败: {e}")

    def apply_theme_to_widget(
        self, widget, theme_config: dict[str, Any], stylesheet: str
    ) -> None:
        """
        将主题应用到指定组件

        Args:
            widget: 目标组件
            theme_config: 主题配置
            stylesheet: 样式表
        """
        try:
            if widget:
                widget.setStyleSheet(stylesheet)
                self._logger.debug(f"主题已应用到组件: {widget.__class__.__name__}")

        except Exception as e:
            self._logger.error(f"组件主题应用失败: {e}")
