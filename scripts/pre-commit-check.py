#!/usr/bin/env python3
"""GitHub提交前检查脚本
用于确保不会提交敏感文件或不必要的文件到GitHub仓库
"""

from pathlib import Path
import re
import subprocess
import sys
from typing import List


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 敏感文件模式 - 这些文件绝对不应该提交
SENSITIVE_PATTERNS = [
    r".*\.db$",  # 数据库文件
    r".*\.sqlite3?$",  # SQLite数据库
    r".*\.env\.local$",  # 本地环境配置
    r".*\.env\.production$",  # 生产环境配置
    r".*config.*local.*\.json$",  # 本地配置文件
    r".*password.*",  # 包含password的文件
    r".*secret.*",  # 包含secret的文件
    r".*\.key$",  # 密钥文件
    r".*\.pem$",  # 证书文件
    r".*\.p12$",  # 证书文件
    r".*backup.*\.sql$",  # SQL备份文件
]

# 大文件模式 - 这些文件通常不应该提交
LARGE_FILE_PATTERNS = [
    r".*\.xlsx$",  # Excel文件
    r".*\.docx$",  # Word文档
    r".*\.pdf$",  # PDF文件
    r".*\.zip$",  # 压缩文件
    r".*\.tar\.gz$",  # 压缩文件
    r".*\.rar$",  # 压缩文件
    r".*\.7z$",  # 压缩文件
    r".*\.mp4$",  # 视频文件
    r".*\.avi$",  # 视频文件
    r".*\.mov$",  # 视频文件
]

# 临时文件模式 - 这些文件不应该提交
TEMP_FILE_PATTERNS = [
    r".*~$",  # 备份文件
    r".*\.tmp$",  # 临时文件
    r".*\.temp$",  # 临时文件
    r".*\.bak$",  # 备份文件
    r".*\.backup$",  # 备份文件
    r".*_temp\.py$",  # 临时Python文件
    r".*_backup\.py$",  # 备份Python文件
    r".*_fixed\.py$",  # 修复后的Python文件
    r"test_.*\.xlsx$",  # 测试Excel文件
    r"test_.*\.pdf$",  # 测试PDF文件
    r"test_.*\.docx$",  # 测试Word文档
    r"dummy\..*$",  # 虚拟文件
]

# 开发工具生成的文件 - 这些文件不应该提交
DEV_TOOL_PATTERNS = [
    r".*__pycache__.*",  # Python缓存
    r".*\.pyc$",  # Python字节码
    r".*\.pyo$",  # Python优化字节码
    r".*\.coverage$",  # 覆盖率文件
    r".*htmlcov.*",  # 覆盖率HTML报告
    r".*\.pytest_cache.*",  # Pytest缓存
    r".*\.mypy_cache.*",  # MyPy缓存
    r".*\.ruff_cache.*",  # Ruff缓存
    r".*\.DS_Store$",  # macOS系统文件
    r".*Thumbs\.db$",  # Windows缩略图
]

# 报告文件模式 - 这些文件通常不需要提交
REPORT_FILE_PATTERNS = [
    r".*_report\.txt$",
    r".*_report\.md$",
    r".*_REPORT\.md$",
    r".*_SUMMARY\.md$",
    r".*_PLAN\.md$",
    r".*_GUIDE\.md$",
    r".*_CHECKLIST\.md$",
    r".*performance_report.*",
    r".*executive_summary.*",
    r".*dependency_check.*\.txt$",
]


def get_git_staged_files() -> List[str]:
    """获取Git暂存区中的文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            check=False,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.split("\n") if f.strip()]
        print(f"警告: 无法获取Git暂存文件: {result.stderr}")
        return []
    except FileNotFoundError:
        print("警告: Git命令未找到，跳过Git检查")
        return []


def check_file_against_patterns(file_path: str, patterns: List[str]) -> bool:
    """检查文件是否匹配给定的模式"""
    for pattern in patterns:
        if re.match(pattern, file_path, re.IGNORECASE):
            return True
    return False


def get_file_size(file_path: Path) -> int:
    """获取文件大小（字节）"""
    try:
        return file_path.stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def check_file_content_for_sensitive_data(file_path: Path) -> List[str]:
    """检查文件内容是否包含敏感数据"""
    sensitive_keywords = [
        "password",
        "secret",
        "api_key",
        "token",
        "private_key",
        "database_url",
        "connection_string",
        "auth_token",
    ]

    issues = []

    try:
        # 只检查文本文件
        if file_path.suffix.lower() in [
            ".py",
            ".json",
            ".txt",
            ".md",
            ".yaml",
            ".yml",
            ".env",
        ]:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                for keyword in sensitive_keywords:
                    if keyword in content:
                        issues.append(f"包含敏感关键词: {keyword}")
    except Exception:
        # 忽略读取错误
        pass

    return issues


def main():
    """主检查函数"""
    print("🔍 开始GitHub提交前检查...")

    # 获取暂存的文件
    staged_files = get_git_staged_files()

    if not staged_files:
        print("✅ 没有暂存的文件需要检查")
        return 0

    print(f"📋 检查 {len(staged_files)} 个暂存文件...")

    issues_found = False

    for file_path in staged_files:
        full_path = PROJECT_ROOT / file_path
        file_issues = []

        # 检查敏感文件
        if check_file_against_patterns(file_path, SENSITIVE_PATTERNS):
            file_issues.append("🚨 敏感文件 - 不应该提交")
            issues_found = True

        # 检查大文件
        elif check_file_against_patterns(file_path, LARGE_FILE_PATTERNS):
            file_size = get_file_size(full_path)
            if file_size > 1024 * 1024:  # 1MB
                file_issues.append(
                    f"📦 大文件 ({file_size / 1024 / 1024:.1f}MB) - 考虑是否需要提交"
                )

        # 检查临时文件
        elif check_file_against_patterns(file_path, TEMP_FILE_PATTERNS):
            file_issues.append("🗑️ 临时文件 - 通常不应该提交")

        # 检查开发工具文件
        elif check_file_against_patterns(file_path, DEV_TOOL_PATTERNS):
            file_issues.append("🔧 开发工具生成文件 - 不应该提交")
            issues_found = True

        # 检查报告文件
        elif check_file_against_patterns(file_path, REPORT_FILE_PATTERNS):
            file_issues.append("📊 报告文件 - 考虑是否需要提交")

        # 检查文件内容
        if full_path.exists():
            content_issues = check_file_content_for_sensitive_data(full_path)
            if content_issues:
                file_issues.extend([f"🔐 {issue}" for issue in content_issues])
                issues_found = True

        # 输出问题
        if file_issues:
            print(f"\n⚠️  {file_path}:")
            for issue in file_issues:
                print(f"   {issue}")

    if issues_found:
        print("\n❌ 发现严重问题！建议解决后再提交。")
        print("\n💡 建议操作:")
        print("   1. 检查 .gitignore 文件是否正确配置")
        print("   2. 使用 'git reset HEAD <file>' 取消暂存问题文件")
        print("   3. 确认敏感信息已被移除")
        return 1
    print("\n✅ 所有检查通过！可以安全提交。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
