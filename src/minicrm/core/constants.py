"""
MiniCRM系统常量定义

定义了系统中使用的所有枚举类型和配置常量.
这些常量确保了数据的一致性和系统的可维护性.

包含的常量类型:
- 业务枚举:客户等级、供应商等级、交互类型等
- 系统配置:数据库配置、UI配置、默认设置等
- 格式常量:日期格式、货币格式等
"""

from enum import Enum, IntEnum
from pathlib import Path


# ==================== 业务枚举类型 ====================


class CustomerLevel(Enum):
    """
    客户等级枚举

    定义了客户的重要性等级,用于差异化服务和资源分配.
    """

    VIP = "vip"  # VIP客户 - 最高等级
    IMPORTANT = "important"  # 重要客户 - 高等级
    NORMAL = "normal"  # 普通客户 - 标准等级
    POTENTIAL = "potential"  # 潜在客户 - 待开发

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.VIP: "VIP客户",
            self.IMPORTANT: "重要客户",
            self.NORMAL: "普通客户",
            self.POTENTIAL: "潜在客户",
        }
        return names[self]

    @property
    def color(self) -> str:
        """返回对应的颜色代码"""
        colors = {
            self.VIP: "#FF6B6B",  # 红色
            self.IMPORTANT: "#4ECDC4",  # 青色
            self.NORMAL: "#45B7D1",  # 蓝色
            self.POTENTIAL: "#96CEB4",  # 绿色
        }
        return colors[self]


class SupplierLevel(Enum):
    """
    供应商等级枚举

    定义了供应商的重要性和合作等级.
    """

    STRATEGIC = "strategic"  # 战略供应商 - 核心合作伙伴
    IMPORTANT = "important"  # 重要供应商 - 主要合作伙伴
    NORMAL = "normal"  # 普通供应商 - 标准合作
    BACKUP = "backup"  # 备选供应商 - 备用选择

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.STRATEGIC: "战略供应商",
            self.IMPORTANT: "重要供应商",
            self.NORMAL: "普通供应商",
            self.BACKUP: "备选供应商",
        }
        return names[self]


class InteractionType(Enum):
    """
    互动类型枚举

    定义了与客户/供应商的各种互动类型.
    """

    PHONE_CALL = "phone_call"  # 电话沟通
    EMAIL = "email"  # 邮件沟通
    MEETING = "meeting"  # 会议
    VISIT = "visit"  # 拜访
    COMPLAINT = "complaint"  # 投诉处理
    CONSULTATION = "consultation"  # 咨询服务
    FOLLOW_UP = "follow_up"  # 跟进
    OTHER = "other"  # 其他

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.PHONE_CALL: "电话沟通",
            self.EMAIL: "邮件沟通",
            self.MEETING: "会议",
            self.VISIT: "拜访",
            self.COMPLAINT: "投诉处理",
            self.CONSULTATION: "咨询服务",
            self.FOLLOW_UP: "跟进",
            self.OTHER: "其他",
        }
        return names[self]


class ContractStatus(Enum):
    """
    合同状态枚举

    定义了合同的各种状态.
    """

    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已审核
    SIGNED = "signed"  # 已签署
    ACTIVE = "active"  # 执行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"  # 已过期

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.DRAFT: "草稿",
            self.PENDING: "待审核",
            self.APPROVED: "已审核",
            self.SIGNED: "已签署",
            self.ACTIVE: "执行中",
            self.COMPLETED: "已完成",
            self.CANCELLED: "已取消",
            self.EXPIRED: "已过期",
        }
        return names[self]


class QuoteStatus(Enum):
    """
    报价状态枚举

    定义了报价的各种状态.
    """

    DRAFT = "draft"  # 草稿
    SENT = "sent"  # 已发送
    VIEWED = "viewed"  # 已查看
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.DRAFT: "草稿",
            self.SENT: "已发送",
            self.VIEWED: "已查看",
            self.ACCEPTED: "已接受",
            self.REJECTED: "已拒绝",
            self.EXPIRED: "已过期",
            self.CANCELLED: "已取消",
        }
        return names[self]


class ServiceTicketStatus(Enum):
    """
    售后工单状态枚举

    定义了售后服务工单的各种状态.
    """

    OPEN = "open"  # 已开启
    IN_PROGRESS = "in_progress"  # 处理中
    PENDING = "pending"  # 等待中
    RESOLVED = "resolved"  # 已解决
    CLOSED = "closed"  # 已关闭
    CANCELLED = "cancelled"  # 已取消

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.OPEN: "已开启",
            self.IN_PROGRESS: "处理中",
            self.PENDING: "等待中",
            self.RESOLVED: "已解决",
            self.CLOSED: "已关闭",
            self.CANCELLED: "已取消",
        }
        return names[self]


class Priority(IntEnum):
    """
    优先级枚举

    定义了任务、工单等的优先级.
    使用IntEnum以便进行数值比较.
    """

    LOW = 1  # 低优先级
    NORMAL = 2  # 普通优先级
    HIGH = 3  # 高优先级
    URGENT = 4  # 紧急
    CRITICAL = 5  # 严重

    @property
    def display_name(self) -> str:
        """返回显示名称"""
        names = {
            self.LOW: "低",
            self.NORMAL: "普通",
            self.HIGH: "高",
            self.URGENT: "紧急",
            self.CRITICAL: "严重",
        }
        return names[self]

    @property
    def color(self) -> str:
        """返回对应的颜色代码"""
        colors = {
            self.LOW: "#28A745",  # 绿色
            self.NORMAL: "#17A2B8",  # 青色
            self.HIGH: "#FFC107",  # 黄色
            self.URGENT: "#FD7E14",  # 橙色
            self.CRITICAL: "#DC3545",  # 红色
        }
        return colors[self]


# ==================== 系统配置常量 ====================

# 应用程序基本信息
APP_NAME = "MiniCRM"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "跨平台客户关系管理系统"
APP_AUTHOR = "MiniCRM开发团队"

# 文件和目录路径
HOME_DIR = Path.home()
APP_DATA_DIR = HOME_DIR / ".minicrm"
CONFIG_DIR = APP_DATA_DIR / "config"
LOG_DIR = APP_DATA_DIR / "logs"
BACKUP_DIR = APP_DATA_DIR / "backups"
TEMPLATE_DIR = APP_DATA_DIR / "templates"
EXPORT_DIR = APP_DATA_DIR / "exports"

# 数据库配置
DATABASE_CONFIG = {
    "default_name": "minicrm.db",
    "default_path": APP_DATA_DIR / "minicrm.db",
    "backup_interval": 24,  # 小时
    "max_backups": 30,  # 保留备份数量
    "connection_timeout": 30,  # 秒
    "pragma_settings": {
        "journal_mode": "WAL",
        "synchronous": "NORMAL",
        "cache_size": -64000,  # 64MB
        "temp_store": "MEMORY",
        "mmap_size": 268435456,  # 256MB
    },
}

# UI配置
UI_CONFIG = {
    "window": {
        "min_width": 1024,
        "min_height": 768,
        "default_width": 1280,
        "default_height": 800,
    },
    "theme": {"default": "light", "available": ["light", "dark"]},
    "fonts": {
        "default": ("Microsoft YaHei UI", 9),
        "heading": ("Microsoft YaHei UI", 12, "bold"),
        "small": ("Microsoft YaHei UI", 8),
        "monospace": ("Consolas", 9),
    },
    "colors": {
        "light": {
            "bg_primary": "#FFFFFF",
            "bg_secondary": "#F8F9FA",
            "text_primary": "#212529",
            "text_secondary": "#6C757D",
            "accent": "#007BFF",
            "success": "#28A745",
            "warning": "#FFC107",
            "danger": "#DC3545",
            "border": "#DEE2E6",
        },
        "dark": {
            "bg_primary": "#2B2B2B",
            "bg_secondary": "#3C3C3C",
            "text_primary": "#FFFFFF",
            "text_secondary": "#CCCCCC",
            "accent": "#4A9EFF",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "danger": "#F44336",
            "border": "#555555",
        },
    },
    "pagination": {"default_page_size": 50, "page_size_options": [25, 50, 100, 200]},
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "encoding": "utf-8",
}

# 数据验证配置
VALIDATION_CONFIG = {
    "phone_pattern": r"^1[3-9]\d{9}$",
    "email_pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "max_text_length": 1000,
    "max_name_length": 100,
    "max_phone_length": 20,
    "max_email_length": 100,
    "currency_precision": 2,
}

# 业务规则配置
BUSINESS_CONFIG = {
    "customer": {
        "default_level": CustomerLevel.NORMAL,
        "max_credit_limit": 10000000,  # 1000万
        "credit_check_threshold": 100000,  # 10万
    },
    "supplier": {
        "default_level": SupplierLevel.NORMAL,
        "max_payment_days": 180,
        "quality_score_range": (0, 100),
    },
    "quote": {
        "default_validity_days": 30,
        "max_validity_days": 365,
        "auto_expire_check_interval": 24,  # 小时
    },
    "contract": {
        "default_duration_months": 12,
        "max_duration_months": 60,
        "renewal_notice_days": 30,
    },
}

# 文档模板配置
DOCUMENT_CONFIG = {
    "templates": {
        "quote": "quote_template.docx",
        "contract": "contract_template.docx",
        "invoice": "invoice_template.docx",
    },
    "export_formats": ["pdf", "docx", "xlsx"],
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "allowed_extensions": [".docx", ".xlsx", ".pdf", ".csv"],
}

# 默认配置汇总
DEFAULT_CONFIG = {
    "app": {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "author": APP_AUTHOR,
    },
    "database": DATABASE_CONFIG,
    "ui": UI_CONFIG,
    "logging": LOG_CONFIG,
    "validation": VALIDATION_CONFIG,
    "business": BUSINESS_CONFIG,
    "document": DOCUMENT_CONFIG,
    "directories": {
        "app_data": str(APP_DATA_DIR),
        "config": str(CONFIG_DIR),
        "logs": str(LOG_DIR),
        "backups": str(BACKUP_DIR),
        "templates": str(TEMPLATE_DIR),
        "exports": str(EXPORT_DIR),
    },
}

# ==================== 格式化常量 ====================

# 日期时间格式
DATE_FORMATS = {
    "default": "%Y-%m-%d",
    "display": "%Y年%m月%d日",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "datetime_display": "%Y年%m月%d日 %H:%M:%S",
    "time": "%H:%M:%S",
    "filename": "%Y%m%d_%H%M%S",
}

# 货币格式
CURRENCY_FORMATS = {
    "symbol": "¥",
    "decimal_places": 2,
    "thousands_separator": ",",
    "format_string": "¥{:,.2f}",
}

# 文件大小格式
FILE_SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"]

# 电话号码格式
PHONE_FORMATS = {
    "mobile": r"^1[3-9]\d{9}$",
    "landline": r"^0\d{2,3}-?\d{7,8}$",
    "display_mobile": "{}-{}-{}",  # 138-1234-5678
    "display_landline": "{}-{}",  # 021-12345678
}

# ==================== 错误代码常量 ====================

ERROR_CODES = {
    # 通用错误
    "UNKNOWN_ERROR": "未知错误",
    "INVALID_PARAMETER": "参数无效",
    "OPERATION_FAILED": "操作失败",
    # 验证错误
    "VALIDATION_FAILED": "数据验证失败",
    "REQUIRED_FIELD_MISSING": "必填字段缺失",
    "INVALID_FORMAT": "格式不正确",
    "VALUE_OUT_OF_RANGE": "值超出范围",
    # 数据库错误
    "DATABASE_CONNECTION_FAILED": "数据库连接失败",
    "DATABASE_QUERY_FAILED": "数据库查询失败",
    "DATABASE_TRANSACTION_FAILED": "数据库事务失败",
    "RECORD_NOT_FOUND": "记录不存在",
    "DUPLICATE_RECORD": "记录重复",
    # 业务逻辑错误
    "BUSINESS_RULE_VIOLATION": "违反业务规则",
    "INSUFFICIENT_PERMISSION": "权限不足",
    "RESOURCE_LOCKED": "资源被锁定",
    "OPERATION_NOT_ALLOWED": "操作不被允许",
    # 配置错误
    "CONFIG_FILE_NOT_FOUND": "配置文件不存在",
    "CONFIG_PARSE_ERROR": "配置解析错误",
    "INVALID_CONFIG_VALUE": "配置值无效",
    # UI错误
    "UI_COMPONENT_INIT_FAILED": "UI组件初始化失败",
    "THEME_LOAD_FAILED": "主题加载失败",
    "WINDOW_DISPLAY_FAILED": "窗口显示失败",
}


# ==================== 工具函数 ====================


def get_enum_choices(enum_class) -> dict[str, str]:
    """
    获取枚举类的选择项

    Args:
        enum_class: 枚举类

    Returns:
        包含枚举值和显示名称的字典
    """
    if hasattr(enum_class, "display_name"):
        return {item.value: item.display_name for item in enum_class}
    else:
        return {item.value: item.name for item in enum_class}


def get_enum_by_value(enum_class, value):
    """
    根据值获取枚举项

    Args:
        enum_class: 枚举类
        value: 枚举值

    Returns:
        枚举项,如果不存在则返回None
    """
    try:
        return enum_class(value)
    except ValueError:
        return None


def validate_enum_value(enum_class, value) -> bool:
    """
    验证值是否为有效的枚举值

    Args:
        enum_class: 枚举类
        value: 要验证的值

    Returns:
        是否为有效枚举值
    """
    return get_enum_by_value(enum_class, value) is not None
