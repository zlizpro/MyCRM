#!/usr/bin/env python3
"""MiniCRM 依赖迁移脚本

此脚本帮助从旧的依赖配置迁移到优化后的配置，
保持sqlite3架构，移除未使用的依赖。
"""

from pathlib import Path
import subprocess


def run_command(cmd: str, description: str) -> bool:
    """执行命令并显示结果"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description}完成")
        if result.stdout:
            print(f"输出: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        if e.stderr:
            print(f"错误: {e.stderr.strip()}")
        return False


def backup_current_env():
    """备份当前环境"""
    print("📦 备份当前环境...")

    # 导出当前安装的包
    if run_command("pip freeze > requirements_backup.txt", "导出当前依赖"):
        print("✅ 依赖备份已保存到 requirements_backup.txt")

    return True


def clean_old_dependencies():
    """清理旧的未使用依赖"""
    print("\n🧹 清理未使用的依赖...")

    # 需要卸载的包列表
    unused_packages = [
        "SQLAlchemy",
        "alembic",
        "python-docx",
        "docxtpl",
        "openpyxl",
        "pydantic",
        "loguru",
        "seaborn",
        "click",
        "rich",
        "tqdm",
        "cachetools",
        "PyYAML",
    ]

    for package in unused_packages:
        run_command(f"pip uninstall -y {package}", f"卸载 {package}")


def install_core_dependencies():
    """安装核心依赖"""
    print("\n📥 安装优化后的核心依赖...")

    # 重新安装项目（仅核心依赖）
    if run_command("pip install -e .", "安装核心依赖"):
        print("✅ 核心依赖安装完成")
        return True
    return False


def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")

    # 检查关键包是否正确安装
    key_packages = ["tkinter", "pandas", "numpy", "matplotlib", "reportlab", "psutil"]

    for package in key_packages:
        if run_command(
            f"python -c 'import {package.lower()}; print(f\"{package} 版本: {{{package.lower()}.__version__}}\")'",
            f"验证 {package}",
        ):
            continue
        print(f"❌ {package} 验证失败")
        return False

    print("✅ 所有核心依赖验证通过")
    return True


def show_optional_installs():
    """显示可选安装选项"""
    print("\n🎯 可选功能安装:")
    print("如需额外功能，可以安装以下可选依赖组:")
    print()
    print("📄 文档处理 (Word/Excel):  pip install -e '.[documents]'")
    print("✅ 数据验证 (Pydantic):   pip install -e '.[validation]'")
    print("📊 图表美化 (Seaborn):    pip install -e '.[charts]'")
    print("🖥️  CLI工具:              pip install -e '.[cli]'")
    print("🔧 工具库:               pip install -e '.[utils]'")
    print("🚀 开发工具:             pip install -e '.[dev]'")
    print("📦 完整安装:             pip install -e '.[full]'")


def main():
    """主函数"""
    print("🚀 MiniCRM 依赖迁移脚本")
    print("=" * 50)
    print("此脚本将:")
    print("1. 备份当前环境")
    print("2. 清理未使用的依赖")
    print("3. 安装优化后的核心依赖")
    print("4. 验证安装")
    print()

    # 确认执行
    response = input("是否继续? (y/N): ").lower().strip()
    if response != "y":
        print("❌ 迁移已取消")
        return

    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        return

    # 执行迁移步骤
    steps = [
        backup_current_env,
        clean_old_dependencies,
        install_core_dependencies,
        verify_installation,
    ]

    for step in steps:
        if not step():
            print("❌ 迁移失败，请检查错误信息")
            return

    print("\n🎉 依赖迁移完成!")
    print("=" * 50)

    # 显示优化结果
    print("📊 优化结果:")
    run_command(
        "pip list | grep -E '(pandas|numpy|matplotlib|reportlab|psutil)'",
        "显示已安装的核心依赖",
    )

    show_optional_installs()

    print("\n✨ 迁移成功! 项目现在使用优化后的依赖配置。")


if __name__ == "__main__":
    main()
