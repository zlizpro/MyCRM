"""
MiniCRM 表单面板组件

重构后的表单面板，使用模块化设计。
为了保持向后兼容性，这里重新导出新的模块化组件。
"""

# 重新导出新的模块化组件
from .form.form_data_binder import FormDataBinder
from .form.form_field_factory import FieldType, FormFieldFactory
from .form.form_panel import FormPanel
from .form.form_validator import FormValidator, ValidationRule


# 保持向后兼容性
__all__ = [
    "FormPanel",
    "FieldType",
    "ValidationRule",
    "FormFieldFactory",
    "FormValidator",
    "FormDataBinder",
]
