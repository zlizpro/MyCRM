# 自动测试运行Hook

## Hook配置

**触发条件**: 当保存测试文件或被测试的源文件时
**执行频率**: 每次保存相关文件
**适用文件**: `test_*.py`, `*_test.py`, 以及对应的源文件

## Hook描述

这个hook会在您保存测试文件或源代码文件时自动运行相关的单元测试，确保代码更改不会破坏现有功能。

## 执行任务

1. **识别相关测试**
   - 如果保存的是测试文件，运行该测试文件
   - 如果保存的是源文件，查找并运行对应的测试文件
   - 例如：保存`customer_service.py`时运行`test_customer_service.py`

2. **运行测试**
   - 使用pytest运行相关测试
   - 捕获测试输出和结果
   - 记录测试执行时间

3. **分析测试结果**
   - 统计通过/失败的测试数量
   - 识别失败的具体测试用例
   - 分析测试覆盖率（如果可用）

4. **生成报告**
   - 提供简洁的测试结果摘要
   - 对于失败的测试，提供详细的错误信息
   - 建议修复方案

## 测试命令示例

```bash
# 运行单个测试文件
pytest tests/test_customer_service.py -v

# 运行特定模块的所有测试
pytest tests/test_services/ -v

# 运行所有测试
pytest tests/ -v
```

## 输出格式

```
🧪 测试运行结果：
✅ 通过: 15个测试
❌ 失败: 2个测试
⏱️ 执行时间: 3.2秒

失败的测试：
1. test_create_customer_with_invalid_data
   错误：ValidationError not raised
   建议：检查客户数据验证逻辑

2. test_update_nonexistent_customer
   错误：Expected BusinessLogicError but got None
   建议：确保更新不存在客户时抛出正确异常
```
