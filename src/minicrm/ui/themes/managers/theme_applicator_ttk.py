"""MiniCRM 主题应用器 - TTK版本

负责将主题应用到TTK应用程序
"""

import logging
from tkinter import ttk
from typing import Any


class ThemeApplicatorTTK:
    """主题应用器 - TTK版本"""

    def __init__(self):
        """初始化主题应用器"""
        self._logger = logging.getLogger(__name__)

    def apply_theme(self, theme_data: dict[str, Any]) -> None:
        """应用主题到TTK应用程序

        Args:
            theme_data: 主题数据字典
        """
        try:
            # 获取TTK样式对象
            style = ttk.Style()

            # 应用基础颜色
            colors = theme_data.get("colors", {})
            self._apply_colors(style, colors)

            # 应用字体设置
            fonts = theme_data.get("fonts", {})
            self._apply_fonts(style, fonts)

            # 应用组件样式
            components = theme_data.get("components", {})
            self._apply_component_styles(style, components)

            self._logger.info("主题应用成功")

        except Exception as e:
            self._logger.error(f"主题应用失败: {e}")

    def _apply_colors(self, style: ttk.Style, colors: dict[str, str]) -> None:
        """应用颜色配置"""
        try:
            # 配置基础颜色
            if "background" in colors:
                style.configure(".", background=colors["background"])

            if "foreground" in colors:
                style.configure(".", foreground=colors["foreground"])

            # 配置按钮颜色
            if "primary" in colors:
                style.configure("Primary.TButton", background=colors["primary"])

            if "secondary" in colors:
                style.configure("Secondary.TButton", background=colors["secondary"])

            # 配置输入框颜色
            if "input_background" in colors:
                style.configure(".", fieldbackground=colors["input_background"])

            self._logger.debug("颜色配置已应用")

        except Exception as e:
            self._logger.error(f"颜色配置应用失败: {e}")

    def _apply_fonts(self, style: ttk.Style, fonts: dict[str, Any]) -> None:
        """应用字体配置"""
        try:
            # 应用默认字体
            if "default" in fonts:
                font_config = fonts["default"]
                if isinstance(font_config, dict):
                    font_tuple = (
                        font_config.get("family", "Microsoft YaHei UI"),
                        font_config.get("size", 9),
                        font_config.get("weight", "normal"),
                    )
                    style.configure(".", font=font_tuple)

            # 应用标题字体
            if "heading" in fonts:
                font_config = fonts["heading"]
                if isinstance(font_config, dict):
                    font_tuple = (
                        font_config.get("family", "Microsoft YaHei UI"),
                        font_config.get("size", 12),
                        font_config.get("weight", "bold"),
                    )
                    style.configure("Heading.TLabel", font=font_tuple)

            self._logger.debug("字体配置已应用")

        except Exception as e:
            self._logger.error(f"字体配置应用失败: {e}")

    def _apply_component_styles(
        self, style: ttk.Style, components: dict[str, Any]
    ) -> None:
        """应用组件样式"""
        try:
            # 应用按钮样式
            if "button" in components:
                button_config = components["button"]
                if isinstance(button_config, dict):
                    style.configure("TButton", **button_config)

            # 应用标签样式
            if "label" in components:
                label_config = components["label"]
                if isinstance(label_config, dict):
                    style.configure("TLabel", **label_config)

            # 应用输入框样式
            if "entry" in components:
                entry_config = components["entry"]
                if isinstance(entry_config, dict):
                    style.configure("TEntry", **entry_config)

            # 应用框架样式
            if "frame" in components:
                frame_config = components["frame"]
                if isinstance(frame_config, dict):
                    style.configure("TFrame", **frame_config)

            # 应用树形视图样式
            if "treeview" in components:
                treeview_config = components["treeview"]
                if isinstance(treeview_config, dict):
                    style.configure("Treeview", **treeview_config)

            self._logger.debug("组件样式已应用")

        except Exception as e:
            self._logger.error(f"组件样式应用失败: {e}")

    def reset_theme(self) -> None:
        """重置主题到默认状态"""
        try:
            style = ttk.Style()

            # 重置到默认主题
            available_themes = style.theme_names()
            if "clam" in available_themes:
                style.theme_use("clam")
            elif "default" in available_themes:
                style.theme_use("default")

            self._logger.info("主题已重置到默认状态")

        except Exception as e:
            self._logger.error(f"主题重置失败: {e}")

    def get_available_themes(self) -> list[str]:
        """获取可用的TTK主题列表"""
        try:
            style = ttk.Style()
            return list(style.theme_names())
        except Exception as e:
            self._logger.error(f"获取可用主题失败: {e}")
            return []

    def set_ttk_theme(self, theme_name: str) -> bool:
        """设置TTK内置主题

        Args:
            theme_name: 主题名称

        Returns:
            bool: 是否设置成功
        """
        try:
            style = ttk.Style()
            available_themes = style.theme_names()

            if theme_name in available_themes:
                style.theme_use(theme_name)
                self._logger.info(f"TTK主题已设置为: {theme_name}")
                return True
            self._logger.warning(f"主题不存在: {theme_name}")
            return False

        except Exception as e:
            self._logger.error(f"设置TTK主题失败: {e}")
            return False

    def create_custom_style(
        self, style_name: str, base_style: str, config: dict[str, Any]
    ) -> bool:
        """创建自定义样式

        Args:
            style_name: 样式名称
            base_style: 基础样式
            config: 样式配置

        Returns:
            bool: 是否创建成功
        """
        try:
            style = ttk.Style()
            style.configure(style_name, **config)
            self._logger.debug(f"自定义样式已创建: {style_name}")
            return True

        except Exception as e:
            self._logger.error(f"创建自定义样式失败: {e}")
            return False


# 为了兼容性,创建一个别名
ThemeApplicator = ThemeApplicatorTTK
