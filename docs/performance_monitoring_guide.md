# MiniCRM 性能监控指南

## 概述

MiniCRM 提供了全面的性能监控功能，包括数据库查询性能监控和UI响应时间监控。这些功能帮助开发者识别性能瓶颈，优化系统性能。

## 功能特性

### 数据库性能监控

- **慢查询检测**: 自动检测超过阈值的数据库查询
- **查询统计分析**: 提供查询频率、执行时间等统计信息
- **查询类型分析**: 按操作类型（SELECT、INSERT、UPDATE、DELETE）分组统计
- **表级别统计**: 按数据库表分组的性能统计
- **连接性能监控**: 数据库连接建立和关闭时间监控

### UI性能监控

- **响应时间统计**: 监控UI操作的响应时间
- **渲染性能分析**: 专门监控界面渲染时间
- **数据加载监控**: 监控数据加载操作的性能
- **卡顿检测**: 自动检测UI卡顿事件
- **组件级别统计**: 按UI组件分组的性能统计

## 使用方法

### 1. 初始化性能监控

```python
from minicrm.core.performance_integration import performance_integration

# 初始化性能监控
performance_integration.initialize()
```

### 2. 数据库性能监控

#### 使用装饰器监控数据库操作

```python
from minicrm.core.performance_hooks import monitor_db_query

class CustomerService:
    @monitor_db_query("select")
    def get_customers(self, limit: int = 10):
        """获取客户列表"""
        # 数据库查询逻辑
        return self.dao.select_customers(limit)

    @monitor_db_query("insert")
    def create_customer(self, customer_data: dict):
        """创建客户"""
        # 数据库插入逻辑
        return self.dao.insert_customer(customer_data)

    @monitor_db_query("update")
    def update_customer(self, customer_id: int, data: dict):
        """更新客户"""
        # 数据库更新逻辑
        return self.dao.update_customer(customer_id, data)
```

#### 集成数据库管理器

```python
from minicrm.core.performance_integration import performance_integration

# 为数据库管理器集成性能监控
performance_integration.integrate_database_manager(database_manager)
```

### 3. UI性能监控

#### 使用装饰器监控UI操作

```python
from minicrm.core.performance_hooks import (
    monitor_ui_operation,
    monitor_render_operation,
    monitor_data_refresh
)

class CustomerPanel:
    @monitor_ui_operation("load_data")
    def load_data(self):
        """加载数据"""
        # 数据加载逻辑
        pass

    @monitor_render_operation()
    def render_view(self):
        """渲染视图"""
        # 界面渲染逻辑
        pass

    @monitor_data_refresh("customers")
    def refresh_customers(self):
        """刷新客户数据"""
        # 数据刷新逻辑
        pass
```

#### 手动计时监控

```python
from minicrm.core.ui_performance_analyzer import ui_performance_analyzer

class CustomComponent:
    def complex_operation(self):
        # 开始计时
        timing_id = ui_performance_analyzer.start_operation_timing(
            "complex_operation", "CustomComponent"
        )

        try:
            # 执行复杂操作
            self.do_complex_work()

        finally:
            # 结束计时
            ui_performance_analyzer.end_operation_timing(
                timing_id,
                render_time=50.0,  # 渲染时间（毫秒）
                data_load_time=100.0,  # 数据加载时间（毫秒）
            )
```

### 4. 获取性能报告

#### 综合性能报告

```python
from minicrm.core.performance_integration import performance_integration

# 获取综合性能报告
report = performance_integration.get_performance_report()

print(f"数据库操作数量: {report['performance_data']['database']['operations_count']}")
print(f"UI操作数量: {report['performance_data']['ui']['operations_count']}")
```

#### 数据库性能报告

```python
from minicrm.core.database_performance_analyzer import database_performance_analyzer

# 获取详细的数据库性能报告
db_report = database_performance_analyzer.generate_performance_report()

print(f"总查询数: {db_report['overall_statistics']['total_queries']}")
print(f"平均执行时间: {db_report['overall_statistics']['avg_execution_time_ms']:.2f}ms")
print(f"慢查询数量: {db_report['overall_statistics']['slow_queries_count']}")

# 获取慢查询列表
slow_queries = database_performance_analyzer.get_slow_queries(limit=10)
for query in slow_queries:
    print(f"慢查询: {query.sql[:50]}... ({query.execution_time:.2f}ms)")
```

#### UI性能报告

```python
from minicrm.core.ui_performance_analyzer import ui_performance_analyzer

# 获取详细的UI性能报告
ui_report = ui_performance_analyzer.generate_performance_report()

print(f"总操作数: {ui_report['overall_statistics']['total_operations']}")
print(f"平均响应时间: {ui_report['overall_statistics']['avg_response_time_ms']:.2f}ms")
print(f"慢操作数量: {ui_report['overall_statistics']['slow_operations_count']}")

# 获取慢操作列表
slow_operations = ui_performance_analyzer.get_slow_operations(limit=10)
for operation in slow_operations:
    print(f"慢操作: {operation.component_name}.{operation.operation_type} ({operation.response_time:.2f}ms)")

# 检测UI卡顿
lag_events = ui_performance_analyzer.detect_ui_lag(threshold=100.0)
for lag in lag_events:
    print(f"卡顿事件: {lag['type']} - {lag['component']}.{lag['operation']} ({lag['duration_ms']:.2f}ms)")
```

## 配置选项

### 性能阈值配置

```python
from minicrm.core.database_performance_analyzer import DatabasePerformanceAnalyzer
from minicrm.core.ui_performance_analyzer import UIPerformanceAnalyzer

# 自定义数据库性能分析器
db_analyzer = DatabasePerformanceAnalyzer(
    slow_query_threshold=500.0  # 慢查询阈值（毫秒）
)

# 自定义UI性能分析器
ui_analyzer = UIPerformanceAnalyzer(
    slow_operation_threshold=300.0,  # 慢操作阈值（毫秒）
    render_threshold=50.0,           # 渲染阈值（毫秒）
    data_load_threshold=800.0        # 数据加载阈值（毫秒）
)
```

### 启用/禁用监控

```python
from minicrm.core.performance_integration import performance_integration
from minicrm.core.database_performance_analyzer import database_performance_analyzer
from minicrm.core.ui_performance_analyzer import ui_performance_analyzer

# 启用/禁用整体性能监控
performance_integration.initialize()  # 启用
performance_integration.shutdown()    # 禁用

# 启用/禁用特定分析器
database_performance_analyzer.enable()   # 启用数据库监控
database_performance_analyzer.disable()  # 禁用数据库监控

ui_performance_analyzer.enable()   # 启用UI监控
ui_performance_analyzer.disable()  # 禁用UI监控
```

## 性能优化建议

### 数据库优化

1. **慢查询优化**
   - 添加适当的索引
   - 优化查询语句
   - 使用查询缓存

2. **连接管理**
   - 使用连接池
   - 及时关闭连接
   - 监控连接数量

### UI优化

1. **响应时间优化**
   - 使用异步操作
   - 实现懒加载
   - 优化数据结构

2. **渲染性能优化**
   - 减少不必要的重绘
   - 使用虚拟化技术
   - 优化CSS和样式

3. **数据加载优化**
   - 实现分页加载
   - 使用缓存机制
   - 压缩数据传输

## 最佳实践

1. **监控关键路径**: 重点监控用户常用的功能和操作
2. **设置合理阈值**: 根据业务需求设置合适的性能阈值
3. **定期分析报告**: 定期查看性能报告，识别性能趋势
4. **及时优化**: 发现性能问题时及时进行优化
5. **测试验证**: 优化后进行性能测试验证效果

## 故障排除

### 常见问题

1. **监控数据不准确**
   - 检查系统时钟同步
   - 确认监控装饰器正确应用
   - 验证分析器是否启用

2. **性能报告为空**
   - 确认已执行被监控的操作
   - 检查监控是否正确初始化
   - 验证装饰器参数是否正确

3. **内存使用过高**
   - 调整最大指标数量限制
   - 定期清理历史数据
   - 优化数据结构

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.getLogger('minicrm.core.performance_monitor').setLevel(logging.DEBUG)
   logging.getLogger('minicrm.core.database_performance_analyzer').setLevel(logging.DEBUG)
   logging.getLogger('minicrm.core.ui_performance_analyzer').setLevel(logging.DEBUG)
   ```

2. **导出性能数据**
   ```python
   from minicrm.core.performance_monitor import performance_monitor

   # 导出性能数据到文件
   performance_monitor.export_metrics("performance_data.json")
   ```

3. **清理测试数据**
   ```python
   # 清空性能指标
   performance_monitor.clear_metrics()
   database_performance_analyzer.clear_metrics()
   ui_performance_analyzer.clear_metrics()
   ```

## 示例代码

完整的使用示例请参考 `examples/performance_monitoring_usage.py` 文件。
