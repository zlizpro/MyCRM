"""MiniCRM 模块间数据传递机制 - TTK版本

提供模块间数据共享和通信的统一接口,包括:
- 数据存储和检索
- 数据变化通知
- 数据验证和转换
- 数据持久化支持
- 数据同步机制

设计原则:
- 松耦合:模块间通过数据总线通信,不直接依赖
- 类型安全:强类型数据传递和验证
- 性能优化:支持数据缓存和懒加载
- 扩展性:支持自定义数据处理器

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


T = TypeVar("T")


class DataChangeType(Enum):
    """数据变化类型"""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    REFRESHED = "refreshed"


@dataclass
class DataChangeEvent:
    """数据变化事件"""

    key: str
    change_type: DataChangeType
    old_value: Any = None
    new_value: Any = None
    timestamp: float = field(default_factory=time.time)
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DataValidator:
    """数据验证器基类"""

    def validate(self, key: str, value: Any) -> bool:
        """验证数据

        Args:
            key: 数据键
            value: 数据值

        Returns:
            bool: 是否验证通过
        """
        return True

    def transform(self, key: str, value: Any) -> Any:
        """转换数据

        Args:
            key: 数据键
            value: 原始数据值

        Returns:
            Any: 转换后的数据值
        """
        return value


class TypedDataValidator(DataValidator):
    """类型化数据验证器"""

    def __init__(self, expected_type: type):
        self.expected_type = expected_type

    def validate(self, key: str, value: Any) -> bool:
        """验证数据类型"""
        return isinstance(value, self.expected_type)

    def transform(self, key: str, value: Any) -> Any:
        """尝试类型转换"""
        if isinstance(value, self.expected_type):
            return value

        try:
            return self.expected_type(value)
        except (ValueError, TypeError):
            raise UIError(
                f"无法将数据转换为 {self.expected_type.__name__}: {value}", "DataBus"
            )


class DataBusTTK:
    """数据总线 - TTK版本

    提供模块间数据传递的核心功能:
    - 数据存储和管理
    - 变化通知和事件分发
    - 数据验证和转换
    - 订阅和取消订阅机制

    使用回调函数替代Qt信号系统
    """

    def __init__(self):
        """初始化数据总线"""
        self._logger = logging.getLogger(__name__)

        # 数据存储
        self._data: dict[str, Any] = {}

        # 数据订阅者
        self._subscribers: dict[str, set[Callable]] = defaultdict(set)

        # 全局订阅者(监听所有数据变化)
        self._global_subscribers: set[Callable] = set()

        # 数据验证器
        self._validators: dict[str, DataValidator] = {}

        # 数据变化历史
        self._change_history: list[DataChangeEvent] = []
        self._max_history_size = 1000

        # 线程锁
        self._lock = threading.RLock()

        # 数据持久化配置
        self._persistent_keys: set[str] = set()

        # 回调函数集合 - 替代Qt信号
        self._data_changed_callbacks: set[Callable[[DataChangeEvent], None]] = set()
        self._data_error_callbacks: set[Callable[[str, str], None]] = set()

        self._logger.debug("数据总线初始化完成")

    def connect_data_changed(self, callback: Callable[[DataChangeEvent], None]) -> None:
        """连接数据变化回调函数"""
        self._data_changed_callbacks.add(callback)

    def disconnect_data_changed(
        self, callback: Callable[[DataChangeEvent], None]
    ) -> None:
        """断开数据变化回调函数"""
        self._data_changed_callbacks.discard(callback)

    def connect_data_error(self, callback: Callable[[str, str], None]) -> None:
        """连接数据错误回调函数"""
        self._data_error_callbacks.add(callback)

    def disconnect_data_error(self, callback: Callable[[str, str], None]) -> None:
        """断开数据错误回调函数"""
        self._data_error_callbacks.discard(callback)

    def _emit_data_changed(self, event: DataChangeEvent) -> None:
        """触发数据变化回调"""
        for callback in self._data_changed_callbacks.copy():
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"数据变化回调执行失败: {e}")

    def _emit_data_error(self, key: str, error: str) -> None:
        """触发数据错误回调"""
        for callback in self._data_error_callbacks.copy():
            try:
                callback(key, error)
            except Exception as e:
                self._logger.error(f"数据错误回调执行失败: {e}")

    def set_data(
        self,
        key: str,
        value: Any,
        source: str | None = None,
        notify: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """设置数据

        Args:
            key: 数据键
            value: 数据值
            source: 数据来源
            notify: 是否发送通知
            metadata: 元数据

        Returns:
            bool: 是否设置成功
        """
        try:
            with self._lock:
                # 数据验证
                if not self._validate_data(key, value):
                    return False

                # 数据转换
                transformed_value = self._transform_data(key, value)

                # 获取旧值
                old_value = self._data.get(key)

                # 确定变化类型
                if key in self._data:
                    change_type = DataChangeType.UPDATED
                else:
                    change_type = DataChangeType.CREATED

                # 设置数据
                self._data[key] = transformed_value

                # 创建变化事件
                event = DataChangeEvent(
                    key=key,
                    change_type=change_type,
                    old_value=old_value,
                    new_value=transformed_value,
                    source=source,
                    metadata=metadata or {},
                )

                # 添加到历史记录
                self._add_to_history(event)

                # 发送通知
                if notify:
                    self._notify_subscribers(event)

                self._logger.debug(f"数据设置成功: {key}")
                return True

        except Exception as e:
            self._logger.error(f"数据设置失败 [{key}]: {e}")
            self._emit_data_error(key, str(e))
            return False

    def get_data(self, key: str, default: Any = None) -> Any:
        """获取数据

        Args:
            key: 数据键
            default: 默认值

        Returns:
            Any: 数据值
        """
        try:
            with self._lock:
                return self._data.get(key, default)

        except Exception as e:
            self._logger.error(f"数据获取失败 [{key}]: {e}")
            return default

    def has_data(self, key: str) -> bool:
        """检查数据是否存在

        Args:
            key: 数据键

        Returns:
            bool: 数据是否存在
        """
        with self._lock:
            return key in self._data

    def delete_data(
        self, key: str, source: str | None = None, notify: bool = True
    ) -> bool:
        """删除数据

        Args:
            key: 数据键
            source: 数据来源
            notify: 是否发送通知

        Returns:
            bool: 是否删除成功
        """
        try:
            with self._lock:
                if key not in self._data:
                    return False

                # 获取旧值
                old_value = self._data[key]

                # 删除数据
                del self._data[key]

                # 创建变化事件
                event = DataChangeEvent(
                    key=key,
                    change_type=DataChangeType.DELETED,
                    old_value=old_value,
                    new_value=None,
                    source=source,
                )

                # 添加到历史记录
                self._add_to_history(event)

                # 发送通知
                if notify:
                    self._notify_subscribers(event)

                self._logger.debug(f"数据删除成功: {key}")
                return True

        except Exception as e:
            self._logger.error(f"数据删除失败 [{key}]: {e}")
            self._emit_data_error(key, str(e))
            return False

    def subscribe(self, key: str, callback: Callable[[DataChangeEvent], None]) -> None:
        """订阅数据变化

        Args:
            key: 数据键
            callback: 回调函数
        """
        try:
            with self._lock:
                self._subscribers[key].add(callback)
                self._logger.debug(f"订阅数据变化: {key}")

        except Exception as e:
            self._logger.error(f"订阅失败 [{key}]: {e}")

    def unsubscribe(
        self, key: str, callback: Callable[[DataChangeEvent], None]
    ) -> None:
        """取消订阅数据变化

        Args:
            key: 数据键
            callback: 回调函数
        """
        try:
            with self._lock:
                if key in self._subscribers:
                    self._subscribers[key].discard(callback)
                    self._logger.debug(f"取消订阅数据变化: {key}")

        except Exception as e:
            self._logger.error(f"取消订阅失败 [{key}]: {e}")

    def subscribe_global(self, callback: Callable[[DataChangeEvent], None]) -> None:
        """订阅所有数据变化

        Args:
            callback: 回调函数
        """
        try:
            with self._lock:
                self._global_subscribers.add(callback)
                self._logger.debug("订阅全局数据变化")

        except Exception as e:
            self._logger.error(f"全局订阅失败: {e}")

    def unsubscribe_global(self, callback: Callable[[DataChangeEvent], None]) -> None:
        """取消订阅所有数据变化

        Args:
            callback: 回调函数
        """
        try:
            with self._lock:
                self._global_subscribers.discard(callback)
                self._logger.debug("取消订阅全局数据变化")

        except Exception as e:
            self._logger.error(f"取消全局订阅失败: {e}")

    def set_validator(self, key: str, validator: DataValidator) -> None:
        """设置数据验证器

        Args:
            key: 数据键
            validator: 验证器
        """
        with self._lock:
            self._validators[key] = validator
            self._logger.debug(f"设置数据验证器: {key}")

    def remove_validator(self, key: str) -> None:
        """移除数据验证器

        Args:
            key: 数据键
        """
        with self._lock:
            if key in self._validators:
                del self._validators[key]
                self._logger.debug(f"移除数据验证器: {key}")

    def _validate_data(self, key: str, value: Any) -> bool:
        """验证数据"""
        try:
            if key in self._validators:
                validator = self._validators[key]
                return validator.validate(key, value)
            return True

        except Exception as e:
            self._logger.error(f"数据验证失败 [{key}]: {e}")
            return False

    def _transform_data(self, key: str, value: Any) -> Any:
        """转换数据"""
        try:
            if key in self._validators:
                validator = self._validators[key]
                return validator.transform(key, value)
            return value

        except Exception as e:
            self._logger.error(f"数据转换失败 [{key}]: {e}")
            raise

    def _notify_subscribers(self, event: DataChangeEvent) -> None:
        """通知订阅者"""
        try:
            # 通知特定键的订阅者
            if event.key in self._subscribers:
                for callback in self._subscribers[event.key].copy():
                    try:
                        callback(event)
                    except Exception as e:
                        self._logger.error(f"订阅者回调失败 [{event.key}]: {e}")

            # 通知全局订阅者
            for callback in self._global_subscribers.copy():
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"全局订阅者回调失败: {e}")

            # 发送回调信号
            self._emit_data_changed(event)

        except Exception as e:
            self._logger.error(f"通知订阅者失败: {e}")

    def _add_to_history(self, event: DataChangeEvent) -> None:
        """添加到历史记录"""
        try:
            self._change_history.append(event)

            # 限制历史记录大小
            if len(self._change_history) > self._max_history_size:
                self._change_history.pop(0)

        except Exception as e:
            self._logger.error(f"添加历史记录失败: {e}")

    def get_change_history(self, key: str | None = None) -> list[DataChangeEvent]:
        """获取变化历史

        Args:
            key: 数据键,如果为None则返回所有历史

        Returns:
            List[DataChangeEvent]: 变化历史列表
        """
        with self._lock:
            if key is None:
                return self._change_history.copy()
            return [event for event in self._change_history if event.key == key]

    def clear_history(self) -> None:
        """清空变化历史"""
        with self._lock:
            self._change_history.clear()
            self._logger.debug("变化历史已清空")

    def get_all_keys(self) -> list[str]:
        """获取所有数据键"""
        with self._lock:
            return list(self._data.keys())

    def get_all_data(self) -> dict[str, Any]:
        """获取所有数据"""
        with self._lock:
            return self._data.copy()

    def clear_all_data(self, notify: bool = True) -> None:
        """清空所有数据

        Args:
            notify: 是否发送通知
        """
        try:
            with self._lock:
                keys_to_delete = list(self._data.keys())

                for key in keys_to_delete:
                    self.delete_data(key, source="clear_all", notify=notify)

                self._logger.debug("所有数据已清空")

        except Exception as e:
            self._logger.error(f"清空数据失败: {e}")

    def refresh_data(self, key: str, source: str | None = None) -> None:
        """刷新数据(发送刷新事件)

        Args:
            key: 数据键
            source: 数据来源
        """
        try:
            with self._lock:
                if key in self._data:
                    value = self._data[key]

                    # 创建刷新事件
                    event = DataChangeEvent(
                        key=key,
                        change_type=DataChangeType.REFRESHED,
                        old_value=value,
                        new_value=value,
                        source=source,
                    )

                    # 添加到历史记录
                    self._add_to_history(event)

                    # 发送通知
                    self._notify_subscribers(event)

                    self._logger.debug(f"数据刷新: {key}")

        except Exception as e:
            self._logger.error(f"数据刷新失败 [{key}]: {e}")

    def batch_update(
        self, updates: dict[str, Any], source: str | None = None, notify: bool = True
    ) -> bool:
        """批量更新数据

        Args:
            updates: 更新数据字典
            source: 数据来源
            notify: 是否发送通知

        Returns:
            bool: 是否全部更新成功
        """
        try:
            success_count = 0

            for key, value in updates.items():
                if self.set_data(key, value, source=source, notify=False):
                    success_count += 1

            # 批量通知
            if notify:
                for key in updates:
                    if key in self._data:
                        self.refresh_data(key, source=source)

            self._logger.debug(f"批量更新完成: {success_count}/{len(updates)}")
            return success_count == len(updates)

        except Exception as e:
            self._logger.error(f"批量更新失败: {e}")
            return False


# 为了兼容性,创建一个别名
DataBus = DataBusTTK

# 全局数据总线实例
_global_data_bus: DataBusTTK | None = None


def get_data_bus() -> DataBusTTK:
    """获取全局数据总线实例"""
    global _global_data_bus
    if _global_data_bus is None:
        _global_data_bus = DataBusTTK()
    return _global_data_bus


def set_global_data_bus(data_bus: DataBusTTK) -> None:
    """设置全局数据总线实例"""
    global _global_data_bus
    _global_data_bus = data_bus


# 便捷函数
def set_shared_data(key: str, value: Any, source: str | None = None) -> bool:
    """设置共享数据"""
    return get_data_bus().set_data(key, value, source=source)


def get_shared_data(key: str, default: Any = None) -> Any:
    """获取共享数据"""
    return get_data_bus().get_data(key, default=default)


def subscribe_data_change(
    key: str, callback: Callable[[DataChangeEvent], None]
) -> None:
    """订阅数据变化"""
    get_data_bus().subscribe(key, callback)


def unsubscribe_data_change(
    key: str, callback: Callable[[DataChangeEvent], None]
) -> None:
    """取消订阅数据变化"""
    get_data_bus().unsubscribe(key, callback)
