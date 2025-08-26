#!/usr/bin/env python3
"""测试仪表盘实现

验证任务5.2的完整实现：
- transfunctions函数使用
- 仪表盘数据生成
- UI组件创建
"""

import os
import sys


# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_transfunctions_import():
    """测试transfunctions导入"""
    print("🔍 测试transfunctions导入...")

    try:
        from transfunctions import (
            calculate_customer_value_score,
            calculate_growth_rate,
            format_currency,
            generate_dashboard_summary,
        )

        print("✅ transfunctions导入成功")

        # 测试format_currency
        formatted = format_currency(123456.78)
        print(f"   format_currency(123456.78) = {formatted}")

        # 测试calculate_growth_rate
        growth = calculate_growth_rate(120, 100)
        print(f"   calculate_growth_rate(120, 100) = {growth}%")

        return True

    except ImportError as e:
        print(f"❌ transfunctions导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ transfunctions测试失败: {e}")
        return False


def test_dashboard_complete_import():
    """测试仪表盘组件导入"""
    print("\n🔍 测试仪表盘组件导入...")

    try:
        from minicrm.ui.dashboard_complete import DashboardComplete

        print("✅ DashboardComplete导入成功")
        return True

    except ImportError as e:
        print(f"❌ DashboardComplete导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ DashboardComplete测试失败: {e}")
        return False


def test_matplotlib_availability():
    """测试matplotlib可用性"""
    print("\n🔍 测试matplotlib可用性...")

    try:
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        import matplotlib.pyplot as plt

        print("✅ matplotlib可用 - 将显示完整图表")
        return True

    except ImportError:
        print("⚠️  matplotlib不可用 - 将显示文本图表")
        return False


def test_dashboard_data_generation():
    """测试仪表盘数据生成"""
    print("\n🔍 测试仪表盘数据生成...")

    try:
        from transfunctions import generate_dashboard_summary

        # 创建模拟DAO
        class MockDAO:
            def count(self):
                return 156

            def count_by_date_range(self, start, end):
                return 12

            def count_active_customers(self, days):
                return 89

            def count_active_suppliers(self, days):
                return 23

        customer_dao = MockDAO()
        supplier_dao = MockDAO()

        # 生成仪表盘数据
        dashboard_data = generate_dashboard_summary(
            customer_dao, supplier_dao, include_charts=True
        )

        print("✅ 仪表盘数据生成成功")
        print(f"   关键指标数量: {len(dashboard_data.get('metrics', []))}")
        print(f"   图表数量: {len(dashboard_data.get('charts', {}))}")
        print(f"   快速操作数量: {len(dashboard_data.get('quick_actions', []))}")
        print(f"   系统预警数量: {len(dashboard_data.get('alerts', []))}")

        return True

    except Exception as e:
        print(f"❌ 仪表盘数据生成失败: {e}")
        return False


def test_dashboard_ui_creation():
    """测试仪表盘UI创建"""
    print("\n🔍 测试仪表盘UI创建...")

    try:
        import tkinter as tk

        from minicrm.ui.dashboard_complete import DashboardComplete

        # 创建测试窗口
        root = tk.Tk()
        root.title("仪表盘测试")
        root.geometry("800x600")

        # 创建仪表盘组件
        dashboard = DashboardComplete(root)
        dashboard.pack(fill="both", expand=True)

        print("✅ 仪表盘UI创建成功")
        print("   注意: 窗口将在3秒后自动关闭")

        # 3秒后关闭窗口
        root.after(3000, root.destroy)
        root.mainloop()

        return True

    except Exception as e:
        print(f"❌ 仪表盘UI创建失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始测试仪表盘实现 (任务5.2)")
    print("=" * 50)

    tests = [
        test_transfunctions_import,
        test_dashboard_complete_import,
        test_matplotlib_availability,
        test_dashboard_data_generation,
        test_dashboard_ui_creation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")

    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！仪表盘实现完成")
        return True
    print("⚠️  部分测试失败，需要修复")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
