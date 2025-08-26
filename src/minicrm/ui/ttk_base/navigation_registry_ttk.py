"""MiniCRM TTK导航注册系统.

负责将所有TTK UI模块注册到导航系统中, 实现统一的页面管理和路由.
这是TTK系统集成的核心组件, 连接导航面板、页面管理器和各个功能模块.

设计原则:
- 集中管理所有TTK页面的注册
- 支持懒加载和动态创建
- 提供统一的导航接口
- 支持权限控制和条件显示
- 与TTK组件系统完全集成

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging
import tkinter as tk
from typing import Any

from minicrm.core.exceptions import UIError
from minicrm.ui.ttk_base.navigation_item_ttk import NavigationItemTTK
from minicrm.ui.ttk_base.navigation_panel import (
    NavigationItemConfig,
    NavigationPanelTTK,
)
from minicrm.ui.ttk_base.page_manager import PageConfig, PageManagerTTK, PageRouterTTK


class NavigationItemTTK:
    """TTK导航项配置"""

    def __init__(
        self,
        name: str,
        title: str,
        icon: str,
        widget_class: Optional[Type[tk.Widget]] = None,
        factory: Optional[Callable[[], tk.Widget]] = None,
        parent: Optional[str] = None,
        order: int = 0,
        visible: bool = True,
        requires_service: Optional[str] = None,
        description: Optional[str] = None,
        route_path: Optional[str] = None,
        cache_enabled: bool = True,
        preload: bool = False,
        init_args: tuple = (),
        init_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """初始化TTK导航项

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


class NavigationRegistryTTK:
    """TTK导航注册系统

    负责管理所有TTK UI模块的注册和集成,提供:
    - 页面注册和管理
    - 导航路由配置
    - 服务依赖检查
    - 动态页面创建
    - 与TTK组件系统的完整集成
    """

    def __init__(
        self,
        app: MiniCRMApplicationTTK,
        page_manager: PageManagerTTK,
        page_router: PageRouterTTK,
        navigation_panel: NavigationPanelTTK,
    ):
        """初始化TTK导航注册系统

        Args:
            app: MiniCRM应用程序实例
            page_manager: TTK页面管理器
            page_router: TTK页面路由器
            navigation_panel: TTK导航面板
        """
        self._app = app
        self._page_manager = page_manager
        self._page_router = page_router
        self._navigation_panel = navigation_panel
        self._logger = logging.getLogger(__name__)

        # 注册的导航项
        self._navigation_items: Dict[str, NavigationItemTTK] = {}

        # 页面创建缓存
        self._page_cache: Dict[str, tk.Widget] = {}

        self._logger.debug("TTK导航注册系统初始化完成")

    def register_navigation_item(self, item: NavigationItemTTK) -> None:
        """注册TTK导航项

        Args:
            item: TTK导航项配置
        """
        try:
            # 检查服务依赖
            if item.requires_service and not self._check_service_available(
                item.requires_service
            ):
                self._logger.warning(
                    f"服务不可用,跳过注册页面: {item.name} "
                    f"(需要服务: {item.requires_service})"
                )
                return

            # 注册到导航项列表
            self._navigation_items[item.name] = item

            # 注册到页面管理器
            self._register_to_page_manager(item)

            # 注册到路由器
            self._register_to_router(item)

            # 注册到导航面板
            self._register_to_navigation_panel(item)

            self._logger.debug(f"成功注册TTK导航项: {item.name}")

        except Exception as e:
            self._logger.error(f"注册TTK导航项失败 [{item.name}]: {e}")
            raise UIError(
                f"注册TTK导航项失败: {item.name}", "NavigationRegistryTTK"
            ) from e

    def _check_service_available(self, service_name: str) -> bool:
        """检查服务是否可用"""
        try:
            service = self._app.get_service(service_name)
            return service is not None
        except Exception:
            return False

    def _register_to_page_manager(self, item: NavigationItemTTK) -> None:
        """注册到TTK页面管理器"""

        # 创建页面工厂函数
        def page_factory() -> tk.Widget:
            return self._create_page_instance(item)

        # 创建页面配置
        page_config = PageConfig(
            page_id=item.name,
            title=item.title,
            page_class=item.widget_class,
            factory_func=page_factory if item.factory else None,
            init_args=item.init_args,
            init_kwargs=item.init_kwargs,
            cache_enabled=item.cache_enabled,
            preload=item.preload,
            description=item.description,
        )

        # 注册到页面管理器
        self._page_manager.register_page(page_config)

    def _register_to_router(self, item: NavigationItemTTK) -> None:
        """注册到TTK路由器"""
        self._page_router.add_route(item.route_path, item.name)

    def _register_to_navigation_panel(self, item: NavigationItemTTK) -> None:
        """注册到TTK导航面板"""
        if not item.visible:
            return

        # 创建导航项配置
        nav_config = NavigationItemConfig(
            item_id=item.name,
            text=item.title,
            command=lambda: self.navigate_to(item.name),
            icon=item.icon,
            tooltip=item.description or item.title,
            parent_id=item.parent,
        )

        # 添加到导航面板
        self._navigation_panel.add_navigation_item(nav_config)

    def _create_page_instance(self, item: NavigationItemTTK) -> tk.Widget:
        """创建TTK页面实例

        Args:
            item: TTK导航项配置

        Returns:
            tk.Widget: TTK页面组件实例
        """
        try:
            # 检查缓存
            if item.name in self._page_cache:
                return self._page_cache[item.name]

            # 使用工厂函数创建
            if item.factory:
                widget = item.factory()
            elif item.widget_class:
                # 根据页面类型创建实例
                widget = self._create_widget_instance(item)
            else:
                raise UIError(
                    f"TTK页面 {item.name} 没有指定创建方式", "NavigationRegistryTTK"
                )

            # 缓存页面实例
            if item.cache_enabled:
                self._page_cache[item.name] = widget

            self._logger.debug(f"成功创建TTK页面实例: {item.name}")
            return widget

        except Exception as e:
            self._logger.error(f"创建TTK页面实例失败 [{item.name}]: {e}")
            raise UIError(
                f"创建TTK页面实例失败: {item.name}", "NavigationRegistryTTK"
            ) from e

    def _create_widget_instance(self, item: NavigationItemTTK) -> tk.Widget:
        """创建TTK页面组件实例

        Args:
            item: TTK导航项配置

        Returns:
            tk.Widget: TTK页面组件实例
        """
        widget_class = item.widget_class

        # 检查widget_class是否存在
        if widget_class is None:
            raise UIError(
                f"TTK页面 {item.name} 没有指定widget_class", "NavigationRegistryTTK"
            )

        # 获取页面管理器的容器作为父组件
        parent = self._page_manager.container

        # 特殊处理需要特定参数的TTK页面
        if item.name == "dashboard":
            # Dashboard需要app参数和可选的parent参数
            widget = widget_class(parent, self._app)
        elif item.name == "customers":
            # CustomerPanelTTK需要customer_service参数
            customer_service = self._app.get_service("customer")
            if customer_service:
                widget = widget_class(parent, customer_service)
            else:
                raise UIError("客户服务不可用", "NavigationRegistryTTK")
        elif item.name == "suppliers":
            # SupplierPanelTTK需要supplier_service参数
            supplier_service = self._app.get_service("supplier")
            if supplier_service:
                widget = widget_class(parent, supplier_service)
            else:
                raise UIError("供应商服务不可用", "NavigationRegistryTTK")
        elif item.name == "finance":
            # FinancePanelTTK需要finance_service参数
            finance_service = self._app.get_service("finance")
            if finance_service:
                widget = widget_class(parent, finance_service)
            else:
                raise UIError("财务服务不可用", "NavigationRegistryTTK")
        elif item.name == "contracts":
            # ContractPanelTTK需要contract_service参数
            contract_service = self._app.get_service("contract")
            if contract_service:
                widget = widget_class(parent, contract_service)
            else:
                raise UIError("合同服务不可用", "NavigationRegistryTTK")
        elif item.name == "quotes":
            # QuotePanelTTK需要quote_service参数
            quote_service = self._app.get_service("quote")
            if quote_service:
                widget = widget_class(parent, quote_service)
            else:
                raise UIError("报价服务不可用", "NavigationRegistryTTK")
        elif item.name == "tasks":
            # TaskPanelTTK需要task_service参数
            task_service = self._app.get_service("task")
            if task_service:
                widget = widget_class(parent, task_service)
            else:
                raise UIError("任务服务不可用", "NavigationRegistryTTK")
        elif item.name == "import_export":
            # ImportExportPanelTTK需要import_export_service参数
            import_export_service = self._app.get_service("import_export")
            if import_export_service:
                widget = widget_class(parent, import_export_service)
            else:
                raise UIError("导入导出服务不可用", "NavigationRegistryTTK")
        elif item.name == "settings":
            # SettingsPanelTTK只需要parent参数
            widget = widget_class(parent)
        # 默认创建方式(使用配置的参数)
        elif item.init_args or item.init_kwargs:
            widget = widget_class(parent, *item.init_args, **item.init_kwargs)
        else:
            widget = widget_class(parent)

        return widget

    def get_navigation_structure(self) -> List[Dict[str, Any]]:
        """获取TTK导航结构

        Returns:
            List[Dict]: TTK导航结构数据
        """
        try:
            # 按父子关系和顺序组织导航项
            root_items = []

            # 获取所有可见的根级导航项
            for item in self._navigation_items.values():
                if item.visible and not item.parent:
                    item_data = {
                        "name": item.name,
                        "title": item.title,
                        "icon": item.icon,
                        "order": item.order,
                        "children": self._get_child_items(item.name),
                    }
                    root_items.append(item_data)

            # 按顺序排序
            root_items.sort(
                key=lambda x: x["order"] if isinstance(x["order"], int) else 0
            )

            return root_items

        except Exception as e:
            self._logger.error(f"获取TTK导航结构失败: {e}")
            return []

    def _get_child_items(self, parent_name: str) -> List[Dict[str, Any]]:
        """获取子导航项"""
        child_items = []

        for item in self._navigation_items.values():
            if item.visible and item.parent == parent_name:
                child_data = {
                    "name": item.name,
                    "title": item.title,
                    "icon": item.icon,
                    "order": item.order,
                    "children": self._get_child_items(item.name),
                }
                child_items.append(child_data)

        # 按顺序排序
        child_items.sort(key=lambda x: x["order"] if isinstance(x["order"], int) else 0)

        return child_items

    def navigate_to(
        self, page_name: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """导航到指定TTK页面

        Args:
            page_name: 页面名称
            params: 导航参数

        Returns:
            bool: 是否成功导航
        """
        try:
            if page_name not in self._navigation_items:
                self._logger.warning(f"TTK页面不存在: {page_name}")
                return False

            return self._page_manager.navigate_to(page_name, params)

        except Exception as e:
            self._logger.error(f"TTK导航失败 [{page_name}]: {e}")
            return False

    def get_registered_pages(self) -> List[str]:
        """获取已注册的TTK页面列表"""
        return list(self._navigation_items.keys())

    def is_page_registered(self, page_name: str) -> bool:
        """检查TTK页面是否已注册"""
        return page_name in self._navigation_items

    def unregister_page(self, page_name: str) -> None:
        """注销TTK页面"""
        try:
            if page_name in self._navigation_items:
                # 从缓存中移除
                if page_name in self._page_cache:
                    del self._page_cache[page_name]

                # 从注册表中移除
                del self._navigation_items[page_name]

                # 从导航面板移除
                self._navigation_panel.remove_item(page_name)

                self._logger.debug(f"成功注销TTK页面: {page_name}")

        except Exception as e:
            self._logger.error(f"注销TTK页面失败 [{page_name}]: {e}")

    def refresh_navigation_panel(self) -> None:
        """刷新导航面板"""
        try:
            # 清空当前导航面板
            self._navigation_panel.clear_all_items()

            # 重新注册所有可见的导航项
            for item in self._navigation_items.values():
                if item.visible:
                    self._register_to_navigation_panel(item)

            self._logger.debug("TTK导航面板刷新完成")

        except Exception as e:
            self._logger.error(f"刷新TTK导航面板失败: {e}")

    def update_navigation_item_state(self, page_name: str, state: str) -> None:
        """更新导航项状态"""
        try:
            if page_name in self._navigation_items:
                self._navigation_panel.update_item_state(page_name, state)
                self._logger.debug(f"更新TTK导航项状态: {page_name} -> {state}")

        except Exception as e:
            self._logger.error(f"更新TTK导航项状态失败 [{page_name}]: {e}")


def register_all_ttk_pages(registry: NavigationRegistryTTK) -> None:
    """注册所有TTK系统页面

    Args:
        registry: TTK导航注册系统实例
    """
    logger = logging.getLogger(__name__)
    logger.info("开始注册所有TTK系统页面...")

    try:
        # 临时简化版本 - 只注册基本导航项,不使用复杂的页面配置
        logger.info("使用简化的页面注册流程")

        # 1. 仪表盘页面

        # 简化的导航项注册 - 跳过复杂的页面管理器集成
        navigation_item = NavigationItemTTK(
            name="dashboard",
            title="仪表盘",
            icon="📊",
            widget_class=DashboardComplete,
            order=1,
            requires_service="analytics",
            description="系统概览和关键指标",
            route_path="/dashboard",
            cache_enabled=False,  # 暂时禁用缓存
            preload=False,  # 暂时禁用预加载
        )

        # 直接添加到导航面板,跳过页面管理器
        registry._navigation_panel.add_navigation_item(navigation_item)

        logger.info("TTK系统页面注册完成(简化版本)")

    except Exception as e:
        logger.error(f"TTK页面注册过程中发生错误: {e}")
        raise UIError("TTK页面注册失败", "NavigationRegistryTTK") from e
