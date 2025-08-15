"""
MiniCRM 数据模型模块

包含应用程序的所有数据模型，包括：
- 基础模型类
- 客户相关模型
- 供应商相关模型
- 业务流程模型
- 财务相关模型

这个模块定义了应用程序中使用的所有数据结构和业务实体。
模型类负责数据的结构定义、验证和基本操作。
"""

# 版本信息
__version__ = "1.0.0"

# 导入基础模型类
from .base import (
    BaseModel,
    ContactModel,
    ModelRegistry,
    ModelStatus,
    NamedModel,
    register_model,
)
from .contract import Contract, ContractType
from .contract import ContractStatus as ContractStatusModel
from .contract import PaymentMethod as PaymentMethodModel

# 具体业务模型
from .customer import Customer, IndustryType
from .customer import CustomerLevel as CustomerLevelModel
from .customer import CustomerType as CustomerTypeModel
from .enums import (
    ContractStatus,
    Currency,
    CustomerLevel,
    CustomerType,
    DocumentType,
    EventType,
    Gender,
    InteractionStatus,
    InteractionType,
    NotificationType,
    PaymentMethod,
    PaymentStatus,
    ProductCategory,
    QualityGrade,
    QuoteStatus,
    SupplierLevel,
    SupplierType,
    TaskPriority,
    TaskStatus,
    UnitOfMeasure,
)
from .interaction import Interaction, PartyType, Priority
from .interaction import InteractionStatus as InteractionStatusModel
from .interaction import InteractionType as InteractionTypeModel
from .quote import Quote, QuoteItem, QuoteType
from .quote import QuoteStatus as QuoteStatusModel
from .supplier import QualityRating, Supplier, SupplierStatus
from .supplier import SupplierLevel as SupplierLevelModel
from .supplier import SupplierType as SupplierTypeModel


# 导出的公共接口
__all__ = [
    # 基础模型
    "BaseModel",
    "NamedModel",
    "ContactModel",
    "ModelRegistry",
    "ModelStatus",
    "register_model",
    # 枚举类型
    "CustomerLevel",
    "CustomerType",
    "SupplierLevel",
    "SupplierType",
    "InteractionType",
    "InteractionStatus",
    "ContractStatus",
    "QuoteStatus",
    "PaymentStatus",
    "PaymentMethod",
    "TaskStatus",
    "TaskPriority",
    "DocumentType",
    "EventType",
    "NotificationType",
    "Gender",
    "Currency",
    "ProductCategory",
    "QualityGrade",
    "UnitOfMeasure",
    # 具体业务模型
    "Customer",
    "CustomerLevelModel",
    "CustomerTypeModel",
    "IndustryType",
    "Supplier",
    "SupplierLevelModel",
    "SupplierStatus",
    "SupplierTypeModel",
    "QualityRating",
    "Contract",
    "ContractStatusModel",
    "ContractType",
    "PaymentMethodModel",
    "Quote",
    "QuoteItem",
    "QuoteStatusModel",
    "QuoteType",
    "Interaction",
    "InteractionStatusModel",
    "InteractionTypeModel",
    "Priority",
    "PartyType",
]
