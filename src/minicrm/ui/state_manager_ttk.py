"""MiniCRM 状态管理器 - TTK版本

提供应用程序级别的状态管理和同步功能,包括:
- 全局状态管理
- 模块间状态同步
- 状态变化通知
- 状态持久化
- 状态回滚和恢复

设计原则:
- 单一数据源:所有状态通过状态管理器统一管理
- 响应式更新:状态变化自动通知相关模块
- 类型安全:强类型状态定义和验证
- 性能优化:支持状态缓存和批量更新

TTK版本特点:
- 使用Python标准库替代Qt信号系统
- 基于回调函数的事件通知机制
- 完全兼容tkinter/ttk环境
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import threading
import time
from typing import Any, TypeVar

from minicrm.core.exceptions import UIError
from minicrm.ui.data_bus import get_data_bus
from minicrm.ui.event_bus import EventPriority, get_event_bus


T = TypeVar("T")


class StateChangeType(Enum):
    """状态变化类型"""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESET = "reset"
    SYNCED = "synced"


@dataclass
class StateChange:
    """状态变化记录"""

    key: str
    change_type: StateChangeType
    old_value: Any = None
    new_value: Any = None
    timestamp: float = field(default_factory=time.time)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class StateValidator:
    """状态验证器基类"""

    def validate(self, key: str, value: Any) -> bool:
        """验证状态值

        Args:
            key: 状态键
            value: 状态值

        Returns:
            bool: 是否验证通过
        """
        return True

    def transform(self, key: str, value: Any) -> Any:
        """转换状态值

        Args:
            key: 状态键
            value: 原始状态值

        Returns:
            Any: 转换后的状态值
        """
        return value


class TypedStateValidator(StateValidator):
    """类型化状态验证器"""

    def __init__(self, expected_type: type, allow_none: bool = False):
        self.expected_type = expected_type
        self.allow_none = allow_none

    def validate(self, key: str, value: Any) -> bool:
        """验证状态类型"""
        if value is None and self.allow_none:
            return True
        return isinstance(value, self.expected_type)

    def transform(self, key: str, value: Any) -> Any:
        """尝试类型转换"""
        if value is None and self.allow_none:
            return None

        if isinstance(value, self.expected_type):
            return value

        try:
            return self.expected_type(value)
        except (ValueError, TypeError):
            raise UIError(
                f"无法将状态转换为 {self.expected_type.__name__}: {value}",
                "StateManager",
            )


@dataclass
class StateDefinition:
    """状态定义"""

    key: str
    default_value: Any = None
    validator: StateValidator | None = None
    persistent: bool = False
    sync_modules: set[str] = field(default_factory=set)
    description: str | None = None


class StateManagerTTK:
    """状态管理器 - TTK版本

    提供应用程序级别的状态管理功能:
    - 全局状态存储和管理
    - 模块间状态同步
    - 状态变化通知
    - 状态持久化支持
    - 状态历史记录

    使用回调函数替代Qt信号系统
    """

    def __init__(self):
        """初始化状态管理器"""
        self._logger = logging.getLogger(__name__)

        # 状态存储
        self._states: dict[str, Any] = {}

        # 状态定义
        self._state_definitions: dict[str, StateDefinition] = {}

        # 状态变化监听器
        self._state_listeners: dict[str, set[Callable]] = defaultdict(set)

        # 全局状态监听器
        self._global_listeners: set[Callable] = set()

        # 模块状态映射
        self._module_states: dict[str, set[str]] = defaultdict(set)

        # 状态变化历史
        self._change_history: list[StateChange] = []
        self._max_history_size = 1000

        # 线程锁
        self._lock = threading.RLock()

        # 事件总线和数据总线
        self._event_bus = get_event_bus()
        self._data_bus = get_data_bus()

        # 回调函数集合 - 替代Qt信号
        self._state_changed_callbacks: set[Callable[[StateChange], None]] = set()
        self._state_synced_callbacks: set[Callable[[str, list], None]] = set()
        self._state_error_callbacks: set[Callable[[str, str], None]] = set()

        # 设置事件监听
        self._setup_event_listeners()

        self._logger.debug("状态管理器初始化完成")

    def connect_state_changed(self, callback: Callable[[StateChange], None]) -> None:
        """连接状态变化回调函数"""
        self._state_changed_callbacks.add(callback)

    def disconnect_state_changed(self, callback: Callable[[StateChange], None]) -> None:
        """断开状态变化回调函数"""
        self._state_changed_callbacks.discard(callback)

    def connect_state_synced(self, callback: Callable[[str, list], None]) -> None:
        """连接状态同步回调函数"""
        self._state_synced_callbacks.add(callback)

    def disconnect_state_synced(self, callback: Callable[[str, list], None]) -> None:
        """断开状态同步回调函数"""
        self._state_synced_callbacks.discard(callback)

    def connect_state_error(self, callback: Callable[[str, str], None]) -> None:
        """连接状态错误回调函数"""
        self._state_error_callbacks.add(callback)

    def disconnect_state_error(self, callback: Callable[[str, str], None]) -> None:
        """断开状态错误回调函数"""
        self._state_error_callbacks.discard(callback)

    def _emit_state_changed(self, change: StateChange) -> None:
        """触发状态变化回调"""
        for callback in self._state_changed_callbacks.copy():
            try:
                callback(change)
            except Exception as e:
                self._logger.error(f"状态变化回调执行失败: {e}")

    def _emit_state_synced(self, module: str, keys: list[str]) -> None:
        """触发状态同步回调"""
        for callback in self._state_synced_callbacks.copy():
            try:
                callback(module, keys)
            except Exception as e:
                self._logger.error(f"状态同步回调执行失败: {e}")

    def _emit_state_error(self, key: str, error: str) -> None:
        """触发状态错误回调"""
        for callback in self._state_error_callbacks.copy():
            try:
                callback(key, error)
            except Exception as e:
                self._logger.error(f"状态错误回调执行失败: {e}")

    def define_state(
        self,
        key: str,
        default_value: Any = None,
        validator: StateValidator | None = None,
        persistent: bool = False,
        sync_modules: set[str] | None = None,
        description: str | None = None,
    ) -> None:
        """定义状态

        Args:
            key: 状态键
            default_value: 默认值
            validator: 状态验证器
            persistent: 是否持久化
            sync_modules: 需要同步的模块集合
            description: 状态描述
        """
        try:
            with self._lock:
                state_def = StateDefinition(
                    key=key,
                    default_value=default_value,
                    validator=validator,
                    persistent=persistent,
                    sync_modules=sync_modules or set(),
                    description=description,
                )

                self._state_definitions[key] = state_def

                # 设置默认值
                if key not in self._states and default_value is not None:
                    self._states[key] = default_value

                # 注册模块状态映射
                for module in state_def.sync_modules:
                    self._module_states[module].add(key)

                self._logger.debug(f"状态定义完成: {key}")

        except Exception as e:
            self._logger.error(f"状态定义失败 [{key}]: {e}")
            raise UIError(f"状态定义失败: {e}", "StateManager") from e

    def set_state(
        self,
        key: str,
        value: Any,
        source: str | None = None,
        sync: bool = True,
        notify: bool = True,
    ) -> bool:
        """设置状态

        Args:
            key: 状态键
            value: 状态值
            source: 状态来源
            sync: 是否同步到其他模块
            notify: 是否发送通知

        Returns:
            bool: 是否设置成功
        """
        try:
            with self._lock:
                # 验证状态
                if not self._validate_state(key, value):
                    return False

                # 转换状态值
                transformed_value = self._transform_state(key, value)

                # 获取旧值
                old_value = self._states.get(key)

                # 检查值是否真的发生了变化
                if old_value == transformed_value:
                    return True

                # 设置状态
                self._states[key] = transformed_value

                # 创建变化记录
                change = StateChange(
                    key=key,
                    change_type=StateChangeType.UPDATED
                    if key in self._states
                    else StateChangeType.CREATED,
                    old_value=old_value,
                    new_value=transformed_value,
                    source=source,
                )

                # 添加到历史记录
                self._add_to_history(change)

                # 同步到数据总线
                self._sync_to_data_bus(key, transformed_value, source)

                # 发送通知
                if notify:
                    self._notify_state_change(change)

                # 同步到模块
                if sync:
                    self._sync_to_modules(key, transformed_value, source)

                self._logger.debug(f"状态设置成功: {key} = {transformed_value}")
                return True

        except Exception as e:
            self._logger.error(f"状态设置失败 [{key}]: {e}")
            self._emit_state_error(key, str(e))
            return False

    def get_state(self, key: str, default: Any = None) -> Any:
        """获取状态

        Args:
            key: 状态键
            default: 默认值

        Returns:
            Any: 状态值
        """
        try:
            with self._lock:
                if key in self._states:
                    return self._states[key]

                # 检查状态定义中的默认值
                if key in self._state_definitions:
                    state_def = self._state_definitions[key]
                    if state_def.default_value is not None:
                        return state_def.default_value

                return default

        except Exception as e:
            self._logger.error(f"状态获取失败 [{key}]: {e}")
            return default

    def has_state(self, key: str) -> bool:
        """检查状态是否存在

        Args:
            key: 状态键

        Returns:
            bool: 状态是否存在
        """
        with self._lock:
            return key in self._states or key in self._state_definitions

    def delete_state(
        self, key: str, source: str | None = None, notify: bool = True
    ) -> bool:
        """删除状态

        Args:
            key: 状态键
            source: 操作来源
            notify: 是否发送通知

        Returns:
            bool: 是否删除成功
        """
        try:
            with self._lock:
                if key not in self._states:
                    return False

                # 获取旧值
                old_value = self._states[key]

                # 删除状态
                del self._states[key]

                # 创建变化记录
                change = StateChange(
                    key=key,
                    change_type=StateChangeType.DELETED,
                    old_value=old_value,
                    new_value=None,
                    source=source,
                )

                # 添加到历史记录
                self._add_to_history(change)

                # 发送通知
                if notify:
                    self._notify_state_change(change)

                self._logger.debug(f"状态删除成功: {key}")
                return True

        except Exception as e:
            self._logger.error(f"状态删除失败 [{key}]: {e}")
            self._emit_state_error(key, str(e))
            return False

    def subscribe_state(
        self, key: str, callback: Callable[[StateChange], None]
    ) -> None:
        """订阅状态变化

        Args:
            key: 状态键
            callback: 回调函数
        """
        try:
            with self._lock:
                self._state_listeners[key].add(callback)
                self._logger.debug(f"订阅状态变化: {key}")

        except Exception as e:
            self._logger.error(f"状态订阅失败 [{key}]: {e}")

    def unsubscribe_state(
        self, key: str, callback: Callable[[StateChange], None]
    ) -> None:
        """取消订阅状态变化

        Args:
            key: 状态键
            callback: 回调函数
        """
        try:
            with self._lock:
                if key in self._state_listeners:
                    self._state_listeners[key].discard(callback)
                    self._logger.debug(f"取消订阅状态变化: {key}")

        except Exception as e:
            self._logger.error(f"取消状态订阅失败 [{key}]: {e}")

    def subscribe_global(self, callback: Callable[[StateChange], None]) -> None:
        """订阅所有状态变化

        Args:
            callback: 回调函数
        """
        try:
            with self._lock:
                self._global_listeners.add(callback)
                self._logger.debug("订阅全局状态变化")

        except Exception as e:
            self._logger.error(f"全局状态订阅失败: {e}")

    def unsubscribe_global(self, callback: Callable[[StateChange], None]) -> None:
        """取消订阅所有状态变化

        Args:
            callback: 回调函数
        """
        try:
            with self._lock:
                self._global_listeners.discard(callback)
                self._logger.debug("取消订阅全局状态变化")

        except Exception as e:
            self._logger.error(f"取消全局状态订阅失败: {e}")

    def sync_module_states(self, module_name: str, states: dict[str, Any]) -> None:
        """同步模块状态

        Args:
            module_name: 模块名称
            states: 状态字典
        """
        try:
            with self._lock:
                synced_keys = []

                for key, value in states.items():
                    if self.set_state(
                        key, value, source=module_name, sync=False, notify=False
                    ):
                        synced_keys.append(key)

                # 发送同步完成信号
                if synced_keys:
                    self._emit_state_synced(module_name, synced_keys)

                    # 发布同步事件
                    self._event_bus.publish(
                        "state.module_synced",
                        data={"module": module_name, "keys": synced_keys},
                        source="StateManager",
                    )

                self._logger.debug(
                    f"模块状态同步完成: {module_name} ({len(synced_keys)} 个状态)"
                )

        except Exception as e:
            self._logger.error(f"模块状态同步失败 [{module_name}]: {e}")

    def get_module_states(self, module_name: str) -> dict[str, Any]:
        """获取模块相关的所有状态

        Args:
            module_name: 模块名称

        Returns:
            Dict[str, Any]: 模块状态字典
        """
        try:
            with self._lock:
                module_states = {}

                if module_name in self._module_states:
                    for key in self._module_states[module_name]:
                        if key in self._states:
                            module_states[key] = self._states[key]

                return module_states

        except Exception as e:
            self._logger.error(f"获取模块状态失败 [{module_name}]: {e}")
            return {}

    def reset_states(
        self, keys: list[str] | None = None, source: str | None = None
    ) -> None:
        """重置状态到默认值

        Args:
            keys: 要重置的状态键列表,如果为None则重置所有状态
            source: 操作来源
        """
        try:
            with self._lock:
                reset_keys = keys or list(self._state_definitions.keys())

                for key in reset_keys:
                    if key in self._state_definitions:
                        state_def = self._state_definitions[key]
                        if state_def.default_value is not None:
                            self.set_state(
                                key,
                                state_def.default_value,
                                source=source,
                                notify=False,
                            )

                # 发布重置事件
                self._event_bus.publish(
                    "state.reset",
                    data={"keys": reset_keys},
                    source=source or "StateManager",
                )

                self._logger.debug(f"状态重置完成: {len(reset_keys)} 个状态")

        except Exception as e:
            self._logger.error(f"状态重置失败: {e}")

    def _validate_state(self, key: str, value: Any) -> bool:
        """验证状态值"""
        try:
            if key in self._state_definitions:
                state_def = self._state_definitions[key]
                if state_def.validator:
                    return state_def.validator.validate(key, value)
            return True

        except Exception as e:
            self._logger.error(f"状态验证失败 [{key}]: {e}")
            return False

    def _transform_state(self, key: str, value: Any) -> Any:
        """转换状态值"""
        try:
            if key in self._state_definitions:
                state_def = self._state_definitions[key]
                if state_def.validator:
                    return state_def.validator.transform(key, value)
            return value

        except Exception as e:
            self._logger.error(f"状态转换失败 [{key}]: {e}")
            raise

    def _notify_state_change(self, change: StateChange) -> None:
        """通知状态变化"""
        try:
            # 通知特定状态的监听器
            if change.key in self._state_listeners:
                for callback in self._state_listeners[change.key].copy():
                    try:
                        callback(change)
                    except Exception as e:
                        self._logger.error(f"状态监听器回调失败 [{change.key}]: {e}")

            # 通知全局监听器
            for callback in self._global_listeners.copy():
                try:
                    callback(change)
                except Exception as e:
                    self._logger.error(f"全局状态监听器回调失败: {e}")

            # 发送回调信号
            self._emit_state_changed(change)

            # 发布状态变化事件
            self._event_bus.publish(
                "state.changed",
                data={
                    "key": change.key,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "change_type": change.change_type.value,
                },
                source=change.source or "StateManager",
            )

        except Exception as e:
            self._logger.error(f"状态变化通知失败: {e}")

    def _sync_to_modules(self, key: str, value: Any, source: str | None) -> None:
        """同步状态到相关模块"""
        try:
            if key in self._state_definitions:
                state_def = self._state_definitions[key]

                for module in state_def.sync_modules:
                    if module != source:  # 避免循环同步
                        # 发布模块同步事件
                        self._event_bus.publish(
                            f"state.sync.{module}",
                            data={"key": key, "value": value},
                            source="StateManager",
                            priority=EventPriority.HIGH,
                        )

        except Exception as e:
            self._logger.error(f"模块状态同步失败 [{key}]: {e}")

    def _sync_to_data_bus(self, key: str, value: Any, source: str | None) -> None:
        """同步状态到数据总线"""
        try:
            # 将状态同步到数据总线,使用state_前缀避免冲突
            data_key = f"state_{key}"
            self._data_bus.set_data(data_key, value, source=source, notify=False)

        except Exception as e:
            self._logger.error(f"数据总线同步失败 [{key}]: {e}")

    def _add_to_history(self, change: StateChange) -> None:
        """添加到历史记录"""
        try:
            self._change_history.append(change)

            # 限制历史记录大小
            if len(self._change_history) > self._max_history_size:
                self._change_history.pop(0)

        except Exception as e:
            self._logger.error(f"添加历史记录失败: {e}")

    def _setup_event_listeners(self) -> None:
        """设置事件监听器"""
        try:
            # 监听模块同步请求事件
            self._event_bus.subscribe("state.sync_request", self._on_sync_request_event)

            # 监听应用关闭事件
            self._event_bus.subscribe("app.shutdown", self._on_app_shutdown_event)

        except Exception as e:
            self._logger.error(f"事件监听器设置失败: {e}")

    def _on_sync_request_event(self, event) -> None:
        """处理同步请求事件"""
        try:
            data = event.data
            if isinstance(data, dict):
                module_name = data.get("module")
                states = data.get("states", {})

                if module_name and states:
                    self.sync_module_states(module_name, states)

        except Exception as e:
            self._logger.error(f"同步请求事件处理失败: {e}")

    def _on_app_shutdown_event(self, event) -> None:
        """处理应用关闭事件"""
        try:
            # 保存持久化状态
            self._save_persistent_states()

        except Exception as e:
            self._logger.error(f"应用关闭事件处理失败: {e}")

    def _save_persistent_states(self) -> None:
        """保存持久化状态"""
        try:
            # TODO: 实现状态持久化到文件或数据库
            persistent_states = {}

            for key, state_def in self._state_definitions.items():
                if state_def.persistent and key in self._states:
                    persistent_states[key] = self._states[key]

            if persistent_states:
                self._logger.debug(f"保存持久化状态: {len(persistent_states)} 个状态")

        except Exception as e:
            self._logger.error(f"持久化状态保存失败: {e}")

    def get_change_history(self, key: str | None = None) -> list[StateChange]:
        """获取状态变化历史

        Args:
            key: 状态键,如果为None则返回所有历史

        Returns:
            List[StateChange]: 变化历史列表
        """
        with self._lock:
            if key is None:
                return self._change_history.copy()
            return [change for change in self._change_history if change.key == key]

    def get_all_states(self) -> dict[str, Any]:
        """获取所有状态"""
        with self._lock:
            return self._states.copy()

    def get_state_definitions(self) -> dict[str, StateDefinition]:
        """获取所有状态定义"""
        with self._lock:
            return self._state_definitions.copy()

    def cleanup(self) -> None:
        """清理资源"""
        try:
            with self._lock:
                # 保存持久化状态
                self._save_persistent_states()

                # 清空监听器
                self._state_listeners.clear()
                self._global_listeners.clear()
                self._state_changed_callbacks.clear()
                self._state_synced_callbacks.clear()
                self._state_error_callbacks.clear()

                # 清空状态
                self._states.clear()
                self._change_history.clear()

                self._logger.debug("状态管理器清理完成")

        except Exception as e:
            self._logger.error(f"状态管理器清理失败: {e}")


# 为了兼容性,创建一个别名
StateManager = StateManagerTTK

# 全局状态管理器实例
_global_state_manager: StateManagerTTK | None = None


def get_state_manager() -> StateManagerTTK:
    """获取全局状态管理器实例"""
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = StateManagerTTK()
    return _global_state_manager


def set_global_state_manager(state_manager: StateManagerTTK) -> None:
    """设置全局状态管理器实例"""
    global _global_state_manager
    _global_state_manager = state_manager


# 便捷函数
def set_app_state(key: str, value: Any, source: str | None = None) -> bool:
    """设置应用状态"""
    return get_state_manager().set_state(key, value, source=source)


def get_app_state(key: str, default: Any = None) -> Any:
    """获取应用状态"""
    return get_state_manager().get_state(key, default=default)


def subscribe_app_state(key: str, callback: Callable[[StateChange], None]) -> None:
    """订阅应用状态变化"""
    get_state_manager().subscribe_state(key, callback)
