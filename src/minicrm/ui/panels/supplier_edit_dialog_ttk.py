"""MiniCRM 供应商编辑对话框TTK组件

实现供应商信息的新增和编辑功能,包括:
- 供应商基本信息编辑表单
- 供应商类型和分类设置
- 联系人信息管理
- 资质信息管理
- 数据验证和保存
- 支持新增和编辑两种模式

设计原则:
- 继承BaseDialogTTK提供标准对话框功能
- 集成FormBuilderTTK构建编辑表单
- 使用transfunctions进行数据验证
- 提供完整的错误处理和用户反馈
- 支持数据绑定和实时验证
"""

from decimal import Decimal
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.models.supplier import QualityRating, SupplierLevel, SupplierType
from minicrm.services.supplier_service import SupplierService
from minicrm.ui.ttk_base.base_dialog import BaseDialogTTK
from minicrm.ui.ttk_base.form_builder import FormBuilderTTK
from transfunctions import validation


class SupplierEditDialogTTK(BaseDialogTTK):
    """供应商编辑对话框TTK组件

    提供供应商信息的新增和编辑功能,支持:
    - 完整的供应商信息编辑表单
    - 数据验证和错误提示
    - 新增和编辑两种模式
    - 模态对话框交互
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        supplier_service: Optional[SupplierService] = None,
        supplier_id: Optional[int] = None,
        on_save_callback: Optional[Callable[[int, bool], None]] = None,
        **kwargs,
    ):
        """初始化供应商编辑对话框

        Args:
            parent: 父窗口组件
            supplier_service: 供应商服务实例
            supplier_id: 供应商ID,None表示新增模式
            on_save_callback: 保存成功回调函数,参数为(supplier_id, is_new)
            **kwargs: 其他参数
        """
        # 依赖注入
        self._supplier_service = supplier_service
        self._supplier_id = supplier_id
        self._on_save_callback = on_save_callback

        # 状态管理
        self._is_new_supplier = supplier_id is None
        self._original_data: Optional[Dict[str, Any]] = None
        self._current_data: Dict[str, Any] = {}

        # 设置对话框标题
        title = "新增供应商" if self._is_new_supplier else "编辑供应商"

        # 初始化基类
        super().__init__(
            parent=parent, title=title, size=(600, 700), min_size=(550, 650), **kwargs
        )

        # UI组件
        self._form_builder: Optional[FormBuilderTTK] = None

        # 日志记录器
        self._logger = logging.getLogger(self.__class__.__name__)

        # 加载数据
        self._load_data()

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建标题
        self._create_title_area()

        # 创建表单区域
        self._create_form_area()

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        # 移除默认按钮
        self.remove_button("取消")
        self.remove_button("确定")

        # 添加自定义按钮
        self.add_button("取消", self._on_cancel_click, DialogResult.CANCEL)
        self.add_button("验证表单", self._validate_form_click)
        self.add_button("保存", self._on_save_click, DialogResult.OK, default=True)

    def _create_title_area(self) -> None:
        """创建标题区域"""
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        # 主标题
        title = "新增供应商" if self._is_new_supplier else "编辑供应商"
        title_label = ttk.Label(
            title_frame,
            text=title,
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        title_label.pack(side=tk.LEFT)

        # 副标题
        subtitle = "请填写供应商的基本信息和联系方式"
        subtitle_label = ttk.Label(
            title_frame,
            text=subtitle,
            foreground="gray",
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0))

    def _create_form_area(self) -> None:
        """创建表单区域"""
        # 创建滚动区域
        form_frame = ttk.Frame(self.content_frame)
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

    def _get_form_fields(self) -> list:
        """获取表单字段定义"""
        return [
            # 基本信息分组
            {"type": "separator", "label": "基本信息"},
            {
                "id": "name",
                "type": "entry",
                "label": "供应商名称",
                "required": True,
                "validation": validation.is_not_empty,
                "placeholder": "请输入供应商名称",
            },
            {
                "id": "short_name",
                "type": "entry",
                "label": "简称",
                "placeholder": "供应商简称(可选)",
            },
            {
                "id": "supplier_type",
                "type": "combobox",
                "label": "供应商类型",
                "required": True,
                "options": [t.value for t in SupplierType],
            },
            {
                "id": "supplier_level",
                "type": "combobox",
                "label": "供应商等级",
                "required": True,
                "options": [l.value for l in SupplierLevel],
            },
            {
                "id": "business_license",
                "type": "entry",
                "label": "营业执照号",
                "placeholder": "请输入统一社会信用代码",
            },
            {
                "id": "tax_number",
                "type": "entry",
                "label": "税号",
                "placeholder": "纳税人识别号",
            },
            # 联系信息分组
            {"type": "separator", "label": "联系信息"},
            {
                "id": "contact_person",
                "type": "entry",
                "label": "主要联系人",
                "required": True,
                "validation": validation.is_not_empty,
                "placeholder": "请输入联系人姓名",
            },
            {
                "id": "phone",
                "type": "entry",
                "label": "联系电话",
                "required": True,
                "validation": validation.is_valid_phone,
                "placeholder": "请输入手机号码",
            },
            {
                "id": "email",
                "type": "entry",
                "label": "邮箱地址",
                "validation": validation.is_valid_email,
                "placeholder": "example@company.com",
            },
            {
                "id": "fax",
                "type": "entry",
                "label": "传真号码",
                "placeholder": "可选",
            },
            {
                "id": "website",
                "type": "entry",
                "label": "公司网站",
                "placeholder": "https://www.company.com",
            },
            # 地址信息分组
            {"type": "separator", "label": "地址信息"},
            {
                "id": "address",
                "type": "text",
                "label": "详细地址",
                "height": 3,
                "placeholder": "请输入详细地址信息",
            },
            {
                "id": "postal_code",
                "type": "entry",
                "label": "邮政编码",
                "placeholder": "6位邮政编码",
            },
            # 财务信息分组
            {"type": "separator", "label": "财务信息"},
            {
                "id": "payment_terms",
                "type": "number_spinner",
                "label": "付款期限",
                "min_value": 0,
                "max_value": 365,
                "unit": "天",
                "default": 30,
            },
            {
                "id": "credit_limit",
                "type": "number_spinner",
                "label": "信用额度",
                "min_value": 0,
                "max_value": 10000000,
                "decimal_places": 2,
                "unit": "元",
                "default": 0,
            },
            {
                "id": "bank_name",
                "type": "entry",
                "label": "开户银行",
                "placeholder": "银行名称",
            },
            {
                "id": "bank_account",
                "type": "entry",
                "label": "银行账号",
                "placeholder": "银行账户号码",
            },
            # 其他信息分组
            {"type": "separator", "label": "其他信息"},
            {
                "id": "quality_rating",
                "type": "combobox",
                "label": "质量评级",
                "options": [q.value for q in QualityRating],
            },
            {
                "id": "certification_status",
                "type": "combobox",
                "label": "认证状态",
                "options": ["已认证", "待认证", "未认证", "认证过期"],
                "default": "待认证",
            },
            {
                "id": "notes",
                "type": "text",
                "label": "备注信息",
                "height": 4,
                "placeholder": "其他需要记录的信息...",
            },
        ]

    def _load_data(self) -> None:
        """加载数据"""
        if self._is_new_supplier:
            # 新增模式,设置默认值
            self._set_default_values()
        else:
            # 编辑模式,加载现有数据
            self._load_supplier_data()

    def _set_default_values(self) -> None:
        """设置默认值(新增模式)"""
        if self._form_builder:
            default_data = {
                "supplier_type": SupplierType.MATERIAL.value,
                "supplier_level": SupplierLevel.NORMAL.value,
                "payment_terms": "30",
                "credit_limit": "0.00",
                "certification_status": "待认证",
            }
            self._form_builder.set_form_data(default_data)

    def _load_supplier_data(self) -> None:
        """加载供应商数据(编辑模式)"""
        try:
            # 获取供应商数据
            supplier_data = self._supplier_service.get_supplier_by_id(self._supplier_id)
            if not supplier_data:
                self.show_error("未找到指定的供应商")
                self._close_dialog()
                return

            # 保存原始数据
            self._original_data = supplier_data.copy()

            # 转换数据格式以适配表单
            form_data = self._convert_to_form_data(supplier_data)

            # 填充表单
            if self._form_builder:
                self._form_builder.set_form_data(form_data)

        except ServiceError as e:
            self._logger.error(f"加载供应商数据失败: {e}")
            self.show_error(f"加载供应商数据失败:{e}")
            self._close_dialog()

    def _convert_to_form_data(self, supplier_data: Dict[str, Any]) -> Dict[str, Any]:
        """将供应商数据转换为表单数据格式"""
        form_data = {}

        # 基本字段直接映射
        field_mappings = {
            "name": "name",
            "short_name": "short_name",
            "supplier_type": "supplier_type",
            "supplier_level": "supplier_level",
            "business_license": "business_license",
            "tax_number": "tax_number",
            "contact_person": "contact_person",
            "phone": "phone",
            "email": "email",
            "fax": "fax",
            "website": "website",
            "address": "address",
            "postal_code": "postal_code",
            "bank_name": "bank_name",
            "bank_account": "bank_account",
            "quality_rating": "quality_rating",
            "certification_status": "certification_status",
            "notes": "notes",
        }

        for form_field, data_field in field_mappings.items():
            value = supplier_data.get(data_field)
            if value is not None:
                form_data[form_field] = str(value)

        # 特殊字段处理
        if "payment_terms" in supplier_data:
            form_data["payment_terms"] = str(supplier_data["payment_terms"])

        if "credit_limit" in supplier_data:
            credit_limit = supplier_data["credit_limit"]
            if isinstance(credit_limit, (int, float, Decimal)):
                form_data["credit_limit"] = f"{credit_limit:.2f}"
            else:
                form_data["credit_limit"] = str(credit_limit)

        return form_data

    def _validate_input(self) -> bool:
        """验证输入数据"""
        if not self._form_builder:
            return False

        # 执行表单验证
        is_valid, errors = self._form_builder.validate_form()

        if not is_valid:
            # 显示验证错误
            error_messages = []
            for field, error in errors.items():
                error_messages.append(f"• {field}: {error}")

            error_text = "表单验证失败,请检查以下问题:\n\n" + "\n".join(
                error_messages
            )
            self.show_error(error_text)
            return False

        return True

    def _validate_form_click(self) -> None:
        """验证表单按钮处理"""
        if self._validate_input():
            self.show_info("所有数据验证通过!")

    def _get_result_data(self) -> Dict[str, Any]:
        """获取结果数据"""
        if not self._form_builder:
            return {}

        form_data = self._form_builder.get_form_data()
        return self._convert_to_supplier_data(form_data)

    def _on_save_click(self) -> None:
        """保存按钮处理"""
        try:
            # 验证表单
            if not self._validate_input():
                return

            # 获取表单数据
            form_data = self._form_builder.get_form_data()
            if not form_data:
                self.show_error("无法获取表单数据")
                return

            # 转换为供应商数据格式
            supplier_data = self._convert_to_supplier_data(form_data)

            # 保存数据
            if self._is_new_supplier:
                # 新增供应商
                supplier_id = self._supplier_service.create_supplier(supplier_data)
                self.show_info("供应商创建成功!")

                # 调用保存回调
                if self._on_save_callback:
                    self._on_save_callback(supplier_id, True)
            else:
                # 更新供应商
                supplier_data["id"] = self._supplier_id
                self._supplier_service.update_supplier(self._supplier_id, supplier_data)
                self.show_info("供应商信息更新成功!")

                # 调用保存回调
                if self._on_save_callback:
                    self._on_save_callback(self._supplier_id, False)

            # 设置结果并关闭对话框
            self.result = DialogResult.OK
            self.return_value = supplier_data
            self._close_dialog()

        except ValidationError as e:
            self.show_error(f"数据验证失败:{e}")
        except ServiceError as e:
            self._logger.error(f"保存供应商失败: {e}")
            self.show_error(f"保存供应商失败:{e}")
        except Exception as e:
            self._logger.error(f"保存供应商时发生未知错误: {e}")
            self.show_error(f"保存时发生错误:{e}")

    def _convert_to_supplier_data(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """将表单数据转换为供应商数据格式"""
        supplier_data = {}

        # 基本字段直接映射
        field_mappings = {
            "name": "name",
            "short_name": "short_name",
            "supplier_type": "supplier_type",
            "supplier_level": "supplier_level",
            "business_license": "business_license",
            "tax_number": "tax_number",
            "contact_person": "contact_person",
            "phone": "phone",
            "email": "email",
            "fax": "fax",
            "website": "website",
            "address": "address",
            "postal_code": "postal_code",
            "bank_name": "bank_name",
            "bank_account": "bank_account",
            "quality_rating": "quality_rating",
            "certification_status": "certification_status",
            "notes": "notes",
        }

        for form_field, data_field in field_mappings.items():
            value = form_data.get(form_field)
            if value and value.strip():
                supplier_data[data_field] = value.strip()

        # 特殊字段处理
        if "payment_terms" in form_data:
            try:
                supplier_data["payment_terms"] = int(form_data["payment_terms"])
            except (ValueError, TypeError):
                supplier_data["payment_terms"] = 30

        if "credit_limit" in form_data:
            try:
                supplier_data["credit_limit"] = float(form_data["credit_limit"])
            except (ValueError, TypeError):
                supplier_data["credit_limit"] = 0.0

        return supplier_data

    def _on_cancel_click(self) -> None:
        """取消按钮处理"""
        # 检查是否有未保存的更改
        if self._has_unsaved_changes():
            if not self.confirm("您有未保存的更改,确定要取消吗?"):
                return

        super()._on_cancel()

    def _has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        if not self._form_builder:
            return False

        current_data = self._form_builder.get_form_data()
        if not current_data:
            return False

        if self._is_new_supplier:
            # 新增模式,检查是否有任何非空值
            for value in current_data.values():
                if value and str(value).strip():
                    return True
            return False
        # 编辑模式,比较当前数据与原始数据
        if not self._original_data:
            return True

        original_form_data = self._convert_to_form_data(self._original_data)
        return current_data != original_form_data

    def get_result(self) -> Optional[Dict[str, Any]]:
        """获取操作结果"""
        # 如果需要返回结果数据,可以在这里实现
        return None
