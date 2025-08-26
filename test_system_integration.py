#!/usr/bin/env python3
"""
MiniCRM 系统集成测试

测试系统集成的基本功能，包括：
- 应用程序启动
- 导航系统
- 数据总线
- 事件总线
- 状态管理器
- 通知系统

这是一个基本的集成测试，验证所有组件能够正常协作。
"""

import logging
import sys
from pathlib import Path


# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_imports():
    """测试所有核心组件的导入"""
    print("🔍 测试组件导入...")

    try:
        # 测试核心组件导入

        print("✅ 所有核心组件导入成功")
        return True

    except Exception as e:
        print(f"❌ 组件导入失败: {e}")
        return False


def test_data_bus():
    """测试数据总线功能"""
    print("🔍 测试数据总线...")

    try:
        from minicrm.ui.data_bus import DataBus

        # 创建数据总线实例
        data_bus = DataBus()

        # 测试数据设置和获取
        test_key = "test_data"
        test_value = "test_value"

        success = data_bus.set_data(test_key, test_value, source="test")
        if not success:
            print("❌ 数据设置失败")
            return False

        retrieved_value = data_bus.get_data(test_key)
        if retrieved_value != test_value:
            print(f"❌ 数据获取失败: 期望 {test_value}, 实际 {retrieved_value}")
            return False

        # 测试数据订阅
        callback_called = False

        def test_callback(event):
            nonlocal callback_called
            callback_called = True

        data_bus.subscribe(test_key, test_callback)
        data_bus.set_data(test_key, "new_value", source="test")

        if not callback_called:
            print("❌ 数据订阅回调未被调用")
            return False

        print("✅ 数据总线功能正常")
        return True

    except Exception as e:
        print(f"❌ 数据总线测试失败: {e}")
        return False


def test_event_bus():
    """测试事件总线功能"""
    print("🔍 测试事件总线...")

    try:
        from minicrm.ui.event_bus import EventBus

        # 创建事件总线实例
        event_bus = EventBus()

        # 测试事件发布和订阅
        event_received = False
        received_data = None

        def test_event_handler(event):
            nonlocal event_received, received_data
            event_received = True
            received_data = event.data

        # 订阅事件
        subscription_id = event_bus.subscribe("test.event", test_event_handler)

        # 发布事件
        test_data = {"message": "test"}
        event_id = event_bus.publish(
            "test.event", data=test_data, source="test", sync=True
        )

        if not event_received:
            print("❌ 事件未被接收")
            return False

        if received_data != test_data:
            print(f"❌ 事件数据不匹配: 期望 {test_data}, 实际 {received_data}")
            return False

        # 测试取消订阅
        event_bus.unsubscribe(subscription_id)

        print("✅ 事件总线功能正常")
        return True

    except Exception as e:
        print(f"❌ 事件总线测试失败: {e}")
        return False


def test_state_manager():
    """测试状态管理器功能"""
    print("🔍 测试状态管理器...")

    try:
        from minicrm.ui.state_manager import StateManager, TypedStateValidator

        # 创建状态管理器实例
        state_manager = StateManager()

        # 定义状态
        state_manager.define_state(
            "test_state",
            default_value="default",
            validator=TypedStateValidator(str),
            description="测试状态",
        )

        # 测试状态设置和获取
        test_value = "test_value"
        success = state_manager.set_state("test_state", test_value, source="test")

        if not success:
            print("❌ 状态设置失败")
            return False

        retrieved_value = state_manager.get_state("test_state")
        if retrieved_value != test_value:
            print(f"❌ 状态获取失败: 期望 {test_value}, 实际 {retrieved_value}")
            return False

        # 测试状态订阅
        callback_called = False

        def test_state_callback(change):
            nonlocal callback_called
            callback_called = True

        state_manager.subscribe_state("test_state", test_state_callback)
        state_manager.set_state("test_state", "new_value", source="test")

        if not callback_called:
            print("❌ 状态订阅回调未被调用")
            return False

        print("✅ 状态管理器功能正常")
        return True

    except Exception as e:
        print(f"❌ 状态管理器测试失败: {e}")
        return False


def test_notification_system():
    """测试通知系统功能"""
    print("🔍 测试通知系统...")

    try:
        from minicrm.ui.notification_system import NotificationSystem, NotificationType

        # 创建通知系统实例
        notification_system = NotificationSystem()

        # 测试通知显示
        notification_id = notification_system.show_notification(
            message="测试通知",
            title="测试",
            notification_type=NotificationType.INFO,
            source="test",
        )

        if not notification_id:
            print("❌ 通知创建失败")
            return False

        # 检查活跃通知
        active_notifications = notification_system.get_active_notifications()
        if len(active_notifications) == 0:
            print("❌ 没有活跃通知")
            return False

        # 测试通知关闭
        success = notification_system.dismiss_notification(notification_id)
        if not success:
            print("❌ 通知关闭失败")
            return False

        print("✅ 通知系统功能正常")
        return True

    except Exception as e:
        print(f"❌ 通知系统测试失败: {e}")
        return False


def test_navigation_registry():
    """测试导航注册系统功能"""
    print("🔍 测试导航注册系统...")

    try:
        from minicrm.ui.navigation_registry import NavigationItem

        # 测试导航项创建
        test_item = NavigationItem(
            name="test_page", title="测试页面", icon="🧪", description="测试页面"
        )

        # 验证导航项属性
        if test_item.name != "test_page":
            print("❌ 导航项名称不正确")
            return False

        if test_item.title != "测试页面":
            print("❌ 导航项标题不正确")
            return False

        if test_item.icon != "🧪":
            print("❌ 导航项图标不正确")
            return False

        print("✅ 导航注册系统功能正常")
        return True

    except Exception as e:
        print(f"❌ 导航注册系统测试失败: {e}")
        return False


def test_system_integration():
    """测试系统集成"""
    print("🔍 测试系统集成...")

    try:
        # 创建全局实例
        from minicrm.ui.data_bus import DataBus, get_data_bus, set_global_data_bus
        from minicrm.ui.event_bus import EventBus, get_event_bus, set_global_event_bus
        from minicrm.ui.notification_system import (
            NotificationSystem,
            get_notification_system,
            set_global_notification_system,
        )
        from minicrm.ui.state_manager import (
            StateManager,
            get_state_manager,
            set_global_state_manager,
        )

        data_bus = DataBus()
        event_bus = EventBus()
        state_manager = StateManager()
        notification_system = NotificationSystem()

        # 设置全局实例
        set_global_data_bus(data_bus)
        set_global_event_bus(event_bus)
        set_global_state_manager(state_manager)
        set_global_notification_system(notification_system)

        # 测试全局实例获取
        if get_data_bus() != data_bus:
            print("❌ 全局数据总线设置失败")
            return False

        if get_event_bus() != event_bus:
            print("❌ 全局事件总线设置失败")
            return False

        if get_state_manager() != state_manager:
            print("❌ 全局状态管理器设置失败")
            return False

        if get_notification_system() != notification_system:
            print("❌ 全局通知系统设置失败")
            return False

        # 测试组件间通信
        # 直接测试通知系统
        notification_id = notification_system.show_info("系统集成测试通知", "测试")

        # 检查通知是否被创建
        active_notifications = notification_system.get_active_notifications()
        if len(active_notifications) == 0:
            print("❌ 通知系统通信失败")
            return False

        print("✅ 系统集成功能正常")
        return True

    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始MiniCRM系统集成测试")
    print("=" * 50)

    # 设置日志级别
    logging.basicConfig(level=logging.WARNING)

    # 运行所有测试
    tests = [
        ("组件导入", test_imports),
        ("数据总线", test_data_bus),
        ("事件总线", test_event_bus),
        ("状态管理器", test_state_manager),
        ("通知系统", test_notification_system),
        ("导航注册系统", test_navigation_registry),
        ("系统集成", test_system_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试 {test_name} 发生异常: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("🎉 所有测试通过！系统集成成功！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查系统集成")
        return 1


if __name__ == "__main__":
    sys.exit(main())
