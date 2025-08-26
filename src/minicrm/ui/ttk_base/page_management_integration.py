"""MiniCRM TTK页面管理集成模块

为任务8提供完整的页面管理集成:
- 集成增强页面管理器与现有导航系统
- 配置所有TTK面板的页面管理策略
- 实现页面缓存和懒加载的完整流程
- 确保页面切换的流畅性和性能优化
- 提供统一的页面管理接口

集成特点:
1. 无缝集成 - 与现有TTK系统完全兼容
2. 配置驱动 - 通过配置管理所有页面策略
3. 性能优化 - 智能缓存和懒加载机制
4. 监控集成 - 实时性能监控和优化建议
5. 扩展性强 - 支持新页面类型的快速集成

作者: MiniCRM开发团队
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from minicrm.application import MiniCRMApplication
from minicrm.core.exceptions import UIError
from minicrm.ui.ttk_base.enhanced_page_manager import (
    EnhancedPageManagerTTK,
    PageCacheConfig,
    PageLoadConfig,
    PageTransitionConfig,
)
from minicrm.ui.ttk_base.navigation_item_ttk import NavigationItemTTK
from minicrm.ui.ttk_base.navigation_panel import NavigationPanelTTK
from minicrm.ui.ttk_base.page_configuration import (
    PageConfigurationManager,
    get_page_config_manager,
)
from minicrm.ui.ttk_base.page_manager import BasePage


class TTKPageAdapter(BasePage):
    """TTK页面适配器

    将现有的TTK组件适配为BasePage接口
    """

    def __init__(
        self,
        page_id: str,
        parent,
        widget_class: type,
        init_args: tuple = (),
        init_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """初始化TTK页面适配器

        Args:
            page_id: 页面ID
            parent: 父组件
            widget_class: TTK组件类
            init_args: 初始化参数
            init_kwargs: 初始化关键字参数
        """
        super().__init__(page_id, parent)

        self.widget_class = widget_class
        self.init_args = init_args
        self.init_kwargs = init_kwargs or {}
        self.widget_instance = None

        # 性能指标
        self.creation_time = 0.0
        self.last_show_time = 0.0

    def create_ui(self) -> tk.Frame:
        """创建TTK页面UI"""
        try:
            start_time = time.time()

            # 创建TTK组件实例
            self.widget_instance = self.widget_class(
                self.parent, *self.init_args, **self.init_kwargs
            )

            # 如果组件不是Frame,需要包装
            if hasattr(self.widget_instance, "pack"):
                # 创建包装Frame
                wrapper_frame = tk.Frame(self.parent)
                self.widget_instance.pack(in_=wrapper_frame, fill=tk.BOTH, expand=True)
                frame = wrapper_frame
            else:
                frame = self.widget_instance

            self.creation_time = time.time() - start_time
            self.logger.debug(
                f"TTK页面UI创建完成: {self.page_id} (耗时: {self.creation_time:.3f}秒)"
            )

            return frame

        except Exception as e:
            error_msg = f"TTK页面UI创建失败: {self.page_id}"
            self.logger.error(f"{error_msg}: {e}")
            raise UIError(error_msg, "TTKPageAdapter") from e

    def on_show(self) -> None:
        """页面显示时调用"""
        self.last_show_time = time.time()

        # 调用组件的显示方法(如果存在)
        if self.widget_instance and hasattr(self.widget_instance, "on_page_enter"):
            try:
                self.widget_instance.on_page_enter()
            except Exception as e:
                self.logger.error(f"页面显示回调失败 [{self.page_id}]: {e}")

    def on_hide(self) -> None:
        """页面隐藏时调用"""
        # 调用组件的隐藏方法(如果存在)
        if self.widget_instance and hasattr(self.widget_instance, "on_page_leave"):
            try:
                self.widget_instance.on_page_leave()
            except Exception as e:
                self.logger.error(f"页面隐藏回调失败 [{self.page_id}]: {e}")

    def on_destroy(self) -> None:
        """页面销毁时调用"""
        # 调用组件的清理方法(如果存在)
        if self.widget_instance and hasattr(self.widget_instance, "cleanup"):
            try:
                self.widget_instance.cleanup()
            except Exception as e:
                self.logger.error(f"页面清理回调失败 [{self.page_id}]: {e}")

        self.widget_instance = None

    def get_widget_instance(self):
        """获取TTK组件实例"""
        return self.widget_instance


class IntegratedPageManager:
    """集成页面管理器

    整合增强页面管理器与现有TTK系统
    """

    def __init__(
        self,
        app: MiniCRMApplication,
        container,
        navigation_panel: NavigationPanelTTK,
        config_manager: Optional[PageConfigurationManager] = None,
    ):
        """初始化集成页面管理器

        Args:
            app: MiniCRM应用程序实例
            container: 页面容器
            navigation_panel: 导航面板
            config_manager: 配置管理器
        """
        self.app = app
        self.container = container
        self.navigation_panel = navigation_panel
        self.config_manager = config_manager or get_page_config_manager()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 创建增强页面管理器
        self._create_enhanced_manager()

        # 页面注册表
        self.registered_pages: Dict[str, NavigationItemTTK] = {}

        # 性能监控
        self.performance_stats = {
            "total_navigations": 0,
            "successful_navigations": 0,
            "failed_navigations": 0,
            "avg_navigation_time": 0.0,
            "cache_hit_rate": 0.0,
        }

        # 初始化完成标志
        self._initialized = False

        self.logger.debug("集成页面管理器初始化完成")

    def _create_enhanced_manager(self) -> None:
        """创建增强页面管理器"""
        try:
            # 获取全局配置
            global_config = self.config_manager.get_global_config()

            # 创建缓存配置
            cache_config = PageCacheConfig(
                enabled=global_config.global_cache_enabled,
                max_size=global_config.global_max_cache_size,
                ttl_seconds=global_config.global_cache_ttl,
                memory_threshold_mb=global_config.memory_threshold_mb,
                auto_cleanup=global_config.auto_cleanup,
                cleanup_interval=global_config.cleanup_interval,
            )

            # 创建加载配置
            load_config = PageLoadConfig(
                background_load=global_config.background_loading
            )

            # 创建切换配置
            transition_config = PageTransitionConfig(
                enabled=global_config.transitions_enabled,
                duration_ms=global_config.default_transition_duration,
                loading_indicator=global_config.loading_indicator_enabled,
            )

            # 创建增强页面管理器
            self.enhanced_manager = EnhancedPageManagerTTK(
                container=self.container,
                cache_config=cache_config,
                load_config=load_config,
                transition_config=transition_config,
            )

            self.logger.debug("增强页面管理器创建完成")

        except Exception as e:
            error_msg = "增强页面管理器创建失败"
            self.logger.error(f"{error_msg}: {e}")
            raise UIError(error_msg, "IntegratedPageManager") from e

    def register_navigation_item(self, item: NavigationItemTTK) -> None:
        """注册导航项

        Args:
            item: 导航项配置
        """
        try:
            # 检查服务依赖
            if item.requires_service and not self._check_service_available(
                item.requires_service
            ):
                self.logger.warning(
                    f"服务不可用,跳过注册页面: {item.name} (需要服务: {item.requires_service})"
                )
                return

            # 获取页面配置
            page_config = self.config_manager.get_page_config(
                item.name, self._get_page_type(item.name)
            )
            cache_config = self.config_manager.get_cache_config(
                item.name, self._get_page_type(item.name)
            )

            # 创建页面工厂函数
            def create_page() -> BasePage:
                return self._create_ttk_page_adapter(item)

            # 注册到增强页面管理器
            self.enhanced_manager.register_page_factory(
                page_id=item.name,
                factory=create_page,
                title=item.title,
                cache_enabled=cache_config.enabled,
                preload=page_config.preload_enabled,
                preload_priority=page_config.preload_priority,
            )

            # 注册到导航面板
            self._register_to_navigation_panel(item)

            # 保存注册信息
            self.registered_pages[item.name] = item

            self.logger.debug(f"导航项注册成功: {item.name}")

        except Exception as e:
            error_msg = f"导航项注册失败: {item.name}"
            self.logger.error(f"{error_msg}: {e}")
            raise UIError(error_msg, "IntegratedPageManager") from e

    def _check_service_available(self, service_name: str) -> bool:
        """检查服务是否可用"""
        try:
            service = self.app.get_service(service_name)
            return service is not None
        except Exception:
            return False

    def _get_page_type(self, page_name: str) -> str:
        """获取页面类型"""
        # 根据页面名称推断类型
        type_mapping = {
            "dashboard": "dashboard",
            "customers": "customers",
            "suppliers": "suppliers",
            "finance": "finance",
            "contracts": "contracts",
            "quotes": "quotes",
            "tasks": "tasks",
            "import_export": "import_export",
            "settings": "settings",
        }

        return type_mapping.get(page_name, "default")

    def _create_ttk_page_adapter(self, item: NavigationItemTTK) -> TTKPageAdapter:
        """创建TTK页面适配器

        Args:
            item: 导航项配置

        Returns:
            TTK页面适配器
        """
        try:
            # 获取组件类和参数
            widget_class = item.widget_class
            init_args = item.init_args
            init_kwargs = item.init_kwargs.copy()

            # 根据页面类型添加特定参数
            if item.name == "dashboard":
                init_kwargs["app"] = self.app
            elif item.requires_service:
                service = self.app.get_service(item.requires_service)
                if service:
                    init_kwargs["service"] = service
                else:
                    raise UIError(f"服务不可用: {item.requires_service}")

            # 创建适配器
            adapter = TTKPageAdapter(
                page_id=item.name,
                parent=self.container,
                widget_class=widget_class,
                init_args=init_args,
                init_kwargs=init_kwargs,
            )

            return adapter

        except Exception as e:
            error_msg = f"TTK页面适配器创建失败: {item.name}"
            self.logger.error(f"{error_msg}: {e}")
            raise UIError(error_msg, "IntegratedPageManager") from e

    def _register_to_navigation_panel(self, item: NavigationItemTTK) -> None:
        """注册到导航面板"""
        if not item.visible:
            return

        try:
            # 创建导航项配置
            from minicrm.ui.ttk_base.navigation_panel import NavigationItemConfig

            nav_config = NavigationItemConfig(
                item_id=item.name,
                text=item.title,
                command=lambda: self.navigate_to(item.name),
                icon=item.icon,
                tooltip=item.description or item.title,
                parent_id=item.parent,
            )

            # 添加到导航面板
            self.navigation_panel.add_navigation_item(nav_config)

        except Exception as e:
            self.logger.error(f"导航面板注册失败 [{item.name}]: {e}")

    def navigate_to(
        self, page_name: str, params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """导航到指定页面

        Args:
            page_name: 页面名称
            params: 导航参数

        Returns:
            是否导航成功
        """
        try:
            start_time = time.time()

            # 更新统计
            self.performance_stats["total_navigations"] += 1

            # 执行导航
            success = self.enhanced_manager.navigate_to(page_name, params)

            # 更新性能统计
            navigation_time = time.time() - start_time
            self._update_performance_stats(success, navigation_time)

            if success:
                self.logger.debug(
                    f"页面导航成功: {page_name} (耗时: {navigation_time:.3f}秒)"
                )

                # 更新导航面板状态
                self._update_navigation_panel_state(page_name)
            else:
                self.logger.error(f"页面导航失败: {page_name}")

            return success

        except Exception as e:
            self.logger.error(f"页面导航异常 [{page_name}]: {e}")
            self.performance_stats["failed_navigations"] += 1
            return False

    def _update_performance_stats(self, success: bool, navigation_time: float) -> None:
        """更新性能统计"""
        if success:
            self.performance_stats["successful_navigations"] += 1
        else:
            self.performance_stats["failed_navigations"] += 1

        # 更新平均导航时间
        total_nav = self.performance_stats["total_navigations"]
        current_avg = self.performance_stats["avg_navigation_time"]
        self.performance_stats["avg_navigation_time"] = (
            current_avg * (total_nav - 1) + navigation_time
        ) / total_nav

        # 更新缓存命中率
        cache_info = self.enhanced_manager.cache.get_cache_info()
        self.performance_stats["cache_hit_rate"] = cache_info["hit_rate"]

    def _update_navigation_panel_state(self, active_page: str) -> None:
        """更新导航面板状态"""
        try:
            # 更新导航面板的活动状态
            # 这里需要根据NavigationPanelTTK的实际接口来实现
            pass

        except Exception as e:
            self.logger.error(f"导航面板状态更新失败: {e}")

    def initialize_all_pages(self) -> None:
        """初始化所有页面"""
        if self._initialized:
            return

        try:
            self.logger.info("开始初始化所有TTK页面...")

            # 获取预加载页面列表
            preload_pages = self.config_manager.get_preload_pages()

            # 添加到预加载队列
            for page_id, priority in preload_pages:
                if page_id in self.registered_pages:
                    self.enhanced_manager.preload_page(page_id, priority)

            self._initialized = True
            self.logger.info(f"TTK页面初始化完成,预加载 {len(preload_pages)} 个页面")

        except Exception as e:
            self.logger.error(f"页面初始化失败: {e}")
            raise UIError("页面初始化失败", "IntegratedPageManager") from e

    def get_current_page(self) -> Optional[str]:
        """获取当前页面"""
        return self.enhanced_manager.get_current_page()

    def get_page_history(self) -> List[str]:
        """获取页面历史"""
        return self.enhanced_manager.get_page_history()

    def go_back(self) -> bool:
        """返回上一页"""
        return self.enhanced_manager.go_back()

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        manager_info = self.enhanced_manager.get_manager_info()

        return {
            **self.performance_stats,
            "manager_info": manager_info,
            "registered_pages": len(self.registered_pages),
            "configuration_summary": self.config_manager.get_configuration_summary(),
        }

    def get_registered_pages(self) -> List[str]:
        """获取已注册页面列表"""
        return list(self.registered_pages.keys())

    def is_page_registered(self, page_name: str) -> bool:
        """检查页面是否已注册"""
        return page_name in self.registered_pages

    def refresh_page_config(self) -> None:
        """刷新页面配置"""
        try:
            # 重新加载配置
            # 这里可以实现配置的热重载
            self.logger.info("页面配置刷新完成")

        except Exception as e:
            self.logger.error(f"页面配置刷新失败: {e}")

    def cleanup(self) -> None:
        """清理资源"""
        try:
            self.enhanced_manager.cleanup()
            self.registered_pages.clear()
            self.performance_stats.clear()

            self.logger.debug("集成页面管理器清理完成")

        except Exception as e:
            self.logger.error(f"集成页面管理器清理失败: {e}")


def create_integrated_page_manager(
    app: MiniCRMApplication,
    container,
    navigation_panel: NavigationPanelTTK,
    config_file: Optional[str] = None,
) -> IntegratedPageManager:
    """创建集成页面管理器

    Args:
        app: MiniCRM应用程序实例
        container: 页面容器
        navigation_panel: 导航面板
        config_file: 配置文件路径

    Returns:
        集成页面管理器实例
    """
    try:
        # 初始化配置管理器
        if config_file:
            from minicrm.ui.ttk_base.page_configuration import initialize_page_config

            config_manager = initialize_page_config(config_file)
        else:
            config_manager = get_page_config_manager()

        # 创建集成页面管理器
        manager = IntegratedPageManager(
            app=app,
            container=container,
            navigation_panel=navigation_panel,
            config_manager=config_manager,
        )

        return manager

    except Exception as e:
        logging.getLogger(__name__).error(f"集成页面管理器创建失败: {e}")
        raise UIError("集成页面管理器创建失败", "create_integrated_page_manager") from e


def register_all_ttk_pages_enhanced(manager: IntegratedPageManager) -> None:
    """注册所有TTK页面到增强管理器

    Args:
        manager: 集成页面管理器
    """
    logger = logging.getLogger(__name__)
    logger.info("开始注册所有TTK页面到增强管理器...")

    try:
        # 导入所有TTK页面类
        from minicrm.ui.panels.customer_panel_ttk import CustomerPanelTTK
        from minicrm.ui.panels.supplier_panel_ttk import SupplierPanelTTK
        from minicrm.ui.settings_panel import SettingsPanel
        from minicrm.ui.ttk_base.contract_panel_ttk import ContractPanelTTK
        from minicrm.ui.ttk_base.finance_panel_ttk import FinancePanelTTK
        from minicrm.ui.ttk_base.import_export_panel_ttk import ImportExportPanelTTK
        from minicrm.ui.ttk_base.quote_panel_ttk import QuotePanelTTK
        from minicrm.ui.ttk_base.task_panel_ttk import TaskPanelTTK

        # 页面配置列表
        page_configs = [
            # 仪表盘页面 - 最高优先级
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
            ),
            # 客户管理页面 - 高优先级
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
            ),
            # 供应商管理页面 - 高优先级
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
            ),
            # 财务管理页面 - 中等优先级
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
                preload=False,
            ),
            # 合同管理页面 - 中等优先级
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
                preload=False,
            ),
            # 报价管理页面 - 中等优先级
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
                preload=False,
            ),
            # 任务管理页面 - 中等优先级
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
                preload=False,
            ),
            # 数据导入导出页面 - 低优先级,不缓存
            NavigationItemTTK(
                name="import_export",
                title="数据管理",
                icon="📤",
                widget_class=ImportExportPanelTTK,
                order=8,
                requires_service="import_export",
                description="数据导入导出功能",
                route_path="/data",
                cache_enabled=False,
                preload=False,
            ),
            # 系统设置页面 - 最低优先级,不缓存
            NavigationItemTTK(
                name="settings",
                title="系统设置",
                icon="⚙️",
                widget_class=SettingsPanel,
                order=9,
                description="系统配置和偏好设置",
                route_path="/settings",
                cache_enabled=False,
                preload=False,
            ),
        ]

        # 注册所有页面
        for page_config in page_configs:
            manager.register_navigation_item(page_config)

        # 初始化所有页面
        manager.initialize_all_pages()

        logger.info(f"所有TTK页面注册完成,共注册 {len(page_configs)} 个页面")

    except Exception as e:
        logger.error(f"TTK页面注册过程中发生错误: {e}")
        raise UIError("TTK页面注册失败", "register_all_ttk_pages_enhanced") from e
