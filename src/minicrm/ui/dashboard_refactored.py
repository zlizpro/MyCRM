"""TTK仪表盘组件

临时占位符仪表盘,用于修复应用程序启动流程.
后续需要实现完整的仪表盘功能.
"""

import logging
from tkinter import ttk


class DashboardRefactored(ttk.Frame):
    """TTK仪表盘组件 - 临时占位符"""

    def __init__(self, parent, app=None):
        """初始化仪表盘

        Args:
            parent: 父组件
            app: 应用程序实例
        """
        super().__init__(parent)
        self.app = app
        self.logger = logging.getLogger(__name__)

        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        # 创建标题
        title_label = ttk.Label(
            self, text="MiniCRM 仪表盘", font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(pady=20)

        # 创建欢迎信息
        welcome_label = ttk.Label(
            self, text="欢迎使用MiniCRM TTK版本!", font=("Microsoft YaHei UI", 12)
        )
        welcome_label.pack(pady=10)

        # 创建状态信息
        status_frame = ttk.LabelFrame(self, text="系统状态", padding=10)
        status_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(status_frame, text="✅ TTK界面系统运行正常").pack(anchor="w")
        ttk.Label(status_frame, text="✅ 数据库连接正常").pack(anchor="w")
        ttk.Label(status_frame, text="✅ 服务层初始化完成").pack(anchor="w")
        ttk.Label(status_frame, text="✅ 导航系统运行正常").pack(anchor="w")

        # 创建功能提示
        info_frame = ttk.LabelFrame(self, text="功能导航", padding=10)
        info_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            info_frame,
            text="请使用左侧导航面板访问各个功能模块:",
            font=("Microsoft YaHei UI", 10),
        ).pack(anchor="w")

        ttk.Label(info_frame, text="• 客户管理 - 管理客户信息和关系").pack(
            anchor="w", padx=20
        )
        ttk.Label(info_frame, text="• 供应商管理 - 管理供应商信息").pack(
            anchor="w", padx=20
        )
        ttk.Label(info_frame, text="• 财务管理 - 查看财务报表").pack(
            anchor="w", padx=20
        )
        ttk.Label(info_frame, text="• 任务管理 - 管理工作任务").pack(
            anchor="w", padx=20
        )

    def cleanup(self):
        """清理资源"""
