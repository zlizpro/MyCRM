"""
MiniCRM 基础数据模型

定义了所有数据模型的基础类和通用功能，包括：
- 基础模型类
- 数据验证机制
- 序列化和反序列化
- 通用字段类型
- 模型元数据管理
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from ..core import (
    ValidationError,
    clean_string,
    format_date,
)


# 泛型类型变量
T = TypeVar("T", bound="BaseModel")


class ModelStatus(Enum):
    """模型状态枚举"""

    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 非活跃
    DELETED = "deleted"  # 已删除
    DRAFT = "draft"  # 草稿


@dataclass
class BaseModel(ABC):
    """
    基础数据模型类

    所有业务模型都应该继承自这个基础类。
    提供通用的字段、验证和序列化功能。
    """

    # 基础字段
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    status: ModelStatus = ModelStatus.ACTIVE

    # 元数据字段
    version: int = 1
    notes: str = ""

    def __post_init__(self):
        """初始化后处理"""
        # 设置创建时间
        if self.created_at is None:
            self.created_at = datetime.now()

        # 设置更新时间
        if self.updated_at is None:
            self.updated_at = datetime.now()

        # 清理字符串字段
        self.notes = clean_string(self.notes)

        # 执行自定义验证
        self.validate()

    @abstractmethod
    def validate(self) -> None:
        """
        验证模型数据

        子类必须实现此方法来定义特定的验证规则。
        如果验证失败，应该抛出ValidationError异常。

        Raises:
            ValidationError: 当数据验证失败时
        """
        pass

    def is_valid(self) -> bool:
        """
        检查模型数据是否有效

        Returns:
            bool: 数据是否有效
        """
        try:
            self.validate()
            return True
        except ValidationError:
            return False

    def update_timestamp(self) -> None:
        """更新时间戳"""
        self.updated_at = datetime.now()
        self.version += 1

    def mark_as_deleted(self) -> None:
        """标记为已删除"""
        self.status = ModelStatus.DELETED
        self.update_timestamp()

    def is_deleted(self) -> bool:
        """检查是否已删除"""
        return self.status == ModelStatus.DELETED

    def is_active(self) -> bool:
        """检查是否活跃"""
        return self.status == ModelStatus.ACTIVE

    def to_dict(self, include_private: bool = False) -> dict[str, Any]:
        """
        将模型转换为字典

        Args:
            include_private: 是否包含私有字段（以_开头的字段）

        Returns:
            Dict[str, Any]: 模型数据字典
        """
        result = {}

        for key, value in self.__dict__.items():
            # 跳过私有字段（除非明确要求包含）
            if not include_private and key.startswith("_"):
                continue

            # 处理特殊类型
            if isinstance(value, datetime):
                result[key] = format_date(value, "%Y-%m-%d %H:%M:%S")
            elif isinstance(value, Enum):
                result[key] = value.value
            elif hasattr(value, "to_dict"):
                result[key] = value.to_dict()
            else:
                result[key] = value

        return result

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        从字典创建模型实例

        Args:
            data: 数据字典

        Returns:
            T: 模型实例

        Raises:
            ValidationError: 当数据无效时
        """
        # 过滤掉不存在的字段
        valid_fields = {key: value for key, value in data.items() if hasattr(cls, key)}

        # 处理特殊字段类型
        if "created_at" in valid_fields and isinstance(valid_fields["created_at"], str):
            try:
                valid_fields["created_at"] = datetime.fromisoformat(
                    valid_fields["created_at"]
                )
            except ValueError:
                valid_fields["created_at"] = None

        if "updated_at" in valid_fields and isinstance(valid_fields["updated_at"], str):
            try:
                valid_fields["updated_at"] = datetime.fromisoformat(
                    valid_fields["updated_at"]
                )
            except ValueError:
                valid_fields["updated_at"] = None

        if "status" in valid_fields and isinstance(valid_fields["status"], str):
            try:
                valid_fields["status"] = ModelStatus(valid_fields["status"])
            except ValueError:
                valid_fields["status"] = ModelStatus.ACTIVE

        return cls(**valid_fields)

    def copy(self: T, **changes: Any) -> T:
        """
        创建模型的副本

        Args:
            **changes: 要修改的字段

        Returns:
            T: 新的模型实例
        """
        data = self.to_dict()
        data.update(changes)

        # 重置ID和时间戳（创建新实例）
        data["id"] = None
        data["created_at"] = None
        data["updated_at"] = None
        data["version"] = 1

        return self.__class__.from_dict(data)

    def __str__(self) -> str:
        """返回模型的字符串表示"""
        class_name = self.__class__.__name__
        if hasattr(self, "name") and self.name:
            return f"{class_name}(id={self.id}, name='{self.name}')"
        else:
            return f"{class_name}(id={self.id})"

    def __repr__(self) -> str:
        """返回模型的详细表示"""
        class_name = self.__class__.__name__
        fields = []

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                if isinstance(value, str):
                    fields.append(f"{key}='{value}'")
                else:
                    fields.append(f"{key}={value}")

        return f"{class_name}({', '.join(fields)})"


@dataclass
class NamedModel(BaseModel):
    """
    带名称的基础模型

    为需要名称字段的模型提供基础实现。
    """

    name: str = ""
    description: str = ""

    def __post_init__(self):
        """初始化后处理"""
        # 清理字符串字段
        self.name = clean_string(self.name)
        self.description = clean_string(self.description)

        super().__post_init__()

    def validate(self) -> None:
        """验证模型数据"""
        if not self.name:
            raise ValidationError("名称不能为空")

        if len(self.name) > 100:
            raise ValidationError("名称长度不能超过100个字符")


@dataclass
class ContactModel(NamedModel):
    """
    联系信息基础模型

    为需要联系信息的模型提供基础实现。
    """

    phone: str = ""
    email: str = ""
    address: str = ""
    contact_person: str = ""

    def __post_init__(self):
        """初始化后处理"""
        # 清理字符串字段
        self.phone = clean_string(self.phone)
        self.email = clean_string(self.email)
        self.address = clean_string(self.address)
        self.contact_person = clean_string(self.contact_person)

        super().__post_init__()

    def validate(self) -> None:
        """验证联系信息"""
        super().validate()

        # 验证邮箱格式（如果提供了邮箱）
        if self.email and ("@" not in self.email or "." not in self.email):
            raise ValidationError("邮箱格式不正确")

        # 验证手机号格式（如果提供了手机号）
        if self.phone and len(self.phone) < 11:
            raise ValidationError("手机号格式不正确")


class ModelRegistry:
    """
    模型注册表

    管理所有已注册的模型类，提供模型发现和实例化功能。
    """

    _models: dict[str, type[BaseModel]] = {}

    @classmethod
    def register(cls, model_class: type[BaseModel]) -> None:
        """
        注册模型类

        Args:
            model_class: 要注册的模型类
        """
        cls._models[model_class.__name__] = model_class

    @classmethod
    def get_model(cls, name: str) -> type[BaseModel] | None:
        """
        获取模型类

        Args:
            name: 模型类名

        Returns:
            Optional[Type[BaseModel]]: 模型类或None
        """
        return cls._models.get(name)

    @classmethod
    def get_all_models(cls) -> dict[str, type[BaseModel]]:
        """
        获取所有已注册的模型

        Returns:
            Dict[str, Type[BaseModel]]: 模型名称到模型类的映射
        """
        return cls._models.copy()

    @classmethod
    def create_instance(cls, name: str, data: dict[str, Any]) -> BaseModel | None:
        """
        创建模型实例

        Args:
            name: 模型类名
            data: 数据字典

        Returns:
            Optional[BaseModel]: 模型实例或None
        """
        model_class = cls.get_model(name)
        if model_class:
            return model_class.from_dict(data)
        return None


# 模型装饰器
def register_model(model_class: type[BaseModel]) -> type[BaseModel]:
    """
    模型注册装饰器

    Args:
        model_class: 要注册的模型类

    Returns:
        Type[BaseModel]: 原模型类
    """
    ModelRegistry.register(model_class)
    return model_class
