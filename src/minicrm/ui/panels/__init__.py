"""MiniCRM TTK业务面板模块

包含所有业务面板的TTK实现:
- 客户管理面板
- 供应商管理面板
- 报价管理面板
- 合同管理面板
- 财务管理面板

设计原则:
- 使用TTK基础组件构建
- 遵循统一的面板设计模式
- 集成业务服务层
- 提供完整的用户交互功能
"""

from .customer_detail_ttk import CustomerDetailTTK
from .customer_edit_dialog_ttk import CustomerEditDialogTTK


__all__ = [
    "CustomerDetailTTK",
    "CustomerEditDialogTTK",
]
