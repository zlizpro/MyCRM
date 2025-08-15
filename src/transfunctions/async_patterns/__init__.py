"""
Transfunctions - 异步模式支持

受pomponchik/transfunctions启发，为MiniCRM提供同步/异步统一的函数模板。
虽然我们不直接使用transfunctions库，但我们采用其设计理念来创建
可以同时支持同步和异步操作的统一接口。

主要功能：
- 数据库操作统一接口
- API调用统一接口
- 文件操作统一接口
- 缓存操作统一接口
"""

# 导入基础类
# 导入具体实现类
from .api import UnifiedAPIClient, create_unified_api_client
from .base import AsyncPatternMixin
from .cache import UnifiedCacheOperations, create_unified_cache
from .database import UnifiedDatabaseOperations, create_unified_database
from .decorators import unified_operation
from .files import UnifiedFileOperations, create_unified_file_ops

# 公开API
__all__ = [
    # 基础类
    "AsyncPatternMixin",
    # 具体实现类
    "UnifiedDatabaseOperations",
    "UnifiedAPIClient",
    "UnifiedFileOperations",
    "UnifiedCacheOperations",
    # 工厂函数
    "create_unified_database",
    "create_unified_api_client",
    "create_unified_file_ops",
    "create_unified_cache",
    # 装饰器
    "unified_operation",
]
