# search_bar_simplified.py 重构指南

## 原文件信息
- 原文件: src/minicrm/ui/components/search_bar_simplified.py
- 原文件行数: 352行
- 拆分策略: generic

## 拆分文件列表

### search_bar_simplified.py
- **描述**: 主类文件
- **最大行数**: 150行
- **包含内容**: 主要类定义

### search_bar_simplified_manager.py
- **描述**: 管理器类
- **最大行数**: 120行
- **包含内容**: 管理相关方法

### search_bar_simplified_utils.py
- **描述**: 工具函数
- **最大行数**: 100行
- **包含内容**: 工具函数和常量

## 重构步骤

1. 分析原文件中的类和方法
2. 按照单一职责原则将代码分配到对应文件
3. 确保每个文件不超过行数限制
4. 使用transfunctions替换重复实现
5. 更新导入语句和依赖关系
6. 运行测试确保功能正常

## 注意事项

- 严格遵循单一职责原则
- 避免循环依赖
- 保持接口的向后兼容性
- 使用类型注解和文档字符串
