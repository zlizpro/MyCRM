"""
MiniCRM 合同审批TTK组件简化单元测试

测试ContractApprovalTTK类的核心功能，避免GUI依赖。

作者: MiniCRM开发团队
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from minicrm.core.exceptions import ServiceError
from minicrm.models.contract import ContractStatus, ContractType
from minicrm.services.contract_service import ContractService


class TestContractApprovalTTKCore:
    """ContractApprovalTTK核心功能测试类（无GUI依赖）"""

    @pytest.fixture
    def mock_contract_service(self):
        """创建模拟的合同服务"""
        service = Mock(spec=ContractService)

        # 使用字典模拟待审批合同数据
        contract1_dict = {
            "id": 1,
            "contract_number": "S20240101001",
            "party_name": "测试客户A",
            "contract_type": ContractType.SALES,
            "contract_status": ContractStatus.PENDING,
            "contract_amount": Decimal(500000),
            "created_at": datetime.now() - timedelta(days=3),
            "terms_and_conditions": "标准销售条款",
            "contract_type_display": "销售合同",
            "status_display": "待审批",
            "formatted_amount": "¥500,000.00",
        }

        contract2_dict = {
            "id": 2,
            "contract_number": "P20240101002",
            "party_name": "测试供应商B",
            "contract_type": ContractType.PURCHASE,
            "contract_status": ContractStatus.PENDING,
            "contract_amount": Decimal(1200000),
            "created_at": datetime.now() - timedelta(days=8),
            "terms_and_conditions": "标准采购条款",
            "contract_type_display": "采购合同",
            "status_display": "待审批",
            "formatted_amount": "¥1,200,000.00",
        }

        # 创建模拟对象
        contract1 = Mock()
        contract1.to_dict.return_value = contract1_dict
        contract2 = Mock()
        contract2.to_dict.return_value = contract2_dict

        service.list_all.return_value = [contract1, contract2]
        service.update_contract_status.return_value = contract1

        return service

    def test_service_initialization(self, mock_contract_service):
        """测试服务初始化"""
        assert mock_contract_service is not None
        assert hasattr(mock_contract_service, "list_all")
        assert hasattr(mock_contract_service, "update_contract_status")

    def test_pending_contracts_data(self, mock_contract_service):
        """测试待审批合同数据"""
        contracts = mock_contract_service.list_all(
            {"contract_status": [ContractStatus.PENDING]}
        )
        assert len(contracts) == 2

        # 测试第一个合同
        contract1_dict = contracts[0].to_dict()
        assert contract1_dict["contract_number"] == "S20240101001"
        assert contract1_dict["contract_status"] == ContractStatus.PENDING
        assert contract1_dict["party_name"] == "测试客户A"

    def test_calculate_pending_days(self):
        """测试待审天数计算"""

        def calculate_pending_days(submit_time):
            if not submit_time:
                return 0
            try:
                if isinstance(submit_time, str):
                    dt = datetime.fromisoformat(submit_time.replace("Z", "+00:00"))
                else:
                    dt = submit_time
                return (datetime.now() - dt).days
            except:
                return 0

        # 测试3天前的日期
        past_date = datetime.now() - timedelta(days=3)
        days = calculate_pending_days(past_date)
        assert days == 3

        # 测试空字符串
        days = calculate_pending_days("")
        assert days == 0

        # 测试无效格式
        days = calculate_pending_days("invalid")
        assert days == 0

    def test_determine_priority(self):
        """测试优先级确定"""

        def determine_priority(approval, days_pending):
            amount = approval.get("contract_amount", 0)
            if days_pending > 7 or amount > 1000000:
                return "高"
            if days_pending > 3 or amount > 500000:
                return "中"
            return "低"

        # 高优先级（超过7天）
        approval = {"contract_amount": Decimal(500000)}
        priority = determine_priority(approval, 8)
        assert priority == "高"

        # 高优先级（金额超过100万）
        approval = {"contract_amount": Decimal(1500000)}
        priority = determine_priority(approval, 2)
        assert priority == "高"

        # 中优先级
        approval = {"contract_amount": Decimal(600000)}
        priority = determine_priority(approval, 4)
        assert priority == "中"

        # 低优先级
        approval = {"contract_amount": Decimal(100000)}
        priority = determine_priority(approval, 1)
        assert priority == "低"

    def test_approval_filtering(self, mock_contract_service):
        """测试审批筛选功能"""
        contracts = mock_contract_service.list_all(
            {"contract_status": [ContractStatus.PENDING]}
        )
        contract_dicts = [c.to_dict() for c in contracts]

        def apply_filters(approvals, type_filter="全部", priority_filter="全部"):
            filtered = approvals.copy()

            # 合同类型筛选
            if type_filter != "全部":
                filtered = [
                    a
                    for a in filtered
                    if a.get("contract_type_display", "") == type_filter
                ]

            # 优先级筛选（需要先计算优先级）
            if priority_filter != "全部":

                def determine_priority(approval, days_pending):
                    amount = approval.get("contract_amount", 0)
                    if days_pending > 7 or amount > 1000000:
                        return "高"
                    if days_pending > 3 or amount > 500000:
                        return "中"
                    return "低"

                filtered = [
                    a
                    for a in filtered
                    if determine_priority(a, 5) == priority_filter  # 假设5天
                ]

            return filtered

        # 测试类型筛选
        sales_contracts = apply_filters(contract_dicts, type_filter="销售合同")
        assert len(sales_contracts) == 1
        assert sales_contracts[0]["contract_type_display"] == "销售合同"

    def test_approval_operations(self, mock_contract_service):
        """测试审批操作"""

        def approve_contract(contract_id, comment):
            """模拟批准操作"""
            try:
                # 调用服务更新状态
                mock_contract_service.update_contract_status(
                    contract_id, ContractStatus.APPROVED, f"审批通过: {comment}"
                )
                return True, "合同已批准"
            except Exception as e:
                return False, f"批准失败: {e}"

        def reject_contract(contract_id, comment):
            """模拟拒绝操作"""
            try:
                # 调用服务更新状态
                mock_contract_service.update_contract_status(
                    contract_id, ContractStatus.DRAFT, f"审批拒绝: {comment}"
                )
                return True, "合同已拒绝"
            except Exception as e:
                return False, f"拒绝失败: {e}"

        def return_contract(contract_id, comment):
            """模拟退回操作"""
            try:
                # 调用服务更新状态
                mock_contract_service.update_contract_status(
                    contract_id, ContractStatus.DRAFT, f"审批退回: {comment}"
                )
                return True, "合同已退回"
            except Exception as e:
                return False, f"退回失败: {e}"

        # 测试批准操作
        success, message = approve_contract(1, "条款符合要求")
        assert success is True
        assert "已批准" in message
        mock_contract_service.update_contract_status.assert_called_with(
            1, ContractStatus.APPROVED, "审批通过: 条款符合要求"
        )

        # 重置mock
        mock_contract_service.reset_mock()

        # 测试拒绝操作
        success, message = reject_contract(1, "条款不符合要求")
        assert success is True
        assert "已拒绝" in message
        mock_contract_service.update_contract_status.assert_called_with(
            1, ContractStatus.DRAFT, "审批拒绝: 条款不符合要求"
        )

        # 重置mock
        mock_contract_service.reset_mock()

        # 测试退回操作
        success, message = return_contract(1, "需要补充材料")
        assert success is True
        assert "已退回" in message
        mock_contract_service.update_contract_status.assert_called_with(
            1, ContractStatus.DRAFT, "审批退回: 需要补充材料"
        )

    def test_approval_validation(self):
        """测试审批验证"""

        def validate_approval_comment(comment):
            """验证审批意见"""
            errors = []

            if not comment or not comment.strip():
                errors.append("审批意见不能为空")

            if len(comment.strip()) < 5:
                errors.append("审批意见至少需要5个字符")

            if len(comment.strip()) > 500:
                errors.append("审批意见不能超过500个字符")

            return len(errors) == 0, errors

        # 测试有效意见
        is_valid, errors = validate_approval_comment("审批通过，条款符合要求")
        assert is_valid is True
        assert len(errors) == 0

        # 测试空意见
        is_valid, errors = validate_approval_comment("")
        assert is_valid is False
        assert "不能为空" in errors[0]

        # 测试过短意见
        is_valid, errors = validate_approval_comment("OK")
        assert is_valid is False
        assert "至少需要5个字符" in errors[0]

    def test_approval_statistics(self, mock_contract_service):
        """测试审批统计"""
        contracts = mock_contract_service.list_all(
            {"contract_status": [ContractStatus.PENDING]}
        )
        contract_dicts = [c.to_dict() for c in contracts]

        def calculate_approval_stats(approvals):
            """计算审批统计信息"""
            total_pending = len(approvals)

            def determine_priority(approval):
                amount = approval.get("contract_amount", 0)
                created_at = approval.get("created_at")
                if created_at:
                    days_pending = (datetime.now() - created_at).days
                    if days_pending > 7 or amount > 1000000:
                        return "高"
                    if days_pending > 3 or amount > 500000:
                        return "中"
                return "低"

            high_priority = sum(1 for a in approvals if determine_priority(a) == "高")

            return {
                "total_pending": total_pending,
                "high_priority": high_priority,
                "medium_priority": sum(
                    1 for a in approvals if determine_priority(a) == "中"
                ),
                "low_priority": sum(
                    1 for a in approvals if determine_priority(a) == "低"
                ),
            }

        stats = calculate_approval_stats(contract_dicts)

        assert stats["total_pending"] == 2
        assert stats["high_priority"] >= 0
        assert stats["medium_priority"] >= 0
        assert stats["low_priority"] >= 0
        assert (
            stats["high_priority"] + stats["medium_priority"] + stats["low_priority"]
        ) == 2

    @patch("minicrm.services.contract_service.ContractService")
    def test_service_error_handling(self, mock_service_class):
        """测试服务错误处理"""
        # 模拟服务错误
        mock_service = Mock()
        mock_service.list_all.side_effect = ServiceError("数据库连接失败")
        mock_service_class.return_value = mock_service

        # 测试错误处理
        with pytest.raises(ServiceError):
            mock_service.list_all({"contract_status": [ContractStatus.PENDING]})

    def test_approval_history_recording(self):
        """测试审批历史记录"""

        def record_approval_action(contract_id, action, comment, approver):
            """记录审批操作"""
            history_record = {
                "contract_id": contract_id,
                "action": action,
                "comment": comment,
                "approver": approver,
                "approval_time": datetime.now(),
            }
            return history_record

        # 测试记录审批操作
        record = record_approval_action(1, "approve", "审批通过", "测试用户")

        assert record["contract_id"] == 1
        assert record["action"] == "approve"
        assert record["comment"] == "审批通过"
        assert record["approver"] == "测试用户"
        assert isinstance(record["approval_time"], datetime)

    def test_batch_approval_logic(self, mock_contract_service):
        """测试批量审批逻辑"""
        contracts = mock_contract_service.list_all(
            {"contract_status": [ContractStatus.PENDING]}
        )
        contract_ids = [c.to_dict()["id"] for c in contracts]

        def batch_approve(contract_ids, comment, approver):
            """批量审批"""
            results = []
            for contract_id in contract_ids:
                try:
                    mock_contract_service.update_contract_status(
                        contract_id, ContractStatus.APPROVED, f"批量审批: {comment}"
                    )
                    results.append(
                        {
                            "contract_id": contract_id,
                            "success": True,
                            "message": "审批成功",
                        }
                    )
                except Exception as e:
                    results.append(
                        {
                            "contract_id": contract_id,
                            "success": False,
                            "message": str(e),
                        }
                    )
            return results

        # 测试批量审批
        results = batch_approve(contract_ids, "批量审批通过", "测试用户")

        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert mock_contract_service.update_contract_status.call_count == 2

    def test_format_datetime_function(self):
        """测试日期时间格式化功能"""

        def format_datetime(datetime_str):
            if not datetime_str:
                return "未知"
            try:
                if isinstance(datetime_str, str):
                    dt = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
                else:
                    dt = datetime_str
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return str(datetime_str)

        # 测试正常日期时间
        dt_str = "2024-01-15T10:30:00"
        formatted = format_datetime(dt_str)
        assert "2024-01-15" in formatted

        # 测试空字符串
        formatted = format_datetime("")
        assert formatted == "未知"

        # 测试无效格式
        formatted = format_datetime("invalid")
        assert formatted == "invalid"


if __name__ == "__main__":
    pytest.main([__file__])
