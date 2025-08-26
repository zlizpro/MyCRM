"""性能基准测试.

测试MiniCRM应用程序的性能指标，包括启动时间、内存使用、
响应时间等关键性能指标的基准测试。
"""

import gc
from pathlib import Path
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import unittest

import psutil


# 添加src目录到Python路径
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from minicrm.core.resource_manager import ResourceManager


class PerformanceBenchmark:
    """性能基准测试工具类."""

    def __init__(self):
        """初始化性能基准测试."""
        self.process = psutil.Process()
        self.benchmarks = {}

    def measure_time(self, func, *args, **kwargs):
        """测量函数执行时间."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        return result, execution_time

    def measure_memory(self, func, *args, **kwargs):
        """测量函数内存使用."""
        # 强制垃圾回收
        gc.collect()

        # 记录初始内存
        initial_memory = self.process.memory_info().rss

        # 执行函数
        result = func(*args, **kwargs)

        # 记录执行后内存
        final_memory = self.process.memory_info().rss
        memory_delta = final_memory - initial_memory

        return result, memory_delta

    def benchmark_function(self, name, func, *args, **kwargs):
        """对函数进行完整的性能基准测试."""
        # 时间测量
        result, execution_time = self.measure_time(func, *args, **kwargs)

        # 内存测量
        _, memory_delta = self.measure_memory(func, *args, **kwargs)

        # 记录基准数据
        self.benchmarks[name] = {
            "execution_time": execution_time,
            "memory_delta": memory_delta,
            "memory_delta_mb": memory_delta / 1024 / 1024,
        }

        return result

    def get_benchmark_report(self):
        """获取基准测试报告."""
        return self.benchmarks.copy()


class TestApplicationStartupPerformance(unittest.TestCase):
    """应用程序启动性能测试."""

    def setUp(self):
        """测试准备."""
        self.benchmark = PerformanceBenchmark()

    def test_resource_manager_initialization_performance(self):
        """测试资源管理器初始化性能."""

        def init_resource_manager():
            return ResourceManager()

        # 基准测试
        resource_manager = self.benchmark.benchmark_function(
            "resource_manager_init", init_resource_manager
        )

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        init_time = benchmarks["resource_manager_init"]["execution_time"]

        # 资源管理器初始化应该在100ms内完成
        self.assertLess(init_time, 0.1, f"资源管理器初始化时间过长: {init_time:.3f}s")

        print(f"资源管理器初始化时间: {init_time:.3f}s")

    def test_tkinter_root_creation_performance(self):
        """测试tkinter根窗口创建性能."""

        def create_root_window():
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口
            return root

        # 基准测试
        root = self.benchmark.benchmark_function(
            "tkinter_root_creation", create_root_window
        )

        try:
            # 验证性能指标
            benchmarks = self.benchmark.get_benchmark_report()
            creation_time = benchmarks["tkinter_root_creation"]["execution_time"]

            # tkinter根窗口创建应该在50ms内完成
            self.assertLess(
                creation_time, 0.05, f"tkinter根窗口创建时间过长: {creation_time:.3f}s"
            )

            print(f"tkinter根窗口创建时间: {creation_time:.3f}s")

        finally:
            root.destroy()

    def test_module_import_performance(self):
        """测试模块导入性能."""
        # 测试核心模块导入
        modules_to_test = [
            "minicrm.core.resource_manager",
            "minicrm.core.constants",
            "minicrm.core.exceptions",
        ]

        total_import_time = 0

        for module_name in modules_to_test:

            def import_module():
                return __import__(module_name, fromlist=[""])

            # 基准测试
            self.benchmark.benchmark_function(f"import_{module_name}", import_module)

            benchmarks = self.benchmark.get_benchmark_report()
            import_time = benchmarks[f"import_{module_name}"]["execution_time"]
            total_import_time += import_time

            print(f"{module_name} 导入时间: {import_time:.3f}s")

        # 总导入时间应该在200ms内
        self.assertLess(
            total_import_time, 0.2, f"模块导入总时间过长: {total_import_time:.3f}s"
        )


class TestUIComponentPerformance(unittest.TestCase):
    """UI组件性能测试."""

    def setUp(self):
        """测试准备."""
        self.benchmark = PerformanceBenchmark()
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理."""
        self.root.destroy()

    def test_component_creation_performance(self):
        """测试组件创建性能."""

        def create_basic_components():
            frame = ttk.Frame(self.root)
            label = ttk.Label(frame, text="性能测试标签")
            entry = ttk.Entry(frame)
            button = ttk.Button(frame, text="测试按钮")
            combobox = ttk.Combobox(frame, values=["选项1", "选项2", "选项3"])

            return frame, label, entry, button, combobox

        # 基准测试
        components = self.benchmark.benchmark_function(
            "basic_components_creation", create_basic_components
        )

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        creation_time = benchmarks["basic_components_creation"]["execution_time"]

        # 基本组件创建应该在10ms内完成
        self.assertLess(
            creation_time, 0.01, f"基本组件创建时间过长: {creation_time:.3f}s"
        )

        print(f"基本组件创建时间: {creation_time:.3f}s")

    def test_treeview_performance(self):
        """测试Treeview性能."""

        def create_and_populate_treeview():
            # 创建Treeview
            columns = ("ID", "名称", "电话", "邮箱", "地址")
            tree = ttk.Treeview(self.root, columns=columns, show="headings")

            # 配置列
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            # 插入1000条测试数据
            for i in range(1000):
                tree.insert(
                    "",
                    "end",
                    values=(
                        i + 1,
                        f"客户{i + 1}",
                        f"138{i:08d}",
                        f"customer{i + 1}@example.com",
                        f"地址{i + 1}",
                    ),
                )

            return tree

        # 基准测试
        tree = self.benchmark.benchmark_function(
            "treeview_1000_items", create_and_populate_treeview
        )

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        creation_time = benchmarks["treeview_1000_items"]["execution_time"]
        memory_usage = benchmarks["treeview_1000_items"]["memory_delta_mb"]

        # 1000条数据的Treeview应该在500ms内创建完成
        self.assertLess(
            creation_time, 0.5, f"Treeview创建时间过长: {creation_time:.3f}s"
        )

        # 内存使用应该在合理范围内（小于50MB）
        self.assertLess(memory_usage, 50, f"Treeview内存使用过多: {memory_usage:.2f}MB")

        print(f"Treeview(1000项)创建时间: {creation_time:.3f}s")
        print(f"Treeview内存使用: {memory_usage:.2f}MB")

    def test_form_creation_performance(self):
        """测试表单创建性能."""

        def create_complex_form():
            form_frame = ttk.Frame(self.root)

            # 创建20个表单字段
            widgets = []
            for i in range(20):
                label = ttk.Label(form_frame, text=f"字段{i + 1}:")
                entry = ttk.Entry(form_frame)
                widgets.extend([label, entry])

            return form_frame, widgets

        # 基准测试
        form_data = self.benchmark.benchmark_function(
            "complex_form_creation", create_complex_form
        )

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        creation_time = benchmarks["complex_form_creation"]["execution_time"]

        # 复杂表单创建应该在50ms内完成
        self.assertLess(
            creation_time, 0.05, f"复杂表单创建时间过长: {creation_time:.3f}s"
        )

        print(f"复杂表单(20字段)创建时间: {creation_time:.3f}s")


class TestDataProcessingPerformance(unittest.TestCase):
    """数据处理性能测试."""

    def setUp(self):
        """测试准备."""
        self.benchmark = PerformanceBenchmark()

    def test_large_dataset_processing(self):
        """测试大数据集处理性能."""

        def process_large_dataset():
            # 创建10000条客户数据
            customers = []
            for i in range(10000):
                customers.append(
                    {
                        "id": i + 1,
                        "name": f"客户{i + 1}",
                        "phone": f"138{i:08d}",
                        "email": f"customer{i + 1}@example.com",
                        "type": ["生态板", "家具板", "阻燃板"][i % 3],
                    }
                )

            # 执行搜索和筛选操作
            search_results = [c for c in customers if "1000" in c["name"]]
            type_filter_results = [c for c in customers if c["type"] == "生态板"]

            return len(customers), len(search_results), len(type_filter_results)

        # 基准测试
        results = self.benchmark.benchmark_function(
            "large_dataset_processing", process_large_dataset
        )

        # 验证结果
        total_count, search_count, filter_count = results
        self.assertEqual(total_count, 10000)
        self.assertGreater(search_count, 0)
        self.assertGreater(filter_count, 0)

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        processing_time = benchmarks["large_dataset_processing"]["execution_time"]
        memory_usage = benchmarks["large_dataset_processing"]["memory_delta_mb"]

        # 10000条数据处理应该在1秒内完成
        self.assertLess(
            processing_time, 1.0, f"大数据集处理时间过长: {processing_time:.3f}s"
        )

        # 内存使用应该在合理范围内（小于100MB）
        self.assertLess(
            memory_usage, 100, f"大数据集处理内存使用过多: {memory_usage:.2f}MB"
        )

        print(f"大数据集(10000条)处理时间: {processing_time:.3f}s")
        print(f"大数据集处理内存使用: {memory_usage:.2f}MB")

    def test_search_performance(self):
        """测试搜索性能."""
        # 准备测试数据
        test_data = []
        for i in range(5000):
            test_data.append(
                {
                    "name": f"客户{i + 1}",
                    "phone": f"138{i:08d}",
                    "keywords": f"关键词{i % 100}",
                }
            )

        def perform_search(keyword):
            return [
                item
                for item in test_data
                if keyword in item["name"] or keyword in item["keywords"]
            ]

        # 测试不同搜索场景
        search_scenarios = [
            ("客户1", "精确搜索"),
            ("客户", "模糊搜索"),
            ("关键词1", "关键词搜索"),
            ("不存在的内容", "无结果搜索"),
        ]

        for keyword, scenario_name in search_scenarios:
            results = self.benchmark.benchmark_function(
                f"search_{scenario_name}", perform_search, keyword
            )

            benchmarks = self.benchmark.get_benchmark_report()
            search_time = benchmarks[f"search_{scenario_name}"]["execution_time"]

            # 搜索应该在100ms内完成
            self.assertLess(
                search_time, 0.1, f"{scenario_name}时间过长: {search_time:.3f}s"
            )

            print(f"{scenario_name}时间: {search_time:.3f}s, 结果数: {len(results)}")


class TestMemoryPerformance(unittest.TestCase):
    """内存性能测试."""

    def setUp(self):
        """测试准备."""
        self.benchmark = PerformanceBenchmark()
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        """测试清理."""
        self.root.destroy()

    def test_memory_leak_detection(self):
        """测试内存泄漏检测."""
        import gc

        # 记录初始对象数量
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建和销毁大量组件
        def create_and_destroy_components():
            components = []

            # 创建1000个组件
            for i in range(1000):
                frame = ttk.Frame(self.root)
                label = ttk.Label(frame, text=f"测试{i}")
                components.append((frame, label))

            # 销毁所有组件
            for frame, label in components:
                label.destroy()
                frame.destroy()

            components.clear()
            return len(components)

        # 执行多次创建销毁循环
        for cycle in range(5):
            self.benchmark.benchmark_function(
                f"memory_cycle_{cycle}", create_and_destroy_components
            )

            # 强制垃圾回收
            gc.collect()

        # 检查最终对象数量
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects

        print(f"初始对象数: {initial_objects}")
        print(f"最终对象数: {final_objects}")
        print(f"对象增加数: {object_increase}")

        # 对象增加应该在合理范围内（小于初始对象数的10%）
        max_acceptable_increase = initial_objects * 0.1
        self.assertLess(
            object_increase,
            max_acceptable_increase,
            f"可能存在内存泄漏，对象增加过多: {object_increase}",
        )

    def test_resource_cleanup_performance(self):
        """测试资源清理性能."""

        def create_resources():
            # 创建多个资源管理器实例
            managers = []
            for i in range(100):
                manager = ResourceManager()
                managers.append(manager)
            return managers

        def cleanup_resources(managers):
            for manager in managers:
                manager.clear_cache()
            managers.clear()

        # 创建资源
        managers = self.benchmark.benchmark_function(
            "resource_creation", create_resources
        )

        # 清理资源
        self.benchmark.benchmark_function(
            "resource_cleanup", cleanup_resources, managers
        )

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        cleanup_time = benchmarks["resource_cleanup"]["execution_time"]

        # 资源清理应该在50ms内完成
        self.assertLess(cleanup_time, 0.05, f"资源清理时间过长: {cleanup_time:.3f}s")

        print(f"资源清理时间: {cleanup_time:.3f}s")


class TestConcurrencyPerformance(unittest.TestCase):
    """并发性能测试."""

    def setUp(self):
        """测试准备."""
        self.benchmark = PerformanceBenchmark()

    def test_thread_safety_performance(self):
        """测试线程安全性能."""

        # 共享数据
        shared_data = {"counter": 0}
        lock = threading.Lock()

        def worker_function(worker_id, iterations):
            for i in range(iterations):
                with lock:
                    shared_data["counter"] += 1

        def run_concurrent_workers():
            threads = []
            worker_count = 10
            iterations_per_worker = 1000

            # 创建并启动线程
            for i in range(worker_count):
                thread = threading.Thread(
                    target=worker_function, args=(i, iterations_per_worker)
                )
                threads.append(thread)
                thread.start()

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            return shared_data["counter"]

        # 基准测试
        final_count = self.benchmark.benchmark_function(
            "concurrent_workers", run_concurrent_workers
        )

        # 验证结果
        expected_count = 10 * 1000
        self.assertEqual(final_count, expected_count)

        # 验证性能指标
        benchmarks = self.benchmark.get_benchmark_report()
        execution_time = benchmarks["concurrent_workers"]["execution_time"]

        # 并发执行应该在2秒内完成
        self.assertLess(execution_time, 2.0, f"并发执行时间过长: {execution_time:.3f}s")

        print(f"并发执行时间: {execution_time:.3f}s")
        print(f"最终计数: {final_count}")


def run_performance_benchmarks():
    """运行性能基准测试套件."""
    # 创建测试套件
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTest(unittest.makeSuite(TestApplicationStartupPerformance))
    suite.addTest(unittest.makeSuite(TestUIComponentPerformance))
    suite.addTest(unittest.makeSuite(TestDataProcessingPerformance))
    suite.addTest(unittest.makeSuite(TestMemoryPerformance))
    suite.addTest(unittest.makeSuite(TestConcurrencyPerformance))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("运行MiniCRM性能基准测试")
    print(
        f"系统信息: {psutil.cpu_count()}核CPU, {psutil.virtual_memory().total / 1024**3:.1f}GB内存"
    )
    print("=" * 60)

    success = run_performance_benchmarks()

    print("=" * 60)
    if success:
        print("✅ 所有性能基准测试通过")
    else:
        print("❌ 部分性能基准测试失败")

    sys.exit(0 if success else 1)
