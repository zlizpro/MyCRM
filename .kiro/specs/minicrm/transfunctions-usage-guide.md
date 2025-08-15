# MiniCRM Transfunctions 使用规范

## 📋 概述

本文档规定了在MiniCRM项目开发中使用transfunctions的标准和最佳实践。所有开发人员必须遵循这些规范，确保代码的一致性和可维护性。

## 🎯 核心原则

### 1. 优先使用原则
**在实现任何功能前，必须首先检查transfunctions是否已有相应函数。**

```python
# ❌ 错误：重复实现已有功能
def validate_phone(phone):
    if not phone:
        return True
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

# ✅ 正确：使用transfunctions
from ..transfunctions import validate_customer_data

def create_customer(self, data):
    validated_data = validate_customer_data(data)  # 包含电话验证
    return self._dao.create(validated_data)
```

### 2. 一致性原则
**使用统一的transfunctions确保整个项目的数据处理一致性。**

```python
# ✅ 正确：在所有地方使用相同的格式化函数
from ..transfunctions import format_currency, format_phone_number

# 在服务层
customer['credit_limit_formatted'] = format_currency(customer['credit_limit'])

# 在UI层
self.credit_label.setText(format_currency(credit_limit))

# 在报表中
report_data['total_credit'] = format_currency(total_credit)
```

### 3. 扩展性原则
**如需新功能，优先考虑扩展transfunctions而非创建独立实现。**

```python
# ✅ 正确：扩展transfunctions
# 在 minicrm/transfunctions/business_validation.py 中添加
def validate_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证产品数据"""
    validate_field(data, 'name', required=True, max_length=100)
    validate_field(data, 'price', required=True, data_type=(int, float), min_value=0)
    # ... 其他验证逻辑
    return data

# 然后在服务中使用
from ..transfunctions import validate_product_data
```

## 📚 模块使用指南

### 1. 业务验证模块 (business_validation)

**用途**: 验证业务实体数据，确保数据完整性和业务规则合规性。

**必须使用的场景**:
- 创建或更新客户、供应商、报价、合同等业务实体
- 表单数据验证
- API数据验证
- 批量数据导入验证

**使用示例**:
```python
from ..transfunctions import (
    validate_customer_data,
    validate_supplier_data,
    validate_quote_data,
    validate_batch_data
)

class CustomerService:
    def create_customer(self, customer_data):
        # 必须使用：业务验证
        validated_data = validate_customer_data(customer_data)
        return self._dao.create(validated_data)
    
    def batch_import_customers(self, customers_list):
        # 必须使用：批量验证
        validated_customers = validate_batch_data(
            customers_list, 
            validate_customer_data,
            "客户"
        )
        return [self._dao.create(customer) for customer in validated_customers]
```

### 2. 数据格式化模块 (data_form
*用途**: 统一数据显示格式，确保用户界面的一致性。

**必须使用的场景**:
- 货币金额显示
- 日期时间显示
- 电话号码显示
- 地址信息显示
- 联系信息显示

**使用示例**:
```python
from ..transfunctions import (
    format_currency,
    format_date,
    format_phone_number,
    format_contact_info
)

class CustomerPanel:
    def display_customer_info(self, customer):
        return {
            'name': customer['name'],
            'phone': format_phone_number(customer['phone']),  # 必须使用
            'credit_limit': format_currency(customer['credit_limit']),  # 必须使用
            'created_at': format_date(customer['created_at'], 'chinese'),  # 必须使用
            'contact_info': format_contact_info({  # 必须使用
                'contact_person': customer['contact_person'],
                'phone': customer['phone'],
                'email': customer['email']
            })
        }
```

### 3. 业务计算模块 (business_calculations)

**用途**: 执行业务相关的计算和分析。

**必须使用的场景**:
- 报价总额计算
- 客户价值评分
- 供应商绩效评分
- 增长率计算
- 趋势分析

**使用示例**:
```python
from ..transfunctions import (
    calculate_quote_total,
    calculate_customer_value_score,
    calculate_growth_rate
)

class QuoteService:
    def create_quote(self, quote_data):
        # 必须使用：报价计算
        calculation_result = calculate_quote_total(
            unit_price=quote_data['unit_price'],
            quantity=quote_data['quantity'],
            discount_rate=quote_data.get('discount_rate', 0),
            tax_rate=quote_data.get('tax_rate', 0.13)
        )
        
        quote_data.update(calculation_result)
        return self._dao.create(quote_data)

class CustomerAnalysisService:
    def analyze_customer_value(self, customer_id):
        customer = self._customer_dao.get_by_id(customer_id)
        transactions = self._transaction_dao.get_by_customer(customer_id)
        interactions = self._interaction_dao.get_by_customer(customer_id)
        
        # 必须使用：客户价值计算
        value_score = calculate_customer_value_score(
            customer_data=customer,
            transaction_history=transactions,
            interaction_history=interactions
        )
        
        return value_score
```

### 4. CRUD模板模块 (crud_templates)

**用途**: 标准化CRUD操作，减少重复代码。

**必须使用的场景**:
- 实现标准的创建、更新、删除操作
- 需要统一的验证和钩子处理
- 需要标准化的错误处理和日志记录

**使用示例**:
```python
from ..transfunctions import (
    crud_create_template,
    crud_update_template,
    crud_delete_template
)

class CustomerService:
    def __init__(self, dao):
        self._dao = dao
        
        # 必须使用：CRUD模板
        self._create_func = crud_create_template(
            dao_instance=dao,
            entity_type="客户",
            validation_config=self._get_validation_config(),
            pre_create_hook=self._pre_create_hook,
            post_create_hook=self._post_create_hook
        )
        
        self._update_func = crud_update_template(
            dao_instance=dao,
            entity_type="客户",
            validation_config=self._get_validation_config(),
            pre_update_hook=self._pre_update_hook,
            post_update_hook=self._post_update_hook
        )
    
    def create_customer(self, data):
        return self._create_func(data)
    
    def update_customer(self, customer_id, data):
        return self._update_func(customer_id, data)
```

### 5. 搜索模板模块 (search_templates)

**用途**: 标准化搜索和分页功能。

**必须使用的场景**:
- 实现分页搜索
- 高级搜索功能
- 聚合搜索

**使用示例**:
```python
from ..transfunctions import (
    paginated_search_template,
    advanced_search_template
)

class CustomerService:
    def search_customers_paginated(self, page, page_size, search_params):
        # 必须使用：分页搜索模板
        return paginated_search_template(
            dao_instance=self._dao,
            search_params=search_params,
            page=page,
            page_size=page_size,
            entity_type="客户"
        )
    
    def advanced_search_customers(self, search_config):
        # 必须使用：高级搜索模板
        return advanced_search_template(
            dao_instance=self._dao,
            search_config=search_config,
            entity_type="客户"
        )
```

### 6. 报表生成模块 (report_templates)

**用途**: 生成标准化的业务报表。

**必须使用的场景**:
- 客户分析报表
- 销售分析报表
- 供应商分析报表
- 仪表盘数据生成

**使用示例**:
```python
from ..transfunctions import (
    generate_customer_report,
    generate_sales_report,
    create_dashboard_summary
)

class ReportService:
    def generate_customer_analysis(self, report_config=None):
        customers = self._customer_dao.get_all()
        
        # 必须使用：客户报表生成
        return generate_customer_report(
            customer_data=customers,
            report_config=report_config or {}
        )
    
    def generate_dashboard_data(self):
        data_sources = {
            'customers': self._customer_dao.get_all(),
            'sales': self._sales_dao.get_recent_sales(),
            'suppliers': self._supplier_dao.get_all()
        }
        
        # 必须使用：仪表盘摘要生成
        return create_dashboard_summary(data_sources, {})
```

## 🚫 禁止的做法

### 1. 重复实现已有功能
```python
# ❌ 禁止：重复实现验证逻辑
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# ✅ 正确：使用transfunctions
from ..transfunctions import validate_customer_data
# validate_customer_data 内部已包含邮箱验证
```

### 2. 不一致的数据格式化
```python
# ❌ 禁止：在不同地方使用不同的格式化方式
# 在某个文件中
formatted_amount = f"¥{amount:,.2f}"

# 在另一个文件中
formatted_amount = f"￥{amount:.2f}"

# ✅ 正确：统一使用transfunctions
from ..transfunctions import format_currency
formatted_amount = format_currency(amount)
```

### 3. 绕过标准验证流程
```python
# ❌ 禁止：直接操作DAO而不验证
def create_customer_quick(self, name, phone):
    return self._dao.create({'name': name, 'phone': phone})

# ✅ 正确：使用标准验证流程
def create_customer(self, customer_data):
    validated_data = validate_customer_data(customer_data)
    return self._dao.create(validated_data)
```

## 📋 代码审查检查清单

在代码审查时，必须检查以下项目：

### 验证相关
- [ ] 是否使用了`validate_customer_data()`, `validate_supplier_data()`等业务验证函数
- [ ] 是否使用了`validate_batch_data()`进行批量验证
- [ ] 是否避免了重复实现验证逻辑

### 格式化相关
- [ ] 货币显示是否使用了`format_currency()`
- [ ] 日期显示是否使用了`format_date()`, `format_datetime()`
- [ ] 电话号码显示是否使用了`format_phone_number()`
- [ ] 联系信息显示是否使用了`format_contact_info()`

### 计算相关
- [ ] 报价计算是否使用了`calculate_quote_total()`
- [ ] 客户价值分析是否使用了`calculate_customer_value_score()`
- [ ] 增长率计算是否使用了`calculate_growth_rate()`

### CRUD相关
- [ ] 是否使用了`crud_create_template()`, `crud_update_template()`等模板
- [ ] 是否避免了重复的CRUD实现

### 搜索相关
- [ ] 分页搜索是否使用了`paginated_search_template()`
- [ ] 高级搜索是否使用了`advanced_search_template()`

### 报表相关
- [ ] 报表生成是否使用了相应的`generate_*_report()`函数
- [ ] 仪表盘数据是否使用了`create_dashboard_summary()`

### 文档处理相关
- [ ] Word文档生成是否使用了`generate_word_document()`
- [ ] PDF生成是否使用了`generate_pdf_report()`

### 导入导出相关
- [ ] 数据导入是否使用了`import_csv_data()`, `import_excel_data()`
- [ ] 数据导出是否使用了`export_csv_data()`, `export_excel_data()`

## 🔧 扩展Transfunctions

当需要扩展transfunctions时，请遵循以下步骤：

### 1. 评估必要性
- 功能是否具有通用性（会在2个以上地方使用）
- 是否符合现有模块的职责范围
- 是否有助于减少代码重复

### 2. 选择合适的模块
- **business_validation**: 数据验证相关
- **data_formatting**: 数据格式化相关
- **business_calculations**: 业务计算相关
- **crud_templates**: CRUD操作模板相关
- **search_templates**: 搜索功能相关
- **report_templates**: 报表生成相关
- **document_processing**: 文档处理相关
- **import_export**: 数据导入导出相关
- **notification_templates**: 通知模板相关

### 3. 实现新函数
```python
def new_function(
    param1: Type1,
    param2: Type2,
    logger: Optional[logging.Logger] = None
) -> ReturnType:
    """函数描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
        logger: 日志记录器
        
    Returns:
        返回值描述
        
    Raises:
        ExceptionType: 异常描述
        
    Example:
        >>> result = new_function(value1, value2)
        >>> print(result)
    """
    # 实现逻辑
    pass
```

### 4. 更新导出
在相应模块的`__init__.py`中添加导出：
```python
from .module_name import new_function

__all__ = [
    # ... 其他函数
    'new_function'
]
```

### 5. 编写测试
为新函数编写单元测试，确保功能正确性。

### 6. 更新文档
更新本文档和任务文档，添加新函数的使用说明。

## 📞 支持和反馈

如果在使用transfunctions过程中遇到问题：

1. **检查现有文档** - 查看函数的文档字符串和使用示例
2. **查看测试用例** - 参考测试文件中的使用方式
3. **提出改进建议** - 如果发现可以改进的地方，请提出建议

记住：transfunctions的目标是减少代码重复，提高开发效率，确保项目的一致性和可维护性。
