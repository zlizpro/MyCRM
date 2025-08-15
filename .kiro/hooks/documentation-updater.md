# 文档自动更新Hook

## Hook配置

**触发条件**: 当修改API接口、配置文件或重要功能时
**执行频率**: 每次保存相关文件
**适用文件**: `services/*.py`, `config/*.py`, `README.md`, `docs/*.md`

## Hook描述

这个hook会在您修改代码时自动检查和更新相关文档，确保文档与代码保持同步。

## 执行任务

1. **API文档检查**
   - 扫描服务类的公共方法
   - 检查方法签名是否有变更
   - 验证docstring是否完整和准确

2. **配置文档更新**
   - 检查配置项的变更
   - 更新配置说明和默认值
   - 验证配置示例的正确性

3. **功能文档同步**
   - 识别新增或修改的功能
   - 检查用户手册是否需要更新
   - 验证示例代码的有效性

4. **变更日志维护**
   - 记录重要的功能变更
   - 更新版本历史
   - 生成发布说明

## 文档类型

### API文档
- 自动生成方法签名和参数说明
- 更新返回值类型和异常信息
- 提供使用示例

### 用户文档
- 功能使用说明
- 配置指南
- 故障排除

### 开发文档
- 架构设计说明
- 代码贡献指南
- 测试指南

## 执行示例

检查以下文件的文档同步需求：
- `services/customer_service.py` → `docs/api/customer-service.md`
- `config/settings.py` → `docs/configuration.md`
- `ui/main_window.py` → `docs/user-guide/interface.md`

## 输出格式

```
📚 文档更新检查：

✅ 文档与代码同步

或

📝 发现以下文档需要更新：

1. API文档更新：
   - CustomerService.create_customer() 方法签名已变更
   - 新增参数：customer_type_id (int, optional)
   - 建议更新：docs/api/customer-service.md

2. 配置文档更新：
   - 新增配置项：DATABASE_BACKUP_INTERVAL
   - 默认值：24 (小时)
   - 建议更新：docs/configuration.md

3. 用户手册更新：
   - 新增客户类型管理功能
   - 需要添加操作说明和截图
   - 建议更新：docs/user-guide/customer-management.md

4. 变更日志：
   - 版本 1.2.0 的新功能记录
   - 建议更新：CHANGELOG.md
```

## 自动生成内容

对于API文档，可以自动生成以下内容：

```markdown
### create_customer(customer_data, customer_type_id=None)

创建新客户记录。

**参数：**
- `customer_data` (Dict[str, Any]): 客户基本信息
- `customer_type_id` (int, optional): 客户类型ID

**返回值：**
- `int`: 创建成功返回客户ID

**异常：**
- `ValidationError`: 客户数据验证失败
- `DatabaseError`: 数据库操作失败

**示例：**
```python
customer_data = {
    "name": "ABC公司",
    "phone": "138-1234-5678",
    "address": "上海市浦东新区..."
}
customer_id = service.create_customer(customer_data, customer_type_id=1)
```
```
