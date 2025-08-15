# 🚀 MiniCRM 性能优化快速开始指南

## 📋 5 分钟快速优化

### 1. 立即生效的优化（0 分钟）

#### 添加性能监控装饰器

```python
from src.minicrm.core.performance import performance_monitor

@performance_monitor("customer_search")
def search_customers(query: str):
    # 你的搜索逻辑
    pass
```

#### 使用智能缓存

```python
from src.minicrm.core.performance import global_cache

def get_customer_stats(customer_id: int):
    cache_key = f"stats_{customer_id}"

    # 尝试从缓存获取
    stats = global_cache.get(cache_key)
    if stats is not None:
        return stats

    # 计算统计信息
    stats = calculate_stats(customer_id)

    # 存入缓存
    global_cache.set(cache_key, stats)
    return stats
```

### 2. 内存监控（1 分钟）

#### 添加内存上下文管理

```python
from src.minicrm.core.performance import memory_context

def process_large_report():
    with memory_context("报表生成") as memory_manager:
        # 生成大量数据
        data = generate_report_data()

        # 检查内存状态
        status = memory_manager.check_memory_status()
        if status['status'] == 'warning':
            # 执行垃圾回收
            memory_manager.force_garbage_collection()

        return process_data(data)
```

### 3. 数据库优化（2 分钟）

#### 使用批量操作

```python
def batch_update_customers(updates: list):
    batch_size = 1000

    for i in range(0, len(updates), batch_size):
        batch = updates[i:i + batch_size]
        # 批量更新而不是逐个更新
        execute_batch_update(batch)
```

### 4. UI 性能优化（2 分钟）

#### Qt 表格虚拟化

```python
from PySide6.QtCore import QAbstractTableModel

class VirtualTableModel(QAbstractTableModel):
    def __init__(self, data_loader):
        super().__init__()
        self.data_loader = data_loader
        self.page_size = 50
        self.current_data = []

    def rowCount(self, parent=None):
        return len(self.current_data)

    def canFetchMore(self, parent=None):
        return len(self.current_data) < self.data_loader.total_count

    def fetchMore(self, parent=None):
        # 按需加载更多数据
        next_batch = self.data_loader.get_next_batch(self.page_size)
        if next_batch:
            self.beginInsertRows(parent, len(self.current_data),
                               len(self.current_data) + len(next_batch) - 1)
            self.current_data.extend(next_batch)
            self.endInsertRows()
```

## 🔧 快速配置

### 1. 环境变量配置（推荐）

```bash
# 开发环境
export MINICRM_ENV=development
export MINICRM_CACHE_SIZE=64
export MINICRM_MEMORY_WARNING=100

# 生产环境
export MINICRM_ENV=production
export MINICRM_CACHE_SIZE=256
export MINICRM_MEMORY_WARNING=300
```

### 2. 代码配置

```python
from src.minicrm.config.performance_config import current_config

# 查看当前配置
current_config.print_config()

# 验证配置
validation = current_config.validate_config()
if not validation['valid']:
    print("配置问题:", validation['issues'])
```

## 📊 效果验证

### 1. 运行性能检查

```bash
# 全面性能检查
./scripts/performance-check.sh

# 查看性能报告
cat performance_report.md
```

### 2. 查看性能统计

```python
from src.minicrm.core.performance import performance_tracker

# 获取性能摘要
summary = performance_tracker.get_performance_summary()
for func_name, stats in summary.items():
    print(f"{func_name}: {stats['avg_time']:.3f}s")

# 查看最慢的函数
slowest = performance_tracker.get_slowest_functions(5)
for func_name, stats in slowest:
    print(f"{func_name}: {stats['avg_time']:.3f}s")
```

### 3. 内存使用监控

```python
from src.minicrm.core.performance import memory_manager

# 检查内存状态
status = memory_manager.check_memory_status()
print(f"内存状态: {status['status']} ({status['current_mb']:.1f}MB)")

# 如果需要，执行垃圾回收
if status['status'] in ['warning', 'critical']:
    result = memory_manager.force_garbage_collection()
    print(f"释放内存: {result['memory_freed_mb']:.1f}MB")
```

### 4. 缓存效率检查

```python
from src.minicrm.core.performance import global_cache

# 查看缓存统计
stats = global_cache.get_stats()
print(f"缓存命中率: {stats['hit_rate_percent']:.1f}%")
print(f"缓存大小: {stats['size']}/{stats['max_size']}")
```

## 🎯 预期效果

### 立即可见的改进

- **内存使用**: 减少 30-50%
- **响应速度**: 提升 40-60%
- **数据库查询**: 提升 50-80%
- **UI 流畅度**: 显著改善

### 性能指标目标

- UI 操作响应: < 100ms
- 数据库查询: < 200ms
- 报表生成: < 2s
- 应用启动: < 3s
- 内存使用: < 200MB (正常操作)

## 🔍 常见问题

### Q: 性能监控会影响程序性能吗？

A: 监控开销很小（< 1%），生产环境可通过配置关闭详细监控。

### Q: 缓存会占用太多内存吗？

A: 缓存有大小限制和 TTL，会自动清理过期数据。

### Q: 如何调整性能参数？

A: 通过环境变量或修改配置类，无需重新编译。

### Q: 如何在现有代码中集成？

A: 渐进式集成，先添加装饰器和缓存，再优化数据库操作。

## 📚 进阶优化

完成快速优化后，可以参考：

- `docs/PERFORMANCE_OPTIMIZATION.md` - 详细优化指南
- `examples/performance_usage_examples.py` - 完整使用示例
- `src/minicrm/core/performance.py` - 核心性能模块

## 🚀 开始优化

```bash
# 1. 运行性能检查
./scripts/performance-check.sh

# 2. 查看示例代码
python examples/performance_usage_examples.py

# 3. 在你的代码中添加性能监控
# 4. 配置环境变量
# 5. 验证效果

echo "🎉 开始享受更快的MiniCRM！"
```

---

**记住**: 性能优化是一个持续的过程，定期检查和调整配置以获得最佳效果！
