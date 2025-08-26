"""MiniCRM TTK增强页面管理器单元测试

测试增强页面管理器的核心功能：
- 页面缓存机制测试
- 懒加载功能测试
- 页面切换性能测试
- 配置管理测试
- 错误处理测试

作者: MiniCRM开发团队
"""

import time
import tkinter as tk

import pytest

from minicrm.ui.ttk_base.enhanced_page_manager import (
    CacheStrategy,
    EnhancedPageManagerTTK,
    LazyPageLoader,
    LoadingStrategy,
    PageCache,
    PageCacheConfig,
    PageLoadConfig,
    PageTransitionConfig,
    PerformanceMonitor,
)
from minicrm.ui.ttk_base.page_manager import BasePage


class MockPage(BasePage):
    """模拟页面类"""

    def __init__(self, page_id: str, parent: tk.Widget, load_delay: float = 0.1):
        super().__init__(page_id, parent)
        self.load_delay = load_delay
        self.created = False

    def create_ui(self) -> tk.Frame:
        time.sleep(self.load_delay)
        frame = tk.Frame(self.parent)
        self.created = True
        return frame


class TestPageCache:
    """页面缓存测试类"""

    @pytest.fixture
    def cache_config(self):
        """缓存配置fixture"""
        return PageCacheConfig(
            enabled=True,
            strategy=CacheStrategy.LRU,
            max_size=3,
            ttl_seconds=1.0,
            auto_cleanup=False,  # 测试中禁用自动清理
        )

    @pytest.fixture
    def page_cache(self, cache_config):
        """页面缓存fixture"""
        return PageCache(cache_config)

    @pytest.fixture
    def mock_pages(self):
        """模拟页面fixture"""
        root = tk.Tk()
        root.withdraw()

        pages = {}
        for i in range(5):
            page_id = f"page_{i}"
            pages[page_id] = MockPage(page_id, root)

        yield pages

        root.destroy()

    def test_cache_put_and_get(self, page_cache, mock_pages):
        """测试缓存存取功能"""
        page_id = "page_0"
        page = mock_pages[page_id]

        # 测试存储
        assert page_cache.put(page_id, page) is True

        # 测试获取
        cached_page = page_cache.get(page_id)
        assert cached_page is page

        # 测试不存在的页面
        assert page_cache.get("nonexistent") is None

    def test_cache_lru_eviction(self, page_cache, mock_pages):
        """测试LRU淘汰策略"""
        # 填满缓存
        for i in range(3):
            page_id = f"page_{i}"
            page_cache.put(page_id, mock_pages[page_id])

        # 访问第一个页面，使其成为最近使用
        page_cache.get("page_0")

        # 添加新页面，应该淘汰page_1（最少使用）
        page_cache.put("page_3", mock_pages["page_3"])

        # 验证淘汰结果
        assert page_cache.get("page_0") is not None  # 最近使用，应该保留
        assert page_cache.get("page_1") is None  # 应该被淘汰
        assert page_cache.get("page_2") is not None  # 应该保留
        assert page_cache.get("page_3") is not None  # 新添加，应该保留

    def test_cache_ttl_expiration(self, mock_pages):
        """测试TTL过期机制"""
        config = PageCacheConfig(
            enabled=True,
            strategy=CacheStrategy.TTL,
            max_size=5,
            ttl_seconds=0.1,  # 100毫秒过期
            auto_cleanup=False,
        )

        cache = PageCache(config)

        # 添加页面到缓存
        page_id = "page_0"
        cache.put(page_id, mock_pages[page_id])

        # 立即获取应该成功
        assert cache.get(page_id) is not None

        # 等待过期
        time.sleep(0.15)

        # 手动触发清理
        cache._evict_pages()

        # 过期后应该获取不到
        assert cache.get(page_id) is None

    def test_cache_disabled(self, mock_pages):
        """测试禁用缓存"""
        config = PageCacheConfig(enabled=False)
        cache = PageCache(config)

        page_id = "page_0"

        # 禁用缓存时，put应该返回False
        assert cache.put(page_id, mock_pages[page_id]) is False

        # get应该返回None
        assert cache.get(page_id) is None

    def test_cache_info(self, page_cache, mock_pages):
        """测试缓存信息获取"""
        # 添加一些页面
        for i in range(2):
            page_id = f"page_{i}"
            page_cache.put(page_id, mock_pages[page_id])

        # 访问页面产生命中和未命中
        page_cache.get("page_0")  # 命中
        page_cache.get("page_1")  # 命中
        page_cache.get("page_2")  # 未命中

        info = page_cache.get_cache_info()

        assert info["enabled"] is True
        assert info["size"] == 2
        assert info["max_size"] == 3
        assert info["total_hits"] == 2
        assert info["total_misses"] == 1
        assert info["hit_rate"] == 2 / 3


class TestLazyPageLoader:
    """懒加载器测试类"""

    @pytest.fixture
    def load_config(self):
        """加载配置fixture"""
        return PageLoadConfig(
            strategy=LoadingStrategy.LAZY,
            preload_priority=0,
            preload_delay=0.05,
            background_load=False,  # 测试中禁用后台加载
        )

    @pytest.fixture
    def lazy_loader(self, load_config):
        """懒加载器fixture"""
        return LazyPageLoader(load_config)

    def test_preload_queue_management(self, lazy_loader):
        """测试预加载队列管理"""
        # 添加页面到队列
        lazy_loader.add_to_preload_queue("page_1", 5)
        lazy_loader.add_to_preload_queue("page_2", 10)
        lazy_loader.add_to_preload_queue("page_3", 1)

        # 验证队列按优先级排序
        queue = lazy_loader._preload_queue
        assert len(queue) == 3
        assert queue[0] == ("page_2", 10)  # 最高优先级
        assert queue[1] == ("page_1", 5)
        assert queue[2] == ("page_3", 1)  # 最低优先级

        # 测试移除
        lazy_loader.remove_from_preload_queue("page_1")
        assert len(lazy_loader._preload_queue) == 2
        assert ("page_1", 5) not in lazy_loader._preload_queue

    def test_loading_state_tracking(self, lazy_loader):
        """测试加载状态跟踪"""
        page_id = "test_page"

        # 初始状态应该不在加载中
        assert lazy_loader.is_loading(page_id) is False

        # 手动设置加载状态
        lazy_loader._loading_pages.add(page_id)
        assert lazy_loader.is_loading(page_id) is True

        # 移除加载状态
        lazy_loader._loading_pages.discard(page_id)
        assert lazy_loader.is_loading(page_id) is False

    def test_load_callbacks(self, lazy_loader):
        """测试加载完成回调"""
        page_id = "test_page"
        callback_called = []

        def test_callback(pid):
            callback_called.append(pid)

        # 添加回调
        lazy_loader.add_load_callback(page_id, test_callback)

        # 验证回调已添加
        assert page_id in lazy_loader._load_callbacks
        assert test_callback in lazy_loader._load_callbacks[page_id]


class TestPerformanceMonitor:
    """性能监控器测试类"""

    @pytest.fixture
    def performance_monitor(self):
        """性能监控器fixture"""
        monitor = PerformanceMonitor()
        monitor.monitoring_enabled = True
        return monitor

    def test_performance_metrics_recording(self, performance_monitor):
        """测试性能指标记录"""
        page_id = "test_page"

        # 记录加载时间
        performance_monitor.record_page_load(page_id, 1.5)

        # 记录显示时间
        performance_monitor.record_page_show(page_id, 0.3)

        # 记录内存使用
        performance_monitor.record_memory_usage(page_id, 45.2)

        # 验证指标记录
        metrics = performance_monitor.metrics[page_id]
        assert metrics.page_id == page_id
        assert metrics.load_time == 1.5
        assert metrics.show_time == 0.3
        assert metrics.memory_usage == 45.2

    def test_performance_report_generation(self, performance_monitor):
        """测试性能报告生成"""
        # 记录多个页面的性能数据
        pages_data = [
            ("page_1", 1.0, 0.2, 30.0),
            ("page_2", 2.0, 0.4, 50.0),
            ("page_3", 1.5, 0.3, 40.0),
        ]

        for page_id, load_time, show_time, memory in pages_data:
            performance_monitor.record_page_load(page_id, load_time)
            performance_monitor.record_page_show(page_id, show_time)
            performance_monitor.record_memory_usage(page_id, memory)

        # 生成报告
        report = performance_monitor.get_performance_report()

        # 验证报告内容
        assert report["total_pages"] == 3
        assert report["average_load_time"] == 1.5
        assert abs(report["average_show_time"] - 0.3) < 0.001  # 使用近似比较
        assert report["average_memory_usage"] == 40.0

        # 验证最差性能页面
        assert report["slowest_load_page"]["page_id"] == "page_2"
        assert report["slowest_load_page"]["load_time"] == 2.0

        assert report["highest_memory_page"]["page_id"] == "page_2"
        assert report["highest_memory_page"]["memory_usage"] == 50.0

    def test_performance_warnings(self, performance_monitor, caplog):
        """测试性能警告"""
        page_id = "slow_page"

        # 记录超过警告阈值的性能数据
        performance_monitor.record_page_load(page_id, 3.0)  # 超过2秒警告阈值
        performance_monitor.record_page_show(page_id, 0.8)  # 超过0.5秒警告阈值
        performance_monitor.record_memory_usage(page_id, 60.0)  # 超过50MB警告阈值

        # 验证警告日志
        assert "页面加载时间过长" in caplog.text
        assert "页面显示时间过长" in caplog.text
        assert "页面内存使用过高" in caplog.text


class TestEnhancedPageManagerTTK:
    """增强页面管理器测试类"""

    @pytest.fixture
    def test_environment(self):
        """测试环境fixture"""
        root = tk.Tk()
        root.withdraw()

        container = tk.Frame(root)

        cache_config = PageCacheConfig(
            enabled=True, strategy=CacheStrategy.LRU, max_size=5, auto_cleanup=False
        )

        load_config = PageLoadConfig(
            strategy=LoadingStrategy.LAZY, background_load=False
        )

        transition_config = PageTransitionConfig(enabled=True, duration_ms=100)

        manager = EnhancedPageManagerTTK(
            container=container,
            cache_config=cache_config,
            load_config=load_config,
            transition_config=transition_config,
        )

        yield root, container, manager

        manager.cleanup()
        root.destroy()

    def test_page_registration(self, test_environment):
        """测试页面注册"""
        root, container, manager = test_environment

        # 注册页面工厂
        def create_page():
            return MockPage("test_page", container)

        manager.register_page_factory(
            page_id="test_page",
            factory=create_page,
            title="Test Page",
            cache_enabled=True,
            preload=False,
        )

        # 验证页面配置已注册
        assert "test_page" in manager.page_configs
        assert "test_page" in manager.page_factories

    def test_page_navigation(self, test_environment):
        """测试页面导航"""
        root, container, manager = test_environment

        # 注册测试页面
        def create_page():
            return MockPage("test_page", container, 0.05)

        manager.register_page_factory(
            page_id="test_page", factory=create_page, title="Test Page"
        )

        # 导航到页面
        success = manager.navigate_to("test_page")

        # 验证导航成功
        assert success is True
        assert manager.get_current_page() == "test_page"

        # 验证页面在缓存中
        cached_page = manager.cache.get("test_page")
        assert cached_page is not None
        # 验证页面已加载（检查状态而不是created属性）
        assert cached_page.state.value in ["loaded", "active"]

    def test_page_navigation_with_params(self, test_environment):
        """测试带参数的页面导航"""
        root, container, manager = test_environment

        # 注册测试页面
        def create_page():
            return MockPage("param_page", container)

        manager.register_page_factory(
            page_id="param_page", factory=create_page, title="Param Page"
        )

        # 带参数导航
        params = {"user_id": 123, "mode": "edit"}
        success = manager.navigate_to("param_page", params)

        assert success is True

        # 验证参数设置
        page = manager.cache.get("param_page")
        assert page.get_data("user_id") == 123
        assert page.get_data("mode") == "edit"

    def test_page_history_management(self, test_environment):
        """测试页面历史管理"""
        root, container, manager = test_environment

        # 注册多个测试页面
        for i in range(3):
            page_id = f"page_{i}"

            def create_page(pid=page_id):
                return MockPage(pid, container)

            manager.register_page_factory(
                page_id=page_id, factory=create_page, title=f"Page {i}"
            )

        # 依次导航到各个页面
        for i in range(3):
            manager.navigate_to(f"page_{i}")

        # 验证历史记录
        history = manager.get_page_history()
        assert len(history) == 3
        assert history == ["page_0", "page_1", "page_2"]

        # 测试返回上一页
        success = manager.go_back()
        assert success is True
        assert manager.get_current_page() == "page_1"

        # 再次返回
        success = manager.go_back()
        assert success is True
        assert manager.get_current_page() == "page_0"

    def test_nonexistent_page_navigation(self, test_environment):
        """测试导航到不存在的页面"""
        root, container, manager = test_environment

        # 尝试导航到不存在的页面
        success = manager.navigate_to("nonexistent_page")

        # 应该导航失败
        assert success is False
        assert manager.get_current_page() is None

    def test_manager_info_retrieval(self, test_environment):
        """测试管理器信息获取"""
        root, container, manager = test_environment

        # 注册一个页面
        def create_page():
            return MockPage("info_page", container)

        manager.register_page_factory(
            page_id="info_page", factory=create_page, title="Info Page"
        )

        # 导航到页面
        manager.navigate_to("info_page")

        # 获取管理器信息
        info = manager.get_manager_info()

        # 验证信息内容
        assert "current_page" in info
        assert "total_pages" in info
        assert "cache_info" in info
        assert "performance_report" in info

        assert info["current_page"] == "info_page"
        assert info["total_pages"] == 1

    def test_preload_functionality(self, test_environment):
        """测试预加载功能"""
        root, container, manager = test_environment

        # 注册预加载页面
        def create_page():
            return MockPage("preload_page", container)

        manager.register_page_factory(
            page_id="preload_page",
            factory=create_page,
            title="Preload Page",
            preload=True,
            preload_priority=5,
        )

        # 手动触发预加载
        manager.preload_page("preload_page", 5)

        # 验证页面已添加到预加载队列
        assert ("preload_page", 5) in manager.loader._preload_queue


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
