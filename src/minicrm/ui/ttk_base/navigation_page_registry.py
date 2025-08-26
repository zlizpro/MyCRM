"""MiniCRM TTK页面注册配置模块.

定义所有TTK系统页面的注册配置, 提供统一的页面注册接口.

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging

from minicrm.core.exceptions import UIError
from minicrm.ui.panels.customer_panel_ttk import CustomerPanelTTK
from minicrm.ui.panels.supplier_panel_ttk import SupplierPanelTTK
from minicrm.ui.settings_panel import SettingsPanel
from minicrm.ui.ttk_base.contract_panel_ttk import ContractPanelTTK
from minicrm.ui.ttk_base.finance_panel_ttk import FinancePanelTTK
from minicrm.ui.ttk_base.import_export_panel_ttk import ImportExportPanelTTK
from minicrm.ui.ttk_base.navigation_item_ttk import NavigationItemTTK
from minicrm.ui.ttk_base.navigation_registry_ttk_fixed import NavigationRegistryTTK
from minicrm.ui.ttk_base.quote_panel_ttk import QuotePanelTTK
from minicrm.ui.ttk_base.task_panel_ttk import TaskPanelTTK


def register_all_ttk_pages(registry: NavigationRegistryTTK) -> None:
    """注册所有TTK系统页面.

    Args:
        registry: TTK导航注册系统实例
    """
    logger = logging.getLogger(__name__)
    logger.info("开始注册所有TTK系统页面...")

    try:
        # 1. 仪表盘页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="dashboard",
                title="仪表盘",
                icon="📊",
                widget_class=DashboardComplete,
                order=1,
                requires_service="analytics",
                description="系统概览和关键指标",
                route_path="/dashboard",
                cache_enabled=True,
                preload=True,
            )
        )

        # 2. 客户管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="customers",
                title="客户管理",
                icon="👥",
                widget_class=CustomerPanelTTK,
                order=2,
                requires_service="customer",
                description="客户信息管理和维护",
                route_path="/customers",
                cache_enabled=True,
                preload=True,
            )
        )

        # 3. 供应商管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="suppliers",
                title="供应商管理",
                icon="🏭",
                widget_class=SupplierPanelTTK,
                order=3,
                requires_service="supplier",
                description="供应商信息和质量管理",
                route_path="/suppliers",
                cache_enabled=True,
                preload=True,
            )
        )

        # 4. 财务管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="finance",
                title="财务管理",
                icon="💰",
                widget_class=FinancePanelTTK,
                order=4,
                requires_service="finance",
                description="财务数据和报表管理",
                route_path="/finance",
                cache_enabled=True,
            )
        )

        # 5. 合同管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="contracts",
                title="合同管理",
                icon="📄",
                widget_class=ContractPanelTTK,
                order=5,
                requires_service="contract",
                description="合同信息和状态管理",
                route_path="/contracts",
                cache_enabled=True,
            )
        )

        # 6. 报价管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="quotes",
                title="报价管理",
                icon="💼",
                widget_class=QuotePanelTTK,
                order=6,
                requires_service="quote",
                description="报价创建和历史管理",
                route_path="/quotes",
                cache_enabled=True,
            )
        )

        # 7. 任务管理页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="tasks",
                title="任务管理",
                icon="📋",
                widget_class=TaskPanelTTK,
                order=7,
                requires_service="task",
                description="任务和提醒管理",
                route_path="/tasks",
                cache_enabled=True,
            )
        )

        # 8. 数据导入导出页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="import_export",
                title="数据管理",
                icon="📤",
                widget_class=ImportExportPanelTTK,
                order=8,
                requires_service="import_export",
                description="数据导入导出功能",
                route_path="/data",
                cache_enabled=False,  # 导入导出不需要缓存
            )
        )

        # 9. 系统设置页面
        registry.register_navigation_item(
            NavigationItemTTK(
                name="settings",
                title="系统设置",
                icon="⚙️",
                widget_class=SettingsPanel,
                order=9,
                description="系统配置和偏好设置",
                route_path="/settings",
                cache_enabled=False,
            )
        )

        logger.info("所有TTK系统页面注册完成")

    except Exception as e:
        error_msg = "TTK页面注册失败"
        logger.exception("TTK页面注册过程中发生错误: %s", e)
        raise UIError(error_msg, "NavigationPageRegistry") from e
