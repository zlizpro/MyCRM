# Transfunctions使用情况报告

生成时间: /Users/zliz/MyCRM

## 检查总结

- 检查文件: 116 个
- 有问题文件: 10 个
- 重复函数: 25 个

## 需要修复的文件

### cell_formatter.py

🔄 替换重复实现的函数:
   第124行: format_cell_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第44行: format_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第68行: _format_currency()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency

   第82行: _format_percentage()
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage

   第89行: _format_date()
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date

   第98行: _format_datetime()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第104行: _format_phone()
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone

   第111行: _format_boolean()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第115行: _format_text()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number


### form_validator.py

🔄 替换重复实现的函数:
   第99行: validate_field()
      → 使用 transfunctions.validation.validate_customer_data
        理由: 验证函数应使用transfunctions.validation.validate_customer_data
      → 使用 transfunctions.validation.validate_supplier_data
        理由: 验证函数应使用transfunctions.validation.validate_supplier_data
      → 使用 transfunctions.validation.validate_email
        理由: 验证函数应使用transfunctions.validation.validate_email
      → 使用 transfunctions.validation.validate_phone
        理由: 验证函数应使用transfunctions.validation.validate_phone
      → 使用 transfunctions.validation.validate_required_fields
        理由: 验证函数应使用transfunctions.validation.validate_required_fields
      → 使用 transfunctions.validation.validate_data_types
        理由: 验证函数应使用transfunctions.validation.validate_data_types

   第132行: validate_form()
      → 使用 transfunctions.validation.validate_customer_data
        理由: 验证函数应使用transfunctions.validation.validate_customer_data
      → 使用 transfunctions.validation.validate_supplier_data
        理由: 验证函数应使用transfunctions.validation.validate_supplier_data
      → 使用 transfunctions.validation.validate_email
        理由: 验证函数应使用transfunctions.validation.validate_email
      → 使用 transfunctions.validation.validate_phone
        理由: 验证函数应使用transfunctions.validation.validate_phone
      → 使用 transfunctions.validation.validate_required_fields
        理由: 验证函数应使用transfunctions.validation.validate_required_fields
      → 使用 transfunctions.validation.validate_data_types
        理由: 验证函数应使用transfunctions.validation.validate_data_types


### base_dialog.py

📥 添加缺失的导入:
   from transfunctions.validation import *

🔄 替换重复实现的函数:
   第368行: validate_data()
      → 使用 transfunctions.validation.validate_customer_data
        理由: 验证函数应使用transfunctions.validation.validate_customer_data
      → 使用 transfunctions.validation.validate_supplier_data
        理由: 验证函数应使用transfunctions.validation.validate_supplier_data
      → 使用 transfunctions.validation.validate_email
        理由: 验证函数应使用transfunctions.validation.validate_email
      → 使用 transfunctions.validation.validate_phone
        理由: 验证函数应使用transfunctions.validation.validate_phone
      → 使用 transfunctions.validation.validate_required_fields
        理由: 验证函数应使用transfunctions.validation.validate_required_fields
      → 使用 transfunctions.validation.validate_data_types
        理由: 验证函数应使用transfunctions.validation.validate_data_types


### dashboard_refactored.py

📥 添加缺失的导入:
   from transfunctions.formatting import *

🔄 替换重复实现的函数:
   第388行: _format_metric_title()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第399行: _format_chart_title()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number


### form_panel_core.py

📥 添加缺失的导入:
   from transfunctions.validation import *

🔄 替换重复实现的函数:
   第270行: validate_form()
      → 使用 transfunctions.validation.validate_customer_data
        理由: 验证函数应使用transfunctions.validation.validate_customer_data
      → 使用 transfunctions.validation.validate_supplier_data
        理由: 验证函数应使用transfunctions.validation.validate_supplier_data
      → 使用 transfunctions.validation.validate_email
        理由: 验证函数应使用transfunctions.validation.validate_email
      → 使用 transfunctions.validation.validate_phone
        理由: 验证函数应使用transfunctions.validation.validate_phone
      → 使用 transfunctions.validation.validate_required_fields
        理由: 验证函数应使用transfunctions.validation.validate_required_fields
      → 使用 transfunctions.validation.validate_data_types
        理由: 验证函数应使用transfunctions.validation.validate_data_types


### table_pagination_manager.py

🔄 替换重复实现的函数:
   第187行: _calculate_total_pages()
      → 使用 transfunctions.calculations.calculate_customer_value_score
        理由: 计算函数应使用transfunctions.calculations.calculate_customer_value_score
      → 使用 transfunctions.calculations.calculate_quote_total
        理由: 计算函数应使用transfunctions.calculations.calculate_quote_total
      → 使用 transfunctions.calculations.calculate_pagination
        理由: 计算函数应使用transfunctions.calculations.calculate_pagination
      → 使用 transfunctions.calculations.calculate_age
        理由: 计算函数应使用transfunctions.calculations.calculate_age
      → 使用 transfunctions.calculations.calculate_discount
        理由: 计算函数应使用transfunctions.calculations.calculate_discount


### pagination_widget.py

🔄 替换重复实现的函数:
   第338行: _calculate_total_pages()
      → 使用 transfunctions.calculations.calculate_customer_value_score
        理由: 计算函数应使用transfunctions.calculations.calculate_customer_value_score
      → 使用 transfunctions.calculations.calculate_quote_total
        理由: 计算函数应使用transfunctions.calculations.calculate_quote_total
      → 使用 transfunctions.calculations.calculate_pagination
        理由: 计算函数应使用transfunctions.calculations.calculate_pagination
      → 使用 transfunctions.calculations.calculate_age
        理由: 计算函数应使用transfunctions.calculations.calculate_age
      → 使用 transfunctions.calculations.calculate_discount
        理由: 计算函数应使用transfunctions.calculations.calculate_discount

   第442行: _calculate_visible_pages()
      → 使用 transfunctions.calculations.calculate_customer_value_score
        理由: 计算函数应使用transfunctions.calculations.calculate_customer_value_score
      → 使用 transfunctions.calculations.calculate_quote_total
        理由: 计算函数应使用transfunctions.calculations.calculate_quote_total
      → 使用 transfunctions.calculations.calculate_pagination
        理由: 计算函数应使用transfunctions.calculations.calculate_pagination
      → 使用 transfunctions.calculations.calculate_age
        理由: 计算函数应使用transfunctions.calculations.calculate_age
      → 使用 transfunctions.calculations.calculate_discount
        理由: 计算函数应使用transfunctions.calculations.calculate_discount


### table_data_manager.py

📥 添加缺失的导入:
   from transfunctions.formatting import *

🔄 替换重复实现的函数:
   第273行: format_cell_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number


### metric_card.py

🔄 替换重复实现的函数:
   第271行: _format_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第300行: _format_currency_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第315行: _format_percentage_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第325行: _format_rating_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number

   第334行: _format_number_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number


### table_data_manager.py

🔄 替换重复实现的函数:
   第151行: _format_cell_value()
      → 使用 transfunctions.formatting.format_currency
        理由: 格式化函数应使用transfunctions.formatting.format_currency
      → 使用 transfunctions.formatting.format_phone
        理由: 格式化函数应使用transfunctions.formatting.format_phone
      → 使用 transfunctions.formatting.format_date
        理由: 格式化函数应使用transfunctions.formatting.format_date
      → 使用 transfunctions.formatting.format_address
        理由: 格式化函数应使用transfunctions.formatting.format_address
      → 使用 transfunctions.formatting.format_percentage
        理由: 格式化函数应使用transfunctions.formatting.format_percentage
      → 使用 transfunctions.formatting.format_number
        理由: 格式化函数应使用transfunctions.formatting.format_number


