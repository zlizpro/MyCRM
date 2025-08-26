# 文件清理系统设计文档

## 概述

文件清理系统是一个智能化的项目维护工具，旨在帮助开发者安全、高效地清理MiniCRM项目中的无用和过期文件。系统采用模块化设计，包含文件扫描、依赖分析、安全清理、备份恢复等核心功能，并提供直观的用户界面和灵活的配置选项。

系统设计遵循MiniCRM项目的分层架构标准，采用服务层处理业务逻辑，数据层管理文件操作，UI层提供用户交互界面。整个系统具有高度的可扩展性和可维护性。

## 架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    文件清理系统架构                          │
├─────────────────────────────────────────────────────────────┤
│  UI层 (用户界面)                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  主界面组件      │  │  进度显示组件    │  │  配置界面组件    ││
│  │  FileCleanupUI  │  │  ProgressWidget │  │  SettingsUI     ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  服务层 (业务逻辑)                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  文件扫描服务    │  │  清理执行服务    │  │  备份管理服务    ││
│  │  ScanService    │  │  CleanupService │  │  BackupService  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  依赖分析服务    │  │  报告生成服务    │  │  配置管理服务    ││
│  │  DependencyServ │  │  ReportService  │  │  ConfigService  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  数据层 (数据访问)                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  文件操作管理    │  │  备份数据管理    │  │  配置数据管理    ││
│  │  FileManager    │  │  BackupManager  │  │  ConfigManager  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
├─────────────────────────────────────────────────────────────┤
│  核心层 (工具和常量)                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  文件分类器      │  │  路径工具        │  │  日志管理器      ││
│  │  FileClassifier │  │  PathUtils      │  │  LogManager     ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 数据流架构

```
用户操作 → UI层 → 服务层 → 数据层 → 文件系统
    ↑                                    ↓
    └── 结果反馈 ← 业务处理 ← 数据操作 ←────┘
```

## 组件和接口

### 1. 文件扫描服务 (ScanService)

**职责：** 扫描项目目录，识别和分类文件

**接口定义：**
```python
class ScanService:
    def scan_project(self, project_path: str, config: ScanConfig) -> ScanResult
    def classify_file(self, file_path: str) -> FileCategory
    def get_scan_progress(self) -> ScanProgress
    def cancel_scan(self) -> bool
```

**核心方法：**
- `scan_project()`: 执行完整的项目扫描
- `classify_file()`: 对单个文件进行分类
- `get_scan_progress()`: 获取扫描进度信息
- `cancel_scan()`: 取消正在进行的扫描

### 2. 依赖分析服务 (DependencyAnalysisService)

**职责：** 分析文件之间的依赖关系

**接口定义：**
```python
class DependencyAnalysisService:
    def analyze_dependencies(self, file_list: List[str]) -> DependencyGraph
    def check_file_usage(self, file_path: str) -> List[str]
    def build_dependency_graph(self, scan_result: ScanResult) -> DependencyGraph
    def is_file_safe_to_delete(self, file_path: str) -> bool
```

**核心方法：**
- `analyze_dependencies()`: 分析文件依赖关系
- `check_file_usage()`: 检查文件是否被其他文件使用
- `build_dependency_graph()`: 构建依赖关系图
- `is_file_safe_to_delete()`: 判断文件是否可以安全删除

### 3. 清理执行服务 (CleanupService)

**职责：** 执行文件清理操作

**接口定义：**
```python
class CleanupService:
    def execute_cleanup(self, cleanup_plan: CleanupPlan) -> CleanupResult
    def preview_cleanup(self, file_list: List[str]) -> CleanupPreview
    def validate_cleanup_plan(self, plan: CleanupPlan) -> ValidationResult
    def get_cleanup_progress(self) -> CleanupProgress
```

**核心方法：**
- `execute_cleanup()`: 执行清理计划
- `preview_cleanup()`: 预览清理效果
- `validate_cleanup_plan()`: 验证清理计划的安全性
- `get_cleanup_progress()`: 获取清理进度

### 4. 备份管理服务 (BackupService)

**职责：** 管理文件备份和恢复

**接口定义：**
```python
class BackupService:
    def create_backup(self, file_path: str) -> str
    def restore_file(self, backup_id: str, target_path: str) -> bool
    def list_backups(self) -> List[BackupInfo]
    def cleanup_old_backups(self, retention_days: int) -> int
```

**核心方法：**
- `create_backup()`: 创建文件备份
- `restore_file()`: 从备份恢复文件
- `list_backups()`: 列出所有备份
- `cleanup_old_backups()`: 清理过期备份

### 5. 报告生成服务 (ReportService)

**职责：** 生成清理报告和统计信息

**接口定义：**
```python
class ReportService:
    def generate_cleanup_report(self, cleanup_result: CleanupResult) -> CleanupReport
    def generate_scan_report(self, scan_result: ScanResult) -> ScanReport
    def export_report(self, report: Report, format: str, output_path: str) -> bool
    def get_historical_reports(self, limit: int = 10) -> List[Report]
```

**核心方法：**
- `generate_cleanup_report()`: 生成清理报告
- `generate_scan_report()`: 生成扫描报告
- `export_report()`: 导出报告到文件
- `get_historical_reports()`: 获取历史报告

## 数据模型

### 1. 文件信息模型

```python
@dataclass
class FileInfo:
    """文件信息数据模型"""
    path: str                    # 文件路径
    size: int                    # 文件大小（字节）
    category: FileCategory       # 文件分类
    last_modified: datetime      # 最后修改时间
    last_accessed: datetime      # 最后访问时间
    is_safe_to_delete: bool     # 是否可以安全删除
    dependencies: List[str]      # 依赖此文件的其他文件
    risk_level: RiskLevel       # 删除风险等级

    def get_size_mb(self) -> float:
        """获取文件大小（MB）"""
        return self.size / (1024 * 1024)

    def is_recently_accessed(self, days: int = 30) -> bool:
        """检查是否在指定天数内被访问过"""
        return (datetime.now() - self.last_accessed).days <= days
```

### 2. 扫描结果模型

```python
@dataclass
class ScanResult:
    """扫描结果数据模型"""
    project_path: str                           # 项目路径
    scan_time: datetime                         # 扫描时间
    total_files: int                           # 总文件数
    total_size: int                            # 总大小
    files_by_category: Dict[FileCategory, List[FileInfo]]  # 按分类的文件
    dependency_graph: DependencyGraph          # 依赖关系图
    scan_duration: timedelta                   # 扫描耗时

    def get_category_stats(self) -> Dict[FileCategory, CategoryStats]:
        """获取各分类的统计信息"""
        stats = {}
        for category, files in self.files_by_category.items():
            stats[category] = CategoryStats(
                count=len(files),
                total_size=sum(f.size for f in files),
                safe_to_delete_count=sum(1 for f in files if f.is_safe_to_delete)
            )
        return stats
```

### 3. 清理计划模型

```python
@dataclass
class CleanupPlan:
    """清理计划数据模型"""
    files_to_delete: List[FileInfo]            # 要删除的文件列表
    backup_enabled: bool                       # 是否启用备份
    confirmation_level: ConfirmationLevel      # 确认级别
    dry_run: bool                             # 是否为试运行
    created_time: datetime                     # 创建时间

    def get_total_size_to_free(self) -> int:
        """计算将要释放的总空间"""
        return sum(f.size for f in self.files_to_delete)

    def get_files_by_risk_level(self) -> Dict[RiskLevel, List[FileInfo]]:
        """按风险等级分组文件"""
        result = {}
        for file_info in self.files_to_delete:
            if file_info.risk_level not in result:
                result[file_info.risk_level] = []
            result[file_info.risk_level].append(file_info)
        return result
```

### 4. 备份信息模型

```python
@dataclass
class BackupInfo:
    """备份信息数据模型"""
    backup_id: str                             # 备份ID
    original_path: str                         # 原始文件路径
    backup_path: str                           # 备份文件路径
    backup_time: datetime                      # 备份时间
    file_size: int                            # 文件大小
    checksum: str                             # 文件校验和

    def is_expired(self, retention_days: int) -> bool:
        """检查备份是否已过期"""
        return (datetime.now() - self.backup_time).days > retention_days
```

## 错误处理

### 异常层次结构

```python
class FileCleanupError(Exception):
    """文件清理系统基础异常"""
    pass

class ScanError(FileCleanupError):
    """扫描过程异常"""
    pass

class CleanupError(FileCleanupError):
    """清理过程异常"""
    pass

class BackupError(FileCleanupError):
    """备份过程异常"""
    pass

class DependencyAnalysisError(FileCleanupError):
    """依赖分析异常"""
    pass

class ConfigurationError(FileCleanupError):
    """配置错误异常"""
    pass
```

### 错误处理策略

1. **扫描错误处理**
   - 权限不足：跳过文件并记录警告
   - 文件不存在：从扫描结果中移除
   - 路径过长：记录错误并继续

2. **清理错误处理**
   - 文件被占用：跳过并记录警告
   - 权限不足：提示用户并停止操作
   - 磁盘空间不足：停止操作并回滚

3. **备份错误处理**
   - 备份目录不存在：自动创建
   - 磁盘空间不足：清理旧备份后重试
   - 备份失败：停止清理操作

## 测试策略

### 单元测试

1. **文件分类测试**
   - 测试各种文件类型的正确分类
   - 测试边界情况和特殊文件名
   - 测试自定义规则的应用

2. **依赖分析测试**
   - 测试Python import语句解析
   - 测试配置文件引用检测
   - 测试循环依赖处理

3. **清理操作测试**
   - 测试文件删除操作
   - 测试备份创建和恢复
   - 测试错误情况处理

### 集成测试

1. **端到端测试**
   - 完整的扫描-清理-恢复流程
   - 多种文件类型的混合测试
   - 大型项目的性能测试

2. **用户界面测试**
   - 界面响应性测试
   - 进度显示准确性测试
   - 用户交互流程测试

### 性能测试

1. **扫描性能测试**
   - 大量文件的扫描速度
   - 内存使用情况监控
   - 并发扫描能力测试

2. **清理性能测试**
   - 批量删除操作性能
   - 备份创建速度测试
   - 磁盘I/O优化效果

## 安全考虑

### 数据安全

1. **备份完整性**
   - 使用校验和验证备份文件完整性
   - 定期检查备份文件的可用性
   - 提供备份文件的加密选项

2. **操作审计**
   - 记录所有文件操作的详细日志
   - 保存操作前后的文件状态
   - 提供操作历史查询功能

### 权限管理

1. **文件权限检查**
   - 操作前检查文件读写权限
   - 处理权限不足的情况
   - 提供权限提升建议

2. **安全确认**
   - 多级确认机制防止误操作
   - 重要文件的特别确认
   - 提供操作撤销功能

## 配置管理

### 配置文件结构

```yaml
# file_cleanup_config.yaml
scan:
  exclude_directories:
    - .git
    - .venv
    - node_modules
  include_hidden_files: false
  max_scan_depth: 10

classification:
  cache_patterns:
    - "__pycache__/**"
    - "*.pyc"
    - ".mypy_cache/**"
  build_patterns:
    - "build/**"
    - "dist/**"
    - "htmlcov/**"
  test_data_patterns:
    - "test_*.xlsx"
    - "test_*.pdf"
    - "test_*.db"

cleanup:
  backup_enabled: true
  backup_retention_days: 30
  confirmation_level: "medium"
  dry_run_by_default: true

backup:
  backup_directory: ".file_cleanup_backups"
  compress_backups: true
  max_backup_size_mb: 1000

reporting:
  save_reports: true
  report_directory: "cleanup_reports"
  report_format: "json"
```

### 配置验证

```python
class ConfigValidator:
    """配置验证器"""

    def validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """验证配置文件的有效性"""
        errors = []
        warnings = []

        # 验证路径配置
        if not self._validate_paths(config):
            errors.append("Invalid path configuration")

        # 验证模式配置
        if not self._validate_patterns(config):
            warnings.append("Some patterns may not work correctly")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

## 部署和维护

### 部署要求

1. **系统要求**
   - Python 3.8+
   - 足够的磁盘空间用于备份
   - 文件系统读写权限

2. **依赖管理**
   - 使用requirements.txt管理Python依赖
   - 提供独立的虚拟环境
   - 支持离线安装

### 维护策略

1. **日志管理**
   - 按日期轮转日志文件
   - 设置日志级别和输出格式
   - 提供日志分析工具

2. **性能监控**
   - 监控扫描和清理操作的性能
   - 记录内存和磁盘使用情况
   - 提供性能优化建议

3. **定期维护**
   - 自动清理过期备份
   - 定期检查配置文件有效性
   - 更新文件分类规则
