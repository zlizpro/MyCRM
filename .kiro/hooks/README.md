# MiniCRM Agent Hooks

这里包含了为MiniCRM项目定制的智能Agent Hooks，可以自动化常见的开发任务。

## 🔧 可用的Hooks

### 1. 代码质量检查 (`code-quality-check.md`)
- **触发条件**: 保存Python文件时
- **功能**: 检查PEP 8规范、类型注解、文档字符串、异常处理
- **优先级**: 1 (最高)

### 2. 自动测试运行 (`test-runner.md`)
- **触发条件**: 保存测试文件或源文件时
- **功能**: 自动运行相关单元测试，生成测试报告
- **优先级**: 2

### 3. 数据库迁移检查 (`database-migration.md`)
- **触发条件**: 修改数据模型文件时
- **功能**: 检测数据库结构变更，生成迁移建议
- **优先级**: 3

### 4. UI组件验证 (`ui-component-validator.md`)
- **触发条件**: 保存UI组件文件时
- **功能**: 验证UI设计规范、用户体验、无障碍性
- **优先级**: 4

### 5. 文档自动更新 (`documentation-updater.md`)
- **触发条件**: 修改API或配置文件时
- **功能**: 检查文档同步，自动生成API文档
- **优先级**: 5

### 6. 依赖检查 (`dependency-checker.md`)
- **触发条件**: 修改导入或requirements.txt时
- **功能**: 检查依赖一致性、版本兼容性、安全漏洞
- **优先级**: 6

### 7. 性能分析 (`performance-profiler.md`)
- **触发条件**: 手动触发或保存关键文件时
- **功能**: 分析数据库、内存、UI性能，提供优化建议
- **优先级**: 7

### 8. 高效自动修复 (`efficient-auto-fixer.md`)
- **触发条件**: 手动触发或代码质量检查后
- **功能**: Token优化的代码自动修复
- **优先级**: 8

## ⚙️ 配置说明

### 启用/禁用Hooks
在 `hooks-config.json` 中修改 `enabled` 字段：
```json
{
  "id": "code-quality-check",
  "enabled": true  // 设置为 false 禁用
}
```

### 调整触发条件
修改 `triggers` 数组中的触发条件：
```json
{
  "triggers": [
    {
      "type": "file_save",
      "pattern": "*.py"  // 文件匹配模式
    }
  ]
}
```

### 设置优先级
较小的数字表示更高的优先级，优先级高的hooks会先执行。

## 🚀 使用方式

1. **自动执行**: Hooks会根据配置的触发条件自动执行
2. **手动触发**: 在Agent Hooks界面中点击相应的hook
3. **批量执行**: 可以同时运行多个hooks（最多3个并发）

## 📊 性能优化

- 所有hooks都经过Token使用优化
- 支持并发执行以提高效率
- 设置了30秒的超时限制
- 智能的依赖关系管理

## 🔍 故障排除

如果hooks没有正常工作：

1. 检查 `hooks-config.json` 中的配置
2. 确认文件路径匹配模式正确
3. 查看Kiro IDE的Agent Hooks面板中的状态
4. 检查hooks文件的内容格式

## 📝 自定义Hooks

要添加新的hook：

1. 在 `.kiro/hooks/` 目录中创建新的 `.md` 文件
2. 在 `hooks-config.json` 中添加相应的配置
3. 重启Kiro IDE或刷新Agent Hooks面板

这些hooks将大大提高您的MiniCRM开发效率！🎉
