"""MiniCRM TTK导航项配置模块.

定义TTK导航系统中的导航项配置类, 提供统一的导航项管理接口.

作者: MiniCRM开发团队
"""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from typing import Any


class NavigationItemTTK:
    """TTK导航项配置类."""

    def __init__(
        self,
        name: str,
        title: str,
        icon: str,
        widget_class: type[tk.Widget] | None = None,
        factory: Callable[[], tk.Widget] | None = None,
        parent: str | None = None,
        order: int = 0,
        visible: bool = True,
        requires_service: str | None = None,
        description: str | None = None,
        route_path: str | None = None,
        cache_enabled: bool = True,
        preload: bool = False,
        init_args: tuple = (),
        init_kwargs: dict[str, Any] | None = None,
    ):
        """初始化TTK导航项.

        Args:
            name: 页面名称(唯一标识)
            title: 显示标题
            icon: 图标名称或路径
            widget_class: 页面组件类
            factory: 页面创建工厂函数
            parent: 父页面名称
            order: 排序顺序
            visible: 是否可见
            requires_service: 需要的服务名称
            description: 描述信息
            route_path: 路由路径
            cache_enabled: 是否启用缓存
            preload: 是否预加载
            init_args: 初始化参数
            init_kwargs: 初始化关键字参数
        """
        self.name = name
        self.title = title
        self.icon = icon
        self.widget_class = widget_class
        self.factory = factory
        self.parent = parent
        self.order = order
        self.visible = visible
        self.requires_service = requires_service
        self.description = description
        self.route_path = route_path or f"/{name}"
        self.cache_enabled = cache_enabled
        self.preload = preload
        self.init_args = init_args
        self.init_kwargs = init_kwargs or {}
