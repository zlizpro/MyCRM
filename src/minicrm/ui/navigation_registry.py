"""MiniCRM 导航注册系统.

负责将所有UI模块注册到导航系统中, 实现统一的页面管理和路由.
这是系统集成的核心组件, 连接导航面板、页面管理器和各个功能模块.

设计原则:
- 集中管理所有页面的注册
- 支持懒加载和动态创建
- 提供统一的导航接口
- 支持权限控制和条件显示
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable

    from minicrm.application import MiniCRMApplication
    from minicrm.ui.page_management import PageManager, PageRouter

# 导入所有需要的组件类
from minicrm.core.exceptions import UIError
from minicrm.ui.contract_panel import ContractPanel
from minicrm.ui.dashboard import Dashboard
from minicrm.ui.data_bus import get_data_bus
from minicrm.ui.panels.customer_panel_ttk import CustomerPanelTTK
from minicrm.ui.quote_panel import QuotePanel
from minicrm.ui.settings_panel import SettingsPanel
from minicrm.ui.supplier_panel import SupplierPanel
from minicrm.ui.ttk_base.finance_panel_ttk import FinancePanelTTK
from minicrm.ui.ttk_base.import_export_panel_ttk import ImportExportPanelTTK
from minicrm.ui.ttk_base.task_panel_ttk import TaskPanelTTK


class NavigationItem:
    """导航项配置."""

    def __init__(
        self,
        name: str,
        title: str,
        icon: str,
        widget_class: type[Any] | None = None,
        factory: Callable[[], Any] | None = None,
        parent: str | None = None,
        order: int = 0,
        visible: bool = True,
        requires_service: str | None = None,
        description: str | None = None,
        route_path: str | None = None,
    ):
        """初始化导航项.

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


class NavigationRegistry:
    """导航注册系统.

    负责管理所有UI模块的注册和集成, 提供:
    - 页面注册和管理
    - 导航路由配置
    - 服务依赖检查
    - 动态页面创建
    """

    def __init__(
        self,
        app: MiniCRMApplication,
        page_manager: PageManager,
        page_router: PageRouter,
    ):
        """初始化导航注册系统.

        Args:
            app: MiniCRM应用程序实例
            page_manager: 页面管理器
            page_router: 页面路由器
        """
        self._app = app
        self._page_manager = page_manager
        self._page_router = page_router
        self._logger = logging.getLogger(__name__)

        # 注册的导航项
        self._navigation_items: dict[str, NavigationItem] = {}

        # 页面创建缓存
        self._page_cache: dict[str, Any] = {}

        self._logger.debug("导航注册系统初始化完成")

    def _raise_no_creation_method_error(self, item_name: str) -> None:
        """抛出没有指定创建方式的错误."""
        error_msg = f"页面 {item_name} 没有指定创建方式"
        raise UIError(error_msg, "NavigationRegistry")

    def register_navigation_item(self, item: NavigationItem) -> None:
        """注册导航项.

        Args:
            item: 导航项配置
        """
        try:
            # 检查服务依赖
            if item.requires_service and not self._check_service_available(
                item.requires_service
            ):
                warning_msg = "服务不可用, 跳过注册页面: %s (需要服务: %s)"
                self._logger.warning(warning_msg, item.name, item.requires_service)
                return

            # 注册到导航项列表
            self._navigation_items[item.name] = item

            # 注册到页面管理器
            self._register_to_page_manager(item)

            # 注册到路由器
            self._register_to_router(item)

            self._logger.debug("成功注册导航项: %s", item.name)

        except Exception:
            self._logger.exception("注册导航项失败 [%s]", item.name)
            error_msg = f"注册导航项失败: {item.name}"
            raise UIError(error_msg, "NavigationRegistry") from None

    def _check_service_available(self, service_name: str) -> bool:
        """检查服务是否可用."""
        try:
            service = self._app.get_service(service_name)
        except (AttributeError, KeyError, ValueError):
            return False
        else:
            return service is not None

    def _register_to_page_manager(self, item: NavigationItem) -> None:
        """注册到页面管理器."""

        # 创建页面工厂函数
        def page_factory() -> Any:  # noqa: ANN401
            return self._create_page_instance(item)

        # 使用页面工厂注册方法
        self._page_manager.register_page_factory(
            name=item.name,
            title=item.title,
            factory_func=page_factory,
            parent_page=item.parent,
            icon=item.icon,
            description=item.description,
            requires_auth=False,
        )

    def _register_to_router(self, item: NavigationItem) -> None:
        """注册到路由器."""
        self._page_router.add_route(item.route_path, item.name)

    def _create_page_instance(self, item: NavigationItem) -> Any:  # noqa: ANN401
        """创建页面实例.

        Args:
            item: 导航项配置

        Returns:
            tk.Widget: 页面组件实例
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
                self._raise_no_creation_method_error(item.name)

            # 为页面设置数据总线访问
            if hasattr(widget, "set_data_bus"):
                data_bus = get_data_bus()
                widget.set_data_bus(data_bus)

            # 缓存页面实例
            self._page_cache[item.name] = widget

            self._logger.debug("成功创建页面实例: %s", item.name)
        except Exception:
            self._logger.exception("创建页面实例失败 [%s]", item.name)
            error_msg = f"创建页面实例失败: {item.name}"
            raise UIError(error_msg, "NavigationRegistry") from None
        else:
            return widget

    def _create_widget_instance(self, item: NavigationItem) -> Any:  # noqa: ANN401
        """创建页面组件实例.

        Args:
            item: 导航项配置

        Returns:
            tk.Widget: 页面组件实例
        """
        widget_class = item.widget_class

        # 检查widget_class是否存在
        if widget_class is None:
            error_msg = f"页面 {item.name} 没有指定widget_class"
            raise UIError(error_msg, "NavigationRegistry")

        # 特殊处理需要特定参数的页面
        if item.name == "dashboard":
            # Dashboard需要app参数和可选的parent参数
            widget = widget_class(self._app, None)
        elif item.name == "customers":
            # CustomerPanelTTK需要parent和customer_service参数
            customer_service = self._app.get_service("customer")
            if customer_service:
                widget = widget_class(parent=None, customer_service=customer_service)
            else:
                error_msg = "客户服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "suppliers":
            # SupplierPanel需要supplier_service参数
            supplier_service = self._app.get_service("supplier")
            if supplier_service:
                widget = widget_class(supplier_service)
            else:
                error_msg = "供应商服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "finance":
            # FinancePanelTTK需要parent和finance_service参数
            finance_service = self._app.get_service("finance")
            if finance_service:
                widget = widget_class(parent=None, finance_service=finance_service)
            else:
                error_msg = "财务服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "contracts":
            # ContractPanel需要contract_service参数
            contract_service = self._app.get_service("contract")
            if contract_service:
                widget = widget_class(contract_service)
            else:
                error_msg = "合同服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "quotes":
            # QuotePanel需要quote_service参数
            quote_service = self._app.get_service("quote")
            if quote_service:
                widget = widget_class(quote_service)
            else:
                error_msg = "报价服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "tasks":
            # TaskPanelTTK需要parent和interaction_service参数
            interaction_service = self._app.get_service("interaction")
            if interaction_service:
                widget = widget_class(
                    parent=None, interaction_service=interaction_service
                )
            else:
                error_msg = "互动服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "import_export":
            import_export_service = self._app.get_service("import_export")
            if import_export_service:
                widget = widget_class(
                    parent=None, import_export_service=import_export_service
                )
            else:
                error_msg = "导入导出服务不可用"
                raise UIError(error_msg, "NavigationRegistry")
        elif item.name == "settings":
            widget = widget_class()
        else:
            widget = widget_class()

        return widget

    def get_navigation_structure(self) -> list[dict[str, Any]]:
        """获取导航结构.

        Returns:
            List[Dict]: 导航结构数据
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
        except Exception:
            self._logger.exception("获取导航结构失败")
            return []
        else:
            return root_items

    def _get_child_items(self, parent_name: str) -> list[dict[str, Any]]:
        """获取子导航项."""
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

    def navigate_to(self, page_name: str, params: dict[str, Any] | None = None) -> bool:
        """导航到指定页面.

        Args:
            page_name: 页面名称
            params: 导航参数

        Returns:
            bool: 是否成功导航
        """
        try:
            if page_name not in self._navigation_items:
                self._logger.warning("页面不存在: %s", page_name)
                return False

            return self._page_manager.navigate_to(page_name, params)

        except Exception:
            self._logger.exception("导航失败 [%s]", page_name)
            return False

    def get_registered_pages(self) -> list[str]:
        """获取已注册的页面列表."""
        return list(self._navigation_items.keys())

    def is_page_registered(self, page_name: str) -> bool:
        """检查页面是否已注册."""
        return page_name in self._navigation_items

    def unregister_page(self, page_name: str) -> None:
        """注销页面."""
        try:
            if page_name in self._navigation_items:
                # 从缓存中移除
                if page_name in self._page_cache:
                    del self._page_cache[page_name]

                # 从注册表中移除
                del self._navigation_items[page_name]

                self._logger.debug("成功注销页面: %s", page_name)

        except Exception:
            self._logger.exception("注销页面失败 [%s]", page_name)


def register_all_pages(registry: NavigationRegistry) -> None:
    """注册所有系统页面.

    Args:
        registry: 导航注册系统实例
    """
    logger = logging.getLogger(__name__)
    logger.info("开始注册所有系统页面...")

    try:
        # 1. 仪表盘页面
        registry.register_navigation_item(
            NavigationItem(
                name="dashboard",
                title="仪表盘",
                icon="📊",
                widget_class=Dashboard,
                order=1,
                requires_service="analytics",
                description="系统概览和关键指标",
                route_path="/dashboard",
            )
        )

        # 2. 客户管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="customers",
                title="客户管理",
                icon="👥",
                widget_class=CustomerPanelTTK,
                order=2,
                requires_service="customer",
                description="客户信息管理和维护",
                route_path="/customers",
            )
        )

        # 3. 供应商管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="suppliers",
                title="供应商管理",
                icon="🏭",
                widget_class=SupplierPanel,
                order=3,
                requires_service="supplier",
                description="供应商信息和质量管理",
                route_path="/suppliers",
            )
        )

        # 4. 财务管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="finance",
                title="财务管理",
                icon="💰",
                widget_class=FinancePanelTTK,
                order=4,
                requires_service="finance",
                description="财务数据和报表管理",
                route_path="/finance",
            )
        )

        # 5. 合同管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="contracts",
                title="合同管理",
                icon="📄",
                widget_class=ContractPanel,
                order=5,
                description="合同信息和状态管理",
                route_path="/contracts",
            )
        )

        # 6. 报价管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="quotes",
                title="报价管理",
                icon="💼",
                widget_class=QuotePanel,
                order=6,
                description="报价创建和历史管理",
                route_path="/quotes",
            )
        )

        # 7. 任务管理页面
        registry.register_navigation_item(
            NavigationItem(
                name="tasks",
                title="任务管理",
                icon="📋",
                widget_class=TaskPanelTTK,
                order=7,
                description="任务和提醒管理",
                route_path="/tasks",
            )
        )

        # 8. 数据导入导出页面
        registry.register_navigation_item(
            NavigationItem(
                name="import_export",
                title="数据管理",
                icon="📤",
                widget_class=ImportExportPanelTTK,
                order=8,
                description="数据导入导出功能",
                route_path="/data",
            )
        )

        # 9. 系统设置页面
        registry.register_navigation_item(
            NavigationItem(
                name="settings",
                title="系统设置",
                icon="⚙️",
                widget_class=SettingsPanel,
                order=9,
                description="系统配置和偏好设置",
                route_path="/settings",
            )
        )

        logger.info("所有系统页面注册完成")

    except Exception:
        logger.exception("页面注册过程中发生错误")
        error_msg = "页面注册失败"
        raise UIError(error_msg, "NavigationRegistry") from None
