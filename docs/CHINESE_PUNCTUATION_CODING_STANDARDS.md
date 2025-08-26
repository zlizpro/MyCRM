# 中文标点符号编码规范

## 概述

本文档规定了MiniCRM项目中关于标点符号使用的编码规范，旨在防止中文标点符号导致的语法错误和代码质量问题。

## 规范要求

### 1. 基本原则

- **所有Python代码中必须使用英文标点符号**
- **注释和文档字符串中的标点符号应使用英文标点符号**
- **字符串字面量中的标点符号根据业务需求决定**

### 2. 标点符号映射表

| 中文标点 | 英文标点 | 使用场景 | 示例 |
|---------|---------|---------|------|
| ，      | ,       | 参数分隔、列表分隔 | `def func(a, b, c):` |
| 。      | .       | 语句结束、属性访问 | `obj.method()` |
| ；      | ;       | 语句分隔 | `import os; import sys` |
| ：      | :       | 字典、函数定义、切片 | `def func():` |
| ？      | ?       | 三元运算符 | `x if condition else y` |
| ！      | !       | 逻辑非运算 | `not condition` |
| （      | (       | 函数调用、分组 | `func(args)` |
| ）      | )       | 函数调用、分组 | `func(args)` |
| 【      | [       | 列表、索引 | `list[0]` |
| 】      | ]       | 列表、索引 | `list[0]` |
| "       | "       | 字符串字面量 | `"hello world"` |
| '       | '       | 字符串字面量 | `'hello world'` |

### 3. 代码示例

#### ✅ 正确示例

```python
def create_customer(self, customer_data: dict[str, Any]) -> int:
    """创建新客户.

    Args:
        customer_data: 客户数据字典

    Returns:
        int: 新创建的客户ID

    Raises:
        ValidationError: 当数据验证失败时
    """
    if not customer_data.get("name"):
        raise ValidationError("客户名称不能为空")

    return self.create(customer_data)
```

#### ❌ 错误示例

```python
def create_customer(self，customer_data: dict[str，Any]) -> int：
    """创建新客户。

    Args：
        customer_data： 客户数据字典

    Returns：
        int： 新创建的客户ID

    Raises：
        ValidationError： 当数据验证失败时
    """
    if not customer_data.get（"name"）：
        raise ValidationError（"客户名称不能为空"）

    return self.create（customer_data）
```

### 4. 特殊情况处理

#### 4.1 用户界面文本

在用户界面显示的文本中，可以根据用户习惯使用中文标点符号：

```python
# 正确：UI显示文本可以使用中文标点
error_message = "客户名称不能为空，请输入有效的客户名称。"
success_message = "客户创建成功！"

# 但代码逻辑部分仍需使用英文标点
if not name:
    show_error(error_message)
    return False
```

#### 4.2 日志消息

日志消息建议使用英文标点符号，便于程序处理：

```python
# 推荐
self._logger.info("Customer created successfully: %s, ID: %s", name, customer_id)

# 不推荐
self._logger.info("客户创建成功：%s，ID：%s", name, customer_id)
```

### 5. 自动化检查

#### 5.1 Pre-commit Hook

项目已配置pre-commit hook来自动检查中文标点符号：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-chinese-punctuation
        name: Check Chinese Punctuation
        entry: python scripts/fix_chinese_punctuation.py
        language: system
        files: \.py$
```

#### 5.2 CI/CD集成

在持续集成流程中添加标点符号检查：

```bash
# 检查中文标点符号
python scripts/fix_chinese_punctuation.py src/minicrm/data/dao/*.py --check-only

# 如果发现问题，自动修复
python scripts/fix_chinese_punctuation.py src/minicrm/data/dao/*.py --fix
```

### 6. IDE配置

#### 6.1 VS Code配置

在VS Code中配置自动检测和提示：

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.ruffArgs": [
        "--select=RUF001,RUF002,RUF003"
    ]
}
```

#### 6.2 PyCharm配置

在PyCharm中启用相关检查：

1. 打开 Settings → Editor → Inspections
2. 启用 "Python → Code style issues → Non-ASCII characters in identifiers"
3. 启用 "Python → Probable bugs → Incorrect string literal"

### 7. 修复工具使用

#### 7.1 批量修复

使用项目提供的修复脚本：

```bash
# 修复单个文件
python scripts/fix_chinese_punctuation.py src/minicrm/data/dao/enhanced_customer_dao.py

# 批量修复多个文件
python scripts/fix_chinese_punctuation.py src/minicrm/data/dao/*.py

# 检查但不修复（仅报告）
python scripts/fix_chinese_punctuation.py src/minicrm/data/dao/*.py --check-only
```

#### 7.2 修复报告

修复工具会生成详细报告：

- 修复的文件数量
- 每个文件的修复详情
- 语法验证结果
- 错误和警告信息

### 8. 团队协作规范

#### 8.1 代码审查检查清单

在代码审查时，需要检查：

- [ ] 是否使用了中文标点符号
- [ ] 函数参数列表是否正确
- [ ] 字符串字面量是否符合规范
- [ ] 注释和文档字符串是否规范

#### 8.2 新人培训

新加入团队的开发者需要：

1. 阅读本编码规范文档
2. 配置IDE检查规则
3. 了解自动化修复工具的使用
4. 在第一次提交前运行完整检查

### 9. 常见问题解答

#### Q: 为什么要统一使用英文标点符号？

A:
- 避免语法错误和解析问题
- 保持代码风格一致性
- 便于自动化工具处理
- 提高代码可读性和维护性

#### Q: 用户界面文本是否也需要使用英文标点符号？

A: 不需要。用户界面显示的文本可以根据用户习惯使用中文标点符号，但代码逻辑部分仍需使用英文标点符号。

#### Q: 如何处理已有的中文标点符号？

A: 使用项目提供的自动化修复脚本进行批量修复，然后手动检查修复结果。

#### Q: 修复后如何验证代码正确性？

A:
1. 运行Python语法检查：`python -m py_compile file.py`
2. 运行代码质量检查：`python -m ruff check file.py`
3. 运行相关单元测试
4. 进行功能验证

### 10. 更新记录

| 版本 | 日期 | 更新内容 | 更新人 |
|------|------|----------|--------|
| 1.0 | 2025-01-19 | 初始版本，建立基本规范 | System |

---

**注意**: 本规范是强制性的，所有团队成员都必须遵守。违反规范的代码将不被接受合并到主分支。
