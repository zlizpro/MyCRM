"""
MiniCRM 数据库管理器 - 兼容性包装器

这个文件作为兼容性包装器，重新导出重构后的数据库模块。

重构说明：
- 原始文件: 736行 -> 重构为3个专门模块
- DatabaseManager: 核心连接和CRUD操作 (287行)
- DatabaseSchema: 表结构和索引定义 (270行)
- DatabaseInitializer: 初始数据插入 (287行)
- 总计: 约844行，但结构更清晰，职责分离

向后兼容：
- 保持原有的DatabaseManager类接口不变
- 现有代码无需修改即可使用重构后的模块
"""

# 重新导出重构后的类，保持向后兼容
from .database.database_initializer import DatabaseInitializer
from .database.database_manager import DatabaseManager
from .database.database_schema import DatabaseSchema


# 导出所有类供外部使用
__all__ = ["DatabaseManager", "DatabaseSchema", "DatabaseInitializer"]
