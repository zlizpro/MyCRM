"""MiniCRM 客户详情TTK组件

实现客户详细信息的显示和管理功能,包括:
- 客户基本信息展示
- 标签页导航(基本信息、互动记录、财务信息)
- 客户统计数据显示
- 快速操作按钮
- 数据实时更新

设计原则:
- 继承BaseWidget提供标准组件功能
- 使用TTK Notebook实现标签页导航
- 集成FormBuilderTTK显示表单数据
- 连接CustomerService获取业务数据
- 支持数据绑定和实时更新
"""

from datetime import datetime
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, Optional

from minicrm.core.exceptions import ServiceError
from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.services.customer.customer_service_facade import CustomerServiceFacade
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK
from minicrm.ui.ttk_base.form_builder import FormBuilderTTK


class CustomerDetailTTK(BaseWidget):
    """客户详情TTK组件

    提供完整的客户详情视图,包括:
    - 标签页导航
    - 基本信息显示
    - 互动记录列表
    - 财务统计信息
    - 快速操作功能
    """

    def __init__(
        self,
        parent: tk.Widget,
        customer_service: CustomerServiceFacade,
        on_edit_callback: Optional[Callable[[int], None]] = None,
        **kwargs,
    ):
        """初始化客户详情组件

        Args:
            parent: 父组件
            customer_service: 客户服务实例
            on_edit_callback: 编辑回调函数
            **kwargs: 其他参数
        """
        self._customer_service = customer_service
        self._on_edit_callback = on_edit_callback
        self._logger = logging.getLogger(__name__)

        # 当前显示的客户数据
        self._current_customer: Optional[Dict[str, Any]] = None
        self._customer_id: Optional[int] = None

        # UI组件引用
        self._notebook: Optional[ttk.Notebook] = None
        self._basic_info_form: Optional[FormBuilderTTK] = None
        self._interaction_table: Optional[DataTableTTK] = None
        self._finance_info_form: Optional[FormBuilderTTK] = None

        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题区域
        self._create_header_area(main_frame)

        # 创建标签页
        self._create_notebook(main_frame)

        # 创建操作按钮区域
        self._create_action_area(main_frame)

    def _create_header_area(self, parent: tk.Widget) -> None:
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # 客户名称标签
        self._customer_name_label = ttk.Label(
            header_frame, text="客户详情", font=("Microsoft YaHei UI", 14, "bold")
        )
        self._customer_name_label.pack(side=tk.LEFT)

        # 客户等级标签
        self._customer_level_label = ttk.Label(
            header_frame, text="", font=("Microsoft YaHei UI", 10)
        )
        self._customer_level_label.pack(side=tk.LEFT, padx=(10, 0))

    def _create_notebook(self, parent: tk.Widget) -> None:
        """创建标签页"""
        self._notebook = ttk.Notebook(parent)
        self._notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 基本信息标签页
        self._create_basic_info_tab()

        # 互动记录标签页
        self._create_interaction_tab()

        # 财务信息标签页
        self._create_finance_tab()

    def _create_basic_info_tab(self) -> None:
        """创建基本信息标签页"""
        basic_frame = ttk.Frame(self._notebook)
        self._notebook.add(basic_frame, text="基本信息")

        # 创建滚动区域
        canvas = tk.Canvas(basic_frame)
        scrollbar = ttk.Scrollbar(basic_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 定义基本信息表单字段
        basic_info_fields = [
            {"id": "name", "label": "客户姓名", "type": "entry", "readonly": True},
            {"id": "phone", "label": "联系电话", "type": "entry", "readonly": True},
            {"id": "email", "label": "邮箱地址", "type": "entry", "readonly": True},
            {
                "id": "company_name",
                "label": "公司名称",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "customer_level",
                "label": "客户等级",
                "type": "combobox",
                "options": [level.value for level in CustomerLevel],
                "readonly": True,
            },
            {
                "id": "customer_type",
                "label": "客户类型",
                "type": "combobox",
                "options": [ctype.value for ctype in CustomerType],
                "readonly": True,
            },
            {
                "id": "industry_type",
                "label": "行业类型",
                "type": "combobox",
                "options": [industry.value for industry in IndustryType],
                "readonly": True,
            },
            {
                "id": "credit_limit",
                "label": "授信额度",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "payment_terms",
                "label": "付款期限(天)",
                "type": "entry",
                "readonly": True,
            },
            {"id": "address", "label": "联系地址", "type": "text", "readonly": True},
            {"id": "notes", "label": "备注信息", "type": "text", "readonly": True},
        ]

        # 创建表单
        self._basic_info_form = FormBuilderTTK(scrollable_frame, basic_info_fields)
        self._basic_info_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_interaction_tab(self) -> None:
        """创建互动记录标签页"""
        interaction_frame = ttk.Frame(self._notebook)
        self._notebook.add(interaction_frame, text="互动记录")

        # 定义互动记录表格列
        interaction_columns = [
            {"id": "date", "text": "日期", "width": 120},
            {"id": "type", "text": "类型", "width": 100},
            {"id": "content", "text": "内容", "width": 300},
            {"id": "result", "text": "结果", "width": 150},
            {"id": "next_action", "text": "下次行动", "width": 200},
        ]

        # 创建互动记录表格
        self._interaction_table = DataTableTTK(interaction_frame, interaction_columns)
        self._interaction_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_finance_tab(self) -> None:
        """创建财务信息标签页"""
        finance_frame = ttk.Frame(self._notebook)
        self._notebook.add(finance_frame, text="财务信息")

        # 定义财务信息表单字段
        finance_fields = [
            {
                "id": "total_orders",
                "label": "总订单数",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "total_amount",
                "label": "总交易金额",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "last_order_date",
                "label": "最后订单日期",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "value_score",
                "label": "客户价值评分",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "loyalty_score",
                "label": "忠诚度评分",
                "type": "entry",
                "readonly": True,
            },
            {
                "id": "cooperation_months",
                "label": "合作月数",
                "type": "entry",
                "readonly": True,
            },
        ]

        # 创建财务信息表单
        self._finance_info_form = FormBuilderTTK(finance_frame, finance_fields)
        self._finance_info_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_action_area(self, parent: tk.Widget) -> None:
        """创建操作按钮区域"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X)

        # 编辑按钮
        self._edit_button = ttk.Button(
            action_frame, text="编辑客户", command=self._on_edit_customer
        )
        self._edit_button.pack(side=tk.LEFT, padx=(0, 10))

        # 刷新按钮
        self._refresh_button = ttk.Button(
            action_frame, text="刷新数据", command=self._refresh_data
        )
        self._refresh_button.pack(side=tk.LEFT, padx=(0, 10))

        # 计算价值评分按钮
        self._calculate_value_button = ttk.Button(
            action_frame, text="计算价值评分", command=self._calculate_value_score
        )
        self._calculate_value_button.pack(side=tk.LEFT)

    def _bind_events(self) -> None:
        """绑定事件处理"""
        # 标签页切换事件
        if self._notebook:
            self._notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def load_customer(self, customer_id: int) -> None:
        """加载客户数据

        Args:
            customer_id: 客户ID
        """
        try:
            self._customer_id = customer_id

            # 获取客户数据
            customer_data = self._customer_service.get_customer_by_id(customer_id)
            if not customer_data:
                messagebox.showerror("错误", f"未找到客户ID: {customer_id}")
                return

            self._current_customer = customer_data

            # 更新UI显示
            self._update_header_display()
            self._update_basic_info_display()
            self._update_finance_info_display()
            self._load_interaction_records()

            self._logger.info(f"成功加载客户数据: {customer_id}")

        except ServiceError as e:
            self._logger.error(f"加载客户数据失败: {e}")
            messagebox.showerror("错误", f"加载客户数据失败: {e}")
        except Exception as e:
            self._logger.exception(f"加载客户数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载客户数据时发生未知错误: {e}")

    def _update_header_display(self) -> None:
        """更新标题显示"""
        if not self._current_customer:
            return

        # 更新客户名称
        customer_name = self._current_customer.get("name", "未知客户")
        company_name = self._current_customer.get("company_name", "")

        if company_name and company_name != customer_name:
            display_name = f"{customer_name} ({company_name})"
        else:
            display_name = customer_name

        self._customer_name_label.config(text=display_name)

        # 更新客户等级
        customer_level = self._current_customer.get("customer_level", "normal")
        level_text = f"等级: {customer_level}"
        self._customer_level_label.config(text=level_text)

    def _update_basic_info_display(self) -> None:
        """更新基本信息显示"""
        if not self._current_customer or not self._basic_info_form:
            return

        # 准备显示数据
        display_data = {
            "name": self._current_customer.get("name", ""),
            "phone": self._current_customer.get("formatted_phone", ""),
            "email": self._current_customer.get("email", ""),
            "company_name": self._current_customer.get("company_name", ""),
            "customer_level": self._current_customer.get("customer_level", ""),
            "customer_type": self._current_customer.get("customer_type", ""),
            "industry_type": self._current_customer.get("industry_type", ""),
            "credit_limit": self._current_customer.get("formatted_credit_limit", ""),
            "payment_terms": str(self._current_customer.get("payment_terms", 0)),
            "address": self._current_customer.get("address", ""),
            "notes": self._current_customer.get("notes", ""),
        }

        # 更新表单数据
        self._basic_info_form.set_form_data(display_data)

    def _update_finance_info_display(self) -> None:
        """更新财务信息显示"""
        if not self._current_customer or not self._finance_info_form:
            return

        # 准备财务数据
        finance_data = {
            "total_orders": str(self._current_customer.get("total_orders", 0)),
            "total_amount": self._current_customer.get("formatted_total_amount", ""),
            "last_order_date": self._format_date(
                self._current_customer.get("last_order_date")
            ),
            "value_score": f"{self._current_customer.get('value_score', 0.0):.2f}",
            "loyalty_score": f"{self._current_customer.get('loyalty_score', 0.0):.2f}",
            "cooperation_months": str(
                self._current_customer.get("cooperation_months", 0)
            ),
        }

        # 更新表单数据
        self._finance_info_form.set_form_data(finance_data)

    def _load_interaction_records(self) -> None:
        """加载互动记录"""
        if not self._customer_id or not self._interaction_table:
            return

        try:
            # 这里应该调用InteractionService获取互动记录
            # 暂时使用模拟数据
            interaction_data = [
                {
                    "date": "2024-01-15",
                    "type": "电话沟通",
                    "content": "讨论新产品需求",
                    "result": "有意向",
                    "next_action": "发送产品资料",
                },
                {
                    "date": "2024-01-10",
                    "type": "邮件联系",
                    "content": "发送报价单",
                    "result": "已查看",
                    "next_action": "电话跟进",
                },
            ]

            self._interaction_table.load_data(interaction_data)

        except Exception as e:
            self._logger.warning(f"加载互动记录失败: {e}")

    def _format_date(self, date_value: Any) -> str:
        """格式化日期显示"""
        if not date_value:
            return ""

        if isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                return date_value
        elif isinstance(date_value, datetime):
            return date_value.strftime("%Y-%m-%d")
        else:
            return str(date_value)

    def _on_tab_changed(self, event) -> None:
        """标签页切换事件处理"""
        if not self._notebook:
            return

        selected_tab = self._notebook.select()
        tab_text = self._notebook.tab(selected_tab, "text")

        self._logger.debug(f"切换到标签页: {tab_text}")

        # 根据标签页执行相应的数据加载
        if tab_text == "互动记录":
            self._load_interaction_records()

    def _on_edit_customer(self) -> None:
        """编辑客户按钮点击处理"""
        if not self._customer_id:
            messagebox.showwarning("警告", "没有选择要编辑的客户")
            return

        if self._on_edit_callback:
            self._on_edit_callback(self._customer_id)

    def _refresh_data(self) -> None:
        """刷新数据"""
        if self._customer_id:
            self.load_customer(self._customer_id)

    def _calculate_value_score(self) -> None:
        """计算客户价值评分"""
        if not self._customer_id:
            messagebox.showwarning("警告", "没有选择客户")
            return

        try:
            # 计算价值评分
            value_metrics = self._customer_service.calculate_customer_value_score(
                self._customer_id
            )

            # 显示结果
            score_info = (
                f"客户价值评分计算完成:\n\n"
                f"总评分: {value_metrics.get('total_score', 0):.2f}\n"
                f"忠诚度评分: {value_metrics.get('loyalty_score', 0):.2f}\n"
                f"交易价值评分: {value_metrics.get('transaction_score', 0):.2f}\n"
                f"互动评分: {value_metrics.get('interaction_score', 0):.2f}"
            )

            messagebox.showinfo("价值评分", score_info)

            # 刷新显示
            self._refresh_data()

        except ServiceError as e:
            self._logger.error(f"计算客户价值评分失败: {e}")
            messagebox.showerror("错误", f"计算客户价值评分失败: {e}")
        except Exception as e:
            self._logger.exception(f"计算客户价值评分时发生未知错误: {e}")
            messagebox.showerror("错误", f"计算客户价值评分时发生未知错误: {e}")

    def get_current_customer_id(self) -> Optional[int]:
        """获取当前客户ID"""
        return self._customer_id

    def get_current_customer_data(self) -> Optional[Dict[str, Any]]:
        """获取当前客户数据"""
        return self._current_customer

    def cleanup(self) -> None:
        """清理资源"""
        self._current_customer = None
        self._customer_id = None
        super().cleanup()
