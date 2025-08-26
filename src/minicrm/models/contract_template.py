"""
MiniCRM 合同模板数据模型

定义合同模板相关的数据结构和业务逻辑,包括:
- 合同模板基本信息模型
- 模板版本管理
- 模板内容和字段定义
- 数据验证和格式化

设计原则:
- 支持系统预设模板和用户自定义模板
- 提供模板版本控制功能
- 集成transfunctions进行数据验证
- 支持模板继承和扩展
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from transfunctions import ValidationError

from .base import NamedModel, register_model
from .contract import ContractType


class TemplateType(Enum):
    """模板类型枚举"""

    SYSTEM = "system"  # 系统预设模板
    USER = "user"  # 用户自定义模板
    SHARED = "shared"  # 共享模板


class TemplateStatus(Enum):
    """模板状态枚举"""

    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 激活
    ARCHIVED = "archived"  # 已归档
    DEPRECATED = "deprecated"  # 已弃用


@register_model
@dataclass
class ContractTemplate(NamedModel):
    """
    合同模板数据模型

    继承自NamedModel,包含合同模板的完整信息,包括模板内容、
    版本管理、使用统计等.
    """

    # 模板基本信息
    template_name: str = ""  # 模板名称
    template_type: TemplateType = TemplateType.USER
    template_status: TemplateStatus = TemplateStatus.DRAFT
    contract_type: ContractType = ContractType.SALES

    # 模板内容
    template_content: str = ""  # 模板内容(JSON格式存储字段定义)
    terms_template: str = ""  # 条款模板
    delivery_terms_template: str = ""  # 交付条款模板
    warranty_terms_template: str = ""  # 保修条款模板

    # 版本信息
    template_version: str = "1.0"  # 模板版本号(与基类version字段区分)
    parent_template_id: int | None = None  # 父模板ID(用于版本继承)
    is_latest_version: bool = True  # 是否为最新版本

    # 创建者信息
    created_by: str = ""  # 创建者
    last_modified_by: str = ""  # 最后修改者

    # 使用统计
    usage_count: int = 0  # 使用次数
    last_used_at: datetime | None = None  # 最后使用时间

    # 模板配置
    default_values: dict[str, Any] = field(default_factory=dict)  # 默认字段值
    required_fields: list[str] = field(default_factory=list)  # 必填字段列表
    field_validations: dict[str, str] = field(default_factory=dict)  # 字段验证规则

    def __post_init__(self):
        """初始化后处理"""
        # 清理字符串字段
        self.template_name = self.template_name.strip()
        self.template_content = self.template_content.strip()
        self.terms_template = self.terms_template.strip()
        self.delivery_terms_template = self.delivery_terms_template.strip()
        self.warranty_terms_template = self.warranty_terms_template.strip()
        self.created_by = self.created_by.strip()
        self.last_modified_by = self.last_modified_by.strip()

        # 初始化模板版本号
        if not self.template_version:
            self.template_version = "1.0"

        super().__post_init__()

    def validate(self) -> None:
        """验证模板数据"""
        super().validate()

        # 验证模板名称
        if not self.template_name:
            raise ValidationError("模板名称不能为空")

        if len(self.template_name) > 100:
            raise ValidationError("模板名称长度不能超过100个字符")

        # 验证模板版本号格式
        if not self._is_valid_version(self.template_version):
            raise ValidationError("模板版本号格式不正确,应为 x.y 格式")

        # 验证创建者
        if not self.created_by:
            raise ValidationError("创建者不能为空")

        # 验证使用次数
        if self.usage_count < 0:
            raise ValidationError("使用次数不能为负数")

        # 验证必填字段列表
        if self.required_fields and not isinstance(self.required_fields, list):
            raise ValidationError("必填字段列表必须是列表类型")

        # 验证默认值字典
        if self.default_values and not isinstance(self.default_values, dict):
            raise ValidationError("默认值必须是字典类型")

    def _is_valid_version(self, version: str) -> bool:
        """验证版本号格式"""
        try:
            parts = version.split(".")
            if len(parts) != 2:
                return False
            int(parts[0])
            int(parts[1])
            return True
        except (ValueError, AttributeError):
            return False

    def increment_usage(self) -> None:
        """增加使用次数"""
        self.usage_count += 1
        self.last_used_at = datetime.now()
        self.update_timestamp()

    def create_new_version(
        self, new_version: str, modified_by: str
    ) -> "ContractTemplate":
        """
        创建新版本模板

        Args:
            new_version: 新版本号
            modified_by: 修改者

        Returns:
            ContractTemplate: 新版本模板实例
        """
        if not self._is_valid_version(new_version):
            raise ValidationError("版本号格式不正确")

        # 将当前版本标记为非最新
        self.is_latest_version = False

        # 创建新版本
        new_template = ContractTemplate(
            template_name=self.template_name,
            template_type=self.template_type,
            template_status=TemplateStatus.DRAFT,
            contract_type=self.contract_type,
            template_content=self.template_content,
            terms_template=self.terms_template,
            delivery_terms_template=self.delivery_terms_template,
            warranty_terms_template=self.warranty_terms_template,
            template_version=new_version,
            parent_template_id=self.id,
            is_latest_version=True,
            created_by=self.created_by,
            last_modified_by=modified_by,
            default_values=self.default_values.copy(),
            required_fields=self.required_fields.copy(),
            field_validations=self.field_validations.copy(),
        )

        return new_template

    def activate_template(self) -> None:
        """激活模板"""
        if self.template_status == TemplateStatus.DEPRECATED:
            raise ValidationError("已弃用的模板无法激活")

        self.template_status = TemplateStatus.ACTIVE
        self.update_timestamp()

    def archive_template(self) -> None:
        """归档模板"""
        if self.template_status == TemplateStatus.DEPRECATED:
            raise ValidationError("已弃用的模板无法归档")

        self.template_status = TemplateStatus.ARCHIVED
        self.update_timestamp()

    def deprecate_template(self) -> None:
        """弃用模板"""
        self.template_status = TemplateStatus.DEPRECATED
        self.is_latest_version = False
        self.update_timestamp()

    def update_content(
        self,
        template_content: str | None = None,
        terms_template: str | None = None,
        delivery_terms_template: str | None = None,
        warranty_terms_template: str | None = None,
        modified_by: str = "",
    ) -> None:
        """
        更新模板内容

        Args:
            template_content: 模板内容
            terms_template: 条款模板
            delivery_terms_template: 交付条款模板
            warranty_terms_template: 保修条款模板
            modified_by: 修改者
        """
        if template_content is not None:
            self.template_content = template_content.strip()

        if terms_template is not None:
            self.terms_template = terms_template.strip()

        if delivery_terms_template is not None:
            self.delivery_terms_template = delivery_terms_template.strip()

        if warranty_terms_template is not None:
            self.warranty_terms_template = warranty_terms_template.strip()

        if modified_by:
            self.last_modified_by = modified_by.strip()

        self.update_timestamp()

    def set_default_value(self, field_name: str, value: Any) -> None:
        """设置字段默认值"""
        if not field_name:
            raise ValidationError("字段名不能为空")

        self.default_values[field_name] = value
        self.update_timestamp()

    def remove_default_value(self, field_name: str) -> None:
        """移除字段默认值"""
        if field_name in self.default_values:
            del self.default_values[field_name]
            self.update_timestamp()

    def add_required_field(self, field_name: str) -> None:
        """添加必填字段"""
        if not field_name:
            raise ValidationError("字段名不能为空")

        if field_name not in self.required_fields:
            self.required_fields.append(field_name)
            self.update_timestamp()

    def remove_required_field(self, field_name: str) -> None:
        """移除必填字段"""
        if field_name in self.required_fields:
            self.required_fields.remove(field_name)
            self.update_timestamp()

    def set_field_validation(self, field_name: str, validation_rule: str) -> None:
        """设置字段验证规则"""
        if not field_name:
            raise ValidationError("字段名不能为空")

        self.field_validations[field_name] = validation_rule
        self.update_timestamp()

    def remove_field_validation(self, field_name: str) -> None:
        """移除字段验证规则"""
        if field_name in self.field_validations:
            del self.field_validations[field_name]
            self.update_timestamp()

    def get_status_display(self) -> str:
        """获取状态显示文本"""
        status_map = {
            TemplateStatus.DRAFT: "草稿",
            TemplateStatus.ACTIVE: "激活",
            TemplateStatus.ARCHIVED: "已归档",
            TemplateStatus.DEPRECATED: "已弃用",
        }
        return status_map.get(self.template_status, "未知")

    def get_type_display(self) -> str:
        """获取类型显示文本"""
        type_map = {
            TemplateType.SYSTEM: "系统模板",
            TemplateType.USER: "用户模板",
            TemplateType.SHARED: "共享模板",
        }
        return type_map.get(self.template_type, "未知")

    def is_editable(self) -> bool:
        """检查模板是否可编辑"""
        # 系统模板不可编辑,已弃用的模板不可编辑
        return (
            self.template_type != TemplateType.SYSTEM
            and self.template_status != TemplateStatus.DEPRECATED
        )

    def is_usable(self) -> bool:
        """检查模板是否可使用"""
        return self.template_status in [TemplateStatus.ACTIVE, TemplateStatus.DRAFT]

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """转换为字典,包含格式化的字段"""
        data = super().to_dict(include_private)

        # 添加格式化字段
        data.update(
            {
                "status_display": self.get_status_display(),
                "type_display": self.get_type_display(),
                "contract_type_display": self.contract_type.value,
                "is_editable": self.is_editable(),
                "is_usable": self.is_usable(),
                "last_used_display": (
                    self.last_used_at.strftime("%Y-%m-%d %H:%M:%S")
                    if self.last_used_at
                    else ""
                ),
            }
        )

        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContractTemplate":
        """从字典创建模板实例"""
        # 处理枚举字段
        enum_fields = {
            "template_type": (TemplateType, TemplateType.USER),
            "template_status": (TemplateStatus, TemplateStatus.DRAFT),
            "contract_type": (ContractType, ContractType.SALES),
        }

        for field_name, (enum_class, default_value) in enum_fields.items():
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = enum_class(data[field_name])
                except ValueError:
                    data[field_name] = default_value

        # 处理日期字段
        if "last_used_at" in data and isinstance(data["last_used_at"], str):
            try:
                data["last_used_at"] = datetime.fromisoformat(data["last_used_at"])
            except ValueError:
                data["last_used_at"] = None

        # 处理字典和列表字段
        if "default_values" not in data or not isinstance(data["default_values"], dict):
            data["default_values"] = {}

        if "required_fields" not in data or not isinstance(
            data["required_fields"], list
        ):
            data["required_fields"] = []

        if "field_validations" not in data or not isinstance(
            data["field_validations"], dict
        ):
            data["field_validations"] = {}

        return super().from_dict(data)

    def __str__(self) -> str:
        """返回模板的字符串表示"""
        return (
            f"ContractTemplate(id={self.id}, name='{self.template_name}', "
            f"version={self.template_version}, status={self.template_status.value})"
        )
