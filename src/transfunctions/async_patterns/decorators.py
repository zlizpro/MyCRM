"""
Transfunctions - 异步装饰器

提供装饰器版本的异步模式支持。
"""

from collections.abc import Callable

from .base import AsyncPatternMixin


def unified_operation(async_func: Callable | None = None):
    """装饰器：将函数转换为统一的同步/异步操作

    Args:
        async_func: 可选的异步版本函数

    Example:
        @unified_operation
        def process_data(data):
            # 同步处理逻辑
            return processed_data

        # 或者提供异步版本
        async def async_process_data(data):
            # 异步处理逻辑
            return processed_data

        @unified_operation(async_process_data)
        def process_data(data):
            # 同步处理逻辑
            return processed_data
    """

    def decorator(sync_func: Callable):
        mixin = AsyncPatternMixin()
        return mixin.sync_or_async(sync_func, async_func)

    return decorator
