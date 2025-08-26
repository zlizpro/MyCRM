#!/usr/bin/env python3
"""Git暂存区清理脚本
移除不应该提交的文件
"""

import os
from pathlib import Path
import subprocess
import sys


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 需要从暂存区移除的文件模式
FILES_TO_UNSTAGE = [
    # 系统文件
    ".DS_Store",
    ".coverage",
    # Python缓存文件
    "**/__pycache__/**",
    "**/*.pyc",
    # 备份文件
    "**/*.backup",
    "**/*_backup.py",
    "**/*_fixed.py",
    "**/*_temp.py",
    # 重构指南
    "**/REFACTOR_GUIDE.md",
    # 测试数据文件
    "test_*.xlsx",
    "test_*.pdf",
    "test_*.docx",
    "dummy.csv",
    # 报告文件
    "*_report.txt",
    "*_report.md",
    "*_REPORT.md",
    "*_SUMMARY.md",
    "*_PLAN.md",
    "*_GUIDE.md",
    "*_CHECKLIST.md",
    "architecture_validation_report.md",
    "chinese_punctuation_fix_report.txt",
    "dependency_check_*.txt",
    "mypy_report.txt",
    "quality_gate_report.md",
    "srp_validation_report.md",
    "transfunctions_usage_report.md",
    # 临时脚本
    "create_ttk_structure_fixed.py",
    "dependency_checker_fixed.py",
    "test_ttk_complete_functionality_fixed.py",
    # 服务备份文件
    "src/minicrm/services/*_backup.py",
    "src/minicrm/services/customer_type_service_fixed.py",
    # TTK固定文件
    "src/minicrm/ui/ttk_base/navigation_registry_ttk_fixed.py",
    # 测试报告
    "test_reports/**",
    # 性能报告
    "reports/static_error_report*.md",
]


def run_git_command(command):
    """运行Git命令"""
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            shell=True,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def unstage_files(patterns):
    """从暂存区移除匹配的文件"""
    print("🧹 开始清理Git暂存区...")

    # 获取所有暂存的文件
    success, staged_files, error = run_git_command("git diff --cached --name-only")
    if not success:
        print(f"❌ 无法获取暂存文件: {error}")
        return False

    staged_files = [f.strip() for f in staged_files.split("\n") if f.strip()]
    if not staged_files:
        print("✅ 暂存区为空，无需清理")
        return True

    print(f"📋 发现 {len(staged_files)} 个暂存文件")

    files_to_remove = []

    # 检查每个暂存文件是否匹配需要移除的模式
    for staged_file in staged_files:
        for pattern in patterns:
            # 简单的模式匹配
            if should_remove_file(staged_file, pattern):
                files_to_remove.append(staged_file)
                break

    if not files_to_remove:
        print("✅ 没有需要移除的文件")
        return True

    print(f"🗑️ 准备移除 {len(files_to_remove)} 个文件:")
    for file in files_to_remove[:10]:  # 只显示前10个
        print(f"   - {file}")
    if len(files_to_remove) > 10:
        print(f"   ... 还有 {len(files_to_remove) - 10} 个文件")

    # 移除文件
    for file in files_to_remove:
        success, _, error = run_git_command(f"git reset HEAD '{file}'")
        if success:
            print(f"✅ 已移除: {file}")
        else:
            print(f"❌ 移除失败: {file} - {error}")

    print(f"🎉 清理完成！移除了 {len(files_to_remove)} 个文件")
    return True


def should_remove_file(file_path, pattern):
    """检查文件是否匹配移除模式"""
    import fnmatch

    # 处理不同类型的模式
    if pattern.startswith("**/") and pattern.endswith("/**"):
        # 目录模式 **/__pycache__/**
        dir_pattern = pattern[3:-3]  # 移除 **/ 和 /**
        return f"/{dir_pattern}/" in f"/{file_path}/"
    if "**/" in pattern:
        # 递归模式 **/*.pyc
        return fnmatch.fnmatch(file_path, pattern)
    if "*" in pattern:
        # 通配符模式
        return fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            os.path.basename(file_path), pattern
        )
    # 精确匹配
    return file_path == pattern or os.path.basename(file_path) == pattern


def main():
    """主函数"""
    print("🔧 Git暂存区清理工具")
    print("=" * 50)

    # 清理暂存区
    success = unstage_files(FILES_TO_UNSTAGE)

    if success:
        print("\n💡 建议接下来的操作:")
        print("1. 运行 'git status' 查看当前状态")
        print("2. 运行 'python scripts/pre-commit-check.py' 再次检查")
        print("3. 确认无问题后再次添加需要的文件")
        return 0
    print("\n❌ 清理过程中出现错误")
    return 1


if __name__ == "__main__":
    sys.exit(main())
