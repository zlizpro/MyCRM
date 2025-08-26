"""MiniCRM 应用程序配置管理 - TTK版本

负责管理应用程序的所有配置项,包括:
- 数据库配置
- UI主题配置
- 日志配置
- 文件路径配置
- 用户偏好设置

TTK版本特点:
- 使用JSON文件替代Qt的QSettings
- 使用Python标准库获取系统路径
- 完全兼容tkinter/ttk环境
"""

from dataclasses import asdict, dataclass
from enum import Enum
import json
import logging
import os
from pathlib import Path
import platform
from typing import Any


class ThemeMode(Enum):
    """主题模式枚举"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # 跟随系统


@dataclass
class DatabaseConfig:
    """数据库配置"""

    path: str = "minicrm.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backup_files: int = 7


@dataclass
class UIConfig:
    """用户界面配置"""

    theme_mode: ThemeMode = ThemeMode.LIGHT
    window_width: int = 1280
    window_height: int = 800
    window_maximized: bool = False
    sidebar_width: int = 250
    font_family: str = "Microsoft YaHei UI"
    font_size: int = 9


@dataclass
class LoggingConfig:
    """日志配置"""

    level: str = "INFO"
    file_enabled: bool = True
    console_enabled: bool = True
    max_file_size_mb: int = 10
    backup_count: int = 5


def get_app_data_directory() -> Path:
    """获取应用程序数据目录 - 替代Qt的QStandardPaths

    Returns:
        Path: 应用程序数据目录路径
    """
    system = platform.system()
    home = Path.home()

    if system == "Windows":
        # Windows: %APPDATA%/MiniCRM
        app_data = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        return app_data / "MiniCRM"
    if system == "Darwin":  # macOS
        # macOS: ~/Library/Application Support/MiniCRM
        return home / "Library" / "Application Support" / "MiniCRM"
    # Linux and other Unix-like systems
    # Linux: ~/.local/share/MiniCRM
    data_home = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    return data_home / "MiniCRM"


class AppConfigTTK:
    """应用程序配置管理器 - TTK版本

    负责加载、保存和管理应用程序的所有配置项.
    配置数据存储在用户的应用程序数据目录中.
    """

    def __init__(self):
        """初始化配置管理器"""
        self._logger = logging.getLogger(__name__)

        # 获取应用程序数据目录
        self._app_data_dir = get_app_data_directory()
        self._app_data_dir.mkdir(parents=True, exist_ok=True)

        # 配置文件路径
        self._config_file = self._app_data_dir / "config.json"
        self._qt_settings_file = self._app_data_dir / "qt_settings.json"

        # 初始化配置对象
        self._database_config = DatabaseConfig()
        self._ui_config = UIConfig()
        self._logging_config = LoggingConfig()

        # Qt设置替代存储
        self._qt_settings: dict[str, Any] = {}

        # 加载配置
        self._load_config()
        self._load_qt_settings()

    def _load_config(self) -> None:
        """从配置文件加载配置

        如果配置文件不存在或损坏,将使用默认配置.
        """
        try:
            if self._config_file.exists():
                with open(self._config_file, encoding="utf-8") as f:
                    config_data = json.load(f)

                # 加载数据库配置
                if "database" in config_data:
                    db_data = config_data["database"]
                    self._database_config = DatabaseConfig(**db_data)

                # 加载UI配置
                if "ui" in config_data:
                    ui_data = config_data["ui"]
                    # 处理主题模式枚举
                    if "theme_mode" in ui_data:
                        ui_data["theme_mode"] = ThemeMode(ui_data["theme_mode"])
                    self._ui_config = UIConfig(**ui_data)

                # 加载日志配置
                if "logging" in config_data:
                    log_data = config_data["logging"]
                    self._logging_config = LoggingConfig(**log_data)

                self._logger.info("配置文件加载成功")
            else:
                self._logger.info("配置文件不存在,使用默认配置")
                self._save_config()  # 保存默认配置

        except Exception as e:
            self._logger.warning(f"配置文件加载失败,使用默认配置: {e}")
            # 使用默认配置
            self._database_config = DatabaseConfig()
            self._ui_config = UIConfig()
            self._logging_config = LoggingConfig()

    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            config_data = {
                "database": asdict(self._database_config),
                "ui": asdict(self._ui_config),
                "logging": asdict(self._logging_config),
            }

            # 处理枚举类型
            config_data["ui"]["theme_mode"] = self._ui_config.theme_mode.value

            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self._logger.debug("配置文件保存成功")

        except Exception as e:
            self._logger.error(f"配置文件保存失败: {e}")

    def _load_qt_settings(self) -> None:
        """加载Qt设置替代存储"""
        try:
            if self._qt_settings_file.exists():
                with open(self._qt_settings_file, encoding="utf-8") as f:
                    self._qt_settings = json.load(f)
                self._logger.debug("Qt设置加载成功")
        except Exception as e:
            self._logger.warning(f"Qt设置加载失败: {e}")
            self._qt_settings = {}

    def _save_qt_settings(self) -> None:
        """保存Qt设置替代存储"""
        try:
            with open(self._qt_settings_file, "w", encoding="utf-8") as f:
                json.dump(self._qt_settings, f, indent=2, ensure_ascii=False)
            self._logger.debug("Qt设置保存成功")
        except Exception as e:
            self._logger.error(f"Qt设置保存失败: {e}")

    def save(self) -> None:
        """保存当前配置"""
        self._save_config()
        self._save_qt_settings()

    # 数据库配置访问器
    @property
    def database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self._database_config

    def get_database_path(self) -> Path:
        """获取数据库文件路径"""
        if Path(self._database_config.path).is_absolute():
            return Path(self._database_config.path)
        return self._app_data_dir / self._database_config.path

    def set_database_path(self, path: str | Path) -> None:
        """设置数据库文件路径"""
        self._database_config.path = str(path)
        self._save_config()

    # UI配置访问器
    @property
    def ui_config(self) -> UIConfig:
        """获取UI配置"""
        return self._ui_config

    def get_theme_mode(self) -> ThemeMode:
        """获取主题模式"""
        return self._ui_config.theme_mode

    def set_theme_mode(self, mode: ThemeMode) -> None:
        """设置主题模式"""
        self._ui_config.theme_mode = mode
        self._save_config()

    def get_window_geometry(self) -> dict[str, int]:
        """获取窗口几何信息"""
        return {
            "width": self._ui_config.window_width,
            "height": self._ui_config.window_height,
            "maximized": self._ui_config.window_maximized,
        }

    def set_window_geometry(
        self, width: int, height: int, maximized: bool = False
    ) -> None:
        """设置窗口几何信息"""
        self._ui_config.window_width = width
        self._ui_config.window_height = height
        self._ui_config.window_maximized = maximized
        self._save_config()

    def get_sidebar_width(self) -> int:
        """获取侧边栏宽度"""
        return self._ui_config.sidebar_width

    def set_sidebar_width(self, width: int) -> None:
        """设置侧边栏宽度"""
        self._ui_config.sidebar_width = width
        self._save_config()

    # 日志配置访问器
    @property
    def logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        return self._logging_config

    def get_log_level(self) -> str:
        """获取日志级别"""
        return self._logging_config.level

    def set_log_level(self, level: str) -> None:
        """设置日志级别"""
        self._logging_config.level = level
        self._save_config()

    # 应用程序目录访问器
    @property
    def app_data_dir(self) -> Path:
        """获取应用程序数据目录"""
        return self._app_data_dir

    def get_logs_dir(self) -> Path:
        """获取日志目录"""
        logs_dir = self._app_data_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir

    def get_backups_dir(self) -> Path:
        """获取备份目录"""
        backups_dir = self._app_data_dir / "backups"
        backups_dir.mkdir(exist_ok=True)
        return backups_dir

    def get_templates_dir(self) -> Path:
        """获取模板目录"""
        templates_dir = self._app_data_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        return templates_dir

    # Qt设置访问器(用于窗口状态等)- 使用JSON文件替代
    def get_qt_setting(self, key: str, default_value: Any = None) -> Any:
        """获取Qt设置值"""
        return self._qt_settings.get(key, default_value)

    def set_qt_setting(self, key: str, value: Any) -> None:
        """设置Qt设置值"""
        self._qt_settings[key] = value
        self._save_qt_settings()

    def remove_qt_setting(self, key: str) -> None:
        """删除Qt设置值"""
        if key in self._qt_settings:
            del self._qt_settings[key]
            self._save_qt_settings()

    def clear_qt_settings(self) -> None:
        """清空所有Qt设置"""
        self._qt_settings.clear()
        self._save_qt_settings()

    def get_all_qt_settings(self) -> dict[str, Any]:
        """获取所有Qt设置"""
        return self._qt_settings.copy()

    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return f"AppConfig(database={self._database_config}, ui={self._ui_config}, logging={self._logging_config})"


# 为了兼容性,创建一个别名
AppConfig = AppConfigTTK
