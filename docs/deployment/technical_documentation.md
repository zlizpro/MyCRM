# MiniCRM技术文档

## 项目概述

MiniCRM是一个基于Python tkinter/ttk框架开发的跨平台客户关系管理系统，专为板材行业设计。本文档详细描述了系统的技术架构、部署方式、开发指南和维护说明。

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MiniCRM 技术架构                          │
├─────────────────────────────────────────────────────────────┤
│  表示层 (Presentation Layer)                                │
│  ├── UI组件 (tkinter/ttk)                                   │
│  ├── 主题系统 (Theme System)                                │
│  ├── 事件处理 (Event Handling)                              │
│  └── 响应式布局 (Responsive Layout)                         │
├─────────────────────────────────────────────────────────────┤
│  业务逻辑层 (Business Logic Layer)                          │
│  ├── 客户服务 (Customer Service)                            │
│  ├── 供应商服务 (Supplier Service)                          │
│  ├── 报价服务 (Quote Service)                               │
│  ├── 合同服务 (Contract Service)                            │
│  └── 财务服务 (Finance Service)                             │
├─────────────────────────────────────────────────────────────┤
│  数据访问层 (Data Access Layer)                             │
│  ├── DAO模式 (Data Access Objects)                          │
│  ├── 数据库管理 (Database Manager)                          │
│  ├── 连接池 (Connection Pool)                               │
│  └── 事务管理 (Transaction Management)                      │
├─────────────────────────────────────────────────────────────┤
│  数据存储层 (Data Storage Layer)                            │
│  ├── SQLite数据库                                           │
│  ├── 文件存储                                               │
│  └── 配置文件                                               │
├─────────────────────────────────────────────────────────────┤
│  基础设施层 (Infrastructure Layer)                          │
│  ├── 日志系统 (Logging System)                              │
│  ├── 配置管理 (Configuration Management)                    │
│  ├── 异常处理 (Exception Handling)                          │
│  ├── 性能监控 (Performance Monitoring)                      │
│  └── 资源管理 (Resource Management)                         │
└─────────────────────────────────────────────────────────────┘
```

### 核心技术栈

#### 前端技术
- **GUI框架**: Python tkinter/ttk
- **图表库**: matplotlib
- **图像处理**: Pillow (PIL)
- **主题系统**: 自定义TTK样式

#### 后端技术
- **编程语言**: Python 3.9+
- **数据库**: SQLite 3
- **ORM**: 自定义轻量级ORM
- **文档处理**: docxtpl, reportlab
- **数据处理**: pandas, openpyxl

#### 开发工具
- **包管理**: uv/pip
- **代码质量**: ruff, mypy
- **测试框架**: unittest, pytest
- **打包工具**: PyInstaller
- **版本控制**: Git

### 模块结构

```
src/minicrm/
├── core/                   # 核心模块
│   ├── constants.py        # 常量定义
│   ├── exceptions.py       # 异常类
│   ├── logging.py          # 日志系统
│   ├── config.py          # 配置管理
│   ├── resource_manager.py # 资源管理器
│   ├── performance_monitor.py # 性能监控
│   └── utils.py           # 工具函数
├── data/                  # 数据访问层
│   ├── database/          # 数据库管理
│   ├── dao/              # 数据访问对象
│   ├── migrations/       # 数据库迁移
│   └── models/           # 数据模型
├── services/             # 业务逻辑层
│   ├── customer/         # 客户服务
│   ├── supplier/         # 供应商服务
│   ├── quote/           # 报价服务
│   ├── contract/        # 合同服务
│   └── finance/         # 财务服务
├── ui/                  # 用户界面层
│   ├── ttk_base/        # TTK基础组件
│   ├── components/      # 可复用组件
│   ├── panels/          # 业务面板
│   ├── dialogs/         # 对话框
│   └── themes/          # 主题系统
├── resources/           # 资源文件
│   ├── icons/           # 图标文件
│   ├── themes/          # 主题配置
│   ├── templates/       # 文档模板
│   └── styles/          # 样式文件
└── config/              # 配置文件
    ├── settings.py      # 应用设置
    └── database.py      # 数据库配置
```

## 部署架构

### 部署模式

#### 1. 单文件部署（推荐）
```bash
# 使用PyInstaller打包为单个可执行文件
pyinstaller --onefile --windowed src/minicrm/main.py
```

**优点**:
- 部署简单，只需一个文件
- 无需安装Python环境
- 适合最终用户使用

**缺点**:
- 文件较大（约50-100MB）
- 启动时间稍长

#### 2. 目录部署
```bash
# 打包为目录结构
pyinstaller --onedir --windowed src/minicrm/main.py
```

**优点**:
- 启动速度快
- 便于调试和维护
- 可以单独更新资源文件

**缺点**:
- 需要整个目录
- 文件较多

#### 3. 源码部署（开发环境）
```bash
# 直接运行Python源码
python src/minicrm/main.py
```

**优点**:
- 便于开发和调试
- 可以实时修改代码
- 占用空间小

**缺点**:
- 需要Python环境
- 需要安装依赖包

### 跨平台兼容性

#### Windows平台
- **支持版本**: Windows 10/11 (x64)
- **打包格式**: .exe可执行文件
- **安装方式**: 直接运行或使用安装程序
- **特殊处理**:
  - 版本信息文件
  - 数字签名（可选）
  - 防病毒软件白名单

#### macOS平台
- **支持版本**: macOS 10.14+ (Intel/Apple Silicon)
- **打包格式**: .app应用包或DMG镜像
- **安装方式**: 拖拽到Applications文件夹
- **特殊处理**:
  - 代码签名和公证
  - 权限配置文件
  - 通用二进制文件

#### Linux平台
- **支持发行版**: Ubuntu 18.04+, CentOS 7+, Fedora 30+
- **打包格式**: 可执行文件、AppImage、DEB/RPM包
- **安装方式**: 直接运行或包管理器安装
- **特殊处理**:
  - 依赖库检查
  - 桌面集成文件
  - 权限设置

## 构建系统

### 构建配置

#### PyInstaller配置
```python
# build/build_config.py
class BuildConfig:
    def get_pyinstaller_args(self, onefile=True, console=False):
        args = [
            str(self.get_main_script()),
            f'--name={self.get_app_name()}',
            '--clean',
            '--noconfirm'
        ]

        if onefile:
            args.append('--onefile')
        else:
            args.append('--onedir')

        if not console:
            args.append('--windowed')

        # 添加隐藏导入
        for module in self.get_hidden_imports():
            args.append(f'--hidden-import={module}')

        # 添加数据文件
        for src, dst in self.get_data_files():
            args.append(f'--add-data={src}{os.pathsep}{dst}')

        return args
```

#### 构建脚本
```bash
# Windows构建
build/build_windows.bat

# macOS构建
build/build_macos.sh

# Linux构建
build/build_linux.sh

# 通用构建
python build/build.py
```

### 资源管理

#### 资源管理器
```python
class ResourceManager:
    def __init__(self):
        self._base_path = self._get_base_path()
        self._resource_path = self._get_resource_path()
        self._cache = {}

    def _get_base_path(self):
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller环境
            return Path(sys._MEIPASS)
        else:
            # 开发环境
            return Path(__file__).parent.parent.parent

    def get_icon_path(self, icon_name):
        # 获取图标文件路径
        pass

    def get_theme_path(self, theme_name):
        # 获取主题文件路径
        pass
```

## 数据库设计

### 数据库架构

#### 核心表结构
```sql
-- 客户表
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    customer_type_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_type_id) REFERENCES customer_types (id)
);

-- 供应商表
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    quality_rating REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 报价表
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    supplier_id INTEGER,
    product_name TEXT NOT NULL,
    specification TEXT,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    valid_until DATE,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);
```

#### 索引优化
```sql
-- 性能优化索引
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_quotes_customer_id ON quotes(customer_id);
CREATE INDEX idx_quotes_supplier_id ON quotes(supplier_id);
CREATE INDEX idx_quotes_status ON quotes(status);
CREATE INDEX idx_quotes_created_at ON quotes(created_at);
```

### 数据访问层

#### DAO模式实现
```python
class BaseDAO:
    def __init__(self, db_manager):
        self._db = db_manager

    def insert(self, table, data):
        # 插入数据
        pass

    def update(self, table, data, where_clause):
        # 更新数据
        pass

    def delete(self, table, where_clause):
        # 删除数据
        pass

    def select(self, table, columns='*', where_clause=None):
        # 查询数据
        pass

class CustomerDAO(BaseDAO):
    def create_customer(self, customer_data):
        return self.insert('customers', customer_data)

    def get_customer_by_id(self, customer_id):
        return self.select('customers', where_clause=f'id = {customer_id}')
```

## 性能优化

### 应用程序性能

#### 启动优化
```python
# 延迟导入
def lazy_import_matplotlib():
    global plt
    if 'plt' not in globals():
        import matplotlib.pyplot as plt
    return plt

# 缓存机制
@lru_cache(maxsize=128)
def get_customer_statistics(customer_id):
    # 缓存客户统计信息
    pass
```

#### 内存优化
```python
# 虚拟滚动
class VirtualScrollMixin:
    def __init__(self):
        self.visible_start = 0
        self.visible_count = 50
        self.total_count = 0

    def render_visible_items(self):
        # 只渲染可见项目
        pass

# 数据分页
class PaginatedDataLoader:
    def __init__(self, page_size=50):
        self.page_size = page_size
        self.current_page = 0

    def load_page(self, page_number):
        # 分页加载数据
        pass
```

#### 数据库优化
```python
# 连接池
class ConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.in_use = set()

    def get_connection(self):
        # 获取数据库连接
        pass

    def return_connection(self, conn):
        # 归还数据库连接
        pass

# 查询优化
class QueryOptimizer:
    def optimize_query(self, sql):
        # 查询优化
        pass

    def add_index_hint(self, sql, index_name):
        # 添加索引提示
        pass
```

### UI性能优化

#### 响应式设计
```python
class ResponsiveLayout:
    def __init__(self):
        self.breakpoints = {
            'small': 800,
            'medium': 1200,
            'large': 1600
        }

    def get_layout_for_size(self, width, height):
        # 根据窗口大小返回布局
        pass

# 异步UI更新
class AsyncUIUpdater:
    def __init__(self):
        self.update_queue = queue.Queue()
        self.worker_thread = None

    def schedule_update(self, update_func, *args):
        # 调度UI更新
        pass
```

## 测试策略

### 测试架构

#### 测试分层
```
测试金字塔:
┌─────────────────────────────────────┐
│           E2E测试 (5%)               │  ← 端到端测试
├─────────────────────────────────────┤
│         集成测试 (15%)               │  ← 模块集成测试
├─────────────────────────────────────┤
│         单元测试 (80%)               │  ← 函数/类测试
└─────────────────────────────────────┘
```

#### 测试类型

1. **单元测试**
   ```python
   class TestCustomerService(unittest.TestCase):
       def setUp(self):
           self.service = CustomerService(MockDAO())

       def test_create_customer(self):
           customer_data = {'name': '测试客户'}
           result = self.service.create_customer(customer_data)
           self.assertIsNotNone(result)
   ```

2. **集成测试**
   ```python
   class TestDatabaseIntegration(unittest.TestCase):
       def test_customer_crud_operations(self):
           # 测试完整的CRUD操作流程
           pass
   ```

3. **UI测试**
   ```python
   class TestUIComponents(unittest.TestCase):
       def setUp(self):
           self.root = tk.Tk()
           self.root.withdraw()

       def test_customer_panel_creation(self):
           panel = CustomerPanel(self.root)
           self.assertIsInstance(panel, CustomerPanel)
   ```

4. **性能测试**
   ```python
   class TestPerformance(unittest.TestCase):
       def test_large_dataset_loading(self):
           start_time = time.time()
           # 加载大量数据
           end_time = time.time()
           self.assertLess(end_time - start_time, 1.0)
   ```

### 测试工具

#### 测试运行器
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_services/

# 生成覆盖率报告
python -m pytest --cov=src/minicrm tests/
```

#### 模拟和存根
```python
# 数据库模拟
class MockDatabaseManager:
    def __init__(self):
        self.data = {}

    def execute_query(self, sql, params=None):
        # 模拟数据库查询
        pass

# UI组件模拟
class MockTkinterWidget:
    def __init__(self, *args, **kwargs):
        self.config = kwargs

    def configure(self, **kwargs):
        self.config.update(kwargs)
```

## 安全考虑

### 数据安全

#### 数据加密
```python
# 敏感数据加密
class DataEncryption:
    def __init__(self, key):
        self.cipher = Fernet(key)

    def encrypt_data(self, data):
        return self.cipher.encrypt(data.encode())

    def decrypt_data(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data).decode()
```

#### 输入验证
```python
class InputValidator:
    @staticmethod
    def validate_phone(phone):
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def sanitize_input(input_string):
        # 清理输入数据
        return html.escape(input_string.strip())
```

### 应用程序安全

#### 权限控制
```python
class PermissionManager:
    def __init__(self):
        self.permissions = {}

    def check_permission(self, user, action, resource):
        # 检查用户权限
        pass

    def grant_permission(self, user, action, resource):
        # 授予权限
        pass
```

#### 审计日志
```python
class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')

    def log_action(self, user, action, resource, result):
        self.logger.info(f"User: {user}, Action: {action}, Resource: {resource}, Result: {result}")
```

## 监控和维护

### 应用程序监控

#### 性能监控
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    def record_execution_time(self, function_name, execution_time):
        if function_name not in self.metrics:
            self.metrics[function_name] = []
        self.metrics[function_name].append(execution_time)

    def get_average_execution_time(self, function_name):
        if function_name in self.metrics:
            return sum(self.metrics[function_name]) / len(self.metrics[function_name])
        return 0
```

#### 错误监控
```python
class ErrorMonitor:
    def __init__(self):
        self.error_count = {}
        self.logger = logging.getLogger('error_monitor')

    def record_error(self, error_type, error_message):
        if error_type not in self.error_count:
            self.error_count[error_type] = 0
        self.error_count[error_type] += 1

        self.logger.error(f"Error Type: {error_type}, Message: {error_message}")
```

### 维护工具

#### 数据库维护
```python
class DatabaseMaintenance:
    def __init__(self, db_manager):
        self.db = db_manager

    def vacuum_database(self):
        # 清理数据库碎片
        self.db.execute('VACUUM')

    def analyze_database(self):
        # 分析数据库统计信息
        self.db.execute('ANALYZE')

    def check_integrity(self):
        # 检查数据库完整性
        result = self.db.execute('PRAGMA integrity_check')
        return result.fetchone()[0] == 'ok'
```

#### 日志管理
```python
class LogManager:
    def __init__(self, log_dir):
        self.log_dir = Path(log_dir)

    def rotate_logs(self, max_size_mb=10):
        # 日志轮转
        pass

    def cleanup_old_logs(self, days_to_keep=30):
        # 清理旧日志
        pass
```

## 部署清单

### 部署前检查

#### 环境检查
- [ ] 目标系统满足最低要求
- [ ] 必要的系统依赖已安装
- [ ] 防火墙和安全软件配置
- [ ] 磁盘空间充足

#### 应用程序检查
- [ ] 所有功能测试通过
- [ ] 性能测试达标
- [ ] 安全扫描无问题
- [ ] 文档完整

#### 数据检查
- [ ] 数据库结构正确
- [ ] 初始数据准备完成
- [ ] 备份策略制定
- [ ] 迁移脚本测试

### 部署步骤

1. **准备阶段**
   ```bash
   # 创建部署目录
   mkdir -p /opt/minicrm

   # 复制应用程序文件
   cp MiniCRM-linux-x86_64 /opt/minicrm/

   # 设置权限
   chmod +x /opt/minicrm/MiniCRM-linux-x86_64
   ```

2. **配置阶段**
   ```bash
   # 创建配置文件
   cp config/settings.json /opt/minicrm/

   # 创建数据目录
   mkdir -p /opt/minicrm/data

   # 设置数据库权限
   chown -R minicrm:minicrm /opt/minicrm/data
   ```

3. **测试阶段**
   ```bash
   # 运行应用程序测试
   /opt/minicrm/MiniCRM-linux-x86_64 --test

   # 检查日志
   tail -f /opt/minicrm/logs/application.log
   ```

4. **启动阶段**
   ```bash
   # 启动应用程序
   /opt/minicrm/MiniCRM-linux-x86_64

   # 验证功能
   # 进行基本功能测试
   ```

### 部署后验证

#### 功能验证
- [ ] 应用程序正常启动
- [ ] 数据库连接正常
- [ ] 基本功能可用
- [ ] 用户界面正常显示

#### 性能验证
- [ ] 启动时间在预期范围内
- [ ] 内存使用正常
- [ ] 响应时间满足要求
- [ ] 并发处理能力达标

#### 安全验证
- [ ] 文件权限正确
- [ ] 网络访问控制生效
- [ ] 日志记录正常
- [ ] 错误处理正确

---

**文档版本**: v1.0.0
**最后更新**: 2024年1月
**维护者**: MiniCRM开发团队
