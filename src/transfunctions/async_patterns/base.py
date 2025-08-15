"""
Transfunctions - 异步模式基础类

提供统一的同步/异步操作基础设施。
"""

import asyncio
import functools
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor


class AsyncPatternMixin:
    """异步模式混入类

    提供统一的同步/异步操作接口，灵感来自transfunctions库。
    """

    def __init__(self):
        self._executor = ThreadPoolExecutor(max_workers=4)

    def sync_or_async(self, sync_func: Callable, async_func: Callable | None = None):
        """创建可以同步或异步调用的函数装饰器

        Args:
            sync_func: 同步函数
            async_func: 异步函数（可选）

        Returns:
            统一的函数接口
        """
        if async_func is None:
            # 如果没有提供异步函数，将同步函数包装为异步
            async_func = self._wrap_sync_to_async(sync_func)

        @functools.wraps(sync_func)
        def wrapper(*args, **kwargs):
            # 检查是否在异步上下文中
            try:
                asyncio.get_running_loop()
                # 在异步上下文中，返回协程
                return async_func(*args, **kwargs)
            except RuntimeError:
                # 在同步上下文中，直接调用同步函数
                return sync_func(*args, **kwargs)

        # 添加显式的同步和异步方法
        wrapper.sync = sync_func
        wrapper.async_call = async_func

        return wrapper

    def _wrap_sync_to_async(self, sync_func: Callable) -> Callable:
        """将同步函数包装为异步函数"""

        async def async_wrapper(*args, **kwargs):
            current_loop = asyncio.get_running_loop()
            return await current_loop.run_in_executor(
                self._executor, lambda: sync_func(*args, **kwargs)
            )

        return async_wrapper
