"""TTK数据导入导出面板

提供统一的数据导入导出功能界面,包括:
- 数据导入功能(CSV、Excel)
- 数据导出功能(CSV、Excel、PDF)
- 文档生成功能(Word、PDF)
- 进度显示和错误处理

设计特点:
1. 标签页组织不同功能模块
2. 集成现有导入导出对话框功能
3. 支持多种数据格式和文件类型
4. 完整的进度跟踪和错误处理
5. 遵循MiniCRM TTK组件标准

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ...services.import_export_service import ImportExportService

from .base_widget import BaseWidget
from .progress_dialog_ttk import ProgressDialogTTK


class ImportExportPanelTTK(BaseWidget):
    """TTK数据导入导出面板类.

    提供统一的数据导入导出功能界面,支持多种数据格式,
    包含进度显示和错误处理功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        import_export_service: ImportExportService | None = None,
        **kwargs,
    ):
        """初始化导入导出面板.

        Args:
            parent: 父窗口
            import_export_service: 导入导出服务实例
            **kwargs: 其他参数
        """
        self.import_export_service = import_export_service
        self.logger = logging.getLogger(self.__class__.__name__)

        # 当前操作状态
        self.current_operation: str | None = None
        self.operation_thread: threading.Thread | None = None
        self.progress_dialog: ProgressDialogTTK | None = None

        # 统计信息
        self.statistics = {
            "customers": {"total": 0, "last_updated": ""},
            "suppliers": {"total": 0, "last_updated": ""},
            "contracts": {"total": 0, "last_updated": ""},
            "quotes": {"total": 0, "last_updated": ""},
        }

        super().__init__(parent, **kwargs)

        # 加载统计信息
        self._load_statistics()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主要容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题
        title_label = ttk.Label(
            main_frame, text="数据导入导出管理", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(pady=(0, 15))

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建各个标签页
        self._create_import_tab()
        self._create_export_tab()
        self._create_document_tab()
        self._create_statistics_tab()

    def _create_import_tab(self) -> None:
        """创建数据导入标签页."""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="数据导入")

        # 创建滚动框架
        canvas = tk.Canvas(import_frame)
        scrollbar = ttk.Scrollbar(import_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 导入说明
        info_frame = ttk.LabelFrame(scrollable_frame, text="导入说明", padding=15)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = (
            "数据导入功能支持以下格式:\n"
            "• CSV文件 (.csv) - 使用UTF-8编码\n"
            "• Excel文件 (.xlsx, .xls)\n"
            "• 支持的数据类型:客户数据、供应商数据、合同数据\n"
            "• 文件大小限制:50MB\n\n"
            "导入前请确保数据格式正确,包含必要的字段信息."
        )

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # 快速导入区域
        quick_import_frame = ttk.LabelFrame(
            scrollable_frame, text="快速导入", padding=15
        )
        quick_import_frame.pack(fill=tk.X, padx=10, pady=5)

        # 数据类型选择
        type_frame = ttk.Frame(quick_import_frame)
        type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(type_frame, text="数据类型:").pack(side=tk.LEFT)
        self.import_data_type_var = tk.StringVar(value="customers")

        data_types = [
            ("customers", "客户数据"),
            ("suppliers", "供应商数据"),
            ("contracts", "合同数据"),
        ]

        for value, text in data_types:
            ttk.Radiobutton(
                type_frame,
                text=text,
                variable=self.import_data_type_var,
                value=value,
            ).pack(side=tk.LEFT, padx=(10, 0))

        # 操作按钮
        button_frame = ttk.Frame(quick_import_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="选择文件导入",
            command=self._open_import_dialog,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="下载模板",
            command=self._download_template,
        ).pack(side=tk.LEFT)

        # 最近导入记录
        recent_frame = ttk.LabelFrame(scrollable_frame, text="最近导入记录", padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建记录表格
        columns = ("time", "type", "file", "status", "count")
        self.import_history_tree = ttk.Treeview(
            recent_frame, columns=columns, show="headings", height=6
        )

        # 设置列标题和宽度
        self.import_history_tree.heading("time", text="导入时间")
        self.import_history_tree.heading("type", text="数据类型")
        self.import_history_tree.heading("file", text="文件名")
        self.import_history_tree.heading("status", text="状态")
        self.import_history_tree.heading("count", text="记录数")

        self.import_history_tree.column("time", width=120)
        self.import_history_tree.column("type", width=80)
        self.import_history_tree.column("file", width=200)
        self.import_history_tree.column("status", width=80)
        self.import_history_tree.column("count", width=80)

        # 滚动条
        history_scrollbar = ttk.Scrollbar(
            recent_frame, orient="vertical", command=self.import_history_tree.yview
        )
        self.import_history_tree.configure(yscrollcommand=history_scrollbar.set)

        self.import_history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")

        # 加载导入历史
        self._load_import_history()

        # 布局滚动框架
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_export_tab(self) -> None:
        """创建数据导出标签页."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="数据导出")

        # 创建滚动框架
        canvas = tk.Canvas(export_frame)
        scrollbar = ttk.Scrollbar(export_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 导出说明
        info_frame = ttk.LabelFrame(scrollable_frame, text="导出说明", padding=15)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = (
            "数据导出功能支持以下格式:\n"
            "• CSV文件 (.csv) - 适合数据分析\n"
            "• Excel文件 (.xlsx) - 适合报表查看\n"
            "• PDF文件 (.pdf) - 适合打印和分享\n\n"
            "可以选择导出字段、设置筛选条件,支持大批量数据导出."
        )

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # 快速导出区域
        quick_export_frame = ttk.LabelFrame(
            scrollable_frame, text="快速导出", padding=15
        )
        quick_export_frame.pack(fill=tk.X, padx=10, pady=5)

        # 数据类型和格式选择
        selection_frame = ttk.Frame(quick_export_frame)
        selection_frame.pack(fill=tk.X, pady=5)

        # 数据类型
        type_label_frame = ttk.Frame(selection_frame)
        type_label_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(type_label_frame, text="数据类型:").pack(anchor=tk.W)
        self.export_data_type_var = tk.StringVar(value="customers")

        # 定义数据类型选项
        data_types = [
            ("customers", "客户数据"),
            ("suppliers", "供应商数据"),
            ("contracts", "合同数据"),
        ]

        for value, text in data_types:
            ttk.Radiobutton(
                type_label_frame,
                text=text,
                variable=self.export_data_type_var,
                value=value,
                command=self._update_export_statistics,
            ).pack(anchor=tk.W, pady=1)

        # 导出格式
        format_label_frame = ttk.Frame(selection_frame)
        format_label_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(30, 0))

        ttk.Label(format_label_frame, text="导出格式:").pack(anchor=tk.W)
        self.export_format_var = tk.StringVar(value="excel")

        export_formats = [
            ("excel", "Excel文件"),
            ("csv", "CSV文件"),
            ("pdf", "PDF文件"),
        ]

        for value, text in export_formats:
            ttk.Radiobutton(
                format_label_frame,
                text=text,
                variable=self.export_format_var,
                value=value,
            ).pack(anchor=tk.W, pady=1)

        # 数据统计显示
        stats_frame = ttk.Frame(quick_export_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(stats_frame, text="可导出数据:").pack(side=tk.LEFT)
        self.export_stats_label = ttk.Label(stats_frame, text="", foreground="blue")
        self.export_stats_label.pack(side=tk.LEFT, padx=(5, 0))

        # 更新统计信息
        self._update_export_statistics()

        # 操作按钮
        button_frame = ttk.Frame(quick_export_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            button_frame,
            text="开始导出",
            command=self._open_export_dialog,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="高级选项",
            command=self._open_advanced_export,
        ).pack(side=tk.LEFT)

        # 最近导出记录
        recent_frame = ttk.LabelFrame(scrollable_frame, text="最近导出记录", padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建记录表格
        export_columns = ("time", "type", "format", "file", "count")
        self.export_history_tree = ttk.Treeview(
            recent_frame, columns=export_columns, show="headings", height=6
        )

        # 设置列标题和宽度
        self.export_history_tree.heading("time", text="导出时间")
        self.export_history_tree.heading("type", text="数据类型")
        self.export_history_tree.heading("format", text="格式")
        self.export_history_tree.heading("file", text="文件路径")
        self.export_history_tree.heading("count", text="记录数")

        self.export_history_tree.column("time", width=120)
        self.export_history_tree.column("type", width=80)
        self.export_history_tree.column("format", width=60)
        self.export_history_tree.column("file", width=250)
        self.export_history_tree.column("count", width=80)

        # 滚动条
        export_history_scrollbar = ttk.Scrollbar(
            recent_frame, orient="vertical", command=self.export_history_tree.yview
        )
        self.export_history_tree.configure(yscrollcommand=export_history_scrollbar.set)

        self.export_history_tree.pack(side="left", fill="both", expand=True)
        export_history_scrollbar.pack(side="right", fill="y")

        # 加载导出历史
        self._load_export_history()

        # 布局滚动框架
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_document_tab(self) -> None:
        """创建文档生成标签页."""
        document_frame = ttk.Frame(self.notebook)
        self.notebook.add(document_frame, text="文档生成")

        # 文档生成说明
        info_frame = ttk.LabelFrame(document_frame, text="文档生成功能", padding=15)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        info_text = (
            "文档生成功能支持:\n"
            "• 合同文档生成 (Word/PDF)\n"
            "• 报价单生成 (Word/PDF)\n"
            "• 客户报告生成 (PDF)\n"
            "• 供应商报告生成 (PDF)\n\n"
            "使用预定义模板,自动填充数据生成专业文档."
        )

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # 文档类型选择
        template_frame = ttk.LabelFrame(document_frame, text="选择文档类型", padding=15)
        template_frame.pack(fill=tk.X, padx=10, pady=5)

        self.document_type_var = tk.StringVar(value="contract")

        document_types = [
            ("contract", "合同文档", "生成标准合同文档"),
            ("quote", "报价单", "生成产品报价单"),
            ("customer_report", "客户报告", "生成客户分析报告"),
            ("supplier_report", "供应商报告", "生成供应商评估报告"),
        ]

        for value, title, description in document_types:
            frame = ttk.Frame(template_frame)
            frame.pack(fill=tk.X, pady=2)

            ttk.Radiobutton(
                frame,
                text=title,
                variable=self.document_type_var,
                value=value,
            ).pack(side=tk.LEFT)

            ttk.Label(frame, text=f" - {description}", foreground="gray").pack(
                side=tk.LEFT
            )

        # 文档格式选择
        format_frame = ttk.LabelFrame(document_frame, text="输出格式", padding=15)
        format_frame.pack(fill=tk.X, padx=10, pady=5)

        self.document_format_var = tk.StringVar(value="pdf")

        ttk.Radiobutton(
            format_frame,
            text="PDF文档 (推荐)",
            variable=self.document_format_var,
            value="pdf",
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            format_frame,
            text="Word文档",
            variable=self.document_format_var,
            value="word",
        ).pack(anchor=tk.W)

        # 操作按钮
        button_frame = ttk.Frame(document_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=15)

        ttk.Button(
            button_frame,
            text="生成文档",
            command=self._generate_document,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="预览模板",
            command=self._preview_template,
        ).pack(side=tk.LEFT)

        # 状态显示
        self.document_status_label = ttk.Label(
            document_frame, text="", foreground="blue"
        )
        self.document_status_label.pack(padx=10, pady=5)

    def _create_statistics_tab(self) -> None:
        """创建统计信息标签页."""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="统计信息")

        # 数据统计概览
        overview_frame = ttk.LabelFrame(stats_frame, text="数据概览", padding=15)
        overview_frame.pack(fill=tk.X, padx=10, pady=10)

        # 创建统计卡片
        cards_frame = ttk.Frame(overview_frame)
        cards_frame.pack(fill=tk.X)

        self.stats_cards = {}

        stats_info = [
            ("customers", "客户数据", "客户"),
            ("suppliers", "供应商数据", "供应商"),
            ("contracts", "合同数据", "合同"),
            ("quotes", "报价数据", "报价"),
        ]

        for i, (key, title, unit) in enumerate(stats_info):
            card_frame = ttk.LabelFrame(cards_frame, text=title, padding=10)
            card_frame.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="ew")

            # 数量显示
            count_label = ttk.Label(
                card_frame,
                text="0",
                font=("Microsoft YaHei UI", 16, "bold"),
                foreground="blue",
            )
            count_label.pack()

            unit_label = ttk.Label(card_frame, text=f"条{unit}记录")
            unit_label.pack()

            # 最后更新时间
            time_label = ttk.Label(
                card_frame, text="", font=("Microsoft YaHei UI", 8), foreground="gray"
            )
            time_label.pack(pady=(5, 0))

            self.stats_cards[key] = {
                "count": count_label,
                "time": time_label,
            }

        # 配置网格权重
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)

        # 操作历史统计
        history_frame = ttk.LabelFrame(stats_frame, text="操作历史", padding=15)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 刷新按钮
        refresh_frame = ttk.Frame(history_frame)
        refresh_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            refresh_frame,
            text="刷新统计",
            command=self._refresh_statistics,
        ).pack(side=tk.LEFT)

        ttk.Button(
            refresh_frame,
            text="清理历史",
            command=self._clear_history,
        ).pack(side=tk.LEFT, padx=(10, 0))

        # 历史记录表格
        history_columns = ("time", "operation", "type", "result", "details")
        self.history_tree = ttk.Treeview(
            history_frame, columns=history_columns, show="headings", height=10
        )

        # 设置列标题和宽度
        self.history_tree.heading("time", text="时间")
        self.history_tree.heading("operation", text="操作")
        self.history_tree.heading("type", text="数据类型")
        self.history_tree.heading("result", text="结果")
        self.history_tree.heading("details", text="详情")

        self.history_tree.column("time", width=120)
        self.history_tree.column("operation", width=80)
        self.history_tree.column("type", width=80)
        self.history_tree.column("result", width=80)
        self.history_tree.column("details", width=200)

        # 滚动条
        history_tree_scrollbar = ttk.Scrollbar(
            history_frame, orient="vertical", command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=history_tree_scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True)
        history_tree_scrollbar.pack(side="right", fill="y")

        # 加载操作历史
        self._load_operation_history()

        # 更新统计信息
        self._update_statistics_display()

    def _bind_events(self) -> None:
        """绑定事件处理."""

        # 绑定鼠标滚轮事件到画布
        def _on_mousewheel(event):
            # 获取当前选中的标签页
            current_tab = self.notebook.select()
            if current_tab:
                # 查找当前标签页中的画布
                tab_widget = self.notebook.nametowidget(current_tab)
                for child in tab_widget.winfo_children():
                    if isinstance(child, tk.Canvas):
                        child.yview_scroll(int(-1 * (event.delta / 120)), "units")
                        break

        # 绑定到整个面板
        self.bind_all("<MouseWheel>", _on_mousewheel)

    def _apply_styles(self) -> None:
        """应用样式."""
        # 设置面板样式
        self.configure(relief="flat", borderwidth=0)

    def _load_statistics(self) -> None:
        """加载统计信息."""
        try:
            if not self.import_export_service:
                return

            # 模拟统计数据 - 实际应用中应从服务获取
            self.statistics = {
                "customers": {"total": 1234, "last_updated": "2024-01-15 10:30"},
                "suppliers": {"total": 567, "last_updated": "2024-01-14 16:45"},
                "contracts": {"total": 890, "last_updated": "2024-01-13 14:20"},
                "quotes": {"total": 2345, "last_updated": "2024-01-12 09:15"},
            }

        except Exception as e:
            self.logger.error(f"加载统计信息失败: {e}")

    def _open_import_dialog(self) -> None:
        """打开导入对话框."""
        try:
            if not self.import_export_service:
                self._show_error("导入导出服务不可用")
                return

            # 创建并显示导入对话框
            dialog = ImportDialogTTK(
                parent=self,
                import_export_service=self.import_export_service,
            )

            result, import_info = dialog.show_dialog()

            if result == "ok" and import_info:
                self._show_success(f"导入完成: {import_info}")
                # 刷新导入历史和统计信息
                self._load_import_history()
                self._refresh_statistics()

        except Exception as e:
            self.logger.error(f"打开导入对话框失败: {e}")
            self._show_error(f"打开导入对话框失败: {e}")

    def _open_export_dialog(self) -> None:
        """打开导出对话框."""
        try:
            if not self.import_export_service:
                self._show_error("导入导出服务不可用")
                return

            # 创建并显示导出对话框
            dialog = ExportDialogTTK(
                parent=self,
                import_export_service=self.import_export_service,
            )

            result, export_info = dialog.show_dialog()

            if result == "ok" and export_info:
                self._show_success(f"导出完成: {export_info}")
                # 刷新导出历史
                self._load_export_history()

        except Exception as e:
            self.logger.error(f"打开导出对话框失败: {e}")
            self._show_error(f"打开导出对话框失败: {e}")

    def _open_advanced_export(self) -> None:
        """打开高级导出选项."""
        try:
            # 创建高级导出对话框,预设当前选择的数据类型和格式
            dialog = ExportDialogTTK(
                parent=self,
                import_export_service=self.import_export_service,
            )

            # 设置默认值
            data_type = self.export_data_type_var.get()
            export_format = self.export_format_var.get()

            # 这里可以预设对话框的初始值
            # dialog.set_initial_values(data_type, export_format)

            result, export_info = dialog.show_dialog()

            if result == "ok" and export_info:
                self._show_success(f"导出完成: {export_info}")
                self._load_export_history()

        except Exception as e:
            self.logger.error(f"打开高级导出失败: {e}")
            self._show_error(f"打开高级导出失败: {e}")

    def _download_template(self) -> None:
        """下载导入模板."""
        try:
            from tkinter import filedialog

            data_type = self.import_data_type_var.get()

            # 选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="保存导入模板",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel文件", "*.xlsx"),
                    ("CSV文件", "*.csv"),
                    ("所有文件", "*.*"),
                ],
                initialname=f"{data_type}_template.xlsx",
            )

            if file_path:
                # 生成模板文件
                self._generate_template_file(data_type, file_path)
                self._show_success(f"模板已保存到: {file_path}")

        except Exception as e:
            self.logger.error(f"下载模板失败: {e}")
            self._show_error(f"下载模板失败: {e}")

    def _generate_template_file(self, data_type: str, file_path: str) -> None:
        """生成模板文件."""
        try:
            # 定义模板字段
            template_fields = {
                "customers": [
                    "客户名称",
                    "联系人",
                    "联系电话",
                    "邮箱地址",
                    "公司名称",
                    "地址",
                    "客户类型",
                    "备注",
                ],
                "suppliers": [
                    "供应商名称",
                    "联系人",
                    "联系电话",
                    "邮箱地址",
                    "公司名称",
                    "地址",
                    "供应商类型",
                    "备注",
                ],
                "contracts": [
                    "合同名称",
                    "客户名称",
                    "合同金额",
                    "签订日期",
                    "开始日期",
                    "结束日期",
                    "合同状态",
                    "备注",
                ],
            }

            fields = template_fields.get(data_type, [])

            if file_path.endswith(".xlsx"):
                # 生成Excel模板
                import pandas as pd

                df = pd.DataFrame(columns=fields)
                df.to_excel(file_path, index=False)
            else:
                # 生成CSV模板
                import csv

                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(fields)

        except Exception as e:
            raise Exception(f"生成模板文件失败: {e}") from e

    def _generate_document(self) -> None:
        """生成文档."""
        try:
            if not self.import_export_service:
                self._show_error("导入导出服务不可用")
                return

            document_type = self.document_type_var.get()
            document_format = self.document_format_var.get()

            # 选择保存位置
            from tkinter import filedialog

            ext = ".pdf" if document_format == "pdf" else ".docx"
            file_path = filedialog.asksaveasfilename(
                title="保存文档",
                defaultextension=ext,
                filetypes=[
                    ("PDF文件", "*.pdf")
                    if document_format == "pdf"
                    else ("Word文档", "*.docx"),
                    ("所有文件", "*.*"),
                ],
                initialname=f"{document_type}_document{ext}",
            )

            if file_path:
                # 显示进度对话框
                self.progress_dialog = ProgressDialogTTK(
                    parent=self,
                    title="生成文档",
                    message="正在生成文档,请稍候...",
                    show_cancel=False,
                )

                # 在后台线程生成文档
                def generate_worker():
                    try:
                        # 模拟文档数据
                        document_data = {
                            "title": f"{document_type.title()} 文档",
                            "date": "2024-01-15",
                            "content": "这是一个示例文档内容.",
                        }

                        if document_format == "pdf":
                            success = self.import_export_service.generate_pdf_document(
                                document_type, document_data, file_path
                            )
                        else:
                            success = self.import_export_service.generate_word_document(
                                document_type, document_data, file_path
                            )

                        # 更新UI
                        self.after(
                            100, lambda: self._on_document_generated(success, file_path)
                        )

                    except Exception:
                        self.after(100, lambda: self._on_document_error(str(e)))

                # 启动生成线程
                self.operation_thread = threading.Thread(
                    target=generate_worker, daemon=True
                )
                self.operation_thread.start()

                # 显示进度对话框
                self.progress_dialog.show_dialog()

        except Exception as e:
            self.logger.error(f"生成文档失败: {e}")
            self._show_error(f"生成文档失败: {e}")

    def _on_document_generated(self, success: bool, file_path: str) -> None:
        """文档生成完成处理."""
        if self.progress_dialog:
            self.progress_dialog.close_dialog()
            self.progress_dialog = None

        if success:
            self._show_success(f"文档已生成: {file_path}")
            self.document_status_label.configure(text=f"最近生成: {file_path}")
        else:
            self._show_error("文档生成失败")

    def _on_document_error(self, error_message: str) -> None:
        """文档生成错误处理."""
        if self.progress_dialog:
            self.progress_dialog.close_dialog()
            self.progress_dialog = None

        self._show_error(f"文档生成失败: {error_message}")

    def _preview_template(self) -> None:
        """预览文档模板."""
        try:
            document_type = self.document_type_var.get()

            # 显示模板预览信息
            template_info = {
                "contract": "合同模板包含:合同标题、甲乙双方信息、合同条款、签署信息等.",
                "quote": "报价单模板包含:报价标题、客户信息、产品清单、价格明细、有效期等.",
                "customer_report": "客户报告模板包含:客户基本信息、交易历史、价值分析、建议等.",
                "supplier_report": "供应商报告模板包含:供应商信息、合作历史、质量评估、风险分析等.",
            }

            info = template_info.get(document_type, "模板信息不可用")
            self._show_info(f"模板预览\n\n{info}")

        except Exception as e:
            self.logger.error(f"预览模板失败: {e}")
            self._show_error(f"预览模板失败: {e}")

    def _update_export_statistics(self) -> None:
        """更新导出统计信息."""
        try:
            data_type = self.export_data_type_var.get()
            stats = self.statistics.get(data_type, {})
            total = stats.get("total", 0)

            self.export_stats_label.configure(text=f"{total} 条记录可导出")

        except Exception as e:
            self.logger.error(f"更新导出统计失败: {e}")

    def _load_import_history(self) -> None:
        """加载导入历史记录."""
        try:
            # 清空现有记录
            for item in self.import_history_tree.get_children():
                self.import_history_tree.delete(item)

            # 模拟历史记录数据
            history_data = [
                ("2024-01-15 10:30", "客户数据", "customers.xlsx", "成功", "120"),
                ("2024-01-14 16:45", "供应商数据", "suppliers.csv", "成功", "85"),
                (
                    "2024-01-13 14:20",
                    "客户数据",
                    "new_customers.xlsx",
                    "部分失败",
                    "95/100",
                ),
                ("2024-01-12 09:15", "合同数据", "contracts.csv", "成功", "45"),
            ]

            for record in history_data:
                self.import_history_tree.insert("", "end", values=record)

        except Exception as e:
            self.logger.error(f"加载导入历史失败: {e}")

    def _load_export_history(self) -> None:
        """加载导出历史记录."""
        try:
            # 清空现有记录
            for item in self.export_history_tree.get_children():
                self.export_history_tree.delete(item)

            # 模拟历史记录数据
            history_data = [
                (
                    "2024-01-15 11:20",
                    "客户数据",
                    "Excel",
                    "/exports/customers_20240115.xlsx",
                    "1234",
                ),
                (
                    "2024-01-14 17:30",
                    "供应商数据",
                    "CSV",
                    "/exports/suppliers_20240114.csv",
                    "567",
                ),
                (
                    "2024-01-13 15:45",
                    "客户数据",
                    "PDF",
                    "/exports/customers_report.pdf",
                    "1200",
                ),
                (
                    "2024-01-12 10:30",
                    "合同数据",
                    "Excel",
                    "/exports/contracts_20240112.xlsx",
                    "890",
                ),
            ]

            for record in history_data:
                self.export_history_tree.insert("", "end", values=record)

        except Exception as e:
            self.logger.error(f"加载导出历史失败: {e}")

    def _load_operation_history(self) -> None:
        """加载操作历史记录."""
        try:
            # 清空现有记录
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            # 模拟操作历史数据
            history_data = [
                (
                    "2024-01-15 11:20",
                    "导出",
                    "客户数据",
                    "成功",
                    "导出1234条记录到Excel",
                ),
                ("2024-01-15 10:30", "导入", "客户数据", "成功", "导入120条客户记录"),
                (
                    "2024-01-14 17:30",
                    "导出",
                    "供应商数据",
                    "成功",
                    "导出567条记录到CSV",
                ),
                (
                    "2024-01-14 16:45",
                    "导入",
                    "供应商数据",
                    "成功",
                    "导入85条供应商记录",
                ),
                (
                    "2024-01-13 15:45",
                    "文档生成",
                    "客户报告",
                    "成功",
                    "生成客户分析报告PDF",
                ),
                (
                    "2024-01-13 14:20",
                    "导入",
                    "客户数据",
                    "部分失败",
                    "导入95/100条记录,5条失败",
                ),
            ]

            for record in history_data:
                self.history_tree.insert("", "end", values=record)

        except Exception as e:
            self.logger.error(f"加载操作历史失败: {e}")

    def _update_statistics_display(self) -> None:
        """更新统计信息显示."""
        try:
            for key, stats in self.statistics.items():
                if key in self.stats_cards:
                    card = self.stats_cards[key]
                    card["count"].configure(text=str(stats.get("total", 0)))

                    last_updated = stats.get("last_updated", "")
                    if last_updated:
                        card["time"].configure(text=f"更新: {last_updated}")

        except Exception as e:
            self.logger.error(f"更新统计显示失败: {e}")

    def _refresh_statistics(self) -> None:
        """刷新统计信息."""
        try:
            # 重新加载统计信息
            self._load_statistics()
            self._update_statistics_display()
            self._update_export_statistics()

            self._show_info("统计信息已刷新")

        except Exception as e:
            self.logger.error(f"刷新统计信息失败: {e}")
            self._show_error(f"刷新统计信息失败: {e}")

    def _clear_history(self) -> None:
        """清理历史记录."""
        try:
            from tkinter import messagebox

            if messagebox.askyesno(
                "确认清理", "确定要清理所有历史记录吗?此操作不可撤销."
            ):
                # 清空所有历史记录表格
                for item in self.import_history_tree.get_children():
                    self.import_history_tree.delete(item)

                for item in self.export_history_tree.get_children():
                    self.export_history_tree.delete(item)

                for item in self.history_tree.get_children():
                    self.history_tree.delete(item)

                self._show_success("历史记录已清理")

        except Exception as e:
            self.logger.error(f"清理历史记录失败: {e}")
            self._show_error(f"清理历史记录失败: {e}")

    def _show_success(self, message: str) -> None:
        """显示成功消息."""
        from tkinter import messagebox

        messagebox.showinfo("成功", message)

    def _show_error(self, message: str) -> None:
        """显示错误消息."""
        from tkinter import messagebox

        messagebox.showerror("错误", message)

    def _show_info(self, message: str) -> None:
        """显示信息消息."""
        from tkinter import messagebox

        messagebox.showinfo("信息", message)

    def cleanup(self) -> None:
        """清理资源."""
        try:
            # 取消正在进行的操作
            if self.operation_thread and self.operation_thread.is_alive():
                # 这里应该实现线程取消逻辑
                pass

            # 关闭进度对话框
            if self.progress_dialog:
                self.progress_dialog.close_dialog()
                self.progress_dialog = None

            self.logger.debug("导入导出面板资源清理完成")

        except Exception as e:
            self.logger.error(f"资源清理失败: {e}")

        super().cleanup()

    def get_current_statistics(self) -> dict[str, Any]:
        """获取当前统计信息.

        Returns:
            当前的统计信息字典
        """
        return self.statistics.copy()

    def refresh_data(self) -> None:
        """刷新面板数据."""
        try:
            self._load_statistics()
            self._load_import_history()
            self._load_export_history()
            self._load_operation_history()
            self._update_statistics_display()
            self._update_export_statistics()

            self.logger.info("面板数据刷新完成")

        except Exception as e:
            self.logger.error(f"刷新面板数据失败: {e}")
            self._show_error(f"刷新面板数据失败: {e}")


# 便利函数
def create_import_export_panel(
    parent: tk.Widget,
    import_export_service: ImportExportService | None = None,
) -> ImportExportPanelTTK:
    """创建导入导出面板.

    Args:
        parent: 父窗口
        import_export_service: 导入导出服务实例

    Returns:
        ImportExportPanelTTK: 创建的面板实例
    """
    return ImportExportPanelTTK(
        parent=parent,
        import_export_service=import_export_service,
    )
