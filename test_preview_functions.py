#!/usr/bin/env python3
"""
设置预览功能验证脚本
验证新增的预览功能是否正确实现
"""

import sys
from pathlib import Path


# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


def test_base_settings_page():
    """测试基础设置页面的预览功能"""
    print("测试基础设置页面...")

    from minicrm.ui.settings_pages.base_settings_page import BaseSettingsPage

    # 检查预览相关方法是否存在
    methods_to_check = [
        "_start_preview_mode",
        "_end_preview_mode",
        "_get_current_ui_values",
        "_restore_original_values",
        "_show_preview_notification",
        "_hide_preview_notification",
        "_apply_preview_effect",
        "_create_preview_button",
        "_create_reset_button",
    ]

    for method in methods_to_check:
        if hasattr(BaseSettingsPage, method):
            print(f"  ✓ {method} 方法已实现")
        else:
            print(f"  ✗ {method} 方法缺失")

    print("基础设置页面测试完成\n")


def test_general_settings_page():
    """测试通用设置页面的预览功能"""
    print("测试通用设置页面...")

    from minicrm.ui.settings_pages.general_settings_page import GeneralSettingsPage

    # 检查预览相关方法是否存在
    preview_methods = [
        "_preview_language",
        "_preview_startup_page",
        "_test_confirm_delete",
        "_apply_tooltips_preview",
        "_create_language_setting_widget",
        "_create_startup_page_setting_widget",
        "_create_confirm_delete_setting_widget",
        "_create_tooltips_setting_widget",
    ]

    for method in preview_methods:
        if hasattr(GeneralSettingsPage, method):
            print(f"  ✓ {method} 方法已实现")
        else:
            print(f"  ✗ {method} 方法缺失")

    print("通用设置页面测试完成\n")


def test_theme_settings_page():
    """测试主题设置页面的预览功能"""
    print("测试主题设置页面...")

    from minicrm.ui.settings_pages.theme_settings_page import ThemeSettingsPage

    # 检查现有和新增的预览方法
    preview_methods = [
        "_apply_theme_preview",
        "_apply_font_preview",
        "_apply_opacity_preview",
        "_show_preview_notification",
        "_hide_preview_notification",
        "_restore_original_settings",
        "_get_current_ui_values",
        "_restore_original_values",
    ]

    for method in preview_methods:
        if hasattr(ThemeSettingsPage, method):
            print(f"  ✓ {method} 方法已实现")
        else:
            print(f"  ✗ {method} 方法缺失")

    print("主题设置页面测试完成\n")


def test_database_settings_page():
    """测试数据库设置页面的预览功能"""
    print("测试数据库设置页面...")

    from minicrm.ui.settings_pages.database_settings_page import DatabaseSettingsPage

    # 检查预览相关方法
    preview_methods = [
        "_preview_auto_backup",
        "_preview_backup_schedule",
        "_create_auto_backup_widget",
        "_create_backup_interval_widget",
        "_get_current_ui_values",
    ]

    for method in preview_methods:
        if hasattr(DatabaseSettingsPage, method):
            print(f"  ✓ {method} 方法已实现")
        else:
            print(f"  ✗ {method} 方法缺失")

    print("数据库设置页面测试完成\n")


def test_system_settings_page():
    """测试系统设置页面的预览功能"""
    print("测试系统设置页面...")

    from minicrm.ui.settings_pages.system_settings_page import SystemSettingsPage

    # 检查预览相关方法
    preview_methods = [
        "_preview_log_level",
        "_preview_performance_monitoring",
        "_preview_cache_size",
        "_create_log_level_widget",
        "_create_performance_monitoring_widget",
        "_create_cache_size_widget",
        "_get_current_ui_values",
    ]

    for method in preview_methods:
        if hasattr(SystemSettingsPage, method):
            print(f"  ✓ {method} 方法已实现")
        else:
            print(f"  ✗ {method} 方法缺失")

    print("系统设置页面测试完成\n")


def test_preview_functionality():
    """测试预览功能的基本逻辑"""
    print("测试预览功能基本逻辑...")

    try:
        from minicrm.services.settings_service import SettingsService

        settings_service = SettingsService()
        print("  ✓ 设置服务创建成功")

        # 测试设置服务的基本功能
        test_setting = settings_service.get_setting("general", "language")
        print(f"  ✓ 获取设置成功: language = {test_setting}")

    except Exception as e:
        print(f"  ✗ 设置服务测试失败: {e}")

    print("预览功能基本逻辑测试完成\n")


def main():
    """主函数"""
    print("=" * 60)
    print("MiniCRM 设置界面实时预览功能验证")
    print("=" * 60)
    print()

    try:
        # 测试各个组件
        test_base_settings_page()
        test_general_settings_page()
        test_theme_settings_page()
        test_database_settings_page()
        test_system_settings_page()
        test_preview_functionality()

        print("=" * 60)
        print("功能验证完成！")
        print()
        print("实现的预览功能包括：")
        print("1. 基础设置页面 - 通用预览框架和UI组件")
        print("2. 通用设置页面 - 语言预览、启动页面预览、工具提示实时切换")
        print("3. 主题设置页面 - 主题、字体、透明度实时预览（改进）")
        print("4. 数据库设置页面 - 自动备份预览、备份计划预览")
        print("5. 系统设置页面 - 日志级别预览、性能监控状态预览")
        print("=" * 60)

    except Exception as e:
        print(f"验证过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
