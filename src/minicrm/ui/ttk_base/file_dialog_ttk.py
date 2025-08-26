"""TTK文件对话框

提供文件选择、保存和目录选择功能,包括:
- 文件选择、保存、目录选择三种模式
- 文件类型筛选和扩展名过滤
- 路径导航和快捷路径
- 文件预览功能(可选)
- 多文件选择支持

设计目标:
1. 提供完整的文件操作界面
2. 支持多种文件选择模式
3. 提供用户友好的文件浏览体验
4. 确保跨平台兼容性

作者: MiniCRM开发团队
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, List, Optional, Tuple

from .base_dialog import BaseDialogTTK, DialogResult


class FileDialogMode:
    """文件对话框模式枚举"""

    OPEN_FILE = "open_file"
    SAVE_FILE = "save_file"
    OPEN_MULTIPLE = "open_multiple"
    SELECT_DIRECTORY = "select_directory"


class FileDialogTTK(BaseDialogTTK):
    """TTK文件对话框

    提供文件选择、保存和目录选择功能,
    支持文件类型筛选和路径导航.
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        title: str = "选择文件",
        mode: str = FileDialogMode.OPEN_FILE,
        initial_dir: Optional[str] = None,
        initial_file: Optional[str] = None,
        file_types: Optional[List[Tuple[str, str]]] = None,
        default_extension: Optional[str] = None,
        multiple_selection: bool = False,
        show_hidden: bool = False,
        **kwargs,
    ):
        """初始化文件对话框

        Args:
            parent: 父窗口
            title: 对话框标题
            mode: 对话框模式
            initial_dir: 初始目录
            initial_file: 初始文件名
            file_types: 文件类型列表 [("描述", "*.ext"), ...]
            default_extension: 默认扩展名
            multiple_selection: 是否支持多选
            show_hidden: 是否显示隐藏文件
            **kwargs: 其他参数
        """
        # 文件对话框特定属性
        self.mode = mode
        self.initial_dir = initial_dir or os.getcwd()
        self.initial_file = initial_file or ""
        self.file_types = file_types or [("所有文件", "*.*")]
        self.default_extension = default_extension
        self.multiple_selection = (
            multiple_selection and mode == FileDialogMode.OPEN_FILE
        )
        self.show_hidden = show_hidden

        # 当前状态
        self.current_dir = self.initial_dir
        self.selected_files: List[str] = []
        self.selected_file_type = 0

        # UI组件
        self.path_frame: Optional[ttk.Frame] = None
        self.path_var = tk.StringVar(value=self.current_dir)
        self.path_entry: Optional[ttk.Entry] = None
        self.up_button: Optional[ttk.Button] = None
        self.home_button: Optional[ttk.Button] = None

        self.file_frame: Optional[ttk.Frame] = None
        self.file_tree: Optional[ttk.Treeview] = None
        self.file_scrollbar: Optional[ttk.Scrollbar] = None

        self.filter_frame: Optional[ttk.Frame] = None
        self.filter_var = tk.StringVar()
        self.filter_combo: Optional[ttk.Combobox] = None

        self.name_frame: Optional[ttk.Frame] = None
        self.name_var = tk.StringVar(value=self.initial_file)
        self.name_entry: Optional[ttk.Entry] = None

        # 设置对话框大小
        kwargs.setdefault("size", (600, 450))
        kwargs.setdefault("min_size", (500, 400))

        # 根据模式设置标题
        if not title or title == "选择文件":
            title = self._get_default_title()

        super().__init__(parent, title, **kwargs)

        # 初始化文件列表
        self._refresh_file_list()

    def _get_default_title(self) -> str:
        """获取默认标题"""
        titles = {
            FileDialogMode.OPEN_FILE: "打开文件",
            FileDialogMode.SAVE_FILE: "保存文件",
            FileDialogMode.OPEN_MULTIPLE: "选择文件",
            FileDialogMode.SELECT_DIRECTORY: "选择文件夹",
        }
        return titles.get(self.mode, "选择文件")

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建路径导航区域
        self._create_path_navigation()

        # 创建文件列表区域
        self._create_file_list()

        # 创建文件类型筛选区域
        if self.mode != FileDialogMode.SELECT_DIRECTORY:
            self._create_file_filter()

        # 创建文件名输入区域
        if self.mode in [FileDialogMode.SAVE_FILE, FileDialogMode.OPEN_FILE]:
            self._create_file_name_input()

    def _create_path_navigation(self) -> None:
        """创建路径导航区域"""
        self.path_frame = ttk.Frame(self.content_frame)
        self.path_frame.pack(fill=tk.X, pady=(0, 5))

        # 上级目录按钮
        self.up_button = ttk.Button(
            self.path_frame, text="↑", width=3, command=self._go_up_directory
        )
        self.up_button.pack(side=tk.LEFT, padx=(0, 5))

        # 主目录按钮
        self.home_button = ttk.Button(
            self.path_frame, text="🏠", width=3, command=self._go_home_directory
        )
        self.home_button.pack(side=tk.LEFT, padx=(0, 5))

        # 路径输入框
        self.path_entry = ttk.Entry(self.path_frame, textvariable=self.path_var)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.path_entry.bind("<Return>", self._on_path_changed)

        # 刷新按钮
        refresh_button = ttk.Button(
            self.path_frame, text="🔄", width=3, command=self._refresh_file_list
        )
        refresh_button.pack(side=tk.LEFT)

    def _create_file_list(self) -> None:
        """创建文件列表区域"""
        self.file_frame = ttk.Frame(self.content_frame)
        self.file_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 创建文件树
        columns = ("name", "size", "modified")
        self.file_tree = ttk.Treeview(
            self.file_frame,
            columns=columns,
            show="tree headings",
            selectmode="extended" if self.multiple_selection else "browse",
        )

        # 配置列
        self.file_tree.heading("#0", text="名称", anchor=tk.W)
        self.file_tree.heading("name", text="", anchor=tk.W)  # 隐藏重复的名称列
        self.file_tree.heading("size", text="大小", anchor=tk.E)
        self.file_tree.heading("modified", text="修改时间", anchor=tk.W)

        self.file_tree.column("#0", width=300, minwidth=200)
        self.file_tree.column("name", width=0, minwidth=0, stretch=False)  # 隐藏
        self.file_tree.column("size", width=80, minwidth=60)
        self.file_tree.column("modified", width=150, minwidth=120)

        # 绑定事件
        self.file_tree.bind("<Double-Button-1>", self._on_file_double_click)
        self.file_tree.bind("<<TreeviewSelect>>", self._on_file_select)

        # 创建滚动条
        self.file_scrollbar = ttk.Scrollbar(
            self.file_frame, orient=tk.VERTICAL, command=self.file_tree.yview
        )
        self.file_tree.configure(yscrollcommand=self.file_scrollbar.set)

        # 布局
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_file_filter(self) -> None:
        """创建文件类型筛选区域"""
        self.filter_frame = ttk.Frame(self.content_frame)
        self.filter_frame.pack(fill=tk.X, pady=(0, 5))

        # 文件类型标签
        filter_label = ttk.Label(self.filter_frame, text="文件类型:")
        filter_label.pack(side=tk.LEFT, padx=(0, 5))

        # 文件类型下拉框
        filter_values = [f"{desc} ({pattern})" for desc, pattern in self.file_types]
        self.filter_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.filter_var,
            values=filter_values,
            state="readonly",
        )
        self.filter_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.filter_combo.current(0)
        self.filter_combo.bind("<<ComboboxSelected>>", self._on_filter_changed)

    def _create_file_name_input(self) -> None:
        """创建文件名输入区域"""
        self.name_frame = ttk.Frame(self.content_frame)
        self.name_frame.pack(fill=tk.X, pady=(5, 0))

        # 文件名标签
        name_label = ttk.Label(self.name_frame, text="文件名:")
        name_label.pack(side=tk.LEFT, padx=(0, 5))

        # 文件名输入框
        self.name_entry = ttk.Entry(self.name_frame, textvariable=self.name_var)
        self.name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name_entry.bind("<KeyRelease>", self._on_name_changed)

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        self.add_button("取消", self._on_cancel, DialogResult.CANCEL)

        # 根据模式设置确定按钮文本
        ok_text = {
            FileDialogMode.OPEN_FILE: "打开",
            FileDialogMode.SAVE_FILE: "保存",
            FileDialogMode.OPEN_MULTIPLE: "打开",
            FileDialogMode.SELECT_DIRECTORY: "选择",
        }.get(self.mode, "确定")

        self.add_button(ok_text, self._on_ok, DialogResult.OK, default=True)

    def _refresh_file_list(self) -> None:
        """刷新文件列表"""
        try:
            # 清空现有项目
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)

            # 检查目录是否存在
            if not os.path.exists(self.current_dir):
                self.current_dir = os.getcwd()
                self.path_var.set(self.current_dir)

            # 获取文件列表
            try:
                entries = os.listdir(self.current_dir)
            except PermissionError:
                messagebox.showerror("错误", "没有权限访问此目录", parent=self)
                return

            # 分离目录和文件
            directories = []
            files = []

            for entry in entries:
                full_path = os.path.join(self.current_dir, entry)

                # 跳过隐藏文件(如果设置不显示)
                if not self.show_hidden and entry.startswith("."):
                    continue

                if os.path.isdir(full_path):
                    directories.append(entry)
                else:
                    files.append(entry)

            # 排序
            directories.sort(key=str.lower)
            files.sort(key=str.lower)

            # 添加目录
            for directory in directories:
                full_path = os.path.join(self.current_dir, directory)
                try:
                    stat_info = os.stat(full_path)
                    modified_time = self._format_time(stat_info.st_mtime)

                    self.file_tree.insert(
                        "",
                        tk.END,
                        text=f"📁 {directory}",
                        values=("", "<DIR>", modified_time),
                        tags=("directory",),
                    )
                except (OSError, PermissionError):
                    # 无法获取信息的目录
                    self.file_tree.insert(
                        "",
                        tk.END,
                        text=f"📁 {directory}",
                        values=("", "<DIR>", ""),
                        tags=("directory",),
                    )

            # 添加文件(如果不是目录选择模式)
            if self.mode != FileDialogMode.SELECT_DIRECTORY:
                for file in files:
                    if self._should_show_file(file):
                        full_path = os.path.join(self.current_dir, file)
                        try:
                            stat_info = os.stat(full_path)
                            file_size = self._format_size(stat_info.st_size)
                            modified_time = self._format_time(stat_info.st_mtime)

                            self.file_tree.insert(
                                "",
                                tk.END,
                                text=f"📄 {file}",
                                values=("", file_size, modified_time),
                                tags=("file",),
                            )
                        except (OSError, PermissionError):
                            # 无法获取信息的文件
                            self.file_tree.insert(
                                "",
                                tk.END,
                                text=f"📄 {file}",
                                values=("", "", ""),
                                tags=("file",),
                            )

            # 更新路径显示
            self.path_var.set(self.current_dir)

        except Exception as e:
            self.logger.error(f"刷新文件列表失败: {e}")
            messagebox.showerror("错误", f"刷新文件列表失败: {e}", parent=self)

    def _should_show_file(self, filename: str) -> bool:
        """检查是否应该显示文件"""
        if self.mode == FileDialogMode.SELECT_DIRECTORY:
            return False

        # 获取当前选择的文件类型
        if self.filter_combo and self.file_types:
            current_index = self.filter_combo.current()
            if 0 <= current_index < len(self.file_types):
                _, pattern = self.file_types[current_index]

                # 处理通配符模式
                if pattern == "*.*" or pattern == "*":
                    return True

                # 处理具体扩展名
                if pattern.startswith("*."):
                    ext = pattern[2:]
                    return filename.lower().endswith(f".{ext.lower()}")

                # 处理多个扩展名(如 "*.jpg;*.png")
                if ";" in pattern:
                    patterns = pattern.split(";")
                    for p in patterns:
                        p = p.strip()
                        if p.startswith("*."):
                            ext = p[2:]
                            if filename.lower().endswith(f".{ext.lower()}"):
                                return True
                    return False

        return True

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def _format_time(self, timestamp: float) -> str:
        """格式化时间"""
        import datetime

        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")

    def _go_up_directory(self) -> None:
        """转到上级目录"""
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:  # 避免在根目录时的无限循环
            self.current_dir = parent_dir
            self._refresh_file_list()

    def _go_home_directory(self) -> None:
        """转到主目录"""
        self.current_dir = os.path.expanduser("~")
        self._refresh_file_list()

    def _on_path_changed(self, event=None) -> None:
        """路径改变处理"""
        new_path = self.path_var.get().strip()
        if os.path.isdir(new_path):
            self.current_dir = os.path.abspath(new_path)
            self._refresh_file_list()
        else:
            messagebox.showerror("错误", "指定的路径不存在或不是目录", parent=self)
            self.path_var.set(self.current_dir)

    def _on_filter_changed(self, event=None) -> None:
        """文件类型筛选改变处理"""
        self._refresh_file_list()

    def _on_name_changed(self, event=None) -> None:
        """文件名改变处理"""
        # 可以在这里添加实时验证逻辑

    def _on_file_select(self, event=None) -> None:
        """文件选择处理"""
        selection = self.file_tree.selection()
        if not selection:
            return

        # 获取选中的项目
        selected_items = []
        for item_id in selection:
            item = self.file_tree.item(item_id)
            text = item["text"]

            # 移除图标前缀
            if text.startswith("📁 "):
                name = text[2:]
                item_type = "directory"
            elif text.startswith("📄 "):
                name = text[2:]
                item_type = "file"
            else:
                name = text
                item_type = "unknown"

            selected_items.append((name, item_type))

        # 根据模式处理选择
        if self.mode == FileDialogMode.SELECT_DIRECTORY:
            # 目录选择模式:只选择目录
            directories = [
                name for name, item_type in selected_items if item_type == "directory"
            ]
            if directories:
                self.name_var.set(directories[0])
        else:
            # 文件选择模式:只选择文件
            files = [name for name, item_type in selected_items if item_type == "file"]
            if files:
                if self.multiple_selection:
                    # 多选模式:显示第一个文件名
                    self.name_var.set(files[0])
                else:
                    # 单选模式:显示选中的文件名
                    self.name_var.set(files[0])

    def _on_file_double_click(self, event=None) -> None:
        """文件双击处理"""
        selection = self.file_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item = self.file_tree.item(item_id)
        text = item["text"]

        # 获取文件/目录名
        if text.startswith("📁 "):
            name = text[2:]
            # 双击目录:进入目录
            new_path = os.path.join(self.current_dir, name)
            if os.path.isdir(new_path):
                self.current_dir = new_path
                self._refresh_file_list()
        elif text.startswith("📄 "):
            name = text[2:]
            # 双击文件:选择文件并确定
            if self.mode in [FileDialogMode.OPEN_FILE, FileDialogMode.OPEN_MULTIPLE]:
                self.name_var.set(name)
                self._on_ok()

    def _validate_input(self) -> bool:
        """验证输入"""
        if self.mode == FileDialogMode.SELECT_DIRECTORY:
            # 目录选择模式
            selected_dir = self.name_var.get().strip()
            if not selected_dir:
                messagebox.showerror("错误", "请选择一个目录", parent=self)
                return False

            full_path = os.path.join(self.current_dir, selected_dir)
            if not os.path.isdir(full_path):
                messagebox.showerror("错误", "选择的不是有效目录", parent=self)
                return False

        elif self.mode == FileDialogMode.SAVE_FILE:
            # 保存文件模式
            filename = self.name_var.get().strip()
            if not filename:
                messagebox.showerror("错误", "请输入文件名", parent=self)
                return False

            # 添加默认扩展名
            if self.default_extension and not os.path.splitext(filename)[1]:
                filename += self.default_extension
                self.name_var.set(filename)

            full_path = os.path.join(self.current_dir, filename)
            if os.path.exists(full_path):
                if not messagebox.askyesno(
                    "确认", f"文件 '{filename}' 已存在,是否覆盖?", parent=self
                ):
                    return False

        else:
            # 打开文件模式
            filename = self.name_var.get().strip()
            if not filename:
                messagebox.showerror("错误", "请选择一个文件", parent=self)
                return False

            full_path = os.path.join(self.current_dir, filename)
            if not os.path.isfile(full_path):
                messagebox.showerror("错误", "选择的文件不存在", parent=self)
                return False

        return True

    def _get_result_data(self) -> Any:
        """获取结果数据"""
        if self.mode == FileDialogMode.SELECT_DIRECTORY:
            # 返回选择的目录路径
            selected_dir = self.name_var.get().strip()
            return os.path.join(self.current_dir, selected_dir)

        if self.mode == FileDialogMode.OPEN_MULTIPLE:
            # 返回选择的多个文件路径
            selection = self.file_tree.selection()
            files = []
            for item_id in selection:
                item = self.file_tree.item(item_id)
                text = item["text"]
                if text.startswith("📄 "):
                    name = text[2:]
                    full_path = os.path.join(self.current_dir, name)
                    files.append(full_path)
            return (
                files
                if files
                else [os.path.join(self.current_dir, self.name_var.get().strip())]
            )

        # 返回选择的单个文件路径
        filename = self.name_var.get().strip()
        return os.path.join(self.current_dir, filename)


# 便利函数
def open_file_dialog(
    parent: Optional[tk.Widget] = None,
    title: str = "打开文件",
    initial_dir: Optional[str] = None,
    file_types: Optional[List[Tuple[str, str]]] = None,
) -> Optional[str]:
    """显示打开文件对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        initial_dir: 初始目录
        file_types: 文件类型列表

    Returns:
        选择的文件路径,取消则返回None
    """
    dialog = FileDialogTTK(
        parent=parent,
        title=title,
        mode=FileDialogMode.OPEN_FILE,
        initial_dir=initial_dir,
        file_types=file_types,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else None


def save_file_dialog(
    parent: Optional[tk.Widget] = None,
    title: str = "保存文件",
    initial_dir: Optional[str] = None,
    initial_file: Optional[str] = None,
    file_types: Optional[List[Tuple[str, str]]] = None,
    default_extension: Optional[str] = None,
) -> Optional[str]:
    """显示保存文件对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        initial_dir: 初始目录
        initial_file: 初始文件名
        file_types: 文件类型列表
        default_extension: 默认扩展名

    Returns:
        保存的文件路径,取消则返回None
    """
    dialog = FileDialogTTK(
        parent=parent,
        title=title,
        mode=FileDialogMode.SAVE_FILE,
        initial_dir=initial_dir,
        initial_file=initial_file,
        file_types=file_types,
        default_extension=default_extension,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else None


def select_directory_dialog(
    parent: Optional[tk.Widget] = None,
    title: str = "选择文件夹",
    initial_dir: Optional[str] = None,
) -> Optional[str]:
    """显示选择目录对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        initial_dir: 初始目录

    Returns:
        选择的目录路径,取消则返回None
    """
    dialog = FileDialogTTK(
        parent=parent,
        title=title,
        mode=FileDialogMode.SELECT_DIRECTORY,
        initial_dir=initial_dir,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else None


def open_multiple_files_dialog(
    parent: Optional[tk.Widget] = None,
    title: str = "选择文件",
    initial_dir: Optional[str] = None,
    file_types: Optional[List[Tuple[str, str]]] = None,
) -> List[str]:
    """显示多文件选择对话框

    Args:
        parent: 父窗口
        title: 对话框标题
        initial_dir: 初始目录
        file_types: 文件类型列表

    Returns:
        选择的文件路径列表,取消则返回空列表
    """
    dialog = FileDialogTTK(
        parent=parent,
        title=title,
        mode=FileDialogMode.OPEN_MULTIPLE,
        initial_dir=initial_dir,
        file_types=file_types,
        multiple_selection=True,
    )

    result, data = dialog.show_dialog()
    return data if result == DialogResult.OK else []
