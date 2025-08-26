"""
MiniCRM Hooks框架

提供灵活的钩子系统,支持在应用程序的各个生命周期阶段插入自定义逻辑.
包括:
- 应用程序生命周期钩子
- 数据库操作钩子
- UI事件钩子
- 业务逻辑钩子
- 性能监控钩子

钩子系统采用观察者模式,允许多个处理器监听同一个事件.
"""

import asyncio
import functools
import inspect
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .logging import get_audit_logger, get_logger, get_performance_logger


logger = get_logger("hooks")
perf_logger = get_performance_logger()
audit_logger = get_audit_logger()


class HookPriority(Enum):
    """
    钩子优先级枚举

    定义钩子执行的优先级顺序.
    """

    HIGHEST = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    LOWEST = 5


class HookExecutionMode(Enum):
    """
    钩子执行模式枚举

    定义钩子的执行方式.
    """

    SYNC = "sync"  # 同步执行
    ASYNC = "async"  # 异步执行
    BACKGROUND = "background"  # 后台执行


@dataclass
class HookInfo:
    """
    钩子信息数据类

    包含钩子的元数据信息.
    """

    name: str
    handler: Callable
    priority: HookPriority = HookPriority.NORMAL
    execution_mode: HookExecutionMode = HookExecutionMode.SYNC
    description: str = ""
    enabled: bool = True
    max_execution_time: float | None = None  # 最大执行时间(秒)
    retry_count: int = 0  # 重试次数
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        """初始化后处理"""
        if not self.description:
            self.description = f"Hook: {self.name}"


class HookResult:
    """
    钩子执行结果

    包含钩子执行的结果和元数据.
    """

    def __init__(
        self,
        success: bool = True,
        result: Any = None,
        error: Exception | None = None,
        duration: float = 0.0,
        hook_name: str = "",
        metadata: dict[str, Any] | None = None,
    ):
        """
        初始化钩子结果

        Args:
            success: 执行是否成功
            result: 执行结果
            error: 错误信息(如果有)
            duration: 执行耗时
            hook_name: 钩子名称
            metadata: 额外的元数据
        """
        self.success = success
        self.result = result
        self.error = error
        self.duration = duration
        self.hook_name = hook_name
        self.metadata = metadata or {}

    def __bool__(self) -> bool:
        """返回执行是否成功"""
        return self.success

    def __str__(self) -> str:
        """返回结果的字符串表示"""
        status = "成功" if self.success else "失败"
        return f"HookResult({self.hook_name}: {status}, 耗时: {self.duration:.3f}秒)"


class HookManager:
    """
    钩子管理器

    负责钩子的注册、管理和执行.
    """

    def __init__(self, max_workers: int = 4):
        """
        初始化钩子管理器

        Args:
            max_workers: 后台执行的最大工作线程数
        """
        self._hooks: dict[str, list[HookInfo]] = {}
        self._global_hooks: list[HookInfo] = []
        self._hook_stats: dict[str, dict[str, Any]] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._enabled = True

    def register(
        self,
        event_name: str,
        handler: Callable,
        priority: HookPriority = HookPriority.NORMAL,
        execution_mode: HookExecutionMode = HookExecutionMode.SYNC,
        **kwargs,
    ) -> HookInfo:
        """
        注册钩子

        Args:
            event_name: 事件名称
            handler: 钩子处理函数
            priority: 优先级
            execution_mode: 执行模式
            **kwargs: 其他钩子配置

        Returns:
            钩子信息对象
        """
        hook_info = HookInfo(
            name=f"{event_name}.{handler.__name__}",
            handler=handler,
            priority=priority,
            execution_mode=execution_mode,
            **kwargs,
        )

        if event_name not in self._hooks:
            self._hooks[event_name] = []

        self._hooks[event_name].append(hook_info)

        # 按优先级排序
        self._hooks[event_name].sort(key=lambda h: h.priority.value)

        # 初始化统计信息
        self._hook_stats[hook_info.name] = {
            "call_count": 0,
            "success_count": 0,
            "error_count": 0,
            "total_duration": 0.0,
            "avg_duration": 0.0,
            "last_execution": None,
        }

        logger.info(f"钩子已注册: {hook_info.name} -> {event_name}")
        return hook_info

    def unregister(self, event_name: str, handler: Callable) -> bool:
        """
        注销钩子

        Args:
            event_name: 事件名称
            handler: 钩子处理函数

        Returns:
            是否成功注销
        """
        if event_name not in self._hooks:
            return False

        hook_name = f"{event_name}.{handler.__name__}"

        # 查找并移除钩子
        for i, hook_info in enumerate(self._hooks[event_name]):
            if hook_info.handler == handler:
                del self._hooks[event_name][i]

                # 清理统计信息
                if hook_name in self._hook_stats:
                    del self._hook_stats[hook_name]

                logger.info(f"钩子已注销: {hook_name}")
                return True

        return False

    def trigger(self, event_name: str, *args, **kwargs) -> list[HookResult]:
        """
        触发钩子

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            钩子执行结果列表
        """
        if not self._enabled:
            return []

        if event_name not in self._hooks:
            return []

        results = []
        hooks = self._hooks[event_name]

        logger.debug(f"触发钩子事件: {event_name}, 钩子数量: {len(hooks)}")

        for hook_info in hooks:
            if not hook_info.enabled:
                continue

            result = self._execute_hook(hook_info, *args, **kwargs)
            results.append(result)

            # 更新统计信息
            self._update_hook_stats(hook_info.name, result)

        return results

    def trigger_async(self, event_name: str, *args, **kwargs) -> list[HookResult]:
        """
        异步触发钩子

        Args:
            event_name: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            钩子执行结果列表
        """
        if not self._enabled:
            return []

        if event_name not in self._hooks:
            return []

        results = []
        hooks = self._hooks[event_name]

        # 分离同步和异步钩子
        sync_hooks = [h for h in hooks if h.execution_mode == HookExecutionMode.SYNC]
        async_hooks = [h for h in hooks if h.execution_mode != HookExecutionMode.SYNC]

        # 执行同步钩子
        for hook_info in sync_hooks:
            if hook_info.enabled:
                result = self._execute_hook(hook_info, *args, **kwargs)
                results.append(result)
                self._update_hook_stats(hook_info.name, result)

        # 提交异步钩子到线程池
        futures = []
        for hook_info in async_hooks:
            if hook_info.enabled:
                future = self._executor.submit(
                    self._execute_hook, hook_info, *args, **kwargs
                )
                futures.append((hook_info, future))

        # 收集异步结果
        for hook_info, future in futures:
            try:
                result = future.result(timeout=hook_info.max_execution_time)
                results.append(result)
                self._update_hook_stats(hook_info.name, result)
            except Exception as e:
                error_result = HookResult(
                    success=False, error=e, hook_name=hook_info.name
                )
                results.append(error_result)
                self._update_hook_stats(hook_info.name, error_result)

        return results

    def _execute_hook(self, hook_info: HookInfo, *args, **kwargs) -> HookResult:
        """
        执行单个钩子

        Args:
            hook_info: 钩子信息
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            钩子执行结果
        """
        start_time = time.time()

        try:
            # 记录钩子开始执行
            perf_logger.start_operation(
                hook_info.name, f"Hook: {hook_info.name}", event_type="hook_execution"
            )

            # 执行钩子处理函数
            if inspect.iscoroutinefunction(hook_info.handler):
                # 异步函数
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(hook_info.handler(*args, **kwargs))
                finally:
                    loop.close()
            else:
                # 同步函数
                result = hook_info.handler(*args, **kwargs)

            duration = time.time() - start_time

            # 记录钩子执行完成
            perf_logger.end_operation(
                hook_info.name,
                f"Hook: {hook_info.name}",
                success=True,
                event_type="hook_execution",
            )

            # 检查执行时间
            if hook_info.max_execution_time and duration > hook_info.max_execution_time:
                logger.warning(
                    f"钩子执行超时: {hook_info.name}, 耗时: {duration:.3f}秒"
                )

            return HookResult(
                success=True, result=result, duration=duration, hook_name=hook_info.name
            )

        except Exception as e:
            duration = time.time() - start_time

            # 记录钩子执行失败
            perf_logger.end_operation(
                hook_info.name,
                f"Hook: {hook_info.name}",
                success=False,
                event_type="hook_execution",
                error=str(e),
            )

            logger.error(f"钩子执行失败: {hook_info.name}, 错误: {e}")

            return HookResult(
                success=False, error=e, duration=duration, hook_name=hook_info.name
            )

    def _update_hook_stats(self, hook_name: str, result: HookResult) -> None:
        """
        更新钩子统计信息

        Args:
            hook_name: 钩子名称
            result: 执行结果
        """
        if hook_name not in self._hook_stats:
            return

        stats = self._hook_stats[hook_name]
        stats["call_count"] += 1
        stats["total_duration"] += result.duration
        stats["avg_duration"] = stats["total_duration"] / stats["call_count"]
        stats["last_execution"] = time.time()

        if result.success:
            stats["success_count"] += 1
        else:
            stats["error_count"] += 1

    def get_hooks(self, event_name: str | None = None) -> dict[str, list[HookInfo]]:
        """
        获取钩子信息

        Args:
            event_name: 事件名称,如果为None则返回所有钩子

        Returns:
            钩子信息字典
        """
        if event_name:
            return {event_name: self._hooks.get(event_name, [])}
        return self._hooks.copy()

    def get_hook_stats(self, hook_name: str | None = None) -> dict[str, Any]:
        """
        获取钩子统计信息

        Args:
            hook_name: 钩子名称,如果为None则返回所有统计信息

        Returns:
            统计信息字典
        """
        if hook_name:
            return self._hook_stats.get(hook_name, {})
        return self._hook_stats.copy()

    def enable_hook(self, event_name: str, handler: Callable) -> bool:
        """
        启用钩子

        Args:
            event_name: 事件名称
            handler: 钩子处理函数

        Returns:
            是否成功启用
        """
        if event_name not in self._hooks:
            return False

        for hook_info in self._hooks[event_name]:
            if hook_info.handler == handler:
                hook_info.enabled = True
                logger.info(f"钩子已启用: {hook_info.name}")
                return True

        return False

    def disable_hook(self, event_name: str, handler: Callable) -> bool:
        """
        禁用钩子

        Args:
            event_name: 事件名称
            handler: 钩子处理函数

        Returns:
            是否成功禁用
        """
        if event_name not in self._hooks:
            return False

        for hook_info in self._hooks[event_name]:
            if hook_info.handler == handler:
                hook_info.enabled = False
                logger.info(f"钩子已禁用: {hook_info.name}")
                return True

        return False

    def enable_all(self) -> None:
        """启用钩子系统"""
        self._enabled = True
        logger.info("钩子系统已启用")

    def disable_all(self) -> None:
        """禁用钩子系统"""
        self._enabled = False
        logger.info("钩子系统已禁用")

    def clear_hooks(self, event_name: str | None = None) -> None:
        """
        清除钩子

        Args:
            event_name: 事件名称,如果为None则清除所有钩子
        """
        if event_name:
            if event_name in self._hooks:
                del self._hooks[event_name]
                logger.info(f"已清除事件钩子: {event_name}")
        else:
            self._hooks.clear()
            self._hook_stats.clear()
            logger.info("已清除所有钩子")

    def shutdown(self) -> None:
        """
        关闭钩子管理器

        清理资源并关闭线程池.
        """
        logger.info("钩子管理器正在关闭")

        # 关闭线程池
        self._executor.shutdown(wait=True)

        # 清理资源
        self._hooks.clear()
        self._hook_stats.clear()

        logger.info("钩子管理器已关闭")


# 全局钩子管理器实例
hook_manager = HookManager()


# ==================== 装饰器函数 ====================


def hook(
    event_name: str,
    priority: HookPriority = HookPriority.NORMAL,
    execution_mode: HookExecutionMode = HookExecutionMode.SYNC,
    **kwargs,
):
    """
    钩子装饰器

    用于将函数注册为钩子处理器.

    Args:
        event_name: 事件名称
        priority: 优先级
        execution_mode: 执行模式
        **kwargs: 其他钩子配置

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        hook_manager.register(
            event_name=event_name,
            handler=func,
            priority=priority,
            execution_mode=execution_mode,
            **kwargs,
        )
        return func

    return decorator


def performance_hook(operation_name: str, threshold: float = 1.0):
    """
    性能监控钩子装饰器

    自动记录函数执行性能.

    Args:
        operation_name: 操作名称
        threshold: 慢操作阈值(秒)

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            operation_id = f"{operation_name}_{int(start_time)}"

            try:
                perf_logger.start_operation(operation_id, operation_name)
                result = func(*args, **kwargs)
                duration = perf_logger.end_operation(operation_id, operation_name, True)

                # 检查是否为慢操作
                perf_logger.log_slow_operation(operation_name, duration, threshold)

                return result

            except Exception as e:
                duration = time.time() - start_time
                perf_logger.end_operation(
                    operation_id, operation_name, False, error=str(e)
                )
                raise

        return wrapper

    return decorator


def audit_hook(action: str, resource_type: str):
    """
    审计钩子装饰器

    自动记录操作审计日志.

    Args:
        action: 操作类型
        resource_type: 资源类型

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # 记录成功的操作
                audit_logger.log_user_action(
                    action=action,
                    resource_type=resource_type,
                    success=True,
                    function_name=func.__name__,
                )

                return result

            except Exception as e:
                # 记录失败的操作
                audit_logger.log_user_action(
                    action=action,
                    resource_type=resource_type,
                    success=False,
                    error=str(e),
                    function_name=func.__name__,
                )
                raise

        return wrapper

    return decorator


# ==================== 便捷函数 ====================


def trigger_hook(event_name: str, *args, **kwargs) -> list[HookResult]:
    """
    触发钩子的便捷函数

    Args:
        event_name: 事件名称
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        钩子执行结果列表
    """
    return hook_manager.trigger(event_name, *args, **kwargs)


def register_hook(event_name: str, handler: Callable, **kwargs) -> HookInfo:
    """
    注册钩子的便捷函数

    Args:
        event_name: 事件名称
        handler: 钩子处理函数
        **kwargs: 其他钩子配置

    Returns:
        钩子信息对象
    """
    return hook_manager.register(event_name, handler, **kwargs)


def unregister_hook(event_name: str, handler: Callable) -> bool:
    """
    注销钩子的便捷函数

    Args:
        event_name: 事件名称
        handler: 钩子处理函数

    Returns:
        是否成功注销
    """
    return hook_manager.unregister(event_name, handler)


def get_hook_manager() -> HookManager:
    """
    获取全局钩子管理器

    Returns:
        钩子管理器实例
    """
    return hook_manager


def shutdown_hooks() -> None:
    """
    关闭钩子系统
    """
    hook_manager.shutdown()
