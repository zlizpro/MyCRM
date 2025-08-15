# MiniCRM 开发标准指导

## 项目特定要求

### 业务领域
- **行业背景**: 板材行业CRM系统
- **客户类型**: 生态板客户、家具板客户、阻燃板客户
- **核心业务**: 客户管理、供应商管理、报价比对、售后跟踪

### 技术栈要求
- **GUI框架**: tkinter/ttk (跨平台兼容)
- **数据库**: SQLite (轻量级本地存储)
- **文档处理**: docxtpl (Word模板), reportlab (PDF)
- **图表库**: matplotlib (数据可视化)
- **打包工具**: PyInstaller (单文件部署)

## 代码架构标准

### 分层架构
```python
# 严格遵循分层架构
minicrm/
├── ui/          # 用户界面层
├── services/    # 业务逻辑层
├── data/        # 数据访问层
├── models/      # 数据模型层
└── core/        # 核心工具层
```

### 命名规范
```python
# 类名：大驼峰
class CustomerService:
    pass

# 函数/变量：下划线
def create_customer():
    customer_data = {}

# 常量：全大写
DATABASE_PATH = "minicrm.db"

# 私有成员：下划线前缀
def _validate_data():
    pass
```

## 业务逻辑标准

### 客户管理模式
```python
# 标准客户操作模式
class CustomerService:
    def create_customer(self, customer_data: Dict[str, Any]) -> int:
        """创建客户 - 标准模式"""
        # 1. 数据验证
        self._validate_customer_data(customer_data)

        # 2. 业务规则检查
        if self._customer_exists(customer_data['name']):
            raise BusinessLogicError("客户已存在")

        # 3. 数据库操作
        customer_id = self._dao.insert(customer_data)

        # 4. 后续处理
        self._create_default_interactions(customer_id)

        # 5. 日志记录
        self._logger.info(f"成功创建客户: {customer_id}")

        return customer_id
```

### 异常处理标准
```python
# 使用项目自定义异常
try:
    result = self._perform_operation()
except ValidationError as e:
    self._logger.warning(f"数据验证失败: {e}")
    raise
except BusinessLogicError as e:
    self._logger.warning(f"业务逻辑错误: {e}")
    raise
except DatabaseError as e:
    self._logger.error(f"数据库操作失败: {e}")
    raise
except Exception as e:
    self._logger.error(f"未知错误: {e}")
    raise MiniCRMError(f"操作失败: {e}")
```

## UI开发标准

### 组件结构
```python
class CustomerPanel(ttk.Frame):
    """客户管理面板 - 标准UI组件结构"""

    def __init__(self, parent, customer_service: CustomerService):
        super().__init__(parent)
        self._customer_service = customer_service
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """设置UI布局"""
        # 搜索区域
        self._create_search_area()
        # 数据列表
        self._create_data_list()
        # 操作按钮
        self._create_action_buttons()

    def _bind_events(self):
        """绑定事件处理"""
        pass

    def cleanup(self):
        """清理资源"""
        pass
```

### 统一样式
```python
# 使用项目主题常量
THEME = {
    'bg_primary': '#FFFFFF',
    'text_primary': '#212529',
    'accent': '#007BFF',
    'success': '#28A745',
    'warning': '#FFC107',
    'danger': '#DC3545'
}

# 统一字体
FONTS = {
    'default': ('Microsoft YaHei UI', 9),
    'heading': ('Microsoft YaHei UI', 12, 'bold'),
    'small': ('Microsoft YaHei UI', 8)
}
```

## 数据库操作标准

### DAO模式
```python
class CustomerDAO:
    """客户数据访问对象 - 标准DAO模式"""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def insert(self, customer_data: Dict[str, Any]) -> int:
        """插入客户数据"""
        sql = """
        INSERT INTO customers (name, phone, customer_type_id, created_at)
        VALUES (?, ?, ?, ?)
        """
        return self._db.execute_insert(sql, (
            customer_data['name'],
            customer_data['phone'],
            customer_data.get('customer_type_id'),
            datetime.now()
        ))
```

### 数据验证
```python
def _validate_customer_data(self, data: Dict[str, Any]) -> None:
    """验证客户数据 - 标准验证模式"""
    if not data.get('name'):
        raise ValidationError("客户名称不能为空")

    if not data.get('phone'):
        raise ValidationError("客户电话不能为空")

    # 电话格式验证
    if not re.match(r'^1[3-9]\d{9}$', data['phone']):
        raise ValidationError("电话格式不正确")
```

## 测试标准

### 单元测试模式
```python
class TestCustomerService(unittest.TestCase):
    """客户服务测试 - 标准测试模式"""

    def setUp(self):
        """测试准备"""
        self.db_manager = MockDatabaseManager()
        self.customer_service = CustomerService(self.db_manager)

    def test_create_customer_success(self):
        """测试创建客户成功"""
        customer_data = {
            'name': '测试公司',
            'phone': '13812345678'
        }

        customer_id = self.customer_service.create_customer(customer_data)

        self.assertIsInstance(customer_id, int)
        self.assertGreater(customer_id, 0)

    def test_create_customer_validation_error(self):
        """测试创建客户验证错误"""
        customer_data = {'name': ''}  # 缺少必填字段

        with self.assertRaises(ValidationError):
            self.customer_service.create_customer(customer_data)
```

## 文件大小控制标准

### 基于实际开发需求的分层文件大小限制

**设计理念**: 基于文件类型和复杂度的合理限制，避免过度拆分，保持代码的内聚性和可读性。

```python
# UI组件文件 (复杂界面逻辑 - 布局、事件、样式、数据绑定)
UI_COMPONENT_LIMITS = {
    'recommended': 400,         # 推荐范围 - 适合大多数UI组件
    'warning_threshold': 600,   # 警告阈值 - 建议考虑拆分
    'max_lines': 800           # 强制限制 - 必须拆分
}

# 业务逻辑文件 (services层 - 完整业务概念，保持单一职责)
BUSINESS_LOGIC_LIMITS = {
    'recommended': 300,         # 推荐范围
    'warning_threshold': 450,   # 警告阈值
    'max_lines': 600           # 强制限制
}

# 数据访问文件 (DAO层 - CRUD操作和查询逻辑)
DATA_ACCESS_LIMITS = {
    'recommended': 250,         # 推荐范围
    'warning_threshold': 350,   # 警告阈值
    'max_lines': 500           # 强制限制
}

# 模型文件 (数据结构定义和验证逻辑)
MODEL_LIMITS = {
    'recommended': 200,         # 推荐范围
    'warning_threshold': 300,   # 警告阈值
    'max_lines': 400           # 强制限制
}

# 核心工具文件 (工具函数集合)
CORE_UTILITY_LIMITS = {
    'recommended': 300,         # 推荐范围
    'warning_threshold': 400,   # 警告阈值
    'max_lines': 500           # 强制限制
}

# 配置文件 (主要是数据配置和设置)
CONFIG_LIMITS = {
    'recommended': 400,         # 推荐范围
    'warning_threshold': 600,   # 警告阈值
    'max_lines': 800           # 强制限制
}

# transfunctions文件 (可复用函数库)
TRANSFUNCTIONS_LIMITS = {
    'recommended': 300,         # 推荐范围
    'warning_threshold': 400,   # 警告阈值
    'max_lines': 500           # 强制限制
}

# 测试文件 (需要覆盖多种测试场景)
TEST_LIMITS = {
    'recommended': 500,         # 推荐范围
    'warning_threshold': 750,   # 警告阈值
    'max_lines': 1000          # 强制限制
}
```

### 文件大小判断逻辑
```python
def get_file_size_limits(file_path: str) -> Dict[str, int]:
    """根据文件路径确定适用的大小限制"""
    if "ui/" in file_path:
        return UI_COMPONENT_LIMITS
    elif "services/" in file_path:
        return BUSINESS_LOGIC_LIMITS
    elif "data/" in file_path:
        return DATA_ACCESS_LIMITS
    elif "models/" in file_path:
        return MODEL_LIMITS
    elif "core/" in file_path:
        return CORE_UTILITY_LIMITS
    elif "config/" in file_path:
        return CONFIG_LIMITS
    elif "transfunctions/" in file_path:
        return TRANSFUNCTIONS_LIMITS
    elif "test" in file_path:
        return TEST_LIMITS
    else:
        return CORE_UTILITY_LIMITS  # 默认标准
```

### 质量检查优先级
```python
QUALITY_PRIORITIES = [
    1,  # 功能正确性 (最高)
    2,  # 类型安全 (MyPy)
    3,  # 代码规范 (Ruff)
    4,  # 架构设计
    5,  # 可读性维护性
    6,  # 文件大小 (最低)
]
```

## 性能优化标准

### 数据库优化
```python
# 使用索引优化查询
CREATE INDEX idx_customers_name_phone ON customers(name, phone);

# 使用缓存减少重复查询
@lru_cache(maxsize=100)
def get_customer_statistics(self, customer_id: int):
    """获取客户统计信息 - 带缓存"""
    pass
```

### UI性能优化
```python
# 大数据集使用分页
def load_customers(self, page: int = 1, page_size: int = 50):
    """分页加载客户数据"""
    pass

# 图表异步渲染
def render_chart_async(self, data):
    """异步渲染图表避免UI阻塞"""
    threading.Thread(target=self._render_chart, args=(data,)).start()
```

## 文档标准

### 函数文档
```python
def calculate_customer_value(
    self,
    customer_id: int,
    time_period: int = 12
) -> Tuple[float, Dict[str, float]]:
    """计算客户价值评分

    基于客户的交易历史、互动频率和合作时长等因素，
    计算客户的综合价值评分。适用于板材行业的客户评估。

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
        >>> service = CustomerService(db_manager)
        >>> score, details = service.calculate_customer_value(123)
        >>> print(f"客户价值评分: {score}")
    """
```

## 深度思考工作流程

### Sequential Thinking要求

在处理MiniCRM项目的重要任务时，必须使用sequential thinking进行深度思考：

#### 需要深度思考的情况
- **架构设计决策** - 选择技术方案、设计系统架构
- **复杂功能实现** - 报价比对算法、数据分析功能
- **问题解决** - 遇到技术难题或业务逻辑复杂性
- **方案选择** - 多个实现方案的对比和选择
- **风险评估** - 项目风险识别和应对策略
- **用户体验设计** - 界面交互和用户流程优化

#### 思考深度要求
1. **多角度分析** - 至少从技术、业务、用户3个角度考虑
2. **方案对比** - 考虑至少2-3种不同的实现方案
3. **风险识别** - 识别潜在问题和应对措施
4. **长远考虑** - 考虑方案的可扩展性和维护性
5. **成本效益** - 评估实现成本和预期收益

#### 思考输出标准
- 展示完整的思考过程
- 提供清晰的决策依据
- 包含风险评估和应对策略
- 给出具体的实施建议

### 工作流程集成
```python
# 在重要决策前使用sequential thinking
def make_important_decision(problem):
    # 1. 使用sequential thinking深度分析
    analysis = sequential_thinking_analysis(problem)

    # 2. 基于分析结果做决策
    decision = make_decision_based_on_analysis(analysis)

    # 3. 记录决策过程和依据
    document_decision_process(analysis, decision)

    return decision
```

这个MiniCRM专用的steering配置比通用配置更加具体和实用，包含了：
- 项目特定的技术栈要求
- 板材行业的业务逻辑标准
- 统一的代码架构和命名规范
- 具体的UI开发和数据库操作模式
- 性能优化和测试标准
- **深度思考工作流程要求**
