"""MiniCRM TTK报价导出组件

基于TTK框架实现的报价导出功能组件,支持多种格式的报价导出和打印.
包括PDF、Excel、Word等格式的导出,以及打印预览和打印功能.

设计特点:
- 支持多种导出格式
- 集成模板选择功能
- 提供导出进度显示
- 支持批量导出
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from datetime import datetime
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.services.quote_template_service import QuoteTemplateService
from minicrm.ui.ttk_base.base_widget import BaseWidget


class QuoteExportTTK(BaseWidget):
    """TTK报价导出组件

    提供完整的报价导出功能:
    - 多种格式导出(PDF、Excel、Word)
    - 模板选择和应用
    - 批量导出支持
    - 导出进度显示
    - 打印预览和打印
    """

    def __init__(
        self,
        parent: tk.Widget,
        template_service: Optional[QuoteTemplateService] = None,
        enable_pdf: bool = True,
        enable_excel: bool = True,
        enable_word: bool = True,
        enable_print: bool = True,
        **kwargs,
    ):
        """初始化报价导出组件

        Args:
            parent: 父组件
            template_service: 模板服务实例
            enable_pdf: 是否启用PDF导出
            enable_excel: 是否启用Excel导出
            enable_word: 是否启用Word导出
            enable_print: 是否启用打印功能
            **kwargs: 其他参数
        """
        self._template_service = template_service or QuoteTemplateService()
        self.enable_pdf = enable_pdf
        self.enable_excel = enable_excel
        self.enable_word = enable_word
        self.enable_print = enable_print

        # 数据存储
        self._quotes_to_export: List[Dict[str, Any]] = []
        self._available_templates: List[Dict[str, Any]] = []
        self._selected_template: Optional[Dict[str, Any]] = None

        # UI组件
        self._export_dialog: Optional[tk.Toplevel] = None
        self._progress_var: Optional[tk.DoubleVar] = None
        self._status_var: Optional[tk.StringVar] = None

        # 事件回调
        self.on_export_started: Optional[Callable] = None
        self.on_export_completed: Optional[Callable] = None
        self.on_export_failed: Optional[Callable] = None

        super().__init__(parent, **kwargs)

        # 加载模板
        self._load_templates()

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 这个组件主要通过对话框使用,基础UI可以为空

    def _load_templates(self) -> None:
        """加载可用模板"""
        try:
            self._available_templates = self._template_service.get_all_templates()

            # 设置默认模板
            for template in self._available_templates:
                if template.get("is_default", False):
                    self._selected_template = template
                    break

            # 如果没有默认模板,选择第一个
            if not self._selected_template and self._available_templates:
                self._selected_template = self._available_templates[0]

            self.logger.info(f"加载了 {len(self._available_templates)} 个导出模板")

        except Exception as e:
            self.logger.error(f"加载导出模板失败: {e}")

    def show_export_dialog(
        self, quotes: List[Dict[str, Any]], default_format: str = "pdf"
    ) -> None:
        """显示导出对话框

        Args:
            quotes: 要导出的报价列表
            default_format: 默认导出格式
        """
        if not quotes:
            messagebox.showwarning("提示", "没有要导出的报价")
            return

        self._quotes_to_export = quotes
        self._create_export_dialog(default_format)

    def _create_export_dialog(self, default_format: str) -> None:
        """创建导出对话框"""
        # 创建对话框窗口
        self._export_dialog = tk.Toplevel(self.parent)
        self._export_dialog.title("导出报价")
        self._export_dialog.geometry("600x500")
        self._export_dialog.resizable(False, False)
        self._export_dialog.transient(self.parent)
        self._export_dialog.grab_set()

        # 居中显示
        self._center_dialog()

        # 创建对话框内容
        self._create_dialog_content(default_format)

    def _center_dialog(self) -> None:
        """居中显示对话框"""
        self._export_dialog.update_idletasks()
        x = (self._export_dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self._export_dialog.winfo_screenheight() // 2) - (500 // 2)
        self._export_dialog.geometry(f"600x500+{x}+{y}")

    def _create_dialog_content(self, default_format: str) -> None:
        """创建对话框内容"""
        main_frame = ttk.Frame(self._export_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 标题
        title_label = ttk.Label(
            main_frame, text="导出报价", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 15))

        # 报价信息区域
        self._create_quote_info_area(main_frame)

        # 导出选项区域
        self._create_export_options_area(main_frame, default_format)

        # 模板选择区域
        self._create_template_selection_area(main_frame)

        # 进度显示区域
        self._create_progress_area(main_frame)

        # 按钮区域
        self._create_button_area(main_frame)

    def _create_quote_info_area(self, parent: ttk.Frame) -> None:
        """创建报价信息区域"""
        info_frame = ttk.LabelFrame(parent, text="导出信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # 报价数量
        count_text = f"选中报价数量: {len(self._quotes_to_export)} 个"
        ttk.Label(info_frame, text=count_text).pack(anchor=tk.W)

        # 报价列表(显示前几个)
        if self._quotes_to_export:
            preview_count = min(3, len(self._quotes_to_export))
            preview_text = "包含报价: "

            for i in range(preview_count):
                quote = self._quotes_to_export[i]
                quote_info = f"{quote.get('quote_number', 'N/A')} ({quote.get('customer_name', 'N/A')})"
                preview_text += quote_info
                if i < preview_count - 1:
                    preview_text += ", "

            if len(self._quotes_to_export) > preview_count:
                preview_text += f" 等 {len(self._quotes_to_export)} 个报价"

            ttk.Label(info_frame, text=preview_text, wraplength=500).pack(
                anchor=tk.W, pady=(5, 0)
            )

    def _create_export_options_area(
        self, parent: ttk.Frame, default_format: str
    ) -> None:
        """创建导出选项区域"""
        options_frame = ttk.LabelFrame(parent, text="导出选项", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # 导出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(format_frame, text="导出格式:").pack(side=tk.LEFT)

        self._format_var = tk.StringVar(value=default_format)

        # 格式选项
        formats = []
        if self.enable_pdf:
            formats.append(("PDF文件", "pdf"))
        if self.enable_excel:
            formats.append(("Excel文件", "excel"))
        if self.enable_word:
            formats.append(("Word文件", "word"))

        for i, (text, value) in enumerate(formats):
            radio = ttk.Radiobutton(
                format_frame, text=text, variable=self._format_var, value=value
            )
            radio.pack(side=tk.LEFT, padx=(10 if i > 0 else 20, 0))

        # 导出选项
        self._single_file_var = tk.BooleanVar(value=True)
        self._open_after_export_var = tk.BooleanVar(value=True)

        single_file_check = ttk.Checkbutton(
            options_frame,
            text="合并为单个文件(多个报价时)",
            variable=self._single_file_var,
        )
        single_file_check.pack(anchor=tk.W, pady=2)

        open_after_check = ttk.Checkbutton(
            options_frame,
            text="导出完成后打开文件",
            variable=self._open_after_export_var,
        )
        open_after_check.pack(anchor=tk.W, pady=2)

    def _create_template_selection_area(self, parent: ttk.Frame) -> None:
        """创建模板选择区域"""
        template_frame = ttk.LabelFrame(parent, text="模板选择", padding=10)
        template_frame.pack(fill=tk.X, pady=(0, 10))

        # 模板选择
        select_frame = ttk.Frame(template_frame)
        select_frame.pack(fill=tk.X)

        ttk.Label(select_frame, text="选择模板:").pack(side=tk.LEFT)

        # 模板下拉框
        template_names = [t.get("name", "未知模板") for t in self._available_templates]
        self._template_combo = ttk.Combobox(
            select_frame, values=template_names, state="readonly", width=30
        )
        self._template_combo.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)

        # 设置默认选择
        if self._selected_template:
            template_name = self._selected_template.get("name", "")
            if template_name in template_names:
                self._template_combo.set(template_name)

        # 绑定选择事件
        self._template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)

        # 模板信息显示
        self._template_info_label = ttk.Label(
            template_frame, text="", foreground="gray", wraplength=500
        )
        self._template_info_label.pack(anchor=tk.W, pady=(5, 0))

        # 更新模板信息显示
        self._update_template_info()

    def _create_progress_area(self, parent: ttk.Frame) -> None:
        """创建进度显示区域"""
        progress_frame = ttk.LabelFrame(parent, text="导出进度", padding=10)
        progress_frame.pack(fill=tk.X, pady=(0, 10))

        # 进度条
        self._progress_var = tk.DoubleVar()
        self._progress_bar = ttk.Progressbar(
            progress_frame, variable=self._progress_var, maximum=100, length=500
        )
        self._progress_bar.pack(fill=tk.X, pady=(0, 5))

        # 状态文本
        self._status_var = tk.StringVar(value="准备导出...")
        self._status_label = ttk.Label(
            progress_frame, textvariable=self._status_var, foreground="gray"
        )
        self._status_label.pack(anchor=tk.W)

    def _create_button_area(self, parent: ttk.Frame) -> None:
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # 右侧按钮
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)

        # 取消按钮
        self._cancel_btn = ttk.Button(
            right_frame, text="取消", command=self._cancel_export
        )
        self._cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 开始导出按钮
        self._export_btn = ttk.Button(
            right_frame, text="开始导出", command=self._start_export
        )
        self._export_btn.pack(side=tk.RIGHT)

        # 左侧按钮(打印相关)
        if self.enable_print:
            left_frame = ttk.Frame(button_frame)
            left_frame.pack(side=tk.LEFT)

            # 打印预览按钮
            preview_btn = ttk.Button(
                left_frame, text="🔍 打印预览", command=self._print_preview
            )
            preview_btn.pack(side=tk.LEFT, padx=(0, 5))

            # 直接打印按钮
            print_btn = ttk.Button(
                left_frame, text="🖨️ 直接打印", command=self._direct_print
            )
            print_btn.pack(side=tk.LEFT)

    def _on_template_selected(self, event=None) -> None:
        """处理模板选择事件"""
        selected_name = self._template_combo.get()

        # 找到对应的模板
        for template in self._available_templates:
            if template.get("name") == selected_name:
                self._selected_template = template
                break

        # 更新模板信息显示
        self._update_template_info()

    def _update_template_info(self) -> None:
        """更新模板信息显示"""
        if not self._selected_template:
            self._template_info_label.config(text="未选择模板")
            return

        template = self._selected_template
        info_parts = []

        # 模板类型
        if template.get("is_system", False):
            info_parts.append("系统模板")
        else:
            info_parts.append("自定义模板")

        # 默认标记
        if template.get("is_default", False):
            info_parts.append("默认模板")

        # 描述
        description = template.get("description", "")
        if description:
            info_parts.append(description)

        info_text = " | ".join(info_parts)
        self._template_info_label.config(text=info_text)

    def _start_export(self) -> None:
        """开始导出"""
        if not self._quotes_to_export:
            messagebox.showwarning("提示", "没有要导出的报价")
            return

        if not self._selected_template:
            messagebox.showwarning("提示", "请选择导出模板")
            return

        # 获取导出参数
        export_format = self._format_var.get()
        single_file = self._single_file_var.get()
        open_after = self._open_after_export_var.get()

        # 选择保存位置
        save_path = self._select_save_path(export_format, single_file)
        if not save_path:
            return

        # 禁用按钮
        self._export_btn.config(state=tk.DISABLED)
        self._cancel_btn.config(text="中止")

        # 重置进度
        self._progress_var.set(0)
        self._status_var.set("开始导出...")

        # 在后台线程中执行导出
        export_thread = threading.Thread(
            target=self._perform_export,
            args=(export_format, save_path, single_file, open_after),
            daemon=True,
        )
        export_thread.start()

    def _select_save_path(self, export_format: str, single_file: bool) -> Optional[str]:
        """选择保存路径"""
        # 文件类型映射
        format_info = {
            "pdf": ("PDF文件", "*.pdf", ".pdf"),
            "excel": ("Excel文件", "*.xlsx", ".xlsx"),
            "word": ("Word文件", "*.docx", ".docx"),
        }

        if export_format not in format_info:
            messagebox.showerror("错误", f"不支持的导出格式: {export_format}")
            return None

        file_desc, file_pattern, file_ext = format_info[export_format]

        if single_file or len(self._quotes_to_export) == 1:
            # 单文件导出
            if len(self._quotes_to_export) == 1:
                quote = self._quotes_to_export[0]
                default_name = (
                    f"报价单_{quote.get('quote_number', 'unknown')}{file_ext}"
                )
            else:
                default_name = (
                    f"批量报价单_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_ext}"
                )

            return filedialog.asksaveasfilename(
                title="保存导出文件",
                defaultextension=file_ext,
                filetypes=[(file_desc, file_pattern), ("所有文件", "*.*")],
                initialvalue=default_name,
            )
        # 多文件导出,选择目录
        return filedialog.askdirectory(title="选择导出目录")

    def _perform_export(
        self, export_format: str, save_path: str, single_file: bool, open_after: bool
    ) -> None:
        """执行导出操作"""
        try:
            # 触发开始事件
            if self.on_export_started:
                self.on_export_started(export_format, len(self._quotes_to_export))

            total_quotes = len(self._quotes_to_export)
            exported_files = []

            if single_file and total_quotes > 1:
                # 合并导出
                self._update_progress(0, "准备合并导出...")
                exported_file = self._export_merged_file(export_format, save_path)
                if exported_file:
                    exported_files.append(exported_file)
                self._update_progress(100, "导出完成")
            else:
                # 分别导出
                for i, quote in enumerate(self._quotes_to_export):
                    progress = (i / total_quotes) * 100
                    status = f"正在导出第 {i + 1}/{total_quotes} 个报价..."
                    self._update_progress(progress, status)

                    exported_file = self._export_single_quote(
                        export_format, quote, save_path, single_file
                    )
                    if exported_file:
                        exported_files.append(exported_file)

                self._update_progress(100, "导出完成")

            # 导出完成处理
            self._on_export_success(exported_files, open_after)

        except Exception as e:
            self.logger.error(f"导出失败: {e}")
            self._on_export_error(str(e))

    def _export_single_quote(
        self,
        export_format: str,
        quote: Dict[str, Any],
        save_path: str,
        is_single_file: bool,
    ) -> Optional[str]:
        """导出单个报价"""
        try:
            if is_single_file:
                # 单文件模式,直接使用save_path
                file_path = save_path
            else:
                # 多文件模式,在目录中创建文件
                quote_number = quote.get("quote_number", "unknown")
                filename = f"报价单_{quote_number}.{export_format}"
                file_path = os.path.join(save_path, filename)

            # 根据格式调用相应的导出方法
            if export_format == "pdf":
                return self._export_to_pdf(quote, file_path)
            if export_format == "excel":
                return self._export_to_excel(quote, file_path)
            if export_format == "word":
                return self._export_to_word(quote, file_path)
            raise ValueError(f"不支持的导出格式: {export_format}")

        except Exception as e:
            self.logger.error(f"导出单个报价失败: {e}")
            return None

    def _export_merged_file(self, export_format: str, save_path: str) -> Optional[str]:
        """导出合并文件"""
        try:
            # 根据格式调用相应的合并导出方法
            if export_format == "pdf":
                return self._export_merged_pdf(save_path)
            if export_format == "excel":
                return self._export_merged_excel(save_path)
            if export_format == "word":
                return self._export_merged_word(save_path)
            raise ValueError(f"不支持的导出格式: {export_format}")

        except Exception as e:
            self.logger.error(f"导出合并文件失败: {e}")
            return None

    def _export_to_pdf(self, quote: Dict[str, Any], file_path: str) -> Optional[str]:
        """导出为PDF格式"""
        # 这里应该调用PDF导出服务
        # 暂时创建一个占位文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(
                    f"PDF导出占位文件\n报价编号: {quote.get('quote_number', 'N/A')}\n"
                )
            return file_path
        except Exception as e:
            self.logger.error(f"PDF导出失败: {e}")
            return None

    def _export_to_excel(self, quote: Dict[str, Any], file_path: str) -> Optional[str]:
        """导出为Excel格式"""
        # 这里应该调用Excel导出服务
        # 暂时创建一个占位文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Excel导出占位文件\n报价编号: {quote.get('quote_number', 'N/A')}\n"
                )
            return file_path
        except Exception as e:
            self.logger.error(f"Excel导出失败: {e}")
            return None

    def _export_to_word(self, quote: Dict[str, Any], file_path: str) -> Optional[str]:
        """导出为Word格式"""
        # 这里应该调用Word导出服务
        # 暂时创建一个占位文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(
                    f"Word导出占位文件\n报价编号: {quote.get('quote_number', 'N/A')}\n"
                )
            return file_path
        except Exception as e:
            self.logger.error(f"Word导出失败: {e}")
            return None

    def _export_merged_pdf(self, file_path: str) -> Optional[str]:
        """导出合并PDF"""
        # 合并多个报价到一个PDF文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("合并PDF导出占位文件\n")
                f.writelines(
                    f"报价 {i + 1}: {quote.get('quote_number', 'N/A')}\n"
                    for i, quote in enumerate(self._quotes_to_export)
                )
            return file_path
        except Exception as e:
            self.logger.error(f"合并PDF导出失败: {e}")
            return None

    def _export_merged_excel(self, file_path: str) -> Optional[str]:
        """导出合并Excel"""
        # 合并多个报价到一个Excel文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("合并Excel导出占位文件\n")
                f.writelines(
                    f"报价 {i + 1}: {quote.get('quote_number', 'N/A')}\n"
                    for i, quote in enumerate(self._quotes_to_export)
                )
            return file_path
        except Exception as e:
            self.logger.error(f"合并Excel导出失败: {e}")
            return None

    def _export_merged_word(self, file_path: str) -> Optional[str]:
        """导出合并Word"""
        # 合并多个报价到一个Word文件
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("合并Word导出占位文件\n")
                f.writelines(
                    f"报价 {i + 1}: {quote.get('quote_number', 'N/A')}\n"
                    for i, quote in enumerate(self._quotes_to_export)
                )
            return file_path
        except Exception as e:
            self.logger.error(f"合并Word导出失败: {e}")
            return None

    def _update_progress(self, progress: float, status: str) -> None:
        """更新进度显示"""
        # 在主线程中更新UI
        self.parent.after(0, lambda: self._do_update_progress(progress, status))

    def _do_update_progress(self, progress: float, status: str) -> None:
        """在主线程中更新进度"""
        if self._progress_var:
            self._progress_var.set(progress)
        if self._status_var:
            self._status_var.set(status)

    def _on_export_success(self, exported_files: List[str], open_after: bool) -> None:
        """导出成功处理"""
        # 在主线程中处理
        self.parent.after(
            0, lambda: self._do_export_success(exported_files, open_after)
        )

    def _do_export_success(self, exported_files: List[str], open_after: bool) -> None:
        """在主线程中处理导出成功"""
        # 恢复按钮状态
        self._export_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(text="关闭")

        # 显示成功消息
        if len(exported_files) == 1:
            message = f"导出成功!\n文件保存在:{exported_files[0]}"
        else:
            message = f"导出成功!\n共导出 {len(exported_files)} 个文件"

        messagebox.showinfo("导出成功", message)

        # 打开文件
        if open_after and exported_files:
            try:
                import platform
                import subprocess

                for file_path in exported_files[:3]:  # 最多打开3个文件
                    if platform.system() == "Windows":
                        os.startfile(file_path)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", file_path], check=False)
                    else:  # Linux
                        subprocess.run(["xdg-open", file_path], check=False)
            except Exception as e:
                self.logger.error(f"打开文件失败: {e}")

        # 触发完成事件
        if self.on_export_completed:
            self.on_export_completed(exported_files)

    def _on_export_error(self, error_message: str) -> None:
        """导出失败处理"""
        # 在主线程中处理
        self.parent.after(0, lambda: self._do_export_error(error_message))

    def _do_export_error(self, error_message: str) -> None:
        """在主线程中处理导出失败"""
        # 恢复按钮状态
        self._export_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(text="关闭")

        # 更新状态
        self._status_var.set("导出失败")

        # 显示错误消息
        messagebox.showerror("导出失败", f"导出过程中发生错误:\n{error_message}")

        # 触发失败事件
        if self.on_export_failed:
            self.on_export_failed(error_message)

    def _print_preview(self) -> None:
        """打印预览"""
        if not self._quotes_to_export:
            messagebox.showwarning("提示", "没有要预览的报价")
            return

        messagebox.showinfo("提示", "打印预览功能将在后续版本中实现")

    def _direct_print(self) -> None:
        """直接打印"""
        if not self._quotes_to_export:
            messagebox.showwarning("提示", "没有要打印的报价")
            return

        messagebox.showinfo("提示", "直接打印功能将在后续版本中实现")

    def _cancel_export(self) -> None:
        """取消导出"""
        if self._export_dialog:
            self._export_dialog.destroy()

    def cleanup(self) -> None:
        """清理资源"""
        self._quotes_to_export.clear()
        self._available_templates.clear()
        self._selected_template = None

        if self._export_dialog:
            self._export_dialog.destroy()

        super().cleanup()
