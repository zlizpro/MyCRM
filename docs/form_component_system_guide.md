# TTK表单组件系统指南

## 概述

TTK表单组件系统是MiniCRM Qt到TTK重构项目的重要组成部分，提供了完整的表单构建、数据绑定、验证和管理功能。

## 系统架构

### 核心组件

1. **高级输入组件** (`advanced_input_components.py`)
   - `NumberSpinnerTTK`: 数字微调器组件
   - `ColorPickerTTK`: 颜色选择组件
   - `FilePickerTTK`: 文件选择组件
   - `DatePickerTTK`: 日期选择组件

2. **表单数据绑定** (`form_data_binding.py`)
   - `DataBinding`: 双向数据绑定类
   - `CommonFormatters`: 常用格式化器
   - `CommonParsers`: 常用解析器
   - `CommonValidators`: 常用验证器

3. **表单构建器** (`form_builder.py`)
   - `FormBuilderTTK`: 动态表单构建器

## 功能特性

### 高级输入组件

#### NumberSpinnerTTK
- 支持数值范围限制
- 可设置步长和小数位数
- 支持单位显示
- 鼠标滚轮操作支持

```python
spinner = NumberSpinnerTTK(
    parent,
    min_value=0,
    max_value=100,
    step=1,
    decimal_places=2,
    unit="元"
)
```

#### ColorPickerTTK
- RGB和HEX格式支持
- 颜色预览功能
- 预设颜色快选
- 颜色对话框集成

```python
color_picker = ColorPickerTTK(
    parent,
    preset_colors=["#FF0000", "#00FF00", "#0000FF"]
)
```

#### FilePickerTTK
- 文件类型过滤
- 单文件和多文件选择
- 文件信息获取
- 路径显示和清除

```python
file_picker = FilePickerTTK(
    parent,
    file_types=[("文本文件", "*.txt"), ("所有文件", "*.*")],
    multiple=False
)
```

#### DatePickerTTK
- 日历界面选择
- 日期格式化显示
- 日期范围限制
- 键盘输入支持

```python
date_picker = DatePickerTTK(
    parent,
    date_format="%Y-%m-%d",
    min_date=date(2020, 1, 1),
    max_date=date(2030, 12, 31)
)
```

### 表单数据绑定

#### 双向数据绑定
```python
binding = DataBinding()

# 绑定组件
binding.bind("username", entry_widget)

# 设置数据
binding.set_data("username", "张三")

# 获取数据
username = binding.get_data("username")
```

#### 数据格式化
```python
# 日期格式化
date_formatter = CommonFormatters.date_formatter("%Y-%m-%d")

# 数字格式化
number_formatter = CommonFormatters.number_formatter(2)

# 货币格式化
currency_formatter = CommonFormatters.currency_formatter("¥")
```

#### 数据验证
```python
# 必填验证
required_validator = CommonValidators.required_validator()

# 邮箱验证
email_validator = CommonValidators.email_validator()

# 电话验证
phone_validator = CommonValidators.phone_validator()

# 范围验证
range_validator = CommonValidators.range_validator(0, 100)
```

### 表单构建器

#### 动态表单生成
```python
fields = [
    {
        'id': 'name',
        'type': 'entry',
        'label': '姓名',
        'required': True
    },
    {
        'id': 'age',
        'type': 'number_spinner',
        'label': '年龄',
        'min_value': 0,
        'max_value': 120
    },
    {
        'id': 'email',
        'type': 'entry',
        'label': '邮箱',
        'format': 'email'
    }
]

form = FormBuilderTTK(parent, fields, columns=2)
```

#### 支持的字段类型
- `entry`: 文本输入框
- `text`: 多行文本框
- `combobox`: 下拉选择框
- `checkbox`: 复选框
- `radiobutton`: 单选按钮组
- `scale`: 滑块
- `spinbox`: 微调框
- `number_spinner`: 数字微调器
- `color_picker`: 颜色选择器
- `file_picker`: 文件选择器
- `date_picker`: 日期选择器

#### 表单操作
```python
# 设置表单数据
form.set_form_data({
    'name': '张三',
    'age': 25,
    'email': 'zhangsan@example.com'
})

# 获取表单数据
data = form.get_form_data()

# 验证表单
is_valid, errors = form.validate_form()

# 清空表单
form.clear_form()

# 字段操作
form.set_field_value('name', '李四')
form.set_field_enabled('email', False)
form.set_field_visible('age', False)
```

#### 事件处理
```python
def on_form_submit(data):
    print("表单提交:", data)

def on_form_reset():
    print("表单重置")

form.add_event_handler("form_submit", on_form_submit)
form.add_event_handler("form_reset", on_form_reset)
```

## 使用示例

### 客户信息表单
```python
import tkinter as tk
from minicrm.ui.ttk_base.form_builder import FormBuilderTTK

# 定义字段
fields = [
    {
        'id': 'company_name',
        'type': 'entry',
        'label': '公司名称',
        'required': True
    },
    {
        'id': 'contact_person',
        'type': 'entry',
        'label': '联系人',
        'required': True
    },
    {
        'id': 'phone',
        'type': 'entry',
        'label': '联系电话',
        'format': 'phone',
        'required': True
    },
    {
        'id': 'email',
        'type': 'entry',
        'label': '邮箱地址',
        'format': 'email'
    },
    {
        'id': 'customer_type',
        'type': 'combobox',
        'label': '客户类型',
        'options': ['生态板客户', '家具板客户', '阻燃板客户']
    },
    {
        'id': 'credit_limit',
        'type': 'number_spinner',
        'label': '信用额度',
        'min_value': 0,
        'max_value': 1000000,
        'decimal_places': 2,
        'unit': '元'
    },
    {
        'id': 'established_date',
        'type': 'date_picker',
        'label': '成立日期'
    },
    {
        'id': 'address',
        'type': 'text',
        'label': '详细地址',
        'height': 3
    }
]

# 创建表单
root = tk.Tk()
form = FormBuilderTTK(root, fields, columns=2)
form.pack(fill=tk.BOTH, expand=True)

# 事件处理
def handle_submit(data):
    print("客户信息:", data)

form.add_event_handler("form_submit", handle_submit)

root.mainloop()
```

## 最佳实践

### 字段定义规范
1. **必填字段标识**: 使用 `required: True` 标识必填字段
2. **数据格式**: 使用 `format` 属性指定数据格式（email、phone、currency等）
3. **验证规则**: 合理设置验证规则，提供友好的错误提示
4. **字段分组**: 使用合适的列数进行字段分组布局

### 数据绑定建议
1. **自动同步**: 对于实时性要求高的字段启用 `auto_sync`
2. **格式化器**: 为日期、数字、货币等字段设置合适的格式化器
3. **验证器**: 组合使用多个验证器实现复杂验证逻辑
4. **监听器**: 使用数据变化监听器实现字段间的联动

### 性能优化
1. **延迟加载**: 对于复杂表单考虑分页或延迟加载
2. **虚拟滚动**: 使用滚动框架处理长表单
3. **事件节流**: 避免频繁的数据同步操作
4. **资源清理**: 及时清理不需要的事件监听器和数据绑定

## 扩展开发

### 自定义输入组件
```python
class CustomInputTTK(BaseWidget, AdvancedInputMixin):
    def __init__(self, parent, **kwargs):
        AdvancedInputMixin.__init__(self)
        super().__init__(parent, **kwargs)

    def _setup_ui(self):
        # 实现自定义UI
        pass

    def _update_display(self):
        # 实现显示更新
        pass
```

### 自定义验证器
```python
def custom_validator(value):
    # 实现自定义验证逻辑
    return True  # 或 False

# 使用自定义验证器
field = {
    'id': 'custom_field',
    'type': 'entry',
    'label': '自定义字段',
    'validator': custom_validator
}
```

### 自定义格式化器
```python
def custom_formatter(value):
    # 实现自定义格式化逻辑
    return str(value)

# 使用自定义格式化器
field = {
    'id': 'custom_field',
    'type': 'entry',
    'label': '自定义字段',
    'formatter': custom_formatter
}
```

## 总结

TTK表单组件系统提供了完整的表单解决方案，支持：

1. **丰富的输入组件**: 满足各种数据输入需求
2. **强大的数据绑定**: 简化数据管理和同步
3. **灵活的验证机制**: 确保数据质量和用户体验
4. **动态表单构建**: 支持配置化的表单生成
5. **良好的扩展性**: 支持自定义组件和功能扩展

该系统为MiniCRM的Qt到TTK重构提供了坚实的基础，确保了表单功能的完整性和用户体验的一致性。
