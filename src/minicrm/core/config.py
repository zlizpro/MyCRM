"""MiniCRM 应用程序配置管理

负责管理应用程序的所有配置项,包括:
- 数据库配置
- UI主题配置
- 日志配置
- 文件路径配置
- 用户偏好设置
"""

from dataclasses import asdict, dataclass
from enum import Enum
import json
import logging
from pathlib import Path
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


class AppConfig:
    """应用程序配置管理器

    负责加载、保存和管理应用程序的所有配置项.
    配置数据存储在用户的应用程序数据目录中.
    """

    def __init__(self):
        """初始化配置管理器"""
        self._logger = logging.getLogger(__name__)

        # 获取应用程序数据目录
        self._app_data_dir = self._get_app_data_dir()
        self._app_data_dir.mkdir(parents=True, exist_ok=True)

        # 设置存储文件
        self._settings_file = self._app_data_dir / "settings.json"
        self._settings_data = {}

        # 配置文件路径
        self._config_file = self._app_data_dir / "config.json"

        # 初始化配置对象
        self._database_config = DatabaseConfig()
        self._ui_config = UIConfig()
        self._logging_config = LoggingConfig()

        # 加载配置
        self._load_config()
        self._load_settings()

    def _get_app_data_dir(self) -> Path:
        """获取应用程序数据目录 - 替代Qt的QStandardPaths"""
        system = platform.system()

        if system == "Windows":
            # Windows: %APPDATA%/MiniCRM
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
            return Path(base_dir) / "MiniCRM"
        if system == "Darwin":
            # macOS: ~/Library/Application Support/MiniCRM
            return Path.home() / "Library" / "Application Support" / "MiniCRM"
        # Linux/Unix: ~/.local/share/MiniCRM
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            return Path(xdg_data_home) / "MiniCRM"
        return Path.home() / ".local" / "share" / "MiniCRM"

    def _load_settings(self) -> None:
        """加载设置数据"""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, encoding="utf-8") as f:
                    self._settings_data = json.load(f)
                self._logger.debug("设置文件加载成功")
            else:
                self._settings_data = {}
                self._logger.debug("设置文件不存在,使用空设置")
        except Exception as e:
            self._logger.warning(f"设置文件加载失败: {e}")
            self._settings_data = {}

    def _save_settings(self) -> None:
        """保存设置数据"""
        try:
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings_data, f, indent=2, ensure_ascii=False)
            self._logger.debug("设置文件保存成功")
        except Exception as e:
            self._logger.error(f"设置文件保存失败: {e}")

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

    def save(self) -> None:
        """保存当前配置"""
        self._save_config()

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

    # 设置访问器(替代Qt设置)
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """获取设置值"""
        return self._settings_data.get(key, default_value)

    def set_setting(self, key: str, value: Any) -> None:
        """设置设置值"""
        self._settings_data[key] = value
        self._save_settings()

    def __str__(self) -> str:
        """返回配置的字符串表示"""
        return f"AppConfig(database={self._database_config}, ui={self._ui_config}, logging={self._logging_config})"
