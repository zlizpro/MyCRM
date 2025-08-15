"""
MiniCRM 数据库模块

重构后的数据库管理模块，按照单一职责原则拆分：
- DatabaseManager: 核心连接和CRUD操作
- DatabaseSchema: 表结构和索引定义
- DatabaseInitializer: 初始数据插入

重构说明：
- 原始文件: 736行 -> 现在3个文件，每个约200-250行
- 符合数据访问层文件大小标准(推荐250行，最大500行)
- 职责清晰分离，便于维护和测试
"""

from .database_initializer import DatabaseInitializer
from .database_manager import DatabaseManager
from .database_schema import DatabaseSchema


__all__ = ["DatabaseManager", "DatabaseSchema", "DatabaseInitializer"]
