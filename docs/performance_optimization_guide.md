# MiniCRM 性能优化完整指南

## 概述

MiniCRM 提供了全面的性能优化解决方案，包括数据库查询优化、UI渲染优化、内存管理、数据缓存和懒加载等功能。本指南将详细介绍如何使用这些功能来提升系统性能。

## 性能优化组件架构

### 核心组件

1. **数据库性能优化**
   - `DatabasePerformanceAnalyzer` - 数据库性能分析器
   - `DatabaseQueryOptimizer` - 查询优化器
   - `DatabaseIndexManager` - 索引管理器

2. **UI性能优化**
   - `UIPerformanceOptimizer` - UI性能优化器
   - `UIPerformanceAnalyzer` - UI性能分析器
   - `UIMemoryManager` - UI内存管理器

3. **数据缓存和懒加载**
   - `DataCacheManager` - 数据缓存管理器
   - `LazyLoadingManager` - 懒加载管理器

4. **性能监控**
   - `PerformanceMonitor` - 性能监控器
   - `PerformanceHooks` - 性能监控钩子

## 快速开始

### 1. 初始化性能优化系统

```python
from minicrm.core.performance_integration import performance_integration

# 初始化性能监控和优化系统
performance_integration.initialize()
```

### 2. 数据库性能优化

#### 基本使用

```python
from minicrm.core.database_query_optimizer import get_query_optimizer
from minicrm.core.database_index_manager import get_index_manager

# 获取优化器实例
query_optimizer = get_query_optimizer(database_manager)
index_manager = get_index_manager(database_manager)

# 分析查询性能
query_plan = query_optimizer.analyze_query_plan("SELECT * FROM customers WHERE name LIKE '%张%'")
print(f"使用索引: {query_plan.uses_index}")
print(f"优化建议: {query_plan.optimization_suggestions}")

# 获取索引推荐
recommendations = index_manager.get_index_recommendations()
for rec in recommendations:
    print(f"推荐为表 {rec['table_name']} 的列 {rec['columns']} 创建索引")
```

#### 自动优化

```python
# 自动优化数据库
optimization_result = database_manager.optimize_database_indexes()
print(f"创建的索引: {optimization_result['created_indexes']}")
print(f"删除的索引: {optimization_result['dropped_indexes']}")

# 维护数据库性能
maintenance_result = database_manager.maintain_database_performance()
print(f"维护结果: {maintenance_result}")
```

### 3. UI性能优化

#### 基本使用

```python
from minicrm.core.ui_performance_optimizer import ui_performance_optimizer
from minicrm.core.ui_memory_manager import ui_memory_manager

# 启用UI性能优化
ui_performance_optimizer.enable()
ui_memory_manager.enable()

# 注册UI组件
component_id = ui_memory_manager.register_component(
    my_widget,
    "CustomerPanel",
    cleanup_callback=my_widget.cleanup
)

# 记录渲染时间
ui_performance_optimizer.track_render_time("CustomerPanel", 45.2)

# 优化内存使用
optimization_result = ui_performance_optimizer.optimize_memory_usage()
print(f"节省内存: {optimization_result['memory_saved_mb']:.1f}MB")
```

#### 组件优化

```python
# 优化组件渲染
optimization_result = ui_performance_optimizer.optimize_widget_rendering(my_widget)
print(f"应用的优化: {optimization_result['optimizations_applied']}")

# 缓存图像
success = ui_performance_optimizer.cache_pixmap("logo", logo_pixmap)
cached_pixmap = ui_performance_optimizer.get_cached_pixmap("logo")
```

### 4. 数据缓存

#### 基本缓存操作

```python
from minicrm.core.data_cache_manager import data_cache_manager

# 启用缓存
data_cache_manager.enable()

# 存储数据
success = data_cache_manager.put("customer_123", customer_data,
                                tags={"customers", "active"})

# 获取数据
customer = data_cache_manager.get("customer_123", default=None)

# 根据标签失效缓存
invalidated_count = data_cache_manager.invalidate_by_tag("customers")
```

#### 高级缓存功能

```python
from datetime import timedelta

# 带TTL和依赖的缓存
data_cache_manager.put(
    "derived_data",
    calculated_result,
    ttl=timedelta(minutes=30),
    dependencies={"base_data"},
    tags={"calculations", "reports"}
)

# 缓存优化
optimization_result = data_cache_manager.optimize()
print(f"移除过期条目: {optimization_result['expired_entries_removed']}")

# 获取缓存统计
stats = data_cache_manager.get_statistics()
print(f"命中率: {stats.hit_rate:.1f}%")
print(f"内存使用: {stats.memory_usage_mb:.2f}MB")
```

### 5. 懒加载

#### 基本懒加载

```python
from minicrm.core.lazy_loading_manager import lazy_loading_manager, LazyLoadConfig

# 配置懒加载
config = LazyLoadConfig(
    batch_size=50,
    max_concurrent_loads=3,
    preload_enabled=True
)

# 启用懒加载
lazy_loading_manager.enable()

# 注册数据加载器
lazy_loading_manager.register_loader(
    "customers",
    customer_service.get_customers,
    batch_size=20,
    cache_ttl_minutes=10
)

# 懒加载数据
future = lazy_loading_manager.load_data(
    "customers",
    limit=20,
    offset=0,
    cache_key="customers_page_0"
)

result = future.result(timeout=10)
```

#### 分页懒加载

```python
# 分页加载
future = lazy_loading_manager.load_page(
    "customers",
    page=0,
    page_size=20
)

page_data = future.result(timeout=10)
print(f"加载了 {len(page_data['data'])} 个客户")

# 预加载
preload_keys = ["customer_1", "customer_2", "customer_3"]
futures = lazy_loading_manager.preload_data("customer_by_id", preload_keys)
```

## 性能监控和分析

### 1. 获取性能报告

```python
# 获取综合性能报告
report = performance_integration.get_performance_report()

# 数据库性能
db_stats = report['performance_data']['database']
print(f"数据库操作数: {db_stats['operations_count']}")
print(f"慢查询数: {db_stats['detailed_analysis']['overall_statistics']['slow_queries_count']}")

# UI性能
ui_stats = report['performance_data']['ui']
print(f"UI操作数: {ui_stats['operations_count']}")
print(f"平均响应时间: {ui_stats['detailed_analysis']['overall_statistics']['avg_response_time_ms']:.2f}ms")
```

### 2. 性能监控装饰器

```python
from minicrm.core.performance_hooks import (
    monitor_db_query,
    monitor_ui_operation,
    monitor_render_operation
)

class CustomerService:
    @monitor_db_query("select")
    def get_customers(self, limit=50):
        # 数据库查询逻辑
        return self.dao.get_customers(limit)

class CustomerPanel:
    @monitor_ui_operation("load_data")
    def load_data(self):
        # 数据加载逻辑
        pass

    @monitor_render_operation()
    def render_view(self):
        # 渲染逻辑
        pass
```

## 最佳实践

### 1. 数据库优化最佳实践

```python
# 1. 定期分析和优化
def maintain_database_performance():
    # 分析慢查询
    slow_queries = database_performance_analyzer.get_slow_queries(limit=10)
    for query in slow_queries:
        print(f"慢查询: {query.sql[:50]}... ({query.execution_time:.2f}ms)")

    # 创建推荐索引
    recommendations = database_manager.get_index_recommendations()
    for rec in recommendations[:3]:  # 只创建前3个推荐
        database_manager.create_recommended_index(rec['table_name'], rec['columns'])

    # 执行维护
    database_manager.maintain_database_performance()

# 2. 使用缓存查询
def get_customer_with_cache(customer_id):
    cache_key = f"customer_{customer_id}"

    # 先检查缓存
    customer = data_cache_manager.get(cache_key)
    if customer:
        return customer

    # 缓存未命中，从数据库加载
    customer = database_manager.execute_query(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,)
    )

    # 缓存结果
    if customer:
        data_cache_manager.put(cache_key, customer[0],
                              tags={"customers"})

    return customer[0] if customer else None
```

### 2. UI优化最佳实践

```python
# 1. 组件生命周期管理
class OptimizedCustomerPanel:
    def __init__(self):
        # 注册到内存管理器
        self.component_id = ui_memory_manager.register_component(
            self, "CustomerPanel", cleanup_callback=self.cleanup
        )

        # 启用虚拟滚动
        ui_performance_optimizer.enable_virtual_scrolling(self.scroll_area)

    def render(self):
        # 记录渲染时间
        start_time = time.perf_counter()

        # 渲染逻辑
        self._do_render()

        # 记录性能
        render_time = (time.perf_counter() - start_time) * 1000
        ui_performance_optimizer.track_render_time("CustomerPanel", render_time)

    def cleanup(self):
        # 清理资源
        self.data.clear()
        self.child_widgets.clear()

# 2. 内存优化
def optimize_ui_memory():
    # 定期清理空闲组件
    cleanup_result = ui_memory_manager.cleanup_idle_components()

    # 强制垃圾回收
    if cleanup_result['cleaned_components'] > 10:
        ui_memory_manager.force_garbage_collection()

    # 检查内存泄漏
    leaks = ui_memory_manager.detect_memory_leaks()
    for leak in leaks:
        print(f"检测到内存泄漏: {leak.component_type}")
```

### 3. 缓存策略最佳实践

```python
# 1. 分层缓存策略
class CacheStrategy:
    def __init__(self):
        # L1缓存：内存缓存，快速访问
        self.l1_cache = data_cache_manager

        # L2缓存：可以是文件缓存或Redis
        self.l2_cache = None

    def get_with_fallback(self, key):
        # 先检查L1缓存
        result = self.l1_cache.get(key)
        if result:
            return result

        # 检查L2缓存
        if self.l2_cache:
            result = self.l2_cache.get(key)
            if result:
                # 回填到L1缓存
                self.l1_cache.put(key, result)
                return result

        return None

# 2. 智能缓存失效
def invalidate_related_cache(entity_type, entity_id):
    """智能失效相关缓存"""
    if entity_type == "customer":
        # 失效客户相关的所有缓存
        data_cache_manager.invalidate_by_tag("customers")
        data_cache_manager.invalidate_by_dependency(f"customer_{entity_id}")
    elif entity_type == "supplier":
        data_cache_manager.invalidate_by_tag("suppliers")
        data_cache_manager.invalidate_by_dependency(f"supplier_{entity_id}")
```

### 4. 懒加载最佳实践

```python
# 1. 智能预加载
class SmartPreloader:
    def __init__(self):
        self.access_patterns = defaultdict(list)

    def record_access(self, resource_type, resource_id):
        self.access_patterns[resource_type].append(resource_id)

        # 基于访问模式预加载
        if len(self.access_patterns[resource_type]) > 5:
            self._predict_and_preload(resource_type)

    def _predict_and_preload(self, resource_type):
        # 简单的预测逻辑：预加载最近访问的相邻资源
        recent_ids = self.access_patterns[resource_type][-5:]

        for resource_id in recent_ids:
            # 预加载相邻的资源
            next_id = resource_id + 1
            lazy_loading_manager.preload_data(
                f"{resource_type}_by_id",
                [f"{resource_type}_{next_id}"]
            )

# 2. 批量加载优化
def load_customers_optimized(page, page_size):
    """优化的客户加载"""
    # 使用懒加载管理器
    future = lazy_loading_manager.load_page(
        "customers",
        page=page,
        page_size=page_size
    )

    # 异步等待结果
    try:
        result = future.result(timeout=30)

        # 记录访问模式
        smart_preloader.record_access("customer", page)

        return result
    except TimeoutError:
        # 超时处理
        print("数据加载超时，返回缓存数据")
        return lazy_loading_manager.get_cached_page("customers", page)
```

## 性能调优指南

### 1. 性能基准测试

```python
def performance_benchmark():
    """性能基准测试"""
    import time

    # 数据库性能测试
    start_time = time.time()
    for i in range(100):
        database_manager.execute_query("SELECT * FROM customers LIMIT 10")
    db_time = time.time() - start_time

    # 缓存性能测试
    start_time = time.time()
    for i in range(100):
        data_cache_manager.get(f"test_key_{i % 10}")
    cache_time = time.time() - start_time

    print(f"数据库查询时间: {db_time:.2f}s")
    print(f"缓存访问时间: {cache_time:.2f}s")
    print(f"性能提升: {(db_time / cache_time):.1f}x")
```

### 2. 性能监控仪表板

```python
def create_performance_dashboard():
    """创建性能监控仪表板"""
    # 获取各组件性能数据
    db_report = database_performance_analyzer.generate_performance_report()
    ui_report = ui_performance_analyzer.generate_performance_report()
    cache_stats = data_cache_manager.get_statistics()
    lazy_stats = lazy_loading_manager.get_statistics()

    dashboard_data = {
        "database": {
            "slow_queries": db_report['overall_statistics']['slow_queries_count'],
            "avg_query_time": db_report['overall_statistics']['avg_execution_time_ms'],
            "recommendations": len(db_report.get('recommendations', []))
        },
        "ui": {
            "slow_operations": ui_report['overall_statistics']['slow_operations_count'],
            "avg_response_time": ui_report['overall_statistics']['avg_response_time_ms'],
            "memory_usage": ui_report.get('memory_statistics', {}).get('current_memory_mb', 0)
        },
        "cache": {
            "hit_rate": cache_stats.hit_rate,
            "memory_usage": cache_stats.memory_usage_mb,
            "entries": cache_stats.total_entries
        },
        "lazy_loading": {
            "total_tasks": lazy_stats.total_tasks,
            "cache_hits": lazy_stats.cached_hits,
            "avg_load_time": lazy_stats.avg_load_time_ms
        }
    }

    return dashboard_data
```

## 故障排除

### 常见问题和解决方案

1. **内存使用过高**
   ```python
   # 检查内存使用
   ui_stats = ui_performance_optimizer.get_performance_statistics()
   if ui_stats['memory_statistics']['current_memory_mb'] > 500:
       # 执行内存优化
       ui_performance_optimizer.optimize_memory_usage()
       ui_memory_manager.force_garbage_collection()
   ```

2. **缓存命中率低**
   ```python
   # 分析缓存使用
   cache_stats = data_cache_manager.get_statistics()
   if cache_stats.hit_rate < 50:
       # 调整缓存策略
       data_cache_manager.set_cache_size(200)  # 增加缓存大小
       data_cache_manager.set_cache_ttl(60)    # 增加TTL
   ```

3. **数据库查询慢**
   ```python
   # 分析慢查询
   slow_queries = database_performance_analyzer.get_slow_queries(limit=5)
   for query in slow_queries:
       print(f"慢查询: {query.sql}")
       print(f"建议: 为表 {query.table_name} 添加索引")

   # 自动创建推荐索引
   database_manager.optimize_database_indexes()
   ```

## 总结

MiniCRM的性能优化系统提供了全面的解决方案，通过合理使用这些工具和遵循最佳实践，可以显著提升应用程序的性能。关键是要：

1. **持续监控** - 使用性能监控工具持续跟踪系统性能
2. **主动优化** - 定期执行性能优化和维护
3. **智能缓存** - 合理使用缓存策略减少重复计算
4. **懒加载** - 按需加载数据减少初始加载时间
5. **内存管理** - 及时清理不需要的资源避免内存泄漏

通过这些措施，可以确保MiniCRM在处理大量数据时仍能保持良好的响应性能。
