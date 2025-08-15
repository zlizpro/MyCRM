"""
MiniCRM 页面管理基础组件

包含页面基类、数据类和基础功能
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from PySide6.QtWidgets import QWidget


@dataclass
class PageInfo:
    """页面信息数据类"""

    name: str
    title: str
    widget_class: type[QWidget]
    parent_page: str | None = None
    icon: str | None = None
    description: str | None = None
    requires_auth: bool = False
    lazy_load: bool = True
    init_args: dict[str, Any] = field(default_factory=dict)
    init_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class NavigationHistory:
    """导航历史记录"""

    page_name: str
    timestamp: float
    params: dict[str, Any] = field(default_factory=dict)


class BasePage(QWidget):
    """
    页面基类

    提供标准的页面生命周期方法和通用功能
    """

    def __init__(self, parent: QWidget | None = None):
        """初始化页面"""
        super().__init__(parent)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._is_initialized = False

    def on_page_enter(self, params: dict[str, Any] | None = None) -> None:
        """
        页面进入时调用

        Args:
            params: 页面参数
        """
        if not self._is_initialized:
            self._initialize_page()
            self._is_initialized = True

        self._on_page_enter(params or {})

    def on_page_leave(self) -> None:
        """页面离开时调用"""
        self._on_page_leave()

    def refresh(self) -> None:
        """刷新页面"""
        self._refresh_page()

    def cleanup(self) -> None:
        """清理页面资源"""
        self._cleanup_page()

    # 子类需要重写的方法
    def _initialize_page(self) -> None:
        """初始化页面（子类重写）"""
        pass

    def _on_page_enter(self, params: dict[str, Any]) -> None:
        """页面进入处理（子类重写）"""
        pass

    def _on_page_leave(self) -> None:
        """页面离开处理（子类重写）"""
        pass

    def _refresh_page(self) -> None:
        """刷新页面处理（子类重写）"""
        pass

    def _cleanup_page(self) -> None:
        """清理页面处理（子类重写）"""
        pass
