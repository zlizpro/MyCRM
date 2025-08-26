"""
Hooks框架测试模块

测试MiniCRM钩子系统的各种功能。
"""

import unittest
from unittest.mock import patch

from src.minicrm.core.hooks import (
    HookExecutionMode,
    HookInfo,
    HookManager,
    HookPriority,
    HookResult,
    audit_hook,
    get_hook_manager,
    hook,
    performance_hook,
    register_hook,
    shutdown_hooks,
    trigger_hook,
    unregister_hook,
)


class TestHookInfo(unittest.TestCase):
    """测试钩子信息数据类"""

    def test_hook_info_creation(self):
        """测试钩子信息创建"""

        def test_handler():
            pass

        hook_info = HookInfo(
            name="test_hook",
            handler=test_handler,
            priority=HookPriority.HIGH,
            execution_mode=HookExecutionMode.ASYNC,
            description="Test hook",
            max_execution_time=5.0,
            tags=["test", "demo"],
        )

        self.assertEqual(hook_info.name, "test_hook")
        self.assertEqual(hook_info.handler, test_handler)
        self.assertEqual(hook_info.priority, HookPriority.HIGH)
        self.assertEqual(hook_info.execution_mode, HookExecutionMode.ASYNC)
        self.assertEqual(hook_info.description, "Test hook")
        self.assertTrue(hook_info.enabled)
        self.assertEqual(hook_info.max_execution_time, 5.0)
        self.assertEqual(hook_info.tags, ["test", "demo"])

    def test_hook_info_default_description(self):
        """测试钩子信息默认描述"""

        def test_handler():
            pass

        hook_info = HookInfo(name="test_hook", handler=test_handler)

        self.assertEqual(hook_info.description, "Hook: test_hook")


class TestHookResult(unittest.TestCase):
    """测试钩子执行结果"""

    def test_hook_result_success(self):
        """测试成功的钩子结果"""
        result = HookResult(
            success=True, result="test_result", duration=1.5, hook_name="test_hook"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.result, "test_result")
        self.assertIsNone(result.error)
        self.assertEqual(result.duration, 1.5)
        self.assertEqual(result.hook_name, "test_hook")
        self.assertTrue(bool(result))

    def test_hook_result_failure(self):
        """测试失败的钩子结果"""
        error = Exception("Test error")
        result = HookResult(
            success=False, error=error, duration=0.5, hook_name="test_hook"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertEqual(result.error, error)
        self.assertEqual(result.duration, 0.5)
        self.assertEqual(result.hook_name, "test_hook")
        self.assertFalse(bool(result))

    def test_hook_result_string_representation(self):
        """测试钩子结果字符串表示"""
        result = HookResult(success=True, hook_name="test_hook", duration=1.234)

        str_repr = str(result)

        self.assertIn("test_hook", str_repr)
        self.assertIn("成功", str_repr)
        self.assertIn("1.234", str_repr)


class TestHookManager(unittest.TestCase):
    """测试钩子管理器"""

    def setUp(self):
        """测试准备"""
        self.hook_manager = HookManager(max_workers=2)
        self.test_results = []

    def tearDown(self):
        """测试清理"""
        self.hook_manager.shutdown()

    def test_register_hook(self):
        """测试注册钩子"""

        def test_handler():
            return "test_result"

        hook_info = self.hook_manager.register(
            event_name="test_event",
            handler=test_handler,
            priority=HookPriority.HIGH,
            description="Test hook",
        )

        self.assertEqual(hook_info.name, "test_event.test_handler")
        self.assertEqual(hook_info.handler, test_handler)
        self.assertEqual(hook_info.priority, HookPriority.HIGH)
        self.assertIn("test_event", self.hook_manager._hooks)
        self.assertIn(hook_info, self.hook_manager._hooks["test_event"])

    def test_unregister_hook(self):
        """测试注销钩子"""

        def test_handler():
            return "test_result"

        # 注册钩子
        self.hook_manager.register("test_event", test_handler)

        # 注销钩子
        success = self.hook_manager.unregister("test_event", test_handler)

        self.assertTrue(success)
        self.assertEqual(len(self.hook_manager._hooks.get("test_event", [])), 0)

    def test_unregister_nonexistent_hook(self):
        """测试注销不存在的钩子"""

        def test_handler():
            pass

        success = self.hook_manager.unregister("nonexistent_event", test_handler)

        self.assertFalse(success)

    def test_trigger_hook_success(self):
        """测试触发钩子成功"""

        def test_handler(value):
            return value * 2

        self.hook_manager.register("test_event", test_handler)

        results = self.hook_manager.trigger("test_event", 5)

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertEqual(results[0].result, 10)

    def test_trigger_hook_failure(self):
        """测试触发钩子失败"""

        def test_handler():
            raise ValueError("Test error")

        self.hook_manager.register("test_event", test_handler)

        results = self.hook_manager.trigger("test_event")

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].success)
        self.assertIsInstance(results[0].error, ValueError)

    def test_trigger_nonexistent_event(self):
        """测试触发不存在的事件"""
        results = self.hook_manager.trigger("nonexistent_event")

        self.assertEqual(len(results), 0)

    def test_hook_priority_ordering(self):
        """测试钩子优先级排序"""
        execution_order = []

        def high_priority_handler():
            execution_order.append("high")

        def low_priority_handler():
            execution_order.append("low")

        def normal_priority_handler():
            execution_order.append("normal")

        # 按非优先级顺序注册
        self.hook_manager.register("test_event", low_priority_handler, HookPriority.LOW)
        self.hook_manager.register(
            "test_event", high_priority_handler, HookPriority.HIGH
        )
        self.hook_manager.register(
            "test_event", normal_priority_handler, HookPriority.NORMAL
        )

        self.hook_manager.trigger("test_event")

        # 验证执行顺序：HIGH -> NORMAL -> LOW
        self.assertEqual(execution_order, ["high", "normal", "low"])

    def test_disabled_hook(self):
        """测试禁用的钩子"""

        def test_handler():
            return "should_not_execute"

        hook_info = self.hook_manager.register("test_event", test_handler)
        hook_info.enabled = False

        results = self.hook_manager.trigger("test_event")

        self.assertEqual(len(results), 0)

    def test_enable_disable_hook(self):
        """测试启用和禁用钩子"""

        def test_handler():
            return "test_result"

        self.hook_manager.register("test_event", test_handler)

        # 禁用钩子
        success = self.hook_manager.disable_hook("test_event", test_handler)
        self.assertTrue(success)

        results = self.hook_manager.trigger("test_event")
        self.assertEqual(len(results), 0)

        # 启用钩子
        success = self.hook_manager.enable_hook("test_event", test_handler)
        self.assertTrue(success)

        results = self.hook_manager.trigger("test_event")
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)

    def test_enable_disable_all(self):
        """测试启用和禁用所有钩子"""

        def test_handler():
            return "test_result"

        self.hook_manager.register("test_event", test_handler)

        # 禁用所有钩子
        self.hook_manager.disable_all()
        results = self.hook_manager.trigger("test_event")
        self.assertEqual(len(results), 0)

        # 启用所有钩子
        self.hook_manager.enable_all()
        results = self.hook_manager.trigger("test_event")
        self.assertEqual(len(results), 1)

    def test_get_hooks(self):
        """测试获取钩子信息"""

        def test_handler1():
            pass

        def test_handler2():
            pass

        self.hook_manager.register("event1", test_handler1)
        self.hook_manager.register("event2", test_handler2)

        # 获取所有钩子
        all_hooks = self.hook_manager.get_hooks()
        self.assertIn("event1", all_hooks)
        self.assertIn("event2", all_hooks)

        # 获取特定事件的钩子
        event1_hooks = self.hook_manager.get_hooks("event1")
        self.assertIn("event1", event1_hooks)
        self.assertNotIn("event2", event1_hooks)

    def test_get_hook_stats(self):
        """测试获取钩子统计信息"""

        def test_handler():
            return "test_result"

        hook_info = self.hook_manager.register("test_event", test_handler)

        # 触发钩子以生成统计信息
        self.hook_manager.trigger("test_event")

        # 获取统计信息
        stats = self.hook_manager.get_hook_stats(hook_info.name)

        self.assertEqual(stats["call_count"], 1)
        self.assertEqual(stats["success_count"], 1)
        self.assertEqual(stats["error_count"], 0)
        self.assertGreater(stats["total_duration"], 0)

    def test_clear_hooks(self):
        """测试清除钩子"""

        def test_handler1():
            pass

        def test_handler2():
            pass

        self.hook_manager.register("event1", test_handler1)
        self.hook_manager.register("event2", test_handler2)

        # 清除特定事件的钩子
        self.hook_manager.clear_hooks("event1")
        self.assertNotIn("event1", self.hook_manager._hooks)
        self.assertIn("event2", self.hook_manager._hooks)

        # 清除所有钩子
        self.hook_manager.clear_hooks()
        self.assertEqual(len(self.hook_manager._hooks), 0)

    @patch("time.time")
    def test_hook_execution_timeout_warning(self, mock_time):
        """测试钩子执行超时警告"""
        mock_time.side_effect = [1000.0, 1003.0]  # 模拟3秒执行时间

        def slow_handler():
            return "result"

        # 注册带超时限制的钩子
        self.hook_manager.register(
            "test_event",
            slow_handler,
            max_execution_time=2.0,  # 2秒超时
        )

        with self.assertLogs("minicrm.hooks", level="WARNING") as log:
            results = self.hook_manager.trigger("test_event")

        # 验证超时警告
        self.assertIn("钩子执行超时", log.output[0])
        self.assertTrue(results[0].success)  # 钩子仍然成功执行


class TestHookDecorators(unittest.TestCase):
    """测试钩子装饰器"""

    def setUp(self):
        """测试准备"""
        # 清除全局钩子管理器的钩子
        from src.minicrm.core.hooks import hook_manager

        hook_manager.clear_hooks()

    def test_hook_decorator(self):
        """测试钩子装饰器"""

        @hook("test_event", priority=HookPriority.HIGH)
        def test_handler():
            return "decorated_result"

        from src.minicrm.core.hooks import hook_manager

        # 验证钩子已注册
        hooks = hook_manager.get_hooks("test_event")
        self.assertEqual(len(hooks["test_event"]), 1)

        # 触发钩子
        results = hook_manager.trigger("test_event")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].result, "decorated_result")

    @patch("time.time")
    def test_performance_hook_decorator(self, mock_time):
        """测试性能钩子装饰器"""
        mock_time.side_effect = [1000.0, 1001.5]  # 模拟1.5秒执行时间

        @performance_hook("test_operation", threshold=1.0)
        def test_function():
            return "result"

        with self.assertLogs("minicrm.performance", level="INFO"):
            result = test_function()

        self.assertEqual(result, "result")

    def test_audit_hook_decorator(self):
        """测试审计钩子装饰器"""

        @audit_hook("CREATE", "CUSTOMER")
        def test_function():
            return "created"

        with self.assertLogs("minicrm.audit", level="INFO"):
            result = test_function()

        self.assertEqual(result, "created")

    def test_audit_hook_decorator_with_exception(self):
        """测试审计钩子装饰器异常处理"""

        @audit_hook("CREATE", "CUSTOMER")
        def test_function():
            raise ValueError("Test error")

        with self.assertLogs("minicrm.audit", level="INFO"):
            with self.assertRaises(ValueError):
                test_function()


class TestGlobalFunctions(unittest.TestCase):
    """测试全局钩子函数"""

    def setUp(self):
        """测试准备"""
        # 清除全局钩子管理器的钩子
        from src.minicrm.core.hooks import hook_manager

        hook_manager.clear_hooks()

    def test_trigger_hook(self):
        """测试触发钩子全局函数"""

        def test_handler():
            return "global_result"

        register_hook("test_event", test_handler)

        results = trigger_hook("test_event")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].result, "global_result")

    def test_register_unregister_hook(self):
        """测试注册和注销钩子全局函数"""

        def test_handler():
            return "test_result"

        # 注册钩子
        hook_info = register_hook("test_event", test_handler)
        self.assertIsInstance(hook_info, HookInfo)

        # 验证钩子已注册
        results = trigger_hook("test_event")
        self.assertEqual(len(results), 1)

        # 注销钩子
        success = unregister_hook("test_event", test_handler)
        self.assertTrue(success)

        # 验证钩子已注销
        results = trigger_hook("test_event")
        self.assertEqual(len(results), 0)

    def test_get_hook_manager(self):
        """测试获取钩子管理器"""
        manager = get_hook_manager()

        self.assertIsInstance(manager, HookManager)

    @patch("src.minicrm.core.hooks.hook_manager")
    def test_shutdown_hooks(self, mock_hook_manager):
        """测试关闭钩子系统"""
        shutdown_hooks()

        mock_hook_manager.shutdown.assert_called_once()


if __name__ == "__main__":
    unittest.main()
