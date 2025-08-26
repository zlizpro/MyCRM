"""TTK数据导入对话框

提供数据导入的向导式图形化界面,包括:
- 文件选择和预览
- 数据类型选择
- 字段映射配置
- 导入选项设置
- 导入进度显示

设计特点:
1. 向导式步骤界面
2. 智能字段映射建议
3. 数据预览和验证
4. 详细的导入进度和结果反馈

作者: MiniCRM开发团队
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path
import threading
import tkinter as tk
from tkinter import ttk
from typing import Any

from ...services.import_export_service import ImportExportService
from .base_dialog import BaseDialogTTK, DialogResult
from .file_dialog_ttk import open_file_dialog


class ImportDialogTTK(BaseDialogTTK):
    """TTK数据导入对话框类

    提供向导式数据导入界面,支持文件选择、字段映射、
    导入选项配置和进度显示.
    """

    def __init__(
        self,
        parent: tk.Widget | None = None,
        import_export_service: ImportExportService | None = None,
        **kwargs,
    ):
        """初始化导入对话框

        Args:
            parent: 父窗口
            import_export_service: 导入导出服务实例
            **kwargs: 其他参数
        """
        self.import_export_service = import_export_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # 向导步骤
        self.current_step = 0
        self.total_steps = 5
        self.step_names = ["文件选择", "数据类型", "字段映射", "导入选项", "执行导入"]

        # 导入配置
        self.import_config: dict[str, Any] = {
            "file_path": "",
            "data_type": "customers",
            "field_mapping": {},
            "options": {
                "skip_duplicates": True,
                "update_existing": False,
                "validate_data": True,
            },
        }

        # 文件数据
        self.file_data: list[dict[str, Any]] = []
        self.file_headers: list[str] = []

        # 数据类型定义
        self.data_types = {"customers": "客户数据", "suppliers": "供应商数据"}

        # 目标字段定义
        self.target_fields = {
            "customers": {
                "name": {"label": "客户名称", "required": True, "type": "string"},
                "phone": {"label": "联系电话", "required": True, "type": "string"},
                "email": {"label": "邮箱地址", "required": False, "type": "email"},
                "address": {"label": "地址", "required": False, "type": "string"},
                "customer_type": {
                    "label": "客户类型",
                    "required": False,
                    "type": "string",
                },
                "contact_person": {
                    "label": "联系人",
                    "required": False,
                    "type": "string",
                },
                "company": {"label": "公司名称", "required": False, "type": "string"},
            },
            "suppliers": {
                "name": {"label": "供应商名称", "required": True, "type": "string"},
                "contact_person": {
                    "label": "联系人",
                    "required": True,
                    "type": "string",
                },
                "phone": {"label": "联系电话", "required": True, "type": "string"},
                "email": {"label": "邮箱地址", "required": False, "type": "email"},
                "address": {"label": "地址", "required": False, "type": "string"},
                "supplier_type": {
                    "label": "供应商类型",
                    "required": False,
                    "type": "string",
                },
                "company": {"label": "公司名称", "required": False, "type": "string"},
            },
        }

        super().__init__(
            parent=parent,
            title="数据导入向导",
            size=(700, 600),
            min_size=(650, 550),
            **kwargs,
        )

    def _setup_content(self) -> None:
        """设置对话框内容"""
        if not self.import_export_service:
            self.show_error("导入导出服务不可用", "错误")
            self._on_cancel()
            return

        # 创建向导界面
        self._create_wizard_interface()

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        # 创建按钮框架
        button_frame = ttk.Frame(self.button_frame)
        button_frame.pack(fill=tk.X)

        # 左侧:步骤指示器
        self.step_label = ttk.Label(button_frame, text="")
        self.step_label.pack(side=tk.LEFT)

        # 右侧:导航按钮
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)

        self.cancel_button = ttk.Button(
            right_frame, text="取消", command=self._on_cancel
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.next_button = ttk.Button(
            right_frame, text="下一步", command=self._next_step, style="Accent.TButton"
        )
        self.next_button.pack(side=tk.RIGHT, padx=(5, 0))

        self.prev_button = ttk.Button(
            right_frame, text="上一步", command=self._prev_step
        )
        self.prev_button.pack(side=tk.RIGHT, padx=(5, 0))

        # 更新按钮状态
        self._update_buttons()

    def _create_wizard_interface(self) -> None:
        """创建向导界面"""
        # 创建步骤容器
        self.step_frames: list[ttk.Frame] = []

        for i in range(self.total_steps):
            frame = ttk.Frame(self.content_frame)
            self.step_frames.append(frame)

        # 创建各个步骤页面
        self._create_file_selection_step()
        self._create_data_type_step()
        self._create_field_mapping_step()
        self._create_options_step()
        self._create_import_step()

        # 显示第一步
        self._show_step(0)

    def _create_file_selection_step(self) -> None:
        """创建文件选择步骤"""
        frame = self.step_frames[0]

        # 标题
        title_label = ttk.Label(frame, text="选择要导入的文件", font=("", 12, "bold"))
        title_label.pack(pady=(10, 20))

        # 文件选择区域
        file_frame = ttk.LabelFrame(frame, text="文件选择", padding=20)
        file_frame.pack(fill=tk.X, padx=20, pady=10)

        # 文件路径
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(path_frame, text="文件路径:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(
            path_frame, textvariable=self.file_path_var, width=50
        )
        self.file_path_entry.pack(side=tk.LEFT, padx=(10, 5), fill=tk.X, expand=True)

        ttk.Button(path_frame, text="浏览", command=self._browse_file).pack(
            side=tk.LEFT
        )

        # 支持的格式说明
        info_label = ttk.Label(
            file_frame,
            text="支持的文件格式: Excel (.xlsx, .xls), CSV (.csv)",
            font=("", 9),
            foreground="gray",
        )
        info_label.pack(pady=(10, 0))

        # 文件预览区域
        preview_frame = ttk.LabelFrame(frame, text="文件预览", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建预览表格
        self.preview_tree = ttk.Treeview(preview_frame, height=8)
        preview_scrollbar_y = ttk.Scrollbar(
            preview_frame, orient="vertical", command=self.preview_tree.yview
        )
        preview_scrollbar_x = ttk.Scrollbar(
            preview_frame, orient="horizontal", command=self.preview_tree.xview
        )

        self.preview_tree.configure(
            yscrollcommand=preview_scrollbar_y.set,
            xscrollcommand=preview_scrollbar_x.set,
        )

        self.preview_tree.pack(side="left", fill="both", expand=True)
        preview_scrollbar_y.pack(side="right", fill="y")
        preview_scrollbar_x.pack(side="bottom", fill="x")

    def _create_data_type_step(self) -> None:
        """创建数据类型选择步骤"""
        frame = self.step_frames[1]

        # 标题
        title_label = ttk.Label(frame, text="选择数据类型", font=("", 12, "bold"))
        title_label.pack(pady=(10, 20))

        # 数据类型选择
        type_frame = ttk.LabelFrame(frame, text="数据类型", padding=20)
        type_frame.pack(fill=tk.X, padx=20, pady=10)

        self.data_type_var = tk.StringVar(value="customers")

        for key, label in self.data_types.items():
            ttk.Radiobutton(
                type_frame,
                text=label,
                variable=self.data_type_var,
                value=key,
                command=self._on_data_type_changed,
            ).pack(anchor=tk.W, pady=5)

        # 数据类型说明
        info_frame = ttk.LabelFrame(frame, text="字段要求", padding=20)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.type_info_text = tk.Text(
            info_frame, height=10, wrap=tk.WORD, state="disabled"
        )
        info_scrollbar = ttk.Scrollbar(
            info_frame, orient="vertical", command=self.type_info_text.yview
        )
        self.type_info_text.configure(yscrollcommand=info_scrollbar.set)

        self.type_info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # 更新数据类型信息
        self._update_data_type_info()

    def _create_field_mapping_step(self) -> None:
        """创建字段映射步骤"""
        frame = self.step_frames[2]

        # 标题
        title_label = ttk.Label(frame, text="配置字段映射", font=("", 12, "bold"))
        title_label.pack(pady=(10, 20))

        # 说明
        info_label = ttk.Label(
            frame, text="将文件中的列映射到系统字段(* 表示必填字段)", font=("", 9)
        )
        info_label.pack(pady=(0, 10))

        # 操作按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=20, pady=5)

        ttk.Button(button_frame, text="自动映射", command=self._auto_map_fields).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(
            button_frame, text="清除映射", command=self._clear_field_mapping
        ).pack(side=tk.LEFT)

        # 映射表格
        mapping_frame = ttk.Frame(frame)
        mapping_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建映射表格
        columns = ("target_field", "source_field", "required", "sample_data")
        self.mapping_tree = ttk.Treeview(
            mapping_frame, columns=columns, show="headings", height=12
        )

        # 设置列标题和宽度
        self.mapping_tree.heading("target_field", text="目标字段")
        self.mapping_tree.heading("source_field", text="源字段")
        self.mapping_tree.heading("required", text="必填")
        self.mapping_tree.heading("sample_data", text="示例数据")

        self.mapping_tree.column("target_field", width=150)
        self.mapping_tree.column("source_field", width=150)
        self.mapping_tree.column("required", width=60)
        self.mapping_tree.column("sample_data", width=200)

        # 滚动条
        mapping_scrollbar = ttk.Scrollbar(
            mapping_frame, orient="vertical", command=self.mapping_tree.yview
        )
        self.mapping_tree.configure(yscrollcommand=mapping_scrollbar.set)

        self.mapping_tree.pack(side="left", fill="both", expand=True)
        mapping_scrollbar.pack(side="right", fill="y")

        # 绑定双击事件
        self.mapping_tree.bind("<Double-1>", self._edit_field_mapping)

        # 字段映射变量
        self.field_mapping_vars: dict[str, tk.StringVar] = {}

    def _create_options_step(self) -> None:
        """创建导入选项步骤"""
        frame = self.step_frames[3]

        # 标题
        title_label = ttk.Label(frame, text="导入选项设置", font=("", 12, "bold"))
        title_label.pack(pady=(10, 20))

        # 数据处理选项
        data_frame = ttk.LabelFrame(frame, text="数据处理", padding=20)
        data_frame.pack(fill=tk.X, padx=20, pady=10)

        self.skip_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            data_frame, text="跳过重复数据", variable=self.skip_duplicates_var
        ).pack(anchor=tk.W, pady=2)

        self.update_existing_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            data_frame, text="更新现有记录", variable=self.update_existing_var
        ).pack(anchor=tk.W, pady=2)

        self.validate_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            data_frame, text="验证数据格式", variable=self.validate_data_var
        ).pack(anchor=tk.W, pady=2)

        # 错误处理选项
        error_frame = ttk.LabelFrame(frame, text="错误处理", padding=20)
        error_frame.pack(fill=tk.X, padx=20, pady=10)

        self.stop_on_error_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            error_frame, text="遇到错误时停止导入", variable=self.stop_on_error_var
        ).pack(anchor=tk.W, pady=2)

        self.create_error_log_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            error_frame, text="创建错误日志文件", variable=self.create_error_log_var
        ).pack(anchor=tk.W, pady=2)

        # 导入摘要
        summary_frame = ttk.LabelFrame(frame, text="导入摘要", padding=20)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.summary_text = tk.Text(
            summary_frame, height=8, wrap=tk.WORD, state="disabled"
        )
        summary_scrollbar = ttk.Scrollbar(
            summary_frame, orient="vertical", command=self.summary_text.yview
        )
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)

        self.summary_text.pack(side="left", fill="both", expand=True)
        summary_scrollbar.pack(side="right", fill="y")

    def _create_import_step(self) -> None:
        """创建导入执行步骤"""
        frame = self.step_frames[4]

        # 标题
        title_label = ttk.Label(frame, text="执行数据导入", font=("", 12, "bold"))
        title_label.pack(pady=(10, 20))

        # 进度显示
        progress_frame = ttk.LabelFrame(frame, text="导入进度", padding=20)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100, length=400
        )
        self.progress_bar.pack(pady=5)

        self.progress_label = ttk.Label(progress_frame, text="准备导入...")
        self.progress_label.pack(pady=5)

        # 结果显示
        result_frame = ttk.LabelFrame(frame, text="导入结果", padding=20)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.result_text = tk.Text(
            result_frame, height=12, wrap=tk.WORD, state="disabled"
        )
        result_scrollbar = ttk.Scrollbar(
            result_frame, orient="vertical", command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=result_scrollbar.set)

        self.result_text.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")

    def _show_step(self, step: int) -> None:
        """显示指定步骤"""
        # 隐藏所有步骤
        for frame in self.step_frames:
            frame.pack_forget()

        # 显示当前步骤
        if 0 <= step < len(self.step_frames):
            self.step_frames[step].pack(fill=tk.BOTH, expand=True)
            self.current_step = step

        # 更新按钮和标签
        self._update_buttons()
        self._update_step_label()

    def _update_buttons(self) -> None:
        """更新按钮状态"""
        # 上一步按钮
        self.prev_button.configure(
            state="normal" if self.current_step > 0 else "disabled"
        )

        # 下一步/完成按钮
        if self.current_step < self.total_steps - 1:
            self.next_button.configure(text="下一步")
            self.next_button.configure(
                state="normal" if self._can_proceed() else "disabled"
            )
        else:
            self.next_button.configure(text="开始导入")
            self.next_button.configure(
                state="normal" if self._can_proceed() else "disabled"
            )

    def _update_step_label(self) -> None:
        """更新步骤标签"""
        step_text = f"步骤 {self.current_step + 1}/{self.total_steps}: {self.step_names[self.current_step]}"
        self.step_label.configure(text=step_text)

    def _can_proceed(self) -> bool:
        """检查是否可以继续下一步"""
        if self.current_step == 0:
            # 文件选择步骤:需要选择文件并成功加载
            return bool(self.file_path_var.get() and self.file_data)
        if self.current_step == 1:
            # 数据类型步骤:需要选择数据类型
            return bool(self.data_type_var.get())
        if self.current_step == 2:
            # 字段映射步骤:需要映射必填字段
            return self._validate_field_mapping()
        if self.current_step == 3:
            # 导入选项步骤:总是可以继续
            return True
        if self.current_step == 4:
            # 导入执行步骤:总是可以继续
            return True

        return False

    def _next_step(self) -> None:
        """下一步"""
        if self.current_step < self.total_steps - 1:
            # 执行步骤切换前的处理
            if self.current_step == 2:
                # 字段映射步骤完成,更新导入摘要
                self._update_import_summary()

            self._show_step(self.current_step + 1)
        else:
            # 最后一步,开始导入
            self._start_import()

    def _prev_step(self) -> None:
        """上一步"""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _browse_file(self) -> None:
        """浏览文件"""
        file_path = open_file_dialog(
            parent=self,
            title="选择导入文件",
            filetypes=[
                ("Excel文件", "*.xlsx *.xls"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*"),
            ],
        )

        if file_path:
            self.file_path_var.set(file_path)
            self._load_file_preview()

    def _load_file_preview(self) -> None:
        """加载文件预览"""
        file_path = self.file_path_var.get()
        if not file_path:
            return

        try:
            # 清空预览
            self.preview_tree.delete(*self.preview_tree.get_children())

            # 根据文件类型加载数据
            if file_path.lower().endswith((".xlsx", ".xls")):
                self._load_excel_preview(file_path)
            elif file_path.lower().endswith(".csv"):
                self._load_csv_preview(file_path)
            else:
                self.show_error("不支持的文件格式")
                return

            # 更新按钮状态
            self._update_buttons()

        except Exception as e:
            self.logger.error("加载文件预览失败: %s", e)
            self.show_error(f"加载文件失败: {e}")

    def _load_excel_preview(self, file_path: str) -> None:
        """加载Excel文件预览"""
        try:
            import pandas as pd

            # 读取Excel文件
            df = pd.read_excel(file_path, nrows=10)  # 只读取前10行用于预览

            # 获取列名
            self.file_headers = list(df.columns)

            # 设置预览表格列
            self.preview_tree["columns"] = self.file_headers
            self.preview_tree["show"] = "headings"

            # 设置列标题
            for col in self.file_headers:
                self.preview_tree.heading(col, text=col)
                self.preview_tree.column(col, width=100)

            # 插入数据
            for _, row in df.iterrows():
                values = [
                    str(row[col]) if pd.notna(row[col]) else ""
                    for col in self.file_headers
                ]
                self.preview_tree.insert("", "end", values=values)

            # 保存完整数据(用于后续处理)
            full_df = pd.read_excel(file_path)
            self.file_data = full_df.to_dict("records")

        except ImportError:
            self.show_error("需要安装pandas库来处理Excel文件")
        except Exception as e:
            raise Exception(f"读取Excel文件失败: {e}")

    def _load_csv_preview(self, file_path: str) -> None:
        """加载CSV文件预览"""
        try:
            with open(file_path, encoding="utf-8-sig") as f:
                # 检测分隔符
                sample = f.read(1024)
                f.seek(0)

                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                # 读取CSV
                reader = csv.DictReader(f, delimiter=delimiter)
                self.file_headers = reader.fieldnames or []

                # 设置预览表格列
                self.preview_tree["columns"] = self.file_headers
                self.preview_tree["show"] = "headings"

                # 设置列标题
                for col in self.file_headers:
                    self.preview_tree.heading(col, text=col)
                    self.preview_tree.column(col, width=100)

                # 插入预览数据(前10行)
                self.file_data = []
                for i, row in enumerate(reader):
                    if i < 10:  # 预览前10行
                        values = [row.get(col, "") for col in self.file_headers]
                        self.preview_tree.insert("", "end", values=values)

                    # 保存所有数据
                    self.file_data.append(row)

        except Exception as e:
            raise Exception(f"读取CSV文件失败: {e}")

    def _on_data_type_changed(self) -> None:
        """数据类型变化处理"""
        self._update_data_type_info()
        self._update_field_mapping_display()

    def _update_data_type_info(self) -> None:
        """更新数据类型信息"""
        data_type = self.data_type_var.get()
        fields = self.target_fields.get(data_type, {})

        # 构建信息文本
        info_lines = [f"{self.data_types[data_type]} 字段要求:\n"]

        required_fields = []
        optional_fields = []

        for field_key, field_info in fields.items():
            field_line = f"• {field_info['label']} ({field_key}) - {field_info['type']}"
            if field_info["required"]:
                required_fields.append(field_line)
            else:
                optional_fields.append(field_line)

        if required_fields:
            info_lines.append("必填字段:")
            info_lines.extend(required_fields)
            info_lines.append("")

        if optional_fields:
            info_lines.append("可选字段:")
            info_lines.extend(optional_fields)

        # 更新文本
        self.type_info_text.configure(state="normal")
        self.type_info_text.delete("1.0", tk.END)
        self.type_info_text.insert("1.0", "\n".join(info_lines))
        self.type_info_text.configure(state="disabled")

    def _update_field_mapping_display(self) -> None:
        """更新字段映射显示"""
        # 清空映射表格
        self.mapping_tree.delete(*self.mapping_tree.get_children())

        data_type = self.data_type_var.get()
        fields = self.target_fields.get(data_type, {})

        # 添加目标字段
        for field_key, field_info in fields.items():
            required_text = "是" if field_info["required"] else "否"

            # 获取示例数据
            sample_data = self._get_sample_data_for_field(field_key)

            # 获取当前映射
            current_mapping = self.import_config["field_mapping"].get(field_key, "")

            self.mapping_tree.insert(
                "",
                "end",
                values=(
                    f"{field_info['label']} ({field_key})",
                    current_mapping,
                    required_text,
                    sample_data,
                ),
            )

    def _get_sample_data_for_field(self, field_key: str) -> str:
        """获取字段的示例数据"""
        if not self.file_data:
            return ""

        # 尝试从当前映射获取示例数据
        mapped_source = self.import_config["field_mapping"].get(field_key)
        if mapped_source and self.file_data:
            sample_values = []
            for i, row in enumerate(self.file_data[:3]):  # 取前3个示例
                value = row.get(mapped_source, "")
                if value:
                    sample_values.append(str(value))
            return ", ".join(sample_values) if sample_values else ""

        return ""

    def _edit_field_mapping(self, event) -> None:
        """编辑字段映射"""
        selection = self.mapping_tree.selection()
        if not selection:
            return

        item = selection[0]
        values = self.mapping_tree.item(item, "values")
        target_field_display = values[0]

        # 提取字段键
        field_key = target_field_display.split("(")[-1].rstrip(")")

        # 创建映射选择对话框
        self._show_field_mapping_dialog(field_key, item)

    def _show_field_mapping_dialog(self, field_key: str, tree_item) -> None:
        """显示字段映射选择对话框"""
        dialog = tk.Toplevel(self)
        dialog.title("选择源字段")
        dialog.geometry("300x400")
        dialog.transient(self)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"300x400+{x}+{y}")

        # 说明标签
        ttk.Label(dialog, text=f"为字段 '{field_key}' 选择源字段:").pack(pady=10)

        # 源字段列表
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        listbox = tk.Listbox(listbox_frame)
        scrollbar = ttk.Scrollbar(
            listbox_frame, orient="vertical", command=listbox.yview
        )
        listbox.configure(yscrollcommand=scrollbar.set)

        # 添加选项
        listbox.insert(0, "(不映射)")
        for header in self.file_headers:
            listbox.insert(tk.END, header)

        # 设置当前选择
        current_mapping = self.import_config["field_mapping"].get(field_key, "")
        if current_mapping in self.file_headers:
            index = self.file_headers.index(current_mapping) + 1
            listbox.selection_set(index)
        else:
            listbox.selection_set(0)

        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def on_ok():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                if index == 0:
                    # 不映射
                    self.import_config["field_mapping"].pop(field_key, None)
                    mapped_field = ""
                else:
                    # 映射到选择的字段
                    mapped_field = self.file_headers[index - 1]
                    self.import_config["field_mapping"][field_key] = mapped_field

                # 更新表格显示
                values = list(self.mapping_tree.item(tree_item, "values"))
                values[1] = mapped_field
                values[3] = self._get_sample_data_for_field(field_key)
                self.mapping_tree.item(tree_item, values=values)

                # 更新按钮状态
                self._update_buttons()

            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ttk.Button(button_frame, text="确定", command=on_ok).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

    def _auto_map_fields(self) -> None:
        """自动映射字段"""
        if not self.file_headers:
            self.show_warning("请先选择文件")
            return

        data_type = self.data_type_var.get()
        fields = self.target_fields.get(data_type, {})

        # 清除现有映射
        self.import_config["field_mapping"].clear()

        # 自动映射逻辑
        for field_key, field_info in fields.items():
            field_label = field_info["label"].lower()

            # 尝试精确匹配
            for header in self.file_headers:
                header_lower = header.lower()
                if (
                    field_key.lower() == header_lower
                    or field_label in header_lower
                    or header_lower in field_label
                ):
                    self.import_config["field_mapping"][field_key] = header
                    break

        # 更新显示
        self._update_field_mapping_display()
        self._update_buttons()

        self.show_info("自动映射完成")

    def _clear_field_mapping(self) -> None:
        """清除字段映射"""
        self.import_config["field_mapping"].clear()
        self._update_field_mapping_display()
        self._update_buttons()

    def _validate_field_mapping(self) -> bool:
        """验证字段映射"""
        data_type = self.data_type_var.get()
        fields = self.target_fields.get(data_type, {})

        # 检查必填字段是否都已映射
        for field_key, field_info in fields.items():
            if (
                field_info["required"]
                and field_key not in self.import_config["field_mapping"]
            ):
                return False

        return True

    def _update_import_summary(self) -> None:
        """更新导入摘要"""
        summary_lines = []

        # 文件信息
        file_path = self.file_path_var.get()
        summary_lines.append(f"文件: {Path(file_path).name}")
        summary_lines.append(f"数据类型: {self.data_types[self.data_type_var.get()]}")
        summary_lines.append(f"总记录数: {len(self.file_data)}")
        summary_lines.append("")

        # 字段映射
        summary_lines.append("字段映射:")
        for target_field, source_field in self.import_config["field_mapping"].items():
            summary_lines.append(f"  {target_field} ← {source_field}")
        summary_lines.append("")

        # 导入选项
        summary_lines.append("导入选项:")
        summary_lines.append(
            f"  跳过重复数据: {'是' if self.skip_duplicates_var.get() else '否'}"
        )
        summary_lines.append(
            f"  更新现有记录: {'是' if self.update_existing_var.get() else '否'}"
        )
        summary_lines.append(
            f"  验证数据格式: {'是' if self.validate_data_var.get() else '否'}"
        )

        # 更新摘要文本
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", "\n".join(summary_lines))
        self.summary_text.configure(state="disabled")

    def _start_import(self) -> None:
        """开始导入"""
        # 收集导入配置
        config = {
            "file_path": self.file_path_var.get(),
            "data_type": self.data_type_var.get(),
            "field_mapping": self.import_config["field_mapping"].copy(),
            "options": {
                "skip_duplicates": self.skip_duplicates_var.get(),
                "update_existing": self.update_existing_var.get(),
                "validate_data": self.validate_data_var.get(),
                "stop_on_error": self.stop_on_error_var.get(),
                "create_error_log": self.create_error_log_var.get(),
            },
        }

        # 确认导入
        if not self.confirm(f"确定要导入 {len(self.file_data)} 条记录吗?"):
            return

        # 执行导入
        self._execute_import(config)

    def _execute_import(self, config: dict[str, Any]) -> None:
        """执行导入"""
        # 更新UI状态
        self.next_button.configure(state="disabled")
        self.prev_button.configure(state="disabled")

        # 重置进度
        self.progress_var.set(0)
        self.progress_label.configure(text="开始导入...")

        # 清空结果
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.configure(state="disabled")

        def import_worker():
            try:
                # 执行导入
                result = self.import_export_service.import_data(
                    file_path=config["file_path"],
                    data_type=config["data_type"],
                    options=config["options"],
                )

                # 更新进度
                self.after(0, lambda: self.progress_var.set(100))
                self.after(0, lambda: self.progress_label.configure(text="导入完成"))

                # 显示结果
                self.after(0, lambda: self._show_import_result(result))

            except Exception as e:
                self.logger.error("导入失败: %s", e)
                self.after(0, lambda: self._show_import_error(str(e)))

        # 启动导入线程
        import_thread = threading.Thread(target=import_worker, daemon=True)
        import_thread.start()

    def _show_import_result(self, result: dict[str, Any]) -> None:
        """显示导入结果"""
        result_lines = []
        result_lines.append("导入完成!")
        result_lines.append("")
        result_lines.append(f"成功导入: {result.get('success_count', 0)} 条记录")
        result_lines.append(f"失败记录: {result.get('error_count', 0)} 条")
        result_lines.append("")

        # 显示错误信息
        errors = result.get("errors", [])
        if errors:
            result_lines.append("错误详情:")
            for error in errors[:10]:  # 只显示前10个错误
                result_lines.append(f"  • {error}")

            if len(errors) > 10:
                result_lines.append(f"  ... 还有 {len(errors) - 10} 个错误")

        # 更新结果文本
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(result_lines))
        self.result_text.configure(state="disabled")

        # 更新按钮
        self.next_button.configure(
            text="完成", state="normal", command=self._on_import_complete
        )

    def _show_import_error(self, error_message: str) -> None:
        """显示导入错误"""
        result_lines = [
            "导入失败!",
            "",
            f"错误信息: {error_message}",
            "",
            "请检查文件格式和字段映射,然后重试.",
        ]

        # 更新结果文本
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", "\n".join(result_lines))
        self.result_text.configure(state="disabled")

        # 更新按钮
        self.prev_button.configure(state="normal")
        self.next_button.configure(text="重试", state="normal")

    def _on_import_complete(self) -> None:
        """导入完成处理"""
        self.result = DialogResult.OK
        self.return_value = self.import_config.copy()
        self._close_dialog()

    def _validate_input(self) -> bool:
        """验证输入数据"""
        return self._can_proceed()

    def get_import_config(self) -> dict[str, Any]:
        """获取导入配置"""
        return self.import_config.copy()


# 便利函数
def show_import_dialog(
    parent: tk.Widget | None = None,
    import_export_service: ImportExportService | None = None,
) -> tuple[str, dict[str, Any] | None]:
    """显示导入对话框

    Args:
        parent: 父窗口
        import_export_service: 导入导出服务实例

    Returns:
        (结果, 导入配置) 元组
    """
    dialog = ImportDialogTTK(parent=parent, import_export_service=import_export_service)
    return dialog.show_dialog()
