"""MiniCRM TTK页面创建工厂模块.

负责根据导航项配置创建具体的TTK页面实例, 处理不同页面类型的特殊创建逻辑.

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging
import tkinter as tk

from minicrm.application import MiniCRMApplication
from minicrm.core.exceptions import UIError
from minicrm.ui.ttk_base.navigation_item_ttk import NavigationItemTTK


class NavigationPageFactory:
    """TTK页面创建工厂类."""

    def __init__(self, app: MiniCRMApplication):
        """初始化页面工厂.

        Args:
            app: MiniCRM应用程序实例
        """
        self._app = app
        self._logger = logging.getLogger(__name__)

    def create_page_instance(
        self, item: NavigationItemTTK, parent: tk.Widget
    ) -> tk.Widget:
        """创建TTK页面实例.

        Args:
            item: TTK导航项配置
            parent: 父组件

        Returns:
            tk.Widget: TTK页面组件实例

        Raises:
            UIError: 当页面创建失败时
        """
        try:
            # 使用工厂函数创建
            if item.factory:
                return item.factory()

            if item.widget_class:
                return self._create_widget_instance(item, parent)

            error_msg = f"TTK页面 {item.name} 没有指定创建方式"
            raise UIError(error_msg, "NavigationPageFactory")

        except Exception as e:
            error_msg = f"创建TTK页面实例失败: {item.name}"
            self._logger.exception("创建TTK页面实例失败 [%s]: %s", item.name, e)
            raise UIError(error_msg, "NavigationPageFactory") from e

    def _create_widget_instance(
        self, item: NavigationItemTTK, parent: tk.Widget
    ) -> tk.Widget:
        """创建TTK页面组件实例.

        Args:
            item: TTK导航项配置
            parent: 父组件

        Returns:
            tk.Widget: TTK页面组件实例

        Raises:
            UIError: 当组件创建失败时
        """
        widget_class = item.widget_class

        # 检查widget_class是否存在
        if widget_class is None:
            error_msg = f"TTK页面 {item.name} 没有指定widget_class"
            raise UIError(error_msg, "NavigationPageFactory")

        # 特殊处理需要特定参数的TTK页面
        return self._create_specialized_widget(item, parent, widget_class)

    def _create_specialized_widget(
        self,
        item: NavigationItemTTK,
        parent: tk.Widget,
        widget_class: type[tk.Widget],
    ) -> tk.Widget:
        """创建特殊化的组件实例.

        Args:
            item: 导航项配置
            parent: 父组件
            widget_class: 组件类

        Returns:
            tk.Widget: 组件实例
        """
        # Dashboard需要app参数
        if item.name == "dashboard":
            return widget_class(parent, self._app)

        # 需要特定服务的页面
        service_mapping = {
            "customers": "customer",
            "suppliers": "supplier",
            "finance": "finance",
            "contracts": "contract",
            "quotes": "quote",
            "tasks": "task",
            "import_export": "import_export",
        }

        if item.name in service_mapping:
            service_name = service_mapping[item.name]
            service = self._app.get_service(service_name)
            if service:
                return widget_class(parent, service)

            error_msg = f"{service_name}服务不可用"
            raise UIError(error_msg, "NavigationPageFactory")

        # Settings页面只需要parent参数
        if item.name == "settings":
            return widget_class(parent)

        # 默认创建方式
        if item.init_args or item.init_kwargs:
            return widget_class(parent, *item.init_args, **item.init_kwargs)

        return widget_class(parent)
