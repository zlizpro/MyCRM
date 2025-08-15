#!/usr/bin/env python3
"""
MiniCRM 代码质量检查脚本
使用基于文件类型的合理标准进行全面质量检查
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 导入配置
from quality_check_config import FILE_SIZE_LIMITS, QUALITY_PRIORITIES


def determine_file_category(file_path: Path) -> str:
    """根据文件路径确定文件类别"""
    file_str = str(file_path)

    if "src/minicrm/ui/" in file_str:
        return "ui_components"
    elif "src/minicrm/services/" in file_str:
        return "business_logic"
    elif "src/minicrm/data/" in file_str:
        return "data_access"
    elif "src/minicrm/models/" in file_str:
        return "models"
    elif "src/minicrm/core/" in file_str:
        return "core_utils"
    elif "src/minicrm/config/" in file_str or "scripts/" in file_str:
        return "config"
    elif "src/transfunctions/" in file_str:
        return "transfunctions"
    elif "tests/" in file_str or "test_" in file_str:
        return "tests"
    else:
        return "default"


def check_file_size(file_path: Path) -> Tuple[str, str, int]:
    """检查单个文件的大小"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_count = len(f.readlines())

        category = determine_file_category(file_path)
        limits = FILE_SIZE_LIMITS[category]

        if line_count > limits["max"]:
            status = "❌ 超标"
            message = f"{file_path}: {line_count}行 (超过{limits['max']}行限制, 类别: {category})"
        elif line_count > limits["warning"]:
            status = "⚠️ 警告"
            message = f"{file_path}: {line_count}行 (建议拆分, 推荐: {limits['recommended']}行, 类别: {category})"
        elif line_count > limits["recommended"]:
            status = "💡 提示"
            message = f"{file_path}: {line_count}行 (适中, 推荐: {limits['recommended']}行, 类别: {category})"
        else:
            status = "✅ 良好"
            message = f"{file_path}: {line_count}行 (良好, 类别: {category})"

        return status, message, line_count

    except Exception as e:
        return "❌ 错误", f"检查 {file_path} 时出错: {e}", 0


def check_all_file_sizes() -> Tuple[List[str], List[str], List[str]]:
    """检查所有文件大小"""
    errors = []
    warnings = []
    info = []

    src_dir = Path("src")
    if not src_dir.exists():
        errors.append("⚠️ src目录不存在")
        return errors, warnings, info

    for py_file in src_dir.glob("**/*.py"):
        if py_file.name == "__init__.py":
            continue

        status, message, line_count = check_file_size(py_file)

        if status == "❌ 超标" or status == "❌ 错误":
            errors.append(message)
        elif status == "⚠️ 警告":
            warnings.append(message)
        elif status == "💡 提示":
            info.append(message)

    return errors, warnings, info


def run_ruff_check(file_path: Optional[str] = None) -> Tuple[bool, str]:
    """运行Ruff代码检查"""
    try:
        target = file_path if file_path else "src/"
        result = subprocess.run(
            ["uv", "run", "ruff", "check", target, "--output-format=github"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"Ruff检查失败: {e}"


def run_mypy_check(file_path: Optional[str] = None) -> Tuple[bool, str]:
    """运行MyPy类型检查"""
    try:
        target = file_path if file_path else "src/"
        result = subprocess.run(
            [
                "uv",
                "run",
                "mypy",
                target,
                "--show-error-codes",
                "--show-column-numbers",
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"MyPy检查失败: {e}"


def main():
    """主检查函数"""
    print("🔧 MiniCRM 代码质量检查")
    print("=" * 50)

    # 1. 文件大小检查
    print("\n📏 文件大小检查...")
    errors, warnings, info = check_all_file_sizes()

    if errors:
        print(f"\n❌ 发现 {len(errors)} 个文件大小违规:")
        for error in errors[:10]:  # 只显示前10个
            print(f"   {error}")
        if len(errors) > 10:
            print(f"   ... 还有 {len(errors) - 10} 个文件")

    if warnings:
        print(f"\n⚠️ 发现 {len(warnings)} 个文件建议拆分:")
        for warning in warnings[:5]:  # 只显示前5个
            print(f"   {warning}")
        if len(warnings) > 5:
            print(f"   ... 还有 {len(warnings) - 5} 个文件")

    # 2. Ruff检查
    print("\n🔍 Ruff代码规范检查...")
    ruff_ok, ruff_output = run_ruff_check()
    if ruff_ok:
        print("✅ Ruff检查通过")
    else:
        print("❌ Ruff检查发现问题:")
        print(ruff_output[:1000] + "..." if len(ruff_output) > 1000 else ruff_output)

    # 3. MyPy检查
    print("\n🔍 MyPy类型检查...")
    mypy_ok, mypy_output = run_mypy_check()
    if mypy_ok:
        print("✅ MyPy检查通过")
    else:
        print("❌ MyPy检查发现问题:")
        print(mypy_output[:1000] + "..." if len(mypy_output) > 1000 else mypy_output)

    # 总结
    print("\n📊 检查总结:")
    print(
        f"   文件大小: {'❌' if errors else '⚠️' if warnings else '✅'} "
        f"({len(errors)} 违规, {len(warnings)} 警告)"
    )
    print(f"   代码规范: {'✅' if ruff_ok else '❌'}")
    print(f"   类型检查: {'✅' if mypy_ok else '❌'}")

    # 建议
    if errors or not ruff_ok or not mypy_ok:
        print("\n🛠️ 修复建议:")
        if errors:
            print("   1. 拆分过大的文件:")
            print("      python scripts/urgent_split_large_files.py")
        if not ruff_ok:
            print("   2. 修复代码规范问题:")
            print("      uv run ruff check src/ --fix")
            print("      uv run ruff format src/")
        if not mypy_ok:
            print("   3. 修复类型注解问题:")
            print("      参考MyPy输出，添加缺失的类型注解")

        print("\n📚 参考标准:")
        print("   - 文件大小标准: scripts/quality-check-config.py")
        print("   - 开发标准: .kiro/steering/minicrm-development-standards.md")

        return 1
    else:
        print("\n🎉 所有检查通过！代码质量良好。")
        return 0


if __name__ == "__main__":
    sys.exit(main())
