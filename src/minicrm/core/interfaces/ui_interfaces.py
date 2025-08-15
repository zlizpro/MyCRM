"""
用户界面层接口定义

定义UI组件的接口契约，确保：
- UI组件的标准化
- 组件间的松耦合
- 易于测试和替换
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class IFormPanel(ABC):
    """表单面板接口"""

    @abstractmethod
    def set_data(self, data: dict[str, Any]) -> None:
        """
        设置表单数据

        Args:
            data: 表单数据字典
        """
        pass

    @abstractmethod
    def get_data(self) -> dict[str, Any]:
        """
        获取表单数据

        Returns:
            Dict[str, Any]: 表单数据字典
        """
        pass

    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        """
        验证表单数据

        Returns:
            Tuple[bool, List[str]]: (是否有效, 错误消息列表)
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """清空表单"""
        pass

    @abstractmethod
    def set_readonly(self, readonly: bool) -> None:
        """
        设置表单只读状态

        Args:
            readonly: 是否只读
        """
        pass


class IDataTable(ABC):
    """数据表格接口"""

    @abstractmethod
    def set_data(self, data: list[dict[str, Any]]) -> None:
        """
        设置表格数据

        Args:
            data: 数据列表
        """
        pass

    @abstractmethod
    def get_selected_rows(self) -> list[int]:
        """
        获取选中的行索引

        Returns:
            List[int]: 选中行的索引列表
        """
        pass

    @abstractmethod
    def get_selected_data(self) -> list[dict[str, Any]]:
        """
        获取选中行的数据

        Returns:
            List[Dict[str, Any]]: 选中行的数据列表
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """刷新表格数据"""
        pass

    @abstractmethod
    def set_columns(self, columns: list[dict[str, Any]]) -> None:
        """
        设置表格列配置

        Args:
            columns: 列配置列表
        """
        pass

    @abstractmethod
    def apply_filter(self, filters: dict[str, Any]) -> None:
        """
        应用筛选条件

        Args:
            filters: 筛选条件字典
        """
        pass

    @abstractmethod
    def set_page(self, page: int, page_size: int) -> None:
        """
        设置分页

        Args:
            page: 页码
            page_size: 每页大小
        """
        pass


class IDashboard(ABC):
    """仪表盘接口"""

    @abstractmethod
    def update_metrics(self, metrics: dict[str, Any]) -> None:
        """
        更新关键指标

        Args:
            metrics: 指标数据字典
        """
        pass

    @abstractmethod
    def update_charts(self, chart_data: dict[str, Any]) -> None:
        """
        更新图表数据

        Args:
            chart_data: 图表数据字典
        """
        pass

    @abstractmethod
    def refresh_all(self) -> None:
        """刷新所有仪表盘数据"""
        pass

    @abstractmethod
    def set_loading(self, loading: bool) -> None:
        """
        设置加载状态

        Args:
            loading: 是否正在加载
        """
        pass


class IUIComponent(ABC):
    """UI组件基础接口"""

    @abstractmethod
    def setup_ui(self) -> None:
        """设置用户界面"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """清理资源"""
        pass

    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """
        设置组件启用状态

        Args:
            enabled: 是否启用
        """
        pass

    @abstractmethod
    def show_message(self, message: str, message_type: str = "info") -> None:
        """
        显示消息

        Args:
            message: 消息内容
            message_type: 消息类型 ("info", "warning", "error", "success")
        """
        pass


class IEventHandler(ABC):
    """事件处理器接口"""

    @abstractmethod
    def handle_event(self, event_type: str, data: Any) -> None:
        """
        处理事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        pass

    @abstractmethod
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        注册事件回调

        Args:
            event_type: 事件类型
            callback: 回调函数
        """
        pass
