# MiniCRM性能基准测试系统

为任务10（性能基准测试）提供完整的Qt vs TTK性能对比测试解决方案。

## 概述

本测试系统旨在验证MiniCRM从Qt框架迁移到TTK框架后的性能表现，确保满足所有性能需求（需求11.1-11.6），并提供详细的性能分析和优化建议。

## 性能需求基准

根据需求文档11.1-11.6，系统需要满足以下性能标准：

- **启动时间**: ≤ 3秒 (需求11.1)
- **响应时间**: ≤ 200毫秒 (需求11.2)
- **内存占用**: ≤ 200MB (需求11.3)
- **CPU占用**: ≤ 10% (需求11.4)
- **虚拟滚动**: 流畅处理大数据集 (需求11.5)
- **页面切换**: ≤ 100毫秒 (需求11.6)

## 测试架构

```
tests/performance/
├── performance_benchmark_framework.py    # 基础测试框架
├── startup_performance_test.py          # 启动性能测试
├── memory_usage_benchmark.py            # 内存使用测试
├── performance_report_generator.py      # 报告生成器
├── main_performance_test.py             # 主测试运行器
└── run_performance_benchmarks.py        # 独立运行器
```

## 快速开始

### 1. 环境准备

```bash
# 安装必要依赖
pip install psutil

# 安装可选依赖（用于图表和PDF生成）
pip install matplotlib reportlab
```

### 2. 运行测试

```bash
# 方式1: 使用快速启动脚本
python run_performance_tests.py

# 方式2: 直接运行主测试
python tests/performance/main_performance_test.py

# 方式3: 运行独立基准测试
python tests/performance/run_performance_benchmarks.py
```

### 3. 查看报告

测试完成后，报告文件将生成在 `reports/` 目录中：

- `performance_report_YYYYMMDD_HHMMSS.html` - 可视化HTML报告
- `performance_report_YYYYMMDD_HHMMSS.json` - 详细JSON数据
- `performance_report_YYYYMMDD_HHMMSS.pdf` - 正式PDF报告（需要reportlab）
- `performance_charts_YYYYMMDD_HHMMSS.png` - 性能对比图表（需要matplotlib）
- `executive_summary_YYYYMMDD_HHMMSS.txt` - 执行摘要

## 测试模块详解

### 1. 启动性能测试 (startup_performance_test.py)

测试应用程序启动的各个阶段：

- **模块导入时间**: 核心模块、UI模块导入耗时
- **数据库初始化**: 数据库连接和初始化时间
- **服务层初始化**: 各业务服务启动时间
- **应用程序创建**: Qt/TTK应用实例创建时间

```python
# 运行启动性能测试
from tests.performance.startup_performance_test import run_startup_performance_tests
run_startup_performance_tests()
```

### 2. 内存使用测试 (memory_usage_benchmark.py)

监控内存使用模式：

- **基础内存占用**: 应用程序基础内存使用
- **大数据集处理**: 处理大量数据时的内存效率
- **内存泄漏检测**: 检测潜在的内存泄漏问题
- **垃圾回收效果**: 分析垃圾回收的有效性

```python
# 运行内存使用测试
from tests.performance.memory_usage_benchmark import run_memory_usage_tests
run_memory_usage_tests()
```

### 3. 性能基准框架 (performance_benchmark_framework.py)

提供统一的测试基础设施：

- **BaseBenchmark**: 基准测试基类
- **PerformanceMonitor**: 实时性能监控
- **PerformanceMetrics**: 性能指标数据结构
- **BenchmarkResult**: 测试结果封装

### 4. 报告生成系统 (performance_report_generator.py)

生成多格式的性能报告：

- **HTML报告**: 交互式可视化报告
- **PDF报告**: 正式文档格式报告
- **图表生成**: 性能对比图表
- **执行摘要**: 简洁的结果总结

## 命令行选项

### 主测试运行器选项

```bash
python tests/performance/main_performance_test.py [选项]

选项:
  --output-dir DIR     报告输出目录 (默认: reports)
  --verbose           详细输出
  --no-charts         不生成图表
  --no-pdf           不生成PDF报告
```

### 独立基准测试选项

```bash
python tests/performance/run_performance_benchmarks.py [选项]

选项:
  --output-dir DIR     报告输出目录 (默认: reports)
  --format FORMAT     报告格式 (json|html|both, 默认: both)
  --verbose           详细输出
```

## 测试结果解读

### 性能指标说明

- **启动时间 (startup_time)**: 应用程序从启动到可用的总时间
- **峰值内存 (peak_memory)**: 测试期间的最大内存使用量
- **内存增长 (memory_growth)**: 相对于初始内存的增长量
- **平均CPU使用 (avg_cpu_usage)**: 测试期间的平均CPU占用率
- **UI响应时间 (ui_response_time)**: UI操作的平均响应时间
- **操作速度 (operations_per_second)**: 每秒可执行的操作数

### 合规性检查

系统会自动检查TTK版本是否满足性能需求：

- ✅ **合规**: 所有指标都满足要求
- ⚠️ **部分合规**: 大部分指标满足，少数需要优化
- ❌ **不合规**: 多项指标不满足，需要重点优化

### 性能对比分析

报告会提供Qt vs TTK的详细对比：

- **改善**: TTK版本性能优于Qt版本
- **退化**: TTK版本性能低于Qt版本
- **持平**: 两个版本性能相当

## 优化建议

系统会根据测试结果自动生成优化建议：

### 启动性能优化
- 实现延迟加载机制
- 减少启动时的模块导入
- 优化数据库连接初始化
- 使用异步初始化

### 内存优化
- 实现对象池机制
- 及时释放不用的资源
- 优化数据结构
- 使用弱引用避免循环引用

### UI响应优化
- 使用虚拟滚动处理大数据
- 实现异步数据加载
- 优化UI更新频率
- 使用数据分页

## 扩展测试

### 添加自定义测试

```python
from tests.performance.performance_benchmark_framework import BaseBenchmark, PerformanceMetrics

class CustomBenchmark(BaseBenchmark):
    def __init__(self):
        super().__init__("custom_test")

    def run_qt_test(self) -> PerformanceMetrics:
        metrics = PerformanceMetrics()
        # 实现Qt版本测试逻辑
        return metrics

    def run_ttk_test(self) -> PerformanceMetrics:
        metrics = PerformanceMetrics()
        # 实现TTK版本测试逻辑
        return metrics
```

### 自定义性能指标

```python
# 在PerformanceMetrics中添加自定义指标
metrics.additional_metrics["custom_metric"] = custom_value
```

## 故障排除

### 常见问题

1. **导入错误**
   ```
   ImportError: No module named 'psutil'
   ```
   解决方案: `pip install psutil`

2. **图表生成失败**
   ```
   matplotlib不可用，跳过图表生成
   ```
   解决方案: `pip install matplotlib`

3. **PDF生成失败**
   ```
   reportlab不可用，跳过PDF报告生成
   ```
   解决方案: `pip install reportlab`

4. **内存不足**
   ```
   MemoryError during large dataset test
   ```
   解决方案: 减少测试数据量或增加系统内存

### 调试模式

```bash
# 启用详细日志
python tests/performance/main_performance_test.py --verbose

# 查看具体错误信息
python -u tests/performance/main_performance_test.py 2>&1 | tee test.log
```

## 持续集成

### GitHub Actions示例

```yaml
name: Performance Tests
on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install psutil matplotlib reportlab
    - name: Run performance tests
      run: |
        python run_performance_tests.py --output-dir ci-reports
    - name: Upload reports
      uses: actions/upload-artifact@v2
      with:
        name: performance-reports
        path: ci-reports/
```

## 贡献指南

### 添加新的性能测试

1. 继承 `BaseBenchmark` 类
2. 实现 `run_qt_test()` 和 `run_ttk_test()` 方法
3. 在主测试套件中注册新测试
4. 添加相应的单元测试
5. 更新文档

### 代码规范

- 遵循PEP 8代码风格
- 添加详细的文档字符串
- 包含类型注解
- 编写单元测试

## 许可证

本项目遵循MIT许可证。详见LICENSE文件。

## 联系方式

如有问题或建议，请联系MiniCRM开发团队。
