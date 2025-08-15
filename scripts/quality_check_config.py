"""
MiniCRM 代码质量检查配置

基于实际开发需求的分层文件大小限制，避免过度拆分，保持代码的内聚性和可读性。
"""

# 基于文件类型和复杂度的合理限制
FILE_SIZE_LIMITS = {
    # UI组件文件 (复杂界面逻辑 - 布局、事件、样式、数据绑定)
    "ui_components": {
        "recommended": 400,  # 推荐范围 - 适合大多数UI组件
        "warning": 600,  # 警告阈值 - 建议考虑拆分
        "max": 800,  # 强制限制 - 必须拆分
    },
    # 业务逻辑文件 (services层 - 完整业务概念，保持单一职责)
    "business_logic": {
        "recommended": 300,  # 推荐范围
        "warning": 450,  # 警告阈值
        "max": 600,  # 强制限制
    },
    # 数据访问文件 (DAO层 - CRUD操作和查询逻辑)
    "data_access": {
        "recommended": 250,  # 推荐范围
        "warning": 350,  # 警告阈值
        "max": 500,  # 强制限制
    },
    # 模型文件 (数据结构定义和验证逻辑)
    "models": {
        "recommended": 200,  # 推荐范围
        "warning": 300,  # 警告阈值
        "max": 400,  # 强制限制
    },
    # 核心工具文件 (工具函数集合)
    "core_utils": {
        "recommended": 300,  # 推荐范围
        "warning": 400,  # 警告阈值
        "max": 500,  # 强制限制
    },
    # 配置文件 (主要是数据配置和设置)
    "config": {
        "recommended": 400,  # 推荐范围
        "warning": 600,  # 警告阈值
        "max": 800,  # 强制限制
    },
    # transfunctions文件 (可复用函数库)
    "transfunctions": {
        "recommended": 300,  # 推荐范围
        "warning": 400,  # 警告阈值
        "max": 500,  # 强制限制
    },
    # 测试文件 (需要覆盖多种测试场景)
    "tests": {
        "recommended": 500,  # 推荐范围
        "warning": 750,  # 警告阈值
        "max": 1000,  # 强制限制
    },
    # 默认标准 (其他文件类型)
    "default": {
        "recommended": 300,  # 推荐范围
        "warning": 400,  # 警告阈值
        "max": 500,  # 强制限制
    },
}

# 质量检查优先级
QUALITY_PRIORITIES = [
    "功能正确性",  # 最高优先级
    "类型安全",  # MyPy检查
    "代码规范",  # Ruff检查
    "架构设计",  # 分层架构
    "可读性维护性",  # 代码清晰度
    "文件大小",  # 最低优先级
]

# 文件类别映射说明
FILE_CATEGORY_DESCRIPTIONS = {
    "ui_components": "UI组件 - 界面逻辑、布局、事件处理",
    "business_logic": "业务逻辑 - 核心业务规则和流程",
    "data_access": "数据访问 - 数据库操作和查询",
    "models": "数据模型 - 数据结构和验证",
    "core_utils": "核心工具 - 通用工具函数",
    "config": "配置文件 - 系统配置和设置",
    "transfunctions": "可复用函数 - 标准化函数库",
    "tests": "测试文件 - 单元测试和集成测试",
    "default": "其他文件 - 未分类文件",
}

# 复杂度检查规则
COMPLEXITY_RULES = {
    "max_cyclomatic_complexity": 10,  # 最大圈复杂度
    "max_function_length": 50,  # 最大函数长度
    "max_class_length": 300,  # 最大类长度
    "max_function_args": 5,  # 最大函数参数数量
    "max_nested_blocks": 4,  # 最大嵌套层数
}

# Ruff检查规则配置
RUFF_RULES = {
    "select": [
        "E",  # pycodestyle errors
        "W",  # pycodestyle warnings
        "F",  # Pyflakes
        "I",  # isort
        "N",  # pep8-naming
        "UP",  # pyupgrade
        "B",  # flake8-bugbear
        "C4",  # flake8-comprehensions
        "PIE",  # flake8-pie
        "SIM",  # flake8-simplify
        "RET",  # flake8-return
        "C901",  # mccabe complexity
        "PLR",  # Pylint refactor
    ],
    "ignore": [
        "E501",  # line too long (handled by formatter)
        "W503",  # line break before binary operator
    ],
}

# MyPy检查配置
MYPY_CONFIG = {
    "strict": True,
    "warn_return_any": True,
    "warn_unused_configs": True,
    "disallow_untyped_defs": True,
    "disallow_incomplete_defs": True,
    "check_untyped_defs": True,
    "disallow_untyped_decorators": True,
}
