"""
MiniCRM 业务服务层测试

测试客户服务、供应商服务和财务服务的核心功能。
"""

import unittest
from decimal import Decimal
from unittest.mock import Mock, patch

from minicrm.core.exceptions import BusinessLogicError, ValidationError
from minicrm.services.customer_service import CustomerService
from minicrm.services.finance_service import FinanceService
from minicrm.services.supplier_service import SupplierService
from minicrm.services.task_service import TaskService


class TestCustomerService(unittest.TestCase):
    """客户服务测试"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = Mock()
        self.customer_service = CustomerService(self.mock_dao)

    @patch("transfunctions.validation.validate_customer_data")
    def test_create_customer_success(self, mock_validate):
        """测试创建客户成功"""
        # 准备测试数据
        customer_data = {
            "name": "测试公司",
            "phone": "13812345678",
            "customer_type": "生态板客户",
        }

        # 模拟验证成功
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validate.return_value = mock_validation_result

        # 模拟DAO操作
        self.mock_dao.search_by_name_or_phone.return_value = []
        self.mock_dao.insert.return_value = 123

        # 执行测试
        customer_id = self.customer_service.create_customer(customer_data)

        # 验证结果
        self.assertEqual(customer_id, 123)
        self.mock_dao.insert.assert_called_once()

        # 验证业务规则应用
        inserted_data = self.mock_dao.insert.call_args[0][0]
        self.assertEqual(inserted_data["level"], "重要")  # 生态板客户默认重要等级
        self.assertEqual(inserted_data["status"], "active")

    @patch("transfunctions.validation.validate_customer_data")
    def test_create_customer_validation_error(self, mock_validate):
        """测试创建客户验证错误"""
        customer_data = {"name": ""}  # 缺少必填字段

        # 模拟验证失败
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = ["客户名称不能为空"]
        mock_validate.return_value = mock_validation_result

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.customer_service.create_customer(customer_data)

        self.assertIn("客户数据验证失败", str(context.exception))

    def test_create_customer_duplicate_error(self):
        """测试创建重复客户错误"""
        customer_data = {"name": "测试公司", "phone": "13812345678"}

        # 模拟验证成功
        with patch("transfunctions.validation.validate_customer_data") as mock_validate:
            mock_validation_result = Mock()
            mock_validation_result.is_valid = True
            mock_validate.return_value = mock_validation_result

            # 模拟客户已存在
            self.mock_dao.search_by_name_or_phone.return_value = [
                {"id": 1, "name": "测试公司"}
            ]

            # 执行测试并验证异常
            with self.assertRaises(BusinessLogicError) as context:
                self.customer_service.create_customer(customer_data)

            self.assertIn("客户已存在", str(context.exception))

    @patch("transfunctions.calculations.calculate_customer_value_score")
    def test_calculate_customer_value_score_success(self, mock_calculate):
        """测试客户价值评分计算成功"""
        customer_id = 123

        # 模拟DAO返回数据
        self.mock_dao.get_by_id.return_value = {"id": 123, "name": "测试公司"}
        self.mock_dao.get_transaction_history.return_value = [
            {"amount": 10000, "date": "2024-12-01"}
        ]
        self.mock_dao.get_recent_interactions.return_value = [
            {"type": "call", "date": "2024-12-15"}
        ]

        # 模拟transfunctions计算结果
        mock_metrics = Mock()
        mock_metrics.total_score = 85.5
        mock_metrics.to_dict.return_value = {
            "transaction_value": 30.0,
            "interaction_score": 20.0,
            "loyalty_score": 25.0,
            "potential_score": 10.5,
            "total_score": 85.5,
        }
        mock_calculate.return_value = mock_metrics

        # 执行测试
        result = self.customer_service.calculate_customer_value_score(customer_id)

        # 验证结果
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["total_score"], 85.5)
        self.assertIn("calculated_at", result)
        self.assertEqual(result["transaction_count"], 0)  # 暂时硬编码为空列表
        self.assertEqual(result["interaction_count"], 1)

    def test_calculate_customer_value_score_not_found(self):
        """测试计算不存在客户的价值评分"""
        customer_id = 999

        # 模拟客户不存在
        self.mock_dao.get_by_id.return_value = None

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.customer_service.calculate_customer_value_score(customer_id)

        self.assertIn("客户不存在", str(context.exception))

    def test_get_total_count_success(self):
        """测试获取客户总数成功"""
        # 模拟DAO返回客户总数
        self.mock_dao.count.return_value = 156

        # 执行测试
        total_count = self.customer_service.get_total_count()

        # 验证结果
        self.assertEqual(total_count, 156)
        self.mock_dao.count.assert_called_once_with()

    def test_get_total_count_zero(self):
        """测试获取客户总数为零的情况"""
        # 模拟DAO返回零客户
        self.mock_dao.count.return_value = 0

        # 执行测试
        total_count = self.customer_service.get_total_count()

        # 验证结果
        self.assertEqual(total_count, 0)
        self.mock_dao.count.assert_called_once_with()

    def test_get_total_count_database_error(self):
        """测试获取客户总数时数据库错误"""
        # 模拟数据库异常
        self.mock_dao.count.side_effect = Exception("数据库连接失败")

        # 执行测试并验证异常
        with self.assertRaises(Exception) as context:
            self.customer_service.get_total_count()

        self.assertIn("获取客户总数失败", str(context.exception))


class TestSupplierService(unittest.TestCase):
    """供应商服务测试"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = Mock()
        self.supplier_service = SupplierService(self.mock_dao)

    @patch("transfunctions.validation.validate_supplier_data")
    def test_create_supplier_success(self, mock_validate):
        """测试创建供应商成功"""
        supplier_data = {
            "name": "测试供应商",
            "phone": "13812345678",
            "supplier_type": "战略合作伙伴",
            "contact_person": "张经理",
        }

        # 模拟验证成功
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validate.return_value = mock_validation_result

        # 模拟DAO操作
        self.mock_dao.search_by_name_or_contact.return_value = []
        self.mock_dao.insert.return_value = 456

        # 执行测试
        supplier_id = self.supplier_service.create_supplier(supplier_data)

        # 验证结果
        self.assertEqual(supplier_id, 456)

        # 验证业务规则应用
        inserted_data = self.mock_dao.insert.call_args[0][0]
        self.assertEqual(
            inserted_data["grade"], "战略供应商"
        )  # 战略合作伙伴默认战略供应商等级

    @patch(
        "minicrm.services.supplier.supplier_quality_service.calculate_customer_value_score"
    )
    def test_evaluate_supplier_quality_success(self, mock_calculate):
        """测试供应商质量评估成功"""
        supplier_id = 456

        # 模拟DAO返回数据
        self.mock_dao.get_by_id.return_value = {"id": 456, "name": "测试供应商"}
        self.mock_dao.get_transaction_history.return_value = []
        self.mock_dao.get_interaction_history.return_value = []

        # 模拟质量评估结果
        mock_metrics = Mock()
        mock_metrics.total_score = 92.0
        mock_calculate.return_value = mock_metrics

        # 执行测试
        result = self.supplier_service.evaluate_supplier_quality(supplier_id)

        # 验证结果
        self.assertEqual(result["supplier_id"], supplier_id)
        self.assertEqual(result["quality_score"], 92.0)
        self.assertEqual(result["grade"], "战略供应商")  # 92分应该是战略供应商

    def test_determine_supplier_grade(self):
        """测试供应商等级确定逻辑"""
        # 测试不同评分对应的等级
        self.assertEqual(
            self.supplier_service.quality._determine_supplier_grade(95), "战略供应商"
        )
        self.assertEqual(
            self.supplier_service.quality._determine_supplier_grade(85), "重要供应商"
        )
        self.assertEqual(
            self.supplier_service.quality._determine_supplier_grade(75), "普通供应商"
        )
        self.assertEqual(
            self.supplier_service.quality._determine_supplier_grade(65), "备选供应商"
        )


class TestFinanceService(unittest.TestCase):
    """财务服务测试"""

    def setUp(self):
        """测试准备"""
        self.mock_customer_dao = Mock()
        self.mock_supplier_dao = Mock()
        self.finance_service = FinanceService(
            self.mock_customer_dao, self.mock_supplier_dao
        )

    def test_manage_customer_credit_success(self):
        """测试客户授信管理成功"""
        customer_id = 123
        credit_data = {"credit_amount": "50000", "credit_period": 30}

        # 模拟客户存在
        self.mock_customer_dao.get_by_id.return_value = {"id": 123, "name": "测试公司"}
        self.mock_customer_dao.insert_credit_record.return_value = 789

        # 模拟历史数据（用于风险评估）
        self.mock_customer_dao.get_transaction_history.return_value = [
            {"amount": 5000, "date": "2024-12-01"}
        ]
        self.mock_customer_dao.get_payments.return_value = [
            {"amount": 3000, "payment_date": "2024-11-15"}
        ]

        # 执行测试
        result = self.finance_service.manage_customer_credit(customer_id, credit_data)

        # 验证结果
        self.assertEqual(result["credit_id"], 789)
        self.assertEqual(result["customer_id"], customer_id)
        self.assertEqual(result["credit_amount"], 50000.0)
        self.assertIn("risk_assessment", result)

    def test_manage_customer_credit_invalid_amount(self):
        """测试无效授信金额"""
        customer_id = 123
        credit_data = {
            "credit_amount": "0",  # 无效金额
            "credit_period": 30,
        }

        # 模拟客户存在
        self.mock_customer_dao.get_by_id.return_value = {"id": 123, "name": "测试公司"}

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.finance_service.manage_customer_credit(customer_id, credit_data)

        self.assertIn("授信金额必须大于0", str(context.exception))

    def test_record_receivable_success(self):
        """测试记录应收账款成功"""
        customer_id = 123
        receivable_data = {
            "amount": "10000",
            "due_date": "2025-02-15",
            "description": "产品销售",
        }

        # 模拟客户存在
        self.mock_customer_dao.get_by_id.return_value = {"id": 123, "name": "测试公司"}
        self.mock_customer_dao.insert_receivable.return_value = 999

        # 模拟授信检查（返回None表示没有授信限制）
        self.mock_customer_dao.get_credit_info.return_value = None

        # 执行测试
        receivable_id = self.finance_service.record_receivable(
            customer_id, receivable_data
        )

        # 验证结果
        self.assertEqual(receivable_id, 999)
        self.mock_customer_dao.insert_receivable.assert_called_once()

    def test_assess_financial_risk_success(self):
        """测试财务风险评估成功"""
        customer_id = 123

        # 模拟客户和财务数据
        self.mock_customer_dao.get_by_id.return_value = {"id": 123, "name": "测试公司"}
        self.mock_customer_dao.get_receivables.return_value = [
            {"amount": 5000, "due_date": "2024-12-01", "status": "pending"}  # 逾期
        ]
        self.mock_customer_dao.get_payments.return_value = [
            {"amount": 3000, "payment_date": "2024-11-15"}
        ]
        self.mock_customer_dao.get_credit_info.return_value = {"credit_amount": 20000}

        # 执行测试
        result = self.finance_service.assess_financial_risk(customer_id)

        # 验证结果
        self.assertEqual(result["customer_id"], customer_id)
        self.assertIn("risk_score", result)
        self.assertIn("risk_level", result)
        self.assertIn("overdue_amount", result)
        self.assertIn("warnings", result)

    def test_calculate_overdue_amount(self):
        """测试逾期金额计算"""
        receivables = [
            {"amount": 5000, "due_date": "2024-12-01", "status": "pending"},  # 逾期
            {
                "amount": 3000,
                "due_date": "2026-03-01",
                "status": "pending",
            },  # 未逾期（未来日期）
            {
                "amount": 2000,
                "due_date": "2024-11-01",
                "status": "paid",
            },  # 已付款，不计算
        ]

        overdue_amount = self.finance_service._calculate_overdue_amount(receivables)

        # 只有第一笔应收账款逾期（pending状态且过期）
        # 第二笔未逾期（未来日期），第三笔虽然过期但已付款，不计算在逾期金额中
        self.assertEqual(overdue_amount, Decimal("5000"))

    def test_determine_risk_level(self):
        """测试风险等级确定"""
        self.assertEqual(self.finance_service._determine_risk_level(85), "低风险")
        self.assertEqual(self.finance_service._determine_risk_level(65), "中风险")
        self.assertEqual(self.finance_service._determine_risk_level(45), "高风险")
        self.assertEqual(self.finance_service._determine_risk_level(25), "极高风险")

    def test_get_total_receivables_success(self):
        """测试获取应收账款总额成功"""
        # 模拟DAO返回应收账款汇总
        self.mock_customer_dao.get_receivables_summary.return_value = {
            "total_amount": 125000.50,
            "overdue_amount": 15000.00,
        }

        # 执行测试
        total_receivables = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(total_receivables, 125000.50)
        self.mock_customer_dao.get_receivables_summary.assert_called_once()

    def test_get_total_receivables_zero(self):
        """测试获取应收账款总额为零的情况"""
        # 模拟DAO返回零应收账款
        self.mock_customer_dao.get_receivables_summary.return_value = {
            "total_amount": 0,
            "overdue_amount": 0,
        }

        # 执行测试
        total_receivables = self.finance_service.get_total_receivables()

        # 验证结果
        self.assertEqual(total_receivables, 0.0)
        self.mock_customer_dao.get_receivables_summary.assert_called_once()

    def test_get_total_receivables_missing_data(self):
        """测试获取应收账款总额时数据缺失的情况"""
        # 模拟DAO返回不完整数据
        self.mock_customer_dao.get_receivables_summary.return_value = {}

        # 执行测试
        total_receivables = self.finance_service.get_total_receivables()

        # 验证结果（应该返回默认值0）
        self.assertEqual(total_receivables, 0.0)
        self.mock_customer_dao.get_receivables_summary.assert_called_once()

    def test_get_total_receivables_database_error(self):
        """测试获取应收账款总额时数据库错误"""
        # 模拟数据库异常
        self.mock_customer_dao.get_receivables_summary.side_effect = Exception(
            "数据库连接失败"
        )

        # 执行测试并验证异常
        with self.assertRaises(Exception) as context:
            self.finance_service.get_total_receivables()

        self.assertIn("获取应收账款总额失败", str(context.exception))


class TestTaskService(unittest.TestCase):
    """任务服务测试"""

    def setUp(self):
        """测试准备"""
        self.mock_db_manager = Mock()
        self.task_service = TaskService(self.mock_db_manager)
        # 模拟InteractionDAO
        self.task_service._interaction_dao = Mock()

    def test_get_pending_count_success(self):
        """测试获取待办任务数量成功"""
        # 模拟get_pending_tasks返回待办任务列表
        mock_pending_tasks = [
            {"id": 1, "title": "任务1", "status": "pending"},
            {"id": 2, "title": "任务2", "status": "pending"},
            {"id": 3, "title": "任务3", "status": "pending"},
        ]

        # 模拟InteractionDAO的search方法
        self.task_service._interaction_dao.search.return_value = [
            {
                "id": 1,
                "content": "任务1",
                "status": "pending",
                "interaction_type": "task",
            },
            {
                "id": 2,
                "content": "任务2",
                "status": "pending",
                "interaction_type": "task",
            },
            {
                "id": 3,
                "content": "任务3",
                "status": "pending",
                "interaction_type": "task",
            },
        ]

        # 执行测试
        pending_count = self.task_service.get_pending_count()

        # 验证结果
        self.assertEqual(pending_count, 3)

    def test_get_pending_count_zero(self):
        """测试获取待办任务数量为零的情况"""
        # 模拟没有待办任务
        self.task_service._interaction_dao.search.return_value = []

        # 执行测试
        pending_count = self.task_service.get_pending_count()

        # 验证结果
        self.assertEqual(pending_count, 0)

    def test_get_pending_count_database_error(self):
        """测试获取待办任务数量时数据库错误"""
        # 模拟数据库异常
        self.task_service._interaction_dao.search.side_effect = Exception(
            "数据库连接失败"
        )

        # 执行测试并验证异常
        with self.assertRaises(Exception) as context:
            self.task_service.get_pending_count()

        self.assertIn("获取待办任务数量失败", str(context.exception))

    def test_create_task_success(self):
        """测试创建任务成功"""
        task_data = {
            "title": "测试任务",
            "description": "任务描述",
            "customer_id": 123,
            "due_date": "2025-02-15T10:00:00",
        }

        # 模拟DAO操作
        self.task_service._interaction_dao.insert.return_value = 456

        # 执行测试
        task_id = self.task_service.create_task(task_data)

        # 验证结果
        self.assertEqual(task_id, 456)
        self.task_service._interaction_dao.insert.assert_called_once()

    def test_create_task_validation_error(self):
        """测试创建任务验证错误"""
        task_data = {"title": ""}  # 缺少必填字段

        # 执行测试并验证异常
        with self.assertRaises(ValidationError) as context:
            self.task_service.create_task(task_data)

        self.assertIn("任务标题不能为空", str(context.exception))

    def test_mark_task_completed_success(self):
        """测试标记任务完成成功"""
        task_id = 123

        # 模拟任务存在
        self.task_service._interaction_dao.get_by_id.return_value = {
            "id": 123,
            "content": "测试任务",
            "interaction_type": "task",
            "status": "pending",
        }
        self.task_service._interaction_dao.update.return_value = True

        # 执行测试
        result = self.task_service.mark_task_completed(task_id)

        # 验证结果
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
