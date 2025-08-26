# MiniCRM 导入导出架构文档

## 📋 架构概述

MiniCRM的导入导出功能采用分层架构设计，将原来的单一大文件拆分为多个专职服务，提高了代码的可维护性和可扩展性。

## 🏗️ 服务架构

```
ImportExportCoordinator (协调器)
├── FileValidator (文件验证)
├── DataImportService (数据导入)
└── DataExportService (数据导出)
```

### 1. ImportExportCoordinator (协调器服务)
**文件**: `src/minicrm/services/import_export_coordinator.py` (179行)
**职责**:
- 协调各个导入导出相关服务
- 提供统一的接口封装
- 管理服务间的依赖关系
- 统一的错误处理

**主要方法**:
- `get_supported_formats()` - 获取支持的文件格式
- `validate_import_file()` - 验证导入文件
- `preview_import_data()` - 预览导入数据
- `import_data()` - 导入数据
- `export_data()` - 导出数据
- `generate_word_document()` - 生成Word文档

### 2. FileValidator (文件验证服务)
**文件**: `src/minicrm/services/file_validator.py` (186行)
**职责**:
- 文件格式验证
- 文件大小检查
- CSV/Excel文件结构验证
- 编码格式检查

**主要方法**:
- `validate_import_file()` - 验证导入文件
- `validate_export_format()` - 验证导出格式
- `validate_output_path()` - 验证输出路径
- `_validate_csv_file()` - CSV文件验证
- `_validate_excel_file()` - Excel文件验证

### 3. DataImportService (数据导入服务)
**文件**: `src/minicrm/services/data_import_service.py` (355行)
**职责**:
- CSV/Excel数据读取
- 数据预览和字段映射
- 数据验证和批量导入
- 进度跟踪和错误处理

**主要方法**:
- `preview_import_data()` - 预览导入数据
- `import_data()` - 导入数据
- `get_field_mapping_suggestions()` - 获取字段映射建议
- `_map_fields()` - 字段映射和格式化
- `_import_mapped_data()` - 导入映射后的数据

### 4. DataExportService (数据导出服务)
**文件**: `src/minicrm/services/data_export_service.py` (276行)
**职责**:
- CSV/Excel数据导出
- PDF报表生成
- Word文档生成
- 数据筛选和格式化

**主要方法**:
- `export_data()` - 导出数据
- `generate_word_document()` - 生成Word文档
- `_export_csv()` - CSV格式导出
- `_export_excel()` - Excel格式导出
- `_export_pdf()` - PDF格式导出

## 🔧 Transfunctions集成

新架构充分利用了transfunctions库进行数据处理：

### 数据验证
```python
from transfunctions import validate_customer_data, validate_supplier_data

# 在DataImportService中使用
validation_result = validate_customer_data(row_data)
```

### 数据格式化
```python
from transfunctions import format_currency, format_date, format_phone

# 在字段映射时自动格式化
if target_field == "phone" and value:
    value = format_phone(str(value))
elif target_field in ["amount", "price", "total"] and value:
    value = format_currency(float(value))
elif target_field in ["date", "created_at", "updated_at"] and value:
    value = format_date(str(value))
```

## 📊 文件大小对比

| 服务                    | 行数  | 状态   | 标准           |
| ----------------------- | ----- | ------ | -------------- |
| 原始文件                | 632行 | ❌ 超标 | >600行强制限制 |
| FileValidator           | 186行 | ✅ 优秀 | ≤300行推荐     |
| DataImportService       | 355行 | ✅ 良好 | ≤450行警告阈值 |
| DataExportService       | 276行 | ✅ 优秀 | ≤300行推荐     |
| ImportExportCoordinator | 179行 | ✅ 优秀 | ≤300行推荐     |

## 🎯 使用示例

### 基本使用
```python
# 初始化协调器
coordinator = ImportExportCoordinator(
    customer_service, supplier_service, contract_service
)

# 验证文件
is_valid, error_msg = coordinator.validate_import_file("data.csv")

# 预览数据
headers, preview_data = coordinator.preview_import_data("data.csv", max_rows=5)

# 导入数据
field_mapping = {"name": "客户名称", "phone": "联系电话"}
success_count, error_count, errors = coordinator.import_data(
    "data.csv", "customers", field_mapping
)

# 导出数据
coordinator.export_data("customers", ".xlsx", "export.xlsx")
```

### 高级功能
```python
# 带筛选条件的导出
filters = {"query": "重要客户", "filters": {"type": "VIP"}}
coordinator.export_data("customers", ".pdf", "vip_customers.pdf", filters=filters)

# 生成Word文档
data = {"customer_name": "测试公司", "contract_amount": "100000"}
coordinator.generate_word_document("contract", data, "contract.docx")
```

## 🚀 优势

### 1. **可维护性提升**
- 单一职责原则：每个服务专注于特定功能
- 代码模块化：便于理解和修改
- 文件大小合理：符合MiniCRM开发标准

### 2. **可扩展性增强**
- 新增文件格式：只需修改对应服务
- 新增数据类型：扩展相应的验证和处理逻辑
- 新增导出格式：在DataExportService中添加

### 3. **代码质量提升**
- 类型安全：通过MyPy检查
- 代码规范：通过Ruff检查
- 异常处理：统一的错误处理机制

### 4. **性能优化**
- 按需加载：只初始化需要的服务
- 缓存机制：文件验证结果可缓存
- 批量处理：支持大数据量导入导出

## 📚 迁移指南

### 从原始ImportExportService迁移

**旧代码**:
```python
from minicrm.services.import_export_service import ImportExportService

service = ImportExportService(customer_service, supplier_service, contract_service)
service.import_data(file_path, data_type, field_mapping)
```

**新代码**:
```python
from minicrm.services.import_export_coordinator import ImportExportCoordinator

coordinator = ImportExportCoordinator(customer_service, supplier_service, contract_service)
coordinator.import_data(file_path, data_type, field_mapping)
```

### 接口兼容性
新架构保持了与原始接口的完全兼容性，只需要更改导入语句即可。

## 🔮 未来扩展

### 1. **异步处理**
- 大文件异步导入
- 后台任务队列
- 进度通知机制

### 2. **更多格式支持**
- JSON格式导入导出
- XML格式支持
- 自定义格式扩展

### 3. **高级功能**
- 数据转换规则引擎
- 模板化导出
- 数据质量检查

---

**总结**: 新的分层架构不仅解决了文件大小问题，还提升了代码质量、可维护性和可扩展性，为MiniCRM的长期发展奠定了坚实基础。
