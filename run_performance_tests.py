#!/usr/bin/env python3
"""MiniCRM性能基准测试快速运行脚本

为任务10提供便捷的性能测试执行入口：
- 一键运行完整的性能基准测试
- 自动生成性能报告
- 提供测试结果摘要

使用方法:
    python run_performance_tests.py
    python run_performance_tests.py --verbose
    python run_performance_tests.py --output-dir custom_reports

作者: MiniCRM开发团队
"""

from pathlib import Path
import sys


# 确保项目路径正确
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    print("🚀 MiniCRM性能基准测试启动器")
    print("=" * 50)

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        return 1

    # 检查必要的依赖
    try:
        import psutil

        print("✅ psutil 已安装")
    except ImportError:
        print("❌ 错误: 缺少psutil依赖，请运行: pip install psutil")
        return 1

    # 检查可选依赖
    optional_deps = {"matplotlib": "图表生成", "reportlab": "PDF报告生成"}

    for dep, description in optional_deps.items():
        try:
            __import__(dep)
            print(f"✅ {dep} 已安装 ({description})")
        except ImportError:
            print(f"⚠️  {dep} 未安装，将跳过{description}")

    print()

    # 运行性能测试
    try:
        from tests.performance.main_performance_test import main as run_tests

        # 传递命令行参数
        sys.argv[0] = str(
            project_root / "tests" / "performance" / "main_performance_test.py"
        )

        return run_tests()

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保项目结构正确且所有文件都存在")
        return 1

    except Exception as e:
        print(f"❌ 运行错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
