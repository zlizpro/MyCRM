"""MiniCRM TTK报价比较组件.

基于TTK框架实现的报价对比分析组件, 用于替换Qt版本的报价比较功能.
支持多个报价的并排比较、差异高亮显示、比较结果导出等功能.

设计特点:
- 使用TTK组件构建比较界面
- 支持多种比较模式(详细比较、简要比较、趋势分析)
- 提供差异高亮和统计分析
- 集成导出和打印功能
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any, Callable

from minicrm.core.exceptions import MiniCRMError, ServiceError
from minicrm.ui.ttk_base.base_widget import BaseWidget


if TYPE_CHECKING:
    from minicrm.services.quote_service import QuoteServiceRefactored


class QuoteComparisonTTK(BaseWidget):
    """TTK报价比较组件.

    提供完整的报价对比分析功能:
    - 多个报价的并排比较
    - 差异高亮显示
    - 比较统计和分析
    - 比较结果导出
    - 历史趋势分析
    """

    def __init__(
        self,
        parent: tk.Widget,
        quote_service: QuoteServiceRefactored,
        comparison_mode: str = "detailed",
        max_quotes: int = 4,
        **kwargs: str | int | bool,
    ) -> None:
        """初始化报价比较组件.

        Args:
            parent: 父组件
            quote_service: 报价服务实例
            comparison_mode: 比较模式 ('detailed', 'summary', 'trend')
            max_quotes: 最大比较报价数量
            **kwargs: 其他参数
        """
        self._quote_service = quote_service
        self.comparison_mode = comparison_mode
        self.max_quotes = max_quotes

        # 数据存储
        self._quotes_to_compare: list[dict[str, Any]] = []
        self._comparison_result: dict[str, Any] | None = None

        # UI组件
        self._notebook: ttk.Notebook | None = None
        self._comparison_frame: ttk.Frame | None = None
        self._statistics_frame: ttk.Frame | None = None
        self._chart_frame: ttk.Frame | None = None

        # 事件回调
        self.on_comparison_completed: Callable | None = None
        self.on_quote_selected: Callable | None = None

        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题区域
        self._create_title_area(main_container)

        # 创建工具栏
        self._create_toolbar(main_container)

        # 创建选择区域
        self._create_selection_area(main_container)

        # 创建比较结果区域
        self._create_comparison_area(main_container)

    def _create_title_area(self, parent: ttk.Frame) -> None:
        """创建标题区域."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        # 标题
        title_label = ttk.Label(
            title_frame, text="报价比较分析", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 模式选择
        mode_frame = ttk.Frame(title_frame)
        mode_frame.pack(side=tk.RIGHT)

        ttk.Label(mode_frame, text="比较模式:").pack(side=tk.LEFT, padx=(0, 5))

        self._mode_var = tk.StringVar(value=self.comparison_mode)
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self._mode_var,
            values=["detailed", "summary", "trend"],
            state="readonly",
            width=10,
        )
        mode_combo.pack(side=tk.LEFT)
        mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

    def _create_toolbar(self, parent: ttk.Frame) -> None:
        """创建工具栏."""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT)

        # 添加报价按钮
        self._add_quote_btn = ttk.Button(
            left_frame, text="+ 添加报价", command=self._add_quote_to_comparison
        )
        self._add_quote_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 清空比较按钮
        self._clear_btn = ttk.Button(
            left_frame, text="清空", command=self._clear_comparison
        )
        self._clear_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 开始比较按钮
        self._compare_btn = ttk.Button(
            left_frame,
            text="开始比较",
            command=self._start_comparison,
            state=tk.DISABLED,
        )
        self._compare_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮
        right_frame = ttk.Frame(toolbar_frame)
        right_frame.pack(side=tk.RIGHT)

        # 导出按钮
        self._export_btn = ttk.Button(
            right_frame,
            text="导出结果",
            command=self._export_comparison,
            state=tk.DISABLED,
        )
        self._export_btn.pack(side=tk.LEFT, padx=(5, 0))

        # 打印按钮
        self._print_btn = ttk.Button(
            right_frame, text="打印", command=self._print_comparison, state=tk.DISABLED
        )
        self._print_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_selection_area(self, parent: ttk.Frame) -> None:
        """创建报价选择区域."""
        selection_frame = ttk.LabelFrame(parent, text="选择比较报价", padding=10)
        selection_frame.pack(fill=tk.X, pady=(0, 10))

        # 创建选择列表
        self._selection_frame = ttk.Frame(selection_frame)
        self._selection_frame.pack(fill=tk.X)

        # 初始显示提示
        self._update_selection_display()

    def _create_comparison_area(self, parent: ttk.Frame) -> None:
        """创建比较结果区域."""
        comparison_frame = ttk.LabelFrame(parent, text="比较结果", padding=10)
        comparison_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标签页
        self._notebook = ttk.Notebook(comparison_frame)
        self._notebook.pack(fill=tk.BOTH, expand=True)

        # 详细比较标签页
        self._comparison_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._comparison_frame, text="详细比较")

        # 统计分析标签页
        self._statistics_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._statistics_frame, text="统计分析")

        # 趋势图表标签页
        self._chart_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._chart_frame, text="趋势图表")

        # 初始显示提示
        self._show_empty_comparison()

    def _update_selection_display(self) -> None:
        """更新选择显示."""
        # 清空现有显示
        for widget in self._selection_frame.winfo_children():
            widget.destroy()

        if not self._quotes_to_compare:
            # 显示提示信息
            tip_label = ttk.Label(
                self._selection_frame,
                text=f"请选择要比较的报价(最多{self.max_quotes}个)",
                foreground="gray",
            )
            tip_label.pack(pady=20)
        else:
            # 显示已选择的报价
            for i, quote in enumerate(self._quotes_to_compare):
                quote_frame = ttk.Frame(self._selection_frame)
                quote_frame.pack(fill=tk.X, pady=2)

                # 报价信息
                info_text = (
                    f"{i + 1}. {quote.get('quote_number', 'N/A')} - "
                    f"{quote.get('customer_name', 'N/A')} - "
                    f"{quote.get('formatted_total', 'N/A')}"
                )
                info_label = ttk.Label(quote_frame, text=info_text)
                info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

                # 移除按钮
                def make_remove_command(idx: int) -> Callable[[], None]:
                    return lambda: self._remove_quote_from_comparison(idx)

                remove_btn = ttk.Button(
                    quote_frame,
                    text="X",
                    width=3,
                    command=make_remove_command(i),
                )
                remove_btn.pack(side=tk.RIGHT)

        # 更新按钮状态
        self._update_button_states()

    def _update_button_states(self) -> None:
        """更新按钮状态."""
        quote_count = len(self._quotes_to_compare)

        # 添加按钮状态
        if quote_count >= self.max_quotes:
            self._add_quote_btn.config(state=tk.DISABLED)
        else:
            self._add_quote_btn.config(state=tk.NORMAL)

        # 比较按钮状态
        if quote_count >= 2:
            self._compare_btn.config(state=tk.NORMAL)
        else:
            self._compare_btn.config(state=tk.DISABLED)

        # 导出和打印按钮状态
        if self._comparison_result:
            self._export_btn.config(state=tk.NORMAL)
            self._print_btn.config(state=tk.NORMAL)
        else:
            self._export_btn.config(state=tk.DISABLED)
            self._print_btn.config(state=tk.DISABLED)

    def add_quote_for_comparison(self, quote_data: dict[str, Any]) -> bool:
        """添加报价到比较列表.

        Args:
            quote_data: 报价数据

        Returns:
            是否添加成功
        """
        if len(self._quotes_to_compare) >= self.max_quotes:
            messagebox.showwarning("提示", f"最多只能比较{self.max_quotes}个报价")
            return False

        # 检查是否已存在
        quote_id = quote_data.get("id")
        for existing_quote in self._quotes_to_compare:
            if existing_quote.get("id") == quote_id:
                messagebox.showwarning("提示", "该报价已在比较列表中")
                return False

        # 添加到比较列表
        self._quotes_to_compare.append(quote_data)
        self._update_selection_display()

        quote_number = quote_data.get("quote_number", "N/A")
        self.logger.info("添加报价到比较列表: %s", quote_number)
        return True

    def _add_quote_to_comparison(self) -> None:
        """添加报价到比较(通过对话框选择)."""
        # 这里应该打开一个报价选择对话框
        # 为了简化, 暂时显示提示
        messagebox.showinfo("提示", "请从报价列表中选择要比较的报价")

    def _remove_quote_from_comparison(self, index: int) -> None:
        """从比较列表中移除报价.

        Args:
            index: 要移除的报价索引
        """
        if 0 <= index < len(self._quotes_to_compare):
            removed_quote = self._quotes_to_compare.pop(index)
            self._update_selection_display()

            # 如果移除后少于2个报价, 清空比较结果
            if len(self._quotes_to_compare) < 2:
                self._comparison_result = None
                self._show_empty_comparison()

            quote_number = removed_quote.get("quote_number", "N/A")
            self.logger.info("从比较列表移除报价: %s", quote_number)

    def _clear_comparison(self) -> None:
        """清空比较."""
        self._quotes_to_compare.clear()
        self._comparison_result = None
        self._update_selection_display()
        self._show_empty_comparison()

        self.logger.info("清空报价比较")

    def _start_comparison(self) -> None:
        """开始比较."""
        if len(self._quotes_to_compare) < 2:
            messagebox.showwarning("提示", "至少需要选择2个报价进行比较")
            return

        try:
            # 获取报价ID列表
            quote_ids: list[int] = []
            for quote in self._quotes_to_compare:
                quote_id = quote.get("id")
                if isinstance(quote_id, int):
                    quote_ids.append(quote_id)

            # 调用服务进行比较
            self._comparison_result = self._quote_service.compare_quotes(
                quote_ids, self.comparison_mode
            )

            # 显示比较结果
            self._display_comparison_result()

            # 触发完成事件
            if self.on_comparison_completed:
                self.on_comparison_completed(self._comparison_result)

            self.logger.info("完成报价比较, 模式: %s", self.comparison_mode)

        except ServiceError as e:
            self.logger.exception("报价比较失败")
            messagebox.showerror("错误", f"报价比较失败: {e}")
        except MiniCRMError as e:
            self.logger.exception("报价比较时发生错误")
            messagebox.showerror("错误", f"报价比较时发生错误: {e}")

    def _display_comparison_result(self) -> None:
        """显示比较结果."""
        if not self._comparison_result:
            return

        # 显示详细比较
        self._display_detailed_comparison()

        # 显示统计分析
        self._display_statistics_analysis()

        # 显示趋势图表
        self._display_trend_chart()

        # 更新按钮状态
        self._update_button_states()

    def _display_detailed_comparison(self) -> None:
        """显示详细比较."""
        # 清空现有内容
        if self._comparison_frame:
            for widget in self._comparison_frame.winfo_children():
                widget.destroy()

        if not self._comparison_result:
            return

        # 创建滚动区域
        canvas = tk.Canvas(self._comparison_frame)
        scrollbar = ttk.Scrollbar(
            self._comparison_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局滚动组件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 显示比较表格
        self._create_comparison_table(scrollable_frame)

    def _create_comparison_table(self, parent: ttk.Frame) -> None:
        """创建比较表格."""
        # 获取比较数据
        if not self._comparison_result:
            ttk.Label(parent, text="没有比较数据").pack(pady=20)
            return

        quotes_data = self._comparison_result.get("quotes", [])
        differences = self._comparison_result.get("differences", {})

        if not quotes_data:
            ttk.Label(parent, text="没有比较数据").pack(pady=20)
            return

        # 创建表格框架
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 表头
        headers = ["比较项目"] + [f"报价{i + 1}" for i in range(len(quotes_data))]

        for col, header in enumerate(headers):
            header_label = ttk.Label(
                table_frame,
                text=header,
                font=("Microsoft YaHei UI", 10, "bold"),
                relief="solid",
                borderwidth=1,
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=1, pady=1)

        # 比较项目
        comparison_items = [
            ("报价编号", "quote_number"),
            ("客户名称", "customer_name"),
            ("联系人", "contact_person"),
            ("报价状态", "status_display"),
            ("报价类型", "quote_type_display"),
            ("小计金额", "formatted_subtotal"),
            ("税额", "formatted_tax_amount"),
            ("总金额", "formatted_total"),
            ("报价日期", "formatted_quote_date"),
            ("有效期至", "formatted_valid_until"),
            ("剩余天数", "remaining_days"),
        ]

        # 填充数据
        for row, (item_name, item_key) in enumerate(comparison_items, 1):
            # 项目名称
            item_label = ttk.Label(
                table_frame,
                text=item_name,
                relief="solid",
                borderwidth=1,
                background="#f0f0f0",
            )
            item_label.grid(row=row, column=0, sticky="ew", padx=1, pady=1)

            # 各报价的值
            for col, quote_data in enumerate(quotes_data, 1):
                value = quote_data.get(item_key, "N/A")

                # 检查是否有差异
                is_different = item_key in differences
                bg_color = "#ffe6e6" if is_different else "white"

                value_label = ttk.Label(
                    table_frame,
                    text=str(value),
                    relief="solid",
                    borderwidth=1,
                    background=bg_color,
                )
                value_label.grid(row=row, column=col, sticky="ew", padx=1, pady=1)

        # 配置列权重
        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)

    def _display_statistics_analysis(self) -> None:
        """显示统计分析."""
        # 清空现有内容
        if self._statistics_frame:
            for widget in self._statistics_frame.winfo_children():
                widget.destroy()

        if not self._comparison_result:
            return

        # 获取统计数据
        statistics = self._comparison_result.get("statistics", {})

        # 创建统计信息显示
        stats_frame = ttk.Frame(self._statistics_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 基本统计
        basic_frame = ttk.LabelFrame(stats_frame, text="基本统计", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))

        basic_stats = [
            ("比较报价数量", len(self._quotes_to_compare)),
            ("平均金额", statistics.get("average_amount", "N/A")),
            ("最高金额", statistics.get("max_amount", "N/A")),
            ("最低金额", statistics.get("min_amount", "N/A")),
            ("金额差异", statistics.get("amount_difference", "N/A")),
        ]

        for label, value in basic_stats:
            row_frame = ttk.Frame(basic_frame)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=f"{label}:").pack(side=tk.LEFT)
            ttk.Label(
                row_frame, text=str(value), font=("Microsoft YaHei UI", 9, "bold")
            ).pack(side=tk.RIGHT)

        # 差异分析
        diff_frame = ttk.LabelFrame(stats_frame, text="差异分析", padding=10)
        diff_frame.pack(fill=tk.X, pady=(0, 10))

        differences = self._comparison_result.get("differences", {})
        if differences:
            for field, diff_info in differences.items():
                diff_text = f"{field}: {diff_info.get('description', '存在差异')}"
                ttk.Label(diff_frame, text=diff_text).pack(anchor=tk.W, pady=1)
        else:
            ttk.Label(diff_frame, text="所有比较项目都相同").pack(anchor=tk.W)

    def _display_trend_chart(self) -> None:
        """显示趋势图表."""
        # 清空现有内容
        if self._chart_frame:
            for widget in self._chart_frame.winfo_children():
                widget.destroy()

        # 暂时显示占位符
        placeholder_label = ttk.Label(
            self._chart_frame,
            text="趋势图表功能将在后续版本中实现",
            font=("Microsoft YaHei UI", 12),
            foreground="gray",
        )
        placeholder_label.pack(expand=True)

    def _show_empty_comparison(self) -> None:
        """显示空比较状态."""
        # 清空所有标签页
        for frame in [
            self._comparison_frame,
            self._statistics_frame,
            self._chart_frame,
        ]:
            if frame:
                for widget in frame.winfo_children():
                    widget.destroy()

                # 显示提示
                tip_label = ttk.Label(
                    frame,
                    text="请选择报价并开始比较",
                    font=("Microsoft YaHei UI", 12),
                    foreground="gray",
                )
                tip_label.pack(expand=True)

    def _on_mode_changed(self, _event: object = None) -> None:
        """处理比较模式变化."""
        new_mode = self._mode_var.get()
        if new_mode != self.comparison_mode:
            self.comparison_mode = new_mode

            # 如果已有比较结果, 重新比较
            if self._comparison_result and len(self._quotes_to_compare) >= 2:
                self._start_comparison()

            self.logger.info("比较模式已更改为: %s", new_mode)

    def _export_comparison(self) -> None:
        """导出比较结果."""
        if not self._comparison_result:
            messagebox.showwarning("提示", "没有比较结果可以导出")
            return

        # 选择导出格式
        export_formats = [
            ("Excel文件", "*.xlsx"),
            ("JSON文件", "*.json"),
            ("文本文件", "*.txt"),
        ]

        file_path = filedialog.asksaveasfilename(
            title="导出比较结果", filetypes=export_formats, defaultextension=".xlsx"
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".xlsx"):
                self._export_to_excel(file_path)
            elif file_path.endswith(".json"):
                self._export_to_json(file_path)
            elif file_path.endswith(".txt"):
                self._export_to_text(file_path)

            messagebox.showinfo("成功", f"比较结果已导出到:\n{file_path}")

        except MiniCRMError as e:
            self.logger.exception("导出比较结果失败")
            messagebox.showerror("错误", f"导出失败: {e}")

    def _export_to_json(self, file_path: str) -> None:
        """导出为JSON格式."""
        export_data = {
            "comparison_mode": self.comparison_mode,
            "comparison_time": datetime.now(timezone.utc).isoformat(),
            "quotes_compared": len(self._quotes_to_compare),
            "comparison_result": self._comparison_result,
        }

        Path(file_path).write_text(
            json.dumps(export_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _export_to_text(self, file_path: str) -> None:
        """导出为文本格式."""
        content = [
            "报价比较结果",
            "=" * 50,
            "",
            f"比较模式: {self.comparison_mode}",
            f"比较时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
            f"比较报价数量: {len(self._quotes_to_compare)}",
            "",
        ]

        # 写入比较数据
        if self._comparison_result:
            quotes_data = self._comparison_result.get("quotes", [])
            for i, quote in enumerate(quotes_data):
                content.extend(
                    [
                        f"报价 {i + 1}:",
                        f"  编号: {quote.get('quote_number', 'N/A')}",
                        f"  客户: {quote.get('customer_name', 'N/A')}",
                        f"  金额: {quote.get('formatted_total', 'N/A')}",
                        f"  状态: {quote.get('status_display', 'N/A')}",
                        "",
                    ]
                )

        Path(file_path).write_text("\n".join(content), encoding="utf-8")

    def _export_to_excel(self, file_path: str) -> None:
        """导出为Excel格式."""
        # 这里需要实现Excel导出功能
        # 暂时抛出未实现异常
        msg = "Excel导出功能将在后续版本中实现"
        raise NotImplementedError(msg)

    def _print_comparison(self) -> None:
        """打印比较结果."""
        if not self._comparison_result:
            messagebox.showwarning("提示", "没有比较结果可以打印")
            return

        messagebox.showinfo("提示", "打印功能将在后续版本中实现")

    def get_comparison_result(self) -> dict[str, Any] | None:
        """获取比较结果.

        Returns:
            比较结果数据
        """
        return self._comparison_result

    def get_selected_quotes(self) -> list[dict[str, Any]]:
        """获取选中的报价列表.

        Returns:
            选中的报价数据列表
        """
        return self._quotes_to_compare.copy()

    def cleanup(self) -> None:
        """清理资源."""
        self._quotes_to_compare.clear()
        self._comparison_result = None
        super().cleanup()
