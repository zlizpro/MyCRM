# 代码质量配置说明

## 🎯 配置理念

MiniCRM项目提供了两套代码质量配置：

1. **标准模式** (`pyproject.toml`) - 适合生产环境和代码审查
2. **宽松模式** (`pyproject-dev.toml`) - 适合开发阶段和快速迭代

## 📋 配置对比

### Ruff 规则对比

| 规则类别         | 标准模式 | 宽松模式 | 说明                         |
| ---------------- | -------- | -------- | ---------------------------- |
| 语法错误 (E, F)  | ✅        | ✅        | 基础语法检查，两种模式都启用 |
| 导入排序 (I)     | ✅        | ✅        | 保持代码整洁                 |
| 代码风格 (W)     | ✅        | ❌        | 标准模式检查代码风格         |
| 文档字符串 (D)   | ❌        | ❌        | 两种模式都暂时禁用           |
| 类型注解 (ANN)   | ❌        | ❌        | 渐进式添加类型注解           |
| 复杂度检查 (PLR) | ❌        | ❌        | 重构阶段再严格要求           |
| 安全检查 (S)     | 部分     | ❌        | 标准模式保留基础安全检查     |
| 性能优化 (PERF)  | ❌        | ❌        | 避免过早优化                 |

### MyPy 配置对比

| 检查项     | 标准模式 | 宽松模式 | 说明                 |
| ---------- | -------- | -------- | -------------------- |
| 类型检查   | 宽松     | 跳过     | 渐进式类型检查       |
| 未标注函数 | 允许     | 忽略     | 不强制要求类型注解   |
| 第三方库   | 忽略     | 忽略     | 避免第三方库类型问题 |
| 错误显示   | 显示     | 隐藏     | 开发时减少干扰       |

## 🚀 使用方法

### 开发阶段（推荐宽松模式）

```bash
# 使用宽松模式检查
make check-relaxed

# 或者直接使用环境变量
RELAXED_MODE=true ./scripts/check-code.sh

# 宽松模式linting
make lint-relaxed

# 自动修复（宽松模式）
make lint-fix-relaxed
```

### 提交前（使用标准模式）

```bash
# 标准模式检查
make check

# 标准模式linting
make lint

# 自动修复
make lint-fix
```

### CI/CD（使用标准模式）

```bash
# 在CI中使用标准配置
uv run ruff check src/ tests/
uv run mypy src/
```

## ⚙️ 自定义配置

### 临时禁用规则

在代码中使用注释临时禁用规则：

```python
# ruff: noqa: E501  # 忽略行长度限制
very_long_line = "这是一行很长的代码..."

# type: ignore  # 忽略MyPy类型检查
result = some_untyped_function()
```

### 文件级别禁用

在文件顶部添加：

```python
# ruff: noqa
# type: ignore

# 这个文件跳过所有检查
```

### 项目级别配置

修改 `pyproject.toml` 中的 `ignore` 列表：

```toml
[tool.ruff.lint]
ignore = [
    "E501",  # 行长度限制
    "D100",  # 缺少模块文档字符串
    # 添加你想忽略的规则
]
```

## 🎛️ 环境变量控制

### 代码检查脚本

```bash
# 宽松模式
export RELAXED_MODE=true
./scripts/check-code.sh

# 跳过特定检查
export SKIP_MYPY=true
export SKIP_SECURITY=true
./scripts/check-code.sh
```

### 性能配置

```bash
# 开发环境
export MINICRM_ENV=development

# 生产环境
export MINICRM_ENV=production
```

## 📊 覆盖率要求

### 测试覆盖率

- **开发阶段**: 60% (宽松要求)
- **生产发布**: 80% (严格要求)

```bash
# 检查当前覆盖率
uv run pytest --cov=src --cov-report=term-missing

# 生成HTML报告
uv run pytest --cov=src --cov-report=html
```

### 文档覆盖率

- **开发阶段**: 不强制要求
- **生产发布**: 60%

```bash
# 检查文档覆盖率
uv run interrogate src/
```

## 🔧 常见问题

### Q: 为什么要有两套配置？

A: 开发阶段需要快速迭代，过于严格的规则会影响开发效率。生产阶段需要高质量代码，严格的规则有助于发现潜在问题。

### Q: 什么时候使用哪种模式？

A:

- **宽松模式**: 日常开发、原型开发、快速迭代
- **标准模式**: 代码审查、提交前检查、CI/CD

### Q: 如何逐步提升代码质量？

A:

1. 开发时使用宽松模式
2. 定期运行标准模式检查
3. 逐步修复标准模式的问题
4. 最终在CI中使用标准模式

### Q: 可以完全禁用某些检查吗？

A: 可以，但不推荐。建议使用宽松模式而不是完全禁用。

## 📈 质量提升路径

### 阶段1: 基础质量（当前）

- 语法正确性
- 导入整理
- 基础格式化

### 阶段2: 代码规范

- 添加类型注解
- 完善文档字符串
- 遵循命名规范

### 阶段3: 高级质量

- 复杂度控制
- 安全检查
- 性能优化

### 阶段4: 生产就绪

- 完整测试覆盖
- 全面文档
- 严格类型检查

## 🎯 建议工作流

```bash
# 1. 开发阶段 - 使用宽松模式
make check-relaxed

# 2. 功能完成 - 自动修复
make format
make lint-fix

# 3. 提交前 - 标准检查
make check

# 4. 如果标准检查失败，逐步修复或使用宽松模式
RELAXED_MODE=true make check
```

这样的配置既保证了代码质量，又不会过度影响开发效率！
