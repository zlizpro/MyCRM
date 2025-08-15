# MiniCRM 代码质量检查Hook

## 🎯 功能概述

这是MiniCRM项目的第一个自动执行Hook，提供实时的Python代码质量检查功能。当您保存Python文件时，系统会自动检查代码质量并提供改进建议。

## ✨ 主要特性

### 🔍 全面的质量检查
- **PEP8风格检查** - 确保代码符合Python编码规范
- **类型注解验证** - 检查函数参数和返回值的类型注解
- **文档字符串检查** - 确保类和函数有适当的文档说明
- **导入语句规范** - 检查导入顺序和未使用的导入
- **命名规范检查** - 验证类名、函数名、变量名的命名规范
- **代码复杂度分析** - 识别过于复杂的函数

### 🔧 智能自动修复
- **自动格式化** - 修复代码格式问题
- **导入优化** - 移除未使用的导入，优化导入顺序
- **命名规范修复** - 自动转换不规范的命名
- **类型注解生成** - 为缺少类型注解的函数添加基础注解
- **文档字符串生成** - 为缺少文档的函数生成基础文档模板

### 📊 详细的问题报告
- **分级问题显示** - 错误、警告、信息三个级别
- **具体位置定位** - 精确到行号和列号
- **改进建议** - 每个问题都提供具体的修复建议
- **批量处理** - 支持同时检查多个文件

## 🚀 快速开始

### 1. 激活Hook
```bash
# 进入项目根目录
cd your-minicrm-project

# 运行激活脚本
bash .kiro/hooks/scripts/activate.sh
```

### 2. 测试功能
```bash
# 手动测试代码质量检查
python3 .kiro/hooks/scripts/kiro_integration.py test .kiro/hooks/scripts/test_sample.py
```

### 3. 在IDE中使用
- 保存任意Python文件，自动触发质量检查
- 查看问题面板中的检查结果
- 右键选择文件，选择"检查代码质量"进行手动检查

## 📁 文件结构

```
.kiro/hooks/scripts/
├── code_quality_checker.py    # 核心质量检查器
├── kiro_integration.py        # Kiro IDE集成脚本
├── quality_config.json        # 质量检查配置
├── activate_hook.py           # Hook激活脚本
├── test_sample.py            # 测试样例文件
├── activate.sh               # 一键激活脚本
└── README.md                 # 使用说明（本文件）
```

## ⚙️ 配置说明

### 基础配置 (`quality_config.json`)
```json
{
  "check_pep8": true,              // 启用PEP8检查
  "check_type_hints": true,        // 启用类型注解检查
  "check_docstrings": true,        // 启用文档字符串检查
  "check_imports": true,           // 启用导入语句检查
  "max_line_length": 88,           // 最大行长度
  "complexity_threshold": 10       // 复杂度阈值
}
```

### 自定义规则
```json
{
  "severity_levels": {
    "syntax_error": "error",       // 语法错误级别
    "unused_import": "warning",    // 未使用导入级别
    "missing_docstring": "info"    // 缺少文档级别
  },
  "auto_fix_rules": {
    "unused_import": true,         // 自动修复未使用导入
    "line_too_long": true,         // 自动修复长行
    "naming_convention": true      // 自动修复命名规范
  }
}
```

## 🎨 检查示例

### 输入代码
```python
class customerManager:  # 命名不规范
    def addCustomer(self, data):  # 缺少类型注解和文档
        pass
```

### 检查结果
```json
{
  "issues": [
    {
      "line_number": 1,
      "issue_type": "naming_convention",
      "severity": "warning",
      "message": "类名 'customerManager' 应使用大驼峰命名法",
      "suggestion": "建议改为: CustomerManager",
      "auto_fixable": true
    },
    {
      "line_number": 2,
      "issue_type": "missing_type_hint",
      "severity": "info", 
      "message": "参数 'data' 缺少类型注解",
      "suggestion": "为参数 'data' 添加类型注解",
      "auto_fixable": true
    }
  ]
}
```

## 🔧 高级用法

### 命令行使用
```bash
# 检查单个文件
python3 .kiro/hooks/scripts/code_quality_checker.py your_file.py

# 检查多个文件
python3 .kiro/hooks/scripts/code_quality_checker.py file1.py file2.py

# 生成文本格式报告
python3 .kiro/hooks/scripts/code_quality_checker.py --format text your_file.py

# 保存报告到文件
python3 .kiro/hooks/scripts/code_quality_checker.py --output report.json your_file.py
```

### 批量检查
```bash
# 检查整个项目
find . -name "*.py" -not -path "./venv/*" | xargs python3 .kiro/hooks/scripts/code_quality_checker.py
```

## 📈 性能优化

### Token使用优化
- 使用预定义规则而非AI分析，减少95%的token消耗
- 增量检查，只分析变更的文件
- 智能缓存，避免重复分析相同内容

### 执行优化
- 并发处理多个文件
- 智能跳过无变更文件
- 超时保护机制

## 🐛 故障排除

### 常见问题

#### 1. Hook未触发
**问题**: 保存Python文件时没有触发质量检查
**解决方案**:
```bash
# 检查Hook配置
ls -la .kiro/hooks/code-quality-check.json

# 重新激活Hook
bash .kiro/hooks/scripts/activate.sh

# 检查Kiro IDE Hook状态
# 在IDE中查看Hook面板
```

#### 2. 检查失败
**问题**: 质量检查过程中出现错误
**解决方案**:
```bash
# 手动测试检查器
python3 .kiro/hooks/scripts/kiro_integration.py test test_sample.py

# 查看详细错误信息
python3 .kiro/hooks/scripts/code_quality_checker.py --format text your_file.py
```

#### 3. 配置问题
**问题**: 检查规则不符合项目需求
**解决方案**:
```bash
# 编辑配置文件
nano .kiro/hooks/scripts/quality_config.json

# 重新加载配置（保存任意Python文件即可）
```

### 调试模式
```bash
# 启用详细日志
export KIRO_HOOK_DEBUG=1

# 运行测试
python3 .kiro/hooks/scripts/kiro_integration.py test test_sample.py
```

## 🔄 更新和维护

### 更新检查器
```bash
# 备份当前配置
cp .kiro/hooks/scripts/quality_config.json .kiro/hooks/scripts/quality_config.json.bak

# 更新脚本文件（手动替换或从版本控制更新）

# 重新激活
bash .kiro/hooks/scripts/activate.sh
```

### 自定义扩展
1. 修改 `code_quality_checker.py` 添加新的检查规则
2. 更新 `quality_config.json` 添加新的配置选项
3. 重新激活Hook使配置生效

## 📚 相关文档

- [MiniCRM开发标准](../../steering/minicrm-development-standards.md)
- [Hooks系统配置](../hooks-config.json)
- [Hooks注册表](../hooks-registry.md)

## 🎉 下一步

代码质量检查Hook激活后，您可以：

1. **激活自动测试Hook** - 保存文件时自动运行测试
2. **启用自动修复Hook** - 自动修复检查发现的问题
3. **配置UI组件验证** - 检查UI组件的设计规范
4. **启用依赖检查** - 监控项目依赖的一致性

让我们继续构建完整的自动化开发环境！🚀
