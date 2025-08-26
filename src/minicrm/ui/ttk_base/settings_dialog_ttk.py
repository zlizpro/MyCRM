"""TTK系统设置对话框.

提供系统设置的图形化管理界面, 包括:
- 主题设置(颜色、字体、样式)
- 数据库设置(备份、性能)
- 系统设置(日志、监控)
- 界面设置(窗口、工具栏)

设计特点:
1. 分类标签页组织设置项
2. 根据设置类型提供合适的输入控件
3. 实时验证和错误提示
4. 支持设置的应用、重置、导入导出

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Union

from minicrm.core.exceptions import ValidationError

from .base_dialog import BaseDialogTTK, DialogResult
from .file_dialog_ttk import open_file_dialog, save_file_dialog


if TYPE_CHECKING:
    from minicrm.services.settings_service import SettingsService


if TYPE_CHECKING:
    from minicrm.services.settings_service import SettingsService


class SettingsDialogTTK(BaseDialogTTK):
    """TTK系统设置对话框类.

    提供系统设置的分类管理界面, 支持设置的查看、编辑、
    验证、保存、重置等功能.
    """

    def __init__(
        self,
        parent: tk.Widget | None = None,
        settings_service: SettingsService | None = None,
        **kwargs: Any,
    ):
        """初始化设置对话框.

        Args:
            parent: 父窗口
            settings_service: 设置服务实例
            **kwargs: 其他参数
        """
        self.settings_service = settings_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # 设置项控件存储
        self.setting_widgets: dict[str, dict[str, tk.Widget]] = {}
        self.setting_vars: dict[str, dict[str, tk.Variable]] = {}

        # 原始设置值(用于重置)
        self.original_settings: dict[str, Any] = {}

        # 当前设置值
        self.current_settings: dict[str, Any] = {}

        # 设置是否已修改
        self.settings_modified = False

        super().__init__(
            parent=parent,
            title="系统设置",
            size=(600, 500),
            min_size=(500, 400),
            **kwargs,
        )

    def _setup_content(self) -> None:
        """设置对话框内容."""
        if not self.settings_service:
            self.show_error("设置服务不可用", "错误")
            self._on_cancel()
            return

        # 加载当前设置
        self._load_current_settings()

        # 创建主要界面
        self._create_main_interface()

        # 加载设置到界面
        self._load_settings_to_ui()

    def _setup_buttons(self) -> None:
        """设置对话框按钮."""
        # 创建按钮框架
        button_frame = ttk.Frame(self.button_frame)
        button_frame.pack(fill=tk.X)

        # 左侧按钮(导入导出)
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)

        ttk.Button(left_frame, text="导入设置", command=self._import_settings).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(left_frame, text="导出设置", command=self._export_settings).pack(
            side=tk.LEFT
        )

        # 右侧按钮(操作按钮)
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)

        ttk.Button(right_frame, text="重置", command=self._reset_settings).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        ttk.Button(right_frame, text="应用", command=self._apply_settings).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        ttk.Button(right_frame, text="取消", command=self._on_cancel).pack(
            side=tk.RIGHT, padx=(5, 0)
        )

        ttk.Button(
            right_frame, text="确定", command=self._on_ok, style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=(5, 0))

    def _load_current_settings(self) -> None:
        """加载当前设置."""
        try:
            self.current_settings = self.settings_service.get_all_settings()
            self.original_settings = self.current_settings.copy()
            self.logger.debug("设置加载完成")
        except Exception as e:
            self.logger.exception("加载设置失败")
            self.show_error(f"加载设置失败: {e}")

    def _create_main_interface(self) -> None:
        """创建主要界面."""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建各个设置分类页面
        self._create_theme_page()
        self._create_database_page()
        self._create_system_page()
        self._create_ui_page()

    def _create_theme_page(self) -> None:
        """创建主题设置页面."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="主题设置")

        # 创建滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 主题设置项
        self._create_setting_group(
            scrollable_frame,
            "主题设置",
            "theme",
            [
                (
                    "theme_name",
                    "主题名称",
                    "combobox",
                    ["default", "dark", "light", "high_contrast"],
                ),
                ("primary_color", "主色调", "entry", None),
                ("secondary_color", "辅助色", "entry", None),
                ("accent_color", "强调色", "entry", None),
                (
                    "font_family",
                    "字体族",
                    "combobox",
                    ["Microsoft YaHei UI", "SimSun", "Arial"],
                ),
                ("font_size", "字体大小", "spinbox", {"from_": 8, "to": 16}),
                ("window_opacity", "窗口透明度", "scale", {"from_": 0.5, "to": 1.0}),
                ("enable_animations", "启用动画", "checkbutton", None),
            ],
        )

    def _create_database_page(self) -> None:
        """创建数据库设置页面."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="数据库设置")

        # 创建滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 数据库设置项
        self._create_setting_group(
            scrollable_frame,
            "备份设置",
            "database",
            [
                ("auto_backup", "自动备份", "checkbutton", None),
                (
                    "backup_interval",
                    "备份间隔",
                    "combobox",
                    ["daily", "weekly", "monthly"],
                ),
                ("max_backups", "最大备份数", "spinbox", {"from_": 1, "to": 100}),
                ("backup_location", "备份位置", "entry", None),
                ("compress_backups", "压缩备份", "checkbutton", None),
            ],
        )

    def _create_system_page(self) -> None:
        """创建系统设置页面."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="系统设置")

        # 创建滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 系统设置项
        self._create_setting_group(
            scrollable_frame,
            "日志和监控",
            "system",
            [
                (
                    "log_level",
                    "日志级别",
                    "combobox",
                    ["DEBUG", "INFO", "WARNING", "ERROR"],
                ),
                ("enable_performance_monitoring", "性能监控", "checkbutton", None),
                ("cache_size", "缓存大小(MB)", "spinbox", {"from_": 10, "to": 1000}),
                ("max_log_files", "最大日志文件数", "spinbox", {"from_": 1, "to": 20}),
                ("enable_crash_reporting", "崩溃报告", "checkbutton", None),
            ],
        )

    def _create_ui_page(self) -> None:
        """创建界面设置页面."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="界面设置")

        # 创建滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 界面设置项
        self._create_setting_group(
            scrollable_frame,
            "窗口和布局",
            "ui",
            [
                ("window_width", "窗口宽度", "spinbox", {"from_": 800, "to": 3840}),
                ("window_height", "窗口高度", "spinbox", {"from_": 600, "to": 2160}),
                ("window_maximized", "窗口最大化", "checkbutton", None),
                ("sidebar_width", "侧边栏宽度", "spinbox", {"from_": 150, "to": 400}),
                ("show_status_bar", "显示状态栏", "checkbutton", None),
                (
                    "toolbar_style",
                    "工具栏样式",
                    "combobox",
                    ["icons_only", "text_only", "icons_and_text"],
                ),
            ],
        )

    def _create_setting_group(
        self,
        parent: tk.Widget,
        group_title: str,
        category: str,
        settings: list[tuple[str, str, str, Any]],
    ) -> None:
        """创建设置组.

        Args:
            parent: 父容器
            group_title: 组标题
            category: 设置分类
            settings: 设置项列表 (key, label, widget_type, options)
        """
        # 创建组框架
        group_frame = ttk.LabelFrame(parent, text=group_title, padding=10)
        group_frame.pack(fill=tk.X, padx=10, pady=5)

        # 初始化分类存储
        if category not in self.setting_widgets:
            self.setting_widgets[category] = {}
            self.setting_vars[category] = {}

        # 创建设置项
        for setting_key, label, widget_type, options in settings:
            self._create_setting_item(
                group_frame, category, setting_key, label, widget_type, options
            )

    def _create_setting_item(
        self,
        parent: tk.Widget,
        category: str,
        key: str,
        label: str,
        widget_type: str,
        options: Union[list[str], dict[str, Any], None],
    ) -> None:
        """创建单个设置项.

        Args:
            parent: 父容器
            category: 设置分类
            key: 设置键
            label: 显示标签
            widget_type: 控件类型
            options: 控件选项
        """
        # 创建行框架
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=2)

        # 创建标签
        ttk.Label(row_frame, text=label, width=15).pack(side=tk.LEFT, padx=(0, 10))

        # 根据类型创建控件
        if widget_type == "entry":
            var = tk.StringVar()
            widget = ttk.Entry(row_frame, textvariable=var, width=30)

        elif widget_type == "checkbutton":
            var = tk.BooleanVar()
            widget = ttk.Checkbutton(row_frame, variable=var)

        elif widget_type == "combobox":
            var = tk.StringVar()
            widget = ttk.Combobox(
                row_frame, textvariable=var, values=options, state="readonly", width=27
            )

        elif widget_type == "spinbox":
            var = tk.IntVar()
            widget = ttk.Spinbox(row_frame, textvariable=var, width=30, **options)

        elif widget_type == "scale":
            var = tk.DoubleVar()
            widget = ttk.Scale(
                row_frame, variable=var, orient=tk.HORIZONTAL, length=200, **options
            )

        else:
            # 默认使用Entry
            var = tk.StringVar()
            widget = ttk.Entry(row_frame, textvariable=var, width=30)

        widget.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 存储控件和变量
        self.setting_widgets[category][key] = widget
        self.setting_vars[category][key] = var

        # 绑定变化事件
        var.trace_add(
            "write", lambda *_, c=category, k=key: self._on_setting_changed(c, k)
        )

    def _load_settings_to_ui(self) -> None:
        """加载设置到界面."""
        for category, settings in self.current_settings.items():
            if category in self.setting_vars:
                for key, value in settings.items():
                    if key in self.setting_vars[category]:
                        var = self.setting_vars[category][key]
                        try:
                            var.set(value)
                        except tk.TclError as e:
                            self.logger.warning(
                                "设置值加载失败 %s.%s: %s", category, key, e
                            )

    def _on_setting_changed(self, category: str, key: str) -> None:
        """设置项变化处理."""
        self.settings_modified = True

        # 实时验证
        try:
            var = self.setting_vars[category][key]
            value = var.get()

            # 更新当前设置
            if category not in self.current_settings:
                self.current_settings[category] = {}
            self.current_settings[category][key] = value

            # 验证设置值
            # 注意: 这里访问私有方法, 在实际实现中应该提供公共验证接口
            if hasattr(self.settings_service, "validate_setting_value"):
                self.settings_service.validate_setting_value(category, key, value)
            else:
                self.settings_service._validate_setting_value(category, key, value)

            # 移除错误样式
            widget = self.setting_widgets[category][key]
            if hasattr(widget, "configure"):
                widget.configure(style="")

        except ValidationError:
            # 添加错误样式
            widget = self.setting_widgets[category][key]
            if hasattr(widget, "configure"):
                widget.configure(style="Error.TEntry")
        except Exception as e:
            self.logger.warning("设置验证失败 %s.%s: %s", category, key, e)

    def _apply_settings(self) -> None:
        """应用设置."""
        try:
            # 验证所有设置
            for category, settings in self.current_settings.items():
                for key, value in settings.items():
                    # 注意: 这里访问私有方法, 在实际实现中应该提供公共验证接口
                    if hasattr(self.settings_service, "validate_setting_value"):
                        self.settings_service.validate_setting_value(
                            category, key, value
                        )
                    else:
                        self.settings_service._validate_setting_value(
                            category, key, value
                        )

            # 保存设置
            for category, settings in self.current_settings.items():
                self.settings_service.update_settings(category, settings)

            self.settings_modified = False
            self.show_info("设置已应用")

        except ValidationError as e:
            self.show_error(f"设置验证失败: {e}")
        except Exception as e:
            self.logger.exception("应用设置失败")
            self.show_error(f"应用设置失败: {e}")

    def _reset_settings(self) -> None:
        """重置设置."""
        if self.confirm("确定要重置所有设置到默认值吗?"):
            try:
                self.settings_service.reset_settings()
                self._load_current_settings()
                self._load_settings_to_ui()
                self.settings_modified = False
                self.show_info("设置已重置")
            except Exception as e:
                self.logger.exception("重置设置失败")
                self.show_error(f"重置设置失败: {e}")

    def _import_settings(self) -> None:
        """导入设置."""
        file_path = open_file_dialog(
            parent=self,
            title="导入设置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                self.settings_service.import_settings(file_path)
                self._load_current_settings()
                self._load_settings_to_ui()
                self.settings_modified = False
                self.show_info("设置导入成功")
            except Exception as e:
                self.logger.exception("导入设置失败")
                self.show_error(f"导入设置失败: {e}")

    def _export_settings(self) -> None:
        """导出设置."""
        file_path = save_file_dialog(
            parent=self,
            title="导出设置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )

        if file_path:
            try:
                self.settings_service.export_settings(file_path)
                self.show_info("设置导出成功")
            except Exception as e:
                self.logger.exception("导出设置失败")
                self.show_error(f"导出设置失败: {e}")

    def _validate_input(self) -> bool:
        """验证输入数据."""
        try:
            # 验证所有设置
            for category, settings in self.current_settings.items():
                for key, value in settings.items():
                    # 注意: 这里访问私有方法, 在实际实现中应该提供公共验证接口
                    if hasattr(self.settings_service, "validate_setting_value"):
                        self.settings_service.validate_setting_value(
                            category, key, value
                        )
                    else:
                        self.settings_service._validate_setting_value(
                            category, key, value
                        )
            return True
        except ValidationError as e:
            self.show_error(f"设置验证失败: {e}")
            return False
        except Exception as e:
            self.logger.exception("设置验证失败")
            self.show_error(f"设置验证失败: {e}")
            return False

    def _on_ok(self) -> None:
        """确定按钮处理."""
        if self._validate_input():
            # 应用设置
            self._apply_settings()
            if not self.settings_modified:
                self.result = DialogResult.OK
                self.return_value = self.current_settings
                self._close_dialog()

    def _on_cancel(self) -> None:
        """取消按钮处理."""
        if self.settings_modified:
            if self.confirm("设置已修改, 确定要放弃更改吗?"):
                super()._on_cancel()
        else:
            super()._on_cancel()

    def get_modified_settings(self) -> dict[str, Any]:
        """获取修改后的设置."""
        return self.current_settings.copy()

    def is_settings_modified(self) -> bool:
        """检查设置是否已修改."""
        return self.settings_modified


# 便利函数
def show_settings_dialog(
    parent: tk.Widget | None = None, settings_service: SettingsService | None = None
) -> tuple[str, dict[str, Any] | None]:
    """显示设置对话框.

    Args:
        parent: 父窗口
        settings_service: 设置服务实例

    Returns:
        (结果, 设置数据) 元组
    """
    dialog = SettingsDialogTTK(parent=parent, settings_service=settings_service)
    return dialog.show_dialog()
