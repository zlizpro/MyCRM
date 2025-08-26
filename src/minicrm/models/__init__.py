"""MiniCRM数据模型模块

定义系统中使用的所有数据模型和实体类.
"""

from .base import BaseModel, ModelStatus
from .quote import Quote, QuoteItem, QuoteStatus, QuoteType


__all__ = [
    "BaseModel",
    "ModelStatus",
    "Quote",
    "QuoteItem",
    "QuoteStatus",
    "QuoteType",
]
