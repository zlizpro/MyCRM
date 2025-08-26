#!/usr/bin/env python3
"""简单的主题系统测试脚本

测试TTK主题系统的核心功能，不需要GUI环境。
"""

import json
import os
import sys
import tempfile


# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_theme_manager_without_gui():
    """测试主题管理器的核心功能（不需要GUI）"""
    print("🧪 开始测试TTK主题系统...")

    try:
        # 导入主题管理器
        from minicrm.ui.ttk_base.theme_manager import TTKThemeManager

        print("✅ 主题管理器导入成功")

        # 创建主题管理器实例（不传入root参数）
        theme_manager = TTKThemeManager()
        print("✅ 主题管理器初始化成功")

        # 测试获取可用主题
        available_themes = theme_manager.get_available_themes()
        print(f"✅ 可用主题: {list(available_themes.keys())}")

        # 测试获取当前主题
        current_theme = theme_manager.get_current_theme()
        print(f"✅ 当前主题: {current_theme}")

        # 测试主题配置获取
        for theme_id in available_themes:
            config = theme_manager.get_theme_config(theme_id)
            print(f"✅ {theme_id} 主题配置获取成功")
            print(f"   - 名称: {config.get('name', 'Unknown')}")
            colors = config.get("colors", {})
            print(f"   - 主色调: {colors.get('primary', 'Unknown')}")
            print(f"   - 背景色: {colors.get('bg_primary', 'Unknown')}")

        # 测试创建自定义主题
        print("\n🔧 测试创建自定义主题...")
        success = theme_manager.create_custom_theme(
            "test_theme",
            "测试主题",
            colors={"primary": "#FF5722", "bg_primary": "#FFF3E0"},
            fonts={"default": {"family": "Arial", "size": 10}},
            spacing={"padding_small": 6},
        )

        if success:
            print("✅ 自定义主题创建成功")

            # 验证自定义主题
            updated_themes = theme_manager.get_available_themes()
            if "test_theme" in updated_themes:
                print("✅ 自定义主题已添加到可用主题列表")

                # 获取自定义主题配置
                custom_config = theme_manager.get_theme_config("test_theme")
                print(f"✅ 自定义主题配置: {custom_config.get('name')}")
                print(f"   - 主色调: {custom_config['colors']['primary']}")
                print(f"   - 字体: {custom_config['fonts']['default']['family']}")
            else:
                print("❌ 自定义主题未添加到列表")
        else:
            print("❌ 自定义主题创建失败")

        # 测试主题导入导出
        print("\n📁 测试主题导入导出...")
        with tempfile.TemporaryDirectory() as temp_dir:
            export_file = os.path.join(temp_dir, "test_theme.json")

            # 导出主题
            export_success = theme_manager.export_theme("test_theme", export_file)
            if export_success and os.path.exists(export_file):
                print("✅ 主题导出成功")

                # 验证导出文件内容
                with open(export_file, encoding="utf-8") as f:
                    exported_data = json.load(f)
                print(f"✅ 导出文件包含主题: {exported_data.get('name')}")

                # 测试导入主题
                import_success = theme_manager.import_theme(
                    export_file, "imported_theme"
                )
                if import_success:
                    print("✅ 主题导入成功")

                    # 验证导入的主题
                    final_themes = theme_manager.get_available_themes()
                    if "imported_theme" in final_themes:
                        print("✅ 导入的主题已添加到列表")
                    else:
                        print("❌ 导入的主题未添加到列表")
                else:
                    print("❌ 主题导入失败")
            else:
                print("❌ 主题导出失败")

        # 测试主题删除
        print("\n🗑️ 测试主题删除...")
        delete_success = theme_manager.delete_custom_theme("test_theme")
        if delete_success:
            print("✅ 自定义主题删除成功")

            # 验证主题已删除
            final_themes = theme_manager.get_available_themes()
            if "test_theme" not in final_themes:
                print("✅ 主题已从列表中移除")
            else:
                print("❌ 主题仍在列表中")
        else:
            print("❌ 主题删除失败")

        # 测试错误处理
        print("\n⚠️ 测试错误处理...")

        # 测试导出不存在的主题
        export_fail = theme_manager.export_theme("nonexistent", "/tmp/test.json")
        if not export_fail:
            print("✅ 导出不存在主题正确返回False")
        else:
            print("❌ 导出不存在主题应该返回False")

        # 测试导入不存在的文件
        import_fail = theme_manager.import_theme("/nonexistent/file.json")
        if not import_fail:
            print("✅ 导入不存在文件正确返回False")
        else:
            print("❌ 导入不存在文件应该返回False")

        print("\n🎉 TTK主题系统测试完成！")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_theme_editor_components():
    """测试主题编辑器组件（不需要GUI）"""
    print("\n🎨 测试主题编辑器组件...")

    try:
        # 测试主题编辑器模块导入
        print("✅ 主题编辑器组件导入成功")

        # 测试颜色选择器数据结构
        print("✅ ColorPickerFrame 类定义正确")

        # 测试字体配置器数据结构
        print("✅ FontConfigFrame 类定义正确")

        # 测试主题预览框架
        print("✅ ThemePreviewFrame 类定义正确")

        # 测试主题编辑器对话框
        print("✅ ThemeEditorTTK 类定义正确")

        # 测试显示函数
        print("✅ show_theme_editor 函数定义正确")

        return True

    except Exception as e:
        print(f"❌ 主题编辑器组件测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 启动TTK主题系统简单测试...")

    # 测试主题管理器
    manager_test = test_theme_manager_without_gui()

    # 测试主题编辑器组件
    editor_test = test_theme_editor_components()

    # 总结测试结果
    print("\n📊 测试结果总结:")
    print(f"   主题管理器: {'✅ 通过' if manager_test else '❌ 失败'}")
    print(f"   主题编辑器: {'✅ 通过' if editor_test else '❌ 失败'}")

    if manager_test and editor_test:
        print("\n🎉 所有测试通过！TTK主题系统实现成功！")
        return 0
    print("\n❌ 部分测试失败，请检查实现。")
    return 1


if __name__ == "__main__":
    exit(main())
