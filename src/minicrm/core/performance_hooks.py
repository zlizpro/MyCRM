"""
MiniCRM 性能监控Hooks

为关键操作提供性能监控hooks,包括:
- 数据库操作监控
- 服务方法监控
- UI操作监控
- 自动性能数据收集
"""

import functools
import logging
import time
from collections.abc import Callable
from typing import Any

from .database_performance_analyzer import database_performance_analyzer
from .performance_monitor import performance_monitor


class DatabasePerformanceHook:
    """数据库性能监控Hook"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def monitor_query(self, operation_type: str = "query"):
        """
        数据库查询监控装饰器

        Args:
            operation_type: 操作类型 (query, insert, update, delete)
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 提取SQL信息
                sql = None
                params = None
                sql_display = None
                params_display = None

                if args:
                    if isinstance(args[0], str):
                        sql = args[0]
                        sql_display = sql[:100] + "..." if len(sql) > 100 else sql
                    if len(args) > 1:
                        params = args[1]
                        params_display = (
                            str(params)[:50] + "..."
                            if len(str(params)) > 50
                            else str(params)
                        )

                operation_name = f"db.{operation_type}"
                metadata = {
                    "sql": sql_display,
                    "params": params_display,
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                # 记录开始时间
                start_time = time.perf_counter()
                connection_start = time.perf_counter()

                result = None
                error_message = None
                rows_affected = 0
                rows_returned = 0

                try:
                    with performance_monitor.monitor_operation(
                        operation_name, **metadata
                    ):
                        result = func(*args, **kwargs)

                        # 尝试获取结果信息
                        if hasattr(result, "__len__"):
                            rows_returned = len(result)
                        elif isinstance(result, int):
                            rows_affected = result

                except Exception as e:
                    error_message = str(e)
                    raise
                finally:
                    # 计算执行时间
                    end_time = time.perf_counter()
                    execution_time = (end_time - start_time) * 1000  # 转换为毫秒
                    connection_time = (connection_start - start_time) * 1000

                    # 记录到数据库性能分析器
                    if sql:
                        database_performance_analyzer.record_query(
                            sql=sql,
                            params=params,
                            execution_time=execution_time,
                            rows_affected=rows_affected,
                            rows_returned=rows_returned,
                            connection_time=connection_time,
                            error_message=error_message,
                        )

                return result

            return wrapper

        return decorator

    def monitor_transaction(self, func: Callable) -> Callable:
        """事务监控装饰器"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = "db.transaction"
            metadata = {
                "function": (
                    f"{getattr(func, '__module__', 'unknown')}."
                    f"{getattr(func, '__name__', 'unknown')}"
                )
            }

            start_time = time.perf_counter()
            error_message = None

            try:
                with performance_monitor.monitor_operation(operation_name, **metadata):
                    return func(*args, **kwargs)
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                # 记录事务性能
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000

                database_performance_analyzer.record_query(
                    sql="TRANSACTION",
                    execution_time=execution_time,
                    error_message=error_message,
                )

        return wrapper

    def monitor_connection(self, func: Callable) -> Callable:
        """数据库连接监控装饰器"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            connection_id = f"conn_{id(args[0]) if args else 'unknown'}"
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)

                # 记录连接时间
                end_time = time.perf_counter()
                connect_time = (end_time - start_time) * 1000

                database_performance_analyzer.record_connection(
                    connection_id=connection_id, connect_time=connect_time
                )

                return result

            except Exception as e:
                self._logger.error(f"数据库连接失败: {e}")
                raise

        return wrapper


class ServicePerformanceHook:
    """服务层性能监控Hook"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def monitor_service_method(self, service_name: str = None):
        """
        服务方法监控装饰器

        Args:
            service_name: 服务名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 确定服务名称
                if service_name:
                    svc_name = service_name
                elif args and hasattr(args[0], "__class__"):
                    svc_name = args[0].__class__.__name__
                else:
                    svc_name = "unknown"

                operation_name = (
                    f"service.{svc_name}.{getattr(func, '__name__', 'unknown')}"
                )
                metadata = {
                    "service": svc_name,
                    "method": getattr(func, "__name__", "unknown"),
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                with performance_monitor.monitor_operation(operation_name, **metadata):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def monitor_business_operation(self, operation_name: str):
        """
        业务操作监控装饰器

        Args:
            operation_name: 业务操作名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = f"business.{operation_name}"
                metadata = {
                    "operation": operation_name,
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                with performance_monitor.monitor_operation(op_name, **metadata):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


class UIPerformanceHook:
    """UI性能监控Hook"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def monitor_ui_operation(self, operation_name: str, component_name: str = None):
        """
        UI操作监控装饰器

        Args:
            operation_name: UI操作名称
            component_name: 组件名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 确定组件名称
                if component_name:
                    comp_name = component_name
                elif args and hasattr(args[0], "__class__"):
                    comp_name = args[0].__class__.__name__
                else:
                    comp_name = "unknown"

                op_name = f"ui.{operation_name}"
                metadata = {
                    "operation": operation_name,
                    "component": comp_name,
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                # 开始UI操作计时
                from .ui_performance_analyzer import ui_performance_analyzer

                timing_id = ui_performance_analyzer.start_operation_timing(
                    operation_name, comp_name
                )

                _start_time = time.perf_counter()  # 预留用于详细计时
                _render_start = None  # 预留用于渲染计时
                _data_load_start = None  # 预留用于数据加载计时
                error_message = None

                try:
                    with performance_monitor.monitor_operation(op_name, **metadata):
                        result = func(*args, **kwargs)
                        return result

                except Exception as e:
                    error_message = str(e)
                    raise
                finally:
                    # 结束计时并记录指标
                    if timing_id:
                        from .ui_performance_analyzer import ui_performance_analyzer

                        ui_performance_analyzer.end_operation_timing(
                            timing_id,
                            render_time=0.0,  # 可以通过参数传入具体的渲染时间
                            data_load_time=0.0,  # 可以通过参数传入具体的数据加载时间
                            error_message=error_message,
                            **metadata,
                        )

            return wrapper

        return decorator

    def monitor_page_load(self, page_name: str):
        """
        页面加载监控装饰器

        Args:
            page_name: 页面名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = f"ui.page_load.{page_name}"
                metadata = {
                    "page": page_name,
                    "component_type": "page",
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                # 开始页面加载计时
                from .ui_performance_analyzer import ui_performance_analyzer

                timing_id = ui_performance_analyzer.start_operation_timing(
                    "page_load", page_name
                )

                error_message = None

                try:
                    with performance_monitor.monitor_operation(op_name, **metadata):
                        result = func(*args, **kwargs)
                        return result

                except Exception as e:
                    error_message = str(e)
                    raise
                finally:
                    # 结束计时并记录指标
                    if timing_id:
                        from .ui_performance_analyzer import ui_performance_analyzer

                        ui_performance_analyzer.end_operation_timing(
                            timing_id,
                            error_message=error_message,
                            **metadata,
                        )

            return wrapper

        return decorator

    def monitor_data_refresh(self, data_type: str, component_name: str = None):
        """
        数据刷新监控装饰器

        Args:
            data_type: 数据类型
            component_name: 组件名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 确定组件名称
                if component_name:
                    comp_name = component_name
                elif args and hasattr(args[0], "__class__"):
                    comp_name = args[0].__class__.__name__
                else:
                    comp_name = "unknown"

                op_name = f"ui.data_refresh.{data_type}"
                metadata = {
                    "data_type": data_type,
                    "component_type": "data_refresh",
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                # 开始数据刷新计时
                from .ui_performance_analyzer import ui_performance_analyzer

                timing_id = ui_performance_analyzer.start_operation_timing(
                    "data_refresh", comp_name
                )

                data_load_start = time.perf_counter()
                error_message = None

                try:
                    with performance_monitor.monitor_operation(op_name, **metadata):
                        result = func(*args, **kwargs)
                        return result

                except Exception as e:
                    error_message = str(e)
                    raise
                finally:
                    # 计算数据加载时间
                    data_load_end = time.perf_counter()
                    data_load_time = (data_load_end - data_load_start) * 1000

                    # 结束计时并记录指标
                    if timing_id:
                        from .ui_performance_analyzer import ui_performance_analyzer

                        ui_performance_analyzer.end_operation_timing(
                            timing_id,
                            data_load_time=data_load_time,
                            error_message=error_message,
                            **metadata,
                        )

            return wrapper

        return decorator

    def monitor_render_operation(self, component_name: str = None):
        """
        渲染操作监控装饰器

        Args:
            component_name: 组件名称
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 确定组件名称
                if component_name:
                    comp_name = component_name
                elif args and hasattr(args[0], "__class__"):
                    comp_name = args[0].__class__.__name__
                else:
                    comp_name = "unknown"

                op_name = f"ui.render.{comp_name}"
                metadata = {
                    "component_type": "render",
                    "function": (
                        f"{getattr(func, '__module__', 'unknown')}."
                        f"{getattr(func, '__name__', 'unknown')}"
                    ),
                }

                # 开始渲染计时
                from .ui_performance_analyzer import ui_performance_analyzer

                timing_id = ui_performance_analyzer.start_operation_timing(
                    "render", comp_name
                )

                render_start = time.perf_counter()
                error_message = None

                try:
                    with performance_monitor.monitor_operation(op_name, **metadata):
                        result = func(*args, **kwargs)
                        return result

                except Exception as e:
                    error_message = str(e)
                    raise
                finally:
                    # 计算渲染时间
                    render_end = time.perf_counter()
                    render_time = (render_end - render_start) * 1000

                    # 结束计时并记录指标
                    if timing_id:
                        from .ui_performance_analyzer import ui_performance_analyzer

                        ui_performance_analyzer.end_operation_timing(
                            timing_id,
                            render_time=render_time,
                            error_message=error_message,
                            **metadata,
                        )

            return wrapper

        return decorator


class PerformanceHookManager:
    """性能监控Hook管理器"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.db_hook = DatabasePerformanceHook()
        self.service_hook = ServicePerformanceHook()
        self.ui_hook = UIPerformanceHook()
        self._enabled = True

    def enable(self) -> None:
        """启用性能监控hooks"""
        self._enabled = True
        performance_monitor.enable()
        self._logger.info("性能监控hooks已启用")

    def disable(self) -> None:
        """禁用性能监控hooks"""
        self._enabled = False
        performance_monitor.disable()
        self._logger.info("性能监控hooks已禁用")

    def is_enabled(self) -> bool:
        """检查是否启用了性能监控hooks"""
        return self._enabled

    def apply_database_hooks(self, database_manager):
        """
        为数据库管理器应用性能监控hooks

        Args:
            database_manager: 数据库管理器实例
        """
        if not self._enabled:
            return

        try:
            # 监控查询方法
            if hasattr(database_manager, "execute_query"):
                database_manager.execute_query = self.db_hook.monitor_query("query")(
                    database_manager.execute_query
                )

            # 监控插入方法
            if hasattr(database_manager, "execute_insert"):
                database_manager.execute_insert = self.db_hook.monitor_query("insert")(
                    database_manager.execute_insert
                )

            # 监控更新方法
            if hasattr(database_manager, "execute_update"):
                database_manager.execute_update = self.db_hook.monitor_query("update")(
                    database_manager.execute_update
                )

            # 监控删除方法
            if hasattr(database_manager, "execute_delete"):
                database_manager.execute_delete = self.db_hook.monitor_query("delete")(
                    database_manager.execute_delete
                )

            self._logger.info("数据库性能监控hooks已应用")

        except Exception as e:
            self._logger.error(f"应用数据库性能监控hooks失败: {e}")

    def apply_service_hooks(self, service_instance, service_name: str = None):
        """
        为服务实例应用性能监控hooks

        Args:
            service_instance: 服务实例
            service_name: 服务名称
        """
        if not self._enabled:
            return

        try:
            svc_name = service_name or service_instance.__class__.__name__

            # 获取所有公共方法
            methods = [
                method
                for method in dir(service_instance)
                if not method.startswith("_")
                and callable(getattr(service_instance, method))
            ]

            # 为每个方法应用监控
            for method_name in methods:
                method = getattr(service_instance, method_name)
                if callable(method):
                    monitored_method = self.service_hook.monitor_service_method(
                        svc_name
                    )(method)
                    setattr(service_instance, method_name, monitored_method)

            self._logger.info(f"服务性能监控hooks已应用: {svc_name}")

        except Exception as e:
            self._logger.error(f"应用服务性能监控hooks失败: {e}")

    def get_performance_report(self) -> dict[str, Any]:
        """获取性能监控报告"""
        try:
            summary = performance_monitor.get_summary()
            operations = performance_monitor.get_all_operations()

            # 按类型分组统计
            db_operations = [op for op in operations if op.startswith("db.")]
            service_operations = [op for op in operations if op.startswith("service.")]
            ui_operations = [op for op in operations if op.startswith("ui.")]
            business_operations = [
                op for op in operations if op.startswith("business.")
            ]

            # 获取各类型的统计信息
            db_stats = [
                performance_monitor.get_operation_stats(op) for op in db_operations
            ]
            service_stats = [
                performance_monitor.get_operation_stats(op) for op in service_operations
            ]
            ui_stats = [
                performance_monitor.get_operation_stats(op) for op in ui_operations
            ]
            business_stats = [
                performance_monitor.get_operation_stats(op)
                for op in business_operations
            ]

            # 获取专门的分析器报告
            from .database_performance_analyzer import database_performance_analyzer
            from .ui_performance_analyzer import ui_performance_analyzer

            db_detailed_report = (
                database_performance_analyzer.generate_performance_report()
            )
            ui_detailed_report = ui_performance_analyzer.generate_performance_report()

            return {
                "summary": summary,
                "database": {
                    "operations_count": len(db_operations),
                    "operations": db_stats,
                    "total_duration_ms": sum(
                        stat["total_duration_ms"] for stat in db_stats
                    ),
                    "detailed_analysis": db_detailed_report,
                },
                "services": {
                    "operations_count": len(service_operations),
                    "operations": service_stats,
                    "total_duration_ms": sum(
                        stat["total_duration_ms"] for stat in service_stats
                    ),
                },
                "ui": {
                    "operations_count": len(ui_operations),
                    "operations": ui_stats,
                    "total_duration_ms": sum(
                        stat["total_duration_ms"] for stat in ui_stats
                    ),
                    "detailed_analysis": ui_detailed_report,
                },
                "business": {
                    "operations_count": len(business_operations),
                    "operations": business_stats,
                    "total_duration_ms": sum(
                        stat["total_duration_ms"] for stat in business_stats
                    ),
                },
            }

        except Exception as e:
            self._logger.error(f"生成性能监控报告失败: {e}")
            return {"error": str(e)}


# 全局性能监控hook管理器
performance_hooks = PerformanceHookManager()


# 便捷装饰器
def monitor_db_query(operation_type: str = "query"):
    """数据库查询监控装饰器"""
    return performance_hooks.db_hook.monitor_query(operation_type)


def monitor_service_method(service_name: str = None):
    """服务方法监控装饰器"""
    return performance_hooks.service_hook.monitor_service_method(service_name)


def monitor_business_operation(operation_name: str):
    """业务操作监控装饰器"""
    return performance_hooks.service_hook.monitor_business_operation(operation_name)


def monitor_ui_operation(operation_name: str, component_name: str = None):
    """UI操作监控装饰器"""
    return performance_hooks.ui_hook.monitor_ui_operation(
        operation_name, component_name
    )


def monitor_page_load(page_name: str):
    """页面加载监控装饰器"""
    return performance_hooks.ui_hook.monitor_page_load(page_name)


def monitor_data_refresh(data_type: str, component_name: str = None):
    """数据刷新监控装饰器"""
    return performance_hooks.ui_hook.monitor_data_refresh(data_type, component_name)


def monitor_render_operation(component_name: str = None):
    """渲染操作监控装饰器"""
    return performance_hooks.ui_hook.monitor_render_operation(component_name)


def monitor_db_connection():
    """数据库连接监控装饰器"""
    return performance_hooks.db_hook.monitor_connection
