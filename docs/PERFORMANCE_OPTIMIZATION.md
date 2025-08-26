# MiniCRM 性能优化指南

## 🚀 概述

本文档提供 MiniCRM 项目的全面性能优化策略，涵盖内存管理、数据库优化、UI 性能和 Python 特定优化。

## 📊 性能目标

### 响应时间目标

- UI 操作响应: < 100ms
- 数据库查询: < 200ms
- 报表生成: < 2s
- 应用启动: < 3s

### 内存使用目标

- 基础内存占用: < 50MB
- 大数据集处理: < 200MB
- 内存泄漏: 0 tolerance

## 🧠 内存优化策略

### 1. Qt 对象生命周期管理

#### 使用上下文管理器

```python
class QtResourceManager:
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.widgets = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for widget in self.widgets:
            if widget:
                widget.deleteLater()
        self.widgets.clear()
```

#### 智能对象池

```python
class WidgetPool:
    def __init__(self, widget_class, max_size=10):
        self.widget_class = widget_class
        self.pool = []
        self.max_size = max_size

    def get_widget(self):
        if self.pool:
            return self.pool.pop()
        return self.widget_class()

    def return_widget(self, widget):
        if len(self.pool) < self.max_size:
            widget.clear()  # 清理状态
            self.pool.append(widget)
        else:
            widget.deleteLater()
```

### 2. 数据分页和虚拟化

#### 智能分页加载器

```python
class PaginatedDataLoader:
    def __init__(self, dao, page_size=50):
        self.dao = dao
        self.page_size = page_size
        self.cache = {}
        self.cache_size = 5  # 缓存5页数据

    def get_page(self, page_num, filters=None):
        cache_key = (page_num, str(filters))

        if cache_key in self.cache:
            return self.cache[cache_key]

        # 清理缓存
        if len(self.cache) >= self.cache_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        # 加载数据
        offset = (page_num - 1) * self.page_size
        data = self.dao.get_paginated(offset, self.page_size, filters)

        self.cache[cache_key] = data
        return data
```

#### Qt 虚拟化表格

```python
class VirtualizedTableModel(QAbstractTableModel):
    def __init__(self, data_loader):
        super().__init__()
        self.data_loader = data_loader
        self.current_page = 1
        self.page_data = []
        self.total_rows = 0

    def rowCount(self, parent=QModelIndex()):
        return len(self.page_data)

    def canFetchMore(self, parent=QModelIndex()):
        return len(self.page_data) < self.total_rows

    def fetchMore(self, parent=QModelIndex()):
        # 按需加载更多数据
        next_page = self.data_loader.get_page(self.current_page + 1)
        if next_page:
            self.beginInsertRows(parent, len(self.page_data),
                               len(self.page_data) + len(next_page) - 1)
            self.page_data.extend(next_page)
            self.current_page += 1
            self.endInsertRows()
```

### 3. 内存监控和分析

#### 内存使用监控器

```python
import psutil
import gc
from typing import Dict, Any

class MemoryMonitor:
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_usage()

    def get_memory_usage(self) -> Dict[str, float]:
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': self.process.memory_percent()
        }

    def check_memory_leak(self, threshold_mb=50):
        current = self.get_memory_usage()
        increase = current['rss'] - self.baseline_memory['rss']

        if increase > threshold_mb:
            gc.collect()  # 强制垃圾回收
            after_gc = self.get_memory_usage()

            return {
                'leak_detected': True,
                'increase_mb': increase,
                'after_gc_mb': after_gc['rss'],
                'objects_collected': gc.collect()
            }

        return {'leak_detected': False}
```

## 🗄️ 数据库性能优化

### 1. 连接池管理

#### SQLite 连接池

```python
import sqlite3
import threading
from queue import Queue
from contextlib import contextmanager

class SQLiteConnectionPool:
    def __init__(self, database_path, max_connections=5):
        self.database_path = database_path
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self.lock = threading.Lock()

        # 预创建连接
        for _ in range(max_connections):
            conn = sqlite3.connect(database_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")  # 性能优化
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self.pool.put(conn)

    @contextmanager
    def get_connection(self):
        conn = self.pool.get()
        try:
            yield conn
        finally:
            self.pool.put(conn)
```

### 2. 查询优化

#### 智能索引管理

```python
class IndexManager:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.query_stats = {}

    def analyze_query_performance(self, sql, params=None):
        # 使用EXPLAIN QUERY PLAN分析查询
        explain_sql = f"EXPLAIN QUERY PLAN {sql}"
        cursor = self.conn.execute(explain_sql, params or [])
        plan = cursor.fetchall()

        # 检查是否使用了索引
        uses_index = any("USING INDEX" in str(row) for row in plan)

        if not uses_index:
            self.suggest_index(sql)

        return {
            'uses_index': uses_index,
            'query_plan': plan
        }

    def suggest_index(self, sql):
        # 简单的索引建议逻辑
        if "WHERE" in sql.upper():
            # 提取WHERE条件中的列名
            # 这里可以实现更复杂的SQL解析
            print(f"建议为查询创建索引: {sql}")
```

#### 批量操作优化

```python
class BatchOperationManager:
    def __init__(self, connection, batch_size=1000):
        self.conn = connection
        self.batch_size = batch_size

    def batch_insert(self, table, data_list):
        if not data_list:
            return

        # 构建批量插入SQL
        columns = list(data_list[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"

        # 分批执行
        with self.conn:
            for i in range(0, len(data_list), self.batch_size):
                batch = data_list[i:i + self.batch_size]
                values = [tuple(item[col] for col in columns) for item in batch]
                self.conn.executemany(sql, values)

    def batch_update(self, table, updates, key_column='id'):
        if not updates:
            return

        # 使用临时表进行批量更新
        temp_table = f"{table}_temp_update"

        with self.conn:
            # 创建临时表
            self.conn.execute(f"CREATE TEMP TABLE {temp_table} AS SELECT * FROM {table} WHERE 0")

            # 插入更新数据
            self.batch_insert(temp_table, updates)

            # 执行批量更新
            columns = [col for col in updates[0].keys() if col != key_column]
            set_clause = ', '.join([f"{col} = temp.{col}" for col in columns])

            update_sql = f"""
            UPDATE {table}
            SET {set_clause}
            FROM {temp_table} temp
            WHERE {table}.{key_column} = temp.{key_column}
            """

            self.conn.execute(update_sql)
            self.conn.execute(f"DROP TABLE {temp_table}")
```

## 🎨 UI 性能优化

### 1. 异步 UI 更新

#### 后台任务管理器

```python
import threading
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
import asyncio

class BackgroundTaskManager(QObject):
    task_completed = Signal(object)
    task_failed = Signal(str)

    def __init__(self, max_workers=4):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = set()

    def run_task(self, func, *args, **kwargs):
        future = self.executor.submit(func, *args, **kwargs)
        self.active_tasks.add(future)

        def on_done(fut):
            self.active_tasks.discard(fut)
            try:
                result = fut.result()
                self.task_completed.emit(result)
            except Exception as e:
                self.task_failed.emit(str(e))

        future.add_done_callback(on_done)
        return future

    def cancel_all_tasks(self):
        for task in self.active_tasks:
            task.cancel()
        self.active_tasks.clear()
```

#### 渐进式数据加载

```python
class ProgressiveDataLoader(QObject):
    data_chunk_loaded = Signal(list)
    loading_finished = Signal()

    def __init__(self, data_source, chunk_size=100):
        super().__init__()
        self.data_source = data_source
        self.chunk_size = chunk_size
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_next_chunk)
        self.current_offset = 0
        self.is_loading = False

    def start_loading(self):
        if self.is_loading:
            return

        self.is_loading = True
        self.current_offset = 0
        self.timer.start(50)  # 每50ms加载一批数据

    def load_next_chunk(self):
        chunk = self.data_source.get_chunk(self.current_offset, self.chunk_size)

        if not chunk:
            self.timer.stop()
            self.is_loading = False
            self.loading_finished.emit()
            return

        self.data_chunk_loaded.emit(chunk)
        self.current_offset += self.chunk_size
```

### 2. 图表性能优化

#### 高性能图表渲染

```python
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class OptimizedChartWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.figure = plt.figure(figsize=(8, 6))
        super().__init__(self.figure)
        self.setParent(parent)

        # 性能优化设置
        self.figure.patch.set_facecolor('white')
        self.setStyleSheet("background-color: white;")

        # 启用blitting以提高动画性能
        self.ax = self.figure.add_subplot(111)
        self.background = None

    def update_chart_data(self, x_data, y_data, animated=True):
        if animated and self.background is not None:
            # 使用blitting进行快速更新
            self.figure.canvas.restore_region(self.background)

            # 更新数据
            if hasattr(self, 'line'):
                self.line.set_data(x_data, y_data)
                self.ax.draw_artist(self.line)
            else:
                self.line, = self.ax.plot(x_data, y_data, animated=True)

            self.figure.canvas.blit(self.ax.bbox)
        else:
            # 完整重绘
            self.ax.clear()
            self.ax.plot(x_data, y_data)
            self.draw()

            # 保存背景用于后续blitting
            self.background = self.figure.canvas.copy_from_bbox(self.ax.bbox)

    def optimize_for_large_dataset(self, max_points=1000):
        # 对大数据集进行采样
        def downsample_data(x, y, max_points):
            if len(x) <= max_points:
                return x, y

            step = len(x) // max_points
            return x[::step], y[::step]

        return downsample_data
```

## 🐍 Python 特定优化

### 1. 使用**slots**优化内存

#### 优化的数据模型

```python
class OptimizedCustomer:
    __slots__ = ['id', 'name', 'phone', 'email', 'company', 'created_at']

    def __init__(self, id=None, name='', phone='', email='', company='', created_at=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.company = company
        self.created_at = created_at

    def to_dict(self):
        return {slot: getattr(self, slot) for slot in self.__slots__}

    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in cls.__slots__})
```

### 2. 生成器和迭代器优化

#### 内存友好的数据处理

```python
class DataProcessor:
    def __init__(self, dao):
        self.dao = dao

    def process_customers_batch(self, batch_size=1000):
        """使用生成器处理大量客户数据"""
        offset = 0
        while True:
            batch = self.dao.get_customers_batch(offset, batch_size)
            if not batch:
                break

            for customer in batch:
                yield self.process_single_customer(customer)

            offset += batch_size

    def calculate_statistics_streaming(self, data_generator):
        """流式计算统计信息，避免加载所有数据到内存"""
        count = 0
        total = 0
        min_val = float('inf')
        max_val = float('-inf')

        for value in data_generator:
            count += 1
            total += value
            min_val = min(min_val, value)
            max_val = max(max_val, value)

        return {
            'count': count,
            'average': total / count if count > 0 else 0,
            'min': min_val if count > 0 else 0,
            'max': max_val if count > 0 else 0
        }
```

### 3. 缓存策略

#### 智能 LRU 缓存

```python
from functools import lru_cache
import weakref
from typing import Any, Dict

class SmartCache:
    def __init__(self, max_size=128, ttl_seconds=300):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.weak_refs = weakref.WeakValueDictionary()

    def get(self, key):
        if key in self.cache:
            import time
            if time.time() - self.access_times[key] < self.ttl_seconds:
                self.access_times[key] = time.time()
                return self.cache[key]
            else:
                # 过期删除
                del self.cache[key]
                del self.access_times[key]

        return None

    def set(self, key, value):
        import time

        # 清理过期项
        self._cleanup_expired()

        # 如果缓存满了，删除最旧的项
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(),
                           key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        self.cache[key] = value
        self.access_times[key] = time.time()

    def _cleanup_expired(self):
        import time
        current_time = time.time()
        expired_keys = [
            key for key, access_time in self.access_times.items()
            if current_time - access_time >= self.ttl_seconds
        ]

        for key in expired_keys:
            del self.cache[key]
            del self.access_times[key]

# 使用装饰器简化缓存
def cached_method(cache_size=128, ttl=300):
    def decorator(func):
        cache = SmartCache(cache_size, ttl)

        def wrapper(*args, **kwargs):
            # 创建缓存键
            cache_key = str(args) + str(sorted(kwargs.items()))

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            return result

        return wrapper
    return decorator
```

## 📈 性能监控和分析

### 1. 性能分析工具

#### 集成性能分析器

```python
import cProfile
import pstats
import io
from functools import wraps
import time

class PerformanceProfiler:
    def __init__(self):
        self.profiles = {}
        self.timing_data = {}

    def profile_function(self, func_name=None):
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                profiler = cProfile.Profile()
                profiler.enable()

                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    profiler.disable()

                    # 保存性能数据
                    s = io.StringIO()
                    ps = pstats.Stats(profiler, stream=s)
                    ps.sort_stats('cumulative')

                    self.profiles[name] = s.getvalue()
                    self.timing_data[name] = end_time - start_time

            return wrapper
        return decorator

    def get_performance_report(self):
        report = []
        for func_name, timing in self.timing_data.items():
            report.append(f"{func_name}: {timing:.4f}s")

        return "\n".join(report)

    def get_slowest_functions(self, top_n=10):
        sorted_funcs = sorted(self.timing_data.items(),
                            key=lambda x: x[1], reverse=True)
        return sorted_funcs[:top_n]

# 全局性能分析器实例
profiler = PerformanceProfiler()
```

### 2. 实时性能监控

#### 性能监控仪表盘

```python
import tkinter as tk
from tkinter import ttk
import threading
import psutil

class PerformanceMonitorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_monitoring()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # CPU使用率
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)

        # 内存使用率
        self.memory_label = QLabel("Memory: 0 MB")
        self.memory_bar = QProgressBar()
        layout.addWidget(self.memory_label)
        layout.addWidget(self.memory_bar)

        # 数据库连接数
        self.db_connections_label = QLabel("DB Connections: 0")
        layout.addWidget(self.db_connections_label)

        # 缓存命中率
        self.cache_hit_rate_label = QLabel("Cache Hit Rate: 0%")
        layout.addWidget(self.cache_hit_rate_label)

    def setup_monitoring(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(1000)  # 每秒更新

        self.process = psutil.Process()

    def update_metrics(self):
        # CPU使用率
        cpu_percent = self.process.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        self.cpu_bar.setValue(int(cpu_percent))

        # 内存使用
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        self.memory_label.setText(f"Memory: {memory_mb:.1f} MB")

        # 设置内存进度条（假设最大500MB）
        memory_percent = min(memory_mb / 500 * 100, 100)
        self.memory_bar.setValue(int(memory_percent))
```

## 🔧 性能优化配置

### 1. 创建性能配置文件

#### performance_config.py

```python
class PerformanceConfig:
    # 数据库配置
    DB_CONNECTION_POOL_SIZE = 5
    DB_QUERY_TIMEOUT = 30
    DB_BATCH_SIZE = 1000

    # UI配置
    UI_UPDATE_INTERVAL = 50  # ms
    TABLE_PAGE_SIZE = 50
    CHART_MAX_POINTS = 1000

    # 缓存配置
    CACHE_SIZE = 128
    CACHE_TTL = 300  # seconds

    # 内存配置
    MEMORY_WARNING_THRESHOLD = 200  # MB
    MEMORY_CRITICAL_THRESHOLD = 400  # MB

    # 性能监控
    ENABLE_PROFILING = False  # 生产环境设为False
    PROFILE_SLOW_QUERIES = True
    SLOW_QUERY_THRESHOLD = 0.5  # seconds

    @classmethod
    def get_config(cls):
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }
```

## 🚀 实施建议

### 1. 优先级排序

#### 高优先级优化（立即实施）

1. **数据库连接池** - 显著提升数据库性能
2. **分页加载** - 解决大数据集内存问题
3. **Qt 对象生命周期管理** - 防止内存泄漏
4. **基础缓存策略** - 减少重复计算

#### 中优先级优化（短期实施）

1. **异步 UI 更新** - 提升用户体验
2. **批量数据库操作** - 提升数据处理效率
3. **图表渲染优化** - 改善可视化性能
4. **内存监控** - 及时发现性能问题

#### 低优先级优化（长期实施）

1. **高级缓存策略** - 进一步优化性能
2. **代码级优化（**slots**等）** - 细节优化
3. **性能分析工具集成** - 开发工具增强

### 2. 性能测试策略

#### 创建性能测试套件

```python
import unittest
import time
import psutil
from unittest.mock import Mock

class PerformanceTestCase(unittest.TestCase):
    def setUp(self):
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss
        self.start_time = time.time()

    def tearDown(self):
        end_memory = self.process.memory_info().rss
        end_time = time.time()

        memory_increase = (end_memory - self.start_memory) / 1024 / 1024
        execution_time = end_time - self.start_time

        # 性能断言
        self.assertLess(memory_increase, 10, "Memory increase > 10MB")
        self.assertLess(execution_time, 1.0, "Execution time > 1 second")

class DatabasePerformanceTests(PerformanceTestCase):
    def test_large_dataset_query(self):
        # 测试大数据集查询性能
        pass

    def test_batch_insert_performance(self):
        # 测试批量插入性能
        pass

class UIPerformanceTests(PerformanceTestCase):
    def test_table_rendering_performance(self):
        # 测试表格渲染性能
        pass

    def test_chart_update_performance(self):
        # 测试图表更新性能
        pass
```

### 3. 监控和维护

#### 性能监控检查清单

- [ ] 内存使用是否在合理范围内（< 200MB）
- [ ] 数据库查询响应时间（< 200ms）
- [ ] UI 操作响应时间（< 100ms）
- [ ] 缓存命中率（> 80%）
- [ ] 无内存泄漏
- [ ] CPU 使用率合理（< 50%）

#### 定期性能审查

```python
class PerformanceAudit:
    def __init__(self):
        self.metrics = {}

    def run_audit(self):
        results = {
            'memory_usage': self.check_memory_usage(),
            'database_performance': self.check_database_performance(),
            'ui_responsiveness': self.check_ui_responsiveness(),
            'cache_efficiency': self.check_cache_efficiency()
        }

        return self.generate_report(results)

    def check_memory_usage(self):
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        return {
            'current_mb': memory_mb,
            'status': 'good' if memory_mb < 200 else 'warning' if memory_mb < 400 else 'critical'
        }

    def generate_report(self, results):
        report = ["=== 性能审查报告 ===\n"]

        for category, data in results.items():
            report.append(f"{category}: {data['status']}")
            if 'details' in data:
                report.append(f"  详情: {data['details']}")

        return "\n".join(report)
```

## 📋 总结

### 预期性能提升

- **内存使用**: 减少 30-50%
- **启动时间**: 提升 40-60%
- **数据库查询**: 提升 50-80%
- **UI 响应**: 提升 60-90%
- **整体用户体验**: 显著改善

### 关键成功因素

1. **渐进式实施** - 按优先级逐步优化
2. **持续监控** - 建立性能监控体系
3. **测试验证** - 每项优化都要测试验证
4. **文档记录** - 记录优化措施和效果
5. **团队培训** - 确保团队了解性能最佳实践

通过实施这些优化措施，MiniCRM 将获得显著的性能提升，为用户提供更流畅的使用体验。
