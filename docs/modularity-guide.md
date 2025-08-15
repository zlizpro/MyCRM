# MiniCRM 模块化开发指南

## 📋 概述

本指南详细说明了MiniCRM项目的模块化开发标准和最佳实践。通过遵循这些标准，我们确保代码的可维护性、可复用性和长期演进能力。

## 🎯 核心原则

### 1. 文件大小控制
- **硬性限制**: 单个Python文件不得超过200行代码
- **警告阈值**: 文件超过150行时必须考虑拆分
- **函数限制**: 单个函数不得超过50行代码
- **类限制**: 单个类不得超过100行代码

### 2. transfunctions强制使用
- 开发任何功能前，必须先检查transfunctions中是否有可用函数
- 禁止重复实现transfunctions中已有的功能
- 新的通用功能必须添加到transfunctions中供复用

### 3. 分层架构约束
```
UI层 (ui/)
├── 可以导入: services, models, core, transfunctions
└── 禁止导入: data

业务逻辑层 (services/)
├── 可以导入: data, models, core, transfunctions
└── 禁止导入: ui

数据访问层 (data/)
├── 可以导入: models, core, transfunctions
└── 禁止导入: ui, services

数据模型层 (models/)
├── 可以导入: core, transfunctions
└── 禁止导入: ui, services, data

核心工具层 (core/)
├── 可以导入: 无
└── 禁止导入: 所有业务层

可复用函数库 (transfunctions/)
├── 可以导入: 无
└── 禁止导入: minicrm相关模块
```

## 🛠️ 开发工具

### 模块化质量检查工具

我们提供了自动化的质量检查工具来确保代码符合标准：

```bash
# 检查单个文件
python scripts/modularity_check.py src/minicrm/services/customer_service.py

# 检查整个项目
python scripts/modularity_check.py --all

# 检查当前目录
python scripts/modularity_check.py .
```

### Git集成

项目已配置了Git pre-commit hook，会在每次提交前自动检查代码质量：

```bash
# 提交代码时会自动运行检查
git add .
git commit -m "实现客户管理功能"
# 如果检查失败，提交会被阻止
```

### IDE集成

推荐在IDE中配置自动检查：

#### VS Code配置
在`.vscode/settings.json`中添加：
```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.mypyEnabled": true,
    "files.associations": {
        "*.py": "python"
    },
    "python.formatting.provider": "black"
}
```

## 📝 编码规范

### 文件结构模板

每个Python文件应遵循以下结构：

```python
"""
模块文档字符串

简要描述模块的功能和用途。
"""

# 标准库导入
import os
import sys
from typing import Dict, List, Optional

# 第三方库导入
from pydantic import BaseModel

# 项目内导入
from minicrm.core.exceptions import MiniCRMError
from transfunctions.validation import validate_email


class ExampleClass:
    """示例类

    详细描述类的功能和用途。

    Attributes:
        attribute_name: 属性描述
    """

    def __init__(self, param: str):
        """初始化方法

        Args:
            param: 参数描述
        """
        self.attribute_name = param

    def public_method(self, arg: str) -> str:
        """公共方法

        Args:
            arg: 参数描述

        Returns:
            返回值描述

        Raises:
            MiniCRMError: 错误描述
        """
        # 使用transfunctions中的函数
        if not validate_email(arg):
            raise MiniCRMError("无效的邮箱地址")

        return self._private_method(arg)

    def _private_method(self, arg: str) -> str:
        """私有方法

        Args:
            arg: 参数描述

        Returns:
            返回值描述
        """
        return f"processed_{arg}"


def utility_function(param: str) -> bool:
    """工具函数

    Args:
        param: 参数描述

    Returns:
        返回值描述
    """
    return len(param) > 0
```

### 类设计原则

#### 单一职责原则
每个类只负责一个明确的业务概念：

```python
# ✅ 好的设计 - 单一职责
class Customer:
    """客户数据模型"""
    pass

class CustomerValidator:
    """客户数据验证器"""
    pass

class CustomerService:
    """客户业务逻辑服务"""
    pass

# ❌ 不好的设计 - 职责混乱
class CustomerManager:
    """既包含数据模型，又包含业务逻辑和验证"""
    pass
```

#### 依赖注入
通过构造函数注入依赖，而不是硬编码：

```python
# ✅ 好的设计 - 依赖注入
class CustomerService:
    def __init__(self, customer_dao: CustomerDAO, validator: CustomerValidator):
        self._customer_dao = customer_dao
        self._validator = validator

# ❌ 不好的设计 - 硬编码依赖
class CustomerService:
    def __init__(self):
        self._customer_dao = CustomerDAO()  # 硬编码依赖
        self._validator = CustomerValidator()  # 硬编码依赖
```

### 函数设计原则

#### 函数大小控制
将大函数拆分为多个小函数：

```python
# ✅ 好的设计 - 小函数
def create_customer(self, customer_data: Dict[str, Any]) -> int:
    """创建客户"""
    self._validate_customer_data(customer_data)
    customer_id = self._save_customer_data(customer_data)
    self._create_default_interactions(customer_id)
    self._send_welcome_notification(customer_id)
    return customer_id

def _validate_customer_data(self, data: Dict[str, Any]) -> None:
    """验证客户数据"""
    # 验证逻辑

def _save_customer_data(self, data: Dict[str, Any]) -> int:
    """保存客户数据"""
    # 保存逻辑

# ❌ 不好的设计 - 大函数
def create_customer(self, customer_data: Dict[str, Any]) -> int:
    """创建客户 - 包含所有逻辑的大函数"""
    # 50+ 行的复杂逻辑
    pass
```

## 🔄 transfunctions使用指南

### 必须使用transfunctions的场景

1. **数据验证**
```python
# ✅ 使用transfunctions
from transfunctions.validation import validate_customer_data

def create_customer(self, data: Dict[str, Any]) -> int:
    validate_customer_data(data)  # 使用可复用函数
    # ...

# ❌ 重复实现
def create_customer(self, data: Dict[str, Any]) -> int:
    if not data.get('name'):  # 重复的验证逻辑
        raise ValueError("客户名称不能为空")
    # ...
```

2. **数据格式化**
```python
# ✅ 使用transfunctions
from transfunctions.formatting import format_currency, format_phone

def display_customer_info(self, customer: Customer) -> str:
    return f"客户: {customer.name}, 电话: {format_phone(customer.phone)}"

# ❌ 重复实现
def display_customer_info(self, customer: Customer) -> str:
    # 重复的格式化逻辑
    formatted_phone = f"{customer.phone[:3]}-{customer.phone[3:7]}-{customer.phone[7:]}"
    return f"客户: {customer.name}, 电话: {formatted_phone}"
```

3. **业务计算**
```python
# ✅ 使用transfunctions
from transfunctions.calculations import calculate_customer_value_score

def analyze_customer(self, customer_id: int) -> Dict[str, Any]:
    score = calculate_customer_value_score(customer_id)
    # ...

# ❌ 重复实现
def analyze_customer(self, customer_id: int) -> Dict[str, Any]:
    # 重复的计算逻辑
    score = self._calculate_complex_score(customer_id)
    # ...
```

### 扩展transfunctions

当需要新的通用功能时，应该添加到transfunctions中：

```python
# 在 src/transfunctions/validation.py 中添加新函数
def validate_supplier_data(data: Dict[str, Any]) -> None:
    """验证供应商数据

    Args:
        data: 供应商数据字典

    Raises:
        ValidationError: 数据验证失败时
    """
    if not data.get('name'):
        raise ValidationError("供应商名称不能为空")

    if not data.get('contact_phone'):
        raise ValidationError("联系电话不能为空")

    # 更多验证逻辑...
```

## 🚨 常见问题和解决方案

### 问题1: 文件过大
**现象**: 检查工具报告文件超过200行

**解决方案**:
1. 按功能拆分文件
2. 提取公共逻辑到transfunctions
3. 将复杂类拆分为多个小类

```python
# 拆分前: customer_service.py (250行)
class CustomerService:
    # 250行代码

# 拆分后:
# customer_service.py (80行)
class CustomerService:
    # 核心业务逻辑

# customer_validator.py (60行)
class CustomerValidator:
    # 验证逻辑

# customer_analyzer.py (70行)
class CustomerAnalyzer:
    # 分析逻辑
```

### 问题2: 架构违规
**现象**: UI层直接导入data层模块

**解决方案**: 通过services层进行访问

```python
# ❌ 违规: UI直接访问data层
from minicrm.data.customer_dao import CustomerDAO

class CustomerPanel:
    def __init__(self):
        self.customer_dao = CustomerDAO()  # 违规

# ✅ 正确: 通过services层访问
from minicrm.services.customer_service import CustomerService

class CustomerPanel:
    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service  # 正确
```

### 问题3: 重复代码
**现象**: 多个地方实现相同的逻辑

**解决方案**: 提取到transfunctions或公共模块

```python
# ❌ 重复代码
# 在多个文件中都有相同的验证逻辑
def validate_phone(phone: str) -> bool:
    return len(phone) == 11 and phone.isdigit()

# ✅ 提取到transfunctions
# src/transfunctions/validation.py
def validate_phone(phone: str) -> bool:
    """验证电话号码格式"""
    return len(phone) == 11 and phone.isdigit()

# 在需要的地方导入使用
from transfunctions.validation import validate_phone
```

## 📊 质量监控

### 健康度指标

项目维护以下质量指标：

- **文件大小合规率**: 目标 > 95%
- **函数大小合规率**: 目标 > 90%
- **类大小合规率**: 目标 > 90%
- **架构合规率**: 目标 > 98%
- **transfunctions使用率**: 目标 > 80%
- **代码重复率**: 目标 < 5%

### 持续改进

1. **每日检查**: 运行质量检查工具
2. **每周回顾**: 分析质量趋势
3. **每月重构**: 处理技术债务
4. **季度评估**: 更新标准和工具

## 🎓 最佳实践总结

1. **开发前检查**: 先查看transfunctions是否有可用函数
2. **小步迭代**: 保持文件和函数的小尺寸
3. **单一职责**: 每个模块、类、函数只做一件事
4. **依赖注入**: 避免硬编码依赖关系
5. **分层架构**: 严格遵循架构约束
6. **自动检查**: 依赖工具而不是人工检查
7. **持续重构**: 定期清理和优化代码

通过遵循这些原则和使用提供的工具，我们可以确保MiniCRM项目始终保持高质量的模块化代码结构。
