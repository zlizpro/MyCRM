"""
MiniCRM 响应式布局管理器

负责管理应用程序的响应式布局，包括断点管理、组件尺寸自适应等。
从 responsive_layout.py 拆分而来，符合MiniCRM模块化标准。
"""

import logging

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget

from .types import BreakPoint, LayoutConfig, ScreenSize


class ResponsiveLayoutManager(QObject):
    """
    响应式布局管理器

    负责管理应用程序的响应式布局，包括：
    - 断点管理和检测
    - 组件尺寸自适应
    - 布局重排和优化
    - 高DPI显示适配

    Signals:
        breakpoint_changed: 断点变化信号 (old_breakpoint: str, new_breakpoint: str)
        layout_changed: 布局变化信号 (screen_size: ScreenSize)
        dpi_changed: DPI变化信号 (dpi_scale: float)
    """

    # Qt信号定义
    breakpoint_changed = Signal(str, str)
    layout_changed = Signal(ScreenSize)
    dpi_changed = Signal(float)

    def __init__(self, parent: QObject | None = None):
        """
        初始化响应式布局管理器

        Args:
            parent: 父对象
        """
        super().__init__(parent)

        self._logger = logging.getLogger(__name__)

        # 布局配置
        self._layout_config = LayoutConfig()

        # 断点配置
        self._breakpoints: dict[str, BreakPoint] = {}
        self._current_breakpoint: str | None = None

        # 当前屏幕信息
        self._current_screen_size: ScreenSize | None = None
        self._current_dpi_scale: float = 1.0

        # 注册的响应式组件
        self._responsive_widgets: list[QWidget] = []

        # 布局更新定时器
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._update_layout)

        # 初始化断点
        self._setup_default_breakpoints()

        # 监听屏幕变化
        self._setup_screen_monitoring()

        self._logger.debug("响应式布局管理器初始化完成")

    def _setup_default_breakpoints(self) -> None:
        """设置默认断点"""
        # 小屏幕断点 (< 1024px)
        self.add_breakpoint(
            "small",
            min_width=0,
            max_width=1023,
            sidebar_width=200,
            content_padding=10,
            font_scale=0.9,
            icon_scale=0.9,
        )

        # 中等屏幕断点 (1024px - 1440px)
        self.add_breakpoint(
            "medium",
            min_width=1024,
            max_width=1439,
            sidebar_width=250,
            content_padding=15,
            font_scale=1.0,
            icon_scale=1.0,
        )

        # 大屏幕断点 (1440px - 1920px)
        self.add_breakpoint(
            "large",
            min_width=1440,
            max_width=1919,
            sidebar_width=300,
            content_padding=20,
            font_scale=1.1,
            icon_scale=1.1,
        )

        # 超大屏幕断点 (> 1920px)
        self.add_breakpoint(
            "xlarge",
            min_width=1920,
            max_width=None,
            sidebar_width=350,
            content_padding=25,
            font_scale=1.2,
            icon_scale=1.2,
        )

    def _setup_screen_monitoring(self) -> None:
        """设置屏幕监控"""
        try:
            app = QApplication.instance()
            if app and isinstance(app, QApplication):
                # 监听屏幕变化
                app.screenAdded.connect(self._on_screen_changed)
                app.screenRemoved.connect(self._on_screen_changed)
                app.primaryScreenChanged.connect(self._on_screen_changed)

                # 获取当前屏幕信息
                self._update_screen_info()

        except Exception as e:
            self._logger.error(f"屏幕监控设置失败: {e}")

    def add_breakpoint(
        self,
        name: str,
        min_width: int,
        max_width: int | None = None,
        sidebar_width: int = 250,
        content_padding: int = 20,
        font_scale: float = 1.0,
        icon_scale: float = 1.0,
    ) -> None:
        """
        添加断点配置

        Args:
            name: 断点名称
            min_width: 最小宽度
            max_width: 最大宽度
            sidebar_width: 侧边栏宽度
            content_padding: 内容区域内边距
            font_scale: 字体缩放比例
            icon_scale: 图标缩放比例
        """
        breakpoint = BreakPoint(
            name=name,
            min_width=min_width,
            max_width=max_width,
            sidebar_width=sidebar_width,
            content_padding=content_padding,
            font_scale=font_scale,
            icon_scale=icon_scale,
        )

        self._breakpoints[name] = breakpoint
        self._logger.debug(f"添加断点: {name} ({min_width}px - {max_width or '∞'}px)")

    def register_responsive_widget(self, widget: QWidget) -> None:
        """
        注册响应式组件

        Args:
            widget: 需要响应式处理的组件
        """
        if widget not in self._responsive_widgets:
            self._responsive_widgets.append(widget)

            # 如果组件有响应式方法，立即应用当前布局
            if hasattr(widget, "apply_responsive_layout"):
                current_breakpoint = self.get_current_breakpoint()
                if current_breakpoint:
                    widget.apply_responsive_layout(current_breakpoint)

            self._logger.debug(f"注册响应式组件: {widget.__class__.__name__}")

    def unregister_responsive_widget(self, widget: QWidget) -> None:
        """
        取消注册响应式组件

        Args:
            widget: 要取消注册的组件
        """
        if widget in self._responsive_widgets:
            self._responsive_widgets.remove(widget)
            self._logger.debug(f"取消注册响应式组件: {widget.__class__.__name__}")

    def get_current_breakpoint(self) -> BreakPoint | None:
        """获取当前断点配置"""
        if self._current_breakpoint and self._current_breakpoint in self._breakpoints:
            return self._breakpoints[self._current_breakpoint]
        return None

    def get_breakpoint_by_width(self, width: int) -> BreakPoint | None:
        """
        根据宽度获取对应的断点

        Args:
            width: 窗口宽度

        Returns:
            对应的断点配置，如果没有匹配则返回None
        """
        for breakpoint in self._breakpoints.values():
            if width >= breakpoint.min_width and (
                breakpoint.max_width is None or width <= breakpoint.max_width
            ):
                return breakpoint
        return None

    def update_layout_for_size(self, width: int, height: int) -> None:
        """
        根据窗口尺寸更新布局

        Args:
            width: 窗口宽度
            height: 窗口高度
        """
        try:
            # 获取对应的断点
            new_breakpoint = self.get_breakpoint_by_width(width)
            if not new_breakpoint:
                return

            # 检查断点是否变化
            old_breakpoint_name = self._current_breakpoint
            new_breakpoint_name = new_breakpoint.name

            if old_breakpoint_name != new_breakpoint_name:
                self._current_breakpoint = new_breakpoint_name

                # 发送断点变化信号
                self.breakpoint_changed.emit(
                    old_breakpoint_name or "", new_breakpoint_name
                )

                # 延迟更新布局（避免频繁更新）
                self._update_timer.start(100)

                self._logger.debug(
                    f"断点变化: {old_breakpoint_name} -> {new_breakpoint_name}"
                )

        except Exception as e:
            self._logger.error(f"布局更新失败: {e}")

    def _update_layout(self) -> None:
        """更新所有响应式组件的布局"""
        try:
            current_breakpoint = self.get_current_breakpoint()
            if not current_breakpoint:
                return

            # 更新所有注册的响应式组件
            for widget in self._responsive_widgets[:]:  # 使用副本避免迭代时修改
                try:
                    if widget and not widget.isHidden():
                        if hasattr(widget, "apply_responsive_layout"):
                            widget.apply_responsive_layout(current_breakpoint)
                        elif hasattr(widget, "update_layout"):
                            widget.update_layout()
                except Exception as e:
                    self._logger.error(
                        f"组件布局更新失败 [{widget.__class__.__name__}]: {e}"
                    )

            # 发送布局变化信号
            screen_size = self._get_screen_size_from_breakpoint(current_breakpoint.name)
            if screen_size:
                self.layout_changed.emit(screen_size)

            self._logger.debug(f"布局更新完成: {current_breakpoint.name}")

        except Exception as e:
            self._logger.error(f"布局更新失败: {e}")

    def _get_screen_size_from_breakpoint(
        self, breakpoint_name: str
    ) -> ScreenSize | None:
        """根据断点名称获取屏幕尺寸枚举"""
        mapping = {
            "small": ScreenSize.SMALL,
            "medium": ScreenSize.MEDIUM,
            "large": ScreenSize.LARGE,
            "xlarge": ScreenSize.XLARGE,
        }
        return mapping.get(breakpoint_name)

    def _update_screen_info(self) -> None:
        """更新屏幕信息"""
        try:
            app = QApplication.instance()
            if not app or not isinstance(app, QApplication):
                return

            primary_screen = app.primaryScreen()
            if not primary_screen:
                return

            # 获取屏幕几何信息
            screen_geometry = primary_screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()

            # 获取DPI信息
            dpi = primary_screen.logicalDotsPerInch()
            dpi_scale = dpi / 96.0  # 96 DPI是标准DPI

            # 检查DPI变化
            if abs(self._current_dpi_scale - dpi_scale) > 0.1:
                old_dpi_scale = self._current_dpi_scale
                self._current_dpi_scale = dpi_scale
                self.dpi_changed.emit(dpi_scale)
                self._logger.debug(f"DPI变化: {old_dpi_scale:.2f} -> {dpi_scale:.2f}")

            # 更新布局
            self.update_layout_for_size(screen_width, screen_height)

        except Exception as e:
            self._logger.error(f"屏幕信息更新失败: {e}")

    def _on_screen_changed(self, screen: QScreen | None = None) -> None:
        """屏幕变化处理"""
        self._logger.debug("检测到屏幕变化")
        # 延迟更新，避免频繁触发
        QTimer.singleShot(500, self._update_screen_info)

    def get_layout_config(self) -> LayoutConfig:
        """获取布局配置"""
        return self._layout_config

    def set_layout_config(self, config: LayoutConfig) -> None:
        """设置布局配置"""
        self._layout_config = config
        self._logger.debug("布局配置已更新")

    def get_optimal_sidebar_width(self, window_width: int) -> int:
        """
        获取最优侧边栏宽度

        Args:
            window_width: 窗口宽度

        Returns:
            最优侧边栏宽度
        """
        breakpoint = self.get_breakpoint_by_width(window_width)
        if breakpoint:
            return max(
                self._layout_config.sidebar_min_width,
                min(breakpoint.sidebar_width, self._layout_config.sidebar_max_width),
            )
        return self._layout_config.sidebar_min_width

    def get_optimal_content_padding(self, window_width: int) -> int:
        """
        获取最优内容区域内边距

        Args:
            window_width: 窗口宽度

        Returns:
            最优内容区域内边距
        """
        breakpoint = self.get_breakpoint_by_width(window_width)
        return breakpoint.content_padding if breakpoint else 20

    def get_font_scale(self, window_width: int) -> float:
        """
        获取字体缩放比例

        Args:
            window_width: 窗口宽度

        Returns:
            字体缩放比例
        """
        breakpoint = self.get_breakpoint_by_width(window_width)
        base_scale = breakpoint.font_scale if breakpoint else 1.0

        # 考虑DPI缩放
        return base_scale * self._current_dpi_scale

    def get_icon_scale(self, window_width: int) -> float:
        """
        获取图标缩放比例

        Args:
            window_width: 窗口宽度

        Returns:
            图标缩放比例
        """
        breakpoint = self.get_breakpoint_by_width(window_width)
        base_scale = breakpoint.icon_scale if breakpoint else 1.0

        # 考虑DPI缩放
        return base_scale * self._current_dpi_scale

    def is_small_screen(self) -> bool:
        """判断是否为小屏幕"""
        return self._current_breakpoint == "small"

    def is_mobile_layout(self) -> bool:
        """判断是否应该使用移动端布局"""
        # 当屏幕宽度小于1024px时使用移动端布局
        return self.is_small_screen()

    def cleanup(self) -> None:
        """清理资源"""
        try:
            self._update_timer.stop()
            self._responsive_widgets.clear()
            self._logger.debug("响应式布局管理器清理完成")

        except Exception as e:
            self._logger.error(f"响应式布局管理器清理失败: {e}")
