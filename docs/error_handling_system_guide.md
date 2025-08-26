# MiniCRM 错误处理和系统监控系统指南

## 概述

MiniCRM 的错误处理和系统监控系统提供了全面的错误管理、系统性能监控和诊断功能。该系统专门为 TTK 界面设计，确保应用程序的稳定性和可靠性。

## 系统架构

### 核心组件

1. **SystemMonitor** - 系统性能监控器
2. **DiagnosticTool** - 系统诊断工具
3. **TTKErrorHandler** - TTK 专用错误处理器
4. **ErrorHandler** - 基础错误处理器

### 组件关系

```
TTKErrorHandler (TTK专用)
    ↓ 继承
ErrorHandler (基础错误处理)
    ↓ 使用
SystemMonitor (性能监控) ← DiagnosticTool (系统诊断)
```

## 功能特性

### 1. 系统监控 (SystemMonitor)

#### 主要功能
- **实时性能监控**: CPU、内存、磁盘使用率
- **应用程序监控**: UI响应时间、数据库响应时间、内存使用
- **健康检查**: 系统资源、应用性能、数据库连接
- **性能报告**: 生成详细的性能分析报告
- **智能建议**: 基于监控数据提供优化建议

#### 使用示例

```python
from src.minicrm.core.system_monitor import get_system_monitor, start_system_monitoring

# 获取监控器实例
monitor = get_system_monitor()

# 启动监控
start_system_monitoring()

# 运行健康检查
health_results = monitor.run_health_check()

# 生成性能报告
report = monitor.generate_performance_report(hours=24)

# 导出报告
monitor.export_report("performance_report.json", hours=24)
```

#### 监控指标

**系统指标**:
- CPU 使用率
- 内存使用率和可用内存
- 磁盘使用率和可用空间
- 进程数和线程数

**应用程序指标**:
- 应用内存使用
- UI 响应时间
- 数据库响应时间
- 活动窗口数
- 错误计数

### 2. 系统诊断 (DiagnosticTool)

#### 主要功能
- **环境检查**: 操作系统、Python版本、依赖库
- **配置验证**: 配置文件格式和完整性
- **数据库检查**: 连接性和基本操作
- **性能分析**: 响应时间和系统资源
- **UI组件检查**: TTK组件和主题支持
- **权限检查**: 文件读写权限

#### 使用示例

```python
from src.minicrm.core.diagnostic_tool import run_system_diagnosis, get_diagnostic_tool

# 运行完整诊断
results = run_system_diagnosis()

# 获取诊断工具实例
diagnostic = get_diagnostic_tool()

# 生成诊断报告
report = diagnostic.generate_report()

# 导出报告
diagnostic.export_report("diagnostic_report.json", format="json")
```

#### 诊断类别

1. **系统信息**: 操作系统兼容性、系统架构
2. **Python环境**: 版本检查、可执行文件路径
3. **依赖库**: 必需和可选模块检查
4. **数据库**: SQLite连接和操作测试
5. **配置文件**: JSON/Python配置文件验证
6. **性能状态**: 响应时间和监控状态
7. **UI组件**: TTK组件和主题支持
8. **文件权限**: 读写权限检查

### 3. TTK错误处理 (TTKErrorHandler)

#### 主要功能
- **UI操作保护**: 自动捕获和处理UI操作错误
- **错误分类**: 智能分类UI相关错误
- **用户友好提示**: 显示易懂的错误消息
- **自动恢复**: 尝试自动恢复常见错误
- **线程安全**: 支持多线程环境下的错误处理

#### 使用示例

```python
from src.minicrm.core.ttk_error_handler import get_ttk_error_handler, handle_ui_operation

# 获取错误处理器
error_handler = get_ttk_error_handler(parent_window)

# UI操作保护
with handle_ui_operation("create_widget", widget_type="Button"):
    button = ttk.Button(parent, text="测试")

# 显示验证错误
error_handler.show_validation_error("用户名", "用户名不能为空")

# 显示业务错误
error_handler.show_business_error("保存数据", "数据库连接失败")

# 确认操作
if error_handler.confirm_operation("删除", "确认删除此项目？"):
    # 执行删除操作
    pass
```

#### 错误恢复机制

**自动恢复策略**:
- **布局错误**: 重置布局管理器
- **样式错误**: 使用默认样式
- **组件错误**: 延迟重试创建
- **事件错误**: 跳过事件绑定

**恢复回调注册**:
```python
def custom_recovery(error_info):
    # 自定义恢复逻辑
    return True

error_handler.register_recovery_callback("custom_component", custom_recovery)
```

### 4. 基础错误处理 (ErrorHandler)

#### 错误分类

- **ValidationError**: 数据验证错误
- **FileFormatError**: 文件格式错误
- **DatabaseError**: 数据库操作错误
- **NetworkError**: 网络连接错误
- **PermissionError**: 权限错误
- **BusinessLogicError**: 业务逻辑错误
- **SystemError**: 系统错误
- **UserInputError**: 用户输入错误
- **TimeoutError**: 超时错误

#### 严重程度

- **LOW**: 低级错误，可以继续处理
- **MEDIUM**: 中级错误，需要用户注意
- **HIGH**: 高级错误，需要停止当前操作
- **CRITICAL**: 严重错误，需要立即处理

## 配置和自定义

### 监控配置

```python
# 设置监控间隔
monitor.set_monitoring_interval(10.0)  # 10秒

# 设置性能阈值
monitor.set_threshold("cpu_warning", 80.0)
monitor.set_threshold("memory_critical", 95.0)

# 注册自定义健康检查
def custom_health_check():
    return HealthCheckResult("custom", "healthy", "自定义检查通过")

monitor.register_health_check("custom_check", custom_health_check)
```

### 错误处理策略

```python
# 设置错误处理策略
error_handler.set_error_strategy(ErrorType.VALIDATION_ERROR, ErrorAction.SKIP)

# 注册错误恢复回调
error_handler.register_recovery_callback("widget", recovery_function)
```

## 性能优化

### 监控优化
- 使用合适的监控间隔（默认5秒）
- 限制历史数据大小（默认1000条）
- 异步数据收集，不阻塞主线程

### 错误处理优化
- 智能错误分类，减少处理开销
- 缓存恢复策略，提高响应速度
- 线程安全设计，支持并发操作

## 最佳实践

### 1. 监控使用
```python
# 应用启动时启动监控
start_system_monitoring()

# 定期运行健康检查
health_results = run_health_check()

# 应用关闭时停止监控
stop_system_monitoring()
```

### 2. 错误处理
```python
# 保护重要的UI操作
with handle_ui_operation("critical_operation"):
    # 执行可能出错的操作
    pass

# 为用户提供友好的错误提示
error_handler.show_validation_error("字段名", "具体错误信息")
```

### 3. 诊断使用
```python
# 应用启动时运行诊断
results = run_system_diagnosis()
failed_checks = [r for r in results if r.status == "fail"]

if failed_checks:
    # 处理诊断失败的项目
    pass
```

## 故障排除

### 常见问题

1. **监控无法启动**
   - 检查 psutil 库是否安装
   - 确认系统权限

2. **错误对话框不显示**
   - 检查父窗口设置
   - 确认在主线程中调用

3. **诊断检查失败**
   - 查看具体错误信息
   - 按照建议进行修复

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看错误统计
stats = error_handler.get_ui_error_statistics()
print(f"错误统计: {stats}")

# 生成错误报告
report = error_handler.create_error_report()
print(report)
```

## 扩展开发

### 添加自定义监控指标

```python
class CustomMonitor(SystemMonitor):
    def _collect_custom_metrics(self):
        # 收集自定义指标
        pass
```

### 添加自定义诊断检查

```python
def custom_diagnostic_check():
    # 执行自定义检查
    return DiagnosticResult("custom", "check_name", "pass", "检查通过")

diagnostic_tool.register_custom_check("custom_check", custom_diagnostic_check)
```

### 添加自定义错误处理

```python
class CustomErrorHandler(TTKErrorHandler):
    def handle_custom_error(self, error):
        # 处理自定义错误
        pass
```

## 总结

MiniCRM 的错误处理和系统监控系统提供了全面的应用程序健康管理功能。通过合理使用这些工具，可以显著提高应用程序的稳定性、可靠性和用户体验。

系统的模块化设计使得各个组件可以独立使用，也可以组合使用以获得最佳效果。建议在开发和生产环境中都启用这些功能，以便及时发现和解决问题。
