"""业务对话框演示

演示SettingsDialogTTK、ImportDialogTTK和ExportDialogTTK的使用方法。

作者: MiniCRM开发团队
"""

import tkinter as tk
from tkinter import ttk
from unittest.mock import Mock

from src.minicrm.services.import_export_service import ImportExportService
from src.minicrm.services.settings_service import SettingsService
from src.minicrm.ui.ttk_base.export_dialog_ttk import (
    show_export_dialog,
)
from src.minicrm.ui.ttk_base.import_dialog_ttk import (
    show_import_dialog,
)

# 导入对话框类
from src.minicrm.ui.ttk_base.settings_dialog_ttk import (
    show_settings_dialog,
)


class BusinessDialogsDemo:
    """业务对话框演示类"""

    def __init__(self):
        """初始化演示"""
        self.root = tk.Tk()
        self.root.title("业务对话框演示")
        self.root.geometry("400x300")

        # 创建模拟服务
        self.setup_mock_services()

        # 创建界面
        self.setup_ui()

    def setup_mock_services(self):
        """设置模拟服务"""
        # 模拟设置服务
        self.settings_service = Mock(spec=SettingsService)
        self.settings_service._validate_setting_value = Mock()
        self.settings_service.get_all_settings.return_value = {
            "theme": {
                "theme_name": "default",
                "primary_color": "#007BFF",
                "font_family": "Microsoft YaHei UI",
                "font_size": 9,
                "window_opacity": 1.0,
                "enable_animations": True,
            },
            "database": {
                "auto_backup": True,
                "backup_interval": "daily",
                "max_backups": 10,
                "backup_location": "/backup",
                "compress_backups": True,
            },
            "system": {
                "log_level": "INFO",
                "enable_performance_monitoring": False,
                "cache_size": 100,
                "max_log_files": 5,
                "enable_crash_reporting": True,
            },
            "ui": {
                "window_width": 1200,
                "window_height": 800,
                "window_maximized": False,
                "sidebar_width": 250,
                "show_status_bar": True,
                "toolbar_style": "icons_and_text",
            },
        }

        # 模拟导入导出服务
        self.import_export_service = Mock(spec=ImportExportService)
        self.import_export_service.export_data.return_value = "/test/export.xlsx"
        self.import_export_service.import_data.return_value = {
            "success_count": 10,
            "error_count": 2,
            "errors": ["错误1", "错误2"],
        }

    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = ttk.Label(
            self.root, text="MiniCRM 业务对话框演示", font=("", 16, "bold")
        )
        title_label.pack(pady=20)

        # 说明
        info_label = ttk.Label(
            self.root, text="点击下面的按钮来演示不同的业务对话框功能", font=("", 10)
        )
        info_label.pack(pady=10)

        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)

        # 设置对话框按钮
        settings_button = ttk.Button(
            button_frame,
            text="系统设置对话框",
            command=self.show_settings_dialog,
            width=20,
        )
        settings_button.pack(pady=5)

        # 导出对话框按钮
        export_button = ttk.Button(
            button_frame,
            text="数据导出对话框",
            command=self.show_export_dialog,
            width=20,
        )
        export_button.pack(pady=5)

        # 导入对话框按钮
        import_button = ttk.Button(
            button_frame,
            text="数据导入对话框",
            command=self.show_import_dialog,
            width=20,
        )
        import_button.pack(pady=5)

        # 退出按钮
        exit_button = ttk.Button(
            button_frame, text="退出", command=self.root.quit, width=20
        )
        exit_button.pack(pady=20)

    def show_settings_dialog(self):
        """显示设置对话框"""
        try:
            result, data = show_settings_dialog(
                parent=self.root, settings_service=self.settings_service
            )

            if result == "ok":
                print("设置对话框：用户点击了确定")
                print(f"设置数据：{data}")
            else:
                print("设置对话框：用户取消了操作")

        except Exception as e:
            print(f"设置对话框错误：{e}")

    def show_export_dialog(self):
        """显示导出对话框"""
        try:
            result, data = show_export_dialog(
                parent=self.root, import_export_service=self.import_export_service
            )

            if result == "ok":
                print("导出对话框：导出成功")
                print(f"导出信息：{data}")
            else:
                print("导出对话框：用户取消了操作")

        except Exception as e:
            print(f"导出对话框错误：{e}")

    def show_import_dialog(self):
        """显示导入对话框"""
        try:
            result, data = show_import_dialog(
                parent=self.root, import_export_service=self.import_export_service
            )

            if result == "ok":
                print("导入对话框：导入成功")
                print(f"导入配置：{data}")
            else:
                print("导入对话框：用户取消了操作")

        except Exception as e:
            print(f"导入对话框错误：{e}")

    def run(self):
        """运行演示"""
        print("业务对话框演示启动")
        print("=" * 50)
        print("功能说明：")
        print("1. 系统设置对话框 - 管理系统配置")
        print("2. 数据导出对话框 - 导出业务数据")
        print("3. 数据导入对话框 - 导入业务数据")
        print("=" * 50)

        self.root.mainloop()


def main():
    """主函数"""
    demo = BusinessDialogsDemo()
    demo.run()


if __name__ == "__main__":
    main()
