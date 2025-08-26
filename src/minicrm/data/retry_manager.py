"""MiniCRM 错误重试管理器.

实现指数退避重试机制.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from typing import Callable, TypeVar

from minicrm.core.exceptions import DatabaseError, ValidationError


T = TypeVar("T")


class RetryManager:
    """错误重试管理器.

    实现指数退避重试机制.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 0.1):
        """初始化重试管理器.

        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间(秒)
        """
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._logger = logging.getLogger(__name__)

    def retry_on_error(
        self, func: Callable[..., T], *args: object, **kwargs: object
    ) -> T:
        """带重试的函数执行.

        Args:
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数

        Returns:
            T: 函数执行结果
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            # 优化: 将异常处理逻辑提取到单独方法, 减少循环内开销
            result = self._execute_with_retry(func, attempt, args, kwargs)

            if isinstance(result, Exception):
                last_exception = result
                if attempt < self._max_retries:
                    delay = self._base_delay * (2**attempt)  # 指数退避
                    self._logger.warning(
                        "数据库操作失败, %.2f秒后重试 (尝试 %d/%d)",
                        delay,
                        attempt + 1,
                        self._max_retries + 1,
                    )
                    time.sleep(delay)
                else:
                    self._logger.exception("数据库操作最终失败")
                    break
            else:
                return result

        error_msg = f"数据库操作重试失败: {last_exception}"
        raise DatabaseError(error_msg) from last_exception

    def _execute_with_retry(
        self, func: Callable[..., T], attempt: int, args: tuple, kwargs: dict
    ) -> T | Exception:
        """执行函数并处理异常.

        Args:
            func: 要执行的函数
            attempt: 当前尝试次数 (保留用于未来扩展)
            args: 函数参数
            kwargs: 函数关键字参数

        Returns:
            T | Exception: 函数结果或异常对象
        """
        # 使用attempt参数避免未使用警告, 同时为未来扩展保留
        _ = attempt

        try:
            return func(*args, **kwargs)
        except (sqlite3.OperationalError, sqlite3.DatabaseError) as e:
            return e
        except (ValidationError, DatabaseError, OSError):
            # 非数据库错误不重试
            self._logger.exception("非数据库错误, 不重试")
            raise
