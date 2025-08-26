"""
常量定义测试模块

测试MiniCRM系统常量的定义和工具函数。
"""

import unittest

from src.minicrm.core.constants import (
    DATABASE_CONFIG,
    DEFAULT_CONFIG,
    UI_CONFIG,
    ContractStatus,
    CustomerLevel,
    InteractionType,
    Priority,
    QuoteStatus,
    ServiceTicketStatus,
    SupplierLevel,
    get_enum_by_value,
    get_enum_choices,
    validate_enum_value,
)


class TestCustomerLevel(unittest.TestCase):
    """测试客户等级枚举"""

    def test_customer_level_values(self):
        """测试客户等级枚举值"""
        self.assertEqual(CustomerLevel.VIP.value, "vip")
        self.assertEqual(CustomerLevel.IMPORTANT.value, "important")
        self.assertEqual(CustomerLevel.NORMAL.value, "normal")
        self.assertEqual(CustomerLevel.POTENTIAL.value, "potential")

    def test_customer_level_display_names(self):
        """测试客户等级显示名称"""
        self.assertEqual(CustomerLevel.VIP.display_name, "VIP客户")
        self.assertEqual(CustomerLevel.IMPORTANT.display_name, "重要客户")
        self.assertEqual(CustomerLevel.NORMAL.display_name, "普通客户")
        self.assertEqual(CustomerLevel.POTENTIAL.display_name, "潜在客户")

    def test_customer_level_colors(self):
        """测试客户等级颜色"""
        self.assertEqual(CustomerLevel.VIP.color, "#FF6B6B")
        self.assertEqual(CustomerLevel.IMPORTANT.color, "#4ECDC4")
        self.assertEqual(CustomerLevel.NORMAL.color, "#45B7D1")
        self.assertEqual(CustomerLevel.POTENTIAL.color, "#96CEB4")


class TestSupplierLevel(unittest.TestCase):
    """测试供应商等级枚举"""

    def test_supplier_level_values(self):
        """测试供应商等级枚举值"""
        self.assertEqual(SupplierLevel.STRATEGIC.value, "strategic")
        self.assertEqual(SupplierLevel.IMPORTANT.value, "important")
        self.assertEqual(SupplierLevel.NORMAL.value, "normal")
        self.assertEqual(SupplierLevel.BACKUP.value, "backup")

    def test_supplier_level_display_names(self):
        """测试供应商等级显示名称"""
        self.assertEqual(SupplierLevel.STRATEGIC.display_name, "战略供应商")
        self.assertEqual(SupplierLevel.IMPORTANT.display_name, "重要供应商")
        self.assertEqual(SupplierLevel.NORMAL.display_name, "普通供应商")
        self.assertEqual(SupplierLevel.BACKUP.display_name, "备选供应商")


class TestInteractionType(unittest.TestCase):
    """测试互动类型枚举"""

    def test_interaction_type_values(self):
        """测试互动类型枚举值"""
        self.assertEqual(InteractionType.PHONE_CALL.value, "phone_call")
        self.assertEqual(InteractionType.EMAIL.value, "email")
        self.assertEqual(InteractionType.MEETING.value, "meeting")
        self.assertEqual(InteractionType.VISIT.value, "visit")

    def test_interaction_type_display_names(self):
        """测试互动类型显示名称"""
        self.assertEqual(InteractionType.PHONE_CALL.display_name, "电话沟通")
        self.assertEqual(InteractionType.EMAIL.display_name, "邮件沟通")
        self.assertEqual(InteractionType.MEETING.display_name, "会议")
        self.assertEqual(InteractionType.VISIT.display_name, "拜访")


class TestContractStatus(unittest.TestCase):
    """测试合同状态枚举"""

    def test_contract_status_values(self):
        """测试合同状态枚举值"""
        self.assertEqual(ContractStatus.DRAFT.value, "draft")
        self.assertEqual(ContractStatus.SIGNED.value, "signed")
        self.assertEqual(ContractStatus.ACTIVE.value, "active")
        self.assertEqual(ContractStatus.COMPLETED.value, "completed")

    def test_contract_status_display_names(self):
        """测试合同状态显示名称"""
        self.assertEqual(ContractStatus.DRAFT.display_name, "草稿")
        self.assertEqual(ContractStatus.SIGNED.display_name, "已签署")
        self.assertEqual(ContractStatus.ACTIVE.display_name, "执行中")
        self.assertEqual(ContractStatus.COMPLETED.display_name, "已完成")


class TestQuoteStatus(unittest.TestCase):
    """测试报价状态枚举"""

    def test_quote_status_values(self):
        """测试报价状态枚举值"""
        self.assertEqual(QuoteStatus.DRAFT.value, "draft")
        self.assertEqual(QuoteStatus.SENT.value, "sent")
        self.assertEqual(QuoteStatus.ACCEPTED.value, "accepted")
        self.assertEqual(QuoteStatus.REJECTED.value, "rejected")

    def test_quote_status_display_names(self):
        """测试报价状态显示名称"""
        self.assertEqual(QuoteStatus.DRAFT.display_name, "草稿")
        self.assertEqual(QuoteStatus.SENT.display_name, "已发送")
        self.assertEqual(QuoteStatus.ACCEPTED.display_name, "已接受")
        self.assertEqual(QuoteStatus.REJECTED.display_name, "已拒绝")


class TestServiceTicketStatus(unittest.TestCase):
    """测试售后工单状态枚举"""

    def test_service_ticket_status_values(self):
        """测试售后工单状态枚举值"""
        self.assertEqual(ServiceTicketStatus.OPEN.value, "open")
        self.assertEqual(ServiceTicketStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(ServiceTicketStatus.RESOLVED.value, "resolved")
        self.assertEqual(ServiceTicketStatus.CLOSED.value, "closed")

    def test_service_ticket_status_display_names(self):
        """测试售后工单状态显示名称"""
        self.assertEqual(ServiceTicketStatus.OPEN.display_name, "已开启")
        self.assertEqual(ServiceTicketStatus.IN_PROGRESS.display_name, "处理中")
        self.assertEqual(ServiceTicketStatus.RESOLVED.display_name, "已解决")
        self.assertEqual(ServiceTicketStatus.CLOSED.display_name, "已关闭")


class TestPriority(unittest.TestCase):
    """测试优先级枚举"""

    def test_priority_values(self):
        """测试优先级枚举值"""
        self.assertEqual(Priority.LOW.value, 1)
        self.assertEqual(Priority.NORMAL.value, 2)
        self.assertEqual(Priority.HIGH.value, 3)
        self.assertEqual(Priority.URGENT.value, 4)
        self.assertEqual(Priority.CRITICAL.value, 5)

    def test_priority_comparison(self):
        """测试优先级比较"""
        self.assertTrue(Priority.CRITICAL > Priority.HIGH)
        self.assertTrue(Priority.HIGH > Priority.NORMAL)
        self.assertTrue(Priority.NORMAL > Priority.LOW)

    def test_priority_display_names(self):
        """测试优先级显示名称"""
        self.assertEqual(Priority.LOW.display_name, "低")
        self.assertEqual(Priority.NORMAL.display_name, "普通")
        self.assertEqual(Priority.HIGH.display_name, "高")
        self.assertEqual(Priority.URGENT.display_name, "紧急")
        self.assertEqual(Priority.CRITICAL.display_name, "严重")

    def test_priority_colors(self):
        """测试优先级颜色"""
        self.assertEqual(Priority.LOW.color, "#28A745")
        self.assertEqual(Priority.NORMAL.color, "#17A2B8")
        self.assertEqual(Priority.HIGH.color, "#FFC107")
        self.assertEqual(Priority.URGENT.color, "#FD7E14")
        self.assertEqual(Priority.CRITICAL.color, "#DC3545")


class TestConfigurations(unittest.TestCase):
    """测试配置常量"""

    def test_database_config_structure(self):
        """测试数据库配置结构"""
        self.assertIn("default_name", DATABASE_CONFIG)
        self.assertIn("default_path", DATABASE_CONFIG)
        self.assertIn("backup_interval", DATABASE_CONFIG)
        self.assertIn("max_backups", DATABASE_CONFIG)
        self.assertIn("pragma_settings", DATABASE_CONFIG)

        # 测试pragma设置
        pragma = DATABASE_CONFIG["pragma_settings"]
        self.assertIn("journal_mode", pragma)
        self.assertIn("synchronous", pragma)
        self.assertIn("cache_size", pragma)

    def test_ui_config_structure(self):
        """测试UI配置结构"""
        self.assertIn("window", UI_CONFIG)
        self.assertIn("theme", UI_CONFIG)
        self.assertIn("fonts", UI_CONFIG)
        self.assertIn("colors", UI_CONFIG)

        # 测试窗口配置
        window = UI_CONFIG["window"]
        self.assertIn("min_width", window)
        self.assertIn("min_height", window)
        self.assertIn("default_width", window)
        self.assertIn("default_height", window)

        # 测试主题配置
        theme = UI_CONFIG["theme"]
        self.assertIn("default", theme)
        self.assertIn("available", theme)

        # 测试颜色配置
        colors = UI_CONFIG["colors"]
        self.assertIn("light", colors)
        self.assertIn("dark", colors)

    def test_default_config_completeness(self):
        """测试默认配置完整性"""
        self.assertIn("app", DEFAULT_CONFIG)
        self.assertIn("database", DEFAULT_CONFIG)
        self.assertIn("ui", DEFAULT_CONFIG)
        self.assertIn("logging", DEFAULT_CONFIG)
        self.assertIn("validation", DEFAULT_CONFIG)
        self.assertIn("business", DEFAULT_CONFIG)
        self.assertIn("document", DEFAULT_CONFIG)
        self.assertIn("directories", DEFAULT_CONFIG)


class TestEnumUtilityFunctions(unittest.TestCase):
    """测试枚举工具函数"""

    def test_get_enum_choices(self):
        """测试获取枚举选择项"""
        choices = get_enum_choices(CustomerLevel)

        expected_choices = {
            "vip": "VIP客户",
            "important": "重要客户",
            "normal": "普通客户",
            "potential": "潜在客户",
        }

        self.assertEqual(choices, expected_choices)

    def test_get_enum_by_value_valid(self):
        """测试根据值获取枚举项 - 有效值"""
        result = get_enum_by_value(CustomerLevel, "vip")
        self.assertEqual(result, CustomerLevel.VIP)

        result = get_enum_by_value(Priority, 3)
        self.assertEqual(result, Priority.HIGH)

    def test_get_enum_by_value_invalid(self):
        """测试根据值获取枚举项 - 无效值"""
        result = get_enum_by_value(CustomerLevel, "invalid")
        self.assertIsNone(result)

        result = get_enum_by_value(Priority, 999)
        self.assertIsNone(result)

    def test_validate_enum_value_valid(self):
        """测试验证枚举值 - 有效值"""
        self.assertTrue(validate_enum_value(CustomerLevel, "vip"))
        self.assertTrue(validate_enum_value(Priority, 1))

    def test_validate_enum_value_invalid(self):
        """测试验证枚举值 - 无效值"""
        self.assertFalse(validate_enum_value(CustomerLevel, "invalid"))
        self.assertFalse(validate_enum_value(Priority, 999))


if __name__ == "__main__":
    unittest.main()
