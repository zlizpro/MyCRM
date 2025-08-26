"""TTK主题管理器.

为MiniCRM TTK界面提供完整的主题管理功能, 包括:
- 多主题切换支持(默认、深色、浅色、高对比度)
- 主题配置保存和加载
- 自定义主题创建和管理
- 主题导入导出功能
- 实时主题预览

设计目标:
1. 提供统一的TTK主题管理接口
2. 支持多种内置主题和自定义主题
3. 实现主题配置的持久化存储
4. 提供主题编辑和预览功能

作者: MiniCRM开发团队
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import tkinter as tk
from typing import Any, Callable

from .style_manager import (
    CustomTheme,
    StyleManager,
    ThemeType,
)


class TTKThemeManager:
    """TTK主题管理器.

    提供完整的TTK主题管理功能, 包括主题切换、配置保存、
    自定义主题创建等功能.
    """

    def __init__(self, root: tk.Tk | None = None) -> None:
        """初始化TTK主题管理器.

        Args:
            root: 根窗口对象
        """
        self.root = root
        self.logger = logging.getLogger(__name__)

        # 使用现有的StyleManager作为底层实现
        self.style_manager = StyleManager(root)

        # 主题配置文件路径
        self.config_dir = Path.home() / ".minicrm" / "themes"
        self.config_file = self.config_dir / "theme_config.json"

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 主题变化回调列表
        self.theme_change_callbacks: list[Callable[[str], None]] = []

        # 加载保存的主题配置
        self._load_theme_config()

        self.logger.info("TTK主题管理器初始化完成")

    def get_available_themes(self) -> dict[str, str]:
        """获取可用主题列表.

        Returns:
            主题ID到主题名称的映射字典
        """
        themes = {}
        for theme_id in self.style_manager.get_available_themes():
            theme = self.style_manager.themes[theme_id]
            # 获取主题名称, 如果没有name属性则使用theme_id
            theme_name = getattr(theme, "name", theme_id)
            themes[theme_id] = theme_name
        return themes

    def get_current_theme(self) -> str:
        """获取当前主题ID.

        Returns:
            当前主题的ID
        """
        current_theme = self.style_manager.get_current_theme()
        return current_theme.name if current_theme else ThemeType.DEFAULT.value

    def set_theme(self, theme_id: str, save_preference: bool = True) -> bool:
        """设置当前主题.

        Args:
            theme_id: 主题ID
            save_preference: 是否保存主题偏好

        Returns:
            是否设置成功
        """
        success = self.style_manager.apply_theme(theme_id)

        if success:
            # 触发主题变化回调
            self._trigger_theme_callbacks(theme_id)

            # 保存主题偏好
            if save_preference:
                self._save_theme_preference(theme_id)

            self.logger.info("主题切换成功: %s", theme_id)

        return success

    def get_theme_config(self, theme_id: str) -> dict[str, Any]:
        """获取主题配置.

        Args:
            theme_id: 主题ID

        Returns:
            主题配置字典
        """
        if theme_id in self.style_manager.themes:
            theme = self.style_manager.themes[theme_id]
            config = theme.get_style_config()
            # 确保配置中有name字段
            if "name" not in config:
                config["name"] = getattr(theme, "name", theme_id)
            return config
        return {}

    def create_custom_theme(
        self,
        theme_id: str,
        theme_name: str,
        base_theme: str = "default",
        colors: dict[str, str] | None = None,
        fonts: dict[str, dict[str, Any]] | None = None,
        spacing: dict[str, int] | None = None,
    ) -> bool:
        """创建自定义主题.

        Args:
            theme_id: 主题ID
            theme_name: 主题显示名称
            base_theme: 基础主题ID
            colors: 颜色配置
            fonts: 字体配置
            spacing: 间距配置

        Returns:
            是否创建成功
        """
        try:
            # 获取基础主题配置
            if base_theme in self.style_manager.themes:
                base_config = self.style_manager.themes[base_theme].get_style_config()
            else:
                base_config = self.style_manager.themes[
                    ThemeType.DEFAULT.value
                ].get_style_config()

            # 创建新的主题配置
            new_config = base_config.copy()
            new_config["name"] = theme_name

            # 更新颜色配置
            if colors:
                new_config["colors"].update(colors)

            # 更新字体配置
            if fonts:
                new_config["fonts"].update(fonts)

            # 更新间距配置
            if spacing:
                new_config["spacing"].update(spacing)

            # 创建自定义主题对象
            custom_theme = CustomTheme(theme_id, new_config)
            self.style_manager.register_theme(custom_theme)

            # 保存自定义主题到文件
            self._save_custom_theme(theme_id, new_config)

            self.logger.info("自定义主题创建成功: %s", theme_id)
        except Exception:
            self.logger.exception("创建自定义主题失败")
            return False
        else:
            return True

    def delete_custom_theme(self, theme_id: str) -> bool:
        """删除自定义主题.

        Args:
            theme_id: 主题ID

        Returns:
            是否删除成功
        """
        try:
            # 不能删除内置主题
            if theme_id in [
                ThemeType.DEFAULT.value,
                ThemeType.DARK.value,
                ThemeType.LIGHT.value,
                ThemeType.HIGH_CONTRAST.value,
            ]:
                self.logger.warning("不能删除内置主题: %s", theme_id)
                return False

            # 从主题管理器中移除
            if theme_id in self.style_manager.themes:
                del self.style_manager.themes[theme_id]

            # 删除主题文件
            theme_file = self.config_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()

            self.logger.info("自定义主题删除成功: %s", theme_id)
        except Exception:
            self.logger.exception("删除自定义主题失败")
            return False
        else:
            return True

    def export_theme(self, theme_id: str, file_path: str) -> bool:
        """导出主题配置到文件.

        Args:
            theme_id: 主题ID
            file_path: 导出文件路径

        Returns:
            是否导出成功
        """
        try:
            # 检查主题是否存在
            if theme_id not in self.style_manager.themes:
                self.logger.warning("主题不存在: %s", theme_id)
                return False

            theme_config = self.get_theme_config(theme_id)

            # 确保目录存在
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            file_path_obj.write_text(
                json.dumps(theme_config, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            self.logger.info("主题导出成功: %s -> %s", theme_id, file_path)
        except Exception:
            self.logger.exception("主题导出失败")
            return False
        else:
            return True

    def import_theme(self, file_path: str, theme_id: str | None = None) -> bool:
        """从文件导入主题配置.

        Args:
            file_path: 主题文件路径
            theme_id: 主题ID, 如果为None则使用文件名

        Returns:
            是否导入成功
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                self.logger.warning("主题文件不存在: %s", file_path)
                return False

            # 读取主题配置
            theme_config = json.loads(file_path_obj.read_text(encoding="utf-8"))

            # 确定主题ID
            if theme_id is None:
                theme_id = file_path_obj.stem

            # 创建自定义主题
            custom_theme = CustomTheme(theme_id, theme_config)
            self.style_manager.register_theme(custom_theme)

            # 保存到本地配置
            self._save_custom_theme(theme_id, theme_config)

            self.logger.info("主题导入成功: %s -> %s", file_path, theme_id)
        except Exception:
            self.logger.exception("主题导入失败")
            return False
        else:
            return True

    def add_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """添加主题变化回调函数.

        Args:
            callback: 回调函数, 接收主题ID参数
        """
        self.theme_change_callbacks.append(callback)

    def remove_theme_change_callback(self, callback: Callable[[str], None]) -> None:
        """移除主题变化回调函数.

        Args:
            callback: 要移除的回调函数
        """
        if callback in self.theme_change_callbacks:
            self.theme_change_callbacks.remove(callback)

    def _trigger_theme_callbacks(self, theme_id: str) -> None:
        """触发主题变化回调.

        Args:
            theme_id: 主题ID
        """
        for callback in self.theme_change_callbacks:
            try:
                callback(theme_id)
            except Exception:
                self.logger.exception("主题变化回调执行失败")

    def get_theme_colors(self, theme_id: str | None = None) -> dict[str, str]:
        """获取主题颜色配置.

        Args:
            theme_id: 主题ID, 如果为None则使用当前主题

        Returns:
            颜色配置字典
        """
        if theme_id is None:
            theme_id = self.get_current_theme()

        theme_config = self.get_theme_config(theme_id)
        colors = theme_config.get("colors", {})
        return colors if isinstance(colors, dict) else {}

    def get_theme_fonts(self, theme_id: str | None = None) -> dict[str, dict[str, Any]]:
        """获取主题字体配置.

        Args:
            theme_id: 主题ID, 如果为None则使用当前主题

        Returns:
            字体配置字典
        """
        if theme_id is None:
            theme_id = self.get_current_theme()

        theme_config = self.get_theme_config(theme_id)
        fonts = theme_config.get("fonts", {})
        return fonts if isinstance(fonts, dict) else {}

    def get_theme_spacing(self, theme_id: str | None = None) -> dict[str, int]:
        """获取主题间距配置.

        Args:
            theme_id: 主题ID, 如果为None则使用当前主题

        Returns:
            间距配置字典
        """
        if theme_id is None:
            theme_id = self.get_current_theme()

        theme_config = self.get_theme_config(theme_id)
        spacing = theme_config.get("spacing", {})
        return spacing if isinstance(spacing, dict) else {}

    def apply_theme_to_widget(
        self, widget: tk.Widget, theme_id: str | None = None
    ) -> None:
        """将主题应用到指定组件.

        Args:
            widget: 目标组件
            theme_id: 主题ID, 如果为None则使用当前主题
        """
        if theme_id is None:
            theme_id = self.get_current_theme()

        if theme_id in self.style_manager.themes:
            theme = self.style_manager.themes[theme_id]
            colors = theme.colors

            # 应用基础样式
            try:
                if hasattr(widget, "configure"):
                    # 只对支持这些选项的组件应用样式
                    configure_options = {}
                    if hasattr(colors, "bg_primary"):
                        configure_options["bg"] = colors.bg_primary
                    if hasattr(colors, "text_primary"):
                        configure_options["fg"] = colors.text_primary

                    if configure_options:
                        widget.configure(**configure_options)
            except (tk.TclError, AttributeError):
                # 某些组件可能不支持这些选项
                pass

    def reset_to_default(self) -> None:
        """重置为默认主题."""
        self.set_theme(ThemeType.DEFAULT.value)
        self.logger.info("重置为默认主题")

    def _load_theme_config(self) -> None:
        """加载保存的主题配置."""
        try:
            if self.config_file.exists():
                config = json.loads(self.config_file.read_text(encoding="utf-8"))

                # 加载当前主题
                current_theme = config.get("current_theme", ThemeType.DEFAULT.value)

                # 加载自定义主题
                custom_themes = config.get("custom_themes", {})
                for theme_id, theme_config in custom_themes.items():
                    custom_theme = CustomTheme(theme_id, theme_config)
                    self.style_manager.register_theme(custom_theme)

                # 应用保存的主题
                self.set_theme(current_theme, save_preference=False)

                self.logger.info("加载主题配置成功, 当前主题: %s", current_theme)
            else:
                # 使用默认主题
                self.set_theme(ThemeType.DEFAULT.value, save_preference=False)

        except Exception:
            self.logger.exception("加载主题配置失败")
            # 使用默认主题
            self.set_theme(ThemeType.DEFAULT.value, save_preference=False)

    def _save_theme_preference(self, theme_id: str) -> None:
        """保存主题偏好设置.

        Args:
            theme_id: 主题ID
        """
        try:
            # 读取现有配置
            config = {}
            if self.config_file.exists():
                config = json.loads(self.config_file.read_text(encoding="utf-8"))

            # 更新当前主题
            config["current_theme"] = theme_id

            # 保存配置
            self.config_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            self.logger.debug("主题偏好保存成功: %s", theme_id)

        except Exception:
            self.logger.exception("保存主题偏好失败")

    def _save_custom_theme(self, theme_id: str, theme_config: dict[str, Any]) -> None:
        """保存自定义主题配置.

        Args:
            theme_id: 主题ID
            theme_config: 主题配置
        """
        try:
            # 读取现有配置
            config = {}
            if self.config_file.exists():
                config = json.loads(self.config_file.read_text(encoding="utf-8"))

            # 更新自定义主题
            if "custom_themes" not in config:
                config["custom_themes"] = {}
            config["custom_themes"][theme_id] = theme_config

            # 保存配置
            self.config_file.write_text(
                json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
            )

            self.logger.debug("自定义主题保存成功: %s", theme_id)

        except Exception:
            self.logger.exception("保存自定义主题失败")

    def get_style_manager(self) -> StyleManager:
        """获取底层样式管理器.

        Returns:
            StyleManager实例
        """
        return self.style_manager


# 全局TTK主题管理器实例
_global_ttk_theme_manager: TTKThemeManager | None = None


def get_global_ttk_theme_manager() -> TTKThemeManager:
    """获取全局TTK主题管理器实例.

    Returns:
        全局TTK主题管理器
    """
    global _global_ttk_theme_manager  # noqa: PLW0603
    if _global_ttk_theme_manager is None:
        _global_ttk_theme_manager = TTKThemeManager()
    return _global_ttk_theme_manager


def apply_global_ttk_theme(theme_id: str) -> bool:
    """应用全局TTK主题.

    Args:
        theme_id: 主题ID

    Returns:
        是否应用成功
    """
    return get_global_ttk_theme_manager().set_theme(theme_id)
