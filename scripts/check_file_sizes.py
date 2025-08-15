#!/usr/bin/env python3
"""
Pre-commit hook: 基于文件类型的分层文件大小检查

使用更合理的、基于文件类型的大小限制标准

功能特性:
- 基于文件类型的智能分层限制
- 详细的违规报告和修复建议
- 支持命令行参数
- 适用于CI/CD集成
"""

import sys
from pathlib import Path


# 基于文件类型和复杂度的分层标准
FILE_SIZE_STANDARDS = {
    # UI组件层 - 需要处理布局、事件、样式、数据绑定
    "ui_components": {
        "recommended": 400,
        "warning": 600,
        "max": 800,
        "paths": ["src/minicrm/ui/"],
    },
    # 业务逻辑层 - 完整的业务概念，但保持单一职责
    "business_logic": {
        "recommended": 300,
        "warning": 450,
        "max": 600,
        "paths": ["src/minicrm/services/"],
    },
    # 数据访问层 - 主要是CRUD操作
    "data_access": {
        "recommended": 250,
        "warning": 350,
        "max": 500,
        "paths": ["src/minicrm/data/"],
    },
    # 模型层 - 数据结构定义
    "models": {
        "recommended": 200,
        "warning": 300,
        "max": 400,
        "paths": ["src/minicrm/models/"],
    },
    # 核心工具层 - 工具函数集合
    "core_utils": {
        "recommended": 300,
        "warning": 400,
        "max": 500,
        "paths": ["src/minicrm/core/"],
    },
    # 配置文件 - 主要是数据配置
    "config": {
        "recommended": 400,
        "warning": 600,
        "max": 800,
        "paths": ["src/minicrm/config/", "scripts/"],
    },
    # transfunctions - 可复用函数库
    "transfunctions": {
        "recommended": 300,
        "warning": 400,
        "max": 500,
        "paths": ["src/transfunctions/"],
    },
    # 测试文件 - 需要覆盖多种场景
    "tests": {
        "recommended": 500,
        "warning": 750,
        "max": 1000,
        "paths": ["tests/", "test_"],
    },
    # 默认标准 - 其他文件
    "default": {"recommended": 300, "warning": 400, "max": 500, "paths": []},
}


def get_file_category(file_path: Path) -> str:
    """根据文件路径确定文件类别"""
    file_str = str(file_path)

    # 检查每个类别的路径模式
    for category, config in FILE_SIZE_STANDARDS.items():
        if category == "default":
            continue

        for path_pattern in config["paths"]:
            if path_pattern in file_str:
                return category

    return "default"


def get_limits(category: str) -> tuple[int, int, int]:
    """获取指定类别的限制值"""
    config = FILE_SIZE_STANDARDS[category]
    return config["recommended"], config["warning"], config["max"]


def main():
    """检查文件大小"""
    issues = []
    warnings = []

    # 检查src目录下的所有Python文件
    src_dir = Path("src")
    if not src_dir.exists():
        print("⚠️  src目录不存在")
        return 0

    for py_file in src_dir.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                line_count = len(f.readlines())

            # 确定文件类别和对应限制
            category = get_file_category(py_file)
            recommended, warning_threshold, max_lines = get_limits(category)

            if line_count > max_lines:
                issues.append(
                    f"❌ {py_file}: {line_count}行 (超过{max_lines}行限制, 类别: {category})"
                )
            elif line_count > warning_threshold:
                warnings.append(
                    f"⚠️  {py_file}: {line_count}行 (建议拆分, 推荐: {recommended}行, 类别: {category})"
                )

        except Exception as e:
            issues.append(f"❌ 检查 {py_file} 时出错: {e}")

    # 输出警告信息
    if warnings:
        for warning in warnings:
            print(warning)

    # 输出错误信息
    if issues:
        print("🚨 发现文件大小违规:")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 修复建议:")
        print("   1. 运行: python scripts/urgent_split_large_files.py")
        print("   2. 按照重构指南拆分文件")
        print("   3. 参考新的分层标准进行拆分")
        print("\n📊 文件大小标准:")
        for category, config in FILE_SIZE_STANDARDS.items():
            if category != "default":
                print(
                    f"   {category}: 推荐{config['recommended']}行, 警告{config['warning']}行, 最大{config['max']}行"
                )
        return 1

    print("✅ 所有文件大小符合标准")
    return 0


if __name__ == "__main__":
    sys.exit(main())
