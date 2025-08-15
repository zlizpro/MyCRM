# MiniCRM 代码质量规范和Hooks系统

## Python代码规范

### 1. 代码风格标准
```python
# 遵循PEP 8标准
# 使用4个空格缩进
# 行长度限制为88字符（Black格式化器标准）
# 使用有意义的变量和函数名

# 示例：
class CustomerManager:
    """客户管理器类
    
    负责处理客户相关的业务逻辑，包括客户信息的增删改查、
    客户等级管理和客户数据分析等功能。
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """初始化客户管理器
        
        Args:
            database_manager: 数据库管理器实例
        """
        self._db_manager = database_manager
        self._logger = logging.getLogger(__name__)
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Optional[int]:
        """创建新客户
        
        Args:
            customer_data: 客户数据字典，包含姓名、电话等信息
            
        Returns:
            创建成功返回客户ID，失败返回None
            
        Raises:
            ValidationError: 当客户数据验证失败时
            DatabaseError: 当数据库操作失败时
        """
        try:
            # 验证客户数据
            self._validate_customer_data(customer_data)
            
            # 保存到数据库
            customer_id = self._db_manager.insert_customer(customer_data)
            
            self._logger.info(f"成功创建客户，ID: {customer_id}")
            return customer_id
            
        except ValidationError as e:
            self._logger.error(f"客户数据验证失败: {e}")
            raise
        except DatabaseError as e:
            self._logger.error(f"数据库操作失败: {e}")
            raise
```

### 2. 文档字符串规范
```python
# 使用Google风格的docstring
def calculate_customer_value(
    self, 
    customer_id: int, 
    time_period: int = 12
) -> Tuple[float, Dict[str, float]]:
    """计算客户价值
    
    基于客户的交易历史、互动频率和合作时长等因素，
    计算客户的综合价值评分。
    
    Args:
        customer_id: 客户ID
        time_period: 计算时间段（月），默认12个月
        
    Returns:
        包含客户价值评分和详细指标的元组:
        - float: 客户价值评分 (0-100)
        - Dict[str, float]: 详细指标字典
            - 'transaction_value': 交易价值
            - 'interaction_score': 互动评分
            - 'loyalty_score': 忠诚度评分
            
    Raises:
        CustomerNotFoundError: 当客户不存在时
        InsufficientDataError: 当数据不足以计算时
        
    Example:
        >>> manager = CustomerManager(db)
        >>> score, details = manager.calculate_customer_value(123)
        >>> print(f"客户价值评分: {score}")
        >>> print(f"交易价值: {details['transaction_value']}")
    """
```

### 3. 类型注解规范
```python
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# 使用数据类定义数据结构
@dataclass
class Customer:
    """客户数据类"""
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    level: CustomerLevel = CustomerLevel.NORMAL
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# 使用枚举定义常量
class CustomerLevel(Enum):
    """客户等级枚举"""
    VIP = "vip"
    IMPORTANT = "important"
    NORMAL = "normal"
    POTENTIAL = "potential"

# 函数类型注解
def search_customers(
    query: str,
    filters: Dict[str, Any],
    page: int = 1,
    page_size: int = 20
) -> Tuple[List[Customer], int]:
    """搜索客户"""
    pass
```

### 4. 异常处理规范
```python
# 自定义异常类
class MiniCRMError(Exception):
    """MiniCRM基础异常类"""
    pass

class ValidationError(MiniCRMError):
    """数据验证异常"""
    pass

class DatabaseError(MiniCRMError):
    """数据库操作异常"""
    pass

class BusinessLogicError(MiniCRMError):
    """业务逻辑异常"""
    pass

# 异常处理示例
def update_customer(self, customer_id: int, data: Dict[str, Any]) -> bool:
    """更新客户信息"""
    try:
        # 验证数据
        if not self._validate_customer_data(data):
            raise ValidationError("客户数据格式不正确")
        
        # 检查客户是否存在
        if not self._customer_exists(customer_id):
            raise BusinessLogicError(f"客户不存在: {customer_id}")
        
        # 更新数据库
        result = self._db_manager.update_customer(customer_id, data)
        if not result:
            raise DatabaseError("数据库更新失败")
            
        return True
        
    except (ValidationError, BusinessLogicError) as e:
        self._logger.warning(f"业务异常: {e}")
        raise
    except DatabaseError as e:
        self._logger.error(f"数据库异常: {e}")
        raise
    except Exception as e:
        self._logger.error(f"未知异常: {e}")
        raise MiniCRMError(f"更新客户失败: {e}")
```

## 项目目录结构

```
minicrm/
├── main.py                 # 应用程序入口
├── config/                 # 配置文件
│   ├── __init__.py
│   ├── settings.py         # 应用设置
│   └── database.py         # 数据库配置
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── exceptions.py       # 自定义异常
│   ├── constants.py        # 常量定义
│   └── utils.py           # 工具函数
├── models/                 # 数据模型
│   ├── __init__.py
│   ├── customer.py         # 客户模型
│   ├── supplier.py         # 供应商模型
│   └── base.py            # 基础模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── customer_service.py # 客户服务
│   ├── supplier_service.py # 供应商服务
│   └── analytics_service.py# 分析服务
├── data/                   # 数据访问层
│   ├── __init__.py
│   ├── database.py         # 数据库管理
│   ├── dao/               # 数据访问对象
│   │   ├── __init__.py
│   │   ├── customer_dao.py
│   │   └── supplier_dao.py
│   └── migrations/         # 数据库迁移
├── ui/                     # 用户界面
│   ├── __init__.py
│   ├── main_window.py      # 主窗口
│   ├── components/         # UI组件
│   │   ├── __init__.py
│   │   ├── d
│   │   ├── customer_panel.py
│   │   └── charts.py
│   └── themes/            # 主题样式
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── test_services/
│   ├── test_models/
│   └── test_ui/
├── docs/                   # 文档
├── requirements.txt        # 依赖列表
├── setup.py               # 安装脚本
└── README.md              # 项目说明
```

## Hooks系统设计

### 1. 应用程序生命周期Hooks

```python
class ApplicationHooks:
    """应用程序钩子管理器"""
    
    def __init__(self):
        self._startup_hooks: List[Callable] = []
        self._shutdown_hooks: List[Callable] = []
        self._error_hooks: List[Callable] = []
    
    def on_startup(self, func: Callable) -> Callable:
        """注册启动钩子"""
        self._startup_hooks.append(func)
        return func
    
    def on_shutdown(self, func: Callable) -> Callable:
        """注册关闭钩子"""
        self._shutdown_hooks.append(func)
        return func
    
    def on_error(self, func: Callable) -> Callable:
        """注册错误处理钩子"""
        self._error_hooks.append(func)
        return func

# 使用示例
app_hooks = ApplicationHooks()

@app_hooks.on_startup
def initialize_database():
    """初始化数据库连接"""
    logger.info("正在初始化数据库...")
    # 数据库初始化逻辑

@app_hooks.on_startup
def load_user_preferences():
    """加载用户偏好设置"""
    logger.info("正在加载用户设置...")
    # 加载设置逻辑

@app_hooks.on_shutdown
def cleanup_resources():
    """清理资源"""
    logger.info("正在清理资源...")
    # 资源清理逻辑
```

### 2. 数据库操作Hooks

```python
class DatabaseHooks:
    """数据库操作钩子"""
    
    def __init__(self):
        self._before_insert_hooks: Dict[str, List[Callable]] = {}
        self._after_insert_hooks: Dict[str, List[Callable]] = {}
        self._before_update_hooks: Dict[str, List[Callable]] = {}
        self._after_update_hooks: Dict[str, List[Callable]] = {}
        self._before_delete_hooks: Dict[str, List[Callable]] = {}
        self._after_delete_hooks: Dict[str, List[Callable]] = {}
    
    def before_insert(self, table: str):
        """插入前钩子装饰器"""
        def decorator(func: Callable):
            if table not in self._before_insert_hooks:
                self._before_insert_hooks[table] = []
            self._before_insert_hooks[table].append(func)
            return func
        return decorator
    
    def after_insert(self, table: str):
        """插入后钩子装饰器"""
        def decorator(func: Callable):
            if table not in self._after_insert_hooks:
                self._after_insert_hooks[table] = []
            self._after_insert_hooks[table].append(func)
            return func
        return decorator

# 使用示例
db_hooks = DatabaseHooks()

@db_hooks.before_insert('customers')
def validate_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """客户数据插入前验证"""
    # 数据验证逻辑
    if not data.get('name'):
        raise ValidationError("客户名称不能为空")
    return data

@db_hooks.after_insert('customers')
def log_customer_creation(customer_id: int, data: Dict[str, Any]):
    """记录客户创建日志"""
    logger.info(f"新客户创建成功: {customer_id}, 名称: {data.get('name')}")

@db_hooks.after_insert('customers')
def send_welcome_notification(customer_id: int, data: Dict[str, Any]):
    """发送欢迎通知"""
    # 发送通知逻辑
    pass
```

### 3. UI事件Hooks

```python
class UIHooks:
    """UI事件钩子管理器"""
    
    def __init__(self):
        self._window_hooks: Dict[str, List[Callable]] = {}
        self._form_hooks: Dict[str, List[Callable]] = {}
        self._data_hooks: Dict[str, List[Callable]] = {}
    
    def on_window_event(self, event_type: str):
        """窗口事件钩子"""
        def decorator(func: Callable):
            if event_type not in self._window_hooks:
                self._window_hooks[event_type] = []
            self._window_hooks[event_type].append(func)
            return func
        return decorator
    
    def on_form_event(self, form_name: str, event_type: str):
        """表单事件钩子"""
        def decorator(func: Callable):
            key = f"{form_name}_{event_type}"
            if key not in self._form_hooks:
                self._form_hooks[key] = []
            self._form_hooks[key].append(func)
            return func
        return decorator

# 使用示例
ui_hooks = UIHooks()

@ui_hooks.on_window_event('window_close')
def confirm_exit():
    """退出确认"""
    if messagebox.askyesno("确认", "确定要退出MiniCRM吗？"):
        return True
    return False

@ui_hooks.on_form_event('customer_form', 'before_save')
def validate_customer_form(form_data: Dict[str, Any]) -> bool:
    """客户表单保存前验证"""
    if not form_data.get('name'):
        messagebox.showerror("错误", "客户名称不能为空")
        return False
    return True

@ui_hooks.on_form_event('customer_form', 'after_save')
def refresh_customer_list(customer_id: int):
    """保存后刷新客户列表"""
    # 刷新列表逻辑
    pass
```

### 4. 业务逻辑Hooks

```python
class BusinessHooks:
    """业务逻辑钩子管理器"""
    
    def __init__(self):
        self._workflow_hooks: Dict[str, Dict[str, List[Callable]]] = {}
    
    def on_workflow_step(self, workflow: str, step: str):
        """工作流步骤钩子"""
        def decorator(func: Callable):
            if workflow not in self._workflow_hooks:
                self._workflow_hooks[workflow] = {}
            if step not in self._workflow_hooks[workflow]:
                self._workflow_hooks[workflow][step] = []
            self._workflow_hooks[workflow][step].append(func)
            return func
        return decorator

# 使用示例
business_hooks = BusinessHooks()

@business_hooks.on_workflow_step('customer_onboarding', 'after_create')
def setup_customer_defaults(customer_id: int):
    """客户创建后设置默认值"""
    # 设置默认客户等级
    # 创建初始互动记录
    pass

@business_hooks.on_workflow_step('quote_process', 'before_send')
def validate_quote(quote_id: int) -> bool:
    """报价发送前验证"""
    # 验证报价完整性
    # 检查价格合理性
    return True

@business_hooks.on_workflow_step('contract_process', 'after_sign')
def activate_contract(contract_id: int):
    """合同签署后激活"""
    # 更新合同状态
    # 创建执行任务
    # 发送通知
    pass
```

### 5. 性能监控Hooks

```python
import time
import functools
from typing import Dict, Any

class PerformanceHooks:
    """性能监控钩子管理器"""
    
    def __init__(self):
        self._performance_data: Dict[str, List[float]] = {}
        self._slow_query_threshold = 1.0  # 1秒
    
    def monitor_performance(self, operation_name: str):
        """性能监控装饰器"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    # 记录性能数据
                    if operation_name not in self._performance_data:
                        self._performance_data[operation_name] = []
                    self._performance_data[operation_name].append(duration)
                    
                    # 慢查询警告
                    if duration > self._slow_query_threshold:
                        logger.warning(
                            f"慢操作检测: {operation_name} 耗时 {duration:.2f}秒"
                        )
            return wrapper
        return decorator
    
    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """获取性能统计信息"""
        stats = {}
        for operation, durations in self._performance_data.items():
            if durations:
                stats[operation] = {
                    'count': len(durations),
                    'total': sum(durations),
                    'average': sum(durations) / len(durations),
                    'min': min(durations),
                    'max': max(durations)
                }
        return stats

# 使用示例
perf_hooks = PerformanceHooks()

@perf_hooks.monitor_performance('database_query')
def execute_query(sql: str, params: tuple = None):
    """执行数据库查询"""
    # 数据库查询逻辑
    pass

@perf_hooks.monitor_performance('ui_render')
def render_customer_list(customers: List[Customer]):
    """渲染客户列表"""
    # UI渲染逻辑
    pass
```

### 6. 日志和审计Hooks

```python
class AuditHooks:
    """操作审计钩子管理器"""
    
    def __init__(self):
        self._audit_logger = logging.getLogger('audit')
    
    def audit_operation(self, operation_type: str, resource_type: str):
        """操作审计装饰器"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 记录操作开始
                self._audit_logger.info(
                    f"操作开始: {operation_type} {resource_type}"
                )
                
                try:
                    result = func(*args, **kwargs)
                    
                    # 记录操作成功
                    self._audit_logger.info(
                        f"操作成功: {operation_type} {resource_type}"
                    )
                    
                    return result
                    
                except Exception as e:
                    # 记录操作失败
                    self._audit_logger.error(
                        f"操作失败: {operation_type} {resource_type}, 错误: {e}"
                    )
                    raise
                    
            return wrapper
        return decorator

# 使用示例
audit_hooks = AuditHooks()

@audit_hooks.audit_operation('CREATE', 'CUSTOMER')
def create_customer(customer_data: Dict[str, Any]) -> int:
    """创建客户"""
    # 客户创建逻辑
    pass

@audit_hooks.audit_operation('UPDATE', 'CUSTOMER')
def update_customer(customer_id: int, data: Dict[str, Any]) -> bool:
    """更新客户"""
    # 客户更新逻辑
    pass

@audit_hooks.audit_operation('DELETE', 'CUSTOMER')
def delete_customer(customer_id: int) -> bool:
    """删除客户"""
    # 客户删除逻辑
    pass
```

## 依赖管理

### requirements.txt
```
# GUI框架
tkinter  # 内置库

# 数据处理
pandas>=1.5.0
numpy>=1.21.0
openpyxl>=3.0.0

# 图表绘制
matplotlib>=3.5.0
Pillow>=9.0.0

# 文档处理
python-docx>=0.8.11
docxtpl>=0.16.0
reportlab>=3.6.0

# 数据库
sqlite3  # 内置库

# 工具库
jinja2>=3.1.0
python-dateutil>=2.8.0

# 开发工具
black>=22.0.0
flake8>=4.0.0
mypy>=0.950
pytest>=7.0.0

# 打包部署
PyInstaller>=5.0.0
```

这套完整的代码质量规范和Hooks系统现在已经生成并可以导入到您的项目中。它包含了：

1. **完整的Python编码规范** - PEP 8标准、类型注解、文档字符串
2. **项目结构标准** - 清晰的目录组织和模块划分
3. **7种核心Hooks系统** - 应用生命周期、数据库操作、UI事件、业务逻辑、性能监控、审计日志
4. **依赖管理** - 完整的requirements.txt文件

您可以在开始实施任务时直接使用这些规范和系统！
