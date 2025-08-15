#!/usr/bin/env python3
"""
MiniCRM 代码质量检查配置
基于实际开发需求的合理标准
"""

# 文件大小限制配置 (基于文件类型的合理标准)
FILE_SIZE_LIMITS = {
    # UI组件文件 (src/minicrm/ui/) - 需要处理布局、事件、样式、数据绑定
    "ui_components": {
        "recommended": 400,
        "warning": 600,
        "max": 800,
        "description": "UI组件包含复杂的界面逻辑，允许适当大一些",
    },
    # 业务逻辑文件 (src/minicrm/services/) - 完整的业务概念
    "business_logic": {
        "recommended": 300,
        "warning": 450,
        "max": 600,
        "description": "业务逻辑需要表达完整的业务概念，保持单一职责",
    },
    # 数据访问文件 (src/minicrm/data/) - CRUD操作和查询逻辑
    "data_access": {
        "recommended": 250,
        "warning": 350,
        "max": 500,
        "description": "数据访问包含CRUD操作和复杂查询",
    },
    # 模型文件 (src/minicrm/models/) - 数据结构定义
    "models": {
        "recommended": 200,
        "warning": 300,
        "max": 400,
        "description": "模型主要是数据结构定义和验证逻辑",
    },
    # 核心工具文件 (src/minicrm/core/) - 工具函数集合
    "core_utils": {
        "recommended": 300,
        "warning": 400,
        "max": 500,
        "description": "核心工具函数集合，可以适当大一些",
    },
    # 配置文件 (src/minicrm/config/, scripts/) - 主要是数据配置
    "config": {
        "recommended": 400,
        "warning": 600,
        "max": 800,
        "description": "配置文件主要是数据，可以较大",
    },
    # transfunctions文件 (src/transfunctions/) - 可复用函数库
    "transfunctions": {
        "recommended": 300,
        "warning": 400,
        "max": 500,
        "description": "可复用函数库，保持适中大小",
    },
    # 测试文件 (tests/, test_) - 需要覆盖多种场景
    "tests": {
        "recommended": 500,
        "warning": 750,
        "max": 1000,
        "description": "测试文件需要覆盖多种场景，可以较大",
    },
    # 默认标准 - 其他文件
    "default": {
        "recommended": 300,
        "warning": 400,
        "max": 500,
        "description": "默认标准，适用于其他类型文件",
    },
}

# 质量检查优先级 (1=最高, 6=最低)
QUALITY_PRIORITIES = {
    "functionality": 1,  # 功能正确性
    "type_safety": 2,  # 类型安全 (MyPy)
    "code_standards": 3,  # 代码规范 (Ruff)
    "architecture": 4,  # 架构设计
    "readability": 5,  # 可读性维护性
    "file_size": 6,  # 文件大小
}


def get_file_type(file_path: str) -> str:
    """根据文件路径判断文件类型"""
    if "/ui/" in file_path:
        return "ui_components"
    elif "/services/" in file_path:
        return "business_logic"
    elif "/data/" in file_path:
        return "data_access"
    else:
        return "utilities"


def check_file_size(file_path: str, line_count: int) -> dict:
    """检查文件大小是否符合标准"""
    file_type = get_file_type(file_path)
    limits = FILE_SIZE_LIMITS[file_type]

    if line_count <= limits["recommended"]:
        status = "excellent"
        message = f"✅ 优秀 ({line_count}行)"
    elif line_count <= limits["warning"]:
        status = "good"
        message = f"✅ 良好 ({line_count}行)"
    elif line_count <= limits["max"]:
        status = "warning"
        message = f"⚠️ 建议优化 ({line_count}行 > {limits['warning']}行)"
    else:
        status = "error"
        message = f"❌ 需要拆分 ({line_count}行 > {limits['max']}行)"

    return {
        "status": status,
        "message": message,
        "file_type": file_type,
        "limits": limits,
    }


if __name__ == "__main__":
    # 示例用法
    result = check_file_size("src/minicrm/ui/components/table/data_table.py", 380)
    print(f"文件大小检查: {result['message']}")
