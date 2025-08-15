# 性能分析Hook

## Hook配置

**触发条件**: 手动触发或当保存关键性能文件时
**执行频率**: 按需执行
**适用文件**: `services/*.py`, `data/*.py`, `ui/*.py`

## Hook描述

这个hook会分析MiniCRM应用的性能瓶颈，识别慢查询、内存泄漏和UI响应问题，并提供优化建议。

## 执行任务

1. **数据库性能分析**
   - 识别慢查询和N+1查询问题
   - 分析数据库连接使用情况
   - 检查索引使用效率

2. **内存使用分析**
   - 监控内存使用趋势
   - 识别潜在的内存泄漏
   - 分析大对象的生命周期

3. **UI响应性分析**
   - 测量UI操作的响应时间
   - 识别阻塞主线程的操作
   - 分析图表渲染性能

4. **业务逻辑性能**
   - 分析复杂计算的执行时间
   - 识别可以优化的算法
   - 检查缓存使用效率

## 性能指标

### 数据库性能
- 查询执行时间 (< 100ms 为优秀)
- 连接池使用率 (< 80% 为正常)
- 索引命中率 (> 95% 为优秀)

### 内存使用
- 应用内存占用 (< 500MB 为正常)
- 内存增长率 (< 1MB/小时为正常)
- 垃圾回收频率

### UI响应性
- 界面操作响应时间 (< 200ms)
- 图表渲染时间 (< 1秒)
- 数据加载时间 (< 3秒)

## 分析方法

1. **代码静态分析**
   - 扫描可能的性能问题模式
   - 检查循环复杂度
   - 识别重复计算

2. **运行时性能监控**
   - 使用装饰器监控函数执行时间
   - 内存使用情况跟踪
   - 数据库查询日志分析

3. **压力测试**
   - 模拟大量数据操作
   - 测试并发用户场景
   - 长时间运行稳定性测试

## 输出格式

```
⚡ 性能分析报告：

## 总体评分：B+ (82/100)

### 🗄️ 数据库性能 (85/100)
✅ 平均查询时间: 45ms (优秀)
⚠️ 发现3个慢查询:
   - CustomerService.search_customers(): 850ms
     建议：为name和phone字段添加复合索引
   - QuoteService.get_comparison_data(): 1.2s
     建议：优化子查询，使用JOIN替代

✅ 连接池使用率: 65% (正常)

### 💾 内存使用 (78/100)
⚠️ 当前内存占用: 680MB (偏高)
⚠️ 检测到潜在内存泄漏:
   - ChartWidget未正确清理matplotlib对象
   - CustomerPanel中的事件监听器未解绑

✅ 垃圾回收正常

### 🎨 UI响应性 (80/100)
✅ 平均响应时间: 150ms (优秀)
⚠️ 发现响应慢的操作:
   - 客户列表加载: 2.8s (1000+记录)
     建议：实现虚拟滚动或分页
   - 报价比对图表: 1.5s
     建议：使用后台线程渲染

### 🔧 业务逻辑 (85/100)
✅ 大部分计算效率良好
⚠️ 优化建议:
   - QuoteComparison.calculate_trends() 可以缓存结果
   - CustomerAnalytics.get_statistics() 建议添加缓存

## 🎯 优化建议 (按优先级排序)

### 高优先级
1. 添加数据库索引解决慢查询
2. 修复ChartWidget内存泄漏
3. 实现客户列表分页加载

### 中优先级
4. 添加计算结果缓存
5. 优化图表渲染性能
6. 实现后台数据预加载

### 低优先级
7. 优化算法复杂度
8. 减少不必要的对象创建
9. 实现更细粒度的缓存策略

## 📊 性能趋势
- 相比上次分析，整体性能提升了5%
- 数据库性能有所改善
- UI响应性基本稳定
- 内存使用略有增加，需要关注
```

## 自动优化功能

### 可自动应用的优化

```
🚀 性能自动优化选项：

检测到以下可自动优化项：

✅ 数据库索引优化 (预计提升查询速度60%)
   - 为customers表添加name+phone复合索引
   - 为quotes表添加customer_id+date索引
   
✅ 缓存优化 (预计减少计算时间80%)
   - 为calculate_customer_trends()添加LRU缓存
   - 为get_statistics()添加时间缓存
   
✅ 内存泄漏修复 (预计减少内存占用30%)
   - 修复ChartWidget的matplotlib对象清理
   - 添加事件监听器自动解绑

⚠️ 需要确认的优化 (可能影响功能)
   - 客户列表虚拟滚动实现
   - 图表异步渲染改造

[🔧 应用所有自动优化] [🔍 逐项确认] [📊 仅查看建议]

选择：应用所有自动优化

正在应用优化...

1. 创建数据库索引...
   ✅ 已创建 idx_customers_name_phone
   ✅ 已创建 idx_quotes_customer_date
   
2. 添加缓存装饰器...
   ✅ 已为 calculate_customer_trends() 添加 @lru_cache
   ✅ 已为 get_statistics() 添加 @timed_cache(300)
   
3. 修复内存泄漏...
   ✅ 已修复 ChartWidget.cleanup() 方法
   ✅ 已添加 CustomerPanel 事件解绑逻辑

优化完成！预计性能提升：
- 查询速度提升：60%
- 计算时间减少：80%  
- 内存占用减少：30%

建议重启应用以获得最佳性能。
```

### 自动生成的优化代码

#### 1. 数据库索引优化
```sql
-- 自动生成的索引创建脚本
-- 文件：migrations/add_performance_indexes.sql

CREATE INDEX IF NOT EXISTS idx_customers_name_phone 
ON customers(name, phone);

CREATE INDEX IF NOT EXISTS idx_quotes_customer_date 
ON quotes(customer_id, quote_date DESC);

CREATE INDEX IF NOT EXISTS idx_interactions_customer_date 
ON customer_interactions(customer_id, interaction_date DESC);
```

#### 2. 缓存装饰器自动添加
```python
# 自动修改前
def calculate_customer_trends(self, customer_id: int, period: int):
    # 复杂计算逻辑
    return trends_data

# 自动修改后  
from functools import lru_cache
from core.decorators import timed_cache

@lru_cache(maxsize=100)
def calculate_customer_trends(self, customer_id: int, period: int):
    """计算客户趋势 (已添加缓存优化)"""
    # 复杂计算逻辑
    return trends_data

@timed_cache(expire_seconds=300)  # 5分钟缓存
def get_customer_statistics(self, customer_id: int):
    """获取客户统计 (已添加时间缓存)"""
    # 统计计算逻辑
    return stats_data
```

#### 3. 内存泄漏自动修复
```python
# 自动修改前
class ChartWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._figure = plt.figure()
        
# 自动修改后
class ChartWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._figure = plt.figure()
        
    def cleanup(self):
        """清理资源 (自动添加)"""
        if hasattr(self, '_figure') and self._figure:
            plt.close(self._figure)
            self._figure = None
            
    def __del__(self):
        """析构函数 (自动添加)"""
        self.cleanup()
```

#### 4. 查询优化自动重构
```python
# 自动优化前 (N+1查询问题)
def get_customers_with_quotes(self):
    customers = self.get_all_customers()
    for customer in customers:
        customer.quotes = self.get_quotes_by_customer(customer.id)
    return customers

# 自动优化后 (使用JOIN)
def get_customers_with_quotes(self):
    """获取客户及其报价 (已优化JOIN查询)"""
    sql = """
    SELECT c.*, q.id as quote_id, q.total_amount, q.quote_date
    FROM customers c
    LEFT JOIN quotes q ON c.id = q.customer_id
    ORDER BY c.id, q.quote_date DESC
    """
    # 使用单次查询替代N+1查询
    return self._execute_optimized_query(sql)
```

### 性能监控集成
```python
# 自动添加性能监控装饰器
from core.hooks import perf_hooks

@perf_hooks.monitor_performance('customer_search')
def search_customers(self, query: str, filters: Dict[str, Any]):
    """搜索客户 (已添加性能监控)"""
    # 原有搜索逻辑
    pass
```
