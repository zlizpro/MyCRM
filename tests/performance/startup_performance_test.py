"""MiniCRM启动性能专项测试

为任务10提供详细的启动性能测试：
- 应用程序启动时间测量
- 模块导入时间分析
- 数据库初始化时间
- UI组件加载时间
- 服务层初始化时间

测试目标：
1. 验证启动时间不超过3秒（需求11.1）
2. 识别启动过程中的性能瓶颈
3. 对比Qt和TTK版本的启动性能
4. 提供启动优化建议

作者: MiniCRM开发团队
"""

import gc
import importlib
import logging
from pathlib import Path
import sys
import time
from typing import Dict
import unittest


# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.performance.performance_benchmark_framework import (
    BaseBenchmark,
    PerformanceMetrics,
)


class ModuleImportBenchmark:
    """模块导入性能基准测试"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def measure_import_time(self, module_name: str) -> float:
        """测量模块导入时间

        Args:
            module_name: 模块名称

        Returns:
            导入时间（秒）
        """
        try:
            # 如果模块已导入，先移除
            if module_name in sys.modules:
                del sys.modules[module_name]

            start_time = time.perf_counter()
            importlib.import_module(module_name)
            end_time = time.perf_counter()

            import_time = end_time - start_time
            self.logger.debug(f"模块 {module_name} 导入时间: {import_time:.4f}秒")

            return import_time

        except ImportError as e:
            self.logger.warning(f"模块 {module_name} 导入失败: {e}")
            return float("inf")

    def benchmark_core_modules(self) -> Dict[str, float]:
        """基准测试核心模块导入"""
        core_modules = [
            # 核心模块
            "minicrm.core.config",
            "minicrm.core.constants",
            "minicrm.core.exceptions",
            "minicrm.core.logging",
            # 数据层模块
            "minicrm.data.database",
            "minicrm.models.customer",
            "minicrm.models.supplier",
            # 服务层模块
            "minicrm.services.customer_service",
            "minicrm.services.supplier_service",
            "minicrm.services.finance_service",
            # 配置模块
            "minicrm.config.settings",
            "minicrm.application_config",
        ]

        import_times = {}
        total_start = time.perf_counter()

        for module in core_modules:
            import_time = self.measure_import_time(module)
            import_times[module] = import_time

        total_time = time.perf_counter() - total_start
        import_times["_total_core_import_time"] = total_time

        self.logger.info(f"核心模块总导入时间: {total_time:.4f}秒")
        return import_times

    def benchmark_ui_modules(self, framework: str) -> Dict[str, float]:
        """基准测试UI模块导入

        Args:
            framework: UI框架 ("qt" 或 "ttk")
        """
        if framework.lower() == "qt":
            ui_modules = [
                "tkinter",
                "tkinter.ttk",
                "tkinter.font",
                "minicrm.ui.main_window",
                "minicrm.ui.customer_panel",
                "minicrm.ui.supplier_panel",
            ]
        else:  # TTK
            ui_modules = [
                "tkinter",
                "tkinter.ttk",
                "minicrm.ui.ttk_base.main_window_ttk",
                "minicrm.ui.ttk_base.theme_manager",
                "minicrm.ui.ttk_base.event_manager",
            ]

        import_times = {}
        total_start = time.perf_counter()

        for module in ui_modules:
            import_time = self.measure_import_time(module)
            import_times[module] = import_time

        total_time = time.perf_counter() - total_start
        import_times[f"_total_{framework}_ui_import_time"] = total_time

        self.logger.info(f"{framework.upper()} UI模块总导入时间: {total_time:.4f}秒")
        return import_times


class DatabaseInitializationBenchmark:
    """数据库初始化性能基准测试"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def measure_database_initialization(self) -> Dict[str, float]:
        """测量数据库初始化时间"""
        try:
            from minicrm.config.settings import get_config
            from minicrm.data.database import DatabaseManager

            config = get_config()

            # 测量数据库管理器创建时间
            start_time = time.perf_counter()
            db_manager = DatabaseManager(config.database.path)
            creation_time = time.perf_counter() - start_time

            # 测量数据库初始化时间
            start_time = time.perf_counter()
            db_manager.initialize_database()
            init_time = time.perf_counter() - start_time

            # 测量连接时间
            start_time = time.perf_counter()
            connection = db_manager.get_connection()
            connection_time = time.perf_counter() - start_time

            # 清理
            connection.close()

            results = {
                "db_manager_creation_time": creation_time,
                "db_initialization_time": init_time,
                "db_connection_time": connection_time,
                "total_db_time": creation_time + init_time + connection_time,
            }

            self.logger.info(f"数据库初始化总时间: {results['total_db_time']:.4f}秒")
            return results

        except Exception as e:
            self.logger.error(f"数据库初始化测试失败: {e}")
            return {
                "db_manager_creation_time": float("inf"),
                "db_initialization_time": float("inf"),
                "db_connection_time": float("inf"),
                "total_db_time": float("inf"),
            }


class ServiceInitializationBenchmark:
    """服务层初始化性能基准测试"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def measure_service_initialization(self) -> Dict[str, float]:
        """测量服务层初始化时间"""
        try:
            from minicrm.application_config import (
                configure_application_dependencies,
                get_service,
            )
            from minicrm.services.customer_service import CustomerService
            from minicrm.services.finance_service import FinanceService
            from minicrm.services.supplier_service import SupplierService

            # 配置依赖注入
            start_time = time.perf_counter()
            configure_application_dependencies()
            config_time = time.perf_counter() - start_time

            # 测量各服务初始化时间
            services_times = {}

            # 客户服务
            start_time = time.perf_counter()
            customer_service = get_service(CustomerService)
            services_times["customer_service_init"] = time.perf_counter() - start_time

            # 供应商服务
            start_time = time.perf_counter()
            supplier_service = get_service(SupplierService)
            services_times["supplier_service_init"] = time.perf_counter() - start_time

            # 财务服务
            start_time = time.perf_counter()
            finance_service = get_service(FinanceService)
            services_times["finance_service_init"] = time.perf_counter() - start_time

            # 计算总时间
            total_service_time = sum(services_times.values())

            results = {
                "dependency_config_time": config_time,
                "total_service_init_time": total_service_time,
                **services_times,
            }

            self.logger.info(f"服务层初始化总时间: {total_service_time:.4f}秒")
            return results

        except Exception as e:
            self.logger.error(f"服务层初始化测试失败: {e}")
            return {
                "dependency_config_time": float("inf"),
                "total_service_init_time": float("inf"),
            }


class ApplicationStartupBenchmark(BaseBenchmark):
    """应用程序启动性能基准测试"""

    def __init__(self):
        super().__init__("application_startup_performance")
        self.module_benchmark = ModuleImportBenchmark()
        self.db_benchmark = DatabaseInitializationBenchmark()
        self.service_benchmark = ServiceInitializationBenchmark()

    def run_qt_test(self) -> PerformanceMetrics:
        """运行Qt版本启动测试"""
        metrics = PerformanceMetrics()

        try:
            self.logger.info("开始Qt应用启动性能测试...")

            # 清理环境
            self._cleanup_environment()

            total_start_time = time.perf_counter()

            # 1. 测量核心模块导入
            core_import_times = self.module_benchmark.benchmark_core_modules()

            # 2. 测量Qt UI模块导入
            qt_ui_import_times = self.module_benchmark.benchmark_ui_modules("qt")

            # 3. 测量数据库初始化
            db_times = self.db_benchmark.measure_database_initialization()

            # 4. 测量服务层初始化
            service_times = self.service_benchmark.measure_service_initialization()

            # 5. 测量Qt应用程序创建
            qt_app_time = self._measure_qt_application_creation()

            total_startup_time = time.perf_counter() - total_start_time

            # 设置指标
            metrics.startup_time = total_startup_time
            metrics.additional_metrics.update(
                {
                    "core_import_time": core_import_times.get(
                        "_total_core_import_time", 0
                    ),
                    "ui_import_time": qt_ui_import_times.get(
                        "_total_qt_ui_import_time", 0
                    ),
                    "database_init_time": db_times.get("total_db_time", 0),
                    "service_init_time": service_times.get(
                        "total_service_init_time", 0
                    ),
                    "qt_app_creation_time": qt_app_time,
                    "detailed_import_times": {
                        **core_import_times,
                        **qt_ui_import_times,
                    },
                    "detailed_db_times": db_times,
                    "detailed_service_times": service_times,
                }
            )

            self.logger.info(f"Qt应用启动总时间: {total_startup_time:.4f}秒")

        except Exception as e:
            self.logger.error(f"Qt启动测试失败: {e}")
            metrics.startup_time = float("inf")

        return metrics

    def run_ttk_test(self) -> PerformanceMetrics:
        """运行TTK版本启动测试"""
        metrics = PerformanceMetrics()

        try:
            self.logger.info("开始TTK应用启动性能测试...")

            # 清理环境
            self._cleanup_environment()

            total_start_time = time.perf_counter()

            # 1. 测量核心模块导入
            core_import_times = self.module_benchmark.benchmark_core_modules()

            # 2. 测量TTK UI模块导入
            ttk_ui_import_times = self.module_benchmark.benchmark_ui_modules("ttk")

            # 3. 测量数据库初始化
            db_times = self.db_benchmark.measure_database_initialization()

            # 4. 测量服务层初始化
            service_times = self.service_benchmark.measure_service_initialization()

            # 5. 测量TTK应用程序创建
            ttk_app_time = self._measure_ttk_application_creation()

            total_startup_time = time.perf_counter() - total_start_time

            # 设置指标
            metrics.startup_time = total_startup_time
            metrics.additional_metrics.update(
                {
                    "core_import_time": core_import_times.get(
                        "_total_core_import_time", 0
                    ),
                    "ui_import_time": ttk_ui_import_times.get(
                        "_total_ttk_ui_import_time", 0
                    ),
                    "database_init_time": db_times.get("total_db_time", 0),
                    "service_init_time": service_times.get(
                        "total_service_init_time", 0
                    ),
                    "ttk_app_creation_time": ttk_app_time,
                    "detailed_import_times": {
                        **core_import_times,
                        **ttk_ui_import_times,
                    },
                    "detailed_db_times": db_times,
                    "detailed_service_times": service_times,
                }
            )

            self.logger.info(f"TTK应用启动总时间: {total_startup_time:.4f}秒")

        except Exception as e:
            self.logger.error(f"TTK启动测试失败: {e}")
            metrics.startup_time = float("inf")

        return metrics

    def _cleanup_environment(self) -> None:
        """清理测试环境"""
        # 清理已导入的模块（保留系统模块）
        modules_to_remove = []
        for module_name in sys.modules:
            if module_name.startswith("minicrm"):
                modules_to_remove.append(module_name)

        for module_name in modules_to_remove:
            try:
                del sys.modules[module_name]
            except KeyError:
                pass

        # 强制垃圾回收
        gc.collect()

    def _measure_qt_application_creation(self) -> float:
        """测量Qt应用程序创建时间"""
        try:
            start_time = time.perf_counter()

            # 导入并创建Qt应用
            from minicrm.application import MiniCRMApplication
            from minicrm.config.settings import get_config

            config = get_config()
            app = MiniCRMApplication(config)

            creation_time = time.perf_counter() - start_time

            # 清理
            app.shutdown()

            return creation_time

        except Exception as e:
            self.logger.error(f"Qt应用创建测试失败: {e}")
            return float("inf")

    def _measure_ttk_application_creation(self) -> float:
        """测量TTK应用程序创建时间"""
        try:
            start_time = time.perf_counter()

            # 导入并创建TTK应用
            from minicrm.application_ttk import MiniCRMApplicationTTK
            from minicrm.config.settings import get_config

            config = get_config()
            app = MiniCRMApplicationTTK(config)

            creation_time = time.perf_counter() - start_time

            # 清理
            app.shutdown()

            return creation_time

        except Exception as e:
            self.logger.error(f"TTK应用创建测试失败: {e}")
            return float("inf")


class StartupPerformanceTestSuite(unittest.TestCase):
    """启动性能测试套件"""

    def setUp(self):
        """测试准备"""
        self.benchmark = ApplicationStartupBenchmark()

    def test_qt_startup_performance(self):
        """测试Qt启动性能"""
        metrics = self.benchmark.run_qt_test()

        # 验证启动时间要求（3秒）
        self.assertLess(
            metrics.startup_time,
            3.0,
            f"Qt启动时间超过要求: {metrics.startup_time:.3f}秒",
        )

        # 验证各阶段时间合理性
        core_import_time = metrics.additional_metrics.get("core_import_time", 0)
        self.assertLess(core_import_time, 1.0, "核心模块导入时间过长")

        ui_import_time = metrics.additional_metrics.get("ui_import_time", 0)
        self.assertLess(ui_import_time, 1.0, "UI模块导入时间过长")

        db_init_time = metrics.additional_metrics.get("database_init_time", 0)
        self.assertLess(db_init_time, 0.5, "数据库初始化时间过长")

    def test_ttk_startup_performance(self):
        """测试TTK启动性能"""
        metrics = self.benchmark.run_ttk_test()

        # 验证启动时间要求（3秒）
        self.assertLess(
            metrics.startup_time,
            3.0,
            f"TTK启动时间超过要求: {metrics.startup_time:.3f}秒",
        )

        # 验证各阶段时间合理性
        core_import_time = metrics.additional_metrics.get("core_import_time", 0)
        self.assertLess(core_import_time, 1.0, "核心模块导入时间过长")

        ui_import_time = metrics.additional_metrics.get("ui_import_time", 0)
        self.assertLess(ui_import_time, 0.5, "TTK UI模块导入时间过长")

        db_init_time = metrics.additional_metrics.get("database_init_time", 0)
        self.assertLess(db_init_time, 0.5, "数据库初始化时间过长")

    def test_startup_performance_comparison(self):
        """测试启动性能对比"""
        qt_metrics = self.benchmark.run_qt_test()
        ttk_metrics = self.benchmark.run_ttk_test()

        # 比较启动时间
        if qt_metrics.startup_time != float(
            "inf"
        ) and ttk_metrics.startup_time != float("inf"):
            improvement = (
                (qt_metrics.startup_time - ttk_metrics.startup_time)
                / qt_metrics.startup_time
                * 100
            )

            print("\n启动性能对比:")
            print(f"Qt启动时间: {qt_metrics.startup_time:.3f}秒")
            print(f"TTK启动时间: {ttk_metrics.startup_time:.3f}秒")
            print(f"性能变化: {improvement:+.1f}%")

            # TTK启动时间不应该比Qt慢太多（允许20%的差异）
            self.assertLess(
                ttk_metrics.startup_time,
                qt_metrics.startup_time * 1.2,
                "TTK启动时间比Qt慢太多",
            )


def run_startup_performance_tests():
    """运行启动性能测试"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("开始MiniCRM启动性能测试...")
    print("=" * 50)

    # 运行基准测试
    benchmark = ApplicationStartupBenchmark()
    qt_result, ttk_result = benchmark.run_benchmark()

    # 输出结果
    print("\n启动性能测试结果:")
    print(f"Qt版本: {qt_result.metrics.startup_time:.3f}秒")
    print(f"TTK版本: {ttk_result.metrics.startup_time:.3f}秒")

    if qt_result.success and ttk_result.success:
        improvement = (
            (qt_result.metrics.startup_time - ttk_result.metrics.startup_time)
            / qt_result.metrics.startup_time
            * 100
        )
        print(f"性能变化: {improvement:+.1f}%")

    # 检查是否满足性能要求
    requirement_met = ttk_result.metrics.startup_time <= 3.0
    print(f"性能要求(≤3秒): {'✓ 满足' if requirement_met else '✗ 不满足'}")

    print("\n启动性能测试完成！")


if __name__ == "__main__":
    run_startup_performance_tests()
