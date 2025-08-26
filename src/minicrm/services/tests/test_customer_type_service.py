"""MiniCRM 客户类型服务单元测试

测试客户类型管理服务的所有功能,包括:
- 客户类型的CRUD操作
- 数据验证和业务规则
- 类型使用统计
- 异常处理

遵循测试最佳实践:
- 使用Mock对象隔离依赖
- 测试覆盖正常和异常情况
- 验证transfunctions的正确使用
"""

import unittest
from unittest.mock import MagicMock

from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from minicrm.services.customer_type_service import CustomerTypeService


class TestCustomerTypeService(unittest.TestCase):
    """客户类型服务测试类"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = MagicMock()
        self.service = CustomerTypeService(self.mock_dao)

    def test_create_customer_type_success(self):
        """测试创建客户类型成功"""
        # 准备测试数据
        type_data = {
            "name": "VIP客户",
            "description": "重要客户类型",
            "color_code": "#FF0000",
        }

        # 模拟DAO返回
        self.mock_dao.insert.return_value = 1
        self.service._check_type_name_exists = MagicMock(return_value=False)

        # 执行测试
        result = self.service.create_customer_type(type_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.mock_dao.insert.assert_called_once()

        # 验证默认值被设置
        call_args = self.mock_dao.insert.call_args[0][0]
        self.assertIn("created_at", call_args)
        self.assertTrue(call_args["is_active"])

    def test_create_customer_type_validation_error(self):
        """测试创建客户类型验证错误"""
        # 准备无效数据(缺少必填字段)
        type_data = {"description": "没有名称的类型"}

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.service.create_customer_type(type_data)

        self.assertIn("name", str(context.exception))

    def test_create_customer_type_duplicate_name(self):
        """测试创建重复名称的客户类型"""
        # 准备测试数据
        type_data = {"name": "已存在的类型"}

        # 模拟名称已存在
        self.service._check_type_name_exists = MagicMock(return_value=True)

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create_customer_type(type_data)

        self.assertIn("已存在", str(context.exception))

    def test_update_customer_type_success(self):
        """测试更新客户类型成功"""
        # 准备测试数据
        type_id = 1
        update_data = {"name": "更新后的名称"}

        # 模拟DAO返回
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "原名称"}
        self.mock_dao.update.return_value = True
        self.service._check_type_name_exists = MagicMock(return_value=False)

        # 执行测试
        result = self.service.update_customer_type(type_id, update_data)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    def test_update_customer_type_not_found(self):
        """测试更新不存在的客户类型"""
        # 模拟类型不存在
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError):
            self.service.update_customer_type(999, {"name": "新名称"})

    def test_delete_customer_type_success(self):
        """测试删除客户类型成功"""
        # 准备测试数据
        type_id = 1

        # 模拟DAO返回
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "测试类型"}
        self.mock_dao.delete.return_value = True
        self.service.get_type_usage_count = MagicMock(return_value=0)

        # 执行测试
        result = self.service.delete_customer_type(type_id)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.delete.assert_called_once_with(type_id)

    def test_delete_customer_type_in_use(self):
        """测试删除正在使用的客户类型"""
        # 准备测试数据
        type_id = 1

        # 模拟类型正在使用
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "使用中的类型"}
        self.service.get_type_usage_count = MagicMock(return_value=5)

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.service.delete_customer_type(type_id)

        self.assertIn("5 个客户使用", str(context.exception))

    def test_delete_customer_type_force(self):
        """测试强制删除正在使用的客户类型"""
        # 准备测试数据
        type_id = 1

        # 模拟类型正在使用
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "使用中的类型"}
        self.mock_dao.delete.return_value = True
        self.service.get_type_usage_count = MagicMock(return_value=5)

        # 执行强制删除
        result = self.service.delete_customer_type(type_id, force=True)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.delete.assert_called_once_with(type_id)

    def test_get_customer_type_by_id_success(self):
        """测试根据ID获取客户类型成功"""
        # 准备测试数据
        type_id = 1
        expected_data = {"id": 1, "name": "测试类型"}

        # 模拟DAO返回
        self.mock_dao.get_by_id.return_value = expected_data
        self.service.get_type_usage_count = MagicMock(return_value=3)

        # 执行测试
        result = self.service.get_customer_type_by_id(type_id)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["usage_count"], 3)
        self.assertFalse(result["can_delete"])

    def test_get_customer_type_by_id_not_found(self):
        """测试获取不存在的客户类型"""
        # 模拟类型不存在
        self.mock_dao.get_by_id.return_value = None

        # 执行测试
        result = self.service.get_customer_type_by_id(999)

        # 验证结果
        self.assertIsNone(result)

    def test_get_all_customer_types(self):
        """测试获取所有客户类型"""
        # 准备测试数据
        expected_types = [{"id": 1, "name": "类型1"}, {"id": 2, "name": "类型2"}]

        # 模拟DAO返回
        self.mock_dao.get_all.return_value = expected_types
        self.service.get_type_usage_count = MagicMock(side_effect=[2, 0])

        # 执行测试
        result = self.service.get_all_customer_types()

        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["usage_count"], 2)
        self.assertEqual(result[1]["usage_count"], 0)
        self.assertFalse(result[0]["can_delete"])
        self.assertTrue(result[1]["can_delete"])

    def test_search_customer_types(self):
        """测试搜索客户类型"""
        # 准备测试数据
        query = "VIP"
        expected_types = [{"id": 1, "name": "VIP客户"}]

        # 模拟DAO返回
        self.mock_dao.search.return_value = expected_types
        self.service.get_type_usage_count = MagicMock(return_value=1)

        # 执行测试
        result = self.service.search_customer_types(query)

        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "VIP客户")
        self.mock_dao.search.assert_called_once()

    def test_get_type_statistics(self):
        """测试获取客户类型统计"""
        # 准备测试数据
        mock_types = [
            {"id": 1, "name": "类型1", "usage_count": 5},
            {"id": 2, "name": "类型2", "usage_count": 0},
            {"id": 3, "name": "类型3", "usage_count": 3},
        ]

        # 模拟方法返回
        self.service.get_all_customer_types = MagicMock(return_value=mock_types)

        # 执行测试
        result = self.service.get_type_statistics()

        # 验证结果
        self.assertEqual(result["total_types"], 3)
        self.assertEqual(result["used_types"], 2)
        self.assertEqual(result["unused_types"], 1)
        self.assertEqual(result["most_used_type"], "类型1")

    def test_validate_customer_type_data_valid(self):
        """测试有效数据验证"""
        # 准备有效数据
        valid_data = {
            "name": "有效类型",
            "description": "有效描述",
            "color_code": "#FF0000",
            "sort_order": 1,
        }

        # 执行验证(不应抛出异常)
        try:
            self.service._validate_customer_type_data(valid_data)
        except ValidationError:
            self.fail("有效数据验证失败")

    def test_validate_customer_type_data_invalid_name(self):
        """测试无效名称验证"""
        # 测试空名称
        with self.assertRaises(ValidationError):
            self.service._validate_customer_type_data({"name": ""})

        # 测试过长名称
        with self.assertRaises(ValidationError):
            self.service._validate_customer_type_data({"name": "x" * 51})

    def test_validate_customer_type_data_invalid_color(self):
        """测试无效颜色代码验证"""
        # 测试无效颜色格式
        with self.assertRaises(ValidationError):
            self.service._validate_customer_type_data(
                {"name": "测试", "color_code": "invalid"}
            )

    def test_validate_customer_type_data_invalid_sort_order(self):
        """测试无效排序值验证"""
        # 测试负数排序值
        with self.assertRaises(ValidationError):
            self.service._validate_customer_type_data(
                {"name": "测试", "sort_order": -1}
            )

        # 测试非数字排序值
        with self.assertRaises(ValidationError):
            self.service._validate_customer_type_data(
                {"name": "测试", "sort_order": "invalid"}
            )

    def test_check_type_name_exists(self):
        """测试检查类型名称是否存在"""
        # 模拟搜索结果
        self.mock_dao.search.return_value = [{"id": 1, "name": "存在的类型"}]

        # 测试名称存在
        result = self.service._check_type_name_exists("存在的类型")
        self.assertTrue(result)

        # 测试名称不存在
        self.mock_dao.search.return_value = []
        result = self.service._check_type_name_exists("不存在的类型")
        self.assertFalse(result)

        # 测试排除特定ID
        self.mock_dao.search.return_value = [{"id": 1, "name": "存在的类型"}]
        result = self.service._check_type_name_exists("存在的类型", exclude_id=1)
        self.assertFalse(result)

    def test_apply_customer_type_defaults(self):
        """测试应用默认值"""
        # 准备测试数据
        data = {"name": "测试类型"}

        # 执行默认值应用
        self.service._apply_customer_type_defaults(data)

        # 验证默认值
        self.assertEqual(data["description"], "")
        self.assertEqual(data["color_code"], "#007BFF")
        self.assertEqual(data["sort_order"], 0)
        self.assertTrue(data["is_active"])
        self.assertIn("created_at", data)

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 模拟DAO抛出异常
        self.mock_dao.insert.side_effect = Exception("数据库错误")
        self.service._check_type_name_exists = MagicMock(return_value=False)

        # 执行测试并验证ServiceError被抛出
        with self.assertRaises(ServiceError) as context:
            self.service.create_customer_type({"name": "测试类型"})

        self.assertIn("创建客户类型失败", str(context.exception))

    def test_get_service_name(self):
        """测试获取服务名称"""
        self.assertEqual(self.service.get_service_name(), "CustomerTypeService")


if __name__ == "__main__":
    unittest.main()
