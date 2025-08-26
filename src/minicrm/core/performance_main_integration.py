"""
MiniCRM 主程序性能监控集成

在MiniCRM主程序启动时集成性能监控,包括:
- 应用程序启动时的自动集成
- 主窗口和关键UI组件的性能监控
- 服务层和数据层的性能监控
- 提供完整的性能监控生命周期管理

这个模块实现了任务21.1.1的完整集成方案.
"""

import logging
from pathlib import Path
from typing import Any

from .performance_bootstrap import performance_bootstrap
from .performance_integration import performance_integration


class MainApplicationPerformanceIntegrator:
    """
    主应用程序性能监控集成器

    负责在MiniCRM主程序中集成性能监控,确保所有关键组件
    都被正确监控,并提供完整的性能数据收集和分析.
    """

    def __init__(self):
        """初始化主应用程序性能监控集成器"""
        self._logger = logging.getLogger(__name__)
        self._integrated = False
        self._app_components: dict[str, Any] = {}
        self._performance_config_path: Path | None = None

    def integrate_with_application(self, app_instance) -> None:
        """
        与MiniCRM应用程序实例集成性能监控

        Args:
            app_instance: MiniCRM应用程序实例
        """
        try:
            self._logger.info("开始集成主应用程序性能监控")

            # 收集应用程序组件
            self._collect_app_components(app_instance)

            # 设置性能监控配置
            self._setup_performance_config()

            # 执行性能监控集成
            self._execute_integration()

            # 设置应用程序生命周期钩子
            self._setup_app_lifecycle_hooks(app_instance)

            self._integrated = True
            self._logger.info("主应用程序性能监控集成完成")

        except Exception as e:
            self._logger.error(f"主应用程序性能监控集成失败: {e}")
            raise

    def _collect_app_components(self, app_instance) -> None:
        """
        收集应用程序组件

        Args:
            app_instance: 应用程序实例
        """
        try:
            # 收集数据库管理器
            if (
                hasattr(app_instance, "database_manager")
                and app_instance.database_manager
            ):
                self._app_components["database_manager"] = app_instance.database_manager
                self._logger.debug("收集到数据库管理器")

            # 收集服务层组件
            services = {}
            service_names = [
                "customer_service",
                "supplier_service",
                "finance_service",
                "contract_service",
                "quote_service",
                "analytics_service",
                "interaction_service",
                "backup_service",
                "settings_service",
            ]

            for service_name in service_names:
                service = app_instance.get_service(service_name)
                if service:
                    services[service_name] = service
                    self._logger.debug(f"收集到服务: {service_name}")

            if services:
                self._app_components["services"] = services

            # 收集UI组件(如果有主窗口)
            ui_components = {}
            if hasattr(app_instance, "main_window") and app_instance.main_window:
                main_window = app_instance.main_window
                ui_components["main_window"] = main_window

                # 收集主窗口的子组件
                if (
                    hasattr(main_window, "_navigation_panel")
                    and main_window._navigation_panel
                ):
                    ui_components["navigation_panel"] = main_window._navigation_panel

                if hasattr(main_window, "_dashboard") and main_window._dashboard:
                    ui_components["dashboard"] = main_window._dashboard

                if (
                    hasattr(main_window, "_content_stack")
                    and main_window._content_stack
                ):
                    ui_components["content_stack"] = main_window._content_stack

                self._logger.debug(f"收集到UI组件: {list(ui_components.keys())}")

            if ui_components:
                self._app_components["ui_components"] = ui_components

            self._logger.info(
                f"应用程序组件收集完成,共收集到 {len(self._app_components)} 类组件"
            )

        except Exception as e:
            self._logger.error(f"应用程序组件收集失败: {e}")
            raise

    def _setup_performance_config(self) -> None:
        """设置性能监控配置"""
        try:
            # 查找配置文件
            config_paths = [
                Path("config/performance.json"),
                Path(".kiro/settings/performance.json"),
                Path("performance_config.json"),
            ]

            for config_path in config_paths:
                if config_path.exists():
                    self._performance_config_path = config_path
                    break

            # 加载配置
            performance_bootstrap.load_config(self._performance_config_path)

            if self._performance_config_path:
                self._logger.info(
                    f"性能监控配置已加载: {self._performance_config_path}"
                )
            else:
                self._logger.info("使用默认性能监控配置")

        except Exception as e:
            self._logger.error(f"性能监控配置设置失败: {e}")
            raise

    def _execute_integration(self) -> None:
        """执行性能监控集成"""
        try:
            # 使用性能监控启动器执行集成
            performance_bootstrap.bootstrap_application(self._app_components)

            self._logger.info("性能监控集成执行完成")

        except Exception as e:
            self._logger.error(f"性能监控集成执行失败: {e}")
            raise

    def _setup_app_lifecycle_hooks(self, app_instance) -> None:
        """
        设置应用程序生命周期钩子

        Args:
            app_instance: 应用程序实例
        """
        try:
            # 连接应用程序信号到性能监控
            if hasattr(app_instance, "startup_completed"):
                app_instance.startup_completed.connect(self._on_app_startup_completed)

            if hasattr(app_instance, "shutdown_started"):
                app_instance.shutdown_started.connect(self._on_app_shutdown_started)

            if hasattr(app_instance, "service_error"):
                app_instance.service_error.connect(self._on_service_error)

            self._logger.debug("应用程序生命周期钩子设置完成")

        except Exception as e:
            self._logger.error(f"应用程序生命周期钩子设置失败: {e}")

    def _on_app_startup_completed(self) -> None:
        """应用程序启动完成处理"""
        try:
            self._logger.info("应用程序启动完成,性能监控已激活")

            # 生成启动报告
            self._generate_startup_report()

        except Exception as e:
            self._logger.error(f"应用程序启动完成处理失败: {e}")

    def _on_app_shutdown_started(self) -> None:
        """应用程序关闭开始处理"""
        try:
            self._logger.info("应用程序开始关闭,生成性能监控报告")

            # 生成关闭报告
            self._generate_shutdown_report()

            # 导出性能数据
            self._export_final_performance_data()

        except Exception as e:
            self._logger.error(f"应用程序关闭处理失败: {e}")

    def _on_service_error(self, service_name: str, error_message: str) -> None:
        """服务错误处理"""
        try:
            self._logger.error(f"服务错误监控: {service_name} - {error_message}")

            # 记录服务错误到性能监控
            from .performance_monitor import performance_monitor

            performance_monitor.record_metric(
                f"service.error.{service_name}",
                duration=0.0,
                memory_delta=0.0,
                error=error_message,
                service=service_name,
            )

        except Exception as e:
            self._logger.error(f"服务错误处理失败: {e}")

    def _generate_startup_report(self) -> None:
        """生成启动报告"""
        try:
            status = performance_bootstrap.get_bootstrap_status()

            report_lines = [
                "=== MiniCRM 性能监控启动报告 ===",
                f"启动时间: {performance_integration.get_performance_report().get('timestamp', 'N/A')}",
                f"集成状态: {'成功' if status['bootstrap_completed'] else '失败'}",
                f"监控启用: {'是' if status['performance_enabled'] else '否'}",
                f"已集成服务: {status['integration_status']['integrated_services_count']}",
                f"已集成数据库组件: {status['integration_status']['integrated_daos_count']}",
                f"已集成UI组件: {status['integration_status']['integrated_ui_components_count']}",
                "=" * 40,
            ]

            startup_report = "\n".join(report_lines)
            self._logger.info(f"启动报告:\n{startup_report}")

        except Exception as e:
            self._logger.error(f"生成启动报告失败: {e}")

    def _generate_shutdown_report(self) -> None:
        """生成关闭报告"""
        try:
            performance_report = performance_integration.get_performance_report()

            if "performance_data" in performance_report:
                perf_data = performance_report["performance_data"]
                summary = perf_data.get("summary", {})

                report_lines = [
                    "=== MiniCRM 性能监控关闭报告 ===",
                    f"总操作数: {summary.get('total_operations', 0)}",
                    f"总耗时: {summary.get('total_duration_ms', 0):.2f}ms",
                    f"平均耗时: {summary.get('avg_duration_ms', 0):.2f}ms",
                    f"内存使用: {summary.get('current_memory_mb', 0):.2f}MB",
                    "",
                    "各类型操作统计:",
                ]

                for category in ["database", "services", "ui", "business"]:
                    if category in perf_data:
                        cat_data = perf_data[category]
                        report_lines.append(
                            f"  {category.upper()}: {cat_data.get('operations_count', 0)} 操作, "
                            f"{cat_data.get('total_duration_ms', 0):.2f}ms"
                        )

                if "recommendations" in performance_report:
                    report_lines.extend(
                        [
                            "",
                            "性能优化建议:",
                        ]
                        + [
                            f"  - {rec}"
                            for rec in performance_report["recommendations"]
                        ]
                    )

                report_lines.append("=" * 40)

                shutdown_report = "\n".join(report_lines)
                self._logger.info(f"关闭报告:\n{shutdown_report}")

        except Exception as e:
            self._logger.error(f"生成关闭报告失败: {e}")

    def _export_final_performance_data(self) -> None:
        """导出最终性能数据"""
        try:
            # 创建导出目录
            export_dir = Path("logs/performance")
            export_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名(包含时间戳)
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = export_dir / f"performance_data_{timestamp}.json"

            # 导出性能数据
            success = performance_integration.export_performance_data(str(export_file))

            if success:
                self._logger.info(f"性能数据已导出: {export_file}")
            else:
                self._logger.warning("性能数据导出失败")

        except Exception as e:
            self._logger.error(f"导出最终性能数据失败: {e}")

    def get_integration_status(self) -> dict[str, Any]:
        """
        获取集成状态

        Returns:
            Dict[str, Any]: 集成状态信息
        """
        return {
            "integrated": self._integrated,
            "components_count": len(self._app_components),
            "components": list(self._app_components.keys()),
            "config_path": str(self._performance_config_path)
            if self._performance_config_path
            else None,
            "bootstrap_status": performance_bootstrap.get_bootstrap_status()
            if self._integrated
            else None,
        }

    def generate_integration_code(self) -> str:
        """
        生成集成代码示例

        Returns:
            str: 集成代码
        """
        return '''
# MiniCRM 主程序性能监控集成代码
# 在应用程序主入口文件中添加以下代码

from minicrm.core.performance_main_integration import MainApplicationPerformanceIntegrator

class MiniCRMApplication:
    def __init__(self):
        # ... 其他初始化代码 ...

        # 创建性能监控集成器
        self._performance_integrator = MainApplicationPerformanceIntegrator()

    def initialize(self):
        """初始化应用程序"""
        try:
            # ... 其他初始化代码 ...

            # 集成性能监控(在所有组件初始化完成后)
            self._performance_integrator.integrate_with_application(self)

            print("应用程序初始化完成,性能监控已激活")

        except Exception as e:
            print(f"应用程序初始化失败: {e}")
            raise

    def shutdown(self):
        """关闭应用程序"""
        try:
            # 性能监控会自动处理关闭时的数据导出

            # ... 其他关闭代码 ...

        except Exception as e:
            print(f"应用程序关闭失败: {e}")

# 使用示例
if __name__ == "__main__":
    app = MiniCRMApplication()
    app.initialize()
    # ... 运行应用程序 ...
    app.shutdown()
'''


# 全局主应用程序性能监控集成器实例
main_performance_integrator = MainApplicationPerformanceIntegrator()


# 便捷函数
def integrate_main_app_performance(app_instance) -> None:
    """集成主应用程序性能监控"""
    main_performance_integrator.integrate_with_application(app_instance)


def get_main_integration_status() -> dict[str, Any]:
    """获取主集成状态"""
    return main_performance_integrator.get_integration_status()


def generate_main_integration_code() -> str:
    """生成主集成代码"""
    return main_performance_integrator.generate_integration_code()
