"""MiniCRM 数据库操作Hooks系统.

提供数据库操作前后的拦截和处理机制.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from minicrm.core.exceptions import DatabaseError, ValidationError


class DatabaseHooks:
    """数据库操作Hooks系统.

    提供数据库操作前后的拦截和处理机制.
    """

    def __init__(self) -> None:
        """初始化Hooks系统."""
        self._before_hooks: dict[str, list[Callable]] = {}
        self._after_hooks: dict[str, list[Callable]] = {}
        self._logger = logging.getLogger(__name__)

    def register_before_hook(self, operation: str, hook_func: Callable) -> None:
        """注册操作前Hook.

        Args:
            operation: 操作类型 (insert, update, delete)
            hook_func: Hook函数
        """
        if operation not in self._before_hooks:
            self._before_hooks[operation] = []
        self._before_hooks[operation].append(hook_func)
        self._logger.debug("注册before hook: %s", operation)

    def register_after_hook(self, operation: str, hook_func: Callable) -> None:
        """注册操作后Hook.

        Args:
            operation: 操作类型 (insert, update, delete)
            hook_func: Hook函数
        """
        if operation not in self._after_hooks:
            self._after_hooks[operation] = []
        self._after_hooks[operation].append(hook_func)
        self._logger.debug("注册after hook: %s", operation)

    def execute_before_hooks(self, operation: str, **kwargs: object) -> dict[str, Any]:
        """执行操作前Hooks.

        Args:
            operation: 操作类型
            **kwargs: Hook参数

        Returns:
            dict[str, Any]: 处理后的参数
        """
        result = kwargs.copy()

        hooks = self._before_hooks.get(operation, [])
        for hook_func in hooks:
            hook_result = self._safe_execute_before_hook(hook_func, **result)
            if hook_result is not None:
                result.update(hook_result)

        return result

    def execute_after_hooks(self, operation: str, **kwargs: object) -> None:
        """执行操作后Hooks.

        Args:
            operation: 操作类型
            **kwargs: Hook参数
        """
        hooks = self._after_hooks.get(operation, [])
        for hook_func in hooks:
            self._safe_execute_after_hook(hook_func, **kwargs)

    def _safe_execute_before_hook(
        self, hook_func: Callable, **kwargs: object
    ) -> dict[str, Any] | None:
        """安全执行Before Hook函数.

        Args:
            hook_func: Hook函数
            **kwargs: Hook参数

        Returns:
            dict[str, Any] | None: Hook处理结果
        """
        try:
            return hook_func(**kwargs)
        except (ValidationError, DatabaseError):
            self._logger.exception("Before hook执行失败")
            raise

    def _safe_execute_after_hook(self, hook_func: Callable, **kwargs: object) -> None:
        """安全执行After Hook函数.

        Args:
            hook_func: Hook函数
            **kwargs: Hook参数
        """
        try:
            hook_func(**kwargs)
        except (ValidationError, DatabaseError, OSError):
            self._logger.exception("After hook执行失败")
            # After hooks失败不应该影响主操作
