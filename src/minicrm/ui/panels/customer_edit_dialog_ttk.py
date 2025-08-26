"""MiniCRM 客户编辑对话框TTK组件

实现客户信息的新增和编辑功能,包括:
- 客户基本信息编辑表单
- 客户等级和类型设置
- 行业类型管理
- 数据验证和保存
- 支持新增和编辑两种模式

设计原则:
- 使用TTK Toplevel实现模态对话框
- 集成FormBuilderTTK构建编辑表单
- 使用transfunctions进行数据验证
- 提供完整的错误处理和用户反馈
- 支持数据绑定和实时验证
"""

from decimal import Decimal
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, Optional

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.models.customer import CustomerLevel, CustomerType, IndustryType
from minicrm.services.customer.customer_service_facade import CustomerServiceFacade
from minicrm.ui.ttk_base.form_builder import FormBuilderTTK
from transfunctions import validation


class CustomerEditDialogTTK(tk.Toplevel):
    """客户编辑对话框TTK组件

    提供客户信息的新增和编辑功能,支持:
    - 完整的客户信息编辑表单
    - 数据验证和错误提示
    - 新增和编辑两种模式
    - 模态对话框交互
    """

    def __init__(
        self,
        parent: tk.Widget,
        customer_service: CustomerServiceFacade,
        customer_id: Optional[int] = None,
        on_save_callback: Optional[Callable[[int, bool], None]] = None,
        **kwargs,
    ):
        """初始化客户编辑对话框

        Args:
            parent: 父窗口
            customer_service: 客户服务实例
            customer_id: 客户ID,None表示新增模式
            on_save_callback: 保存成功回调函数 (customer_id, is_new)
            **kwargs: 其他参数
        """
        super().__init__(parent, **kwargs)

        self._customer_service = customer_service
        self._customer_id = customer_id
        self._on_save_callback = on_save_callback
        self._logger = logging.getLogger(__name__)

        # 对话框状态
        self._is_new_customer = customer_id is None
        self._current_customer_data: Optional[Dict[str, Any]] = None
        self._form_builder: Optional[FormBuilderTTK] = None

        # 对话框结果
        self.result = None

        # 设置对话框
        self._setup_dialog()
        self._setup_ui()
        self._bind_events()

        # 加载数据
        if not self._is_new_customer:
            self._load_customer_data()
        else:
            self._set_default_values()

    def _setup_dialog(self) -> None:
        """设置对话框属性"""
        # 设置标题
        title = "新增客户" if self._is_new_customer else "编辑客户"
        self.title(title)

        # 设置大小和位置
        self.geometry("600x700")
        self.resizable(True, True)

        # 设置为模态对话框
        self.transient(self.master)
        self.grab_set()

        # 居中显示
        self._center_dialog()

    def _center_dialog(self) -> None:
        """居中显示对话框"""
        self.update_idletasks()

        # 获取屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 获取对话框尺寸
        dialog_width = self.winfo_reqwidth()
        dialog_height = self.winfo_reqheight()

        # 计算居中位置
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2

        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主容器
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建标题
        self._create_title_area(main_frame)

        # 创建表单区域
        self._create_form_area(main_frame)

        # 创建按钮区域
        self._create_button_area(main_frame)

    def _create_title_area(self, parent: tk.Widget) -> None:
        """创建标题区域"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        # 标题标签
        title_text = "新增客户信息" if self._is_new_customer else "编辑客户信息"
        title_label = ttk.Label(
            title_frame, text=title_text, font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 必填字段提示
        hint_label = ttk.Label(
            title_frame,
            text="* 表示必填字段",
            font=("Microsoft YaHei UI", 9),
            foreground="red",
        )
        hint_label.pack(side=tk.RIGHT)

    def _create_form_area(self, parent: tk.Widget) -> None:
        """创建表单区域"""
        # 创建滚动区域
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(form_frame)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 定义表单字段
        form_fields = self._get_form_fields()

        # 创建表单构建器
        self._form_builder = FormBuilderTTK(scrollable_frame, form_fields)
        self._form_builder.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

    def _get_form_fields(self) -> list[Dict[str, Any]]:
        """获取表单字段定义"""
        return [
            {
                "id": "name",
                "label": "客户姓名 *",
                "type": "entry",
                "required": True,
                "validator": self._validate_name,
            },
            {
                "id": "phone",
                "label": "联系电话 *",
                "type": "entry",
                "required": True,
                "validator": self._validate_phone,
            },
            {
                "id": "email",
                "label": "邮箱地址",
                "type": "entry",
                "validator": self._validate_email,
            },
            {"id": "company_name", "label": "公司名称", "type": "entry"},
            {
                "id": "customer_level",
                "label": "客户等级",
                "type": "combobox",
                "options": [level.value for level in CustomerLevel],
                "default": CustomerLevel.NORMAL.value,
            },
            {
                "id": "customer_type",
                "label": "客户类型",
                "type": "combobox",
                "options": [ctype.value for ctype in CustomerType],
                "default": CustomerType.ENTERPRISE.value,
            },
            {
                "id": "industry_type",
                "label": "行业类型",
                "type": "combobox",
                "options": [industry.value for industry in IndustryType],
                "default": IndustryType.OTHER.value,
            },
            {"id": "tax_id", "label": "税号", "type": "entry"},
            {
                "id": "credit_limit",
                "label": "授信额度",
                "type": "entry",
                "validator": self._validate_credit_limit,
                "default": "0.00",
            },
            {
                "id": "payment_terms",
                "label": "付款期限(天)",
                "type": "entry",
                "validator": self._validate_payment_terms,
                "default": "30",
            },
            {"id": "address", "label": "联系地址", "type": "text", "height": 3},
            {"id": "source", "label": "客户来源", "type": "entry"},
            {"id": "notes", "label": "备注信息", "type": "text", "height": 4},
        ]

    def _create_button_area(self, parent: tk.Widget) -> None:
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self._on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=(10, 0))

        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=self._on_save)
        save_button.pack(side=tk.RIGHT)

        # 验证按钮
        validate_button = ttk.Button(
            button_frame, text="验证数据", command=self._validate_form
        )
        validate_button.pack(side=tk.LEFT)

    def _bind_events(self) -> None:
        """绑定事件处理"""
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        # 键盘事件
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.bind("<Control-s>", lambda e: self._on_save())

    def _load_customer_data(self) -> None:
        """加载客户数据"""
        if not self._customer_id:
            return

        try:
            customer_data = self._customer_service.get_customer_by_id(self._customer_id)
            if not customer_data:
                messagebox.showerror("错误", f"未找到客户ID: {self._customer_id}")
                self._on_cancel()
                return

            self._current_customer_data = customer_data

            # 设置表单值
            if self._form_builder:
                form_values = self._prepare_form_values(customer_data)
                self._form_builder.set_form_data(form_values)

            self._logger.info(f"成功加载客户数据: {self._customer_id}")

        except ServiceError as e:
            self._logger.error(f"加载客户数据失败: {e}")
            messagebox.showerror("错误", f"加载客户数据失败: {e}")
            self._on_cancel()
        except Exception as e:
            self._logger.exception(f"加载客户数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"加载客户数据时发生未知错误: {e}")
            self._on_cancel()

    def _prepare_form_values(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备表单值"""
        return {
            "name": customer_data.get("name", ""),
            "phone": customer_data.get("phone", ""),
            "email": customer_data.get("email", ""),
            "company_name": customer_data.get("company_name", ""),
            "customer_level": customer_data.get(
                "customer_level", CustomerLevel.NORMAL.value
            ),
            "customer_type": customer_data.get(
                "customer_type", CustomerType.ENTERPRISE.value
            ),
            "industry_type": customer_data.get(
                "industry_type", IndustryType.OTHER.value
            ),
            "tax_id": customer_data.get("tax_id", ""),
            "credit_limit": str(customer_data.get("credit_limit", "0.00")),
            "payment_terms": str(customer_data.get("payment_terms", 30)),
            "address": customer_data.get("address", ""),
            "source": customer_data.get("source", ""),
            "notes": customer_data.get("notes", ""),
        }

    def _set_default_values(self) -> None:
        """设置默认值"""
        if not self._form_builder:
            return

        default_values = {
            "customer_level": CustomerLevel.NORMAL.value,
            "customer_type": CustomerType.ENTERPRISE.value,
            "industry_type": IndustryType.OTHER.value,
            "credit_limit": "0.00",
            "payment_terms": "30",
        }

        self._form_builder.set_form_data(default_values)

    def _validate_form(self) -> bool:
        """验证表单数据"""
        if not self._form_builder:
            return False

        try:
            # 获取表单数据
            form_data = self._form_builder.get_form_data()

            # 执行验证
            is_valid, errors = self._form_builder.validate()

            if not is_valid:
                error_message = "数据验证失败:\n\n" + "\n".join(errors)
                messagebox.showerror("验证错误", error_message)
                return False

            # 额外的业务验证
            business_errors = self._validate_business_rules(form_data)
            if business_errors:
                error_message = "业务规则验证失败:\n\n" + "\n".join(business_errors)
                messagebox.showerror("验证错误", error_message)
                return False

            messagebox.showinfo("验证成功", "所有数据验证通过!")
            return True

        except Exception as e:
            self._logger.exception(f"表单验证时发生错误: {e}")
            messagebox.showerror("错误", f"表单验证时发生错误: {e}")
            return False

    def _validate_business_rules(self, form_data: Dict[str, Any]) -> list[str]:
        """验证业务规则"""
        errors = []

        # 检查客户名称是否重复(新增时)
        if self._is_new_customer:
            try:
                # 这里应该调用服务检查名称重复
                # 暂时跳过此检查
                pass
            except Exception as e:
                self._logger.warning(f"检查客户名称重复时出错: {e}")

        return errors

    def _validate_name(self, value: str) -> tuple[bool, str]:
        """验证客户姓名"""
        if not value or not value.strip():
            return False, "客户姓名不能为空"

        if len(value.strip()) < 2:
            return False, "客户姓名至少需要2个字符"

        if len(value.strip()) > 50:
            return False, "客户姓名不能超过50个字符"

        return True, ""

    def _validate_phone(self, value: str) -> tuple[bool, str]:
        """验证电话号码"""
        if not value or not value.strip():
            return False, "联系电话不能为空"

        # 使用transfunctions验证电话号码
        try:
            phone_result = validation.validate_phone(value.strip())
            if not phone_result.is_valid:
                return False, phone_result.errors[
                    0
                ] if phone_result.errors else "电话号码格式不正确"
        except Exception as e:
            self._logger.warning(f"电话号码验证出错: {e}")
            return False, "电话号码验证失败"

        return True, ""

    def _validate_email(self, value: str) -> tuple[bool, str]:
        """验证邮箱地址"""
        if not value or not value.strip():
            return True, ""  # 邮箱不是必填项

        # 使用transfunctions验证邮箱
        try:
            email_result = validation.validate_email(value.strip())
            if not email_result.is_valid:
                return False, email_result.errors[
                    0
                ] if email_result.errors else "邮箱地址格式不正确"
        except Exception as e:
            self._logger.warning(f"邮箱验证出错: {e}")
            return False, "邮箱验证失败"

        return True, ""

    def _validate_credit_limit(self, value: str) -> tuple[bool, str]:
        """验证授信额度"""
        if not value or not value.strip():
            return True, ""  # 可以为空,默认为0

        try:
            credit_limit = Decimal(value.strip())
            if credit_limit < 0:
                return False, "授信额度不能为负数"
            if credit_limit > Decimal("999999999.99"):
                return False, "授信额度不能超过999,999,999.99"
        except Exception:
            return False, "授信额度必须是有效的数字"

        return True, ""

    def _validate_payment_terms(self, value: str) -> tuple[bool, str]:
        """验证付款期限"""
        if not value or not value.strip():
            return True, ""  # 可以为空,默认为30

        try:
            payment_terms = int(value.strip())
            if payment_terms < 0:
                return False, "付款期限不能为负数"
            if payment_terms > 365:
                return False, "付款期限不能超过365天"
        except (ValueError, TypeError):
            return False, "付款期限必须是有效的整数"

        return True, ""

    def _on_save(self) -> None:
        """保存按钮点击处理"""
        try:
            # 验证表单
            if not self._validate_form():
                return

            # 获取表单数据
            if not self._form_builder:
                messagebox.showerror("错误", "表单未初始化")
                return

            form_data = self._form_builder.get_form_data()

            # 准备保存数据
            save_data = self._prepare_save_data(form_data)

            # 保存数据
            if self._is_new_customer:
                customer_id = self._customer_service.create_customer(save_data)
                messagebox.showinfo("成功", f"客户创建成功!客户ID: {customer_id}")
            else:
                success = self._customer_service.update_customer(
                    self._customer_id, save_data
                )
                if success:
                    customer_id = self._customer_id
                    messagebox.showinfo("成功", "客户信息更新成功!")
                else:
                    messagebox.showerror("错误", "客户信息更新失败")
                    return

            # 调用回调函数
            if self._on_save_callback:
                self._on_save_callback(customer_id, self._is_new_customer)

            # 设置结果并关闭对话框
            self.result = customer_id
            self.destroy()

        except ServiceError as e:
            self._logger.error(f"保存客户数据失败: {e}")
            messagebox.showerror("错误", f"保存客户数据失败: {e}")
        except ValidationError as e:
            self._logger.error(f"数据验证失败: {e}")
            messagebox.showerror("验证错误", f"数据验证失败: {e}")
        except Exception as e:
            self._logger.exception(f"保存客户数据时发生未知错误: {e}")
            messagebox.showerror("错误", f"保存客户数据时发生未知错误: {e}")

    def _prepare_save_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """准备保存数据"""
        save_data = {}

        # 基本信息
        save_data["name"] = form_data.get("name", "").strip()
        save_data["phone"] = form_data.get("phone", "").strip()
        save_data["email"] = form_data.get("email", "").strip()
        save_data["company_name"] = form_data.get("company_name", "").strip()
        save_data["tax_id"] = form_data.get("tax_id", "").strip()
        save_data["address"] = form_data.get("address", "").strip()
        save_data["source"] = form_data.get("source", "").strip()
        save_data["notes"] = form_data.get("notes", "").strip()

        # 枚举字段
        save_data["customer_level"] = form_data.get(
            "customer_level", CustomerLevel.NORMAL.value
        )
        save_data["customer_type"] = form_data.get(
            "customer_type", CustomerType.ENTERPRISE.value
        )
        save_data["industry_type"] = form_data.get(
            "industry_type", IndustryType.OTHER.value
        )

        # 数值字段
        try:
            credit_limit_str = form_data.get("credit_limit", "0.00").strip()
            save_data["credit_limit"] = (
                float(Decimal(credit_limit_str)) if credit_limit_str else 0.00
            )
        except (ValueError, TypeError):
            save_data["credit_limit"] = 0.00

        try:
            payment_terms_str = form_data.get("payment_terms", "30").strip()
            save_data["payment_terms"] = (
                int(payment_terms_str) if payment_terms_str else 30
            )
        except (ValueError, TypeError):
            save_data["payment_terms"] = 30

        return save_data

    def _on_cancel(self) -> None:
        """取消按钮点击处理"""
        # 检查是否有未保存的更改
        if self._has_unsaved_changes():
            result = messagebox.askyesno(
                "确认取消", "您有未保存的更改,确定要取消吗?", icon="warning"
            )
            if not result:
                return

        self.result = None
        self.destroy()

    def _has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        if not self._form_builder:
            return False

        try:
            current_data = self._form_builder.get_form_data()

            if self._is_new_customer:
                # 新增模式:检查是否有任何非默认值
                default_values = {
                    "name": "",
                    "phone": "",
                    "email": "",
                    "company_name": "",
                    "customer_level": CustomerLevel.NORMAL.value,
                    "customer_type": CustomerType.ENTERPRISE.value,
                    "industry_type": IndustryType.OTHER.value,
                    "tax_id": "",
                    "credit_limit": "0.00",
                    "payment_terms": "30",
                    "address": "",
                    "source": "",
                    "notes": "",
                }

                for key, default_value in default_values.items():
                    current_value = current_data.get(key, "").strip()
                    if current_value != str(default_value).strip():
                        return True

                return False
            # 编辑模式:与原始数据比较
            if not self._current_customer_data:
                return False

            original_values = self._prepare_form_values(self._current_customer_data)

            for key, original_value in original_values.items():
                current_value = current_data.get(key, "").strip()
                if current_value != str(original_value).strip():
                    return True

            return False

        except Exception as e:
            self._logger.warning(f"检查未保存更改时出错: {e}")
            return True  # 出错时假设有更改

    def get_result(self) -> Optional[int]:
        """获取对话框结果"""
        return self.result

    @staticmethod
    def show_new_customer_dialog(
        parent: tk.Widget,
        customer_service: CustomerServiceFacade,
        on_save_callback: Optional[Callable[[int, bool], None]] = None,
    ) -> Optional[int]:
        """显示新增客户对话框

        Args:
            parent: 父窗口
            customer_service: 客户服务实例
            on_save_callback: 保存成功回调函数

        Returns:
            Optional[int]: 新创建的客户ID,取消时返回None
        """
        dialog = CustomerEditDialogTTK(
            parent=parent,
            customer_service=customer_service,
            customer_id=None,
            on_save_callback=on_save_callback,
        )

        parent.wait_window(dialog)
        return dialog.get_result()

    @staticmethod
    def show_edit_customer_dialog(
        parent: tk.Widget,
        customer_service: CustomerServiceFacade,
        customer_id: int,
        on_save_callback: Optional[Callable[[int, bool], None]] = None,
    ) -> Optional[int]:
        """显示编辑客户对话框

        Args:
            parent: 父窗口
            customer_service: 客户服务实例
            customer_id: 要编辑的客户ID
            on_save_callback: 保存成功回调函数

        Returns:
            Optional[int]: 客户ID,取消时返回None
        """
        dialog = CustomerEditDialogTTK(
            parent=parent,
            customer_service=customer_service,
            customer_id=customer_id,
            on_save_callback=on_save_callback,
        )

        parent.wait_window(dialog)
        return dialog.get_result()
