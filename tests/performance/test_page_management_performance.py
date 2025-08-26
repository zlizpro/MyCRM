"""MiniCRM TTK页面管理性能测试

为任务8提供全面的页面管理性能测试：
- 页面加载性能测试
- 页面切换流畅性测试
- 缓存效率测试
- 内存使用测试
- 并发加载测试

测试目标：
1. 验证页面加载时间符合性能要求
2. 确保页面切换的流畅性
3. 验证缓存策略的有效性
4. 监控内存使用情况
5. 测试系统在高负载下的表现

作者: MiniCRM开发团队
"""

from concurrent.futures import ThreadPoolExecutor
import gc
import logging
import time
import tkinter as tk
from typing import Dict, List

import psutil
import pytest

from minicrm.ui.ttk_base.enhanced_page_manager import (
    CacheStrategy,
    EnhancedPageManagerTTK,
    LoadingStrategy,
    PageCacheConfig,
    PageLoadConfig,
    PageTransitionConfig,
)
from minicrm.ui.ttk_base.page_manager import BasePage


class MockPage(BasePage):
    """模拟页面类用于测试"""

    def __init__(self, page_id: str, parent: tk.Widget, load_delay: float = 0.1):
        """初始化模拟页面

        Args:
            page_id: 页面ID
            parent: 父组件
            load_delay: 加载延迟（秒）
        """
        super().__init__(page_id, parent)
        self.load_delay = load_delay
        self.load_count = 0
        self.show_count = 0
        self.hide_count = 0

    def create_ui(self) -> tk.Frame:
        """创建页面UI"""
        # 模拟加载时间
        time.sleep(self.load_delay)

        frame = tk.Frame(self.parent)
        label = tk.Label(frame, text=f"Mock Page: {self.page_id}")
        label.pack()

        self.load_count += 1
        return frame

    def on_show(self) -> None:
        """页面显示时调用"""
        self.show_count += 1

    def on_hide(self) -> None:
        """页面隐藏时调用"""
        self.hide_count += 1


class PerformanceTestSuite:
    """页面管理性能测试套件"""

    def __init__(self):
        """初始化测试套件"""
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 测试结果
        self.test_results: Dict[str, Dict[str, float]] = {}

        # 性能基准
        self.performance_benchmarks = {
            "max_load_time": 2.0,  # 最大加载时间（秒）
            "max_show_time": 0.5,  # 最大显示时间（秒）
            "max_switch_time": 0.3,  # 最大切换时间（秒）
            "max_memory_mb": 100.0,  # 最大内存使用（MB）
            "min_cache_hit_rate": 0.8,  # 最小缓存命中率
        }

    def setup_test_environment(self) -> tuple[tk.Tk, EnhancedPageManagerTTK]:
        """设置测试环境

        Returns:
            测试根窗口和页面管理器
        """
        # 创建测试窗口
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口

        # 创建容器
        container = tk.Frame(root)

        # 创建配置
        cache_config = PageCacheConfig(
            enabled=True,
            strategy=CacheStrategy.LRU,
            max_size=10,
            ttl_seconds=300.0,
            auto_cleanup=True,
        )

        load_config = PageLoadConfig(
            strategy=LoadingStrategy.LAZY,
            preload_priority=0,
            preload_delay=0.1,
            background_load=True,
        )

        transition_config = PageTransitionConfig(
            enabled=True, duration_ms=200, fade_effect=True, loading_indicator=True
        )

        # 创建页面管理器
        manager = EnhancedPageManagerTTK(
            container=container,
            cache_config=cache_config,
            load_config=load_config,
            transition_config=transition_config,
        )

        return root, manager

    def register_test_pages(
        self, manager: EnhancedPageManagerTTK, page_count: int = 10
    ) -> List[str]:
        """注册测试页面

        Args:
            manager: 页面管理器
            page_count: 页面数量

        Returns:
            页面ID列表
        """
        page_ids = []

        for i in range(page_count):
            page_id = f"test_page_{i}"

            # 创建页面工厂
            def create_page(pid=page_id, delay=0.1 + i * 0.05):
                return MockPage(pid, manager.container, delay)

            # 注册页面
            manager.register_page_factory(
                page_id=page_id,
                factory=create_page,
                title=f"Test Page {i}",
                cache_enabled=True,
                preload=(i < 3),  # 前3个页面预加载
                preload_priority=10 - i,
            )

            page_ids.append(page_id)

        return page_ids

    def test_page_load_performance(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """测试页面加载性能

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            加载性能结果
        """
        self.logger.info("开始页面加载性能测试...")

        load_times = []

        for page_id in page_ids:
            start_time = time.time()

            # 导航到页面
            success = manager.navigate_to(page_id)

            load_time = time.time() - start_time
            load_times.append(load_time)

            self.logger.debug(f"页面 {page_id} 加载时间: {load_time:.3f}秒")

            # 验证加载成功
            assert success, f"页面加载失败: {page_id}"

            # 验证性能基准
            if load_time > self.performance_benchmarks["max_load_time"]:
                self.logger.warning(
                    f"页面加载时间超过基准: {page_id} ({load_time:.3f}秒)"
                )

        results = {
            "avg_load_time": sum(load_times) / len(load_times),
            "max_load_time": max(load_times),
            "min_load_time": min(load_times),
            "total_pages": len(page_ids),
            "failed_pages": 0,  # 在这个测试中没有失败的页面
        }

        self.test_results["page_load_performance"] = results
        self.logger.info(f"页面加载性能测试完成: 平均 {results['avg_load_time']:.3f}秒")

        return results

    def test_page_switch_performance(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """测试页面切换性能

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            切换性能结果
        """
        self.logger.info("开始页面切换性能测试...")

        switch_times = []

        # 先加载第一个页面
        manager.navigate_to(page_ids[0])

        # 测试页面间切换
        for i in range(1, len(page_ids)):
            start_time = time.time()

            # 切换到下一个页面
            success = manager.navigate_to(page_ids[i])

            switch_time = time.time() - start_time
            switch_times.append(switch_time)

            self.logger.debug(
                f"页面切换 {page_ids[i - 1]} -> {page_ids[i]} 时间: {switch_time:.3f}秒"
            )

            # 验证切换成功
            assert success, f"页面切换失败: {page_ids[i]}"

            # 验证性能基准
            if switch_time > self.performance_benchmarks["max_switch_time"]:
                self.logger.warning(
                    f"页面切换时间超过基准: {page_ids[i]} ({switch_time:.3f}秒)"
                )

        results = {
            "avg_switch_time": sum(switch_times) / len(switch_times),
            "max_switch_time": max(switch_times),
            "min_switch_time": min(switch_times),
            "total_switches": len(switch_times),
        }

        self.test_results["page_switch_performance"] = results
        self.logger.info(
            f"页面切换性能测试完成: 平均 {results['avg_switch_time']:.3f}秒"
        )

        return results

    def test_cache_efficiency(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """测试缓存效率

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            缓存效率结果
        """
        self.logger.info("开始缓存效率测试...")

        # 第一轮访问 - 建立缓存
        for page_id in page_ids[:5]:  # 只访问前5个页面
            manager.navigate_to(page_id)

        # 获取初始缓存信息
        initial_cache_info = manager.cache.get_cache_info()

        # 第二轮访问 - 测试缓存命中
        cache_hit_times = []

        for page_id in page_ids[:5]:
            start_time = time.time()
            manager.navigate_to(page_id)
            hit_time = time.time() - start_time
            cache_hit_times.append(hit_time)

        # 获取最终缓存信息
        final_cache_info = manager.cache.get_cache_info()

        # 计算缓存命中率
        hit_rate = final_cache_info["hit_rate"]

        results = {
            "cache_hit_rate": hit_rate,
            "avg_hit_time": sum(cache_hit_times) / len(cache_hit_times),
            "cache_size": final_cache_info["size"],
            "total_hits": final_cache_info["total_hits"],
            "total_misses": final_cache_info["total_misses"],
        }

        self.test_results["cache_efficiency"] = results
        self.logger.info(f"缓存效率测试完成: 命中率 {hit_rate:.2%}")

        # 验证缓存命中率基准
        if hit_rate < self.performance_benchmarks["min_cache_hit_rate"]:
            self.logger.warning(f"缓存命中率低于基准: {hit_rate:.2%}")

        return results

    def test_memory_usage(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """测试内存使用情况

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            内存使用结果
        """
        self.logger.info("开始内存使用测试...")

        # 获取当前进程
        process = psutil.Process()

        # 记录初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_samples = [initial_memory]

        # 加载所有页面并记录内存使用
        for page_id in page_ids:
            manager.navigate_to(page_id)

            # 强制垃圾回收
            gc.collect()

            # 记录内存使用
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)

            self.logger.debug(f"页面 {page_id} 加载后内存: {current_memory:.2f}MB")

        # 计算内存增长
        memory_growth = max(memory_samples) - initial_memory

        results = {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": max(memory_samples),
            "memory_growth_mb": memory_growth,
            "avg_memory_mb": sum(memory_samples) / len(memory_samples),
            "memory_samples": len(memory_samples),
        }

        self.test_results["memory_usage"] = results
        self.logger.info(
            f"内存使用测试完成: 峰值 {max(memory_samples):.2f}MB, 增长 {memory_growth:.2f}MB"
        )

        # 验证内存使用基准
        if max(memory_samples) > self.performance_benchmarks["max_memory_mb"]:
            self.logger.warning(f"内存使用超过基准: {max(memory_samples):.2f}MB")

        return results

    def test_concurrent_loading(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """测试并发加载性能

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            并发加载结果
        """
        self.logger.info("开始并发加载测试...")

        # 并发加载函数
        def load_page(page_id: str) -> tuple[str, float, bool]:
            start_time = time.time()
            success = manager.navigate_to(page_id)
            load_time = time.time() - start_time
            return page_id, load_time, success

        # 使用线程池进行并发测试
        concurrent_results = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            start_time = time.time()

            # 提交并发任务
            futures = [executor.submit(load_page, page_id) for page_id in page_ids[:5]]

            # 收集结果
            for future in futures:
                page_id, load_time, success = future.result()
                concurrent_results.append((page_id, load_time, success))
                self.logger.debug(
                    f"并发加载 {page_id}: {load_time:.3f}秒, 成功: {success}"
                )

            total_time = time.time() - start_time

        # 分析结果
        successful_loads = [r for r in concurrent_results if r[2]]
        load_times = [r[1] for r in successful_loads]

        results = {
            "total_concurrent_time": total_time,
            "successful_loads": len(successful_loads),
            "failed_loads": len(concurrent_results) - len(successful_loads),
            "avg_concurrent_load_time": sum(load_times) / len(load_times)
            if load_times
            else 0,
            "max_concurrent_load_time": max(load_times) if load_times else 0,
            "concurrency_efficiency": len(successful_loads) / len(concurrent_results)
            if concurrent_results
            else 0,
        }

        self.test_results["concurrent_loading"] = results
        self.logger.info(
            f"并发加载测试完成: {len(successful_loads)}/{len(concurrent_results)} 成功"
        )

        return results

    def test_stress_testing(
        self, manager: EnhancedPageManagerTTK, page_ids: List[str]
    ) -> Dict[str, float]:
        """压力测试

        Args:
            manager: 页面管理器
            page_ids: 页面ID列表

        Returns:
            压力测试结果
        """
        self.logger.info("开始压力测试...")

        # 压力测试参数
        iterations = 100
        rapid_switches = []

        start_time = time.time()

        # 快速切换页面
        for i in range(iterations):
            page_id = page_ids[i % len(page_ids)]

            switch_start = time.time()
            success = manager.navigate_to(page_id)
            switch_time = time.time() - switch_start

            rapid_switches.append((page_id, switch_time, success))

            if i % 20 == 0:
                self.logger.debug(f"压力测试进度: {i}/{iterations}")

        total_stress_time = time.time() - start_time

        # 分析结果
        successful_switches = [r for r in rapid_switches if r[2]]
        switch_times = [r[1] for r in successful_switches]

        results = {
            "total_stress_time": total_stress_time,
            "total_iterations": iterations,
            "successful_switches": len(successful_switches),
            "failed_switches": len(rapid_switches) - len(successful_switches),
            "avg_switch_time": sum(switch_times) / len(switch_times)
            if switch_times
            else 0,
            "max_switch_time": max(switch_times) if switch_times else 0,
            "switches_per_second": len(successful_switches) / total_stress_time,
            "stress_success_rate": len(successful_switches) / len(rapid_switches)
            if rapid_switches
            else 0,
        }

        self.test_results["stress_testing"] = results
        self.logger.info(
            f"压力测试完成: {len(successful_switches)}/{iterations} 成功, {results['switches_per_second']:.2f} 切换/秒"
        )

        return results

    def run_full_performance_suite(self) -> Dict[str, Dict[str, float]]:
        """运行完整的性能测试套件

        Returns:
            完整测试结果
        """
        self.logger.info("开始完整性能测试套件...")

        # 设置测试环境
        root, manager = self.setup_test_environment()

        try:
            # 注册测试页面
            page_ids = self.register_test_pages(manager, 10)

            # 运行各项测试
            self.test_page_load_performance(manager, page_ids)
            self.test_page_switch_performance(manager, page_ids)
            self.test_cache_efficiency(manager, page_ids)
            self.test_memory_usage(manager, page_ids)
            self.test_concurrent_loading(manager, page_ids)
            self.test_stress_testing(manager, page_ids)

            # 生成性能报告
            self.generate_performance_report()

        finally:
            # 清理资源
            manager.cleanup()
            root.destroy()

        return self.test_results

    def generate_performance_report(self) -> None:
        """生成性能测试报告"""
        self.logger.info("生成性能测试报告...")

        print("\n" + "=" * 60)
        print("MiniCRM TTK页面管理性能测试报告")
        print("=" * 60)

        for test_name, results in self.test_results.items():
            print(f"\n{test_name.upper()}:")
            print("-" * 40)

            for metric, value in results.items():
                if isinstance(value, float):
                    if "time" in metric:
                        print(f"  {metric}: {value:.3f}秒")
                    elif "rate" in metric:
                        print(f"  {metric}: {value:.2%}")
                    elif "mb" in metric.lower():
                        print(f"  {metric}: {value:.2f}MB")
                    else:
                        print(f"  {metric}: {value:.3f}")
                else:
                    print(f"  {metric}: {value}")

        # 性能基准对比
        print("\n性能基准对比:")
        print("-" * 40)

        # 检查各项指标
        if "page_load_performance" in self.test_results:
            load_results = self.test_results["page_load_performance"]
            max_load = load_results["max_load_time"]
            benchmark = self.performance_benchmarks["max_load_time"]
            status = "✓" if max_load <= benchmark else "✗"
            print(f"  最大加载时间: {max_load:.3f}秒 (基准: {benchmark}秒) {status}")

        if "page_switch_performance" in self.test_results:
            switch_results = self.test_results["page_switch_performance"]
            max_switch = switch_results["max_switch_time"]
            benchmark = self.performance_benchmarks["max_switch_time"]
            status = "✓" if max_switch <= benchmark else "✗"
            print(f"  最大切换时间: {max_switch:.3f}秒 (基准: {benchmark}秒) {status}")

        if "cache_efficiency" in self.test_results:
            cache_results = self.test_results["cache_efficiency"]
            hit_rate = cache_results["cache_hit_rate"]
            benchmark = self.performance_benchmarks["min_cache_hit_rate"]
            status = "✓" if hit_rate >= benchmark else "✗"
            print(f"  缓存命中率: {hit_rate:.2%} (基准: {benchmark:.2%}) {status}")

        if "memory_usage" in self.test_results:
            memory_results = self.test_results["memory_usage"]
            peak_memory = memory_results["peak_memory_mb"]
            benchmark = self.performance_benchmarks["max_memory_mb"]
            status = "✓" if peak_memory <= benchmark else "✗"
            print(f"  峰值内存使用: {peak_memory:.2f}MB (基准: {benchmark}MB) {status}")

        print("\n" + "=" * 60)


# pytest测试类
class TestPageManagementPerformance:
    """页面管理性能测试类"""

    @pytest.fixture
    def performance_suite(self):
        """性能测试套件fixture"""
        return PerformanceTestSuite()

    @pytest.fixture
    def test_environment(self):
        """测试环境fixture"""
        suite = PerformanceTestSuite()
        root, manager = suite.setup_test_environment()

        yield root, manager

        # 清理
        manager.cleanup()
        root.destroy()

    def test_page_load_performance_benchmark(self, test_environment):
        """测试页面加载性能基准"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 5)

        # 运行加载性能测试
        results = suite.test_page_load_performance(manager, page_ids)

        # 验证性能基准
        assert (
            results["max_load_time"] <= suite.performance_benchmarks["max_load_time"]
        ), f"页面加载时间超过基准: {results['max_load_time']:.3f}秒"

        assert (
            results["avg_load_time"]
            <= suite.performance_benchmarks["max_load_time"] * 0.8
        ), f"平均加载时间过长: {results['avg_load_time']:.3f}秒"

    def test_page_switch_performance_benchmark(self, test_environment):
        """测试页面切换性能基准"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 5)

        # 运行切换性能测试
        results = suite.test_page_switch_performance(manager, page_ids)

        # 验证性能基准
        assert (
            results["max_switch_time"]
            <= suite.performance_benchmarks["max_switch_time"]
        ), f"页面切换时间超过基准: {results['max_switch_time']:.3f}秒"

    def test_cache_efficiency_benchmark(self, test_environment):
        """测试缓存效率基准"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 5)

        # 运行缓存效率测试
        results = suite.test_cache_efficiency(manager, page_ids)

        # 验证缓存命中率基准
        assert (
            results["cache_hit_rate"]
            >= suite.performance_benchmarks["min_cache_hit_rate"]
        ), f"缓存命中率低于基准: {results['cache_hit_rate']:.2%}"

    def test_memory_usage_benchmark(self, test_environment):
        """测试内存使用基准"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 8)

        # 运行内存使用测试
        results = suite.test_memory_usage(manager, page_ids)

        # 验证内存使用基准
        assert (
            results["peak_memory_mb"] <= suite.performance_benchmarks["max_memory_mb"]
        ), f"内存使用超过基准: {results['peak_memory_mb']:.2f}MB"

    def test_concurrent_loading_stability(self, test_environment):
        """测试并发加载稳定性"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 5)

        # 运行并发加载测试
        results = suite.test_concurrent_loading(manager, page_ids)

        # 验证并发加载成功率
        assert results["concurrency_efficiency"] >= 0.8, (
            f"并发加载成功率过低: {results['concurrency_efficiency']:.2%}"
        )

    def test_stress_testing_stability(self, test_environment):
        """测试压力测试稳定性"""
        root, manager = test_environment
        suite = PerformanceTestSuite()

        # 注册测试页面
        page_ids = suite.register_test_pages(manager, 3)

        # 运行压力测试（减少迭代次数以加快测试）
        suite.test_stress_testing(manager, page_ids)
        results = suite.test_results["stress_testing"]

        # 验证压力测试成功率
        assert results["stress_success_rate"] >= 0.9, (
            f"压力测试成功率过低: {results['stress_success_rate']:.2%}"
        )

    @pytest.mark.slow
    def test_full_performance_suite(self, performance_suite):
        """运行完整性能测试套件（标记为慢速测试）"""
        results = performance_suite.run_full_performance_suite()

        # 验证所有测试都有结果
        expected_tests = [
            "page_load_performance",
            "page_switch_performance",
            "cache_efficiency",
            "memory_usage",
            "concurrent_loading",
            "stress_testing",
        ]

        for test_name in expected_tests:
            assert test_name in results, f"缺少测试结果: {test_name}"


if __name__ == "__main__":
    """直接运行性能测试"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 运行完整性能测试套件
    suite = PerformanceTestSuite()
    results = suite.run_full_performance_suite()

    print(f"\n性能测试完成！共运行 {len(results)} 项测试。")
