#!/usr/bin/env python3
"""TTK主题系统使用示例

展示如何在MiniCRM项目中使用TTK主题系统。
"""

import os
import sys


# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minicrm.ui.ttk_base.theme_manager import (
    TTKThemeManager,
    get_global_ttk_theme_manager,
)


def basic_usage_example():
    """基础使用示例"""
    print("📚 TTK主题系统基础使用示例")
    print("=" * 50)

    # 1. 创建主题管理器
    theme_manager = TTKThemeManager()

    # 2. 获取可用主题
    themes = theme_manager.get_available_themes()
    print(f"可用主题: {list(themes.keys())}")

    # 3. 切换主题
    print(f"\n当前主题: {theme_manager.get_current_theme()}")

    # 切换到深色主题
    success = theme_manager.set_theme("dark")
    print(f"切换到深色主题: {'成功' if success else '失败'}")
    print(f"当前主题: {theme_manager.get_current_theme()}")

    # 4. 获取主题颜色
    colors = theme_manager.get_theme_colors("dark")
    print("\n深色主题颜色:")
    for key, value in list(colors.items())[:5]:  # 只显示前5个
        print(f"  {key}: {value}")

    # 5. 重置为默认主题
    theme_manager.reset_to_default()
    print(f"\n重置后当前主题: {theme_manager.get_current_theme()}")


def custom_theme_example():
    """自定义主题示例"""
    print("\n🎨 自定义主题创建示例")
    print("=" * 50)

    theme_manager = TTKThemeManager()

    # 创建自定义主题
    success = theme_manager.create_custom_theme(
        theme_id="my_theme",
        theme_name="我的专属主题",
        base_theme="light",
        colors={
            "primary": "#E91E63",  # 粉红色主色调
            "secondary": "#9C27B0",  # 紫色次要色
            "success": "#4CAF50",  # 绿色成功色
            "bg_primary": "#FCE4EC",  # 浅粉色背景
            "text_primary": "#880E4F",  # 深粉色文本
        },
        fonts={
            "default": {"family": "Microsoft YaHei UI", "size": 10, "weight": "normal"},
            "heading": {"family": "Microsoft YaHei UI", "size": 14, "weight": "bold"},
        },
        spacing={"padding_small": 6, "padding_medium": 12, "padding_large": 18},
    )

    if success:
        print("✅ 自定义主题创建成功")

        # 应用自定义主题
        theme_manager.set_theme("my_theme")
        print(f"当前主题: {theme_manager.get_current_theme()}")

        # 显示自定义主题配置
        config = theme_manager.get_theme_config("my_theme")
        print(f"主题名称: {config['name']}")
        print(f"主色调: {config['colors']['primary']}")
        print(f"背景色: {config['colors']['bg_primary']}")
    else:
        print("❌ 自定义主题创建失败")


def theme_callback_example():
    """主题变化回调示例"""
    print("\n🔔 主题变化回调示例")
    print("=" * 50)

    theme_manager = TTKThemeManager()

    # 定义回调函数
    def on_theme_changed(theme_id):
        print(f"🎨 主题已切换到: {theme_id}")
        colors = theme_manager.get_theme_colors(theme_id)
        print(f"   主色调: {colors.get('primary', 'Unknown')}")

    # 添加回调
    theme_manager.add_theme_change_callback(on_theme_changed)

    # 切换主题触发回调
    print("切换主题...")
    theme_manager.set_theme("dark")
    theme_manager.set_theme("light")
    theme_manager.set_theme("high_contrast")

    # 移除回调
    theme_manager.remove_theme_change_callback(on_theme_changed)
    print("\n回调已移除，后续切换不会触发回调")
    theme_manager.set_theme("default")


def global_theme_manager_example():
    """全局主题管理器示例"""
    print("\n🌍 全局主题管理器示例")
    print("=" * 50)

    # 获取全局主题管理器实例
    global_manager = get_global_ttk_theme_manager()

    print(f"全局管理器当前主题: {global_manager.get_current_theme()}")

    # 使用全局函数应用主题
    from minicrm.ui.ttk_base.theme_manager import apply_global_ttk_theme

    success = apply_global_ttk_theme("dark")
    print(f"全局应用深色主题: {'成功' if success else '失败'}")
    print(f"全局管理器当前主题: {global_manager.get_current_theme()}")


def theme_export_import_example():
    """主题导入导出示例"""
    print("\n💾 主题导入导出示例")
    print("=" * 50)

    import os
    import tempfile

    theme_manager = TTKThemeManager()

    # 创建一个自定义主题用于导出
    theme_manager.create_custom_theme(
        "export_theme",
        "导出测试主题",
        colors={"primary": "#FF9800", "bg_primary": "#FFF3E0"},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        export_file = os.path.join(temp_dir, "my_theme.json")

        # 导出主题
        success = theme_manager.export_theme("export_theme", export_file)
        if success:
            print(f"✅ 主题已导出到: {export_file}")

            # 删除原主题
            theme_manager.delete_custom_theme("export_theme")
            print("原主题已删除")

            # 重新导入主题
            success = theme_manager.import_theme(export_file, "imported_theme")
            if success:
                print("✅ 主题导入成功")

                # 验证导入的主题
                themes = theme_manager.get_available_themes()
                if "imported_theme" in themes:
                    print(f"导入的主题: {themes['imported_theme']}")

                    # 应用导入的主题
                    theme_manager.set_theme("imported_theme")
                    colors = theme_manager.get_theme_colors("imported_theme")
                    print(f"导入主题的主色调: {colors.get('primary')}")
            else:
                print("❌ 主题导入失败")
        else:
            print("❌ 主题导出失败")


def main():
    """主函数"""
    print("🎨 MiniCRM TTK主题系统使用示例")
    print("=" * 60)

    try:
        # 基础使用
        basic_usage_example()

        # 自定义主题
        custom_theme_example()

        # 主题回调
        theme_callback_example()

        # 全局管理器
        global_theme_manager_example()

        # 导入导出
        theme_export_import_example()

        print("\n🎉 所有示例运行完成！")
        print("\n💡 提示:")
        print("   - 在GUI应用中，主题切换会立即更新界面样式")
        print("   - 可以使用主题编辑器进行可视化主题编辑")
        print("   - 主题配置会自动保存到用户配置目录")
        print("   - 支持主题的导入导出和分享")

    except Exception as e:
        print(f"❌ 示例运行失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
