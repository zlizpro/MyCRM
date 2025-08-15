"""
Transfunctions - 异步模式支持 (向后兼容模块)

⚠️ 注意：此文件已重构为模块化结构，当前文件仅用于向后兼容。
新代码请使用 async_patterns 包中的具体模块。

受pomponchik/transfunctions启发，为MiniCRM提供同步/异步统一的函数模板。
虽然我们不直接使用transfunctions库，但我们采用其设计理念来创建
可以同时支持同步和异步操作的统一接口。

主要功能：
- 数据库操作统一接口
- API调用统一接口
- 文件操作统一接口
- 缓存操作统一接口

新的模块化结构：
- async_patterns.base - 基础类
- async_patterns.database - 数据库操作
- async_patterns.api - API客户端
- async_patterns.files - 文件操作
- async_patterns.cache - 缓存操作
- async_patterns.decorators - 装饰器
"""

# 为了向后兼容，从新的模块化结构中导入所有类
from .async_patterns import (
    AsyncPatternMixin,
    UnifiedAPIClient,
    UnifiedCacheOperations,
    UnifiedDatabaseOperations,
    UnifiedFileOperations,
    create_unified_api_client,
    create_unified_cache,
    create_unified_database,
    create_unified_file_ops,
    unified_operation,
)

# 保持原有的公开API
__all__ = [
    "AsyncPatternMixin",
    "UnifiedDatabaseOperations",
    "UnifiedAPIClient",
    "UnifiedFileOperations",
    "UnifiedCacheOperations",
    "create_unified_database",
    "create_unified_api_client",
    "create_unified_file_ops",
    "create_unified_cache",
    "unified_operation",
]
