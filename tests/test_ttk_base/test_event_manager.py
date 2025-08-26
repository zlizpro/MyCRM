"""
事件管理器单元测试

测试EventManager及其相关类的功能，包括：
- 事件绑定和解绑功能测试
- 事件触发和处理测试
- 事件委托功能测试
- 异步事件处理测试
- 事件统计和调试功能测试

作者: MiniCRM开发团队
"""

import os
import sys
import time
import unittest
from unittest.mock import Mock


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.minicrm.ui.ttk_base.event_manager import (
    Event,
    EventHandler,
    EventManager,
    EventPriority,
    EventType,
    debounce,
    event_handler,
    get_global_event_manager,
    throttle,
)


class TestEvent(unittest.TestCase):
    """事件对象测试类"""

    def test_event_creation(self):
        """测试事件创建"""
        event = Event("test_event", source="test_source", data={"key": "value"})

        self.assertEqual(event.event_type, "test_event")
        self.assertEqual(event.source, "test_source")
        self.assertEqual(event.data["key"], "value")
        self.assertEqual(event.priority, EventPriority.NORMAL)
        self.assertFalse(event.handled)
        self.assertFalse(event.cancelled)
        self.assertIsNotNone(event.timestamp)

    def test_event_cancel(self):
        """测试事件取消"""
        event = Event("test_event")
        self.assertFalse(event.is_cancelled())

        event.cancel()
        self.assertTrue(event.is_cancelled())

    def test_event_mark_handled(self):
        """测试事件标记为已处理"""
        event = Event("test_event")
        self.assertFalse(event.is_handled())

        event.mark_handled()
        self.assertTrue(event.is_handled())


class TestEventHandler(unittest.TestCase):
    """事件处理器测试类"""

    def test_event_handler_creation(self):
        """测试事件处理器创建"""
        handler_func = Mock()
        handler = EventHandler(handler_func, EventPriority.HIGH, once=True)

        self.assertEqual(handler.handler, handler_func)
        self.assertEqual(handler.priority, EventPriority.HIGH)
        self.assertTrue(handler.once)
        self.assertEqual(handler.call_count, 0)

    def test_event_handler_execution(self):
        """测试事件处理器执行"""
        handler_func = Mock(return_value="result")
        handler = EventHandler(handler_func)
        event = Event("test_event")

        result = handler.handle(event)

        self.assertEqual(result, "result")
        self.assertEqual(handler.call_count, 1)
        self.assertIsNotNone(handler.last_call_time)
        handler_func.assert_called_once_with(event)

    def test_event_handler_condition(self):
        """测试事件处理器条件"""
        handler_func = Mock()
        condition = Mock(return_value=False)
        handler = EventHandler(handler_func, condition=condition)
        event = Event("test_event")

        result = handler.handle(event)

        self.assertIsNone(result)
        self.assertEqual(handler.call_count, 0)
        condition.assert_called_once_with(event)
        handler_func.assert_not_called()

    def test_event_handler_once(self):
        """测试一次性事件处理器"""
        handler_func = Mock()
        handler = EventHandler(handler_func, once=True)

        self.assertFalse(handler.should_remove())

        # 执行一次
        event = Event("test_event")
        handler.handle(event)

        self.assertTrue(handler.should_remove())


class TestEventManagerLogic(unittest.TestCase):
    """事件管理器逻辑测试类（无需GUI）"""

    def setUp(self):
        """测试准备"""
        self.event_manager = EventManager(enable_debug=True)

    def tearDown(self):
        """测试清理"""
        self.event_manager.cleanup()

    def test_event_manager_creation(self):
        """测试事件管理器创建"""
        self.assertIsNotNone(self.event_manager)
        self.assertTrue(self.event_manager.enable_debug)
        self.assertIsNotNone(self.event_manager._handlers)
        self.assertIsNotNone(self.event_manager._event_queue)

    def test_bind_global_event(self):
        """测试绑定全局事件"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler)

        self.assertIn("test_event", self.event_manager._handlers)
        self.assertEqual(len(self.event_manager._handlers["test_event"]), 1)

    def test_unbind_global_event(self):
        """测试解绑全局事件"""
        handler = Mock()

        # 先绑定
        self.event_manager.bind_global_event("test_event", handler)
        self.assertEqual(len(self.event_manager._handlers["test_event"]), 1)

        # 再解绑
        self.event_manager.unbind_global_event("test_event", handler)
        self.assertEqual(len(self.event_manager._handlers["test_event"]), 0)

    def test_trigger_global_event(self):
        """测试触发全局事件"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler)
        self.event_manager.trigger_event("test_event", data={"key": "value"})

        # 等待异步处理完成
        time.sleep(0.1)

        handler.assert_called_once()
        event_arg = handler.call_args[0][0]
        self.assertEqual(event_arg.event_type, "test_event")
        self.assertEqual(event_arg.data["key"], "value")

    def test_event_priority_ordering(self):
        """测试事件优先级排序"""
        call_order = []

        def low_handler(event):
            call_order.append("low")

        def high_handler(event):
            call_order.append("high")

        def normal_handler(event):
            call_order.append("normal")

        # 按相反顺序绑定
        self.event_manager.bind_global_event(
            "test_event", low_handler, EventPriority.LOW
        )
        self.event_manager.bind_global_event(
            "test_event", high_handler, EventPriority.HIGH
        )
        self.event_manager.bind_global_event(
            "test_event", normal_handler, EventPriority.NORMAL
        )

        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        # 应该按优先级顺序执行：HIGH -> NORMAL -> LOW
        self.assertEqual(call_order, ["high", "normal", "low"])

    def test_once_event_handler(self):
        """测试一次性事件处理器"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler, once=True)

        # 触发两次事件
        self.event_manager.trigger_event("test_event")
        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        # 应该只被调用一次
        self.assertEqual(handler.call_count, 1)

    def test_event_condition(self):
        """测试事件条件"""
        handler = Mock()
        condition = Mock(return_value=False)

        self.event_manager.bind_global_event("test_event", handler, condition=condition)
        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        # 条件为False，处理器不应该被调用
        handler.assert_not_called()
        condition.assert_called_once()

    def test_event_cancellation(self):
        """测试事件取消"""
        handler1 = Mock()
        handler2 = Mock()

        def cancelling_handler(event):
            event.cancel()
            handler1()

        self.event_manager.bind_global_event(
            "test_event", cancelling_handler, EventPriority.HIGH
        )
        self.event_manager.bind_global_event("test_event", handler2, EventPriority.LOW)

        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        # 第一个处理器取消了事件，第二个不应该被调用
        handler1.assert_called_once()
        handler2.assert_not_called()

    def test_async_event_processing(self):
        """测试异步事件处理"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler)
        self.event_manager.trigger_event("test_event", async_mode=True)

        # 等待异步处理
        time.sleep(0.2)

        handler.assert_called_once()

    def test_event_statistics(self):
        """测试事件统计"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler)
        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        stats = self.event_manager.get_event_stats()
        self.assertIn("test_event", stats)
        self.assertEqual(stats["test_event"]["count"], 1)
        self.assertGreater(stats["test_event"]["total_time"], 0)

    def test_clear_event_statistics(self):
        """测试清空事件统计"""
        handler = Mock()

        self.event_manager.bind_global_event("test_event", handler)
        self.event_manager.trigger_event("test_event")
        time.sleep(0.1)

        # 确认有统计数据
        stats = self.event_manager.get_event_stats()
        self.assertIn("test_event", stats)

        # 清空统计
        self.event_manager.clear_event_stats()
        stats = self.event_manager.get_event_stats()
        self.assertEqual(len(stats), 0)


class TestEventDecorators(unittest.TestCase):
    """事件装饰器测试类"""

    def test_event_handler_decorator(self):
        """测试事件处理器装饰器"""

        @event_handler("test_event", priority=EventPriority.HIGH, once=True)
        def test_handler(event):
            return "handled"

        self.assertEqual(test_handler._event_type, "test_event")
        self.assertEqual(test_handler._event_priority, EventPriority.HIGH)
        self.assertTrue(test_handler._event_once)

    def test_throttle_decorator(self):
        """测试节流装饰器"""
        call_count = [0]

        @throttle(0.1)  # 100ms节流
        def throttled_func():
            call_count[0] += 1

        # 快速调用多次
        for _ in range(5):
            throttled_func()

        # 应该只执行一次
        self.assertEqual(call_count[0], 1)

        # 等待节流间隔
        time.sleep(0.15)
        throttled_func()

        # 现在应该执行第二次
        self.assertEqual(call_count[0], 2)

    def test_debounce_decorator(self):
        """测试防抖装饰器"""
        call_count = [0]

        @debounce(0.1)  # 100ms防抖
        def debounced_func():
            call_count[0] += 1

        # 快速调用多次
        for _ in range(5):
            debounced_func()

        # 立即检查，应该还没执行
        self.assertEqual(call_count[0], 0)

        # 等待防抖延迟
        time.sleep(0.15)

        # 现在应该执行一次
        self.assertEqual(call_count[0], 1)


class TestGlobalEventManager(unittest.TestCase):
    """全局事件管理器测试类"""

    def test_get_global_event_manager(self):
        """测试获取全局事件管理器"""
        manager1 = get_global_event_manager()
        manager2 = get_global_event_manager()

        # 应该返回同一个实例
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, EventManager)

    def tearDown(self):
        """测试清理"""
        # 清理全局事件管理器
        from src.minicrm.ui.ttk_base.event_manager import cleanup_global_event_manager

        cleanup_global_event_manager()


class TestEventTypes(unittest.TestCase):
    """事件类型测试类"""

    def test_event_type_enum(self):
        """测试事件类型枚举"""
        self.assertEqual(EventType.CLICK.value, "click")
        self.assertEqual(EventType.DOUBLE_CLICK.value, "double_click")
        self.assertEqual(EventType.RIGHT_CLICK.value, "right_click")
        self.assertEqual(EventType.KEY_PRESS.value, "key_press")
        self.assertEqual(EventType.KEY_RELEASE.value, "key_release")
        self.assertEqual(EventType.FOCUS_IN.value, "focus_in")
        self.assertEqual(EventType.FOCUS_OUT.value, "focus_out")
        self.assertEqual(EventType.MOUSE_ENTER.value, "mouse_enter")
        self.assertEqual(EventType.MOUSE_LEAVE.value, "mouse_leave")
        self.assertEqual(EventType.MOUSE_MOVE.value, "mouse_move")
        self.assertEqual(EventType.WINDOW_RESIZE.value, "window_resize")
        self.assertEqual(EventType.CUSTOM.value, "custom")

    def test_event_priority_enum(self):
        """测试事件优先级枚举"""
        self.assertEqual(EventPriority.LOW.value, 1)
        self.assertEqual(EventPriority.NORMAL.value, 2)
        self.assertEqual(EventPriority.HIGH.value, 3)
        self.assertEqual(EventPriority.CRITICAL.value, 4)


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2)
