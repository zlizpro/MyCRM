"""MiniCRM配置管理系统.

提供完整的配置管理功能, 包括:
- 配置文件的读取和写入
- 配置验证和默认值设置
- 配置更新和合并
- 跨平台兼容性支持

配置系统采用分层设计:
- 默认配置: 系统内置的默认设置
- 用户配置: 用户自定义的配置文件
- 运行时配置: 程序运行时的动态配置
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
import json
import logging
from pathlib import Path
from typing import Any, Union

from minicrm.core.constants import APP_DATA_DIR, CONFIG_DIR, DEFAULT_CONFIG
from minicrm.core.exceptions import ConfigurationError, ValidationError
from minicrm.core.utils import ensure_directory_exists, safe_int, safe_str


logger = logging.getLogger(__name__)


@dataclass
class ApplicationConfig:
    """应用程序基本配置.

    包含应用程序的基本信息和全局设置.
    """

    name: str = "MiniCRM"
    version: str = "1.0.0"
    description: str = "跨平台客户关系管理系统"
    author: str = "MiniCRM开发团队"
    debug: bool = False
    auto_save: bool = True
    auto_backup: bool = True
    language: str = "zh_CN"

    def validate(self) -> None:
        """验证应用配置."""
        if not self.name or not isinstance(self.name, str):
            msg = "应用名称不能为空"
            raise ValidationError(msg)

        if not self.version or not isinstance(self.version, str):
            msg = "版本号不能为空"
            raise ValidationError(msg)


@dataclass
class DatabaseConfig:
    """数据库配置.

    包含数据库连接、性能优化和备份相关的配置.
    """

    name: str = "minicrm.db"
    path: str = str(APP_DATA_DIR / "minicrm.db")
    backup_interval: int = 24  # 小时
    max_backups: int = 30
    connection_timeout: int = 30  # 秒
    enable_wal: bool = True
    cache_size: int = 64000  # KB
    auto_vacuum: bool = True

    # SQLite Pragma设置
    pragma_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "journal_mode": "WAL",
            "synchronous": "NORMAL",
            "cache_size": -64000,  # 64MB
            "temp_store": "MEMORY",
            "mmap_size": 268435456,  # 256MB
        }
    )

    def validate(self) -> None:
        """验证数据库配置."""
        if not self.name or not isinstance(self.name, str):
            msg = "数据库名称不能为空"
            raise ValidationError(msg)

        if self.backup_interval <= 0:
            msg = "备份间隔必须大于0"
            raise ValidationError(msg)

        if self.max_backups <= 0:
            msg = "最大备份数量必须大于0"
            raise ValidationError(msg)

        if self.connection_timeout <= 0:
            msg = "连接超时时间必须大于0"
            raise ValidationError(msg)

    def get_full_path(self) -> Path:
        """获取数据库完整路径."""
        return Path(self.path)

    def ensure_directory(self) -> None:
        """确保数据库目录存在."""
        db_path = self.get_full_path()
        ensure_directory_exists(db_path.parent)


@dataclass
class UIConfig:
    """用户界面配置.

    包含窗口大小、主题、字体、颜色等UI相关配置.
    """

    # 窗口配置
    min_width: int = 1024
    min_height: int = 768
    default_width: int = 1280
    default_height: int = 800
    remember_window_state: bool = True

    # 主题配置
    theme: str = "light"
    available_themes: list[str] = field(default_factory=lambda: ["light", "dark"])

    # 字体配置
    default_font_family: str = "Microsoft YaHei UI"
    default_font_size: int = 9
    heading_font_size: int = 12
    small_font_size: int = 8
    monospace_font_family: str = "Consolas"

    # 分页配置
    default_page_size: int = 50
    page_size_options: list[int] = field(default_factory=lambda: [25, 50, 100, 200])

    # 界面行为配置
    auto_refresh_interval: int = 300  # 秒
    show_tooltips: bool = True
    enable_animations: bool = True
    confirm_delete: bool = True

    def validate(self) -> None:
        """验证UI配置."""
        if self.min_width <= 0 or self.min_height <= 0:
            msg = "窗口最小尺寸必须大于0"
            raise ValidationError(msg)

        if self.default_width < self.min_width or self.default_height < self.min_height:
            msg = "默认窗口尺寸不能小于最小尺寸"
            raise ValidationError(msg)

        if self.theme not in self.available_themes:
            msg = f"主题 '{self.theme}' 不在可用主题列表中"
            raise ValidationError(msg)

        if self.default_font_size <= 0:
            msg = "字体大小必须大于0"
            raise ValidationError(msg)

        if self.default_page_size not in self.page_size_options:
            msg = "默认分页大小必须在可选项中"
            raise ValidationError(msg)


@dataclass
class LoggingConfig:
    """日志配置.

    包含日志级别、格式、文件管理等配置.
    """

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    encoding: str = "utf-8"
    log_to_file: bool = True
    log_to_console: bool = True

    def validate(self) -> None:
        """验证日志配置."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level not in valid_levels:
            msg = f"日志级别必须是: {', '.join(valid_levels)}"
            raise ValidationError(msg)

        if self.max_file_size <= 0:
            msg = "日志文件最大大小必须大于0"
            raise ValidationError(msg)

        if self.backup_count < 0:
            msg = "备份文件数量不能为负数"
            raise ValidationError(msg)


@dataclass
class ValidationConfig:
    """数据验证配置.

    包含各种数据验证规则和限制.
    """

    phone_pattern: str = r"^1[3-9]\d{9}$"
    email_pattern: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    max_text_length: int = 1000
    max_name_length: int = 100
    max_phone_length: int = 20
    max_email_length: int = 100
    currency_precision: int = 2

    def validate(self) -> None:
        """验证数据验证配置."""
        if self.max_text_length <= 0:
            msg = "最大文本长度必须大于0"
            raise ValidationError(msg)

        if self.max_name_length <= 0:
            msg = "最大姓名长度必须大于0"
            raise ValidationError(msg)

        if self.currency_precision < 0:
            msg = "货币精度不能为负数"
            raise ValidationError(msg)


@dataclass
class BusinessConfig:
    """业务规则配置.

    包含客户、供应商、报价、合同等业务相关的配置.
    """

    # 客户相关配置
    customer_default_level: str = "normal"
    customer_max_credit_limit: float = 10000000.0  # 1000万
    customer_credit_check_threshold: float = 100000.0  # 10万

    # 供应商相关配置
    supplier_default_level: str = "normal"
    supplier_max_payment_days: int = 180
    supplier_quality_score_min: int = 0
    supplier_quality_score_max: int = 100

    # 报价相关配置
    quote_default_validity_days: int = 30
    quote_max_validity_days: int = 365
    quote_auto_expire_check_interval: int = 24  # 小时

    # 合同相关配置
    contract_default_duration_months: int = 12
    contract_max_duration_months: int = 60
    contract_renewal_notice_days: int = 30

    def validate(self) -> None:
        """验证业务配置."""
        if self.customer_max_credit_limit <= 0:
            msg = "客户最大信用额度必须大于0"
            raise ValidationError(msg)

        if self.supplier_max_payment_days <= 0:
            msg = "供应商最大付款天数必须大于0"
            raise ValidationError(msg)

        if self.quote_default_validity_days <= 0:
            msg = "报价默认有效期必须大于0"
            raise ValidationError(msg)

        if self.contract_default_duration_months <= 0:
            msg = "合同默认期限必须大于0"
            raise ValidationError(msg)


@dataclass
class DocumentConfig:
    """文档配置.

    包含文档模板、导出格式、文件大小限制等配置.
    """

    # 模板文件配置
    quote_template: str = "quote_template.docx"
    contract_template: str = "contract_template.docx"
    invoice_template: str = "invoice_template.docx"

    # 导出格式配置
    export_formats: list[str] = field(default_factory=lambda: ["pdf", "docx", "xlsx"])
    default_export_format: str = "pdf"

    # 文件大小限制
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    max_template_size: int = 10 * 1024 * 1024  # 10MB

    # 允许的文件扩展名
    allowed_extensions: list[str] = field(
        default_factory=lambda: [".docx", ".xlsx", ".pdf", ".csv"]
    )

    def validate(self) -> None:
        """验证文档配置."""
        if self.default_export_format not in self.export_formats:
            msg = "默认导出格式必须在支持的格式列表中"
            raise ValidationError(msg)

        if self.max_file_size <= 0:
            msg = "最大文件大小必须大于0"
            raise ValidationError(msg)

        if self.max_template_size <= 0:
            msg = "最大模板大小必须大于0"
            raise ValidationError(msg)


class ConfigManager:
    """配置管理器.

    负责配置的加载、保存、验证和管理.
    支持默认配置和用户自定义配置的合并.
    """

    def __init__(self, config_file: str | None = None):
        """初始化配置管理器.

        Args:
            config_file: 配置文件路径, 默认使用标准路径
        """
        self.config_file = (
            Path(config_file) if config_file else CONFIG_DIR / "config.json"
        )
        self._config_data: dict[str, Any] = {}
        self._is_loaded = False

        # 配置对象
        self.app = ApplicationConfig()
        self.database = DatabaseConfig()
        self.ui = UIConfig()
        self.logging = LoggingConfig()
        self.validation = ValidationConfig()
        self.business = BusinessConfig()
        self.document = DocumentConfig()

        # 确保配置目录存在
        ensure_directory_exists(self.config_file.parent)

    def load(self) -> None:
        """加载配置.

        从配置文件加载用户配置, 与默认配置合并.
        如果配置文件不存在, 使用默认配置并创建配置文件.

        Raises:
            ConfigurationError: 当配置加载或解析失败时
        """
        try:
            # 加载默认配置
            self._config_data = deepcopy(DEFAULT_CONFIG)

            # 如果配置文件存在, 加载用户配置
            if self.config_file.exists():
                with self.config_file.open(encoding="utf-8") as f:
                    user_config = json.load(f)

                # 合并用户配置
                self._merge_config(self._config_data, user_config)
                logger.info("配置文件加载成功: %s", self.config_file)
            else:
                logger.info("配置文件不存在, 使用默认配置")
                # 创建默认配置文件
                self.save()

            # 应用配置到各个配置对象
            self._apply_config()

            # 验证配置
            self.validate()

            self._is_loaded = True

        except json.JSONDecodeError as e:
            msg = f"配置文件格式错误: {e}"
            raise ConfigurationError(
                msg,
                config_file=str(self.config_file),
                original_exception=e,
            )
        except OSError as e:
            msg = f"配置加载失败: {e}"
            raise ConfigurationError(
                msg,
                config_file=str(self.config_file),
                original_exception=e,
            )

    def save(self) -> None:
        """保存配置到文件.

        将当前配置保存到配置文件中.

        Raises:
            ConfigurationError: 当配置保存失败时
        """
        try:
            # 收集当前配置
            current_config = self._collect_config()

            # 确保目录存在
            ensure_directory_exists(self.config_file.parent)

            # 保存到文件
            with self.config_file.open("w", encoding="utf-8") as f:
                json.dump(current_config, f, indent=2, ensure_ascii=False)

            logger.info("配置文件保存成功: %s", self.config_file)

        except OSError as e:
            msg = f"配置保存失败: {e}"
            raise ConfigurationError(
                msg,
                config_file=str(self.config_file),
                original_exception=e,
            )

    def validate(self) -> None:
        """验证所有配置.

        Raises:
            ValidationError: 当配置验证失败时
        """
        try:
            self.app.validate()
            self.database.validate()
            self.ui.validate()
            self.logging.validate()
            self.validation.validate()
            self.business.validate()
            self.document.validate()

            logger.info("配置验证通过")

        except ValidationError:
            logger.exception("配置验证失败")
            raise

    def reset_to_default(self) -> None:
        """重置为默认配置.

        将所有配置重置为系统默认值.
        """
        self._config_data = deepcopy(DEFAULT_CONFIG)
        self._apply_config()
        logger.info("配置已重置为默认值")

    def update_config(
        self, section: str, key: str, value: Union[str, float, bool, list, dict]
    ) -> None:
        """更新单个配置项.

        Args:
            section: 配置节名称 (如 'app', 'database', 'ui')
            key: 配置键名
            value: 配置值

        Raises:
            ConfigurationError: 当配置节或键不存在时
        """
        if not self._is_loaded:
            self.load()

        # 获取配置对象
        config_obj = getattr(self, section, None)
        if config_obj is None:
            msg = f"配置节不存在: {section}"
            raise ConfigurationError(msg)

        # 检查属性是否存在
        if not hasattr(config_obj, key):
            msg = f"配置键不存在: {section}.{key}"
            raise ConfigurationError(msg)

        # 更新配置对象
        setattr(config_obj, key, value)

        # 更新内部配置数据
        if section not in self._config_data:
            self._config_data[section] = {}
        self._config_data[section][key] = value

        logger.info("配置更新: %s.%s = %s", section, key, value)

    def get_config(
        self,
        section: str,
        key: str,
        default: Union[str, float, bool, list, dict, None] = None,
    ) -> Union[str, int, float, bool, list, dict, None]:
        """获取配置值.

        Args:
            section: 配置节名称
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        if not self._is_loaded:
            self.load()

        config_obj = getattr(self, section, None)
        if config_obj is None:
            return default

        return getattr(config_obj, key, default)

    def get_all_config(self) -> dict[str, Any]:
        """获取所有配置.

        Returns:
            包含所有配置的字典
        """
        if not self._is_loaded:
            self.load()

        return self._collect_config()

    def _merge_config(
        self, base_config: dict[str, Any], user_config: dict[str, Any]
    ) -> None:
        """合并用户配置到基础配置.

        Args:
            base_config: 基础配置字典
            user_config: 用户配置字典
        """
        for key, value in user_config.items():
            if (
                key in base_config
                and isinstance(base_config[key], dict)
                and isinstance(value, dict)
            ):
                # 递归合并嵌套字典
                self._merge_config(base_config[key], value)
            else:
                # 直接覆盖值
                base_config[key] = value

    def _apply_config(self) -> None:
        """将配置数据应用到配置对象."""
        # 应用应用程序配置
        if "app" in self._config_data:
            app_config = self._config_data["app"]
            self.app.name = safe_str(app_config.get("name", self.app.name))
            self.app.version = safe_str(app_config.get("version", self.app.version))
            self.app.description = safe_str(
                app_config.get("description", self.app.description)
            )
            self.app.author = safe_str(app_config.get("author", self.app.author))
            self.app.debug = bool(app_config.get("debug", self.app.debug))
            self.app.auto_save = bool(app_config.get("auto_save", self.app.auto_save))
            self.app.auto_backup = bool(
                app_config.get("auto_backup", self.app.auto_backup)
            )
            self.app.language = safe_str(app_config.get("language", self.app.language))

        # 应用数据库配置
        if "database" in self._config_data:
            db_config = self._config_data["database"]
            self.database.name = safe_str(
                db_config.get("default_name", self.database.name)
            )
            self.database.path = safe_str(
                db_config.get("default_path", self.database.path)
            )
            self.database.backup_interval = safe_int(
                db_config.get("backup_interval", self.database.backup_interval)
            )
            self.database.max_backups = safe_int(
                db_config.get("max_backups", self.database.max_backups)
            )
            self.database.connection_timeout = safe_int(
                db_config.get("connection_timeout", self.database.connection_timeout)
            )

            if "pragma_settings" in db_config:
                self.database.pragma_settings.update(db_config["pragma_settings"])

        # 应用UI配置
        if "ui" in self._config_data:
            ui_config = self._config_data["ui"]
            if "window" in ui_config:
                window_config = ui_config["window"]
                self.ui.min_width = safe_int(
                    window_config.get("min_width", self.ui.min_width)
                )
                self.ui.min_height = safe_int(
                    window_config.get("min_height", self.ui.min_height)
                )
                self.ui.default_width = safe_int(
                    window_config.get("default_width", self.ui.default_width)
                )
                self.ui.default_height = safe_int(
                    window_config.get("default_height", self.ui.default_height)
                )

            if "theme" in ui_config:
                # 主题可能是字符串或字典,需要处理两种情况
                theme_config = ui_config["theme"]
                if isinstance(theme_config, str):
                    self.ui.theme = safe_str(theme_config)
                elif isinstance(theme_config, dict):
                    self.ui.theme = safe_str(theme_config.get("default", self.ui.theme))
                    if "available" in theme_config:
                        self.ui.available_themes = theme_config["available"]

            if "available_themes" in ui_config:
                self.ui.available_themes = ui_config["available_themes"]

            if "pagination" in ui_config:
                pagination_config = ui_config["pagination"]
                self.ui.default_page_size = safe_int(
                    pagination_config.get(
                        "default_page_size", self.ui.default_page_size
                    )
                )
                if "page_size_options" in pagination_config:
                    self.ui.page_size_options = pagination_config["page_size_options"]

        # 应用其他配置
        # 为了保持代码简洁, 这里省略了其他配置的应用逻辑

    def _collect_config(self) -> dict[str, Any]:
        """收集当前配置到字典.

        Returns:
            包含所有配置的字典
        """
        return {
            "app": asdict(self.app),
            "database": asdict(self.database),
            "ui": asdict(self.ui),
            "logging": asdict(self.logging),
            "validation": asdict(self.validation),
            "business": asdict(self.business),
            "document": asdict(self.document),
        }


# 全局配置管理器实例
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """获取全局配置管理器实例.

    Returns:
        配置管理器实例
    """
    # 通过调用公共方法来检查是否需要加载配置
    try:
        config_manager.get_all_config()
    except (AttributeError, KeyError):
        config_manager.load()
    return config_manager


def load_config(config_file: str | None = None) -> ConfigManager:
    """加载配置.

    Args:
        config_file: 配置文件路径

    Returns:
        配置管理器实例
    """
    # 避免使用global语句, 直接返回新实例或使用现有实例
    if config_file:
        new_manager = ConfigManager(config_file)
        new_manager.load()
        return new_manager
    config_manager.load()
    return config_manager


def save_config() -> None:
    """保存当前配置."""
    config_manager.save()


def reset_config() -> None:
    """重置配置为默认值."""
    config_manager.reset_to_default()
    config_manager.save()
