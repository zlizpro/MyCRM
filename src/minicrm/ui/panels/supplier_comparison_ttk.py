"""MiniCRM 供应商对比和评估TTK组件.

实现供应商对比和评估功能,包括:
- 供应商多维度对比分析
- 质量评分系统和可视化
- 供应商评估报告生成
- 对比结果导出功能

设计原则:
- 继承BaseWidget提供标准组件功能
- 集成图表组件进行数据可视化
- 连接SupplierService处理业务逻辑
- 遵循模块化设计和文件大小限制
"""

from __future__ import annotations

import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any

from minicrm.core.exceptions import ServiceError
from minicrm.models.supplier import QualityRating, SupplierType
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK


if TYPE_CHECKING:
    from minicrm.services.supplier_service import SupplierService


class SupplierComparisonTTK(BaseWidget):
    """供应商对比和评估TTK组件.

    提供完整的供应商对比和评估功能:
    - 多供应商选择和对比
    - 质量、价格、服务等维度评估
    - 可视化对比图表
    - 评估报告生成和导出
    """

    def __init__(
        self,
        parent: tk.Widget,
        supplier_service: SupplierService,
        **kwargs,
    ):
        """初始化供应商对比组件.

        Args:
            parent: 父组件
            supplier_service: 供应商服务实例
            **kwargs: 其他参数
        """
        self._supplier_service = supplier_service
        self._logger = logging.getLogger(__name__)

        # UI组件引用
        self._supplier_selector: ttk.Frame | None = None
        self._comparison_table: DataTableTTK | None = None
        self._chart_widget: ChartContainerTTK | None = None
        self._evaluation_frame: ttk.Frame | None = None

        # 数据状态
        self._available_suppliers: list[dict[str, Any]] = []
        self._selected_suppliers: list[dict[str, Any]] = []
        self._comparison_data: dict[str, Any] = {}
        self._evaluation_results: dict[str, Any] = {}

        super().__init__(parent, **kwargs)

        # 初始化数据
        self._load_suppliers()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建供应商选择区域
        self._create_supplier_selector(main_frame)

        # 创建对比结果区域
        self._create_comparison_area(main_frame)

        # 创建操作按钮区域
        self._create_action_buttons(main_frame)

    def _create_supplier_selector(self, parent: tk.Widget) -> None:
        """创建供应商选择区域."""
        selector_frame = ttk.LabelFrame(parent, text="选择对比供应商", padding=10)
        selector_frame.pack(fill=tk.X, pady=(0, 10))

        # 供应商搜索和筛选
        search_frame = ttk.Frame(selector_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="搜索供应商:").pack(side=tk.LEFT, padx=(0, 5))

        self._search_entry = ttk.Entry(search_frame, width=30)
        self._search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._on_search_changed)

        # 供应商类型筛选
        ttk.Label(search_frame, text="类型:").pack(side=tk.LEFT, padx=(10, 5))
        self._type_filter = ttk.Combobox(
            search_frame,
            values=["全部"] + [stype.value for stype in SupplierType],
            state="readonly",
            width=12,
        )
        self._type_filter.set("全部")
        self._type_filter.pack(side=tk.LEFT, padx=(0, 10))
        self._type_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 质量等级筛选
        ttk.Label(search_frame, text="质量等级:").pack(side=tk.LEFT, padx=(10, 5))
        self._quality_filter = ttk.Combobox(
            search_frame,
            values=["全部"] + [rating.value for rating in QualityRating],
            state="readonly",
            width=12,
        )
        self._quality_filter.set("全部")
        self._quality_filter.pack(side=tk.LEFT, padx=(0, 10))
        self._quality_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 供应商列表和选择区域
        list_frame = ttk.Frame(selector_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 可选供应商列表
        available_frame = ttk.LabelFrame(list_frame, text="可选供应商", padding=5)
        available_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self._available_listbox = tk.Listbox(
            available_frame, selectmode=tk.MULTIPLE, height=8
        )
        self._available_listbox.pack(fill=tk.BOTH, expand=True)

        # 选择按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side=tk.LEFT, padx=5)

        self._add_button = ttk.Button(
            button_frame, text="添加 →", command=self._add_suppliers
        )
        self._add_button.pack(pady=5)

        self._remove_button = ttk.Button(
            button_frame, text="← 移除", command=self._remove_suppliers
        )
        self._remove_button.pack(pady=5)

        self._clear_button = ttk.Button(
            button_frame, text="清空", command=self._clear_selection
        )
        self._clear_button.pack(pady=5)

        # 已选供应商列表
        selected_frame = ttk.LabelFrame(list_frame, text="对比供应商", padding=5)
        selected_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self._selected_listbox = tk.Listbox(
            selected_frame, selectmode=tk.MULTIPLE, height=8
        )
        self._selected_listbox.pack(fill=tk.BOTH, expand=True)

    def _create_comparison_area(self, parent: tk.Widget) -> None:
        """创建对比结果区域."""
        comparison_frame = ttk.LabelFrame(parent, text="对比分析", padding=10)
        comparison_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建标签页
        notebook = ttk.Notebook(comparison_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 对比表格标签页
        self._create_comparison_table_tab(notebook)

        # 图表分析标签页
        self._create_chart_analysis_tab(notebook)

        # 评估报告标签页
        self._create_evaluation_report_tab(notebook)

    def _create_comparison_table_tab(self, notebook: ttk.Notebook) -> None:
        """创建对比表格标签页."""
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="对比表格")

        # 定义对比表格列
        columns = [
            {"id": "metric", "text": "对比指标", "width": 120, "anchor": "w"},
            {"id": "supplier1", "text": "供应商1", "width": 100, "anchor": "center"},
            {"id": "supplier2", "text": "供应商2", "width": 100, "anchor": "center"},
            {"id": "supplier3", "text": "供应商3", "width": 100, "anchor": "center"},
            {"id": "supplier4", "text": "供应商4", "width": 100, "anchor": "center"},
            {"id": "best", "text": "最优", "width": 80, "anchor": "center"},
        ]

        self._comparison_table = DataTableTTK(
            table_frame,
            columns=columns,
            multi_select=False,
            show_pagination=False,
        )
        self._comparison_table.pack(fill=tk.BOTH, expand=True)

    def _create_chart_analysis_tab(self, notebook: ttk.Notebook) -> None:
        """创建图表分析标签页."""
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="图表分析")

        # 图表类型选择
        chart_control_frame = ttk.Frame(chart_frame)
        chart_control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(chart_control_frame, text="图表类型:").pack(side=tk.LEFT, padx=(0, 5))
        self._chart_type = ttk.Combobox(
            chart_control_frame,
            values=["雷达图", "柱状图", "折线图", "散点图"],
            state="readonly",
            width=12,
        )
        self._chart_type.set("雷达图")
        self._chart_type.pack(side=tk.LEFT, padx=(0, 10))
        self._chart_type.bind("<<ComboboxSelected>>", self._on_chart_type_changed)

        # 更新图表按钮
        self._update_chart_button = ttk.Button(
            chart_control_frame, text="更新图表", command=self._update_chart
        )
        self._update_chart_button.pack(side=tk.LEFT, padx=(10, 0))

        # 图表组件
        self._chart_widget = ChartContainerTTK(chart_frame)
        self._chart_widget.pack(fill=tk.BOTH, expand=True)

    def _create_evaluation_report_tab(self, notebook: ttk.Notebook) -> None:
        """创建评估报告标签页."""
        report_frame = ttk.Frame(notebook)
        notebook.add(report_frame, text="评估报告")

        # 报告控制区域
        control_frame = ttk.Frame(report_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self._generate_report_button = ttk.Button(
            control_frame, text="生成评估报告", command=self._generate_evaluation_report
        )
        self._generate_report_button.pack(side=tk.LEFT, padx=(0, 10))

        self._export_report_button = ttk.Button(
            control_frame, text="导出报告", command=self._export_evaluation_report
        )
        self._export_report_button.pack(side=tk.LEFT)

        # 报告内容显示区域
        report_text_frame = ttk.Frame(report_frame)
        report_text_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文本框和滚动条
        self._report_text = tk.Text(
            report_text_frame, wrap=tk.WORD, font=("Microsoft YaHei UI", 10)
        )

        scrollbar = ttk.Scrollbar(report_text_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._report_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._report_text.yview)

    def _create_action_buttons(self, parent: tk.Widget) -> None:
        """创建操作按钮区域."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # 左侧按钮
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        self._compare_button = ttk.Button(
            left_buttons, text="🔍 开始对比", command=self._start_comparison
        )
        self._compare_button.pack(side=tk.LEFT, padx=(0, 10))

        self._reset_button = ttk.Button(
            left_buttons, text="🔄 重置", command=self._reset_comparison
        )
        self._reset_button.pack(side=tk.LEFT, padx=(0, 10))

        # 右侧按钮
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        self._export_button = ttk.Button(
            right_buttons, text="📥 导出对比", command=self._export_comparison
        )
        self._export_button.pack(side=tk.RIGHT, padx=(10, 0))

        self._save_template_button = ttk.Button(
            right_buttons, text="💾 保存模板", command=self._save_comparison_template
        )
        self._save_template_button.pack(side=tk.RIGHT, padx=(10, 0))

    def _bind_events(self) -> None:
        """绑定事件处理."""
        # 双击添加供应商
        self._available_listbox.bind(
            "<Double-Button-1>", self._on_available_double_click
        )
        # 双击移除供应商
        self._selected_listbox.bind("<Double-Button-1>", self._on_selected_double_click)

    # ==================== 数据加载方法 ====================

    def _load_suppliers(self) -> None:
        """加载可用供应商列表."""
        try:
            # 获取所有供应商
            suppliers, _ = self._supplier_service.search_suppliers(
                query="", filters={}, page=1, page_size=1000
            )

            self._available_suppliers = suppliers
            self._update_available_listbox()

            self._logger.info(f"成功加载 {len(suppliers)} 个供应商")

        except ServiceError as e:
            self._logger.exception(f"加载供应商数据失败: {e}")
            messagebox.showerror("错误", f"加载供应商数据失败:{e}")
        except Exception as e:
            self._logger.exception(f"加载供应商数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载供应商数据时发生未知错误:{e}")

    def _update_available_listbox(self) -> None:
        """更新可选供应商列表框."""
        if not self._available_listbox:
            return

        # 清空列表
        self._available_listbox.delete(0, tk.END)

        # 获取筛选条件
        search_query = self._search_entry.get().lower() if self._search_entry else ""
        type_filter = self._type_filter.get() if self._type_filter else "全部"
        quality_filter = self._quality_filter.get() if self._quality_filter else "全部"

        # 筛选供应商
        filtered_suppliers = []
        for supplier in self._available_suppliers:
            # 搜索筛选
            if search_query and search_query not in supplier.get("name", "").lower():
                continue

            # 类型筛选
            if type_filter != "全部" and supplier.get("supplier_type") != type_filter:
                continue

            # 质量等级筛选
            if (
                quality_filter != "全部"
                and supplier.get("quality_rating") != quality_filter
            ):
                continue

            # 排除已选择的供应商
            if not any(
                s.get("id") == supplier.get("id") for s in self._selected_suppliers
            ):
                filtered_suppliers.append(supplier)

        # 添加到列表框
        for supplier in filtered_suppliers:
            display_text = (
                f"{supplier.get('name', '')} - {supplier.get('company_name', '')}"
            )
            self._available_listbox.insert(tk.END, display_text)

        # 保存筛选后的供应商数据
        self._filtered_suppliers = filtered_suppliers

    def _update_selected_listbox(self) -> None:
        """更新已选供应商列表框."""
        if not self._selected_listbox:
            return

        # 清空列表
        self._selected_listbox.delete(0, tk.END)

        # 添加已选供应商
        for supplier in self._selected_suppliers:
            display_text = (
                f"{supplier.get('name', '')} - {supplier.get('company_name', '')}"
            )
            self._selected_listbox.insert(tk.END, display_text)

    # ==================== 事件处理方法 ====================

    def _on_search_changed(self, event) -> None:
        """处理搜索输入变化."""
        self._update_available_listbox()

    def _on_filter_changed(self, event) -> None:
        """处理筛选变化."""
        self._update_available_listbox()

    def _on_available_double_click(self, event) -> None:
        """处理可选列表双击."""
        self._add_suppliers()

    def _on_selected_double_click(self, event) -> None:
        """处理已选列表双击."""
        self._remove_suppliers()

    def _add_suppliers(self) -> None:
        """添加选中的供应商到对比列表."""
        if not hasattr(self, "_filtered_suppliers"):
            return

        selected_indices = self._available_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("提示", "请先选择要添加的供应商")
            return

        # 检查对比供应商数量限制
        if len(self._selected_suppliers) + len(selected_indices) > 4:
            messagebox.showwarning("提示", "最多只能对比4个供应商")
            return

        # 添加选中的供应商
        for index in selected_indices:
            if index < len(self._filtered_suppliers):
                supplier = self._filtered_suppliers[index]
                if not any(
                    s.get("id") == supplier.get("id") for s in self._selected_suppliers
                ):
                    self._selected_suppliers.append(supplier)

        # 更新列表显示
        self._update_available_listbox()
        self._update_selected_listbox()

        self._logger.info(f"添加了 {len(selected_indices)} 个供应商到对比列表")

    def _remove_suppliers(self) -> None:
        """从对比列表移除选中的供应商."""
        selected_indices = self._selected_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("提示", "请先选择要移除的供应商")
            return

        # 从后往前删除,避免索引变化
        for index in reversed(selected_indices):
            if index < len(self._selected_suppliers):
                removed_supplier = self._selected_suppliers.pop(index)
                self._logger.info(
                    f"从对比列表移除供应商: {removed_supplier.get('name')}"
                )

        # 更新列表显示
        self._update_available_listbox()
        self._update_selected_listbox()

    def _clear_selection(self) -> None:
        """清空已选供应商."""
        self._selected_suppliers.clear()
        self._update_available_listbox()
        self._update_selected_listbox()
        self._logger.info("清空了对比供应商列表")

    def _on_chart_type_changed(self, event) -> None:
        """处理图表类型变化."""
        if self._comparison_data:
            self._update_chart()

    # ==================== 对比分析方法 ====================

    def _start_comparison(self) -> None:
        """开始供应商对比分析."""
        if len(self._selected_suppliers) < 2:
            messagebox.showwarning("提示", "请至少选择2个供应商进行对比")
            return

        try:
            # 获取供应商详细评估数据
            comparison_data = {}
            for supplier in self._selected_suppliers:
                supplier_id = supplier.get("id")
                if supplier_id:
                    # 获取供应商质量评估
                    evaluation = self._supplier_service.evaluate_supplier_quality(
                        supplier_id
                    )
                    # 获取供应商绩效指标
                    performance = (
                        self._supplier_service.get_supplier_performance_metrics(
                            supplier_id
                        )
                    )

                    comparison_data[supplier_id] = {
                        "basic_info": supplier,
                        "evaluation": evaluation,
                        "performance": performance,
                    }

            self._comparison_data = comparison_data

            # 更新对比表格
            self._update_comparison_table()

            # 更新图表
            self._update_chart()

            messagebox.showinfo("成功", "供应商对比分析完成!")
            self._logger.info(
                f"完成 {len(self._selected_suppliers)} 个供应商的对比分析"
            )

        except ServiceError as e:
            self._logger.exception(f"供应商对比分析失败: {e}")
            messagebox.showerror("错误", f"供应商对比分析失败:{e}")
        except Exception as e:
            self._logger.exception(f"对比分析时发生未知错误: {e}")
            messagebox.showerror("错误", f"对比分析时发生未知错误:{e}")

    def _update_comparison_table(self) -> None:
        """更新对比表格数据."""
        if not self._comparison_table or not self._comparison_data:
            return

        # 构建对比数据
        table_data = []

        # 定义对比指标
        metrics = [
            ("供应商名称", "name"),
            ("公司名称", "company_name"),
            ("供应商等级", "supplier_level"),
            ("质量评分", "quality_score"),
            ("交期评分", "delivery_rating"),
            ("服务评分", "service_rating"),
            ("综合评分", "overall_rating"),
            ("合作年限", "cooperation_years"),
            ("总订单数", "total_orders"),
            ("总交易额", "total_amount"),
            ("质量问题数", "quality_issues"),
            ("按时交付率", "on_time_delivery_rate"),
            ("客户满意度", "customer_satisfaction"),
        ]

        # 构建表格数据
        for metric_name, metric_key in metrics:
            row_data = {"metric": metric_name}

            # 收集各供应商的指标值
            values = []
            for i, (supplier_id, data) in enumerate(self._comparison_data.items()):
                supplier_name = f"supplier{i + 1}"
                value = self._get_metric_value(data, metric_key)
                row_data[supplier_name] = value
                values.append((value, supplier_name))

            # 确定最优值
            if metric_key in [
                "quality_score",
                "delivery_rating",
                "service_rating",
                "overall_rating",
                "on_time_delivery_rate",
                "customer_satisfaction",
                "total_orders",
                "total_amount",
                "cooperation_years",
            ]:
                # 数值越大越好
                best_value, best_supplier = max(
                    values, key=lambda x: self._safe_float(x[0])
                )
                row_data["best"] = best_supplier
            elif metric_key in ["quality_issues"]:
                # 数值越小越好
                best_value, best_supplier = min(
                    values, key=lambda x: self._safe_float(x[0])
                )
                row_data["best"] = best_supplier
            else:
                # 非数值指标
                row_data["best"] = "-"

            table_data.append(row_data)

        # 更新表格列标题
        supplier_names = [
            data["basic_info"].get("name", f"供应商{i + 1}")
            for i, data in enumerate(self._comparison_data.values())
        ]

        # 动态更新列标题
        columns = [
            {"id": "metric", "text": "对比指标", "width": 120, "anchor": "w"},
        ]

        for i, name in enumerate(supplier_names):
            columns.append(
                {
                    "id": f"supplier{i + 1}",
                    "text": name[:10] + "..." if len(name) > 10 else name,
                    "width": 100,
                    "anchor": "center",
                }
            )

        columns.append({"id": "best", "text": "最优", "width": 80, "anchor": "center"})

        # 重新配置表格列 - 使用正确的API
        # self._comparison_table.configure_columns(columns)  # 此方法不存在,需要重新实现表格

        # 加载数据
        self._comparison_table.load_data(table_data)

    def _get_metric_value(self, supplier_data: dict[str, Any], metric_key: str) -> str:
        """获取供应商指标值."""
        basic_info = supplier_data.get("basic_info", {})
        evaluation = supplier_data.get("evaluation", {})
        performance = supplier_data.get("performance", {})

        # 基本信息指标
        if metric_key in basic_info:
            value = basic_info[metric_key]
            if isinstance(value, (int, float)):
                return f"{value:.2f}" if isinstance(value, float) else str(value)
            return str(value) if value else "-"

        # 评估指标
        if metric_key in evaluation:
            value = evaluation[metric_key]
            if isinstance(value, (int, float)):
                return f"{value:.2f}" if isinstance(value, float) else str(value)
            return str(value) if value else "-"

        # 绩效指标
        if metric_key in performance:
            value = performance[metric_key]
            if isinstance(value, (int, float)):
                return f"{value:.2f}" if isinstance(value, float) else str(value)
            return str(value) if value else "-"

        return "-"

    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数."""
        try:
            if isinstance(value, str):
                # 移除非数字字符
                clean_value = "".join(c for c in value if c.isdigit() or c in ".-")
                return float(clean_value) if clean_value else 0.0
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _update_chart(self) -> None:
        """更新对比图表."""
        if not self._chart_widget or not self._comparison_data:
            return

        chart_type = self._chart_type.get()

        try:
            if chart_type == "雷达图":
                self._create_radar_chart()
            elif chart_type == "柱状图":
                self._create_bar_chart()
            elif chart_type == "折线图":
                self._create_line_chart()
            elif chart_type == "散点图":
                self._create_scatter_chart()

        except Exception as e:
            self._logger.exception(f"更新图表失败: {e}")
            messagebox.showerror("错误", f"更新图表失败:{e}")

    def _create_radar_chart(self) -> None:
        """创建雷达图."""
        import matplotlib.pyplot as plt
        import numpy as np

        # 准备数据
        metrics = ["质量评分", "交期评分", "服务评分", "价格竞争力", "创新能力"]
        supplier_names = []
        supplier_scores = []

        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_names.append(basic_info.get("name", "未知供应商"))

            scores = [
                evaluation.get("quality_score", 0),
                evaluation.get("delivery_score", 0),
                evaluation.get("service_score", 0),
                evaluation.get("price_competitiveness", 70),  # 默认值
                evaluation.get("innovation_capability", 60),  # 默认值
            ]
            supplier_scores.append(scores)

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection="polar"))

        # 设置角度
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # 闭合图形

        # 绘制每个供应商的数据
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        for i, (name, scores) in enumerate(zip(supplier_names, supplier_scores)):
            scores += scores[:1]  # 闭合数据
            ax.plot(angles, scores, "o-", linewidth=2, label=name, color=colors[i % 4])
            ax.fill(angles, scores, alpha=0.25, color=colors[i % 4])

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 100)
        ax.set_title("供应商综合能力雷达图", size=16, fontweight="bold", pad=20)
        ax.legend(loc="upper right", bbox_to_anchor=(1.2, 1.0))

        # 显示图表
        # 将matplotlib图表转换为ChartData格式
        # 这里需要根据实际的ChartContainerTTK API进行调整
        # 暂时使用简化的方式
        plt.show()

    def _create_bar_chart(self) -> None:
        """创建柱状图."""
        import matplotlib.pyplot as plt
        import numpy as np

        # 准备数据
        supplier_names = []
        quality_scores = []
        delivery_scores = []
        service_scores = []

        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_names.append(basic_info.get("name", "未知供应商"))
            quality_scores.append(evaluation.get("quality_score", 0))
            delivery_scores.append(evaluation.get("delivery_score", 0))
            service_scores.append(evaluation.get("service_score", 0))

        # 创建柱状图
        fig, ax = plt.subplots(figsize=(12, 8))

        x = np.arange(len(supplier_names))
        width = 0.25

        bars1 = ax.bar(
            x - width, quality_scores, width, label="质量评分", color="#FF6B6B"
        )
        bars2 = ax.bar(x, delivery_scores, width, label="交期评分", color="#4ECDC4")
        bars3 = ax.bar(
            x + width, service_scores, width, label="服务评分", color="#45B7D1"
        )

        # 设置标签和标题
        ax.set_xlabel("供应商")
        ax.set_ylabel("评分")
        ax.set_title("供应商各项评分对比")
        ax.set_xticks(x)
        ax.set_xticklabels(supplier_names)
        ax.legend()

        # 添加数值标签
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.1f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                )

        plt.tight_layout()
        plt.show()

    def _create_line_chart(self) -> None:
        """创建折线图."""
        import matplotlib.pyplot as plt

        # 准备数据
        metrics = ["质量", "交期", "服务", "价格", "创新"]
        fig, ax = plt.subplots(figsize=(12, 8))

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        for i, (supplier_id, data) in enumerate(self._comparison_data.items()):
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_name = basic_info.get("name", "未知供应商")
            scores = [
                evaluation.get("quality_score", 0),
                evaluation.get("delivery_score", 0),
                evaluation.get("service_score", 0),
                evaluation.get("price_competitiveness", 70),
                evaluation.get("innovation_capability", 60),
            ]

            ax.plot(
                metrics,
                scores,
                marker="o",
                linewidth=2,
                label=supplier_name,
                color=colors[i % 4],
            )

        ax.set_xlabel("评估维度")
        ax.set_ylabel("评分")
        ax.set_title("供应商各维度评分趋势")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)

        plt.tight_layout()
        plt.show()

    def _create_scatter_chart(self) -> None:
        """创建散点图."""
        import matplotlib.pyplot as plt

        # 准备数据
        fig, ax = plt.subplots(figsize=(10, 8))

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
        for i, (supplier_id, data) in enumerate(self._comparison_data.items()):
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_name = basic_info.get("name", "未知供应商")
            quality_score = evaluation.get("quality_score", 0)
            price_score = evaluation.get("price_competitiveness", 70)

            ax.scatter(
                quality_score,
                price_score,
                s=200,
                alpha=0.7,
                color=colors[i % 4],
                label=supplier_name,
            )

            # 添加供应商名称标签
            ax.annotate(
                supplier_name,
                (quality_score, price_score),
                xytext=(5, 5),
                textcoords="offset points",
            )

        ax.set_xlabel("质量评分")
        ax.set_ylabel("价格竞争力")
        ax.set_title("供应商质量-价格散点图")
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)

        plt.tight_layout()
        plt.show()

    # ==================== 评估报告方法 ====================

    def _generate_evaluation_report(self) -> None:
        """生成供应商评估报告."""
        if not self._comparison_data:
            messagebox.showwarning("提示", "请先进行供应商对比分析")
            return

        try:
            # 生成报告内容
            report_content = self._build_evaluation_report()

            # 显示报告
            self._report_text.delete("1.0", tk.END)
            self._report_text.insert("1.0", report_content)

            # 保存评估结果
            from datetime import datetime

            self._evaluation_results = {
                "report_content": report_content,
                "comparison_data": self._comparison_data,
                "generated_at": datetime.now().isoformat(),
            }

            messagebox.showinfo("成功", "评估报告生成完成!")
            self._logger.info("成功生成供应商评估报告")

        except Exception as e:
            self._logger.exception(f"生成评估报告失败: {e}")
            messagebox.showerror("错误", f"生成评估报告失败:{e}")

    def _build_evaluation_report(self) -> str:
        """构建评估报告内容."""
        from datetime import datetime

        report_lines = []

        # 报告标题
        report_lines.append("=" * 60)
        report_lines.append("供应商对比评估报告")
        report_lines.append("=" * 60)
        report_lines.append(f"生成时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"对比供应商数量:{len(self._comparison_data)}")
        report_lines.append("")

        # 执行摘要
        report_lines.append("一、执行摘要")
        report_lines.append("-" * 30)
        best_supplier = self._find_best_supplier()
        if best_supplier:
            report_lines.append(f"推荐供应商:{best_supplier['name']}")
            report_lines.append(f"综合评分:{best_supplier['overall_score']:.2f}")
            report_lines.append(f"推荐理由:{best_supplier['reason']}")
        report_lines.append("")

        # 供应商详细分析
        report_lines.append("二、供应商详细分析")
        report_lines.append("-" * 30)

        for i, (supplier_id, data) in enumerate(self._comparison_data.items(), 1):
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            report_lines.append(f"{i}. {basic_info.get('name', '未知供应商')}")
            report_lines.append(f"   公司名称:{basic_info.get('company_name', '-')}")
            report_lines.append(
                f"   供应商等级:{basic_info.get('supplier_level', '-')}"
            )
            report_lines.append(
                f"   质量评分:{evaluation.get('quality_score', 0):.2f}"
            )
            report_lines.append(
                f"   交期评分:{evaluation.get('delivery_score', 0):.2f}"
            )
            report_lines.append(
                f"   服务评分:{evaluation.get('service_score', 0):.2f}"
            )
            report_lines.append(
                f"   合作年限:{basic_info.get('cooperation_years', 0)} 年"
            )
            report_lines.append("")

        # 对比分析结果
        report_lines.append("三、对比分析结果")
        report_lines.append("-" * 30)

        # 各维度最优供应商
        dimensions = [
            ("质量评分", "quality_score"),
            ("交期评分", "delivery_score"),
            ("服务评分", "service_score"),
        ]

        for dim_name, dim_key in dimensions:
            best_in_dim = self._find_best_in_dimension(dim_key)
            if best_in_dim:
                report_lines.append(
                    f"{dim_name}最优:{best_in_dim['name']} ({best_in_dim['score']:.2f})"
                )

        report_lines.append("")

        # 风险评估
        report_lines.append("四、风险评估")
        report_lines.append("-" * 30)
        risks = self._assess_risks()
        for risk in risks:
            report_lines.append(f"• {risk}")
        report_lines.append("")

        # 建议和结论
        report_lines.append("五、建议和结论")
        report_lines.append("-" * 30)
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report_lines.append(f"• {rec}")

        return "\n".join(report_lines)

    def _find_best_supplier(self) -> dict[str, Any] | None:
        """找出最佳供应商."""
        if not self._comparison_data:
            return None

        best_supplier = None
        best_score = -1

        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            # 计算综合评分
            quality_score = evaluation.get("quality_score", 0)
            delivery_score = evaluation.get("delivery_score", 0)
            service_score = evaluation.get("service_score", 0)

            overall_score = (
                quality_score * 0.4 + delivery_score * 0.3 + service_score * 0.3
            )

            if overall_score > best_score:
                best_score = overall_score
                best_supplier = {
                    "id": supplier_id,
                    "name": basic_info.get("name", "未知供应商"),
                    "overall_score": overall_score,
                    "reason": "在质量、交期、服务三个维度表现均衡,综合评分最高",
                }

        return best_supplier

    def _find_best_in_dimension(self, dimension_key: str) -> dict[str, Any] | None:
        """找出某个维度的最佳供应商."""
        if not self._comparison_data:
            return None

        best_supplier = None
        best_score = -1

        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            score = evaluation.get(dimension_key, 0)
            if score > best_score:
                best_score = score
                best_supplier = {
                    "id": supplier_id,
                    "name": basic_info.get("name", "未知供应商"),
                    "score": score,
                }

        return best_supplier

    def _assess_risks(self) -> list[str]:
        """评估风险."""
        risks = []

        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_name = basic_info.get("name", "未知供应商")

            # 质量风险
            if evaluation.get("quality_score", 0) < 60:
                risks.append(f"{supplier_name}:质量评分较低,存在质量风险")

            # 交期风险
            if evaluation.get("delivery_score", 0) < 70:
                risks.append(f"{supplier_name}:交期评分较低,可能影响供货及时性")

            # 合作风险
            if basic_info.get("cooperation_years", 0) < 1:
                risks.append(f"{supplier_name}:合作时间较短,缺乏长期合作经验")

        if not risks:
            risks.append("暂未发现明显风险")

        return risks

    def _generate_recommendations(self) -> list[str]:
        """生成建议."""
        recommendations = []

        best_supplier = self._find_best_supplier()
        if best_supplier:
            recommendations.append(
                f"建议优先选择 {best_supplier['name']} 作为主要供应商"
            )

        # 多元化建议
        if len(self._comparison_data) > 1:
            recommendations.append("建议采用多供应商策略,降低供应风险")

        # 改进建议
        for supplier_id, data in self._comparison_data.items():
            basic_info = data["basic_info"]
            evaluation = data["evaluation"]

            supplier_name = basic_info.get("name", "未知供应商")

            if evaluation.get("quality_score", 0) < 80:
                recommendations.append(f"建议与 {supplier_name} 协商质量改进计划")

        recommendations.append("定期重新评估供应商表现,动态调整合作策略")

        return recommendations

    # ==================== 导出功能方法 ====================

    def _export_comparison(self) -> None:
        """导出对比结果."""
        if not self._comparison_data:
            messagebox.showwarning("提示", "没有可导出的对比数据")
            return

        # 选择导出格式
        export_format = messagebox.askyesno(
            "选择导出格式", "是否导出为Excel格式?\n\n是:Excel格式\n否:CSV格式"
        )

        try:
            if export_format:
                self._export_to_excel()
            else:
                self._export_to_csv()

        except Exception as e:
            self._logger.exception(f"导出对比结果失败: {e}")
            messagebox.showerror("错误", f"导出对比结果失败:{e}")

    def _export_to_excel(self) -> None:
        """导出为Excel格式."""
        from datetime import datetime

        # 选择保存路径
        filename = filedialog.asksaveasfilename(
            title="保存对比结果",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialfile=f"供应商对比_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        )

        if not filename:
            return

        # TODO: 实现Excel导出功能
        # 这里需要使用openpyxl或pandas库
        messagebox.showinfo(
            "提示", f"Excel导出功能将在后续版本中实现\n保存路径:{filename}"
        )

    def _export_to_csv(self) -> None:
        """导出为CSV格式."""
        import csv
        from datetime import datetime

        # 选择保存路径
        filename = filedialog.asksaveasfilename(
            title="保存对比结果",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")],
            initialfile=f"供应商对比_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )

        if not filename:
            return

        # 导出CSV
        with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
            writer = csv.writer(csvfile)

            # 写入标题行
            headers = ["对比指标"]
            supplier_names = [
                data["basic_info"].get("name", f"供应商{i + 1}")
                for i, data in enumerate(self._comparison_data.values())
            ]
            headers.extend(supplier_names)
            writer.writerow(headers)

            # 写入数据行
            metrics = [
                ("供应商名称", "name"),
                ("公司名称", "company_name"),
                ("质量评分", "quality_score"),
                ("交期评分", "delivery_rating"),
                ("服务评分", "service_rating"),
                ("合作年限", "cooperation_years"),
            ]

            for metric_name, metric_key in metrics:
                row = [metric_name]
                for supplier_id, data in self._comparison_data.items():
                    value = self._get_metric_value(data, metric_key)
                    row.append(value)
                writer.writerow(row)

        messagebox.showinfo("成功", f"对比结果已导出到:\n{filename}")

    def _export_evaluation_report(self) -> None:
        """导出评估报告."""
        if not self._evaluation_results:
            messagebox.showwarning("提示", "请先生成评估报告")
            return

        from datetime import datetime

        # 选择保存路径
        filename = filedialog.asksaveasfilename(
            title="保存评估报告",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"供应商评估报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )

        if not filename:
            return

        try:
            # 保存报告
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self._evaluation_results["report_content"])

            messagebox.showinfo("成功", f"评估报告已导出到:\n{filename}")

        except Exception as e:
            self._logger.exception(f"导出评估报告失败: {e}")
            messagebox.showerror("错误", f"导出评估报告失败:{e}")

    def _save_comparison_template(self) -> None:
        """保存对比模板."""
        if not self._selected_suppliers:
            messagebox.showwarning("提示", "请先选择对比供应商")
            return

        # TODO: 实现保存对比模板功能
        messagebox.showinfo("提示", "保存对比模板功能将在后续版本中实现")

    def _reset_comparison(self) -> None:
        """重置对比分析."""
        # 确认重置
        result = messagebox.askyesno("确认重置", "确定要重置所有对比数据吗?")
        if not result:
            return

        # 清空数据
        self._selected_suppliers.clear()
        self._comparison_data.clear()
        self._evaluation_results.clear()

        # 更新UI
        self._update_available_listbox()
        self._update_selected_listbox()

        if self._comparison_table:
            self._comparison_table.load_data([])

        if self._chart_widget:
            self._chart_widget.clear()

        if self._report_text:
            self._report_text.delete("1.0", tk.END)

        messagebox.showinfo("成功", "对比数据已重置")

    # ==================== 公共接口方法 ====================

    def load_suppliers_for_comparison(self, supplier_ids: list[int]) -> None:
        """加载指定供应商进行对比(公共接口)."""
        try:
            # 清空当前选择
            self._selected_suppliers.clear()

            # 加载指定供应商
            for supplier_id in supplier_ids:
                # 从可用供应商中查找
                supplier = next(
                    (
                        s
                        for s in self._available_suppliers
                        if s.get("id") == supplier_id
                    ),
                    None,
                )
                if supplier:
                    self._selected_suppliers.append(supplier)

            # 更新UI
            self._update_available_listbox()
            self._update_selected_listbox()

            self._logger.info(
                f"加载了 {len(self._selected_suppliers)} 个供应商进行对比"
            )

        except Exception as e:
            self._logger.exception(f"加载对比供应商失败: {e}")
            messagebox.showerror("错误", f"加载对比供应商失败:{e}")

    def get_comparison_results(self) -> dict[str, Any]:
        """获取对比结果(公共接口)."""
        return {
            "selected_suppliers": self._selected_suppliers,
            "comparison_data": self._comparison_data,
            "evaluation_results": self._evaluation_results,
        }

    def cleanup(self) -> None:
        """清理资源."""
        # 清理图表组件
        if self._chart_widget:
            self._chart_widget.cleanup()

        super().cleanup()
