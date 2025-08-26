"""MiniCRM 合同编辑TTK对话框

基于tkinter/ttk实现的合同编辑对话框,替换Qt版本的ContractEditDialog.
提供合同创建和编辑功能,包括:
- 合同基本信息编辑
- 合同条款和条件设置
- 数据验证和保存
- 模板应用支持

设计原则:
- 继承BaseDialog提供标准对话框功能
- 使用FormBuilderTTK构建表单界面
- 集成数据验证和错误提示
- 支持创建和编辑两种模式

作者: MiniCRM开发团队
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from minicrm.core.exceptions import ValidationError
from minicrm.models.contract import Contract
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.base_dialog import BaseDialog
from minicrm.ui.ttk_base.form_builder import FormBuilderTTK


class ContractEditDialogTTK(BaseDialog):
    """合同编辑TTK对话框

    提供合同创建和编辑功能:
    - 合同基本信息输入
    - 合同条款编辑
    - 数据验证
    - 保存和取消操作
    """

    def __init__(
        self,
        parent: tk.Widget,
        contract_service: ContractService,
        contract: Optional[Contract] = None,
        **kwargs,
    ):
        """初始化合同编辑对话框

        Args:
            parent: 父组件
            contract_service: 合同服务实例
            contract: 要编辑的合同(None表示创建新合同)
            **kwargs: 其他参数
        """
        self.contract_service = contract_service
        self.contract = contract
        self.is_edit_mode = contract is not None

        # 表单数据
        self.contract_data: Dict[str, Any] = {}

        # UI组件
        self.form_builder: Optional[FormBuilderTTK] = None
        self.notebook: Optional[ttk.Notebook] = None

        # 设置对话框标题
        title = "编辑合同" if self.is_edit_mode else "新建合同"

        # 初始化基础对话框
        super().__init__(
            parent, title=title, width=700, height=600, resizable=True, **kwargs
        )

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建选项卡容器
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建各个选项卡
        self._create_basic_info_tab()
        self._create_financial_tab()
        self._create_terms_tab()
        self._create_settings_tab()

        # 如果是编辑模式,加载数据
        if self.is_edit_mode and self.contract:
            self._load_contract_data()

    def _create_basic_info_tab(self) -> None:
        """创建基本信息选项卡"""
        # 创建选项卡框架
        basic_frame = ttk.Frame(self.notebook)
        self.notebook.add(basic_frame, text="基本信息")

        # 定义基本信息字段
        basic_fields = [
            {
                "id": "contract_number",
                "label": "合同编号",
                "type": "entry",
                "required": False,  # 可以自动生成
                "placeholder": "自动生成或手动输入",
            },
            {
                "id": "party_name",
                "label": "合同方名称",
                "type": "entry",
                "required": True,
                "placeholder": "请输入客户或供应商名称",
            },
            {
                "id": "contract_type",
                "label": "合同类型",
                "type": "combobox",
                "required": True,
                "options": [
                    ("sales", "销售合同"),
                    ("purchase", "采购合同"),
                    ("service", "服务合同"),
                    ("framework", "框架合同"),
                    ("other", "其他"),
                ],
                "state": "readonly",
            },
            {
                "id": "contract_status",
                "label": "合同状态",
                "type": "combobox",
                "required": True,
                "options": [
                    ("draft", "草稿"),
                    ("pending", "待审批"),
                    ("approved", "已审批"),
                    ("signed", "已签署"),
                    ("active", "执行中"),
                    ("completed", "已完成"),
                    ("terminated", "已终止"),
                    ("expired", "已过期"),
                ],
                "state": "readonly",
            },
        ]

        # 创建表单
        self.basic_form = FormBuilderTTK(basic_frame, fields=basic_fields, columns=1)
        self.basic_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_financial_tab(self) -> None:
        """创建财务信息选项卡"""
        # 创建选项卡框架
        financial_frame = ttk.Frame(self.notebook)
        self.notebook.add(financial_frame, text="财务信息")

        # 定义财务信息字段
        financial_fields = [
            {
                "id": "contract_amount",
                "label": "合同金额",
                "type": "number_spinner",
                "required": True,
                "min_value": 0,
                "max_value": 999999999,
                "decimal_places": 2,
                "step": 0.01,
            },
            {
                "id": "currency",
                "label": "货币类型",
                "type": "combobox",
                "required": True,
                "options": ["CNY", "USD", "EUR", "JPY"],
                "state": "readonly",
            },
            {
                "id": "payment_method",
                "label": "付款方式",
                "type": "combobox",
                "required": True,
                "options": [
                    ("bank_transfer", "银行转账"),
                    ("cash", "现金"),
                    ("check", "支票"),
                    ("credit_card", "信用卡"),
                    ("installment", "分期付款"),
                    ("other", "其他"),
                ],
                "state": "readonly",
            },
            {
                "id": "payment_terms",
                "label": "付款期限",
                "type": "number_spinner",
                "required": True,
                "min_value": 0,
                "max_value": 365,
                "decimal_places": 0,
                "unit": "天",
            },
            {
                "id": "sign_date",
                "label": "签署日期",
                "type": "date_picker",
                "required": False,
                "date_format": "%Y-%m-%d",
            },
            {
                "id": "effective_date",
                "label": "生效日期",
                "type": "date_picker",
                "required": False,
                "date_format": "%Y-%m-%d",
            },
            {
                "id": "expiry_date",
                "label": "到期日期",
                "type": "date_picker",
                "required": False,
                "date_format": "%Y-%m-%d",
            },
        ]

        # 创建表单
        self.financial_form = FormBuilderTTK(
            financial_frame, fields=financial_fields, columns=1
        )
        self.financial_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_terms_tab(self) -> None:
        """创建合同条款选项卡"""
        # 创建选项卡框架
        terms_frame = ttk.Frame(self.notebook)
        self.notebook.add(terms_frame, text="合同条款")

        # 创建滚动区域
        canvas = tk.Canvas(terms_frame)
        scrollbar = ttk.Scrollbar(terms_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 条款和条件
        terms_frame_inner = ttk.LabelFrame(
            scrollable_frame, text="条款和条件", padding=10
        )
        terms_frame_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        self.terms_text = tk.Text(
            terms_frame_inner, height=6, wrap=tk.WORD, font=("Microsoft YaHei UI", 9)
        )
        self.terms_text.pack(fill=tk.BOTH, expand=True)

        # 交付条款
        delivery_frame = ttk.LabelFrame(scrollable_frame, text="交付条款", padding=10)
        delivery_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.delivery_text = tk.Text(
            delivery_frame, height=4, wrap=tk.WORD, font=("Microsoft YaHei UI", 9)
        )
        self.delivery_text.pack(fill=tk.BOTH, expand=True)

        # 保修条款
        warranty_frame = ttk.LabelFrame(scrollable_frame, text="保修条款", padding=10)
        warranty_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        self.warranty_text = tk.Text(
            warranty_frame, height=4, wrap=tk.WORD, font=("Microsoft YaHei UI", 9)
        )
        self.warranty_text.pack(fill=tk.BOTH, expand=True)

    def _create_settings_tab(self) -> None:
        """创建其他设置选项卡"""
        # 创建选项卡框架
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="其他设置")

        # 定义设置字段
        settings_fields = [
            {
                "id": "reminder_days",
                "label": "到期提醒",
                "type": "number_spinner",
                "required": True,
                "min_value": 1,
                "max_value": 365,
                "decimal_places": 0,
                "unit": "天",
                "default": 30,
            },
            {
                "id": "auto_renewal",
                "label": "自动续约",
                "type": "checkbox",
                "required": False,
            },
            {
                "id": "progress_percentage",
                "label": "执行进度",
                "type": "number_spinner",
                "required": False,
                "min_value": 0,
                "max_value": 100,
                "decimal_places": 1,
                "unit": "%",
                "default": 0,
            },
            {
                "id": "notes",
                "label": "备注信息",
                "type": "text",
                "required": False,
                "height": 4,
                "placeholder": "请输入备注信息",
            },
        ]

        # 创建表单
        self.settings_form = FormBuilderTTK(
            settings_frame, fields=settings_fields, columns=1
        )
        self.settings_form.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _setup_buttons(self) -> None:
        """设置按钮"""
        # 创建按钮框架
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 右侧按钮组
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        # 取消按钮
        cancel_btn = ttk.Button(right_buttons, text="取消", command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 保存按钮
        save_btn = ttk.Button(right_buttons, text="保存", command=self._on_save)
        save_btn.pack(side=tk.LEFT)

        # 左侧按钮组
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        # 验证按钮
        validate_btn = ttk.Button(left_buttons, text="验证", command=self._on_validate)
        validate_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 重置按钮
        reset_btn = ttk.Button(left_buttons, text="重置", command=self._on_reset)
        reset_btn.pack(side=tk.LEFT)

    def _load_contract_data(self) -> None:
        """加载合同数据到表单"""
        if not self.contract:
            return

        try:
            # 获取合同数据
            contract_dict = (
                self.contract.to_dict()
                if hasattr(self.contract, "to_dict")
                else self.contract
            )

            # 加载基本信息
            if self.basic_form:
                basic_data = {
                    "contract_number": contract_dict.get("contract_number", ""),
                    "party_name": contract_dict.get("party_name", ""),
                    "contract_type": self._get_enum_value(
                        contract_dict.get("contract_type")
                    ),
                    "contract_status": self._get_enum_value(
                        contract_dict.get("contract_status")
                    ),
                }
                self.basic_form.set_form_data(basic_data)

            # 加载财务信息
            if self.financial_form:
                financial_data = {
                    "contract_amount": float(contract_dict.get("contract_amount", 0)),
                    "currency": contract_dict.get("currency", "CNY"),
                    "payment_method": self._get_enum_value(
                        contract_dict.get("payment_method")
                    ),
                    "payment_terms": contract_dict.get("payment_terms", 30),
                }

                # 处理日期字段
                for date_field in ["sign_date", "effective_date", "expiry_date"]:
                    date_value = contract_dict.get(date_field)
                    if date_value:
                        if hasattr(date_value, "strftime"):
                            financial_data[date_field] = date_value.strftime("%Y-%m-%d")
                        else:
                            financial_data[date_field] = str(date_value)[:10]

                self.financial_form.set_form_data(financial_data)

            # 加载条款信息
            if hasattr(self, "terms_text"):
                self.terms_text.delete("1.0", tk.END)
                self.terms_text.insert(
                    "1.0", contract_dict.get("terms_and_conditions", "")
                )

            if hasattr(self, "delivery_text"):
                self.delivery_text.delete("1.0", tk.END)
                self.delivery_text.insert(
                    "1.0", contract_dict.get("delivery_terms", "")
                )

            if hasattr(self, "warranty_text"):
                self.warranty_text.delete("1.0", tk.END)
                self.warranty_text.insert(
                    "1.0", contract_dict.get("warranty_terms", "")
                )

            # 加载设置信息
            if self.settings_form:
                settings_data = {
                    "reminder_days": contract_dict.get("reminder_days", 30),
                    "auto_renewal": contract_dict.get("auto_renewal", False),
                    "progress_percentage": contract_dict.get("progress_percentage", 0),
                    "notes": contract_dict.get("notes", ""),
                }
                self.settings_form.set_form_data(settings_data)

            self.logger.info("合同数据加载完成")

        except Exception as e:
            self.logger.error(f"加载合同数据失败: {e}")
            message_dialogs_ttk.show_error(self, f"加载合同数据失败: {e}")

    def _get_enum_value(self, enum_obj) -> str:
        """获取枚举值"""
        if hasattr(enum_obj, "value"):
            return enum_obj.value
        return str(enum_obj) if enum_obj else ""

    def _on_save(self) -> None:
        """处理保存事件"""
        try:
            # 收集表单数据
            contract_data = self._collect_form_data()

            # 验证数据
            self._validate_contract_data(contract_data)

            # 保存合同数据
            self.contract_data = contract_data

            # 关闭对话框
            self.result = True
            self.destroy()

        except ValidationError as e:
            message_dialogs_ttk.show_warning(self, str(e))
        except Exception as e:
            self.logger.error(f"保存合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"保存合同失败: {e}")

    def _on_cancel(self) -> None:
        """处理取消事件"""
        self.result = False
        self.destroy()

    def _on_validate(self) -> None:
        """处理验证事件"""
        try:
            # 收集表单数据
            contract_data = self._collect_form_data()

            # 验证数据
            self._validate_contract_data(contract_data)

            message_dialogs_ttk.show_info(self, "合同数据验证通过!")

        except ValidationError as e:
            message_dialogs_ttk.show_warning(self, str(e))
        except Exception as e:
            self.logger.error(f"验证合同失败: {e}")
            message_dialogs_ttk.show_error(self, f"验证合同失败: {e}")

    def _on_reset(self) -> None:
        """处理重置事件"""
        if message_dialogs_ttk.confirm(
            self, "确定要重置表单吗?所有未保存的更改将丢失.", "确认重置"
        ):
            # 清空所有表单
            if self.basic_form:
                self.basic_form.clear_form()

            if self.financial_form:
                self.financial_form.clear_form()

            if hasattr(self, "terms_text"):
                self.terms_text.delete("1.0", tk.END)

            if hasattr(self, "delivery_text"):
                self.delivery_text.delete("1.0", tk.END)

            if hasattr(self, "warranty_text"):
                self.warranty_text.delete("1.0", tk.END)

            if self.settings_form:
                self.settings_form.clear_form()

            # 如果是编辑模式,重新加载数据
            if self.is_edit_mode:
                self._load_contract_data()

    def _collect_form_data(self) -> Dict[str, Any]:
        """收集表单数据"""
        contract_data = {}

        # 收集基本信息
        if self.basic_form:
            basic_data = self.basic_form.get_form_data()
            contract_data.update(basic_data)

        # 收集财务信息
        if self.financial_form:
            financial_data = self.financial_form.get_form_data()
            contract_data.update(financial_data)

        # 收集条款信息
        if hasattr(self, "terms_text"):
            contract_data["terms_and_conditions"] = self.terms_text.get(
                "1.0", tk.END
            ).strip()

        if hasattr(self, "delivery_text"):
            contract_data["delivery_terms"] = self.delivery_text.get(
                "1.0", tk.END
            ).strip()

        if hasattr(self, "warranty_text"):
            contract_data["warranty_terms"] = self.warranty_text.get(
                "1.0", tk.END
            ).strip()

        # 收集设置信息
        if self.settings_form:
            settings_data = self.settings_form.get_form_data()
            contract_data.update(settings_data)

        return contract_data

    def _validate_contract_data(self, data: Dict[str, Any]) -> None:
        """验证合同数据"""
        # 验证必填字段
        if not data.get("party_name", "").strip():
            raise ValidationError("合同方名称不能为空")

        if not data.get("contract_type"):
            raise ValidationError("请选择合同类型")

        if not data.get("contract_status"):
            raise ValidationError("请选择合同状态")

        # 验证合同金额
        amount = data.get("contract_amount")
        if amount is None or amount < 0:
            raise ValidationError("合同金额不能为负数")

        # 验证付款期限
        payment_terms = data.get("payment_terms", 0)
        if payment_terms < 0 or payment_terms > 365:
            raise ValidationError("付款期限必须在0-365天之间")

        # 验证日期逻辑
        sign_date = data.get("sign_date")
        effective_date = data.get("effective_date")
        expiry_date = data.get("expiry_date")

        if effective_date and expiry_date:
            try:
                if isinstance(effective_date, str):
                    effective_dt = datetime.strptime(effective_date, "%Y-%m-%d")
                else:
                    effective_dt = effective_date

                if isinstance(expiry_date, str):
                    expiry_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
                else:
                    expiry_dt = expiry_date

                if effective_dt >= expiry_dt:
                    raise ValidationError("生效日期必须早于到期日期")
            except ValueError:
                raise ValidationError("日期格式不正确")

        if sign_date and effective_date:
            try:
                if isinstance(sign_date, str):
                    sign_dt = datetime.strptime(sign_date, "%Y-%m-%d")
                else:
                    sign_dt = sign_date

                if isinstance(effective_date, str):
                    effective_dt = datetime.strptime(effective_date, "%Y-%m-%d")
                else:
                    effective_dt = effective_date

                if sign_dt > effective_dt:
                    raise ValidationError("签署日期不能晚于生效日期")
            except ValueError:
                raise ValidationError("日期格式不正确")

        # 验证进度
        progress = data.get("progress_percentage", 0)
        if progress < 0 or progress > 100:
            raise ValidationError("执行进度必须在0-100之间")

    def get_contract_data(self) -> Dict[str, Any]:
        """获取合同数据"""
        return self.contract_data.copy()

    def show_modal(self) -> bool:
        """显示模态对话框

        Returns:
            bool: 用户是否点击了保存按钮
        """
        # 设置为模态
        self.transient(self.parent)
        self.grab_set()

        # 居中显示
        self.center_on_parent()

        # 等待对话框关闭
        self.wait_window()

        return getattr(self, "result", False)


# 导出类
__all__ = ["ContractEditDialogTTK"]
