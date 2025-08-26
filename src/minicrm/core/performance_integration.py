"""
MiniCRM 性能监控集成模块

负责将性能监控hooks集成到系统的关键操作中,包括:
- 数据库操作监控
- 服务层方法监控
- UI操作监控
- 自动化性能数据收集

这个模块实现了任务21.1.1的要求,为关键操作提供全面的性能监控.
"""

import logging
from typing import TYPE_CHECKING, Any

from .performance_hooks import performance_hooks
from .performance_monitor import performance_monitor


if TYPE_CHECKING:
    from ..data.database.database_manager import DatabaseManager


class PerformanceIntegration:
    """
    性能监控集成管理器

    负责协调和管理整个系统的性能监控集成,确保所有关键操作
    都被正确监控,并提供统一的性能数据收集和报告功能.
    """

    def __init__(self):
        """初始化性能监控集成管理器"""
        self._logger = logging.getLogger(__name__)
        self._integrated_services: dict[str, Any] = {}
        self._integrated_daos: dict[str, Any] = {}
        self._integrated_ui_components: dict[str, Any] = {}
        self._is_initialized = False

    def initialize(self) -> None:
        """
        初始化性能监控集成

        启用性能监控并准备集成环境
        """
        try:
            # 启用性能监控
            performance_hooks.enable()

            # 启用专门的分析器(通过延迟导入避免循环依赖)
            from .database_performance_analyzer import database_performance_analyzer
            from .ui_performance_analyzer import ui_performance_analyzer

            database_performance_analyzer.enable()
            ui_performance_analyzer.enable()

            self._is_initialized = True
            self._logger.info("性能监控集成初始化完成")

        except Exception as e:
            self._logger.error(f"性能监控集成初始化失败: {e}")
            raise RuntimeError(f"性能监控集成初始化失败: {e}") from e

    def integrate_database_manager(self, database_manager: "DatabaseManager") -> None:
        """
        为数据库管理器集成性能监控hooks

        Args:
            database_manager: 数据库管理器实例
        """
        if not self._is_initialized:
            self.initialize()

        try:
            # 使用性能hooks管理器应用数据库监控
            performance_hooks.apply_database_hooks(database_manager)

            # 记录集成状态
            self._integrated_daos["database_manager"] = database_manager

            self._logger.info("数据库管理器性能监控集成完成")

        except Exception as e:
            self._logger.error(f"数据库管理器性能监控集成失败: {e}")
            raise RuntimeError(f"数据库管理器性能监控集成失败: {e}") from e

    def integrate_service(self, service_instance, service_name: str = None) -> None:
        """
        为服务实例集成性能监控hooks

        Args:
            service_instance: 服务实例
            service_name: 服务名称,如果不提供则使用类名
        """
        if not self._is_initialized:
            self.initialize()

        try:
            svc_name = service_name or service_instance.__class__.__name__

            # 使用性能hooks管理器应用服务监控
            performance_hooks.apply_service_hooks(service_instance, svc_name)

            # 记录集成状态
            self._integrated_services[svc_name] = service_instance

            self._logger.info(f"服务性能监控集成完成: {svc_name}")

        except Exception as e:
            self._logger.error(f"服务性能监控集成失败: {e}")
            raise RuntimeError(f"服务性能监控集成失败: {e}") from e

    def integrate_all_services(self, service_registry: dict[str, Any]) -> None:
        """
        批量集成所有服务的性能监控

        Args:
            service_registry: 服务注册表,包含所有服务实例
        """
        if not self._is_initialized:
            self.initialize()

        integrated_count = 0
        failed_services = []

        for service_name, service_instance in service_registry.items():
            try:
                self.integrate_service(service_instance, service_name)
                integrated_count += 1
            except Exception as e:
                failed_services.append((service_name, str(e)))
                self._logger.warning(f"服务 {service_name} 性能监控集成失败: {e}")

        self._logger.info(
            f"批量服务性能监控集成完成: 成功 {integrated_count} 个,"
            f"失败 {len(failed_services)} 个"
        )

        if failed_services:
            self._logger.warning(f"集成失败的服务: {failed_services}")

    def integrate_ui_component(self, ui_component, component_name: str) -> None:
        """
        为UI组件集成性能监控hooks

        Args:
            ui_component: UI组件实例
            component_name: 组件名称
        """
        if not self._is_initialized:
            self.initialize()

        try:
            # 为UI组件的关键方法添加性能监控
            self._apply_ui_performance_hooks(ui_component, component_name)

            # 记录集成状态
            self._integrated_ui_components[component_name] = ui_component

            self._logger.info(f"UI组件性能监控集成完成: {component_name}")

        except Exception as e:
            self._logger.error(f"UI组件性能监控集成失败: {e}")
            raise RuntimeError(f"UI组件性能监控集成失败: {e}") from e

    def _apply_ui_performance_hooks(self, ui_component, component_name: str) -> None:
        """
        为UI组件应用性能监控hooks

        Args:
            ui_component: UI组件实例
            component_name: 组件名称
        """
        # 获取需要监控的UI方法列表
        ui_methods_to_monitor = [
            "load_data",
            "refresh_data",
            "update_display",
            "render",
            "show",
            "hide",
            "resize",
            "paint_event",
            "update_ui",
        ]

        for method_name in ui_methods_to_monitor:
            if hasattr(ui_component, method_name):
                method = getattr(ui_component, method_name)
                if callable(method):
                    # 应用UI操作监控装饰器
                    monitored_method = performance_hooks.ui_hook.monitor_ui_operation(
                        f"{component_name}.{method_name}"
                    )(method)
                    setattr(ui_component, method_name, monitored_method)

    def get_integration_status(self) -> dict[str, Any]:
        """
        获取性能监控集成状态

        Returns:
            Dict[str, Any]: 集成状态信息
        """
        return {
            "initialized": self._is_initialized,
            "monitoring_enabled": performance_hooks.is_enabled(),
            "integrated_services_count": len(self._integrated_services),
            "integrated_daos_count": len(self._integrated_daos),
            "integrated_ui_components_count": len(self._integrated_ui_components),
            "integrated_services": list(self._integrated_services.keys()),
            "integrated_daos": list(self._integrated_daos.keys()),
            "integrated_ui_components": list(self._integrated_ui_components.keys()),
        }

    def get_performance_report(self) -> dict[str, Any]:
        """
        获取完整的性能监控报告

        Returns:
            Dict[str, Any]: 性能监控报告
        """
        try:
            # 获取基础性能报告
            base_report = performance_hooks.get_performance_report()

            # 添加集成状态信息
            integration_status = self.get_integration_status()

            # 生成综合报告
            comprehensive_report = {
                "timestamp": performance_monitor.get_summary().get("newest_metric"),
                "integration_status": integration_status,
                "performance_data": base_report,
                "recommendations": self._generate_performance_recommendations(
                    base_report
                ),
            }

            return comprehensive_report

        except Exception as e:
            self._logger.error(f"生成性能监控报告失败: {e}")
            return {"error": str(e)}

    def _generate_performance_recommendations(
        self, performance_data: dict[str, Any]
    ) -> list[str]:
        """
        基于性能数据生成优化建议

        Args:
            performance_data: 性能数据

        Returns:
            List[str]: 优化建议列表
        """
        recommendations = []

        try:
            # 分析数据库性能
            db_data = performance_data.get("database", {})
            if db_data.get("total_duration_ms", 0) > 5000:  # 5秒阈值
                recommendations.append(
                    "数据库操作总耗时较长,建议优化查询语句或添加索引"
                )

            # 分析服务性能
            service_data = performance_data.get("services", {})
            if service_data.get("total_duration_ms", 0) > 3000:  # 3秒阈值
                recommendations.append("服务层操作耗时较长,建议优化业务逻辑或添加缓存")

            # 分析UI性能
            ui_data = performance_data.get("ui", {})
            if ui_data.get("total_duration_ms", 0) > 2000:  # 2秒阈值
                recommendations.append("UI操作响应较慢,建议优化界面渲染或使用异步加载")

            # 分析操作频率
            summary = performance_data.get("summary", {})
            if summary.get("total_operations", 0) > 1000:
                recommendations.append("操作频率较高,建议考虑批量处理或缓存策略")

            if not recommendations:
                recommendations.append("系统性能表现良好,无需特别优化")

        except Exception as e:
            self._logger.warning(f"生成性能建议时出错: {e}")
            recommendations.append("性能分析出现异常,建议检查监控数据")

        return recommendations

    def export_performance_data(self, file_path: str) -> bool:
        """
        导出性能监控数据

        Args:
            file_path: 导出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            # 使用性能监控器的导出功能
            performance_monitor.export_metrics(file_path)

            self._logger.info(f"性能监控数据导出成功: {file_path}")
            return True

        except Exception as e:
            self._logger.error(f"性能监控数据导出失败: {e}")
            return False

    def reset_performance_data(self) -> None:
        """重置性能监控数据"""
        try:
            performance_monitor.clear_metrics()
            self._logger.info("性能监控数据已重置")

        except Exception as e:
            self._logger.error(f"重置性能监控数据失败: {e}")
            raise RuntimeError(f"重置性能监控数据失败: {e}") from e

    def shutdown(self) -> None:
        """关闭性能监控集成"""
        try:
            # 禁用性能监控
            performance_hooks.disable()

            # 禁用专门的分析器(通过延迟导入避免循环依赖)
            try:
                from .database_performance_analyzer import database_performance_analyzer
                from .ui_performance_analyzer import ui_performance_analyzer

                database_performance_analyzer.disable()
                ui_performance_analyzer.disable()
            except ImportError:
                pass  # 如果分析器未导入,忽略

            # 清理集成状态
            self._integrated_services.clear()
            self._integrated_daos.clear()
            self._integrated_ui_components.clear()

            self._is_initialized = False

            self._logger.info("性能监控集成已关闭")

        except Exception as e:
            self._logger.error(f"关闭性能监控集成失败: {e}")


# 全局性能监控集成管理器实例
performance_integration = PerformanceIntegration()


# 便捷函数
def initialize_performance_monitoring() -> None:
    """初始化性能监控"""
    performance_integration.initialize()


def integrate_database_performance(database_manager: "DatabaseManager") -> None:
    """集成数据库性能监控"""
    performance_integration.integrate_database_manager(database_manager)


def integrate_service_performance(service_instance, service_name: str = None) -> None:
    """集成服务性能监控"""
    performance_integration.integrate_service(service_instance, service_name)


def integrate_ui_performance(ui_component, component_name: str) -> None:
    """集成UI性能监控"""
    performance_integration.integrate_ui_component(ui_component, component_name)


def get_performance_report() -> dict[str, Any]:
    """获取性能监控报告"""
    return performance_integration.get_performance_report()


def export_performance_data(file_path: str) -> bool:
    """导出性能监控数据"""
    return performance_integration.export_performance_data(file_path)
