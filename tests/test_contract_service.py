"""
MiniCRM 合同服务单元测试

测试合同管理服务的所有功能，包括：
- 基础CRUD操作
- 合同生命周期管理
- 合同到期提醒和续约
- 合同模板管理
- 业务规则验证
- 异常处理

测试策略：
- 使用Mock对象模拟DAO层
- 测试各种业务场景和边界条件
- 验证异常处理和错误信息
- 确保业务规则的正确性
"""

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from src.minicrm.core.exceptions import (
    BusinessLogicError,
    ServiceError,
    ValidationError,
)
from src.minicrm.models.contract import Contract, ContractStatus, ContractType
from src.minicrm.models.contract_template import (
    ContractTemplate,
    TemplateStatus,
    TemplateType,
)
from src.minicrm.services.contract_service import (
    ContractService,
    ContractStatusError,
    ContractTemplateError,
)


class TestContractService(unittest.TestCase):
    """合同服务测试类"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = MagicMock()
        self.contract_service = ContractService(self.mock_dao)

        # 准备测试数据
        self.sample_contract_data = {
            "name": "测试合同",  # 添加name字段，因为Contract继承自NamedModel
            "contract_number": "C202501150001",
            "contract_type": ContractType.SALES,
            "customer_id": 1,
            "party_name": "测试客户公司",
            "contract_amount": Decimal("100000.00"),
            "currency": "CNY",
            "effective_date": datetime.now(),
            "expiry_date": datetime.now() + timedelta(days=365),
            "terms_and_conditions": "测试条款",
        }

        self.sample_template_data = {
            "name": "标准销售合同模板",  # 添加name字段
            "template_name": "标准销售合同模板",
            "contract_type": ContractType.SALES,
            "template_type": TemplateType.SYSTEM,
            "template_status": TemplateStatus.ACTIVE,
            "created_by": "系统管理员",
            "terms_template": "标准销售合同条款模板",
            "default_values": {"currency": "CNY", "payment_terms": 30},
            "required_fields": ["party_name", "contract_amount"],
        }

    def tearDown(self):
        """测试清理"""
        self.contract_service = None
        self.mock_dao = None

    # ==================== 基础CRUD操作测试 ====================

    def test_create_contract_success(self):
        """测试创建合同成功"""
        # 准备
        contract_data = self.sample_contract_data.copy()

        # 执行
        contract = self.contract_service.create(contract_data)

        # 验证
        self.assertIsInstance(contract, Contract)
        self.assertEqual(contract.contract_number, "C202501150001")
        self.assertEqual(contract.party_name, "测试客户公司")
        self.assertEqual(contract.contract_amount, Decimal("100000.00"))
        self.assertEqual(contract.contract_status, ContractStatus.DRAFT)

    def test_create_contract_validation_error(self):
        """测试创建合同数据验证错误"""
        # 准备 - 缺少必填字段
        invalid_data = {"contract_number": ""}

        # 执行和验证
        with self.assertRaises(ValidationError) as context:
            self.contract_service.create(invalid_data)

        self.assertIn("缺少必填字段", str(context.exception))

    def test_create_contract_invalid_amount(self):
        """测试创建合同金额无效"""
        # 准备
        contract_data = self.sample_contract_data.copy()
        contract_data["contract_amount"] = Decimal("-1000.00")

        # 执行和验证
        with self.assertRaises(ValidationError) as context:
            self.contract_service.create(contract_data)

        self.assertIn("合同金额不能为负数", str(context.exception))

    def test_create_sales_contract_without_customer(self):
        """测试创建销售合同但没有客户信息"""
        # 准备
        contract_data = self.sample_contract_data.copy()
        del contract_data["customer_id"]
        del contract_data["party_name"]

        # 执行和验证
        with self.assertRaises(ValidationError) as context:
            self.contract_service.create(contract_data)

        self.assertIn("销售合同必须关联客户", str(context.exception))

    def test_update_contract_success(self):
        """测试更新合同成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1

        with patch.object(self.contract_service, "get_by_id", return_value=contract):
            # 执行
            update_data = {"contract_amount": Decimal("120000.00")}
            updated_contract = self.contract_service.update(1, update_data)

            # 验证
            self.assertEqual(updated_contract.contract_amount, Decimal("120000.00"))

    def test_delete_contract_success(self):
        """测试删除合同成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.DRAFT

        with patch.object(self.contract_service, "get_by_id", return_value=contract):
            # 执行
            result = self.contract_service.delete(1)

            # 验证
            self.assertTrue(result)

    def test_delete_signed_contract_error(self):
        """测试删除已签署合同错误"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.SIGNED

        with patch.object(self.contract_service, "get_by_id", return_value=contract):
            # 执行和验证 - 根据实际的异常处理机制，期望ServiceError
            with self.assertRaises(ServiceError) as context:
                self.contract_service.delete(1)

            self.assertIn("已签署或执行中的合同不能删除", str(context.exception))

    # ==================== 合同生命周期管理测试 ====================

    def test_sign_contract_success(self):
        """测试签署合同成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.DRAFT

        with (
            patch.object(self.contract_service, "get_by_id", return_value=contract),
            patch.object(self.contract_service, "update") as mock_update,
        ):
            mock_update.return_value = contract

            # 执行
            sign_date = datetime.now()
            signed_contract = self.contract_service.sign_contract(
                1, sign_date, "张经理"
            )

            # 验证
            self.assertEqual(signed_contract.contract_status, ContractStatus.SIGNED)
            self.assertEqual(signed_contract.sign_date, sign_date)
            self.assertIn("张经理", signed_contract.notes)

    def test_update_contract_status_success(self):
        """测试更新合同状态成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.SIGNED

        with (
            patch.object(self.contract_service, "get_by_id", return_value=contract),
            patch.object(self.contract_service, "update") as mock_update,
        ):
            mock_update.return_value = contract

            # 执行
            updated_contract = self.contract_service.update_contract_status(
                1, ContractStatus.ACTIVE, "开始执行"
            )

            # 验证
            self.assertEqual(updated_contract.contract_status, ContractStatus.ACTIVE)
            self.assertIn("开始执行", updated_contract.notes)

    def test_update_contract_status_invalid_transition(self):
        """测试无效的合同状态转换"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.COMPLETED

        with patch.object(self.contract_service, "get_by_id", return_value=contract):
            # 执行和验证
            with self.assertRaises(ContractStatusError) as context:
                self.contract_service.update_contract_status(
                    1, ContractStatus.DRAFT, "回退到草稿"
                )

            self.assertIn("不能从completed转换到draft", str(context.exception))

    def test_terminate_contract_success(self):
        """测试终止合同成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.ACTIVE

        with (
            patch.object(self.contract_service, "get_by_id", return_value=contract),
            patch.object(self.contract_service, "update") as mock_update,
        ):
            mock_update.return_value = contract

            # 执行
            terminated_contract = self.contract_service.terminate_contract(
                1, "客户要求终止", datetime.now()
            )

            # 验证
            self.assertEqual(
                terminated_contract.contract_status, ContractStatus.TERMINATED
            )
            self.assertIn("客户要求终止", terminated_contract.notes)

    def test_update_contract_progress_success(self):
        """测试更新合同进度成功"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1
        contract.contract_status = ContractStatus.SIGNED

        with (
            patch.object(self.contract_service, "get_by_id", return_value=contract),
            patch.object(self.contract_service, "update") as mock_update,
        ):
            mock_update.return_value = contract

            # 执行
            updated_contract = self.contract_service.update_contract_progress(
                1, 50.0, Decimal("50000.00")
            )

            # 验证
            self.assertEqual(updated_contract.progress_percentage, 50.0)
            self.assertEqual(updated_contract.actual_amount, Decimal("50000.00"))
            self.assertEqual(updated_contract.contract_status, ContractStatus.ACTIVE)

    def test_update_contract_progress_invalid_percentage(self):
        """测试更新合同进度无效百分比"""
        # 准备
        contract = Contract.from_dict(self.sample_contract_data)
        contract.id = 1

        with patch.object(self.contract_service, "get_by_id", return_value=contract):
            # 执行和验证
            with self.assertRaises(ValidationError) as context:
                self.contract_service.update_contract_progress(1, 150.0)

            self.assertIn("执行进度必须在0-100之间", str(context.exception))

    # ==================== 合同到期提醒和续约测试 ====================

    def test_get_expiring_contracts(self):
        """测试获取即将到期的合同"""
        # 准备
        expiring_contract = Contract.from_dict(self.sample_contract_data)
        expiring_contract.expiry_date = datetime.now() + timedelta(days=15)
        expiring_contract.contract_status = ContractStatus.ACTIVE

        normal_contract = Contract.from_dict(self.sample_contract_data)
        normal_contract.expiry_date = datetime.now() + timedelta(days=60)
        normal_contract.contract_status = ContractStatus.ACTIVE

        with patch.object(
            self.contract_service,
            "list_all",
            return_value=[expiring_contract, normal_contract],
        ):
            # 执行
            expiring_contracts = self.contract_service.get_expiring_contracts(30)

            # 验证
            self.assertEqual(len(expiring_contracts), 1)
            self.assertEqual(expiring_contracts[0], expiring_contract)

    def test_get_expired_contracts(self):
        """测试获取已过期的合同"""
        # 准备
        expired_contract = Contract.from_dict(self.sample_contract_data)
        expired_contract.expiry_date = datetime.now() - timedelta(days=10)
        expired_contract.contract_status = ContractStatus.ACTIVE

        active_contract = Contract.from_dict(self.sample_contract_data)
        active_contract.expiry_date = datetime.now() + timedelta(days=30)
        active_contract.contract_status = ContractStatus.ACTIVE

        with patch.object(
            self.contract_service,
            "list_all",
            return_value=[expired_contract, active_contract],
        ):
            # 执行
            expired_contracts = self.contract_service.get_expired_contracts()

            # 验证
            self.assertEqual(len(expired_contracts), 1)
            self.assertEqual(expired_contracts[0], expired_contract)

    def test_process_expired_contracts(self):
        """测试处理已过期的合同"""
        # 准备
        expired_contract = Contract.from_dict(self.sample_contract_data)
        expired_contract.id = 1
        expired_contract.expiry_date = datetime.now() - timedelta(days=10)

        with (
            patch.object(
                self.contract_service,
                "get_expired_contracts",
                return_value=[expired_contract],
            ),
            patch.object(
                self.contract_service, "update_contract_status"
            ) as mock_update,
        ):
            # 执行
            result = self.contract_service.process_expired_contracts()

            # 验证
            self.assertEqual(result["processed"], 1)
            self.assertEqual(result["errors"], 0)
            mock_update.assert_called_once_with(1, ContractStatus.EXPIRED, "合同已过期")

    def test_create_renewal_contract_success(self):
        """测试创建续约合同成功"""
        # 准备
        original_contract = Contract.from_dict(self.sample_contract_data)
        original_contract.id = 1
        original_contract.contract_status = ContractStatus.ACTIVE

        renewal_data = {
            "expiry_date": datetime.now() + timedelta(days=365),
            "contract_amount": Decimal("110000.00"),
        }

        with (
            patch.object(
                self.contract_service, "get_by_id", return_value=original_contract
            ),
            patch.object(self.contract_service, "create_contract") as mock_create,
            patch.object(self.contract_service, "update") as mock_update,
        ):
            renewal_contract = Contract.from_dict(self.sample_contract_data)
            renewal_contract.id = 2
            mock_create.return_value = renewal_contract

            # 执行
            result = self.contract_service.create_renewal_contract(1, renewal_data)

            # 验证
            self.assertEqual(result, renewal_contract)
            mock_create.assert_called_once()
            mock_update.assert_called_once()

    def test_create_renewal_contract_inactive_original(self):
        """测试续约非活跃合同错误"""
        # 准备
        original_contract = Contract.from_dict(self.sample_contract_data)
        original_contract.id = 1
        original_contract.contract_status = ContractStatus.DRAFT

        with patch.object(
            self.contract_service, "get_by_id", return_value=original_contract
        ):
            # 执行和验证
            with self.assertRaises(BusinessLogicError) as context:
                self.contract_service.create_renewal_contract(1, {})

            self.assertIn("只有活跃状态的合同才能续约", str(context.exception))

    # ==================== 合同模板管理测试 ====================

    def test_create_template_success(self):
        """测试创建合同模板成功"""
        # 准备
        template_data = self.sample_template_data.copy()

        # 执行
        template = self.contract_service.create_template(template_data)

        # 验证
        self.assertIsInstance(template, ContractTemplate)
        self.assertEqual(template.template_name, "标准销售合同模板")
        self.assertEqual(template.contract_type, ContractType.SALES)
        self.assertEqual(template.template_status, TemplateStatus.ACTIVE)

    def test_create_template_validation_error(self):
        """测试创建模板数据验证错误"""
        # 准备 - 缺少必填字段
        invalid_data = {"template_name": ""}

        # 执行和验证
        with self.assertRaises(ValidationError) as context:
            self.contract_service.create_template(invalid_data)

        self.assertIn("缺少必填字段", str(context.exception))

    def test_create_from_template_success(self):
        """测试基于模板创建合同成功"""
        # 准备
        template = ContractTemplate.from_dict(self.sample_template_data)
        template.id = 1

        contract_data = {
            "name": "模板测试合同",
            "contract_number": "C202501150002",
            "party_name": "模板测试客户",
            "contract_amount": Decimal("80000.00"),
        }

        with (
            patch.object(
                self.contract_service, "get_template_by_id", return_value=template
            ),
            patch.object(self.contract_service, "create_contract") as mock_create,
        ):
            expected_contract = Contract.from_dict(contract_data)
            mock_create.return_value = expected_contract

            # 执行
            contract = self.contract_service.create_from_template(1, contract_data)

            # 验证
            self.assertEqual(contract, expected_contract)
            mock_create.assert_called_once()

    def test_create_from_template_not_found(self):
        """测试基于不存在的模板创建合同"""
        # 准备
        with patch.object(
            self.contract_service, "get_template_by_id", return_value=None
        ):
            # 执行和验证
            with self.assertRaises(ContractTemplateError) as context:
                self.contract_service.create_from_template(999, {})

            self.assertIn("模板不存在", str(context.exception))

    def test_create_from_template_unusable(self):
        """测试基于不可用模板创建合同"""
        # 准备
        template = ContractTemplate.from_dict(self.sample_template_data)
        template.id = 1
        template.template_status = TemplateStatus.DEPRECATED

        with patch.object(
            self.contract_service, "get_template_by_id", return_value=template
        ):
            # 执行和验证
            with self.assertRaises(ContractTemplateError) as context:
                self.contract_service.create_from_template(1, {})

            self.assertIn("模板不可用", str(context.exception))

    # ==================== 业务规则测试 ====================

    def test_status_transition_validation(self):
        """测试状态转换验证"""
        service = self.contract_service

        # 测试合法转换
        self.assertTrue(
            service._is_valid_status_transition(
                ContractStatus.DRAFT, ContractStatus.SIGNED
            )
        )
        self.assertTrue(
            service._is_valid_status_transition(
                ContractStatus.SIGNED, ContractStatus.ACTIVE
            )
        )
        self.assertTrue(
            service._is_valid_status_transition(
                ContractStatus.ACTIVE, ContractStatus.COMPLETED
            )
        )

        # 测试非法转换
        self.assertFalse(
            service._is_valid_status_transition(
                ContractStatus.COMPLETED, ContractStatus.DRAFT
            )
        )
        self.assertFalse(
            service._is_valid_status_transition(
                ContractStatus.TERMINATED, ContractStatus.ACTIVE
            )
        )

    def test_apply_template(self):
        """测试应用模板"""
        # 准备
        template = ContractTemplate.from_dict(self.sample_template_data)
        contract_data = {
            "name": "模板应用测试合同",
            "contract_number": "C202501150003",
            "party_name": "模板应用测试",
        }

        # 执行
        merged_data = self.contract_service._apply_template(contract_data, template)

        # 验证
        self.assertEqual(merged_data["contract_number"], "C202501150003")
        self.assertEqual(merged_data["party_name"], "模板应用测试")
        self.assertEqual(merged_data["currency"], "CNY")  # 来自模板默认值
        self.assertEqual(merged_data["payment_terms"], 30)  # 来自模板默认值
        self.assertEqual(
            merged_data["terms_and_conditions"], "标准销售合同条款模板"
        )  # 来自模板

    # ==================== 统计功能测试 ====================

    def test_get_contract_statistics(self):
        """测试获取合同统计信息"""
        # 准备
        contracts = [
            Contract(
                name="测试合同1",
                contract_number="C001",
                party_name="测试客户1",
                contract_status=ContractStatus.DRAFT,
                contract_type=ContractType.SALES,
                contract_amount=Decimal("10000"),
            ),
            Contract(
                name="测试合同2",
                contract_number="C002",
                party_name="测试客户2",
                contract_status=ContractStatus.SIGNED,
                contract_type=ContractType.SALES,
                contract_amount=Decimal("20000"),
            ),
            Contract(
                name="测试合同3",
                contract_number="C003",
                party_name="测试供应商1",
                contract_status=ContractStatus.ACTIVE,
                contract_type=ContractType.PURCHASE,
                contract_amount=Decimal("30000"),
            ),
        ]

        with (
            patch.object(self.contract_service, "list_all", return_value=contracts),
            patch.object(
                self.contract_service, "get_expiring_contracts", return_value=[]
            ),
            patch.object(
                self.contract_service, "get_expired_contracts", return_value=[]
            ),
        ):
            # 执行
            stats = self.contract_service.get_contract_statistics()

            # 验证
            self.assertEqual(stats["total_contracts"], 3)
            self.assertEqual(stats["status_distribution"]["draft"], 1)
            self.assertEqual(stats["status_distribution"]["signed"], 1)
            self.assertEqual(stats["status_distribution"]["active"], 1)
            self.assertEqual(stats["type_distribution"]["sales"], 2)
            self.assertEqual(stats["type_distribution"]["purchase"], 1)

    # ==================== 异常处理测试 ====================

    def test_service_error_handling(self):
        """测试服务异常处理"""
        # 准备 - 模拟DAO异常
        self.mock_dao.insert.side_effect = Exception("数据库连接失败")

        # 执行和验证 - 基类服务会将异常包装为ServiceError
        with self.assertRaises(ServiceError) as context:
            self.contract_service.create(self.sample_contract_data)

        self.assertIn("创建记录失败", str(context.exception))

    def test_contract_not_found_error(self):
        """测试合同不存在错误"""
        # 准备
        with patch.object(self.contract_service, "get_by_id", return_value=None):
            # 执行和验证
            with self.assertRaises(BusinessLogicError) as context:
                self.contract_service.update_contract_status(999, ContractStatus.ACTIVE)

            self.assertIn("合同不存在", str(context.exception))


if __name__ == "__main__":
    unittest.main()
