"""
MiniCRM 设置管理服务

负责系统设置的读取、保存、验证和管理,包括:
- 用户偏好设置
- 主题和界面设置
- 系统配置管理
- 设置的导入导出
"""

import json
from pathlib import Path
from typing import Any

from ..core import BusinessLogicError, ValidationError
from ..core.interfaces.service_interfaces import ISettingsService
from ..services.base_service import BaseService


class SettingsService(BaseService, ISettingsService):
    """
    设置管理服务

    提供系统设置的完整管理功能,包括读取、保存、验证和重置.
    """

    def __init__(self):
        """初始化设置服务"""
        super().__init__()
        self._settings_file = self._get_settings_file_path()
        self._default_settings = self._get_default_settings()
        self._current_settings: dict[str, Any] = {}
        self._load_settings()

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SettingsService"

    def _get_settings_file_path(self) -> Path:
        """
        获取设置文件路径

        Returns:
            Path: 设置文件路径
        """
        # 获取用户数据目录
        data_dir = Path.home() / "Library" / "Application Support" / "MiniCRM"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / "settings.json"

    def _get_default_settings(self) -> dict[str, Any]:
        """
        获取默认设置

        Returns:
            Dict[str, Any]: 默认设置字典
        """
        return {
            "general": {
                "language": "zh_CN",
                "startup_page": "dashboard",
                "auto_save_interval": 300,  # 秒
                "data_refresh_interval": 60,  # 秒
                "confirm_delete": True,
                "show_tooltips": True,
            },
            "theme": {
                "theme_name": "light",
                "font_size": 9,
                "font_family": "Microsoft YaHei UI",
                "window_opacity": 1.0,
                "enable_animations": True,
            },
            "database": {
                "auto_backup": True,
                "backup_interval": "daily",  # daily, weekly, monthly
                "max_backups": 10,
                "backup_location": str(
                    Path.home()
                    / "Library"
                    / "Application Support"
                    / "MiniCRM"
                    / "backups"
                ),
                "compress_backups": True,
            },
            "system": {
                "log_level": "INFO",
                "enable_performance_monitoring": True,
                "cache_size": 100,
                "max_log_files": 5,
                "enable_crash_reporting": True,
            },
            "ui": {
                "window_width": 1280,
                "window_height": 800,
                "window_maximized": False,
                "sidebar_width": 200,
                "show_status_bar": True,
                "toolbar_style": "icons_and_text",
            },
        }

    def _load_settings(self) -> None:
        """加载设置文件"""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, encoding="utf-8") as f:
                    loaded_settings = json.load(f)

                # 合并默认设置和加载的设置
                self._current_settings = self._merge_settings(
                    self._default_settings, loaded_settings
                )
                self._logger.info("设置文件加载成功")
            else:
                # 使用默认设置
                self._current_settings = self._default_settings.copy()
                self._save_settings()
                self._logger.info("创建默认设置文件")

        except Exception as e:
            self._logger.error(f"加载设置文件失败: {e}")
            self._current_settings = self._default_settings.copy()

    def _merge_settings(
        self, default: dict[str, Any], loaded: dict[str, Any]
    ) -> dict[str, Any]:
        """
        合并默认设置和加载的设置

        Args:
            default: 默认设置
            loaded: 加载的设置

        Returns:
            Dict[str, Any]: 合并后的设置
        """
        result = default.copy()

        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    def _save_settings(self) -> None:
        """保存设置到文件"""
        try:
            # 确保目录存在
            self._settings_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self._current_settings, f, indent=2, ensure_ascii=False)

            self._logger.info("设置保存成功")

        except Exception as e:
            self._logger.error(f"保存设置失败: {e}")
            raise BusinessLogicError(f"保存设置失败: {e}") from e

    def get_setting(self, category: str, key: str | None = None) -> Any:
        """
        获取设置值

        Args:
            category: 设置分类
            key: 设置键,如果为None则返回整个分类

        Returns:
            Any: 设置值

        Raises:
            ValidationError: 当分类或键不存在时
        """
        if category not in self._current_settings:
            raise ValidationError(f"设置分类不存在: {category}")

        if key is None:
            return self._current_settings[category].copy()

        if key not in self._current_settings[category]:
            raise ValidationError(f"设置键不存在: {category}.{key}")

        return self._current_settings[category][key]

    def set_setting(self, category: str, key: str, value: Any) -> None:
        """
        设置值

        Args:
            category: 设置分类
            key: 设置键
            value: 设置值

        Raises:
            ValidationError: 当设置验证失败时
        """
        # 验证设置
        self._validate_setting(category, key, value)

        # 确保分类存在
        if category not in self._current_settings:
            self._current_settings[category] = {}

        # 设置值
        old_value = self._current_settings[category].get(key)
        self._current_settings[category][key] = value

        # 保存设置
        try:
            self._save_settings()
            self._logger.info(f"设置更新: {category}.{key} = {value}")
        except Exception:
            # 回滚更改
            if old_value is not None:
                self._current_settings[category][key] = old_value
            else:
                del self._current_settings[category][key]
            raise

    def update_settings(self, category: str, settings: dict[str, Any]) -> None:
        """
        批量更新设置

        Args:
            category: 设置分类
            settings: 设置字典

        Raises:
            ValidationError: 当设置验证失败时
        """
        # 验证所有设置
        for key, value in settings.items():
            self._validate_setting(category, key, value)

        # 确保分类存在
        if category not in self._current_settings:
            self._current_settings[category] = {}

        # 备份当前设置
        old_settings = self._current_settings[category].copy()

        try:
            # 更新设置
            self._current_settings[category].update(settings)

            # 保存设置
            self._save_settings()
            self._logger.info(f"批量更新设置: {category}")

        except Exception:
            # 回滚更改
            self._current_settings[category] = old_settings
            raise

    def _validate_setting(self, category: str, key: str, value: Any) -> None:
        """
        验证设置值

        Args:
            category: 设置分类
            key: 设置键
            value: 设置值

        Raises:
            ValidationError: 当设置值无效时
        """
        # 通用验证规则
        validation_rules = {
            "general": {
                "language": lambda v: v in ["zh_CN", "en_US"],
                "startup_page": lambda v: v
                in ["dashboard", "customers", "suppliers", "finance"],
                "auto_save_interval": lambda v: isinstance(v, int) and 30 <= v <= 3600,
                "data_refresh_interval": lambda v: isinstance(v, int)
                and 10 <= v <= 300,
                "confirm_delete": lambda v: isinstance(v, bool),
                "show_tooltips": lambda v: isinstance(v, bool),
            },
            "theme": {
                "theme_name": lambda v: v in ["light", "dark"],
                "font_size": lambda v: isinstance(v, int) and 8 <= v <= 16,
                "font_family": lambda v: isinstance(v, str) and len(v) > 0,
                "window_opacity": lambda v: isinstance(v, int | float)
                and 0.5 <= v <= 1.0,
                "enable_animations": lambda v: isinstance(v, bool),
            },
            "database": {
                "auto_backup": lambda v: isinstance(v, bool),
                "backup_interval": lambda v: v in ["daily", "weekly", "monthly"],
                "max_backups": lambda v: isinstance(v, int) and 1 <= v <= 100,
                "backup_location": lambda v: isinstance(v, str) and len(v) > 0,
                "compress_backups": lambda v: isinstance(v, bool),
            },
            "system": {
                "log_level": lambda v: v in ["DEBUG", "INFO", "WARNING", "ERROR"],
                "enable_performance_monitoring": lambda v: isinstance(v, bool),
                "cache_size": lambda v: isinstance(v, int) and 10 <= v <= 1000,
                "max_log_files": lambda v: isinstance(v, int) and 1 <= v <= 20,
                "enable_crash_reporting": lambda v: isinstance(v, bool),
            },
            "ui": {
                "window_width": lambda v: isinstance(v, int) and 800 <= v <= 3840,
                "window_height": lambda v: isinstance(v, int) and 600 <= v <= 2160,
                "window_maximized": lambda v: isinstance(v, bool),
                "sidebar_width": lambda v: isinstance(v, int) and 150 <= v <= 400,
                "show_status_bar": lambda v: isinstance(v, bool),
                "toolbar_style": lambda v: v
                in ["icons_only", "text_only", "icons_and_text"],
            },
        }

        if category in validation_rules and key in validation_rules[category]:
            validator = validation_rules[category][key]
            if not validator(value):
                raise ValidationError(f"设置值无效: {category}.{key} = {value}")

    def reset_settings(self, category: str | None = None) -> None:
        """
        重置设置到默认值

        Args:
            category: 要重置的分类,如果为None则重置所有设置
        """
        if category is None:
            # 重置所有设置
            self._current_settings = self._default_settings.copy()
            self._logger.info("重置所有设置到默认值")
        else:
            # 重置指定分类
            if category in self._default_settings:
                self._current_settings[category] = self._default_settings[
                    category
                ].copy()
                self._logger.info(f"重置设置分类到默认值: {category}")
            else:
                raise ValidationError(f"设置分类不存在: {category}")

        # 保存设置
        self._save_settings()

    def export_settings(self, file_path: str) -> None:
        """
        导出设置到文件

        Args:
            file_path: 导出文件路径

        Raises:
            BusinessLogicError: 当导出失败时
        """
        try:
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(self._current_settings, f, indent=2, ensure_ascii=False)

            self._logger.info(f"设置导出成功: {file_path}")

        except Exception as e:
            self._logger.error(f"导出设置失败: {e}")
            raise BusinessLogicError(f"导出设置失败: {e}") from e

    def import_settings(self, file_path: str, merge: bool = True) -> None:
        """
        从文件导入设置

        Args:
            file_path: 导入文件路径
            merge: 是否与现有设置合并,False则完全替换

        Raises:
            ValidationError: 当文件不存在或格式错误时
            BusinessLogicError: 当导入失败时
        """
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                raise ValidationError(f"设置文件不存在: {file_path}")

            with open(import_path, encoding="utf-8") as f:
                imported_settings = json.load(f)

            # 验证导入的设置
            self._validate_imported_settings(imported_settings)

            # 备份当前设置
            backup_settings = self._current_settings.copy()

            try:
                if merge:
                    # 合并设置
                    self._current_settings = self._merge_settings(
                        self._current_settings, imported_settings
                    )
                else:
                    # 完全替换
                    self._current_settings = self._merge_settings(
                        self._default_settings, imported_settings
                    )

                # 保存设置
                self._save_settings()
                self._logger.info(f"设置导入成功: {file_path}")

            except Exception as e:
                # 回滚设置
                self._current_settings = backup_settings
                raise BusinessLogicError(f"导入设置失败: {e}") from e

        except json.JSONDecodeError as e:
            raise ValidationError(f"设置文件格式错误: {e}") from e
        except Exception as e:
            self._logger.error(f"导入设置失败: {e}")
            raise BusinessLogicError(f"导入设置失败: {e}") from e

    def _validate_imported_settings(self, settings: dict[str, Any]) -> None:
        """
        验证导入的设置

        Args:
            settings: 导入的设置字典

        Raises:
            ValidationError: 当设置格式错误时
        """
        if not isinstance(settings, dict):
            raise ValidationError("设置文件格式错误:根对象必须是字典")

        # 验证每个设置项
        for category, category_settings in settings.items():
            if not isinstance(category_settings, dict):
                continue

            for key, value in category_settings.items():
                try:
                    self._validate_setting(category, key, value)
                except ValidationError as e:
                    self._logger.warning(f"跳过无效设置: {e}")

    def get_all_settings(self) -> dict[str, Any]:
        """
        获取所有设置

        Returns:
            Dict[str, Any]: 所有设置的副本
        """
        return self._current_settings.copy()

    def get_settings_info(self) -> dict[str, Any]:
        """
        获取设置信息

        Returns:
            Dict[str, Any]: 设置信息
        """
        return {
            "settings_file": str(self._settings_file),
            "file_exists": self._settings_file.exists(),
            "categories": list(self._current_settings.keys()),
            "total_settings": sum(len(cat) for cat in self._current_settings.values()),
            "file_size": self._settings_file.stat().st_size
            if self._settings_file.exists()
            else 0,
        }
