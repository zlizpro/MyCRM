"""
MiniCRM 主题导入导出管理器

负责主题配置的导入和导出
"""

import json
import logging
from pathlib import Path
from typing import Any


class ThemeIOManager:
    """主题导入导出管理器"""

    def __init__(self):
        """初始化主题IO管理器"""
        self._logger = logging.getLogger(__name__)

    def export_theme(self, theme_config: dict[str, Any], file_path: str) -> bool:
        """
        导出主题配置

        Args:
            theme_config: 主题配置
            file_path: 导出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            # 验证主题配置
            if not self._validate_theme_config(theme_config):
                self._logger.error("主题配置验证失败")
                return False

            # 确保目录存在
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(theme_config, f, indent=2, ensure_ascii=False)

            self._logger.info(f"主题导出成功: {file_path}")
            return True

        except Exception as e:
            self._logger.error(f"主题导出失败: {e}")
            return False

    def import_theme(self, file_path: str) -> dict[str, Any] | None:
        """
        导入主题配置

        Args:
            file_path: 导入文件路径

        Returns:
            dict | None: 主题配置，失败时返回None
        """
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                self._logger.error(f"主题文件不存在: {file_path}")
                return None

            # 读取文件
            with open(file_path, encoding="utf-8") as f:
                theme_config = json.load(f)

            # 验证主题配置
            if not self._validate_theme_config(theme_config):
                self._logger.error("导入的主题配置验证失败")
                return None

            self._logger.info(f"主题导入成功: {file_path}")
            return theme_config

        except json.JSONDecodeError as e:
            self._logger.error(f"主题文件格式错误: {e}")
            return None
        except Exception as e:
            self._logger.error(f"主题导入失败: {e}")
            return None

    def _validate_theme_config(self, config: dict[str, Any]) -> bool:
        """验证主题配置"""
        try:
            required_keys = ["name", "colors", "fonts", "spacing", "border_radius"]

            # 检查必需的顶级键
            for key in required_keys:
                if key not in config:
                    self._logger.error(f"主题配置缺少必需键: {key}")
                    return False

            # 验证颜色配置
            colors = config.get("colors", {})
            required_colors = ["primary", "background", "text_primary", "border"]
            for color_key in required_colors:
                if color_key not in colors:
                    self._logger.error(f"主题配置缺少必需颜色: {color_key}")
                    return False

            # 验证字体配置
            fonts = config.get("fonts", {})
            required_fonts = ["family", "size_normal"]
            for font_key in required_fonts:
                if font_key not in fonts:
                    self._logger.error(f"主题配置缺少必需字体: {font_key}")
                    return False

            return True

        except Exception as e:
            self._logger.error(f"主题配置验证失败: {e}")
            return False

    def create_theme_template(self) -> dict[str, Any]:
        """创建主题模板"""
        return {
            "name": "自定义主题",
            "colors": {
                "primary": "#007BFF",
                "secondary": "#6C757D",
                "success": "#28A745",
                "warning": "#FFC107",
                "danger": "#DC3545",
                "info": "#17A2B8",
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "card": "#FFFFFF",
                "text_primary": "#212529",
                "text_secondary": "#6C757D",
                "text_muted": "#ADB5BD",
                "border": "#DEE2E6",
                "border_light": "#E9ECEF",
                "border_dark": "#CED4DA",
                "hover": "#F8F9FA",
                "active": "#E9ECEF",
                "focus": "#80BDFF",
                "disabled": "#E9ECEF",
            },
            "fonts": {
                "family": "Microsoft YaHei UI, Arial, sans-serif",
                "size_small": "12px",
                "size_normal": "14px",
                "size_large": "16px",
                "size_heading": "18px",
                "weight_normal": "400",
                "weight_bold": "600",
            },
            "spacing": {
                "xs": "4px",
                "sm": "8px",
                "md": "16px",
                "lg": "24px",
                "xl": "32px",
            },
            "border_radius": {
                "small": "4px",
                "medium": "6px",
                "large": "8px",
                "round": "50%",
            },
        }
