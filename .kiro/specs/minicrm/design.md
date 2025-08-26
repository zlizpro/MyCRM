# MiniCRM 设计文档

## 概述

MiniCRM是一个基于Python和tkinter/ttk的跨平台客户关系管理系统，支持macOS和Windows平台。系统采用现代化的TTK GUI设计，提供完整的客户和供应商管理功能，包括数据仪表盘、业务流程管理和智能分析功能。

## 架构设计

### 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    MiniCRM 应用架构                          │
├─────────────────────────────────────────────────────────────┤
│  表示层 (Presentation Layer)                                │
│  ├── 主窗口管理器 (MainWindow)                               │
│  ├── 仪表盘界面 (Dashboard)                                 │
│  ├── 客户管理界面 (CustomerUI)                              │
│  ├── 供应商管理界面 (SupplierUI)                            │
│  ├── 报表界面 (ReportsUI)                                   │
│  └── 设置界面 (SettingsUI)                                  │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Business Logic Layer)                          │
│  ├── 客户管理服务 (CustomerService)                         │
│  ├── 供应商管理服务 (SupplierService)                       │
│  ├── 财务管理服务 (FinanceService)                          │
│  ├── 文档管理服务 (DocumentService)                         │
│  └── 分析服务 (AnalyticsService)                            │
├─────────────────────────────────────────────────────────────┤
│  数据访问层 (Data Access Layer)                             │
│  ├── 数据库管理器 (DatabaseManager)                         │
│  ├── 客户数据访问 (CustomerDAO)                             │
│  ├── 供应商数据访问 (SupplierDAO)                           │
│  └── 系统数据访问 (SystemDAO)                               │
├─────────────────────────────────────────────────────────────┤
│  数据存储层 (Data Storage Layer)                            │
│  ├── SQLite 数据库                                          │
│  ├── 配置文件 (JSON)                                        │
│  ├── 模板文件 (Word/Excel)                                  │
│  └── 备份文件                                               │
└─────────────────────────────────────────────────────────────┘
```

## 用户界面设计

### 主窗口布局
```
┌─────────────────────────────────────────────────────────────┐
│  MiniCRM - 客户管理系统                    [_][□][×] │
├─────────────────────────────────────────────────────────────┤
│  菜单栏: 文件 | 编辑 | 视图 | 工具 | 帮助                    │
├─────────────────────────────────────────────────────────────┤
│  工具栏: [新建] [保存] [导入] [导出] [设置] [帮助]           │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │
│ │  导航面板   │ │              主内容区域                 │ │
│ │             │ │                                         │ │
│ │ 📊 仪表盘   │ │  根据左侧导航选择显示不同的功能界面     │ │
│ │ 👥 客户管理 │ │                                         │ │
│ │ 🏭 供应商   │ │  - 仪表盘：图表和关键指标               │ │
│ │ 💰 财务管理 │ │  - 客户管理：客户列表和详情             │ │
│ │ 📄 合同管理 │ │  - 供应商：供应商列表和详情             │ │
│ │ 📊 报表分析 │ │  - 其他功能模块界面                     │ │
│ │ ⚙️  系统设置 │ │                                         │ │
│ │             │ │                                         │ │
│ └─────────────┘ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  状态栏: 就绪 | 数据库连接正常 | 最后同步: 2025-01-15 10:30  │
└─────────────────────────────────────────────────────────────┘
```

### 仪表盘界面设计
```
┌─────────────────────────────────────────────────────────────┐
│                        数据仪表盘                           │
├─────────────────────────────────────────────────────────────┤
│  关键指标卡片区域                                           │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │客户总数 │ │新增客户 │ │待办任务 │ │应收账款 │ │应付账款 │ │
│ │  156   │ │   12   │ │   8    │ │ ¥50.2K │ │ ¥32.1K │ │
│ │  个    │ │  本月   │ │  项    │ │        │ │        │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────────────────────────────┤
│  图表区域                                                   │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │   客户增长趋势图    │ │      客户类型分布饼图           │ │
│ │                     │ │                                 │ │
│ │  📈 折线图显示      │ │   🥧 饼图显示各类型客户占比     │ │
│ │                     │ │                                 │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │  月度互动频率图     │ │      应收账款状态图             │ │
│ │                     │ │                                 │ │
│ │  📊 柱状图显示      │ │   📊 堆叠柱状图显示账款状态     │ │
│ │                     │ │                                 │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  快速操作区域                                               │
│  [新增客户] [新增供应商] [创建报价] [记录收款] [查看报表]    │
└─────────────────────────────────────────────────────────────┘
```

### 客户管理界面设计
```
┌─────────────────────────────────────────────────────────────┐
│                        客户管理                             │
├─────────────────────────────────────────────────────────────┤
│  搜索和筛选区域                                             │
│  🔍 [搜索框: 输入客户名称、电话等]  [高级筛选 ▼]           │
│  筛选: [客户等级 ▼] [客户类型 ▼] [地区 ▼] [产品类别 ▼]     │
├─────────────────────────────────────────────────────────────┤
│  操作按钮区域                                               │
│  [➕ 新增客户] [📤 导入] [📥 导出] [🔄 刷新]                │
├─────────────────────────────────────────────────────────────┤
│  客户列表区域                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 客户名称    │ 联系人  │ 电话        │ 等级 │ 最后联系   │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 🏢 ABC公司  │ 张经理  │ 138****1234 │ VIP │ 2025-01-10 │ │
│ │ 🏢 XYZ企业  │ 李总    │ 139****5678 │ 重要 │ 2025-01-08 │ │
│ │ 🏢 DEF集团  │ 王主管  │ 137****9012 │ 普通 │ 2025-01-05 │ │
│ │ ...                                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  客户详情面板 (选中客户时显示)                              │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    基本信息         │ │         快速操作                │ │
│ │  公司: ABC公司      │ │  [📞 记录通话] [📧 发送邮件]    │ │
│ │  联系人: 张经理     │ │  [💰 创建报价] [📋 查看合同]    │ │
│ │  电话: 138****1234  │ │  [📝 添加备注] [📊 查看统计]    │ │
│ │  等级: VIP客户      │ │                                 │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 客户详情界面设计
```
┌─────────────────────────────────────────────────────────────┐
│                    客户详情 - ABC公司                       │
├─────────────────────────────────────────────────────────────┤
│  标签页导航                                                 │
│  [📋 基本信息] [💬 互动记录] [💰 财务信息] [📄 合同报价]    │
├─────────────────────────────────────────────────────────────┤
│  基本信息标签页内容                                         │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    公司信息         │ │         联系信息                │ │
│ │  公司名称: ABC公司  │ │  主要联系人: 张经理             │ │
│ │  客户等级: VIP      │ │  电话: 138-1234-5678            │ │
│ │  客户类型: 制造企业 │ │  传真: 021-1234-5678            │ │
│ │  所属行业: 制造业   │ │  地址: 上海市浦东新区...        │ │
│ │  合作时间: 2年3个月 │ │  备注: 重要合作伙伴             │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    业务统计                             │ │
│ │  合作时长: 2年3个月  │  总交易额: ¥1,250,000           │ │
│ │  合同数量: 8个       │  平均订单: ¥156,250             │ │
│ │  最后交易: 2024-12-15│  信用等级: AAA                  │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  操作按钮                                                   │
│  [✏️ 编辑信息] [📞 记录互动] [💰 创建报价] [📄 新建合同]    │
└─────────────────────────────────────────────────────────────┘
```

## 组件设计

### 核心UI组件

#### 1. 主窗口组件 (MainWindow)
```python
class MainWindow:
    """主窗口管理器"""
    - 窗口初始化和布局
    - 菜单栏和工具栏管理
    - 导航面板控制
    - 状态栏更新
    - 主题切换支持
```

#### 2. 导航面板组件 (NavigationPanel)
```python
class NavigationPanel:
    """左侧导航面板"""
    - 树形导航结构
    - 图标和文字显示
    - 选中状态管理
    - 折叠/展开功能
```

#### 3. 仪表盘组件 (Dashboard)
```python
class Dashboard:
    """数据仪表盘"""
    - 关键指标卡片
    - 图表组件集成
    - 实时数据更新
    - 交互式图表
```

#### 4. 数据表格组件 (DataTable)
```python
class DataTable:
    """通用数据表格"""
    - 分页显示
    - 排序功能
    - 筛选功能
    - 行选择
    - 右键菜单
```

#### 5. 表单组件 (FormPanel)
```python
class FormPanel:
    """通用表单面板"""
    - 字段验证
    - 自动布局
    - 数据绑定
    - 错误提示
```

#### 6. 图表组件 (ChartWidget)
```python
class ChartWidget:
    """图表显示组件"""
    - matplotlib集成
    - 多种图表类型
    - 交互功能
    - 导出功能
```

### UI主题和样式

#### 主题配置
```python
# 主题色彩方案
THEMES = {
    'light': {
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F8F9FA',
        'text_primary': '#212529',
        'text_secondary': '#6C757D',
        'accent': '#007BFF',
        'success': '#28A745',
        'warning': '#FFC107',
        'danger': '#DC3545'
    },
    'dark': {
        'bg_primary': '#2B2B2B',
        'bg_secondary': '#3C3C3C',
        'text_primary': '#FFFFFF',
        'text_secondary': '#CCCCCC',
        'accent': '#4A9EFF',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#F44336'
    }
}
```

#### 字体配置
```python
# 字体设置
FONTS = {
    'default': ('Microsoft YaHei UI', 9),
    'heading': ('Microsoft YaHei UI', 12, 'bold'),
    'small': ('Microsoft YaHei UI', 8),
    'monospace': ('Consolas', 9)
}
```

### 响应式布局

#### 窗口大小适配
- 最小窗口尺寸: 1024x768
- 推荐窗口尺寸: 1280x800
- 组件自适应缩放
- 内容区域滚动支持

#### 分辨率适配
- 支持高DPI显示器
- 自动缩放因子检测
- 图标和字体自适应

## 交互设计

### 用户操作流程

#### 1. 系统启动流程
```
启动应用 → 检查数据库 → 加载配置 → 显示仪表盘 → 准备就绪
```

#### 2. 客户管理流程
```
客户列表 → 搜索/筛选 → 选择客户 → 查看详情 → 编辑/操作
```

#### 3. 数据录入流程
```
点击新增 → 打开表单 → 填写信息 → 验证数据 → 保存确认
```

### 快捷键设计
```
Ctrl+N: 新建记录
Ctrl+S: 保存当前
Ctrl+F: 搜索功能
Ctrl+R: 刷新数据
F5: 刷新界面
ESC: 取消操作
Enter: 确认操作
```

### 右键菜单
```
客户列表右键菜单:
- 查看详情
- 编辑信息
- 创建报价
- 记录互动
- 删除客户
```

## 错误处理和用户反馈

### 错误提示设计
- 友好的错误消息
- 具体的解决建议
- 错误日志记录
- 用户操作指导

### 加载状态指示
- 进度条显示
- 加载动画
- 操作状态提示
- 超时处理

### 数据验证
- 实时字段验证
- 表单提交验证
- 数据格式检查
- 必填项提醒

这个UI设计重点关注了用户体验和界面的现代化，为后续的开发实现提供了清晰的指导。接下来我们可以开始具体的UI组件实现。
## 代码质量规范

### Python代码规范

#### 1. 代码风格标准
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

#### 2. 文档字符串规范
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

#### 3. 类型注解规范
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

#### 4. 异常处理规范
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

### 代码组织结构

#### 项目目录结构
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
│   │   ├── dashboard.py
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

## 执行期间Hooks设计

### 1. 应用程序生命周期Hooks

#### 应用启动Hooks
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
        """注册"""
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

### 2. 数据操作Hooks

#### 数据库操作Hooks
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

#### 界面操作Hooks
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

#### 业务流程Hooks
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

### 5. 插件系统Hooks

#### 插件管理Hooks
```python
class PluginHooks:
    """插件系统钩子管理器"""

    def __init__(self):
        self._plugin_hooks: Dict[str, List[Callable]] = {}
        self._loaded_plugins: Dict[str, Any] = {}

    def register_plugin_hook(self, hook_name: str):
        """注册插件钩子"""
        def decorator(func: Callable):
            if hook_name not in self._plugin_hooks:
                self._plugin_hooks[hook_name] = []
            self._plugin_hooks[hook_name].append(func)
            return func
        return decorator

    def execute_plugin_hooks(self, hook_name: str, *args, **kwargs):
        """执行插件钩子"""
        if hook_name in self._plugin_hooks:
            for hook_func in self._plugin_hooks[hook_name]:
                try:
                    hook_func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"插件钩子执行失败 {hook_name}: {e}")

# 使用示例
plugin_hooks = PluginHooks()

@plugin_hooks.register_plugin_hook('customer_data_export')
def export_to_excel(customer_data: List[Dict]):
    """导出客户数据到Excel"""
    # Excel导出逻辑
    pass

@plugin_hooks.register_plugin_hook('customer_data_export')
def export_to_pdf(customer_data: List[Dict]):
    """导出客户数据到PDF"""
    # PDF导出逻辑
    pass
```

### 6. 性能监控Hooks

#### 性能统计Hooks
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

### 7. 日志和审计Hooks

#### 操作审计Hooks
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

这些代码质量规范和hooks设计将确保MiniCRM项目具有良好的代码结构、可维护性和扩展性。
## 报价历史比对功能设计

### 报价比对界面设计

#### 报价创建界面增强
```
┌─────────────────────────────────────────────────────────────┐
│                    创建报价 - ABC公司                       │
├─────────────────────────────────────────────────────────────┤
│  历史报价参考区域                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📊 前3次报价对比  [展开/收起 ▼]                        │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │ │
│ │ │ 2024-12-01  │ │ 2024-10-15  │ │ 2024-08-20  │         │ │
│ │ │ 报价#001    │ │ 报价#002    │ │ 报价#003    │         │ │
│ │ │ ¥125,000    │ │ ¥118,000    │ │ ¥132,000    │         │ │
│ │ │ [查看详情]  │ │ [查看详情]  │ │ [查看详情]  │         │ │
│ │ │ [复制模板]  │ │ [复制模板]  │ │ [复制模板]  │         │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘         │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  当前报价信息                                               │
│  客户: ABC公司          报价日期: 2025-01-15               │
│  有效期: 30天           报价编号: Q2025001                 │
├─────────────────────────────────────────────────────────────┤
│  产品清单                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 产品名称    │ 规格型号 │ 数量 │ 单价    │ 小计      │历史价格│ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 产品A      │ Model-X  │ 10   │ 5,000   │ 50,000   │📊     │ │
│ │ 产品B      │ Model-Y  │ 5    │ 8,000   │ 40,000   │📊     │ │
│ │ 产品C      │ Model-Z  │ 2    │ 15,000  │ 30,000   │📊     │ │
│ │                                        总计: ¥120,000    │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  价格趋势分析                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  💡 智能建议:                                           │ │
│ │  • 产品A价格比上次报价下降5%，符合市场趋势              │ │
│ │  • 产品B价格与历史平均价格一致                          │ │
│ │  • 总报价比上次降低4.2%，竞争力提升                     │ │
│ │  • 建议重点关注产品C的价格敏感性                        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  操作按钮                                                   │
│  [💾 保存草稿] [👁️ 预览] [📊 详细比对] [📤 发送报价]        │
└─────────────────────────────────────────────────────────────┘
```

#### 详细比对弹窗界面
```
┌─────────────────────────────────────────────────────────────┐
│                    报价详细比对分析                         │
├─────────────────────────────────────────────────────────────┤
│  时间轴导航                                                 │
│  [当前报价] ←→ [2024-12-01] ←→ [2024-10-15] ←→ [2024-08-20] │
├─────────────────────────────────────────────────────────────┤
│  并排比对视图                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 当前报价(2025-01-15) │ 上次报价(2024-12-01) │ 变化趋势   │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 产品A: ¥5,000       │ 产品A: ¥5,250       │ ↓ -4.8%   │ │
│ │ 产品B: ¥8,000       │ 产品B: ¥8,000       │ → 0%      │ │
│ │ 产品C: ¥15,000      │ 产品C: ¥15,500      │ ↓ -3.2%   │ │
│ │ 总计: ¥120,000      │ 总计: ¥125,000      │ ↓ -4.0%   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  价格趋势图表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📈 价格趋势分析                                        │ │
│ │     ¥140K ┤                                             │ │
│ │     ¥130K ┤     ●                                       │ │
│ │     ¥120K ┤           ●         ●                       │ │
│ │     ¥110K ┤                 ●       ●                   │ │
│ │     ¥100K └─────────────────────────────────────────    │ │
│ │           2024-08  2024-10  2024-12  2025-01           │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  竞争力分析                                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  🎯 竞争力评估:                                         │ │
│ │  • 价格竞争力: ⭐⭐⭐⭐☆ (4/5)                          │ │
│ │  • 价格稳定性: ⭐⭐⭐☆☆ (3/5)                          │ │
│ │  • 成交概率: 78% (基于历史数据)             │ │
│ │  • 建议策略: 适度降价，重点突出产品价值                 │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [📋 复制到当前] [📊 导出分析] [💾 保存比对] [❌ 关闭]      │
└─────────────────────────────────────────────────────────────┘
```

### 数据模型设计

#### 报价表结构增强
```sql
-- 报价主表
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL,
    quote_date DATE NOT NULL,
    valid_until DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft', -- draft, sent, accepted, rejected, expired
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- 报价明细表
CREATE TABLE quote_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_model VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    notes TEXT,
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
);

-- 报价比对历史表
CREATE TABLE quote_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    current_quote_id INTEGER NOT NULL,
    comparison_data TEXT, -- JSON格式存储比对数据
    analysis_result TEXT, -- JSON格式存储分析结果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (current_quote_id) REFERENCES quotes(id)
);
```

#### 报价比对数据结构
```python
@dataclass
class QuoteComparison:
    """报价比对数据类"""
    customer_id: int
    current_quote: Quote
    historical_quotes: List[Quote]  # 最近3次报价
    comparison_items: List[QuoteItemComparison]
    price_trends: Dict[str, List[float]]
    analysis_summary: QuoteAnalysisSummary

@dataclass
class QuoteItemComparison:
    """报价项目比对"""
    product_name: str
    current_price: float
    historical_prices: List[float]
    price_change_percent: float
    price_trend: str  # 'up', 'down', 'stable'
    competitiveness_score: float

@dataclass
class QuoteAnalysisSummary:
    """报价分析摘要"""
    total_change_percent: float
    competitiveness_score: float
    success_probability: float
    recommended_strategy: str
    key_insights: List[str]
```

### 业务逻辑设计

#### 报价比对服务
```python
class QuoteComparisonService:
    """报价比对服务"""

    def __init__(self, quote_dao: QuoteDAO):
        self._quote_dao = quote_dao
        self._logger = logging.getLogger(__name__)

    def get_quote_comparison(
        self,
        customer_id: int,
        current_quote_data: Dict[str, Any]
    ) -> QuoteComparison:
        """获取报价比对数据"""
        try:
            # 获取历史报价（最近3次）
            historical_quotes = self._quote_dao.get_recent_quotes(
                customer_id, limit=3
            )

            # 创建当前报价对象
            current_quote = self._create_quote_from_data(current_quote_data)

            # 生成比对项目
            comparison_items = self._generate_item_comparisons(
                current_quote, historical_quotes
            )

            # 计算价格趋势
            price_trends = self._calculate_price_trends(
                current_quote, historical_quotes
            )

            # 生成分析摘要
            analysis_summary = self._generate_analysis_summary(
                current_quote, historical_quotes, comparison_items
            )

            return QuoteComparison(
                customer_id=customer_id,
                current_quote=current_quote,
                historical_quotes=historical_quotes,
                comparison_items=comparison_items,
                price_trends=price_trends,
                analysis_summary=analysis_summary
            )

        except Exception as e:
            self._logger.error(f"报价比对失败: {e}")
            raise BusinessLogicError(f"无法生成报价比对: {e}")

    def _generate_item_comparisons(
        self,
        current_quote: Quote,
        historical_quotes: List[Quote]
    ) -> List[QuoteItemComparison]:
        """生成项目比对数据"""
        comparisons = []

        for current_item in current_quote.items:
            # 查找历史价格
            historical_prices = []
            for hist_quote in historical_quotes:
                hist_item = self._find_matching_item(
                    current_item, hist_quote.items
                )
                if hist_item:
                    historical_prices.append(hist_item.unit_price)

            # 计算价格变化
            if historical_prices:
                latest_price = historical_prices[0]
                price_change = (
                    (current_item.unit_price - latest_price) / latest_price * 100
                )

                # 判断价格趋势
                if abs(price_change) < 2:
                    trend = 'stable'
                elif price_change > 0:
                    trend = 'up'
                else:
                    trend = 'down'

                # 计算竞争力评分
                competitiveness = self._calculate_competitiveness(
                    current_item.unit_price, historical_prices
                )

                comparisons.append(QuoteItemComparison(
                    product_name=current_item.product_name,
                    current_price=current_item.unit_price,
                    historical_prices=historical_prices,
                    price_change_percent=price_change,
                    price_trend=trend,
                    competitiveness_score=competitiveness
                ))

        return comparisons

    def _generate_analysis_summary(
        self,
        current_quote: Quote,
        historical_quotes: List[Quote],
        comparison_items: List[QuoteItemComparison]
    ) -> QuoteAnalysisSummary:
        """生成分析摘要"""
        if not historical_quotes:
            return QuoteAnalysisSummary(
                total_change_percent=0,
                competitiveness_score=3.0,
                success_probability=50.0,
                recommended_strategy="首次报价，建议关注市场反馈",
                key_insights=["这是该客户的首次报价"]
            )

        # 计算总价变化
        latest_total = historical_quotes[0].total_amount
        total_change = (
            (current_quote.total_amount - latest_total) / latest_total * 100
        )

        # 计算平均竞争力
        avg_competitiveness = sum(
            item.competitiveness_score for item in comparison_items
        ) / len(comparison_items) if comparison_items else 3.0

        # 预测成交概率（基于历史数据和价格趋势）
        success_prob = self._predict_success_probability(
            total_change, avg_competitiveness, historical_quotes
        )

        # 生成策略建议
        strategy = self._generate_strategy_recommendation(
            total_change, avg_competitiveness, success_prob
        )

        # 生成关键洞察
        insights = self._generate_key_insights(
            comparison_items, total_change, historical_quotes
        )

        return QuoteAnalysisSummary(
            total_change_percent=total_change,
            competitiveness_score=avg_competitiveness,
            success_probability=success_prob,
            recommended_strategy=strategy,
            key_insights=insights
        )

    def _generate_key_insights(
        self,
        comparison_items: List[QuoteItemComparison],
        total_change: float,
        historical_quotes: List[Quote]
    ) -> List[str]:
        """生成关键洞察"""
        insights = []

        # 价格趋势洞察
        if total_change < -5:
            insights.append(f"总报价下降{abs(total_change):.1f}%，竞争力显著提升")
        elif total_change > 5:
            insights.append(f"总报价上涨{total_change:.1f}%，需关注客户接受度")
        else:
            insights.append("报价价格相对稳定，符合市场预期")

        # 产品价格洞察
        price_down_items = [
            item for item in comparison_items
            if item.price_trend == 'down'
        ]
        if price_down_items:
            insights.append(
                f"{len(price_down_items)}个产品价格下降，有利于成交"
            )

        # 历史成交洞察
        if len(historical_quotes) >= 3:
            insights.append("客户合作历史丰富，建议重点维护关系")

        # 竞争力洞察
        high_comp_items = [
            item for item in comparison_items
            if item.competitiveness_score >= 4.0
        ]
        if high_comp_items:
            insights.append(
                f"{len(high_comp_items)}个产品具有较强价格竞争力"
            )

        return insights
```

### UI组件设计

#### 报价比对组件
```python
class QuoteComparisonWidget(ttk.Frame):
    """报价比对组件"""

    def __init__(self, parent, quote_service: QuoteComparisonService):
        super().__init__(parent)
        self._quote_service = quote_service
        self._comparison_data: Optional[QuoteComparison] = None
        self._setup_ui()

    def _setup_ui(self):
        """设置UI界面"""
        # 历史报价参考区域
        self._create_historical_quotes_panel()

        # 价格趋势图表区域
        self._create_price_trend_chart()

        # 智能建议区域
        self._create_insights_panel()

        # 操作按钮
        self._create_action_buttons()

    def load_comparison_data(self, customer_id: int, current_quote_data: Dict):
        """加载比对数据"""
        try:
            self._comparison_data = self._quote_service.get_quote_comparison(
                customer_id, current_quote_data
            )
            self._update_ui()
        except Exception as e:
            messagebox.showerror("错误", f"加载比对数据失败: {e}")

    def _create_historical_quotes_panel(self):
        """创建历史报价面板"""
        frame = ttk.LabelFrame(self, text="前3次报价对比")
        frame.pack(fill='x', padx=5, pady=5)

        # 历史报价卡片容器
        self._hist_quotes_frame = ttk.Frame(frame)
        self._hist_quotes_frame.pack(fill='x', padx=5, pady=5)

    def _create_price_trend_chart(self):
        """创建价格趋势图表"""
        frame = ttk.LabelFrame(self, text="价格趋势分析")
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        # matplotlib图表
        self._chart_frame = ttk.Frame(frame)
        self._chart_frame.pack(fill='both', expand=True, padx=5, pady=5)

    def _create_insights_panel(self):
        """创建智能建议面板"""
        frame = ttk.LabelFrame(self, text="智能建议")
        frame.pack(fill='x', padx=5, pady=5)

        self._insights_text = tk.Text(
            frame, height=4, wrap='word', state='disabled'
        )
        self._insights_text.pack(fill='x', padx=5, pady=5)

    def show_detailed_comparison(self):
        """显示详细比对弹窗"""
        if not self._comparison_data:
            return

        dialog = QuoteComparisonDialog(
            self, self._comparison_data
        )
        dialog.show()
```

这个报价历史比对功能设计提供了：

1. **可视化比对** - 直观显示前3次报价的对比
2. **智能分析** - 自动分析价格趋势和竞争力
3. **策略建议** - 基于历史数据提供报价策略
4. **一键复制** - 快速基于历史报价创建新报价
5. **详细分析** - 深入的价格趋势和成交概率分析

这将大大提升报价管理的效率和准确性！
## 客户类型管理设计

### 客户类型自定义功能

#### 客户类型管理界面
```
┌─────────────────────────────────────────────────────────────┐
│                    客户类型管理                             │
├─────────────────────────────────────────────────────────────┤
│  操作按钮区域                                               │
│  [➕ 新增类型] [✏️ 编辑] [🗑️ 删除] [🔄 刷新]                │
├─────────────────────────────────────────────────────────────┤
│  客户类型列表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 类型名称    │ 描述说明        │ 客户数量 │ 创建时间      │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 生态板客户  │ 主要采购生态板  │ 28      │ 2024-01-15   │ │
│ │ 家具板客户  │ 主要采购家具板  │ 22      │ 2024-01-20   │ │
│ │ 阻燃板客户  │ 主要采购阻燃板  │ 15      │ 2024-02-01   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  类型详情面板 (选中类型时显示)                              │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  类型信息                                               │ │
│ │  名称: 生态板客户                                       │ │
│ │  描述: 主要采购生态板产品的客户群体                     │ │
│ │  颜色标识: � 绿色                                       │ │
│ │  关联客户: 28个                                         │ │
│ │  平均订单: ¥125,000                                     │ │
│ │  创建时间: 2024-01-15                                   │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 新增/编辑客户类型弹窗
```
┌─────────────────────────────────────────────────────────────┐
│                    新增客户类型                             │
├─────────────────────────────────────────────────────────────┤
│  基本信息                                                   │
│  类型名称: [生态板客户                  ] *必填             │
│  描述说明: [主要采购生态板产品的客户群体                    │
│           ________________________________] *必填           │
│                                                             │
│  显示设置                                                   │
│  颜色标识: [�]] [�] [�] [� [] [�] [🟪] [⚪[⚫] [⚪]          │
│  图标选择: [�] [[🪑] [🔥] [�]  [🏢] [�] [💼 ] [🎯]          │
│                                                             │
│  业务设置                                                   │
│  默认授信额度: [¥100,000        ] (可选)                   │
│  默认账期天数: [30              ] 天 (可选)                │
│  优先级设置:   [普通 ▼] (高/中/普通/低)                     │
│                                                             │
│  备注信息                                                   │
│  [生态板客户对环保要求较高，需要重点关注产品环保认证       │
│   ________________________________________________]         │
├─────────────────────────────────────────────────────────────┤
│  预览效果                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 🏭 制造企业 (25个客户)                                  │ │
│ │ 专业从事产品生产制造的企业客户                          │ │
│ │ 默认授信: ¥100,000 | 账期: 30天 | 优先级: 普通          │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [💾 保存] [👁️ 预览] [❌ 取消]                              │
└─────────────────────────────────────────────────────────────┘
```

### 客户信息字段调整

#### 更新后的客户信息数据模型
```python
@dataclass
class Customer:
    """客户数据类 - 更新版"""
    id: Optional[int] = None
    name: str = ""                    # 客户名称
    contact_person: str = ""          # 联系人
    phone: str = ""                   # 电话
    fax: str = ""                     # 传真
    address: str = ""                 # 地址
    customer_type_id: Optional[int] = None  # 客户类型ID (关联到客户类型表)
    industry: str = ""                # 所属行业
    level: CustomerLevel = CustomerLevel.NORMAL  # 客户等级
    cooperation_start_date: Optional[date] = None  # 合作开始时间
    notes: str = ""                   # 备注
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CustomerType:
    """客户类型数据类"""
    id: Optional[int] = None
    name: str = ""                    # 类型名称
    description: str = ""             # 描述说明
    color_code: str = "#007BFF"       # 颜色标识
    icon: str = "🏢"                  # 图标
    default_credit_limit: Optional[float] = None  # 默认授信额度
    default_payment_days: Optional[int] = None    # 默认账期天数
    priority: str = "normal"          # 优先级 (high/medium/normal/low)
    notes: str = ""                   # 备注
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

#### 数据库表结构调整
```sql
-- 客户类型表
CREATE TABLE customer_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color_code VARCHAR(7) DEFAULT '#007BFF',
    icon VARCHAR(10) DEFAULT '🏢',
    default_credit_limit DECIMAL(15,2),
    default_payment_days INTEGER,
    priority VARCHAR(20) DEFAULT 'normal',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 客户表 (更新版)
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(50),
    fax VARCHAR(50),
    address TEXT,
    customer_type_id INTEGER,
    industry VARCHAR(100),
    level VARCHAR(20) DEFAULT 'normal',
    cooperation_start_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_type_id) REFERENCES customer_types(id)
);

-- 插入默认客户类型 (板材业务)
INSERT INTO customer_types (name, description, icon, priority) VALUES
('生态板客户', '主要采购生态板产品的客户', '�', 'higih'),
('家具板客户', '主要采购家具板产品的客户', '🪑', 'high'),
('阻燃板客户', '主要采购阻燃板产品的客户', '🔥', 'medium');
```

### 客户类型管理服务
```python
class CustomerTypeService:
    """客户类型管理服务"""

    def __init__(self, customer_type_dao: CustomerTypeDAO):
        self._dao = customer_type_dao
        self._logger = logging.getLogger(__name__)

    def create_customer_type(self, type_data: Dict[str, Any]) -> int:
        """创建客户类型"""
        try:
            # 验证类型名称唯一性
            if self._dao.exists_by_name(type_data['name']):
                raise ValidationError(f"客户类型 '{type_data['name']}' 已存在")

            # 验证必填字段
            if not type_data.get('name'):
                raise ValidationError("客户类型名称不能为空")

            if not type_data.get('description'):
                raise ValidationError("客户类型描述不能为空")

            # 创建客户类型
            type_id = self._dao.insert(type_data)

            self._logger.info(f"成功创建客户类型: {type_data['name']}")
            return type_id

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"创建客户类型失败: {e}")
            raise BusinessLogicError(f"创建客户类型失败: {e}")

    def update_customer_type(self, type_id: int, type_data: Dict[str, Any]) -> bool:
        """更新客户类型"""
        try:
            # 检查类型是否存在
            if not self._dao.exists_by_id(type_id):
                raise BusinessLogicError(f"客户类型不存在: {type_id}")

            # 检查是否有客户使用该类型
            customer_count = self._dao.get_customer_count(type_id)

            # 如果有客户使用，某些字段不能修改
            if customer_count > 0:
                restricted_fields = ['default_credit_limit', 'default_payment_days']
                for field in restricted_fields:
                    if field in type_data:
                        self._logger.warning(
                            f"客户类型 {type_id} 有 {customer_count} 个客户使用，"
                            f"不能修改字段: {field}"
                        )

            # 更新客户类型
            result = self._dao.update(type_id, type_data)

            if result:
                self._logger.info(f"成功更新客户类型: {type_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"更新客户类型失败: {e}")
            raise BusinessLogicError(f"更新客户类型失败: {e}")

    def delete_customer_type(self, type_id: int) -> bool:
        """删除客户类型"""
        try:
            # 检查是否有客户使用该类型
            customer_count = self._dao.get_customer_count(type_id)
            if customer_count > 0:
                raise BusinessLogicError(
                    f"无法删除客户类型，还有 {customer_count} 个客户使用该类型"
                )

            # 删除客户类型
            result = self._dao.delete(type_id)

            if result:
                self._logger.info(f"成功删除客户类型: {type_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除客户类型失败: {e}")
            raise BusinessLogicError(f"删除客户类型失败: {e}")

    def get_customer_types_with_stats(self) -> List[Dict[str, Any]]:
        """获取客户类型及统计信息"""
        try:
            types = self._dao.get_all()

            # 为每个类型添加统计信息
            for type_info in types:
                type_id = type_info['id']

                # 客户数量
                type_info['customer_count'] = self._dao.get_customer_count(type_id)

                # 平均订单金额
                type_info['avg_order_amount'] = self._dao.get_avg_order_amount(type_id)

                # 最后更新时间
                type_info['last_customer_date'] = self._dao.get_last_customer_date(type_id)

            return types

        except Exception as e:
            self._logger.error(f"获取客户类型统计失败: {e}")
            raise BusinessLogicError(f"获取客户类型统计失败: {e}")
```

### UI组件更新

#### 客户信息表单组件更新
```python
class CustomerFormPanel(ttk.Frame):
    """客户信息表单面板 - 更新版"""

    def _create_form_fields(self):
        """创建表单字段"""
        # 基本信息区域
        basic_frame = ttk.LabelFrame(self, text="基本信息")
        basic_frame.pack(fill='x', padx=5, pady=5)

        # 客户名称
        ttk.Label(basic_frame, text="客户名称:").grid(row=0, column=0, sticky='w')
        self.name_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.name_var, width=30).grid(row=0, column=1)

        # 联系人
        ttk.Label(basic_frame, text="联系人:").grid(row=0, column=2, sticky='w')
        self.contact_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.contact_var, width=20).grid(row=0, column=3)

        # 电话
        ttk.Label(basic_frame, text="电话:").grid(row=1, column=0, sticky='w')
        self.phone_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.phone_var, width=30).grid(row=1, column=1)

        # 传真
        ttk.Label(basic_frame, text="传真:").grid(row=1, column=2, sticky='w')
        self.fax_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.fax_var, width=20).grid(row=1, column=3)

        # 客户类型 (下拉选择)
        ttk.Label(basic_frame, text="客户类型:").grid(row=2, column=0, sticky='w')
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(
            basic_frame, textvariable=self.type_var, width=27, state='readonly'
        )
        self.type_combo.grid(row=2, column=1)

        # 客户等级
        ttk.Label(basic_frame, text="客户等级:").grid(row=2, column=2, sticky='w')
        self.level_var = tk.StringVar()
        level_combo = ttk.Combobox(
            basic_frame, textvariable=self.level_var, width=17, state='readonly'
        )
        level_combo['values'] = ('VIP客户', '重要客户', '普通客户', '潜在客户')
        level_combo.grid(row=2, column=3)

        # 合作时间
        ttk.Label(basic_frame, text="合作开始:").grid(row=3, column=0, sticky='w')
        self.cooperation_date_var = tk.StringVar()
        cooperation_entry = ttk.Entry(
            basic_frame, textvariable=self.cooperation_date_var, width=30
        )
        cooperation_entry.grid(row=3, column=1)

        # 所属行业
        ttk.Label(basic_frame, text="所属行业:").grid(row=3, column=2, sticky='w')
        self.industry_var = tk.StringVar()
        ttk.Entry(basic_frame, textvariable=self.industry_var, width=20).grid(row=3, column=3)

        # 地址信息
        address_frame = ttk.LabelFrame(self, text="地址信息")
        address_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(address_frame, text="详细地址:").pack(anchor='w')
        self.address_var = tk.StringVar()
        ttk.Entry(address_frame, textvariable=self.address_var, width=80).pack(fill='x', pady=2)

        # 备注信息
        notes_frame = ttk.LabelFrame(self, text="备注信息")
        notes_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.notes_text = tk.Text(notes_frame, height=4, wrap='word')
        self.notes_text.pack(fill='both', expand=True, padx=5, pady=5)

    def load_customer_types(self):
        """加载客户类型选项"""
        try:
            types = self._customer_type_service.get_all_customer_types()
            type_names = [f"{t['icon']} {t['name']}" for t in types]
            self.type_combo['values'] = type_names
        except Exception as e:
            messagebox.showerror("错误", f"加载客户类型失败: {e}")
```

这些更新包括：

1. **客户类型自定义** - 用户可以创建、编辑、删除客户类型
2. **字段调整** - 移除邮箱和网站，成立时间改为合作时间，增加传真字段
3. **可视化标识** - 客户类型支持颜色和图标标识
4. **业务设置** - 客户类型可设置默认授信额度和账期
5. **统计信息** - 显示每种类型的客户数量和业务数据

这样的设计更加灵活和实用！
## 统一业务流程页面设计

### 业务流程统一界面

#### 主业务流程页面布局
```
┌─────────────────────────────────────────────────────────────┐
│                    业务流程管理                             │
├─────────────────────────────────────────────────────────────┤
│  流程类型选择标签页                                         │
│  [📋 报价管理] [📄 合同管理] [🔧 售后跟踪] [💰 收款管理]    │
├─────────────────────────────────────────────────────────────┤
│  搜索和筛选区域                                             │
│  🔍 [搜索框: 输入编号、客户名称等]  [高级筛选 ▼]           │
│  筛选: [状态 ▼] [客户类型 ▼] [时间范围 ▼] [负责人 ▼]       │
├─────────────────────────────────────────────────────────────┤
│  操作按钮区域                                               │
│  [➕ 新建] [📤 导入] [📥 导出] [📊 统计] [🔄 刷新]          │
├─────────────────────────────────────────────────────────────┤
│  业务流程列表区域 (根据选中标签页显示不同内容)             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 编号      │ 客户名称  │ 状态    │ 金额     │ 日期      │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ Q2025001  │ ABC公司   │ 已发送  │ ¥120,000 │ 01-15    │ │
│ │ Q2025002  │ XYZ企业   │ 草稿    │ ¥85,000  │ 01-14    │ │
│ │ Q2025003  │ DEF集团   │ 已接受  │ ¥200,000 │ 01-13    │ │
│ │ ...                                                     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  详情面板 (选中项目时显示)                                  │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    基本信息         │ │         快速操作                │ │
│ │  编号: Q2025001     │ │  [👁️ 查看详情] [✏️ 编辑]        │ │
│ │  客户: ABC公司      │ │  [📧 发送邮件] [📞 联系客户]    │ │
│ │  状态: 已发送       │ │  [📋 复制] [🗑️ 删除]            │ │
│ │  金额: ¥120,000     │ │  [📊 查看统计] [📝 添加备注]    │ │
│ │  日期: 2025-01-15   │ │                                 │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 各业务流程标签页内容

#### 1. 报价管理标签页
```
┌─────────────────────────────────────────────────────────────┐
│  报价列表                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 报价编号  │ 客户名称  │ 状态    │ 金额     │ 有效期    │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ Q2025001  │ ABC公司   │ 已发送  │ ¥120,000 │ 02-14    │ │
│ │ Q2025002  │ XYZ企业   │ 草稿    │ ¥85,000  │ 02-13    │ │
│ │ Q2025003  │ DEF集团   │ 已接受  │ ¥200,000 │ 已过期   │ │
│ │ Q2025004  │ GHI公司   │ 已拒绝  │ ¥150,000 │ 已过期   │ │
│ └─────────────────────────────────────────────────────────┘ │
│  状态统计: 草稿(5) | 已发送(12) | 已接受(8) | 已拒绝(3)   │
└─────────────────────────────────────────────────────────────┘
```

#### 2. 合同管理标签页
```
┌─────────────────────────────────────────────────────────────┐
│  合同列表                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 合同编号  │ 客户名称  │ 状态    │ 金额     │ 到期日    │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ C2025001  │ ABC公司   │ 执行中  │ ¥200,000 │ 12-31    │ │
│ │ C2025002  │ XYZ企业   │ 已签署  │ ¥150,000 │ 06-30    │ │
│ │ C2025003  │ DEF集团   │ 草稿    │ ¥300,000 │ 未设置   │ │
│ │ C2025004  │ GHI公司   │ 已完成  │ ¥180,000 │ 已到期   │ │
│ └─────────────────────────────────────────────────────────┘ │
│  状态统计: 草稿(3) | 已签署(15) | 执行中(22) | 已完成(18) │
└─────────────────────────────────────────────────────────────┘
```

#### 3. 售后跟踪标签页
```
┌─────────────────────────────────────────────────────────────┐
│  售后记录列表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 工单编号  │ 客户名称  │ 问题类型│ 状态    │ 创建日期  │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ S2025001  │ ABC公司   │ 质量问题│ 处理中  │ 01-15    │ │
│ │ S2025002  │ XYZ企业   │ 使用咨询│ 已完成  │ 01-14    │ │
│ │ S2025003  │ DEF集团   │ 安装问题│ 待处理  │ 01-13    │ │
│ │ S2025004  │ GHI公司   │ 配件更换│ 已关闭  │ 01-12    │ │
│ └─────────────────────────────────────────────────────────┘ │
│  状态统计: 待处理(8) | 处理中(15) | 已完成(45) | 已关闭(32)│
└─────────────────────────────────────────────────────────────┘
```

#### 4. 收款管理标签页
```
┌─────────────────────────────────────────────────────────────┐
│  收款记录列表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 收款编号  │ 客户名称  │ 应收金额│ 已收金额│ 状态      │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ R2025001  │ ABC公司   │ ¥200,000│ ¥200,000│ 已完成    │ │
│ │ R2025002  │ XYZ企业   │ ¥150,000│ ¥100,000│ 部分收款  │ │
│ │ R2025003  │ DEF集团   │ ¥300,000│ ¥0      │ 未收款    │ │
│ │ R2025004  │ GHI公司   │ ¥180,000│ ¥0      │ 逾期      │ │
│ └─────────────────────────────────────────────────────────┘ │
│  状态统计: 未收款(12) | 部分收款(8) | 已完成(35) | 逾期(5) │
└─────────────────────────────────────────────────────────────┘
```

### 统一详情弹窗设计

#### 通用详情弹窗模板
```
┌─────────────────────────────────────────────────────────────┐
│                 [业务类型] 详情 - [编号]                 │
├─────────────────────────────────────────────────────────────┤
│  详情标签页导航                                             │
│  [📋 基本信息] [📝 详细内容] [📞 沟通记录] [📊 相关数据]    │
├─────────────────────────────────────────────────────────────┤
│  基本信息标签页内容                                         │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    基础信息         │ │         状态信息                │ │
│ │  编号: Q2025001     │ │  当前状态: 已发送               │ │
│ │  客户: ABC公司      │ │  创建时间: 2025-01-15 10:30     │ │
│ │  类型: 生态板客户   │ │  更新时间: 2025-01-15 14:20     │ │
│ │  金额: ¥120,000     │ │  负责人: 张经理                 │ │
│ │  有效期: 2025-02-14 │ │  优先级: 高                     │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    进度跟踪                             │ │
│ │  ●────●────○────○  创建 → 发送 → 接受 → 签约           │ │
│ │  01-15  01-15   待定   待定                             │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  操作按钮                                                   │
│  [✏️ 编辑] [📧 发送] [📋 复制] [📊 统计] [🗑️ 删除]         │
└─────────────────────────────────────────────────────────────┘
```

### 统一组件设计

#### 业务流程管理组件
```python
class BusinessProcessManager(ttk.Frame):
    """统一业务流程管理组件"""

    def __init__(self, parent):
        super().__init__(parent)
        self._current_process_type = "quote"  # quote, contract, service, payment
        self._setup_ui()

    def _setup_ui(self):
        """设置统一界面"""
        # 标签页导航
        self._create_tab_navigation()

        # 搜索筛选区域
        self._create_search_filter_area()

        # 操作按钮区域
        self._create_action_buttons()

        # 数据列表区域
        self._create_data_list_area()

        # 详情面板
        self._create_details_panel()

    def _create_tab_navigation(self):
        """创建标签页导航"""
        tab_frame = ttk.Frame(self)
        tab_frame.pack(fill='x', padx=5, pady=5)

        # 业务流程标签按钮
        self.tab_buttons = {}
        tabs = [
            ("quote", "📋 报价管理"),
            ("contract", "📄 合同管理"),
            ("service", "🔧 售后跟踪"),
            ("payment", "💰 收款管理")
        ]

        for i, (tab_id, tab_text) in enumerate(tabs):
            btn = ttk.Button(
                tab_frame,
                text=tab_text,
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.grid(row=0, column=i, padx=2, sticky='ew')
            self.tab_buttons[tab_id] = btn

        # 设置列权重
        for i in range(len(tabs)):
            tab_frame.columnconfigure(i, weight=1)

    def _create_search_filter_area(self):
        """创建搜索筛选区域"""
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)

        # 搜索框
        ttk.Label(search_frame, text="🔍").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=30
        )
        search_entry.pack(side='left', padx=5)

        # 高级筛选按钮
        ttk.Button(
            search_frame, text="高级筛选 ▼",
            command=self._show_advanced_filter
        ).pack(side='left', padx=5)

        # 快速筛选
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(side='left', padx=20)

        # 状态筛选
        ttk.Label(filter_frame, text="状态:").pack(side='left')
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(
            filter_frame, textvariable=self.status_var, width=10, state='readonly'
        )
        status_combo.pack(side='left', padx=2)

        # 客户类型筛选
        ttk.Label(filter_frame, text="类型:").pack(side='left', padx=(10,0))
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            filter_frame, textvariable=self.type_var, width=12, state='readonly'
        )
        type_combo.pack(side='left', padx=2)

    def _create_action_buttons(self):
        """创建操作按钮区域"""
        action_frame = ttk.Frame(self)
        action_frame.pack(fill='x', padx=5, pady=5)

        buttons = [
            ("➕ 新建", self._create_new),
            ("📤 导入", self._import_data),
            ("📥 导出", self._export_data),
            ("📊 统计", self._show_statistics),
            ("🔄 刷新", self._refresh_data)
        ]

        for text, command in buttons:
            ttk.Button(action_frame, text=text, command=command).pack(
                side='left', padx=2
            )

    def _create_data_list_area(self):
        """创建数据列表区域"""
        list_frame = ttk.Frame(self)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # 创建Treeview
        self.tree = ttk.Treeview(list_frame, show='headings', height=15)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # 布局
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self._on_item_select)
        self.tree.bind('<Double-1>', self._on_item_double_click)

    def _create_details_panel(self):
        """创建详情面板"""
        details_frame = ttk.LabelFrame(self, text="详情信息")
        details_frame.pack(fill='x', padx=5, pady=5)

        # 基本信息区域
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)

        self.info_labels = {}
        info_fields = ["编号", "客户", "状态", "金额", "日期"]

        for i, field in enumerate(info_fields):
            ttk.Label(info_frame, text=f"{field}:").grid(
                row=i, column=0, sticky='w', pady=2
            )
            label = ttk.Label(info_frame, text="")
            label.grid(row=i, column=1, sticky='w', padx=10, pady=2)
            self.info_labels[field] = label

        # 快速操作区域
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(side='right', padx=5, pady=5)

        quick_actions = [
            ("👁️ 查看详情", self._view_details),
            ("✏️ 编辑", self._edit_item),
            ("📧 发送邮件", self._send_email),
            ("📞 联系客户", self._contact_customer),
            ("📋 复制", self._copy_item),
            ("🗑️ 删除", self._delete_item)
        ]

        for i, (text, command) in enumerate(quick_actions):
            ttk.Button(action_frame, text=text, command=command).grid(
                row=i, column=0, sticky='ew', pady=1
            )

    def _switch_tab(self, tab_id: str):
        """切换标签页"""
        self._current_process_type = tab_id

        # 更新按钮状态
        for btn_id, btn in self.tab_buttons.items():
            if btn_id == tab_id:
                btn.configure(state='disabled')
            else:
                btn.configure(state='normal')

        # 更新列表配置
        self._update_list_columns()

        # 更新筛选选项
        self._update_filter_options()

        # 刷新数据
        self._refresh_data()

    def _update_list_columns(self):
        """根据当前标签页更新列表列配置"""
        column_configs = {
            "quote": [
                ("编号", 100),
                ("客户名称", 150),
                ("状态", 80),
                ("金额", 100),
                ("有效期", 100)
            ],
            "contract": [
                ("编号", 100),
                ("客户名称", 150),
                ("状态", 80),
                ("金额", 100),
                ("到期日", 100)
            ],
            "service": [
                ("工单编号", 100),
                ("客户名称", 150),
                ("问题类型", 100),
                ("状态", 80),
                ("创建日期", 100)
            ],
            "payment": [
                ("收款编号", 100),
                ("客户名称", 150),
                ("应收金额", 100),
                ("已收金额", 100),
                ("状态", 80)
            ]
        }

        columns = column_configs.get(self._current_process_type, [])

        # 清除现有列
        self.tree['columns'] = []

        # 设置新列
        column_ids = [col[0] for col in columns]
        self.tree['columns'] = column_ids

        for col_name, width in columns:
            self.tree.heading(col_name, text=col_name)
            self.tree.column(col_name, width=width, minwidth=50)

    def _update_filter_options(self):
        """更新筛选选项"""
        status_options = {
            "quote": ["全部", "草稿", "已发送", "已接受", "已拒绝", "已过期"],
            "contract": ["全部", "草稿", "已签署", "执行中", "已完成", "已终止"],
            "service": ["全部", "待处理", "处理中", "已完成", "已关闭"],
            "payment": ["全部", "未收款", "部分收款", "已完成", "逾期"]
        }

        # 更新状态筛选选项
        options = status_options.get(self._current_process_type, ["全部"])
        status_combo = None
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Combobox) and subchild.cget('textvariable') == str(self.status_var):
                        status_combo = subchild
                        break

        if status_combo:
            status_combo['values'] = options
            status_combo.set("全部")
```

### 统一数据服务接口

#### 业务流程服务接口
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BusinessProcessService(ABC):
    """业务流程服务基类"""

    @abstractmethod
    def get_list(
        self,
        filters: Dict[str, Any] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取业务流程列表"""
        pass

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取详情"""
        pass

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> int:
        """创建新项目"""
        pass

    @abstractmethod
    def update(self, item_id: int, data: Dict[str, Any]) -> bool:
        """更新项目"""
        pass

    @abstractmethod
    def delete(self, item_id: int) -> bool:
        """删除项目"""
        pass

    @abstractmethod
    def get_status_statistics(self) -> Dict[str, int]:
        """获取状态统计"""
        pass

# 具体实现类
class QuoteService(BusinessProcessService):
    """报价服务实现"""
    pass

class ContractService(BusinessProcessService):
    """合同服务实现"""
    pass

class ServiceTicketService(BusinessProcessService):
    """售后服务实现"""
    pass

class PaymentService(BusinessProcessService):
    """收款服务实现"""
    pass
```

这个统一的业务流程页面设计提供了：

1. **统一的用户界面** - 所有业务流程使用相同的布局和交互模式
2. **标签页切换** - 在一个页面内管理多种业务流程
3. **一致的操作体验** - 搜索、筛选、操作按钮保持一致
4. **灵活的列表配置** - 根据业务类型动态调整列表显示
5. **统一的详情展示** - 标准化的详情弹窗和信息面板
6. **可扩展的架构** - 基于接口的服务设计，便于扩展新的业务流程

这样用户只需要熟悉一套操作模式，就能高效地管理所有业务流程！
## 供应商报价管理设计

### 供应商报价统一页面

#### 供应商业务流程页面扩展
```
┌─────────────────────────────────────────────────────────────┐
│                    供应商业务流程管理                       │
├─────────────────────────────────────────────────────────────┤
│  流程类型选择标签页                                         │
│  [📋 供应商报价] [📄 采购合同] [🔧 质量跟踪] [💰 付款管理]  │
├─────────────────────────────────────────────────────────────┤
│  搜索和筛选区域                                             │
│  🔍 [搜索框: 输入编号、供应商名称等]  [高级筛选 ▼]         │
│  筛选: [状态 ▼] [供应商类型 ▼] [产品类别 ▼] [时间范围 ▼]   │
├─────────────────────────────────────────────────────────────┤
│  操作按钮区域                                               │
│  [➕ 新建询价] [📤 导入] [📥 导出] [📊 比价分析] [🔄 刷新]  │
├─────────────────────────────────────────────────────────────┤
│  供应商报价列表区域                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 报价编号  │ 供应商    │ 产品类别│ 状态    │ 金额      │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ SQ2025001 │ 木材供应商│ 生态板  │ 已收到  │ ¥85,000   │ │
│ │ SQ2025002 │ 板材厂家  │ 家具板  │ 待回复  │ ¥120,000  │ │
│ │ SQ2025003 │ 环保材料  │ 阻燃板  │ 已接受  │ ¥95,000   │ │
│ │ SQ2025004 │ 优质木业  │ 生态板  │ 已拒绝  │ ¥92,000   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  详情面板 (选中报价时显示)                                  │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    报价信息         │ │         快速操作                │ │
│ │  编号: SQ2025001    │ │  [👁️ 查看详情] [📊 价格比对]    │ │
│ │  供应商: 木材供应商 │ │  [✅ 接受报价] [❌ 拒绝报价]    │ │
│ │  产品: 生态板       │ │  [📞 联系供应商] [📋 复制询价]  │ │
│ │  金额: ¥85,000      │ │  [📝 添加备注] [🗑️ 删除]        │ │
│ │  日期: 2025-01-15   │ │                                 │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 供应商报价比对功能

#### 供应商报价创建/查看界面
```
┌─────────────────────────────────────────────────────────────┐
│                供应商报价详情 - 木材供应商                  │
├─────────────────────────────────────────────────────────────┤
│  历史报价比对区域                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📊 该供应商前3次报价对比  [展开/收起 ▼]                │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │ │
│ │ │ 2024-12-20  │ │ 2024-11-15  │ │ 2024-10-10  │         │ │
│ │ │ SQ2024088   │ │ SQ2024065   │ │ SQ2024042   │         │ │
│ │ │ ¥88,000     │ │ ¥90,000     │ │ ¥85,000     │         │ │
│ │ │ [查看详情]  │ │ [查看详情]  │ │ [查看详情]  │         │ │
│ │ │ [对比分析]  │ │ [对比分析]  │ │ [对比分析]  │         │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘         │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  当前报价信息                                               │
│  供应商: 木材供应商      报价日期: 2025-01-15              │
│  有效期: 30天           报价编号: SQ2025001                │
│  产品类别: 生态板       询价编号: RFQ2025001               │
├─────────────────────────────────────────────────────────────┤
│  产品明细                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 产品名称    │ 规格     │ 数量 │ 单价    │ 小计    │历史价格│ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 生态板18mm  │ E0级     │ 100  │ 280     │ 28,000  │📊     │ │
│ │ 生态板15mm  │ E0级     │ 200  │ 250     │ 50,000  │📊     │ │
│ │ 运费       │ 物流费用  │ 1    │ 7,000   │ 7,000   │📊     │ │
│ │                                        总计: ¥85,000    │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  价格趋势分析                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  💡 智能分析:                                           │ │
│ │  • 生态板18mm价格比上次下降2.8%，市场价格趋于稳定       │ │
│ │  • 生态板15mm价格与历史平均价格一致                     │ │
│ │  • 总报价比上次降低3.4%，供应商让利明显                 │ │
│ │  • 建议：价格合理，可考虑接受并建立长期合作             │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  操作按钮                                                   │
│  [💾 保存] [📊 详细比对] [✅ 接受报价] [❌ 拒绝报价]        │
└─────────────────────────────────────────────────────────────┘
```

#### 供应商报价详细比对弹窗
```
┌─────────────────────────────────────────────────────────────┐
│                供应商报价详细比对分析                       │
├─────────────────────────────────────────────────────────────┤
│  时间轴导航                                                 │
│  [当前报价] ←→ [2024-12-20] ←→ [2024-11-15] ←→ [2024-10-10] │
├─────────────────────────────────────────────────────────────┤
│  并排比对视图                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 当前报价(2025-01-15) │ 上次报价(2024-12-20) │ 变化趋势   │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 生态板18mm: ¥280     │ 生态板18mm: ¥288     │ ↓ -2.8%   │ │
│ │ 生态板15mm: ¥250     │ 生态板15mm: ¥250     │ → 0%      │ │
│ │ 运费: ¥7,000        │ 运费: ¥8,000        │ ↓ -12.5%  │ │
│ │ 总计: ¥85,000       │ 总计: ¥88,000       │ ↓ -3.4%   │ │
│ └─────────────────────────────────────────────────────
├─────────────────────────────────────────────────────────────┤
│  价格趋势图表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📈 供应商价格趋势分析                                  │ │
│ │     ¥95K  ┤                                             │ │
│ │     ¥90K  ┤           ●                                 │ │
│ │     ¥85K  ┤     ●           ●         ●                 │ │
│ │     ¥80K  ┤                                             │ │
│ │     ¥75K  └─────────────────────────────────────────    │ │
│ │           2024-10  2024-11  2024-12  2025-01           │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  供应商评估                                                 │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  🎯 供应商评估:                                         │ │
│ │  • 价格稳定性: ⭐⭐⭐⭐☆ (4/5)                          │ │
│ │  • 价格竞争力: ⭐⭐⭐⭐⭐ (5/5)                          │ │
│ │  • 合作推荐度: 85% (基于历史表现)                       │ │
│ │  • 建议策略: 价格合理且呈下降趋势，建议接受             │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [📋 接受报价] [📊 导出分析] [💾 保存比对] [❌ 关闭]        │
└─────────────────────────────────────────────────────────────┘
```

### 多供应商比价功能

#### 同产品多供应商比价界面
```
┌─────────────────────────────────────────────────────────────┐
│                    多供应商比价分析                         │
├─────────────────────────────────────────────────────────────┤
│  询价信息                                                   │
│  询价编号: RFQ2025001    产品类别: 生态板                  │
│  询价日期: 2025-01-10    截止日期: 2025-01-20              │
├─────────────────────────────────────────────────────────────┤
│  供应商报价对比                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 供应商      │ 总报价   │ 交期 │ 质量等级│ 综合评分│ 推荐  │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 木材供应商  │ ¥85,000  │ 7天  │ E0级    │ 92分   │ ⭐⭐⭐ │ │
│ │ 板材厂家    │ ¥88,000  │ 5天  │ E0级    │ 88分   │ ⭐⭐   │ │
│ │ 环保材料    │ ¥82,000  │ 10天 │ E1级    │ 85分   │ ⭐⭐   │ │
│ │ 优质木业    │ ¥92,000  │ 3天  │ E0级    │ 90分   │ ⭐⭐⭐ │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  详细产品价格对比                                           │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 产品        │木材供应商│板材厂家 │环保材料 │优质木业     │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 生态板18mm  │ ¥280    │ ¥285   │ ¥275   │ ¥290       │ │
│ │ 生态板15mm  │ ¥250    │ ¥255   │ ¥245   │ ¥260       │ │
│ │ 运费        │ ¥7,000  │ ¥6,000 │ ¥8,000 │ ¥5,000     │ │
│ │ 最低价标识  │         │        │ ✓单价  │ ✓运费      │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  智能推荐                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  🤖 AI推荐分析:                                         │ │
│ │  推荐供应商: 木材供应商                                 │ │
│ │  推荐理由:                                              │ │
│ │  • 价格适中，性价比最高                                 │ │
│ │  • 历史合作表现良好，质量稳定                           │ │
│ │  • 交期合理，能满足生产需求                             │ │
│ │  • 综合评分最高，风险最低                               │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [✅ 选择供应商] [📊 导出比价表] [📧 发送询价] [❌ 关闭]    │
└─────────────────────────────────────────────────────────────┘
```

### 供应商报价数据模型

#### 供应商报价相关表结构
```sql
-- 供应商报价表
CREATE TABLE supplier_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INTEGER NOT NULL,
    rfq_id INTEGER, -- 关联询价单
    quote_date DATE NOT NULL,
    valid_until DATE NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    delivery_days INTEGER, -- 交期天数
    quality_grade VARCHAR(20), -- 质量等级
    status VARCHAR(20) DEFAULT 'received', -- received, accepted, rejected, expired
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (rfq_id) REFERENCES rfq_requests(id)
);

-- 供应商报价明细表
CREATE TABLE supplier_quote_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_spec VARCHAR(100),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(15,2) NOT NULL,
    notes TEXT,
    FOREIGN KEY (quote_id) REFERENCES supplier_quotes(id) ON DELETE CASCADE
);

-- 询价单表 (RFQ - Request for Quotation)
CREATE TABLE rfq_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfq_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    request_date DATE NOT NULL,
    deadline_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'sent', -- sent, closed, cancelled
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 询价单明细表
CREATE TABLE rfq_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfq_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_spec VARCHAR(100),
    quantity INTEGER NOT NULL,
    target_price DECIMAL(10,2), -- 目标价格
    notes TEXT,
    FOREIGN KEY (rfq_id) REFERENCES rfq_requests(id) ON DELETE CASCADE
);

-- 供应商报价比对历史表
CREATE TABLE supplier_quote_comparisons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    current_quote_id INTEGER NOT NULL,
    comparison_data TEXT, -- JSON格式存储比对数据
    analysis_result TEXT, -- JSON格式存储分析结果
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (current_quote_id) REFERENCES supplier_quotes(id)
);
```

### 供应商报价服务

#### 供应商报价比对服务
```python
class SupplierQuoteComparisonService:
    """供应商报价比对服务"""

    def __init__(self, quote_dao: SupplierQuoteDAO):
        self._quote_dao = quote_dao
        self._logger = logging.getLogger(__name__)

    def get_supplier_quote_comparison(
        self,
        supplier_id: int,
        current_quote_data: Dict[str, Any]
    ) -> SupplierQuoteComparison:
        """获取供应商报价比对数据"""
        try:
            # 获取该供应商历史报价（最近3次）
            historical_quotes = self._quote_dao.get_recent_quotes_by_supplier(
                supplier_id, limit=3
            )

            # 创建当前报价对象
            current_quote = self._create_quote_from_data(current_quote_data)

            # 生成比对项目
            comparison_items = self._generate_supplier_item_comparisons(
                current_quote, historical_quotes
            )

            # 计算价格趋势
            price_trends = self._calculate_supplier_price_trends(
                current_quote, historical_quotes
            )

            # 生成供应商评估
            supplier_evaluation = self._generate_supplier_evaluation(
                supplier_id, current_quote, historical_quotes, comparison_items
            )

            return SupplierQuoteComparison(
                supplier_id=supplier_id,
                current_quote=current_quote,
                historical_quotes=historical_quotes,
                comparison_items=comparison_items,
                price_trends=price_trends,
                supplier_evaluation=supplier_evaluation
            )

        except Exception as e:
            self._logger.error(f"供应商报价比对失败: {e}")
            raise BusinessLogicError(f"无法生成供应商报价比对: {e}")

    def get_multi_supplier_comparison(
        self,
        rfq_id: int
    ) -> MultiSupplierComparison:
        """获取多供应商比价数据"""
        try:
            # 获取询价单信息
            rfq_info = self._quote_dao.get_rfq_by_id(rfq_id)
            if not rfq_info:
                raise BusinessLogicError(f"询价单不存在: {rfq_id}")

            # 获取所有供应商报价
            supplier_quotes = self._quote_dao.get_quotes_by_rfq(rfq_id)

            # 生成比价分析
            comparison_analysis = self._generate_multi_supplier_analysis(
                supplier_quotes
            )

            # 生成智能推荐
            recommendation = self._generate_supplier_recommendation(
                supplier_quotes, comparison_analysis
            )

            return MultiSupplierComparison(
                rfq_info=rfq_info,
                supplier_quotes=supplier_quotes,
                comparison_analysis=comparison_analysis,
                recommendation=recommendation
            )

        except Exception as e:
            self._logger.error(f"多供应商比价失败: {e}")
            raise BusinessLogicError(f"无法生成多供应商比价: {e}")

    def _generate_supplier_evaluation(
        self,
        supplier_id: int,
        current_quote: SupplierQuote,
        historical_quotes: List[SupplierQuote],
        comparison_items: List[SupplierQuoteItemComparison]
    ) -> SupplierEvaluation:
        """生成供应商评估"""

        # 计算价格稳定性评分
        price_stability = self._calculate_price_stability(historical_quotes)

        # 计算价格竞争力评分
        price_competitiveness = self._calculate_price_competitiveness(
            current_quote, comparison_items
        )

        # 基于历史数据计算合作推荐度
        cooperation_score = self._calculate_cooperation_score(
            supplier_id, historical_quotes
        )

        # 生成策略建议
        strategy = self._generate_supplier_strategy(
            price_stability, price_competitiveness, cooperation_score
        )

        return SupplierEvaluation(
            price_stability_score=price_stability,
            price_competitiveness_score=price_competitiveness,
            cooperation_recommendation=cooperation_score,
            recommended_strategy=strategy
        )

    def _generate_supplier_recommendation(
        self,
        supplier_quotes: List[SupplierQuote],
        comparison_analysis: Dict[str, Any]
    ) -> SupplierRecommendation:
        """生成供应商推荐"""

        # 计算综合评分
        scored_suppliers = []
        for quote in supplier_quotes:
            score = self._calculate_comprehensive_score(quote, comparison_analysis)
            scored_suppliers.append((quote, score))

        # 按评分排序
        scored_suppliers.sort(key=lambda x: x[1], reverse=True)

        # 选择最佳供应商
        best_supplier = scored_suppliers[0] if scored_suppliers else None

        if best_supplier:
            quote, score = best_supplier
            reasons = self._generate_recommendation_reasons(
                quote, comparison_analysis
            )

            return SupplierRecommendation(
                recommended_supplier_id=quote.supplier_id,
                recommended_quote_id=quote.id,
                comprehensive_score=score,
                recommendation_reasons=reasons
            )

        return None

@dataclass
class SupplierQuoteComparison:
    """供应商报价比对数据类"""
    supplier_id: int
    current_quote: SupplierQuote
    historical_quotes: List[SupplierQuote]
    comparison_items: List[SupplierQuoteItemComparison]
    price_trends: Dict[str, List[float]]
    supplier_evaluation: SupplierEvaluation

@dataclass
class SupplierEvaluation:
    """供应商评估数据类"""
    price_stability_score: float
    price_competitiveness_score: float
    cooperation_recommendation: float
    recommended_strategy: str

@dataclass
class MultiSupplierComparison:
    """多供应商比价数据类"""
    rfq_info: Dict[str, Any]
    supplier_quotes: List[SupplierQuote]
    comparison_analysis: Dict[str, Any]
    recommendation: SupplierRecommendation

@dataclass
class SupplierRecommendation:
    """供应商推荐数据类"""
    recommended_supplier_id: int
    recommended_quote_id: int
    comprehensive_score: float
    recommendation_reasons: List[str]
```

这个供应商报价管理设计提供了：

1. **供应商报价统一管理** - 在业务流程页面中集成供应商报价标签
2. **历史报价比对** - 显示供应商前3次报价的详细对比分析
3. **多供应商比价** - 同一询价的多个供应商报价横向对比
4. **智能评估推荐** - 基于价格、质量、交期等因素的综合评估
5. **价格趋势分析** - 供应商价格变化趋势和稳定性分析
6. **询价单管理** - 完整的RFQ流程管理

这样您就可以高效地管理供应商报价，做出最优的采购决策！
## 供应商产品售后跟踪设计

### 供应商售后管理界面

#### 供应商售后跟踪标签页
```
┌─────────────────────────────────────────────────────────────┐
│                    供应商售后跟踪管理                       │
├─────────────────────────────────────────────────────────────┤
│  售后工单列表                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 工单编号  │ 供应商    │ 产品    │ 问题类型│ 状态    │日期│ │
│ │─────────────────────────────────────────────────────────│ │
│ │ SS2025001 │ 木材供应商│ 生态板  │ 质量问题│ 处理中  │01-15│ │
│ │ SS2025002 │ 板材厂家  │ 家具板  │ 交期延误│ 已解决  │01-14│ │
│ │ SS2025003 │ 环保材料  │ 阻燃板  │ 规格不符│ 待处理  │01-13│ │
│ │ SS2025004 │ 优质木业  │ 生态板  │ 包装破损│ 已关闭  │01-12│ │
│ └─────────────────────────────────────────────────────────┘ │
│  状态统计: 待处理(12) | 处理中(8) | 已解决(35) | 已关闭(15) │
├─────────────────────────────────────────────────────────────┤
│  问题分类统计                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📊 售后问题分类统计 (本月)                              │ │
│ │ • 质量问题: 15件 (42.9%) - 主要是板材开裂、变形        │ │
│ │ • 交期延误: 8件 (22.9%) - 供应商生产能力不足            │ │
│ │ • 规格不符: 6件 (17.1%) - 尺寸、厚度与要求不符         │ │
│ │ • 包装破损: 4件 (11.4%) - 运输过程中的损坏             │ │
│ │ • 其他问题: 2件 (5.7%) - 文档、发票等问题              │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

#### 供应商售后工单详情界面
```
┌─────────────────────────────────────────────────────────────┐
│                供应商售后工单 - SS2025001                   │
├─────────────────────────────────────────────────────────────┤
│  标签页导航                                                 │
│  [📋 基本信息] [📝 问题详情] [💬 沟通记录] [📊 处理方案]    │
├─────────────────────────────────────────────────────────────┤
│  基本信息标签页内容                                         │
│ ┌─────────────────────┐ ┌─────────────────────────────────┐ │
│ │    工单信息         │ │         产品信息                │ │
│ │  工单编号: SS2025001│ │  产品名称: 生态板18mm           │ │
│ │  供应商: 木材供应商 │ │  产品批次: B20250110            │ │
│ │  问题类型: 质量问题 │ │  采购数量: 100张                │ │
│ │  紧急程度: 高       │ │  采购金额: ¥28,000              │ │
│ │  创建时间: 01-15    │ │  采购合同: C2025001             │ │
│ │  当前状态: 处理中   │ │  交付日期: 2025-01-10           │ │
│ └─────────────────────┘ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    处理进度                             │ │
│ │  ●────●────●────○────○  创建 → 确认 → 处理 → 验收 → 关闭│ │
│ │  01-15  01-15  01-16   待定   待定                      │ │
│ │  已创建  供应商确认  开始处理  等待验收  等待关闭        │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  问题详情标签页内容                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  问题描述:                                              │ │
│ │  收到的生态板18mm存在以下质量问题：                     │ │
│ │  1. 约20%的板材表面有明显划痕和凹陷                     │ │
│ │  2. 部分板材边缘不平整，影响使用                        │ │
│ │  3. 板材厚度不均匀，误差超过标准范围                    │ │
│ │                                                         │ │
│ │  影响评估:                                              │ │
│ │  • 无法直接用于客户订单，需要重新采购                   │ │
│ │  • 可能影响客户交期，造成违约风险                       │ │
│ │  • 预计损失: ¥28,000 + 重新采购成本                    │ │
│ │                                                         │ │
│ │  要求处理方案:                                          │ │
│ │  1. 供应商派技术人员现场查看                            │ │
│ │  2. 更换全部不合格产品                                  │ │
│ │  3. 承担重新采购的额外成本                              │ │
│ │  4. 提供质量保证措施，避免再次发生                      │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  沟通记录标签页内容                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📞 2025-01-15 10:30 - 电话沟通                         │ │
│ │  联系人: 张经理 (木材供应商)                            │ │
│ │  内容: 已向供应商反馈质量问题，对方表示重视，承诺当天   │ │
│ │        派技术人员到现场查看。                           │ │
│ │  ────────────────────────────────────────────────────── │ │
│ │  📧 2025-01-15 14:20 - 邮件确认                         │ │
│ │  发送方: 张经理 (木材供应商)                    │ │
│ │  内容: 确认收到质量问题反馈，技术人员明天上午到达现场。 │ │
│ │        初步分析可能是生产工艺问题，将全力配合解决。     │ │
│ │  ────────────────────────────────────────────────────── │ │
│ │  🏃 2025-01-16 09:00 - 现场查看                         │ │
│ │  参与人: 李工程师 (供应商技术), 王主管 (我方质检)       │ │
│ │  结果: 确认质量问题属实，供应商承认生产过程中的疏忽。   │ │
│ │        同意更换全部产品，并承担相关费用。               │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  处理方案标签页内容                                         │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  🔧 供应商处理方案:                                     │ │
│ │  1. 立即安排更换全部不合格产品 (100张)                  │ │
│ │  2. 新产品将在3个工作日内交付                           │ │
│ │  3. 承担重新运输费用 ¥2,000                            │ │
│ │  4. 给予5%的价格折扣作为补偿 ¥1,400                    │ │
│ │  5. 建立专项质检流程，确保后续产品质量                  │ │
│ │                                                         │ │
│ │  📋 我方验收标准:                                       │ │
│ │  1. 新产品必须通过第三方质检机构检验                    │ │
│ │  2. 表面质量达到A级标准，无划痕凹陷                     │ │
│ │  3. 厚度误差控制在±0.1mm范围内                         │ │
│ │  4. 边缘平整度符合行业标准                              │ │
│ │                                                         │ │
│ │  💰 费用结算:                                           │ │
│ │  • 原产品退款: ¥28,000                                 │ │
│ │  • 运输费补偿: ¥2,000                                  │ │
│ │  • 价格折扣: ¥1,400                                    │ │
│ │  • 总补偿金额: ¥31,400                                 │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  操作按钮                                                   │
│  [📝 添加沟通] [✅ 确认方案] [❌ 拒绝方案] [🔄 更新状态]    │
└─────────────────────────────────────────────────────────────┘
```

### 供应商售后统计分析

#### 供应商售后质量分析界面
```
┌─────────────────────────────────────────────────────────────┐
│                供应商售后质量分析报告                       │
├─────────────────────────────────────────────────────────────┤
│  时间范围选择                                               │
│  [最近30天] [最近3个月] [最近6个月] [最近1年] [自定义]      │
├─────────────────────────────────────────────────────────────┤
│  供应商售后统计                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 供应商      │售后次数│问题率│平均处理│满意度│质量评级    │ │
│ │─────────────────────────────────────────────────────────│ │
│ │ 木材供应商  │ 8次    │2.1% │ 3.2天  │ 4.2分│ B级 ⚠️     │ │
│ │ 板材厂家    │ 3次    │0.8% │ 2.1天  │ 4.6分│ A级 ✅     │ │
│ │ 环保材料    │ 12次   │3.5% │ 4.8天  │ 3.8分│ C级 ❌     │ │
│ │ 优质木业    │ 2次    │0.5% │ 1.8天  │ 4.8分│ A级 ✅     │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  问题趋势分析                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  📈 售后问题趋势图                                      │ │
│ │     15 ┤                                                │ │
│ │     12 ┤     ●                                          │ │
│ │      9 ┤           ●                                    │ │
│ │      6 ┤                 ●         ●                    │ │
│ │      3 ┤                       ●       ●               │ │
│ │      0 └─────────────────────────────────────────       │ │
│ │        10月   11月   12月   1月    2月    3月          │ │
│ │                                                         │ │
│ │  趋势分析: 售后问题数量呈下降趋势，供应商质量管理       │ │
│ │           措施开始见效，但仍需持续关注重点供应商。      │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  改进建议                                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │  🎯 供应商管理建议:                                     │ │
│ │                                                         │ │
│ │  高风险供应商 (环保材料):                               │ │
│ │  • 问题率3.5%，超过行业平均水平                         │ │
│ │  • 建议: 加强入厂检验，要求提供质量改进计划             │ │
│ │  • 考虑: 寻找备选供应商，降低依赖度                     │ │
│ │                                                         │ │
│ │  关注供应商 (木材供应商):                               │ │
│ │  • 问题率2.1%，处于临界水平                             │ │
│ │  • 建议: 定期质量审核，建立质量改进机制                 │ │
│ │  • 措施: 增加抽检频率，强化质量协议                     │ │
│ │                                                         │ │
│ │  优秀供应商 (板材厂家、优质木业):                       │ │
│ │  • 问题率低于1%，质量稳定可靠                           │ │
│ │  • 建议: 建立长期合作关系，给予更多订单                 │ │
│ │  • 激励: 考虑价格优惠或优先合作政策                     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 供应商售后数据模型

#### 供应商售后相关表结构
```sql
-- 供应商售后工单表
CREATE TABLE supplier_service_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_batch VARCHAR(100), -- 产品批次
    purchase_contract_id INTEGER, -- 关联采购合同
    issue_type VARCHAR(50) NOT NULL, -- 问题类型
    priority VARCHAR(20) DEFAULT 'medium', -- 紧急程度: high, medium, low
    status VARCHAR(20) DEFAULT 'created', -- created, confirmed, processing, resolved, closed
    issue_description TEXT NOT NULL,
    impact_assessment TEXT, -- 影响评估
    required_solution TEXT, -- 要求处理方案
    supplier_solution TEXT, -- 供应商处理方案
    acceptance_criteria TEXT, -- 验收标准
    compensation_amount DECIMAL(15,2) DEFAULT 0, -- 补偿金额
    created_by VARCHAR(100),
    assigned_to VARCHAR(100), -- 负责人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP, -- 解决时间
    closed_at TIMESTAMP, -- 关闭时间
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
    FOREIGN KEY (purchase_contract_id) REFERENCES purchase_contracts(id)
);

-- 供应商售后沟通记录表
CREATE TABLE supplier_service_communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    communication_type VARCHAR(20) NOT NULL, -- phone, email, meeting, site_visit
    contact_person VARCHAR(100),
    contact_company VARCHAR(100), -- 联系人所属公司
    communication_date TIMESTAMP NOT NULL,
    content TEXT NOT NULL,
    attachments TEXT, -- JSON格式存储附件信息
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES supplier_service_tickets(id) ON DELETE CASCADE
);

-- 供应商售后处理方案表
CREATE TABLE supplier_service_solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    solution_type VARCHAR(50), -- replacement, repair, refund, compensation
    solution_description TEXT NOT NULL,
    cost_estimate DECIMAL(15,2), -- 成本估算
    timeline_days INTEGER, -- 处理时间(天)
    acceptance_criteria TEXT, -- 验收标准
    status VARCHAR(20) DEFAULT 'proposed', -- proposed, accepted, rejected, completed
    proposed_by VARCHAR(100), -- 提出方
    proposed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted_at TIMESTAMP, -- 接受时间
    completed_at TIMESTAMP, -- 完成时间
    FOREIGN KEY (ticket_id) REFERENCES supplier_service_tickets(id) ON DELETE CASCADE
);

-- 供应商质量评估表
CREATE TABLE supplier_quality_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    assessment_period VARCHAR(20) NOT NULL, -- monthly, quarterly, yearly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_orders INTEGER DEFAULT 0, -- 总订单数
    total_issues INTEGER DEFAULT 0, -- 总问题数
    issue_rate DECIMAL(5,2) DEFAULT 0, -- 问题率(%)
    avg_resolution_days DECIMAL(5,2) DEFAULT 0, -- 平均解决天数
    satisfaction_score DECIMAL(3,1) DEFAULT 0, -- 满意度评分(1-5)
    quality_grade VARCHAR(10), -- 质量等级: A, B, C, D
    improvement_suggestions TEXT, -- 改进建议
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);
```

### 供应商售后服务类

#### 供应商售后管理服务
```python
class SupplierServiceTicketService:
    """供应商售后工单管理服务"""

    def __init__(self, ticket_dao: SupplierServiceTicketDAO):
        self._ticket_dao = ticket_dao
        self._logger = logging.getLogger(__name__)

    def create_service_ticket(
        self,
        ticket_data: Dict[str, Any]
    ) -> int:
        """创建供应商售后工单"""
        try:
            # 验证必填字段
            required_fields = [
                'supplier_id', 'product_name', 'issue_type',
                'issue_description'
            ]
            for field in required_fields:
                if not ticket_data.get(field):
                    raise ValidationError(f"字段 {field} 不能为空")

            # 生成工单编号
            ticket_data['ticket_number'] = self._generate_ticket_number()

            # 设置默认值
            ticket_data.setdefault('priority', 'medium')
            ticket_data.setdefault('status', 'created')
            ticket_data.setdefault('created_by', 'system')

            # 创建工单
            ticket_id = self._ticket_dao.insert(ticket_data)

            # 自动通知供应商
            self._notify_supplier_about_issue(ticket_id)

            self._logger.info(f"成功创建供应商售后工单: {ticket_id}")
            return ticket_id

        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"创建供应商售后工单失败: {e}")
            raise BusinessLogicError(f"创建售后工单失败: {e}")

    def add_communication_record(
        self,
        ticket_id: int,
        communication_data: Dict[str, Any]
    ) -> int:
        """添加沟通记录"""
        try:
            # 验证工单是否存在
            if not self._ticket_dao.exists_by_id(ticket_id):
                raise BusinessLogicError(f"售后工单不存在: {ticket_id}")

            # 验证必填字段
            required_fields = ['communication_type', 'content']
            for field in required_fields:
                if not communication_data.get(field):
                    raise ValidationError(f"字段 {field} 不能为空")

            communication_data['ticket_id'] = ticket_id
            communication_data.setdefault('communication_date', datetime.now())
            communication_data.setdefault('created_by', 'system')

            # 添加沟通记录
            comm_id = self._ticket_dao.insert_communication(communication_data)

            # 更新工单状态
            self._update_ticket_status_based_on_communication(
                ticket_id, communication_data
            )

            self._logger.info(f"成功添加沟通记录: {comm_id}")
            return comm_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"添加沟通记录失败: {e}")
            raise BusinessLogicError(f"添加沟通记录失败: {e}")

    def propose_solution(
        self,
        ticket_id: int,
        solution_data: Dict[str, Any]
    ) -> int:
        """提出处理方案"""
        try:
            # 验证工单是否存在
            if not self._ticket_dao.exists_by_id(ticket_id):
                raise BusinessLogicError(f"售后工单不存在: {ticket_id}")

            # 验证必填字段
            if not solution_data.get('solution_description'):
                raise ValidationError("处理方案描述不能为空")

            solution_data['ticket_id'] = ticket_id
            solution_data.setdefault('status', 'proposed')
            solution_data.setdefault('proposed_by', 'supplier')
            solution_data.setdefault('proposed_at', datetime.now())

            # 添加处理方案
            solution_id = self._ticket_dao.insert_solution(solution_data)

            # 更新工单状态为处理中
            self._ticket_dao.update_status(ticket_id, 'processing')

            self._logger.info(f"成功提出处理方案: {solution_id}")
            return solution_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"提出处理方案失败: {e}")
            raise BusinessLogicError(f"提出处理方案失败: {e}")

    def accept_solution(
        self,
        solution_id: int,
        acceptance_data: Dict[str, Any] = None
    ) -> bool:
        """接受处理方案"""
        try:
            # 验证方案是否存在
            solution = self._ticket_dao.get_solution_by_id(solution_id)
            if not solution:
                raise BusinessLogicError(f"处理方案不存在: {solution_id}")

            # 更新方案状态
            update_data = {
                'status': 'accepted',
                'accepted_at': datetime.now()
            }

            if acceptance_data:
                update_data.update(acceptance_data)

            result = self._ticket_dao.update_solution(solution_id, update_data)

            if result:
                # 更新工单状态
                self._ticket_dao.update_status(
                    solution['ticket_id'], 'processing'
                )

                self._logger.info(f"成功接受处理方案: {solution_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"接受处理方案失败: {e}")
            raise BusinessLogicError(f"接受处理方案失败: {e}")

    def complete_solution(
        self,
        solution_id: int,
        completion_data: Dict[str, Any] = None
    ) -> bool:
        """完成处理方案"""
        try:
            # 验证方案是否存在且已接受
            solution = self._ticket_dao.get_solution_by_id(solution_id)
            if not solution:
                raise BusinessLogicError(f"处理方案不存在: {solution_id}")

            if solution['status'] != 'accepted':
                raise BusinessLogicError("只能完成已接受的处理方案")

            # 更新方案状态
            update_data = {
                'status': 'completed',
                'completed_at': datetime.now()
            }

            if completion_data:
                update_data.update(completion_data)

            result = self._ticket_dao.update_solution(solution_id, update_data)

            if result:
                # 更新工单状态为已解决
                self._ticket_dao.update_status(
                    solution['ticket_id'], 'resolved'
                )

                # 记录解决时间
                self._ticket_dao.update(
                    solution['ticket_id'],
                    {'resolved_at': datetime.now()}
                )

                self._logger.info(f"成功完成处理方案: {solution_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"完成处理方案失败: {e}")
            raise BusinessLogicError(f"完成处理方案失败: {e}")

    def get_supplier_quality_analysis(
        self,
        supplier_id: int = None,
        period_months: int = 6
    ) -> Dict[str, Any]:
        """获取供应商质量分析"""
        try:
            # 计算时间范围
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_months * 30)

            # 获取售后统计数据
            if supplier_id:
                suppliers_data = [self._get_supplier_quality_stats(
                    supplier_id, start_date, end_date
                )]
            else:
                suppliers_data = self._get_all_suppliers_quality_stats(
                    start_date, end_date
                )

            # 获取问题趋势数据
            trend_data = self._get_issue_trend_data(start_date, end_date)

            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(
                suppliers_data
            )

            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'months': period_months
                },
                'suppliers_stats': suppliers_data,
                'trend_data': trend_data,
                'improvement_suggestions': improvement_suggestions
            }

        except Exception as e:
            self._logger.error(f"获取供应商质量分析失败: {e}")
            raise BusinessLogicError(f"获取质量分析失败: {e}")

    def _get_supplier_quality_stats(
        self,
        supplier_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """获取单个供应商质量统计"""

        # 获取基本统计数据
        stats = self._ticket_dao.get_supplier_stats(
            supplier_id, start_date, end_date
        )

        # 计算质量指标
        total_orders = stats.get('total_orders', 0)
        total_issues = stats.get('total_issues', 0)
        issue_rate = (total_issues / total_orders * 100) if total_orders > 0 else 0

        # 计算平均处理时间
        avg_resolution_days = stats.get('avg_resolution_days', 0)

        # 计算满意度评分
        satisfaction_score = stats.get('avg_satisfaction', 0)

        # 确定质量等级
        quality_grade = self._calculate_quality_grade(
            issue_rate, avg_resolution_days, satisfaction_score
        )

        return {
            'supplier_id': supplier_id,
            'supplier_name': stats.get('supplier_name', ''),
            'total_orders': total_orders,
            'total_issues': total_issues,
            'issue_rate': round(issue_rate, 2),
            'avg_resolution_days': round(avg_resolution_days, 1),
            'satisfaction_score': round(satisfaction_score, 1),
            'quality_grade': quality_grade
        }

    def _calculate_quality_grade(
        self,
        issue_rate: float,
        avg_resolution_days: float,
        satisfaction_score: float
    ) -> str:
        """计算质量等级"""

        # 质量等级评分规则
        if issue_rate <= 1.0 and avg_resolution_days <= 2.0 and satisfaction_score >= 4.5:
            return 'A'
        elif issue_rate <= 2.0 and avg_resolution_days <= 3.0 and satisfaction_score >= 4.0:
            return 'B'
        elif issue_rate <= 3.0 and avg_resolution_days <= 5.0 and satisfaction_score >= 3.5:
            return 'C'
        else:
            return 'D'

    def _generate_improvement_suggestions(
        self,
        suppliers_data: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """生成改进建议"""

        suggestions = {
            'high_risk': [],
            'attention_needed': [],
            'excellent': []
        }

        for supplier in suppliers_data:
            supplier_name = supplier['supplier_name']
            issue_rate = supplier['issue_rate']
            quality_grade = supplier['quality_grade']

            if quality_grade == 'D' or issue_rate > 3.0:
                suggestions['high_risk'].append({
                    'supplier': supplier_name,
                    'issue_rate': issue_rate,
                    'recommendations': [
                        '加强入厂检验，要求提供质量改进计划',
                        '考虑寻找备选供应商，降低依赖度',
                        '建立质量保证金制度'
                    ]
                })
            elif quality_grade == 'C' or issue_rate > 1.5:
                suggestions['attention_needed'].append({
                    'supplier': supplier_name,
                    'issue_rate': issue_rate,
                    'recommendations': [
                        '定期质量审核，建立质量改进机制',
                        '增加抽检频率，强化质量协议',
                        '要求供应商提供质量改进报告'
                    ]
                })
            elif quality_grade in ['A', 'B'] and issue_rate <= 1.0:
                suggestions['excellent'].append({
                    'supplier': supplier_name,
                    'issue_rate': issue_rate,
                    'recommendations': [
                        '建立长期合作关系，给予更多订单',
                        '考虑价格优惠或优先合作政策',
                        '作为标杆供应商，分享最佳实践'
                    ]
                })

        return suggestions

@dataclass
class SupplierServiceTicket:
    """供应商售后工单数据类"""
    id: Optional[int] = None
    ticket_number: str = ""
    supplier_id: int = 0
    product_name: str = ""
    product_batch: str = ""
    issue_type: str = ""
    priority: str = "medium"
    status: str = "created"
    issue_description: str = ""
    impact_assessment: str = ""
    required_solution: str = ""
    supplier_solution: str = ""
    compensation_amount: float = 0.0
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
```

这个供应商产品售后跟踪设计提供了：

1. **完整的售后工单管理** - 从问题创建到解决关闭的全流程跟踪
2. **详细的沟通记录** - 电话、邮件、现场查看等各种沟通方式记录
3. **处理方案管理** - 供应商提出方案、我方确认、执行验收的完整流程
4. **质量统计分析** - 供应商问题率、处理时间、满意度等关键指标
5. **智能改进建议** - 基于数据分析的供应商管理建议
6. **多维度评估** - 质量等级、风险分类、合作建议等综合评估

这样您就可以有效地管理供应商产品质量，及时处理售后问题，并基于数据做出供应商管理决策！

<function_calls>
<invoke name="userInput">
<parameter name="question">**供应商产品售后跟踪功能设计已完成，包含了完整的工单管理、沟通记录、处理方案和质量分析。整个MiniCRM设计文档现在是否完整并满足您的需求？如果满意的话，我们可以继续创建实施任务列表。**
