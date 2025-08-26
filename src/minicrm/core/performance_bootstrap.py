"""
MiniCRM 性能监控启动集成模块

在应用程序启动时自动集成性能监控到关键组件,包括:
- 自动发现和集成服务
- 自动集成数据库管理器
- 自动集成UI组件
- 提供启动时的性能监控配置

这个模块确保性能监控在应用启动时就被正确配置和激活.
"""

import logging
from pathlib import Path
from typing import Any

from .performance_integration import performance_integration


class PerformanceBootstrap:
    """
    性能监控启动集成器

    负责在应用程序启动时自动发现和集成性能监控到系统的各个组件中.
    """

    def __init__(self):
        """初始化性能监控启动集成器"""
        self._logger = logging.getLogger(__name__)
        self._config: dict[str, Any] = {}
        self._bootstrap_completed = False

    def load_config(self, config_path: Path | None = None) -> None:
        """
        加载性能监控配置

        Args:
            config_path: 配置文件路径,如果为None则使用默认配置
        """
        try:
            if config_path and config_path.exists():
                import json

                with open(config_path, encoding="utf-8") as f:
                    self._config = json.load(f)
                self._logger.info(f"性能监控配置已加载: {config_path}")
            else:
                # 使用默认配置
                self._config = self._get_default_config()
                self._logger.info("使用默认性能监控配置")

        except Exception as e:
            self._logger.warning(f"加载性能监控配置失败,使用默认配置: {e}")
            self._config = self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """
        获取默认性能监控配置

        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            "enabled": True,
            "auto_integrate_services": True,
            "auto_integrate_database": True,
            "auto_integrate_ui": True,
            "performance_thresholds": {
                "database_query_ms": 1000,  # 数据库查询警告阈值
                "service_method_ms": 500,  # 服务方法警告阈值
                "ui_operation_ms": 200,  # UI操作警告阈值
            },
            "monitoring_targets": {
                "database_operations": [
                    "execute_query",
                    "execute_insert",
                    "execute_update",
                    "execute_delete",
                ],
                "service_methods": [
                    "create",
                    "update",
                    "delete",
                    "search",
                    "get_by_id",
                ],
                "ui_operations": [
                    "load_data",
                    "refresh_data",
                    "update_display",
                    "render",
                ],
            },
            "export_settings": {
                "auto_export": False,
                "export_interval_minutes": 60,
                "export_path": "logs/performance_data.json",
            },
        }

    def bootstrap_application(self, app_components: dict[str, Any]) -> None:
        """
        为整个应用程序启动性能监控

        Args:
            app_components: 应用程序组件字典,包含数据库管理器、服务等
        """
        if not self._config.get("enabled", True):
            self._logger.info("性能监控已禁用,跳过启动集成")
            return

        try:
            self._logger.info("开始应用程序性能监控启动集成")

            # 初始化性能监控集成
            performance_integration.initialize()

            # 集成数据库管理器
            if self._config.get("auto_integrate_database", True):
                self._bootstrap_database(app_components)

            # 集成服务层
            if self._config.get("auto_integrate_services", True):
                self._bootstrap_services(app_components)

            # 集成UI组件
            if self._config.get("auto_integrate_ui", True):
                self._bootstrap_ui_components(app_components)

            # 设置性能阈值
            self._configure_performance_thresholds()

            # 设置自动导出(如果启用)
            if self._config.get("export_settings", {}).get("auto_export", False):
                self._setup_auto_export()

            self._bootstrap_completed = True
            self._logger.info("应用程序性能监控启动集成完成")

        except Exception as e:
            self._logger.error(f"应用程序性能监控启动集成失败: {e}")
            raise

    def _bootstrap_database(self, app_components: dict[str, Any]) -> None:
        """
        启动集成数据库性能监控

        Args:
            app_components: 应用程序组件
        """
        try:
            database_manager = app_components.get("database_manager")
            if database_manager:
                performance_integration.integrate_database_manager(database_manager)
                self._logger.info("数据库管理器性能监控启动集成完成")
            else:
                self._logger.warning("未找到数据库管理器,跳过数据库性能监控集成")

        except Exception as e:
            self._logger.error(f"数据库性能监控启动集成失败: {e}")

    def _bootstrap_services(self, app_components: dict[str, Any]) -> None:
        """
        启动集成服务层性能监控

        Args:
            app_components: 应用程序组件
        """
        try:
            services = app_components.get("services", {})
            if services:
                performance_integration.integrate_all_services(services)
                self._logger.info(
                    f"服务层性能监控启动集成完成,集成了 {len(services)} 个服务"
                )
            else:
                self._logger.warning("未找到服务组件,跳过服务性能监控集成")

        except Exception as e:
            self._logger.error(f"服务性能监控启动集成失败: {e}")

    def _bootstrap_ui_components(self, app_components: dict[str, Any]) -> None:
        """
        启动集成UI组件性能监控

        Args:
            app_components: 应用程序组件
        """
        try:
            ui_components = app_components.get("ui_components", {})
            integrated_count = 0

            for component_name, component in ui_components.items():
                try:
                    performance_integration.integrate_ui_component(
                        component, component_name
                    )
                    integrated_count += 1
                except Exception as e:
                    self._logger.warning(
                        f"UI组件 {component_name} 性能监控集成失败: {e}"
                    )

            if integrated_count > 0:
                self._logger.info(
                    f"UI组件性能监控启动集成完成,集成了 {integrated_count} 个组件"
                )
            else:
                self._logger.warning("未找到UI组件或集成失败,跳过UI性能监控集成")

        except Exception as e:
            self._logger.error(f"UI性能监控启动集成失败: {e}")

    def _configure_performance_thresholds(self) -> None:
        """配置性能监控阈值"""
        try:
            thresholds = self._config.get("performance_thresholds", {})

            # 这里可以设置性能监控器的阈值
            # 由于当前的性能监控器设计中没有直接的阈值设置接口
            # 我们记录配置以供后续使用
            self._logger.info(f"性能监控阈值配置: {thresholds}")

        except Exception as e:
            self._logger.error(f"配置性能监控阈值失败: {e}")

    def _setup_auto_export(self) -> None:
        """设置自动导出性能数据"""
        try:
            export_settings = self._config.get("export_settings", {})
            export_interval = export_settings.get("export_interval_minutes", 60)
            export_path = export_settings.get(
                "export_path", "logs/performance_data.json"
            )

            # 这里可以设置定时任务来自动导出性能数据
            # 由于这是一个简化的实现,我们只记录配置
            self._logger.info(
                f"自动导出配置: 间隔 {export_interval} 分钟,路径 {export_path}"
            )

        except Exception as e:
            self._logger.error(f"设置自动导出失败: {e}")

    def get_bootstrap_status(self) -> dict[str, Any]:
        """
        获取启动集成状态

        Returns:
            Dict[str, Any]: 启动集成状态
        """
        integration_status = performance_integration.get_integration_status()

        return {
            "bootstrap_completed": self._bootstrap_completed,
            "config_loaded": bool(self._config),
            "performance_enabled": self._config.get("enabled", False),
            "integration_status": integration_status,
            "config": self._config,
        }

    def create_performance_startup_script(self) -> str:
        """
        创建性能监控启动脚本代码

        Returns:
            str: 启动脚本代码
        """
        script_template = '''
# MiniCRM 性能监控启动脚本
# 在应用程序主入口处添加以下代码

from minicrm.core.performance_bootstrap import performance_bootstrap

def initialize_performance_monitoring(app_components):
    """
    初始化应用程序性能监控

    Args:
        app_components: 应用程序组件字典,应包含:
            - 'database_manager': 数据库管理器实例
            - 'services': 服务实例字典
            - 'ui_components': UI组件实例字典
    """
    try:
        # 加载性能监控配置
        performance_bootstrap.load_config()

        # 启动性能监控集成
        performance_bootstrap.bootstrap_application(app_components)

        print("性能监控启动集成完成")

    except Exception as e:
        print(f"性能监控启动集成失败: {e}")

# 使用示例:
# app_components = {
#     'database_manager': database_manager,
#     'services': {
#         'customer_service': customer_service,
#         'supplier_service': supplier_service,
#         # ... 其他服务
#     },
#     'ui_components': {
#         'main_window': main_window,
#         'customer_panel': customer_panel,
#         # ... 其他UI组件
#     }
# }
# initialize_performance_monitoring(app_components)
'''
        return script_template

    def generate_integration_report(self) -> str:
        """
        生成性能监控集成报告

        Returns:
            str: 集成报告
        """
        try:
            status = self.get_bootstrap_status()
            performance_report = performance_integration.get_performance_report()

            report_lines = [
                "=== MiniCRM 性能监控集成报告 ===",
                "",
                f"启动集成状态: {'完成' if status['bootstrap_completed'] else '未完成'}",
                f"配置加载状态: {'已加载' if status['config_loaded'] else '未加载'}",
                f"性能监控启用: {'是' if status['performance_enabled'] else '否'}",
                "",
                "=== 集成统计 ===",
                f"已集成服务数量: {status['integration_status']['integrated_services_count']}",
                f"已集成数据库组件: {status['integration_status']['integrated_daos_count']}",
                f"已集成UI组件: {status['integration_status']['integrated_ui_components_count']}",
                "",
                "=== 已集成组件列表 ===",
                "服务: "
                + ", ".join(status["integration_status"]["integrated_services"]),
                "数据库: " + ", ".join(status["integration_status"]["integrated_daos"]),
                "UI组件: "
                + ", ".join(status["integration_status"]["integrated_ui_components"]),
                "",
                "=== 性能监控数据 ===",
            ]

            if "performance_data" in performance_report:
                perf_data = performance_report["performance_data"]
                summary = perf_data.get("summary", {})

                report_lines.extend(
                    [
                        f"总操作数: {summary.get('total_operations', 0)}",
                        f"唯一操作数: {summary.get('unique_operations', 0)}",
                        f"总耗时: {summary.get('total_duration_ms', 0):.2f}ms",
                        f"平均耗时: {summary.get('avg_duration_ms', 0):.2f}ms",
                        f"当前内存使用: {summary.get('current_memory_mb', 0):.2f}MB",
                    ]
                )

            if "recommendations" in performance_report:
                report_lines.extend(
                    [
                        "",
                        "=== 性能优化建议 ===",
                    ]
                    + [f"- {rec}" for rec in performance_report["recommendations"]]
                )

            return "\n".join(report_lines)

        except Exception as e:
            return f"生成集成报告失败: {e}"


# 全局性能监控启动集成器实例
performance_bootstrap = PerformanceBootstrap()


# 便捷函数
def bootstrap_performance_monitoring(app_components: dict[str, Any]) -> None:
    """启动性能监控集成"""
    performance_bootstrap.bootstrap_application(app_components)


def get_bootstrap_status() -> dict[str, Any]:
    """获取启动集成状态"""
    return performance_bootstrap.get_bootstrap_status()


def generate_startup_script() -> str:
    """生成启动脚本"""
    return performance_bootstrap.create_performance_startup_script()
