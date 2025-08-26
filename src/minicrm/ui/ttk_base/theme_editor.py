"""TTK主题编辑器

提供可视化的主题编辑和预览功能,包括:
- 主题颜色编辑
- 字体配置编辑
- 间距设置调整
- 实时预览功能
- 主题导入导出
- 主题分享功能

设计目标:
1. 提供直观的主题编辑界面
2. 支持实时预览主题效果
3. 简化主题创建和自定义过程
4. 支持主题的导入导出和分享

作者: MiniCRM开发团队
"""

import logging
import tkinter as tk
from tkinter import colorchooser, filedialog, font, messagebox, ttk
from typing import Any, Callable, Dict, Optional

from .base_dialog import BaseDialog
from .theme_manager import TTKThemeManager


class ColorPickerFrame(ttk.Frame):
    """颜色选择器框架"""

    def __init__(
        self,
        parent,
        label_text: str,
        initial_color: str = "#FFFFFF",
        on_color_change: Optional[Callable[[str], None]] = None,
    ):
        """初始化颜色选择器

        Args:
            parent: 父容器
            label_text: 标签文本
            initial_color: 初始颜色
            on_color_change: 颜色变化回调函数
        """
        super().__init__(parent)

        self.current_color = initial_color
        self.on_color_change = on_color_change

        self._setup_ui(label_text)

    def _setup_ui(self, label_text: str) -> None:
        """设置UI"""
        # 标签
        self.label = ttk.Label(self, text=label_text, width=15)
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        # 颜色显示按钮
        self.color_button = tk.Button(
            self,
            width=3,
            height=1,
            bg=self.current_color,
            command=self._choose_color,
            relief=tk.RAISED,
            bd=2,
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 5))

        # 颜色值标签
        self.color_label = ttk.Label(self, text=self.current_color, width=10)
        self.color_label.pack(side=tk.LEFT)

    def _choose_color(self) -> None:
        """选择颜色"""
        color = colorchooser.askcolor(
            color=self.current_color, title=f"选择{self.label.cget('text')}颜色"
        )

        if color[1]:  # 用户选择了颜色
            self.set_color(color[1])

    def set_color(self, color: str) -> None:
        """设置颜色

        Args:
            color: 颜色值
        """
        self.current_color = color
        self.color_button.configure(bg=color)
        self.color_label.configure(text=color)

        if self.on_color_change:
            self.on_color_change(color)

    def get_color(self) -> str:
        """获取当前颜色

        Returns:
            当前颜色值
        """
        return self.current_color


class FontConfigFrame(ttk.Frame):
    """字体配置框架"""

    def __init__(
        self,
        parent,
        label_text: str,
        initial_config: Dict[str, Any],
        on_font_change: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """初始化字体配置框架

        Args:
            parent: 父容器
            label_text: 标签文本
            initial_config: 初始字体配置
            on_font_change: 字体变化回调函数
        """
        super().__init__(parent)

        self.font_config = initial_config.copy()
        self.on_font_change = on_font_change

        self._setup_ui(label_text)

    def _setup_ui(self, label_text: str) -> None:
        """设置UI"""
        # 标签
        ttk.Label(self, text=label_text, width=15).grid(
            row=0, column=0, sticky="w", padx=(0, 5)
        )

        # 字体族
        ttk.Label(self, text="字体:").grid(row=0, column=1, sticky="w", padx=(0, 2))
        self.family_var = tk.StringVar(
            value=self.font_config.get("family", "Microsoft YaHei UI")
        )
        family_combo = ttk.Combobox(
            self,
            textvariable=self.family_var,
            values=list(font.families()),
            width=15,
            state="readonly",
        )
        family_combo.grid(row=0, column=2, padx=(0, 5))
        family_combo.bind("<<ComboboxSelected>>", self._on_font_change)

        # 字体大小
        ttk.Label(self, text="大小:").grid(row=0, column=3, sticky="w", padx=(0, 2))
        self.size_var = tk.StringVar(value=str(self.font_config.get("size", 9)))
        size_spin = ttk.Spinbox(
            self,
            from_=8,
            to=72,
            textvariable=self.size_var,
            width=5,
            command=self._on_font_change,
        )
        size_spin.grid(row=0, column=4, padx=(0, 5))
        size_spin.bind("<KeyRelease>", self._on_font_change)

        # 字体粗细
        ttk.Label(self, text="粗细:").grid(row=0, column=5, sticky="w", padx=(0, 2))
        self.weight_var = tk.StringVar(value=self.font_config.get("weight", "normal"))
        weight_combo = ttk.Combobox(
            self,
            textvariable=self.weight_var,
            values=["normal", "bold"],
            width=8,
            state="readonly",
        )
        weight_combo.grid(row=0, column=6)
        weight_combo.bind("<<ComboboxSelected>>", self._on_font_change)

    def _on_font_change(self, event=None) -> None:
        """字体变化处理"""
        try:
            self.font_config = {
                "family": self.family_var.get(),
                "size": int(self.size_var.get()),
                "weight": self.weight_var.get(),
                "slant": self.font_config.get("slant", "roman"),
            }

            if self.on_font_change:
                self.on_font_change(self.font_config)

        except ValueError:
            pass  # 忽略无效的数字输入

    def get_font_config(self) -> Dict[str, Any]:
        """获取字体配置

        Returns:
            字体配置字典
        """
        return self.font_config.copy()

    def set_font_config(self, config: Dict[str, Any]) -> None:
        """设置字体配置

        Args:
            config: 字体配置
        """
        self.font_config = config.copy()
        self.family_var.set(config.get("family", "Microsoft YaHei UI"))
        self.size_var.set(str(config.get("size", 9)))
        self.weight_var.set(config.get("weight", "normal"))


class ThemePreviewFrame(ttk.Frame):
    """主题预览框架"""

    def __init__(self, parent):
        """初始化主题预览框架

        Args:
            parent: 父容器
        """
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """设置预览UI"""
        # 预览标题
        title_label = ttk.Label(
            self, text="主题预览", font=("Microsoft YaHei UI", 12, "bold")
        )
        title_label.pack(pady=(0, 10))

        # 创建预览组件容器
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 按钮预览
        button_frame = ttk.Frame(preview_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Label(button_frame, text="按钮:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="普通按钮").pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="禁用按钮", state="disabled").pack(
            side=tk.LEFT, padx=2
        )

        # 输入框预览
        entry_frame = ttk.Frame(preview_frame)
        entry_frame.pack(fill=tk.X, pady=5)

        ttk.Label(entry_frame, text="输入框:").pack(side=tk.LEFT, padx=(0, 5))
        entry = ttk.Entry(entry_frame, width=20)
        entry.pack(side=tk.LEFT, padx=2)
        entry.insert(0, "示例文本")

        # 下拉框预览
        combo_frame = ttk.Frame(preview_frame)
        combo_frame.pack(fill=tk.X, pady=5)

        ttk.Label(combo_frame, text="下拉框:").pack(side=tk.LEFT, padx=(0, 5))
        combo = ttk.Combobox(
            combo_frame, values=["选项1", "选项2", "选项3"], width=17, state="readonly"
        )
        combo.pack(side=tk.LEFT, padx=2)
        combo.set("选项1")

        # 复选框预览
        check_frame = ttk.Frame(preview_frame)
        check_frame.pack(fill=tk.X, pady=5)

        ttk.Label(check_frame, text="复选框:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(check_frame, text="选项A").pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(check_frame, text="选项B").pack(side=tk.LEFT, padx=2)

        # 单选框预览
        radio_frame = ttk.Frame(preview_frame)
        radio_frame.pack(fill=tk.X, pady=5)

        ttk.Label(radio_frame, text="单选框:").pack(side=tk.LEFT, padx=(0, 5))
        radio_var = tk.StringVar(value="选项1")
        ttk.Radiobutton(
            radio_frame, text="选项1", variable=radio_var, value="选项1"
        ).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(
            radio_frame, text="选项2", variable=radio_var, value="选项2"
        ).pack(side=tk.LEFT, padx=2)

        # 进度条预览
        progress_frame = ttk.Frame(preview_frame)
        progress_frame.pack(fill=tk.X, pady=5)

        ttk.Label(progress_frame, text="进度条:").pack(side=tk.LEFT, padx=(0, 5))
        progress = ttk.Progressbar(progress_frame, length=200, mode="determinate")
        progress.pack(side=tk.LEFT, padx=2)
        progress["value"] = 60

        # 表格预览
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Label(tree_frame, text="表格:").pack(anchor="w")

        # 创建表格
        columns = ("列1", "列2", "列3")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=4)

        # 配置列
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        # 添加示例数据
        for i in range(3):
            tree.insert(
                "", "end", values=(f"数据{i + 1}A", f"数据{i + 1}B", f"数据{i + 1}C")
            )

        tree.pack(fill=tk.BOTH, expand=True)


class ThemeEditorTTK(BaseDialog):
    """TTK主题编辑器对话框

    提供可视化的主题编辑功能,包括颜色、字体、间距的调整,
    以及实时预览和主题导入导出功能.
    """

    def __init__(self, parent, theme_manager: Optional[TTKThemeManager] = None):
        """初始化主题编辑器

        Args:
            parent: 父窗口
            theme_manager: 主题管理器实例
        """
        self.theme_manager = theme_manager or TTKThemeManager()
        self.logger = logging.getLogger(__name__)

        # 当前编辑的主题配置
        self.current_theme_config: Dict[str, Any] = {}
        self.current_theme_id = "custom"

        # 颜色选择器字典
        self.color_pickers: Dict[str, ColorPickerFrame] = {}

        # 字体配置器字典
        self.font_configs: Dict[str, FontConfigFrame] = {}

        super().__init__(parent, title="主题编辑器", size=(900, 700), resizable=True)

    def _setup_ui(self) -> None:
        """设置UI"""
        # 创建主容器
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建左右分割的界面
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧编辑面板
        edit_frame = ttk.Frame(paned_window)
        paned_window.add(edit_frame, weight=2)

        # 右侧预览面板
        preview_frame = ttk.Frame(paned_window)
        paned_window.add(preview_frame, weight=1)

        # 设置编辑面板
        self._setup_edit_panel(edit_frame)

        # 设置预览面板
        self._setup_preview_panel(preview_frame)

        # 加载默认主题配置
        self._load_theme_config("default")

    def _setup_edit_panel(self, parent: ttk.Frame) -> None:
        """设置编辑面板

        Args:
            parent: 父容器
        """
        # 主题选择区域
        theme_frame = ttk.LabelFrame(parent, text="主题选择", padding=10)
        theme_frame.pack(fill=tk.X, pady=(0, 10))

        # 基础主题选择
        base_frame = ttk.Frame(theme_frame)
        base_frame.pack(fill=tk.X, pady=5)

        ttk.Label(base_frame, text="基础主题:").pack(side=tk.LEFT, padx=(0, 5))
        self.base_theme_var = tk.StringVar(value="default")
        base_combo = ttk.Combobox(
            base_frame,
            textvariable=self.base_theme_var,
            values=list(self.theme_manager.get_available_themes().keys()),
            state="readonly",
            width=20,
        )
        base_combo.pack(side=tk.LEFT, padx=(0, 10))
        base_combo.bind("<<ComboboxSelected>>", self._on_base_theme_change)

        # 主题名称
        name_frame = ttk.Frame(theme_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="主题名称:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_name_var = tk.StringVar(value="自定义主题")
        ttk.Entry(name_frame, textvariable=self.theme_name_var, width=25).pack(
            side=tk.LEFT
        )

        # 创建滚动区域
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 颜色配置区域
        self._setup_color_config(scrollable_frame)

        # 字体配置区域
        self._setup_font_config(scrollable_frame)

        # 间距配置区域
        self._setup_spacing_config(scrollable_frame)

    def _setup_color_config(self, parent: ttk.Frame) -> None:
        """设置颜色配置区域

        Args:
            parent: 父容器
        """
        color_frame = ttk.LabelFrame(parent, text="颜色配置", padding=10)
        color_frame.pack(fill=tk.X, pady=(0, 10))

        # 主要颜色
        primary_frame = ttk.LabelFrame(color_frame, text="主要颜色", padding=5)
        primary_frame.pack(fill=tk.X, pady=(0, 5))

        primary_colors = [
            ("primary", "主色调"),
            ("secondary", "次要色"),
            ("success", "成功色"),
            ("warning", "警告色"),
            ("danger", "危险色"),
            ("info", "信息色"),
        ]

        for color_key, color_name in primary_colors:
            picker = ColorPickerFrame(
                primary_frame,
                color_name,
                "#007BFF",
                lambda color, key=color_key: self._on_color_change(key, color),
            )
            picker.pack(fill=tk.X, pady=2)
            self.color_pickers[color_key] = picker

        # 背景颜色
        bg_frame = ttk.LabelFrame(color_frame, text="背景颜色", padding=5)
        bg_frame.pack(fill=tk.X, pady=(0, 5))

        bg_colors = [
            ("bg_primary", "主背景"),
            ("bg_secondary", "次背景"),
            ("bg_tertiary", "第三背景"),
        ]

        for color_key, color_name in bg_colors:
            picker = ColorPickerFrame(
                bg_frame,
                color_name,
                "#FFFFFF",
                lambda color, key=color_key: self._on_color_change(key, color),
            )
            picker.pack(fill=tk.X, pady=2)
            self.color_pickers[color_key] = picker

        # 文本颜色
        text_frame = ttk.LabelFrame(color_frame, text="文本颜色", padding=5)
        text_frame.pack(fill=tk.X, pady=(0, 5))

        text_colors = [
            ("text_primary", "主文本"),
            ("text_secondary", "次文本"),
            ("text_muted", "弱化文本"),
            ("text_white", "白色文本"),
        ]

        for color_key, color_name in text_colors:
            picker = ColorPickerFrame(
                text_frame,
                color_name,
                "#212529",
                lambda color, key=color_key: self._on_color_change(key, color),
            )
            picker.pack(fill=tk.X, pady=2)
            self.color_pickers[color_key] = picker

    def _setup_font_config(self, parent: ttk.Frame) -> None:
        """设置字体配置区域

        Args:
            parent: 父容器
        """
        font_frame = ttk.LabelFrame(parent, text="字体配置", padding=10)
        font_frame.pack(fill=tk.X, pady=(0, 10))

        font_types = [
            ("default", "默认字体"),
            ("heading", "标题字体"),
            ("small", "小字体"),
            ("large", "大字体"),
        ]

        for font_key, font_name in font_types:
            config_frame = FontConfigFrame(
                font_frame,
                font_name,
                {"family": "Microsoft YaHei UI", "size": 9, "weight": "normal"},
                lambda config, key=font_key: self._on_font_change(key, config),
            )
            config_frame.pack(fill=tk.X, pady=5)
            self.font_configs[font_key] = config_frame

    def _setup_spacing_config(self, parent: ttk.Frame) -> None:
        """设置间距配置区域

        Args:
            parent: 父容器
        """
        spacing_frame = ttk.LabelFrame(parent, text="间距配置", padding=10)
        spacing_frame.pack(fill=tk.X, pady=(0, 10))

        # 内边距配置
        padding_frame = ttk.LabelFrame(spacing_frame, text="内边距", padding=5)
        padding_frame.pack(fill=tk.X, pady=(0, 5))

        self.spacing_vars = {}

        padding_items = [
            ("padding_small", "小内边距"),
            ("padding_medium", "中内边距"),
            ("padding_large", "大内边距"),
        ]

        for spacing_key, spacing_name in padding_items:
            item_frame = ttk.Frame(padding_frame)
            item_frame.pack(fill=tk.X, pady=2)

            ttk.Label(item_frame, text=f"{spacing_name}:", width=15).pack(
                side=tk.LEFT, padx=(0, 5)
            )

            var = tk.StringVar(value="5")
            spinbox = ttk.Spinbox(
                item_frame,
                from_=0,
                to=50,
                textvariable=var,
                width=10,
                command=lambda: self._on_spacing_change(),
            )
            spinbox.pack(side=tk.LEFT)
            spinbox.bind("<KeyRelease>", lambda e: self._on_spacing_change())

            self.spacing_vars[spacing_key] = var

    def _setup_preview_panel(self, parent: ttk.Frame) -> None:
        """设置预览面板

        Args:
            parent: 父容器
        """
        # 预览标题
        title_label = ttk.Label(
            parent, text="实时预览", font=("Microsoft YaHei UI", 12, "bold")
        )
        title_label.pack(pady=(10, 5))

        # 预览组件
        self.preview_frame = ThemePreviewFrame(parent)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _setup_buttons(self) -> None:
        """设置按钮"""
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 左侧按钮
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        ttk.Button(left_buttons, text="导入主题", command=self._import_theme).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(left_buttons, text="导出主题", command=self._export_theme).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(left_buttons, text="重置", command=self._reset_theme).pack(
            side=tk.LEFT
        )

        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        ttk.Button(right_buttons, text="应用", command=self._apply_theme).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(right_buttons, text="保存", command=self._save_theme).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(right_buttons, text="取消", command=self.destroy).pack(side=tk.LEFT)

    def _on_base_theme_change(self, event=None) -> None:
        """基础主题变化处理"""
        base_theme = self.base_theme_var.get()
        self._load_theme_config(base_theme)

    def _on_color_change(self, color_key: str, color_value: str) -> None:
        """颜色变化处理

        Args:
            color_key: 颜色键
            color_value: 颜色值
        """
        if "colors" not in self.current_theme_config:
            self.current_theme_config["colors"] = {}

        self.current_theme_config["colors"][color_key] = color_value
        self._apply_preview()

    def _on_font_change(self, font_key: str, font_config: Dict[str, Any]) -> None:
        """字体变化处理

        Args:
            font_key: 字体键
            font_config: 字体配置
        """
        if "fonts" not in self.current_theme_config:
            self.current_theme_config["fonts"] = {}

        self.current_theme_config["fonts"][font_key] = font_config
        self._apply_preview()

    def _on_spacing_change(self) -> None:
        """间距变化处理"""
        if "spacing" not in self.current_theme_config:
            self.current_theme_config["spacing"] = {}

        for key, var in self.spacing_vars.items():
            try:
                value = int(var.get())
                self.current_theme_config["spacing"][key] = value
            except ValueError:
                pass

        self._apply_preview()

    def _load_theme_config(self, theme_id: str) -> None:
        """加载主题配置

        Args:
            theme_id: 主题ID
        """
        try:
            self.current_theme_config = self.theme_manager.get_theme_config(theme_id)
            self.current_theme_id = theme_id

            # 更新颜色选择器
            colors = self.current_theme_config.get("colors", {})
            for color_key, picker in self.color_pickers.items():
                color_value = colors.get(color_key, "#FFFFFF")
                picker.set_color(color_value)

            # 更新字体配置器
            fonts = self.current_theme_config.get("fonts", {})
            for font_key, config_frame in self.font_configs.items():
                font_config = fonts.get(
                    font_key,
                    {"family": "Microsoft YaHei UI", "size": 9, "weight": "normal"},
                )
                config_frame.set_font_config(font_config)

            # 更新间距配置
            spacing = self.current_theme_config.get("spacing", {})
            for spacing_key, var in self.spacing_vars.items():
                value = spacing.get(spacing_key, 5)
                var.set(str(value))

            # 应用预览
            self._apply_preview()

            self.logger.info(f"加载主题配置: {theme_id}")

        except Exception as e:
            self.logger.error(f"加载主题配置失败: {e}")
            messagebox.showerror("错误", f"加载主题配置失败: {e}")

    def _apply_preview(self) -> None:
        """应用预览"""
        try:
            # 创建临时主题并应用
            temp_theme_id = "temp_preview"

            # 创建自定义主题
            success = self.theme_manager.create_custom_theme(
                temp_theme_id,
                "预览主题",
                colors=self.current_theme_config.get("colors", {}),
                fonts=self.current_theme_config.get("fonts", {}),
                spacing=self.current_theme_config.get("spacing", {}),
            )

            if success:
                # 应用到预览区域
                self.theme_manager.apply_theme_to_widget(
                    self.preview_frame, temp_theme_id
                )

        except Exception as e:
            self.logger.error(f"应用预览失败: {e}")

    def _import_theme(self) -> None:
        """导入主题"""
        try:
            file_path = filedialog.askopenfilename(
                title="导入主题文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            )

            if file_path:
                success = self.theme_manager.import_theme(file_path)
                if success:
                    messagebox.showinfo("成功", "主题导入成功!")
                    # 刷新基础主题列表
                    base_combo = self.base_theme_var
                    # 这里可以添加刷新逻辑
                else:
                    messagebox.showerror("错误", "主题导入失败!")

        except Exception as e:
            self.logger.error(f"导入主题失败: {e}")
            messagebox.showerror("错误", f"导入主题失败: {e}")

    def _export_theme(self) -> None:
        """导出主题"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="导出主题文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            )

            if file_path:
                # 保存当前配置到临时主题
                temp_theme_id = "temp_export"
                self.theme_manager.create_custom_theme(
                    temp_theme_id,
                    self.theme_name_var.get(),
                    colors=self.current_theme_config.get("colors", {}),
                    fonts=self.current_theme_config.get("fonts", {}),
                    spacing=self.current_theme_config.get("spacing", {}),
                )

                success = self.theme_manager.export_theme(temp_theme_id, file_path)
                if success:
                    messagebox.showinfo("成功", "主题导出成功!")
                else:
                    messagebox.showerror("错误", "主题导出失败!")

        except Exception as e:
            self.logger.error(f"导出主题失败: {e}")
            messagebox.showerror("错误", f"导出主题失败: {e}")

    def _reset_theme(self) -> None:
        """重置主题"""
        base_theme = self.base_theme_var.get()
        self._load_theme_config(base_theme)

    def _apply_theme(self) -> None:
        """应用主题"""
        try:
            theme_name = self.theme_name_var.get()
            if not theme_name:
                messagebox.showerror("错误", "请输入主题名称!")
                return

            # 创建自定义主题
            success = self.theme_manager.create_custom_theme(
                self.current_theme_id,
                theme_name,
                colors=self.current_theme_config.get("colors", {}),
                fonts=self.current_theme_config.get("fonts", {}),
                spacing=self.current_theme_config.get("spacing", {}),
            )

            if success:
                # 应用主题
                self.theme_manager.set_theme(self.current_theme_id)
                messagebox.showinfo("成功", "主题应用成功!")
            else:
                messagebox.showerror("错误", "主题应用失败!")

        except Exception as e:
            self.logger.error(f"应用主题失败: {e}")
            messagebox.showerror("错误", f"应用主题失败: {e}")

    def _save_theme(self) -> None:
        """保存主题"""
        try:
            theme_name = self.theme_name_var.get()
            if not theme_name:
                messagebox.showerror("错误", "请输入主题名称!")
                return

            # 创建自定义主题
            success = self.theme_manager.create_custom_theme(
                self.current_theme_id,
                theme_name,
                colors=self.current_theme_config.get("colors", {}),
                fonts=self.current_theme_config.get("fonts", {}),
                spacing=self.current_theme_config.get("spacing", {}),
            )

            if success:
                messagebox.showinfo("成功", "主题保存成功!")
                self.destroy()
            else:
                messagebox.showerror("错误", "主题保存失败!")

        except Exception as e:
            self.logger.error(f"保存主题失败: {e}")
            messagebox.showerror("错误", f"保存主题失败: {e}")


def show_theme_editor(
    parent=None, theme_manager: Optional[TTKThemeManager] = None
) -> None:
    """显示主题编辑器对话框

    Args:
        parent: 父窗口
        theme_manager: 主题管理器实例
    """
    editor = ThemeEditorTTK(parent, theme_manager)
    editor.show_modal()


if __name__ == "__main__":
    # 测试主题编辑器
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    show_theme_editor()
