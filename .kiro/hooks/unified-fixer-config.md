# Python统一自动修复Hook配置指南

## 概述
统一的Python代码自动修复系统整合了原有的三个修复hooks：
- Token优化代码修复
- 智能自动修复  
- 高效自动修复

## 修复模式选择

### 1. 智能模式 (smart) - 默认推荐
**适用场景**: 日常开发，代码质量要求高
**特点**:
- 全面的代码质量分析
- 交互式修复建议
- 支持复杂问题处理
- 提供多种修复方案选择

**配置**:
```json
{
  "fixMode": "smart",
  "autoApplySimpleFixes": true,
  "maxTokens": 500,
  "interactiveMode": true
}
```

### 2. 快速模式 (fast)
**适用场景**: 快速迭代，时间紧迫
**特点**:
- 速度优先，快速修复
- 使用预定义模板
- 专注核心问题
- 批量应用标准规则

**配置**:
```json
{
  "fixMode": "fast",
  "autoApplySimpleFixes": true,
  "maxTokens": 200,
  "interactiveMode": false
}
```

### 3. 节约模式 (token-optimized)
**适用场景**: Token成本敏感，大量文件处理
**特点**:
- 最小token消耗
- 预编译规则匹配
- 增量处理
- 成本效益最高

**配置**:
```json
{
  "fixMode": "token-optimized",
  "autoApplySimpleFixes": true,
  "maxTokens": 100,
  "interactiveMode": false
}
```

## 配置参数说明

| 参数                   | 类型    | 默认值  | 说明                                 |
| ---------------------- | ------- | ------- | ------------------------------------ |
| `fixMode`              | string  | "smart" | 修复模式：fast/smart/token-optimized |
| `autoApplySimpleFixes` | boolean | true    | 是否自动应用简单修复                 |
| `maxTokens`            | number  | 500     | 最大token使用限制                    |
| `interactiveMode`      | boolean | true    | 是否启用交互式修复建议               |

## 修改配置

要更改修复模式，编辑 `.kiro/hooks/unified-python-fixer.kiro.hook` 文件中的 `config` 部分：

```json
{
  "config": {
    "fixMode": "fast",           // 改为快速模式
    "autoApplySimpleFixes": true,
    "maxTokens": 200,            // 降低token限制
    "interactiveMode": false     // 关闭交互模式
  }
}
```

## 原有Hooks状态
为避免冲突，以下hooks已被禁用：
- `token-optimization-hook.kiro.hook` (disabled)
- `smart-auto-fixer.kiro.hook` (disabled)  
- `efficient-python-fixer.kiro.hook` (disabled)

如需重新启用单独的hook，将对应文件中的 `"enabled": false` 改为 `"enabled": true`，并禁用统一修复hook。

## 使用建议

### 开发阶段建议
- **开发初期**: 使用智能模式，确保代码质量
- **快速迭代**: 使用快速模式，提高开发效率
- **批量处理**: 使用节约模式，控制成本

### 团队协作建议
- 统一团队使用的修复模式
- 在代码审查前使用智能模式进行全面检查
- 在CI/CD流程中使用快速模式进行基础检查

## 故障排除

### 常见问题
1. **Hook不触发**: 检查文件是否匹配 `*.py` 模式
2. **修复效果不理想**: 尝试切换到智能模式
3. **Token消耗过多**: 切换到节约模式或降低maxTokens
4. **修复冲突**: 确保其他Python修复hooks已禁用

### 重置配置
如需重置为默认配置，将config部分替换为：
```json
{
  "config": {
    "fixMode": "smart",
    "autoApplySimpleFixes": true,
    "maxTokens": 500,
    "interactiveMode": true
  }
}
```
