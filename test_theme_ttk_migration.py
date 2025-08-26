#!/usr/bin/env python3
"""测试TTK主题系统迁移

验证主题系统是否成功从Qt迁移到TTK
"""

import os
import sys


# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_theme_manager_import():
    """测试主题管理器导入"""
    try:
        # 测试从主入口导入
        from minicrm.ui.themes.theme_manager import ThemeManager

        print("✓ 主题管理器导入成功")

        # 测试TTK主题管理器导入
        from minicrm.ui.ttk_base.theme_manager import TTKThemeManager

        print("✓ TTK主题管理器导入成功")

        return True
    except ImportError as e:
        print(f"✗ 主题管理器导入失败: {e}")
        return False


def test_component_styler_import():
    """测试组件样式应用器导入"""
    try:
        from minicrm.ui.themes.component_styler import ComponentStyler

        print("✓ 组件样式应用器导入成功")
        return True
    except ImportError as e:
        print(f"✗ 组件样式应用器导入失败: {e}")
        return False


def test_shadow_effects_import():
    """测试阴影效果导入"""
    try:
        from minicrm.ui.themes.shadow_effects import get_shadow_manager

        print("✓ 阴影效果管理器导入成功")
        return True
    except ImportError as e:
        print(f"✗ 阴影效果管理器导入失败: {e}")
        return False


def test_no_qt_dependencies():
    """测试是否还有Qt依赖"""
    try:
        # 尝试导入主题相关模块，不应该有PySide6依赖

        # 检查是否意外导入了PySide6
        import sys

        qt_modules = [
            name for name in sys.modules.keys() if "PySide6" in name or "PyQt" in name
        ]

        if qt_modules:
            print(f"✗ 发现Qt依赖: {qt_modules}")
            return False
        print("✓ 无Qt依赖检测通过")
        return True

    except Exception as e:
        print(f"✗ Qt依赖检测失败: {e}")
        return False


def test_theme_manager_functionality():
    """测试主题管理器基本功能"""
    try:
        import tkinter as tk

        from minicrm.ui.themes.theme_manager import ThemeManager

        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口

        # 创建主题管理器
        theme_manager = ThemeManager(root)

        # 测试获取可用主题
        themes = theme_manager.get_available_themes()
        print(f"✓ 可用主题: {list(themes.keys())}")

        # 测试获取当前主题
        current_theme = theme_manager.get_current_theme()
        print(f"✓ 当前主题: {current_theme}")

        # 清理
        root.destroy()

        return True
    except Exception as e:
        print(f"✗ 主题管理器功能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("开始TTK主题系统迁移测试...")
    print("=" * 50)

    tests = [
        ("主题管理器导入", test_theme_manager_import),
        ("组件样式应用器导入", test_component_styler_import),
        ("阴影效果导入", test_shadow_effects_import),
        ("Qt依赖检测", test_no_qt_dependencies),
        ("主题管理器功能", test_theme_manager_functionality),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n测试: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"测试失败: {test_name}")

    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✓ 所有测试通过！TTK主题系统迁移成功。")
        return True
    print("✗ 部分测试失败，需要进一步检查。")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
