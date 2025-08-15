"""
供应商服务单元测试

测试供应商管理服务的所有核心功能：
- 基础CRUD操作
- 质量评估算法
- 分级管理算法
- 互动和任务管理
- 交流事件处理

严格遵循测试最佳实践：
- 使用Mock对象隔离依赖
- 测试覆盖所有业务场景
- 验证异常处理逻辑
- 确保测试的独立性和可重复性
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from minicrm.core.exceptions import BusinessLogicError, ServiceError
from minicrm.services.supplier_service import (
    EventPriority,
    SupplierService,
)
from transfunctions import CustomerValueMetrics, ValidationResult
from transfunctions.validation.business import ValidationError


class TestSupplierService(unittest.TestCase):
    """供应商服务测试类"""

    def setUp(self):
        """测试准备"""
        # 创建Mock DAO对象
        self.mock_dao = Mock()

        # 创建供应商服务实例
        self.supplier_service = SupplierService(self.mock_dao)

        # 准备测试数据
        self.valid_supplier_data = {
            "name": "测试供应商",
            "contact_person": "张经理",
            "phone": "13812345678",
            "email": "test@supplier.com",
            "company_name": "测试供应商有限公司",
            "supplier_type": "manufacturer",
            "business_license": "123456789012345",
        }

        self.supplier_record = {
            "id": 1,
            "name": "测试供应商",
            "contact_person": "张经理",
            "phone": "13812345678",
            "email": "test@supplier.com",
            "created_at": datetime.now().isoformat(),
        }

    def tearDown(self):
        """测试清理"""
        pass

    # ==================== 基础CRUD操作测试 ====================

    @patch("minicrm.services.supplier_service.validate_supplier_data")
    def test_create_supplier_success(self, mock_validate):
        """测试创建供应商成功"""
        # 准备Mock返回值
        mock_validate.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[]
        )
        self.mock_dao.get_by_id.return_value = None  # 供应商不存在
        self.mock_dao.search_by_name_or_contact.return_value = []  # 无重复
        self.mock_dao.insert.return_value = 1

        # 执行测试
        result = self.supplier_service.create_supplier(self.valid_supplier_data)

        # 验证结果
        self.assertEqual(result, 1)
        mock_validate.assert_called_once()
        self.mock_dao.insert.assert_called_once()

    @patch("minicrm.services.supplier_service.validate_supplier_data")
    def test_create_supplier_validation_error(self, mock_validate):
        """测试创建供应商数据验证失败"""
        # 准备Mock返回值
        mock_validate.return_value = ValidationResult(
            is_valid=False, errors=["供应商名称不能为空"], warnings=[]
        )

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.supplier_service.create_supplier({"name": ""})

        self.assertIn("供应商数据验证失败", str(context.exception))

    @patch("minicrm.services.supplier_service.validate_supplier_data")
    def test_create_supplier_duplicate_error(self, mock_validate):
        """测试创建重复供应商"""
        # 准备Mock返回值
        mock_validate.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[]
        )
        self.mock_dao.search_by_name_or_contact.return_value = [self.supplier_record]

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.create_supplier(self.valid_supplier_data)

        self.assertIn("供应商已存在", str(context.exception))

    @patch("minicrm.services.supplier_service.validate_supplier_data")
    def test_update_supplier_success(self, mock_validate):
        """测试更新供应商成功"""
        # 准备Mock返回值
        mock_validate.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[]
        )
        self.mock_dao.get_by_id.return_value = self.supplier_record
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.supplier_service.update_supplier(1, {"name": "更新后的名称"})

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    @patch("minicrm.services.supplier_service.validate_supplier_data")
    def test_update_supplier_not_found(self, mock_validate):
        """测试更新不存在的供应商"""
        # 准备Mock返回值
        mock_validate.return_value = ValidationResult(
            is_valid=True, errors=[], warnings=[]
        )
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.update_supplier(999, {"name": "测试"})

        self.assertIn("供应商不存在", str(context.exception))

    def test_delete_supplier_success(self):
        """测试删除供应商成功"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record
        self.mock_dao.delete.return_value = True

        # 执行测试
        result = self.supplier_service.delete_supplier(1)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.delete.assert_called_once_with(1)

    def test_delete_supplier_not_found(self):
        """测试删除不存在的供应商"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.delete_supplier(999)

        self.assertIn("供应商不存在", str(context.exception))

    # ==================== 质量评估算法测试 ====================

    @patch("minicrm.services.supplier_service.calculate_customer_value_score")
    def test_evaluate_supplier_quality_success(self, mock_calculate):
        """测试供应商质量评估成功"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record
        self.mock_dao.get_transaction_history.return_value = [
            {"amount": 10000, "date": "2024-01-01"}
        ]
        self.mock_dao.get_interaction_history.return_value = [
            {"type": "meeting", "date": "2024-01-01"}
        ]

        mock_metrics = CustomerValueMetrics(
            total_score=85.5,
            transaction_value=80.0,
            interaction_score=90.0,
            loyalty_score=85.0,
            potential_score=88.0,
        )
        mock_calculate.return_value = mock_metrics

        # 执行测试
        result = self.supplier_service.evaluate_supplier_quality(1)

        # 验证结果
        self.assertEqual(result["supplier_id"], 1)
        self.assertEqual(result["quality_score"], 85.5)
        self.assertEqual(result["grade"], "重要供应商")
        self.assertIn("evaluated_at", result)

    def test_evaluate_supplier_quality_not_found(self):
        """测试评估不存在的供应商"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.evaluate_supplier_quality(999)

        self.assertIn("供应商不存在", str(context.exception))

    def test_determine_supplier_grade(self):
        """测试供应商等级确定逻辑"""
        # 测试各个等级阈值
        test_cases = [
            (95.0, "战略供应商"),
            (85.0, "重要供应商"),
            (75.0, "普通供应商"),
            (65.0, "备选供应商"),
            (50.0, "备选供应商"),
        ]

        for score, expected_grade in test_cases:
            with self.subTest(score=score):
                result = self.supplier_service._determine_supplier_grade(score)
                self.assertEqual(result, expected_grade)

    # ==================== 互动管理测试 ====================

    def test_manage_supplier_interaction_success(self):
        """测试管理供应商互动成功"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record
        self.mock_dao.insert_interaction.return_value = 1

        interaction_data = {
            "interaction_type": "meeting",
            "content": "讨论新产品合作",
            "created_by": "user1",
        }

        # 执行测试
        result = self.supplier_service.manage_supplier_interaction(1, interaction_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.mock_dao.insert_interaction.assert_called_once()

    def test_manage_supplier_interaction_not_found(self):
        """测试管理不存在供应商的互动"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.manage_supplier_interaction(999, {})

        self.assertIn("供应商不存在", str(context.exception))

    # ==================== 交流事件处理测试 ====================

    def test_create_communication_event_success(self):
        """测试创建交流事件成功"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record
        self.mock_dao.get_daily_event_count.return_value = 0
        self.mock_dao.insert_communication_event.return_value = 1

        event_data = {
            "event_type": "inquiry",
            "title": "产品询价",
            "content": "询问新产品价格",
            "urgency_level": "medium",
            "created_by": "user1",
        }

        # 执行测试
        result = self.supplier_service.create_communication_event(1, event_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.mock_dao.insert_communication_event.assert_called_once()

    def test_create_communication_event_validation_error(self):
        """测试创建交流事件数据验证失败"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record

        # 测试缺少必填字段
        with self.assertRaises(ValidationError) as context:
            self.supplier_service.create_communication_event(1, {})

        self.assertIn("事件event_type不能为空", str(context.exception))

    def test_create_communication_event_invalid_type(self):
        """测试创建交流事件类型无效"""
        # 准备Mock返回值
        self.mock_dao.get_by_id.return_value = self.supplier_record

        event_data = {"event_type": "invalid_type", "content": "测试内容"}

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.supplier_service.create_communication_event(1, event_data)

        self.assertIn("无效的事件类型", str(context.exception))

    def test_update_event_status_success(self):
        """测试更新事件状态成功"""
        # 准备Mock返回值
        event_record = {
            "id": 1,
            "supplier_id": 1,
            "status": "pending",
            "event_type": "inquiry",
        }
        self.mock_dao.get_communication_event.return_value = event_record
        self.mock_dao.update_communication_event.return_value = True

        # 执行测试
        result = self.supplier_service.update_event_status(
            1, "in_progress", "开始处理", "user1"
        )

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update_communication_event.assert_called_once()

    def test_update_event_status_invalid_status(self):
        """测试更新事件状态为无效值"""
        # 准备Mock返回值
        event_record = {"id": 1, "status": "pending"}
        self.mock_dao.get_communication_event.return_value = event_record

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.supplier_service.update_event_status(1, "invalid_status")

        self.assertIn("无效的事件状态", str(context.exception))

    def test_process_event_success(self):
        """测试处理交流事件成功"""
        # 准备Mock返回值
        event_record = {
            "id": 1,
            "supplier_id": 1,
            "status": "in_progress",
            "title": "产品询价",
        }
        self.mock_dao.get_communication_event.return_value = event_record
        self.mock_dao.update_communication_event.return_value = True
        self.mock_dao.insert_event_processing_result.return_value = 1

        processing_data = {
            "solution": "提供详细报价单",
            "result": "客户满意",
            "satisfaction_rating": 5,
            "processed_by": "user1",
        }

        # 执行测试
        result = self.supplier_service.process_event(1, processing_data)

        # 验证结果
        self.assertEqual(result["event_id"], 1)
        self.assertEqual(result["solution"], "提供详细报价单")
        self.mock_dao.insert_event_processing_result.assert_called_once()

    def test_process_event_already_completed(self):
        """测试处理已完成的事件"""
        # 准备Mock返回值
        event_record = {"id": 1, "status": "completed"}
        self.mock_dao.get_communication_event.return_value = event_record

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.supplier_service.process_event(1, {})

        self.assertIn("事件已完成或关闭", str(context.exception))

    def test_get_event_statistics_success(self):
        """测试获取事件统计成功"""
        # 准备Mock返回值
        mock_events = [
            {
                "id": 1,
                "event_type": "inquiry",
                "status": "completed",
                "priority": "medium",
                "created_at": datetime.now().isoformat(),
                "completed_at": (datetime.now() + timedelta(hours=2)).isoformat(),
                "satisfaction_rating": 4,
            },
            {
                "id": 2,
                "event_type": "complaint",
                "status": "pending",
                "priority": "high",
                "created_at": datetime.now().isoformat(),
                "due_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            },
        ]
        self.mock_dao.get_communication_events.return_value = mock_events

        # 执行测试
        result = self.supplier_service.get_event_statistics(supplier_id=1)

        # 验证结果
        self.assertEqual(result["total_events"], 2)
        self.assertEqual(result["by_type"]["inquiry"], 1)
        self.assertEqual(result["by_type"]["complaint"], 1)
        self.assertEqual(result["by_status"]["completed"], 1)
        self.assertEqual(result["by_status"]["pending"], 1)
        self.assertEqual(result["overdue_events"], 1)

    def test_get_overdue_events_success(self):
        """测试获取超时事件成功"""
        # 准备Mock返回值
        overdue_time = datetime.now() - timedelta(hours=2)
        mock_events = [
            {
                "id": 1,
                "status": "pending",
                "due_time": overdue_time.isoformat(),
                "priority": "high",
            }
        ]
        self.mock_dao.get_communication_events.return_value = mock_events

        # 执行测试
        result = self.supplier_service.get_overdue_events()

        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertGreater(result[0]["overdue_hours"], 0)

    # ==================== 搜索功能测试 ====================

    def test_search_suppliers_by_query(self):
        """测试按关键词搜索供应商"""
        # 准备Mock返回值
        self.mock_dao.search_by_name_or_contact.return_value = [self.supplier_record]
        self.mock_dao.count.return_value = 1

        # 执行测试
        suppliers, total = self.supplier_service.search_suppliers(query="测试")

        # 验证结果
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(total, 1)
        self.mock_dao.search_by_name_or_contact.assert_called_once_with("测试")

    def test_search_suppliers_with_filters(self):
        """测试按筛选条件搜索供应商"""
        # 准备Mock返回值
        self.mock_dao.search.return_value = [self.supplier_record]
        self.mock_dao.count.return_value = 1

        filters = {"status": "active", "level": "important"}

        # 执行测试
        suppliers, total = self.supplier_service.search_suppliers(
            filters=filters, page=1, page_size=10
        )

        # 验证结果
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(total, 1)
        self.mock_dao.search.assert_called_once()

    # ==================== 私有方法测试 ====================

    def test_determine_event_priority(self):
        """测试事件优先级确定逻辑"""
        # 测试质量问题的优先级
        quality_issue_data = {"event_type": "quality_issue", "urgency_level": "urgent"}
        priority = self.supplier_service._determine_event_priority(quality_issue_data)
        self.assertEqual(priority, EventPriority.URGENT)

        # 测试投诉的优先级
        complaint_data = {"event_type": "complaint", "urgency_level": "high"}
        priority = self.supplier_service._determine_event_priority(complaint_data)
        self.assertEqual(priority, EventPriority.HIGH)

        # 测试一般事件的优先级
        general_data = {"event_type": "inquiry", "urgency_level": "medium"}
        priority = self.supplier_service._determine_event_priority(general_data)
        self.assertEqual(priority, EventPriority.MEDIUM)

    def test_calculate_event_due_time(self):
        """测试事件截止时间计算"""
        # 测试紧急事件的截止时间
        due_time = self.supplier_service._calculate_event_due_time(EventPriority.URGENT)
        expected_time = datetime.now() + timedelta(hours=2)

        # 允许1分钟的误差
        time_diff = abs((due_time - expected_time).total_seconds())
        self.assertLess(time_diff, 60)

    def test_generate_event_number(self):
        """测试事件编号生成"""
        # 准备Mock返回值
        self.mock_dao.get_daily_event_count.return_value = 0

        # 执行测试
        event_number = self.supplier_service._generate_event_number(1)

        # 验证结果格式
        self.assertTrue(event_number.startswith("SE0001"))
        self.assertEqual(len(event_number), 17)  # SE + 4位供应商ID + 8位日期 + 3位序号

    def test_validate_event_data(self):
        """测试事件数据验证"""
        # 测试有效数据
        valid_data = {
            "event_type": "inquiry",
            "content": "测试内容",
            "urgency_level": "medium",
        }
        # 不应该抛出异常
        self.supplier_service._validate_event_data(valid_data)

        # 测试缺少必填字段
        invalid_data = {"event_type": "inquiry"}  # 缺少content
        with self.assertRaises(ValidationError):
            self.supplier_service._validate_event_data(invalid_data)

        # 测试无效事件类型
        invalid_type_data = {"event_type": "invalid", "content": "测试内容"}
        with self.assertRaises(ValidationError):
            self.supplier_service._validate_event_data(invalid_type_data)

    # ==================== 异常处理测试 ====================

    def test_service_error_handling(self):
        """测试服务异常处理"""
        # 模拟数据库异常
        self.mock_dao.get_by_id.side_effect = Exception("数据库连接失败")

        # 执行测试并验证异常
        with self.assertRaises(ServiceError) as context:
            self.supplier_service.evaluate_supplier_quality(1)

        self.assertIn("供应商质量评估失败", str(context.exception))

    def test_apply_supplier_defaults(self):
        """测试应用供应商默认值"""
        # 测试数据
        supplier_data = {"name": "测试供应商", "supplier_type": "原材料供应商"}

        # 执行测试
        self.supplier_service._apply_supplier_defaults(supplier_data)

        # 验证结果
        self.assertEqual(supplier_data["grade"], "重要供应商")
        self.assertEqual(supplier_data["status"], "active")
        self.assertIn("created_at", supplier_data)

        # 测试战略合作伙伴
        strategic_data = {"name": "战略供应商", "supplier_type": "战略合作伙伴"}
        self.supplier_service._apply_supplier_defaults(strategic_data)
        self.assertEqual(strategic_data["grade"], "战略供应商")


class TestSupplierServiceIntegration(unittest.TestCase):
    """供应商服务集成测试"""

    def setUp(self):
        """集成测试准备"""
        # 这里可以设置真实的数据库连接进行集成测试
        # 由于当前环境限制，暂时跳过集成测试
        self.skipTest("集成测试需要真实数据库环境")

    def test_full_supplier_lifecycle(self):
        """测试完整的供应商生命周期"""
        # 创建 -> 评估 -> 互动 -> 事件处理 -> 删除
        pass


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
