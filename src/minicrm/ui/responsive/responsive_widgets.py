"""
MiniCRM 响应式组件基类

提供响应式布局的基础功能和自动缩放功能。
从 responsive_layout.py 拆分而来，符合MiniCRM模块化标准。
"""

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QPushButton, QToolButton, QWidget

from .types import BreakPoint


if TYPE_CHECKING:
    from .layout_manager import ResponsiveLayoutManager


class ResponsiveWidget(QWidget):
    """
    响应式组件基类

    提供响应式布局的基础功能
    """

    def __init__(self, parent: QWidget | None = None):
        """
        初始化响应式组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._layout_manager: ResponsiveLayoutManager | None = None
        self._current_breakpoint: BreakPoint | None = None

    def set_layout_manager(self, layout_manager: "ResponsiveLayoutManager") -> None:
        """
        设置布局管理器

        Args:
            layout_manager: 响应式布局管理器
        """
        self._layout_manager = layout_manager
        layout_manager.register_responsive_widget(self)

    def apply_responsive_layout(self, breakpoint: BreakPoint) -> None:
        """
        应用响应式布局

        Args:
            breakpoint: 当前断点配置
        """
        try:
            old_breakpoint = self._current_breakpoint
            self._current_breakpoint = breakpoint

            # 调用子类实现的布局更新方法
            self._update_responsive_layout(breakpoint, old_breakpoint)

        except Exception as e:
            self._logger.error(f"响应式布局应用失败: {e}")

    def _update_responsive_layout(
        self, breakpoint: BreakPoint, old_breakpoint: BreakPoint | None
    ) -> None:
        """
        更新响应式布局（子类重写）

        Args:
            breakpoint: 当前断点配置
            old_breakpoint: 之前的断点配置
        """
        pass

    def get_current_breakpoint(self) -> BreakPoint | None:
        """获取当前断点配置"""
        return self._current_breakpoint

    def cleanup(self) -> None:
        """清理资源"""
        if self._layout_manager:
            self._layout_manager.unregister_responsive_widget(self)


class AutoScaleWidget(ResponsiveWidget):
    """
    自动缩放组件

    根据屏幕尺寸自动调整组件大小和字体
    """

    def __init__(self, parent: QWidget | None = None):
        """
        初始化自动缩放组件

        Args:
            parent: 父组件
        """
        super().__init__(parent)

        # 基础尺寸配置
        self._base_font_size = 12
        self._base_icon_size = 16
        self._base_padding = 10
        self._base_margin = 5

        # 缩放配置
        self._font_scale_enabled = True
        self._icon_scale_enabled = True
        self._padding_scale_enabled = True
        self._margin_scale_enabled = True

    def _update_responsive_layout(
        self, breakpoint: BreakPoint, old_breakpoint: BreakPoint | None
    ) -> None:
        """更新响应式布局"""
        try:
            # 应用字体缩放
            if self._font_scale_enabled:
                self._apply_font_scaling(breakpoint.font_scale)

            # 应用图标缩放
            if self._icon_scale_enabled:
                self._apply_icon_scaling(breakpoint.icon_scale)

            # 应用间距缩放
            if self._padding_scale_enabled or self._margin_scale_enabled:
                self._apply_spacing_scaling(breakpoint)

            # 应用自定义缩放
            self._apply_custom_scaling(breakpoint, old_breakpoint)

        except Exception as e:
            self._logger.error(f"自动缩放更新失败: {e}")

    def _apply_font_scaling(self, font_scale: float) -> None:
        """应用字体缩放"""
        try:
            # 获取当前字体
            current_font = self.font()

            # 计算新的字体大小
            new_font_size = int(self._base_font_size * font_scale)

            # 应用新字体大小
            current_font.setPointSize(new_font_size)
            self.setFont(current_font)

            # 递归应用到子组件
            self._apply_font_to_children(current_font)

        except Exception as e:
            self._logger.error(f"字体缩放应用失败: {e}")

    def _apply_font_to_children(self, font: QFont) -> None:
        """递归应用字体到子组件"""
        for child in self.findChildren(QWidget):
            if hasattr(child, "_base_font_size"):
                # 如果子组件也是自动缩放组件，跳过（它会自己处理）
                continue
            child.setFont(font)

    def _apply_icon_scaling(self, icon_scale: float) -> None:
        """应用图标缩放"""
        try:
            # 计算新的图标大小
            new_icon_size = int(self._base_icon_size * icon_scale)
            icon_size = QSize(new_icon_size, new_icon_size)

            # 应用到按钮组件
            for button in self.findChildren(QPushButton):
                button.setIconSize(icon_size)

            for tool_button in self.findChildren(QToolButton):
                tool_button.setIconSize(icon_size)

            # 应用到标签组件（如果有图标）
            for label in self.findChildren(QLabel):
                if label.pixmap():
                    # 重新缩放图标
                    original_pixmap = label.pixmap()
                    scaled_pixmap = original_pixmap.scaled(
                        icon_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    label.setPixmap(scaled_pixmap)

        except Exception as e:
            self._logger.error(f"图标缩放应用失败: {e}")

    def _apply_spacing_scaling(self, breakpoint: BreakPoint) -> None:
        """应用间距缩放"""
        try:
            # 计算缩放比例
            scale = (breakpoint.font_scale + breakpoint.icon_scale) / 2

            # 应用内边距缩放
            if self._padding_scale_enabled:
                new_padding = int(self._base_padding * scale)
                self._apply_padding(new_padding)

            # 应用外边距缩放
            if self._margin_scale_enabled:
                new_margin = int(self._base_margin * scale)
                self._apply_margin(new_margin)

        except Exception as e:
            self._logger.error(f"间距缩放应用失败: {e}")

    def _apply_padding(self, padding: int) -> None:
        """应用内边距"""
        layout = self.layout()
        if layout:
            layout.setContentsMargins(padding, padding, padding, padding)

    def _apply_margin(self, margin: int) -> None:
        """应用外边距"""
        layout = self.layout()
        if layout:
            layout.setSpacing(margin)

    def _apply_custom_scaling(
        self, breakpoint: BreakPoint, old_breakpoint: BreakPoint | None
    ) -> None:
        """应用自定义缩放（子类重写）"""
        pass

    # 配置方法
    def set_base_font_size(self, size: int) -> None:
        """设置基础字体大小"""
        self._base_font_size = size

    def set_base_icon_size(self, size: int) -> None:
        """设置基础图标大小"""
        self._base_icon_size = size

    def set_scaling_enabled(
        self,
        font: bool = True,
        icon: bool = True,
        padding: bool = True,
        margin: bool = True,
    ) -> None:
        """设置缩放功能启用状态"""
        self._font_scale_enabled = font
        self._icon_scale_enabled = icon
        self._padding_scale_enabled = padding
        self._margin_scale_enabled = margin
