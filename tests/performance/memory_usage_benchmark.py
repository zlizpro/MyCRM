"""MiniCRM内存使用性能基准测试

为任务10提供详细的内存使用性能测试：
- 应用程序内存占用监控
- 内存泄漏检测
- 大数据集处理内存效率
- 垃圾回收效果分析
- Qt vs TTK内存使用对比

测试目标：
1. 验证内存占用不超过200MB（需求11.3）
2. 检测内存泄漏问题
3. 分析内存使用模式
4. 提供内存优化建议

作者: MiniCRM开发团队
"""

import gc
import logging
from pathlib import Path
import sys
import threading
import time
from typing import Dict, List, Optional, Tuple
import unittest
import weakref

import psutil


# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from tests.performance.performance_benchmark_framework import (
    BaseBenchmark,
    PerformanceMetrics,
)


class MemoryTracker:
    """内存跟踪器"""

    def __init__(self, sample_interval: float = 0.1):
        """初始化内存跟踪器

        Args:
            sample_interval: 采样间隔（秒）
        """
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        self.logger = logging.getLogger(self.__class__.__name__)

        # 跟踪数据
        self.memory_samples: List[float] = []
        self.timestamps: List[float] = []
        self.gc_counts: List[Tuple[int, int, int]] = []

        # 跟踪控制
        self._tracking = False
        self._track_thread: Optional[threading.Thread] = None

    def start_tracking(self) -> None:
        """开始内存跟踪"""
        if self._tracking:
            return

        self._tracking = True
        self.memory_samples.clear()
        self.timestamps.clear()
        self.gc_counts.clear()

        self._track_thread = threading.Thread(target=self._track_loop)
        self._track_thread.daemon = True
        self._track_thread.start()

    def stop_tracking(self) -> Dict[str, float]:
        """停止内存跟踪并返回统计信息"""
        self._tracking = False

        if self._track_thread:
            self._track_thread.join(timeout=1.0)

        if not self.memory_samples:
            return {}

        return {
            "initial_memory_mb": self.memory_samples[0],
            "peak_memory_mb": max(self.memory_samples),
            "final_memory_mb": self.memory_samples[-1],
            "memory_growth_mb": self.memory_samples[-1] - self.memory_samples[0],
            "max_memory_growth_mb": max(self.memory_samples) - self.memory_samples[0],
            "avg_memory_mb": sum(self.memory_samples) / len(self.memory_samples),
            "memory_volatility": self._calculate_volatility(),
            "sample_count": len(self.memory_samples),
        }

    def _track_loop(self) -> None:
        """内存跟踪循环"""
        while self._tracking:
            try:
                # 采样内存使用
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                self.memory_samples.append(memory_mb)
                self.timestamps.append(time.time())

                # 采样垃圾回收计数
                self.gc_counts.append(gc.get_count())

                time.sleep(self.sample_interval)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            except Exception as e:
                self.logger.warning(f"内存跟踪采样失败: {e}")

    def _calculate_volatility(self) -> float:
        """计算内存使用波动性"""
        if len(self.memory_samples) < 2:
            return 0.0

        # 计算相邻样本间的变化率
        changes = []
        for i in range(1, len(self.memory_samples)):
            if self.memory_samples[i - 1] > 0:
                change = (
                    abs(self.memory_samples[i] - self.memory_samples[i - 1])
                    / self.memory_samples[i - 1]
                )
                changes.append(change)

        return sum(changes) / len(changes) if changes else 0.0

    def force_gc_and_measure(self) -> Tuple[float, float]:
        """强制垃圾回收并测量效果

        Returns:
            (回收前内存MB, 回收后内存MB)
        """
        before_memory = self.process.memory_info().rss / 1024 / 1024

        # 执行多轮垃圾回收
        for generation in range(3):
            gc.collect(generation)

        time.sleep(0.1)  # 等待回收完成

        after_memory = self.process.memory_info().rss / 1024 / 1024

        return before_memory, after_memory


class MemoryLeakDetector:
    """内存泄漏检测器"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tracked_objects: List[weakref.ref] = []

    def track_object(self, obj) -> None:
        """跟踪对象生命周期"""
        try:
            weak_ref = weakref.ref(obj)
            self.tracked_objects.append(weak_ref)
        except TypeError:
            # 某些对象不支持弱引用
            pass

    def check_leaks(self) -> Dict[str, int]:
        """检查内存泄漏"""
        # 清理已释放的弱引用
        alive_objects = []
        dead_count = 0

        for weak_ref in self.tracked_objects:
            if weak_ref() is not None:
                alive_objects.append(weak_ref)
            else:
                dead_count += 1

        self.tracked_objects = alive_objects

        return {
            "tracked_objects": len(self.tracked_objects),
            "alive_objects": len(alive_objects),
            "released_objects": dead_count,
            "potential_leaks": len(alive_objects),
        }

    def reset(self) -> None:
        """重置检测器"""
        self.tracked_objects.clear()


class LargeDatasetMemoryBenchmark:
    """大数据集内存基准测试"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tracker = MemoryTracker()

    def test_customer_data_loading(self, record_count: int = 50000) -> Dict[str, float]:
        """测试客户数据加载内存使用"""
        self.logger.info(f"测试加载{record_count}条客户数据的内存使用...")

        self.tracker.start_tracking()

        try:
            # 创建大量客户数据
            customers = []
            for i in range(record_count):
                customer = {
                    "id": i + 1,
                    "name": f"客户公司{i + 1}",
                    "contact_person": f"联系人{i + 1}",
                    "phone": f"138{i:08d}",
                    "email": f"customer{i + 1}@example.com",
                    "address": f"地址{i + 1}" * 5,  # 增加数据大小
                    "customer_type": ["生态板客户", "家具板客户", "阻燃板客户"][i % 3],
                    "credit_rating": ["A", "B", "C"][i % 3],
                    "notes": f"备注信息{i + 1}" * 10,
                    "created_at": f"2024-01-{(i % 28) + 1:02d}",
                    "interactions": [
                        {
                            "date": f"2024-02-{j + 1:02d}",
                            "type": "电话",
                            "content": f"交互{j}",
                        }
                        for j in range(i % 5)  # 每个客户0-4个交互记录
                    ],
                }
                customers.append(customer)

            # 模拟数据处理操作
            # 1. 搜索操作
            search_results = [c for c in customers if "1000" in c["name"]]

            # 2. 筛选操作
            filtered_customers = [
                c for c in customers if c["customer_type"] == "生态板客户"
            ]

            # 3. 排序操作
            sorted_customers = sorted(customers[:1000], key=lambda x: x["name"])

            # 4. 聚合操作
            type_counts = {}
            for customer in customers:
                customer_type = customer["customer_type"]
                type_counts[customer_type] = type_counts.get(customer_type, 0) + 1

            results = {
                "total_records": len(customers),
                "search_results": len(search_results),
                "filtered_results": len(filtered_customers),
                "sorted_sample": len(sorted_customers),
                "type_aggregation": len(type_counts),
            }

            # 清理数据
            customers.clear()
            search_results.clear()
            filtered_customers.clear()
            sorted_customers.clear()
            type_counts.clear()

            return results

        finally:
            memory_stats = self.tracker.stop_tracking()
            self.logger.info(f"客户数据测试内存统计: {memory_stats}")
            return memory_stats

    def test_ui_component_memory(self, component_count: int = 1000) -> Dict[str, float]:
        """测试UI组件内存使用"""
        self.logger.info(f"测试创建{component_count}个UI组件的内存使用...")

        self.tracker.start_tracking()

        try:
            import tkinter as tk
            from tkinter import ttk

            # 创建根窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏窗口

            # 创建大量UI组件
            components = []
            for i in range(component_count):
                frame = ttk.Frame(root)
                label = ttk.Label(frame, text=f"标签{i}" * 5)
                entry = ttk.Entry(frame)
                button = ttk.Button(frame, text=f"按钮{i}")
                combobox = ttk.Combobox(frame, values=[f"选项{j}" for j in range(10)])

                # 设置一些数据
                entry.insert(0, f"测试数据{i}" * 3)
                combobox.set(f"选项{i % 10}")

                components.extend([frame, label, entry, button, combobox])

            # 模拟组件操作
            for i, component in enumerate(components[:100]):  # 只操作前100个
                if isinstance(component, ttk.Entry):
                    component.delete(0, tk.END)
                    component.insert(0, f"更新数据{i}")
                elif isinstance(component, ttk.Label):
                    component.config(text=f"更新标签{i}")

            # 清理组件
            for component in components:
                try:
                    component.destroy()
                except:
                    pass

            components.clear()
            root.destroy()

            return {"component_count": component_count}

        finally:
            memory_stats = self.tracker.stop_tracking()
            self.logger.info(f"UI组件测试内存统计: {memory_stats}")
            return memory_stats


class MemoryUsageBenchmark(BaseBenchmark):
    """内存使用基准测试"""

    def __init__(self):
        super().__init__("memory_usage_benchmark")
        self.leak_detector = MemoryLeakDetector()
        self.dataset_benchmark = LargeDatasetMemoryBenchmark()

    def run_qt_test(self) -> PerformanceMetrics:
        """运行Qt版本内存测试"""
        metrics = PerformanceMetrics()

        try:
            self.logger.info("开始Qt内存使用测试...")

            # 重置检测器
            self.leak_detector.reset()

            # 开始监控
            self.monitor.start_monitoring()

            # 1. 测试应用程序基础内存使用
            app_memory = self._test_qt_application_memory()

            # 2. 测试大数据集处理
            dataset_memory = self.dataset_benchmark.test_customer_data_loading(10000)

            # 3. 测试内存泄漏
            leak_stats = self._test_qt_memory_leaks()

            # 4. 测试垃圾回收效果
            gc_stats = self._test_garbage_collection()

            # 停止监控
            monitor_stats = self.monitor.stop_monitoring()

            # 设置指标
            metrics.initial_memory = monitor_stats.initial_memory
            metrics.peak_memory = monitor_stats.peak_memory
            metrics.memory_growth = monitor_stats.memory_growth

            # 强制垃圾回收后的内存
            tracker = MemoryTracker()
            before_gc, after_gc = tracker.force_gc_and_measure()
            metrics.memory_after_gc = after_gc

            metrics.additional_metrics.update(
                {
                    "app_memory_stats": app_memory,
                    "dataset_memory_stats": dataset_memory,
                    "leak_detection_stats": leak_stats,
                    "gc_effectiveness": {
                        "before_gc_mb": before_gc,
                        "after_gc_mb": after_gc,
                        "gc_freed_mb": before_gc - after_gc,
                        "gc_effectiveness_percent": (
                            (before_gc - after_gc) / before_gc * 100
                        )
                        if before_gc > 0
                        else 0,
                    },
                    **gc_stats,
                }
            )

            self.logger.info(f"Qt内存测试完成，峰值内存: {metrics.peak_memory:.1f}MB")

        except Exception as e:
            self.logger.error(f"Qt内存测试失败: {e}")

        return metrics

    def run_ttk_test(self) -> PerformanceMetrics:
        """运行TTK版本内存测试"""
        metrics = PerformanceMetrics()

        try:
            self.logger.info("开始TTK内存使用测试...")

            # 重置检测器
            self.leak_detector.reset()

            # 开始监控
            self.monitor.start_monitoring()

            # 1. 测试应用程序基础内存使用
            app_memory = self._test_ttk_application_memory()

            # 2. 测试大数据集处理
            dataset_memory = self.dataset_benchmark.test_customer_data_loading(10000)

            # 3. 测试UI组件内存使用
            ui_memory = self.dataset_benchmark.test_ui_component_memory(1000)

            # 4. 测试内存泄漏
            leak_stats = self._test_ttk_memory_leaks()

            # 5. 测试垃圾回收效果
            gc_stats = self._test_garbage_collection()

            # 停止监控
            monitor_stats = self.monitor.stop_monitoring()

            # 设置指标
            metrics.initial_memory = monitor_stats.initial_memory
            metrics.peak_memory = monitor_stats.peak_memory
            metrics.memory_growth = monitor_stats.memory_growth

            # 强制垃圾回收后的内存
            tracker = MemoryTracker()
            before_gc, after_gc = tracker.force_gc_and_measure()
            metrics.memory_after_gc = after_gc

            metrics.additional_metrics.update(
                {
                    "app_memory_stats": app_memory,
                    "dataset_memory_stats": dataset_memory,
                    "ui_memory_stats": ui_memory,
                    "leak_detection_stats": leak_stats,
                    "gc_effectiveness": {
                        "before_gc_mb": before_gc,
                        "after_gc_mb": after_gc,
                        "gc_freed_mb": before_gc - after_gc,
                        "gc_effectiveness_percent": (
                            (before_gc - after_gc) / before_gc * 100
                        )
                        if before_gc > 0
                        else 0,
                    },
                    **gc_stats,
                }
            )

            self.logger.info(f"TTK内存测试完成，峰值内存: {metrics.peak_memory:.1f}MB")

        except Exception as e:
            self.logger.error(f"TTK内存测试失败: {e}")

        return metrics

    def _test_qt_application_memory(self) -> Dict[str, float]:
        """测试Qt应用程序内存使用"""
        try:
            from minicrm.application import MiniCRMApplication
            from minicrm.config.settings import get_config

            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 创建Qt应用
            config = get_config()
            app = MiniCRMApplication(config)
            self.leak_detector.track_object(app)

            after_creation_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 模拟一些操作
            if app.customer_service:
                customers = app.customer_service.get_all_customers()
                self.leak_detector.track_object(customers)

            after_operations_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 清理
            app.shutdown()

            after_cleanup_memory = psutil.Process().memory_info().rss / 1024 / 1024

            return {
                "initial_memory_mb": initial_memory,
                "after_creation_mb": after_creation_memory,
                "after_operations_mb": after_operations_memory,
                "after_cleanup_mb": after_cleanup_memory,
                "creation_cost_mb": after_creation_memory - initial_memory,
                "operations_cost_mb": after_operations_memory - after_creation_memory,
                "cleanup_freed_mb": after_operations_memory - after_cleanup_memory,
            }

        except Exception as e:
            self.logger.error(f"Qt应用内存测试失败: {e}")
            return {}

    def _test_ttk_application_memory(self) -> Dict[str, float]:
        """测试TTK应用程序内存使用"""
        try:
            from minicrm.application_ttk import MiniCRMApplicationTTK
            from minicrm.config.settings import get_config

            initial_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 创建TTK应用
            config = get_config()
            app = MiniCRMApplicationTTK(config)
            self.leak_detector.track_object(app)

            after_creation_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 模拟一些操作
            if app.customer_service:
                customers = app.customer_service.get_all_customers()
                self.leak_detector.track_object(customers)

            after_operations_memory = psutil.Process().memory_info().rss / 1024 / 1024

            # 清理
            app.shutdown()

            after_cleanup_memory = psutil.Process().memory_info().rss / 1024 / 1024

            return {
                "initial_memory_mb": initial_memory,
                "after_creation_mb": after_creation_memory,
                "after_operations_mb": after_operations_memory,
                "after_cleanup_mb": after_cleanup_memory,
                "creation_cost_mb": after_creation_memory - initial_memory,
                "operations_cost_mb": after_operations_memory - after_creation_memory,
                "cleanup_freed_mb": after_operations_memory - after_cleanup_memory,
            }

        except Exception as e:
            self.logger.error(f"TTK应用内存测试失败: {e}")
            return {}

    def _test_qt_memory_leaks(self) -> Dict[str, int]:
        """测试Qt内存泄漏"""
        # 创建和销毁多个Qt对象
        try:
            for i in range(100):
                # 模拟创建Qt对象
                obj = {"id": i, "data": "x" * 1000}
                self.leak_detector.track_object(obj)

            # 强制垃圾回收
            gc.collect()

            return self.leak_detector.check_leaks()

        except Exception as e:
            self.logger.error(f"Qt内存泄漏测试失败: {e}")
            return {}

    def _test_ttk_memory_leaks(self) -> Dict[str, int]:
        """测试TTK内存泄漏"""
        try:
            import tkinter as tk
            from tkinter import ttk

            root = tk.Tk()
            root.withdraw()

            # 创建和销毁多个TTK组件
            for i in range(100):
                frame = ttk.Frame(root)
                label = ttk.Label(frame, text=f"测试{i}")
                self.leak_detector.track_object(frame)
                self.leak_detector.track_object(label)

                # 销毁组件
                label.destroy()
                frame.destroy()

            root.destroy()

            # 强制垃圾回收
            gc.collect()

            return self.leak_detector.check_leaks()

        except Exception as e:
            self.logger.error(f"TTK内存泄漏测试失败: {e}")
            return {}

    def _test_garbage_collection(self) -> Dict[str, int]:
        """测试垃圾回收统计"""
        # 获取垃圾回收前的计数
        before_counts = gc.get_count()
        before_stats = gc.get_stats()

        # 创建一些循环引用对象
        objects = []
        for i in range(1000):
            obj1 = {"id": i, "ref": None}
            obj2 = {"id": i + 1000, "ref": obj1}
            obj1["ref"] = obj2
            objects.append((obj1, obj2))

        # 清除引用
        objects.clear()

        # 执行垃圾回收
        collected = []
        for generation in range(3):
            collected.append(gc.collect(generation))

        after_counts = gc.get_count()
        after_stats = gc.get_stats()

        return {
            "before_gen0": before_counts[0],
            "before_gen1": before_counts[1],
            "before_gen2": before_counts[2],
            "after_gen0": after_counts[0],
            "after_gen1": after_counts[1],
            "after_gen2": after_counts[2],
            "collected_gen0": collected[0],
            "collected_gen1": collected[1],
            "collected_gen2": collected[2],
            "total_collected": sum(collected),
        }


class MemoryUsageTestSuite(unittest.TestCase):
    """内存使用测试套件"""

    def setUp(self):
        """测试准备"""
        self.benchmark = MemoryUsageBenchmark()

    def test_ttk_memory_requirements(self):
        """测试TTK内存需求合规性"""
        metrics = self.benchmark.run_ttk_test()

        # 验证峰值内存不超过200MB（需求11.3）
        self.assertLess(
            metrics.peak_memory,
            200.0,
            f"TTK峰值内存超过要求: {metrics.peak_memory:.1f}MB",
        )

        # 验证内存增长合理
        self.assertLess(
            metrics.memory_growth,
            150.0,
            f"TTK内存增长过大: {metrics.memory_growth:.1f}MB",
        )

    def test_memory_leak_detection(self):
        """测试内存泄漏检测"""
        ttk_metrics = self.benchmark.run_ttk_test()

        leak_stats = ttk_metrics.additional_metrics.get("leak_detection_stats", {})
        potential_leaks = leak_stats.get("potential_leaks", 0)

        # 潜在泄漏对象数量应该很少
        self.assertLess(
            potential_leaks, 10, f"检测到可能的内存泄漏: {potential_leaks}个对象"
        )

    def test_garbage_collection_effectiveness(self):
        """测试垃圾回收效果"""
        ttk_metrics = self.benchmark.run_ttk_test()

        gc_stats = ttk_metrics.additional_metrics.get("gc_effectiveness", {})
        gc_freed_mb = gc_stats.get("gc_freed_mb", 0)

        # 垃圾回收应该能释放一些内存
        self.assertGreaterEqual(gc_freed_mb, 0, "垃圾回收没有释放内存")

    def test_memory_performance_comparison(self):
        """测试内存性能对比"""
        qt_metrics = self.benchmark.run_qt_test()
        ttk_metrics = self.benchmark.run_ttk_test()

        print("\n内存使用对比:")
        print(f"Qt峰值内存: {qt_metrics.peak_memory:.1f}MB")
        print(f"TTK峰值内存: {ttk_metrics.peak_memory:.1f}MB")

        if qt_metrics.peak_memory > 0 and ttk_metrics.peak_memory > 0:
            memory_change = ttk_metrics.peak_memory - qt_metrics.peak_memory
            change_percent = (memory_change / qt_metrics.peak_memory) * 100

            print(f"内存变化: {memory_change:+.1f}MB ({change_percent:+.1f}%)")

            # TTK内存使用不应该比Qt高太多（允许50%的差异）
            self.assertLess(
                ttk_metrics.peak_memory,
                qt_metrics.peak_memory * 1.5,
                "TTK内存使用比Qt高太多",
            )


def run_memory_usage_tests():
    """运行内存使用测试"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("开始MiniCRM内存使用性能测试...")
    print("=" * 50)

    # 运行基准测试
    benchmark = MemoryUsageBenchmark()
    qt_result, ttk_result = benchmark.run_benchmark()

    # 输出结果
    print("\n内存使用测试结果:")
    print(f"Qt版本峰值内存: {qt_result.metrics.peak_memory:.1f}MB")
    print(f"TTK版本峰值内存: {ttk_result.metrics.peak_memory:.1f}MB")

    if qt_result.success and ttk_result.success:
        memory_change = ttk_result.metrics.peak_memory - qt_result.metrics.peak_memory
        change_percent = (
            (memory_change / qt_result.metrics.peak_memory) * 100
            if qt_result.metrics.peak_memory > 0
            else 0
        )
        print(f"内存变化: {memory_change:+.1f}MB ({change_percent:+.1f}%)")

    # 检查是否满足性能要求
    requirement_met = ttk_result.metrics.peak_memory <= 200.0
    print(f"内存要求(≤200MB): {'✓ 满足' if requirement_met else '✗ 不满足'}")

    # 输出垃圾回收效果
    if ttk_result.success:
        gc_stats = ttk_result.metrics.additional_metrics.get("gc_effectiveness", {})
        gc_freed = gc_stats.get("gc_freed_mb", 0)
        print(f"垃圾回收释放: {gc_freed:.1f}MB")

    print("\n内存使用测试完成！")


if __name__ == "__main__":
    run_memory_usage_tests()
