"""
MiniCRM 常量定义

定义了应用程序中使用的所有常量，包括：
- 应用程序信息
- 数据库配置常量
- UI配置常量
- 业务规则常量
- 文件路径常量
- 默认值常量
"""

# 应用程序信息
APP_NAME = "MiniCRM"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "轻量级客户关系管理系统"
APP_AUTHOR = "MiniCRM Team"
APP_COPYRIGHT = "© 2025 MiniCRM Team"

# 数据库配置
DEFAULT_DB_NAME = "minicrm.db"
DB_VERSION = "1.0"
DB_TIMEOUT = 30.0  # 秒
DB_MAX_CONNECTIONS = 10

# 文件大小限制（字节）
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_BACKUP_SIZE = 100 * 1024 * 1024  # 100MB
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 分页配置
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 5

# UI配置
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
DEFAULT_SIDEBAR_WIDTH = 250

# 字体配置
DEFAULT_FONT_FAMILY = "Microsoft YaHei UI"
DEFAULT_FONT_SIZE = 9
HEADING_FONT_SIZE = 12
SMALL_FONT_SIZE = 8

# 颜色配置
COLORS = {
    # 主色调
    "primary": "#007BFF",
    "secondary": "#6C757D",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    # 背景色
    "bg_primary": "#FFFFFF",
    "bg_secondary": "#F8F9FA",
    "bg_dark": "#343A40",
    # 文字色
    "text_primary": "#212529",
    "text_secondary": "#6C757D",
    "text_muted": "#ADB5BD",
    "text_white": "#FFFFFF",
    # 边框色
    "border_light": "#DEE2E6",
    "border_dark": "#495057",
}

# 深色主题颜色
DARK_COLORS = {
    "primary": "#4A9EFF",
    "secondary": "#ADB5BD",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "info": "#2196F3",
    "bg_primary": "#2B2B2B",
    "bg_secondary": "#3C3C3C",
    "bg_dark": "#1E1E1E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#CCCCCC",
    "text_muted": "#999999",
    "text_white": "#FFFFFF",
    "border_light": "#555555",
    "border_dark": "#777777",
}

# 业务规则常量
BUSINESS_RULES = {
    # 客户相关
    "max_customer_name_length": 100,
    "max_customer_phone_length": 20,
    "max_customer_email_length": 100,
    "max_customer_address_length": 200,
    "max_customer_notes_length": 1000,
    # 供应商相关
    "max_supplier_name_length": 100,
    "max_supplier_contact_length": 50,
    "max_supplier_phone_length": 20,
    "max_supplier_email_length": 100,
    "max_supplier_address_length": 200,
    # 合同相关
    "max_contract_title_length": 200,
    "max_contract_description_length": 2000,
    "min_contract_amount": 0.01,
    "max_contract_amount": 999999999.99,
    # 报价相关
    "max_quote_title_length": 200,
    "max_quote_description_length": 1000,
    "default_quote_validity_days": 30,
    "max_quote_validity_days": 365,
    # 互动记录相关
    "max_interaction_title_length": 200,
    "max_interaction_content_length": 2000,
    # 任务相关
    "max_task_title_length": 200,
    "max_task_description_length": 1000,
    "default_task_priority": "normal",
}

# 文件路径常量
FILE_PATHS = {
    "config_dir": "config",
    "data_dir": "data",
    "logs_dir": "logs",
    "backups_dir": "backups",
    "templates_dir": "templates",
    "exports_dir": "exports",
    "imports_dir": "imports",
}

# 文件扩展名
FILE_EXTENSIONS = {
    "database": ".db",
    "backup": ".bak",
    "log": ".log",
    "config": ".json",
    "export_excel": ".xlsx",
    "export_csv": ".csv",
    "export_pdf": ".pdf",
    "export_word": ".docx",
    "template": ".template",
}

# 日期时间格式
DATE_FORMATS = {
    "date": "%Y-%m-%d",
    "datetime": "%Y-%m-%d %H:%M:%S",
    "time": "%H:%M:%S",
    "display_date": "%Y年%m月%d日",
    "display_datetime": "%Y年%m月%d日 %H:%M:%S",
    "filename_datetime": "%Y%m%d_%H%M%S",
}

# 货币格式
CURRENCY_FORMATS = {
    "symbol": "¥",
    "decimal_places": 2,
    "thousands_separator": ",",
    "decimal_separator": ".",
}

# 电话号码格式
PHONE_FORMATS = {
    "mobile_pattern": r"^1[3-9]\d{9}$",
    "landline_pattern": r"^0\d{2,3}-?\d{7,8}$",
    "display_format": "{}-{}-{}",  # 138-1234-5678
}

# 邮箱格式
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# 缓存配置
CACHE_CONFIG = {
    "default_ttl": 300,  # 5分钟
    "max_size": 1000,
    "cleanup_interval": 600,  # 10分钟
}

# 性能配置
PERFORMANCE_CONFIG = {
    "db_query_timeout": 30,  # 秒
    "ui_update_interval": 100,  # 毫秒
    "auto_save_interval": 300,  # 5分钟
    "backup_interval": 3600,  # 1小时
}

# 日志配置
LOG_CONFIG = {
    "default_level": "INFO",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}

# 网络配置
NETWORK_CONFIG = {
    "timeout": 30,  # 秒
    "max_retries": 3,
    "retry_delay": 1,  # 秒
}

# 导入导出配置
IMPORT_EXPORT_CONFIG = {
    "max_import_rows": 10000,
    "batch_size": 1000,
    "supported_formats": ["csv", "xlsx", "json"],
    "csv_encoding": "utf-8",
    "excel_sheet_name": "数据",
}

# 搜索配置
SEARCH_CONFIG = {
    "min_search_length": 2,
    "max_search_results": 100,
    "search_delay": 300,  # 毫秒
    "highlight_color": "#FFFF00",
}

# 通知配置
NOTIFICATION_CONFIG = {
    "default_duration": 5000,  # 5秒
    "max_notifications": 10,
    "auto_dismiss": True,
    "position": "top-right",
}

# 备份配置
BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_interval": 24,  # 小时
    "max_backups": 7,
    "compress_backups": True,
}

# 安全配置
SECURITY_CONFIG = {
    "password_min_length": 8,
    "session_timeout": 3600,  # 1小时
    "max_login_attempts": 5,
    "lockout_duration": 300,  # 5分钟
}

# API配置（为将来扩展预留）
API_CONFIG = {
    "version": "v1",
    "timeout": 30,
    "max_requests_per_minute": 60,
    "base_url": "http://localhost:8000/api",
}

# 板材行业特定常量
BOARD_INDUSTRY = {
    # 产品类别
    "product_categories": [
        "生态板",
        "家具板",
        "阻燃板",
        "胶合板",
        "刨花板",
        "中密度纤维板",
        "定向刨花板",
        "细木工板",
    ],
    # 质量等级
    "quality_grades": ["优等品", "一等品", "合格品"],
    # 规格尺寸（毫米）
    "standard_sizes": [
        "1220x2440",
        "1525x2440",
        "1830x2440",
        "1220x3050",
        "1525x3050",
    ],
    # 厚度规格（毫米）
    "standard_thickness": [3, 5, 9, 12, 15, 18, 25],
    # 计量单位
    "units": ["张", "立方米", "平方米", "吨"],
}

# 错误消息
ERROR_MESSAGES = {
    "validation_failed": "数据验证失败",
    "database_error": "数据库操作失败",
    "file_not_found": "文件不存在",
    "permission_denied": "权限不足",
    "network_error": "网络连接失败",
    "timeout_error": "操作超时",
    "unknown_error": "未知错误",
}

# 成功消息
SUCCESS_MESSAGES = {
    "save_success": "保存成功",
    "delete_success": "删除成功",
    "import_success": "导入成功",
    "export_success": "导出成功",
    "backup_success": "备份成功",
    "restore_success": "恢复成功",
}

# 确认消息
CONFIRM_MESSAGES = {
    "delete_confirm": "确定要删除这条记录吗？",
    "exit_confirm": "确定要退出程序吗？",
    "overwrite_confirm": "文件已存在，是否覆盖？",
    "reset_confirm": "确定要重置所有设置吗？",
}

# 应用程序状态
APP_STATES = {
    "initializing": "初始化中",
    "ready": "就绪",
    "loading": "加载中",
    "saving": "保存中",
    "error": "错误",
    "closing": "关闭中",
}

# 快捷键
SHORTCUTS = {
    "new": "Ctrl+N",
    "open": "Ctrl+O",
    "save": "Ctrl+S",
    "save_as": "Ctrl+Shift+S",
    "find": "Ctrl+F",
    "refresh": "F5",
    "exit": "Alt+F4",
    "copy": "Ctrl+C",
    "paste": "Ctrl+V",
    "cut": "Ctrl+X",
    "undo": "Ctrl+Z",
    "redo": "Ctrl+Y",
}

# 正则表达式模式
REGEX_PATTERNS = {
    "phone": r"^1[3-9]\d{9}$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "id_card": r"^\d{17}[\dXx]$",
    "postal_code": r"^\d{6}$",
    "chinese_name": r"^[\u4e00-\u9fa5]{2,10}$",
    "number": r"^\d+(\.\d+)?$",
    "positive_number": r"^[1-9]\d*(\.\d+)?$",
}

# 版本信息
VERSION_INFO = {
    "major": 1,
    "minor": 0,
    "patch": 0,
    "build": 1,
    "release_date": "2025-01-15",
    "codename": "初始版本",
}
