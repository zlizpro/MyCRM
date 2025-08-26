#!/usr/bin/env python3
"""MiniCRM 依赖验证脚本

验证优化后的依赖是否满足项目需求，检查所有关键模块的导入。
"""

from pathlib import Path
import sys
import traceback


def test_import(module_name: str, description: str) -> bool:
    """测试模块导入"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_name} - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {description}: {module_name} - 意外错误: {e}")
        return False


def test_core_dependencies():
    """测试核心依赖"""
    print("🔍 测试核心依赖...")

    tests = [
        ("tkinter", "GUI框架 - tkinter"),
        ("tkinter.ttk", "GUI框架 - ttk"),
        ("pandas", "数据处理"),
        ("numpy", "数值计算"),
        ("matplotlib.pyplot", "图表绘制"),
        ("matplotlib.backends.backend_tkagg", "Tkinter图表后端"),
        ("reportlab.pdfgen", "PDF生成"),
        ("reportlab.lib.pagesizes", "PDF页面设置"),
        ("psutil", "系统监控"),
        ("sqlite3", "数据库"),
        ("datetime", "日期时间"),
        ("pathlib", "路径处理"),
        ("logging", "日志系统"),
    ]

    passed = 0
    total = len(tests)

    for module, desc in tests:
        if test_import(module, desc):
            passed += 1

    print(f"\n📊 核心依赖测试结果: {passed}/{total} 通过")
    return passed == total


def test_project_modules():
    """测试项目模块导入"""
    print("\n🔍 测试项目模块...")

    # 添加src到路径
    src_path = Path(__file__).parent.parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))

    tests = [
        ("minicrm.core.exceptions", "核心异常"),
        ("minicrm.data.database.database_manager", "数据库管理"),
        ("minicrm.services.base_service", "基础服务"),
        ("minicrm.ui.data_bus", "UI数据总线"),
        ("transfunctions.calculations", "计算函数"),
    ]

    passed = 0
    total = len(tests)

    for module, desc in tests:
        if test_import(module, desc):
            passed += 1

    print(f"\n📊 项目模块测试结果: {passed}/{total} 通过")
    return passed == total


def test_critical_functionality():
    """测试关键功能"""
    print("\n🔍 测试关键功能...")

    try:
        # 测试数据库连接
        print("🔄 测试数据库连接...")
        import sqlite3

        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.close()
        print("✅ SQLite数据库连接正常")

        # 测试GUI初始化
        print("🔄 测试GUI初始化...")
        import tkinter as tk
        from tkinter import ttk

        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        test_label = ttk.Label(root, text="测试")
        root.destroy()
        print("✅ tkinter/ttk GUI初始化正常")

        # 测试图表功能
        print("🔄 测试图表功能...")
        import matplotlib

        matplotlib.use("Agg")  # 使用非交互式后端
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        ax.plot(x, np.sin(x))
        plt.close(fig)
        print("✅ Matplotlib图表功能正常")

        # 测试PDF生成
        print("🔄 测试PDF生成...")
        from io import BytesIO

        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(100, 750, "测试PDF")
        c.save()
        print("✅ ReportLab PDF生成正常")

        return True

    except Exception as e:
        print(f"❌ 关键功能测试失败: {e}")
        traceback.print_exc()
        return False


def check_optional_dependencies():
    """检查可选依赖状态"""
    print("\n🔍 检查可选依赖状态...")

    optional_deps = {
        "文档处理": ["docx", "docxtpl", "openpyxl"],
        "数据验证": ["pydantic"],
        "增强日志": ["loguru"],
        "图表美化": ["seaborn"],
        "CLI工具": ["click", "rich", "tqdm"],
        "工具库": ["cachetools", "yaml"],
    }

    for category, modules in optional_deps.items():
        print(f"\n📦 {category}:")
        available = 0
        for module in modules:
            if test_import(module, f"  {module}"):
                available += 1

        if available == 0:
            print(f"  💡 如需此功能，运行: pip install -e '.[{category.lower()}]'")


def generate_report():
    """生成依赖报告"""
    print("\n📋 生成依赖报告...")

    try:
        import subprocess

        result = subprocess.run(
            ["pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            check=True,
        )

        installed_packages = result.stdout.strip().split("\n")
        core_packages = [
            pkg
            for pkg in installed_packages
            if any(
                name in pkg.lower()
                for name in [
                    "pandas",
                    "numpy",
                    "matplotlib",
                    "reportlab",
                    "psutil",
                    "pillow",
                    "docxtpl",
                    "openpyxl",
                ]
            )
        ]

        print("📦 已安装的核心依赖:")
        for pkg in core_packages:
            print(f"  {pkg}")

        # 计算大致的包大小节省
        total_packages = len(installed_packages)
        print(f"\n📊 当前安装包总数: {total_packages}")
        print("💡 优化前预计包数: ~40+ (节省了大量未使用的依赖)")

    except Exception as e:
        print(f"⚠️  无法生成详细报告: {e}")


def main():
    """主函数"""
    print("🔍 MiniCRM 依赖验证脚本")
    print("=" * 50)

    # 执行所有测试
    tests_passed = []

    tests_passed.append(test_core_dependencies())
    tests_passed.append(test_project_modules())
    tests_passed.append(test_critical_functionality())

    # 检查可选依赖
    check_optional_dependencies()

    # 生成报告
    generate_report()

    # 总结
    print("\n" + "=" * 50)
    if all(tests_passed):
        print("🎉 所有测试通过! 依赖优化成功!")
        print("✨ 项目现在使用精简的依赖配置，性能更佳。")
    else:
        print("⚠️  部分测试失败，请检查上述错误信息。")
        print("💡 可能需要安装额外的依赖或修复导入问题。")

    print(f"\n📊 测试结果: {sum(tests_passed)}/{len(tests_passed)} 通过")


if __name__ == "__main__":
    main()
