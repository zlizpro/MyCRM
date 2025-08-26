"""MiniCRM 主题管理器 - TTK版本

使用模块化设计的主题管理器,支持用户偏好保存和跨平台适配
完全基于TTK,无Qt依赖
"""

import logging
import platform
from typing import Any

from .stylesheet_generator import StylesheetGenerator
from .theme_applicator import ThemeApplicator
from .theme_definitions import get_theme_definitions
from .theme_io_manager import ThemeIOManager


class ThemeManager:
    """主题管理器 - TTK版本

    使用模块化设计:
    - ThemeDefinitions: 主题定义
    - StylesheetGenerator: 样式表生成
    - ThemeApplicator: 主题应用
    - ThemeIOManager: 导入导出
    - 集成用户偏好保存和跨平台适配

    回调机制:
        theme_changed_callbacks: 主题切换回调列表
    """

    _instance = None  # 单例实例

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化主题管理器"""
        # 避免重复初始化
        if hasattr(self, "_initialized"):
            return

        self._logger = logging.getLogger(__name__)
        self._current_theme = "light"

        # 主题变化回调列表(替代Qt信号)
        self._theme_changed_callbacks: list[Callable[[str], None]] = []

        # 配置管理器(延迟导入以避免循环依赖)
        self._config = None

        # 组件管理器
        self._stylesheet_generator = StylesheetGenerator()
        self._theme_applicator = ThemeApplicator()
        self._theme_io_manager = ThemeIOManager()

        # 主题定义
        self._themes = get_theme_definitions()

        # 自定义主题
        self._custom_themes: dict[str, dict[str, Any]] = {}

        # 平台信息
        self._platform = platform.system().lower()
        self._is_high_dpi = self._detect_high_dpi()

        # 从配置加载主题(如果可用)
        self._load_theme_from_config()

        self._initialized = True
        self._logger.debug("主题管理器初始化完成")

    def get_available_themes(self) -> dict[str, str]:
        """获取可用主题列表"""
        themes = {}

        # 内置主题
        for theme_id, config in self._themes.items():
            themes[theme_id] = config.get("name", theme_id)

        # 自定义主题
        for theme_id, config in self._custom_themes.items():
            themes[theme_id] = config.get("name", theme_id)

        return themes

    def get_current_theme(self) -> str:
        """获取当前主题ID"""
        return self._current_theme

    def set_theme(self, theme_id: str, save_preference: bool = True) -> bool:
        """设置当前主题"""
        try:
            if theme_id not in self._themes and theme_id not in self._custom_themes:
                self._logger.warning(f"主题不存在: {theme_id}")
                return False

            self._current_theme = theme_id

            # 获取主题配置并应用平台调整
            theme_config = self.get_theme_config(theme_id)
            adjusted_config = self._apply_platform_adjustments(theme_config)

            # 生成样式表
            stylesheet = self._stylesheet_generator.generate_stylesheet(adjusted_config)

            # 应用主题
            self._theme_applicator.apply_theme_to_application(
                adjusted_config, stylesheet
            )

            # 保存用户偏好(如果不是自动模式触发的切换)
            if save_preference and not self.is_auto_theme_enabled():
                self.save_theme_preference(theme_id)

            # 触发回调
            self._trigger_theme_changed_callbacks(theme_id)

            self._logger.info(f"主题切换成功: {theme_id}")
            return True

        except Exception as e:
            self._logger.error(f"主题切换失败: {e}")
            return False

    def get_theme_config(self, theme_id: str | None = None) -> dict[str, Any]:
        """获取主题配置"""
        if theme_id is None:
            theme_id = self._current_theme

        # 优先查找自定义主题
        if theme_id in self._custom_themes:
            return self._custom_themes[theme_id]

        # 查找内置主题
        return self._themes.get(theme_id, self._themes["light"])

    def get_color(self, color_name: str, theme_id: str | None = None) -> str:
        """获取主题颜色"""
        theme_config = self.get_theme_config(theme_id)
        return theme_config["colors"].get(color_name, "#000000")

    def get_stylesheet(self, theme_id: str | None = None) -> str:
        """生成主题样式表"""
        theme_config = self.get_theme_config(theme_id)
        adjusted_config = self._apply_platform_adjustments(theme_config)
        return self._stylesheet_generator.generate_stylesheet(adjusted_config)

    def apply_theme_to_application(self, theme_id: str | None = None) -> None:
        """将主题应用到整个应用程序"""
        theme_config = self.get_theme_config(theme_id)
        adjusted_config = self._apply_platform_adjustments(theme_config)
        stylesheet = self._stylesheet_generator.generate_stylesheet(adjusted_config)
        self._theme_applicator.apply_theme_to_application(adjusted_config, stylesheet)

    def apply_theme_to_widget(self, widget, theme_id: str | None = None) -> None:
        """将主题应用到指定组件"""
        theme_config = self.get_theme_config(theme_id)
        adjusted_config = self._apply_platform_adjustments(theme_config)
        stylesheet = self._stylesheet_generator.generate_stylesheet(adjusted_config)
        self._theme_applicator.apply_theme_to_widget(
            widget, adjusted_config, stylesheet
        )

    def create_custom_theme(
        self,
        theme_id: str,
        theme_name: str,
        colors: dict[str, str] | None = None,
        fonts: dict[str, str] | None = None,
        spacing: dict[str, str] | None = None,
        border_radius: dict[str, str] | None = None,
    ) -> bool:
        """创建自定义主题"""
        try:
            # 创建基础模板
            template = self._theme_io_manager.create_theme_template()

            # 更新配置
            template["name"] = theme_name
            if colors:
                template["colors"].update(colors)
            if fonts:
                template["fonts"].update(fonts)
            if spacing:
                template["spacing"].update(spacing)
            if border_radius:
                template["border_radius"].update(border_radius)

            # 保存自定义主题
            self._custom_themes[theme_id] = template

            self._logger.info(f"自定义主题创建成功: {theme_id}")
            return True

        except Exception as e:
            self._logger.error(f"自定义主题创建失败: {e}")
            return False

    def export_theme(self, theme_id: str, file_path: str) -> bool:
        """导出主题配置"""
        try:
            theme_config = self.get_theme_config(theme_id)
            return self._theme_io_manager.export_theme(theme_config, file_path)

        except Exception as e:
            self._logger.error(f"主题导出失败: {e}")
            return False

    def import_theme(self, theme_id: str, file_path: str) -> bool:
        """导入主题配置"""
        try:
            theme_config = self._theme_io_manager.import_theme(file_path)
            if theme_config:
                self._custom_themes[theme_id] = theme_config
                self._logger.info(f"主题导入成功: {theme_id}")
                return True
            return False

        except Exception as e:
            self._logger.error(f"主题导入失败: {e}")
            return False

    def delete_custom_theme(self, theme_id: str) -> bool:
        """删除自定义主题"""
        try:
            if theme_id in self._custom_themes:
                del self._custom_themes[theme_id]
                self._logger.info(f"自定义主题删除成功: {theme_id}")
                return True
            self._logger.warning(f"自定义主题不存在: {theme_id}")
            return False

        except Exception as e:
            self._logger.error(f"自定义主题删除失败: {e}")
            return False

    def _detect_high_dpi(self) -> bool:
        """检测是否为高DPI显示 - TTK版本"""
        try:
            # 在TTK中,我们可以通过tkinter获取DPI信息
            import tkinter as tk

            # 创建临时窗口来检测DPI
            temp_root = tk.Tk()
            temp_root.withdraw()  # 隐藏窗口

            # 获取DPI信息
            dpi = temp_root.winfo_fpixels("1i")  # 每英寸像素数
            temp_root.destroy()

            # 标准DPI是96,高DPI通常是144或更高
            return dpi > 120
        except Exception as e:
            self._logger.warning(f"高DPI检测失败: {e}")
            return False

    def _get_config(self):
        """获取配置管理器实例(延迟导入)"""
        if self._config is None:
            try:
                from minicrm.core.config import AppConfig

                self._config = AppConfig()
            except ImportError:
                self._logger.warning("配置管理器不可用,使用默认设置")
                self._config = False  # 标记为不可用
        return self._config if self._config is not False else None

    def _load_theme_from_config(self) -> None:
        """从配置加载主题设置"""
        try:
            config = self._get_config()
            if config:
                from minicrm.core.config import ThemeMode

                theme_mode = config.get_theme_mode()

                if theme_mode == ThemeMode.AUTO:
                    # 自动模式:根据系统主题选择
                    system_theme = self._detect_system_theme()
                    self._current_theme = system_theme
                else:
                    # 手动模式:使用配置的主题
                    self._current_theme = theme_mode.value

                self._logger.info(f"从配置加载主题: {self._current_theme}")
            else:
                # 配置不可用,使用默认主题
                self._current_theme = "light"
                self._logger.info("配置不可用,使用默认主题: light")

        except Exception as e:
            self._logger.warning(f"从配置加载主题失败,使用默认主题: {e}")
            self._current_theme = "light"

    def _detect_system_theme(self) -> str:
        """检测系统主题"""
        try:
            if self._platform == "windows":
                return self._detect_windows_theme()
            if self._platform == "darwin":  # macOS
                return self._detect_macos_theme()
            # Linux等其他系统默认使用浅色主题
            return "light"
        except Exception as e:
            self._logger.warning(f"系统主题检测失败: {e}")
            return "light"

    def _detect_windows_theme(self) -> str:
        """检测Windows系统主题"""
        try:
            import winreg

            # 读取Windows注册表中的主题设置
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )

            # AppsUseLightTheme: 0=深色, 1=浅色
            apps_use_light_theme, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)

            return "light" if apps_use_light_theme else "dark"

        except Exception as e:
            self._logger.warning(f"Windows主题检测失败: {e}")
            return "light"

    def _detect_macos_theme(self) -> str:
        """检测macOS系统主题"""
        try:
            import subprocess

            # 使用defaults命令检查macOS主题
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                check=False,
                capture_output=True,
                text=True,
            )

            # 如果返回"Dark"则为深色主题,否则为浅色主题
            return "dark" if result.stdout.strip() == "Dark" else "light"

        except Exception as e:
            self._logger.warning(f"macOS主题检测失败: {e}")
            return "light"

    def _apply_platform_adjustments(
        self, theme_config: dict[str, Any]
    ) -> dict[str, Any]:
        """应用平台特定的样式调整"""
        try:
            adjusted_config = theme_config.copy()

            # 高DPI调整
            if self._is_high_dpi:
                adjusted_config = self._apply_high_dpi_adjustments(adjusted_config)

            # 平台特定调整
            if self._platform == "darwin":  # macOS
                adjusted_config = self._apply_macos_adjustments(adjusted_config)
            elif self._platform == "windows":
                adjusted_config = self._apply_windows_adjustments(adjusted_config)

            return adjusted_config

        except Exception as e:
            self._logger.warning(f"平台调整失败: {e}")
            return theme_config

    def _apply_high_dpi_adjustments(
        self, theme_config: dict[str, Any]
    ) -> dict[str, Any]:
        """应用高DPI显示调整"""
        try:
            adjusted_config = theme_config.copy()

            # 调整字体大小
            fonts = adjusted_config.get("fonts", {}).copy()
            for key, value in fonts.items():
                if key.startswith("size_") and value.endswith("px"):
                    # 提取数字并增加20%
                    size = int(value[:-2])
                    new_size = int(size * 1.2)
                    fonts[key] = f"{new_size}px"

            adjusted_config["fonts"] = fonts

            # 调整间距
            spacing = adjusted_config.get("spacing", {}).copy()
            for key, value in spacing.items():
                if value.endswith("px"):
                    # 提取数字并增加20%
                    size = int(value[:-2])
                    new_size = int(size * 1.2)
                    spacing[key] = f"{new_size}px"

            adjusted_config["spacing"] = spacing

            return adjusted_config

        except Exception as e:
            self._logger.warning(f"高DPI调整失败: {e}")
            return theme_config

    def _apply_macos_adjustments(self, theme_config: dict[str, Any]) -> dict[str, Any]:
        """应用macOS平台调整"""
        try:
            adjusted_config = theme_config.copy()

            # macOS使用系统字体
            fonts = adjusted_config.get("fonts", {}).copy()
            fonts["family"] = (
                "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
            )
            adjusted_config["fonts"] = fonts

            # 调整圆角半径以匹配macOS风格
            border_radius = adjusted_config.get("border_radius", {}).copy()
            border_radius["medium"] = "8px"
            border_radius["large"] = "12px"
            adjusted_config["border_radius"] = border_radius

            return adjusted_config

        except Exception as e:
            self._logger.warning(f"macOS调整失败: {e}")
            return theme_config

    def _apply_windows_adjustments(
        self, theme_config: dict[str, Any]
    ) -> dict[str, Any]:
        """应用Windows平台调整"""
        try:
            adjusted_config = theme_config.copy()

            # Windows使用Segoe UI字体
            fonts = adjusted_config.get("fonts", {}).copy()
            fonts["family"] = "Segoe UI, Microsoft YaHei UI, sans-serif"
            adjusted_config["fonts"] = fonts

            # Windows风格的圆角较小
            border_radius = adjusted_config.get("border_radius", {}).copy()
            border_radius["medium"] = "4px"
            border_radius["large"] = "6px"
            adjusted_config["border_radius"] = border_radius

            return adjusted_config

        except Exception as e:
            self._logger.warning(f"Windows调整失败: {e}")
            return theme_config

    def save_theme_preference(self, theme_id: str) -> None:
        """保存主题偏好到配置"""
        try:
            config = self._get_config()
            if config:
                from minicrm.core.config import ThemeMode

                # 将主题ID转换为ThemeMode
                if theme_id == "light":
                    theme_mode = ThemeMode.LIGHT
                elif theme_id == "dark":
                    theme_mode = ThemeMode.DARK
                else:
                    # 自定义主题暂时保存为light模式
                    theme_mode = ThemeMode.LIGHT

                config.set_theme_mode(theme_mode)
                self._logger.info(f"主题偏好已保存: {theme_id}")
            else:
                self._logger.warning("配置管理器不可用,无法保存主题偏好")

        except Exception as e:
            self._logger.error(f"保存主题偏好失败: {e}")

    def set_auto_theme_mode(self, enabled: bool) -> None:
        """设置自动主题模式"""
        try:
            config = self._get_config()
            if config:
                from minicrm.core.config import ThemeMode

                if enabled:
                    config.set_theme_mode(ThemeMode.AUTO)
                    # 立即应用系统主题
                    system_theme = self._detect_system_theme()
                    self.set_theme(system_theme)
                else:
                    # 保存当前主题为手动模式
                    current_mode = (
                        ThemeMode.LIGHT
                        if self._current_theme == "light"
                        else ThemeMode.DARK
                    )
                    config.set_theme_mode(current_mode)

                self._logger.info(f"自动主题模式: {'启用' if enabled else '禁用'}")
            else:
                self._logger.warning("配置管理器不可用,无法设置自动主题模式")

        except Exception as e:
            self._logger.error(f"设置自动主题模式失败: {e}")

    def is_auto_theme_enabled(self) -> bool:
        """检查是否启用了自动主题模式"""
        try:
            config = self._get_config()
            if config:
                from minicrm.core.config import ThemeMode

                return config.get_theme_mode() == ThemeMode.AUTO
            return False
        except Exception:
            return False

    def get_platform_info(self) -> dict[str, Any]:
        """获取平台信息"""
        return {
            "platform": self._platform,
            "is_high_dpi": self._is_high_dpi,
            "system_theme": self._detect_system_theme()
            if self._platform in ["windows", "darwin"]
            else "unknown",
        }

    def get_component_styler(self):
        """获取组件样式应用器"""
        try:
            from ..component_styler import ComponentStyler
            from ..styles import create_style_system

            # 获取当前主题配置
            theme_config = self.get_theme_config()
            adjusted_config = self._apply_platform_adjustments(theme_config)

            # 创建样式系统
            style_tokens, style_generator = create_style_system(adjusted_config)

            # 创建组件样式应用器
            return ComponentStyler(style_tokens, style_generator)

        except ImportError as e:
            self._logger.warning(f"无法创建组件样式应用器: {e}")
            return None

    def add_theme_changed_callback(self, callback: Callable[[str], None]) -> None:
        """添加主题变化回调函数

        Args:
            callback: 回调函数,接收主题ID参数
        """
        if callback not in self._theme_changed_callbacks:
            self._theme_changed_callbacks.append(callback)

    def remove_theme_changed_callback(self, callback: Callable[[str], None]) -> None:
        """移除主题变化回调函数

        Args:
            callback: 要移除的回调函数
        """
        if callback in self._theme_changed_callbacks:
            self._theme_changed_callbacks.remove(callback)

    def _trigger_theme_changed_callbacks(self, theme_id: str) -> None:
        """触发主题变化回调

        Args:
            theme_id: 主题ID
        """
        for callback in self._theme_changed_callbacks:
            try:
                callback(theme_id)
            except Exception as e:
                self._logger.error(f"主题变化回调执行失败: {e}")

    @classmethod
    def get_instance(cls) -> "ThemeManager":
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
