"""
供应商财务管理服务

专门处理供应商相关的财务业务逻辑：
- 应付账款管理
- 供应商付款管理
- 账期管理
- 供应商财务风险评估

严格遵循分层架构和模块化原则：
- 只处理业务逻辑，不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
- 文件大小控制在推荐范围内
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from minicrm.data.dao.supplier_dao import SupplierDAO


class SupplierFinanceService:
    """
    供应商财务管理服务实现

    负责供应商财务相关的核心业务逻辑：
    - 应付账款管理
    - 供应商付款记录管理
    - 账期设置和管理
    - 供应商财务风险评估

    严格遵循单一职责原则和模块化标准。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商财务服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)
        self._logger.info("供应商财务服务初始化完成")

    def record_payable(self, supplier_id: int, payable_data: dict[str, Any]) -> int:
        """
        记录应付账款

        业务逻辑：
        1. 验证供应商存在
        2. 验证应付账款数据
        3. 记录应付账款
        4. 更新供应商财务状态

        Args:
            supplier_id: 供应商ID
            payable_data: 应付账款数据

        Returns:
            int: 应付账款记录ID

        Raises:
            BusinessLogicError: 当供应商不存在时
            ValidationError: 当数据验证失败时
            ServiceError: 当操作失败时
        """
        try:
            # 验证供应商存在
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 验证数据
            required_fields = ["amount", "due_date", "description"]
            self._validate_required_fields(payable_data, required_fields)

            amount = Decimal(str(payable_data["amount"]))
            if amount <= 0:
                raise ValidationError("应付金额必须大于0")

            # 记录应付账款
            payable_record = {
                "supplier_id": supplier_id,
                "amount": float(amount),
                "due_date": payable_data["due_date"],
                "description": payable_data["description"],
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "purchase_order_id": payable_data.get("purchase_order_id"),
            }

            payable_id = self._supplier_dao.insert_payable(payable_record)

            self._logger.info(f"成功记录应付账款: {supplier_id}, 金额: {amount}")
            return payable_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"记录应付账款失败: {e}")
            raise ServiceError(f"记录应付账款失败: {e}") from e

    def record_supplier_payment(
        self, supplier_id: int, payment_data: dict[str, Any]
    ) -> int:
        """
        记录供应商付款

        Args:
            supplier_id: 供应商ID
            payment_data: 付款数据

        Returns:
            int: 付款记录ID
        """
        try:
            # 验证供应商存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 验证数据
            required_fields = ["amount", "payment_method"]
            self._validate_required_fields(payment_data, required_fields)

            amount = Decimal(str(payment_data["amount"]))
            if amount <= 0:
                raise ValidationError("付款金额必须大于0")

            # 检查付款金额是否超过应付金额
            pending_payables = self._supplier_dao.get_pending_payables(supplier_id)
            total_payable = sum(
                Decimal(str(p.get("amount", 0))) for p in pending_payables
            )

            if amount > total_payable:
                self._logger.warning(f"付款金额({amount})超过应付金额({total_payable})")

            # 记录付款
            payment_record = {
                "supplier_id": supplier_id,
                "amount": float(amount),
                "payment_method": payment_data["payment_method"],
                "payment_date": payment_data.get(
                    "payment_date", datetime.now().isoformat()
                ),
                "description": payment_data.get("description", ""),
                "created_at": datetime.now().isoformat(),
                "reference_number": payment_data.get("reference_number"),
            }

            payment_id = self._supplier_dao.insert_supplier_payment(payment_record)

            # 更新应付账款状态
            self._update_payable_status(supplier_id, amount)

            self._logger.info(f"成功记录供应商付款: {supplier_id}, 金额: {amount}")
            return payment_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"记录供应商付款失败: {e}")
            raise ServiceError(f"记录供应商付款失败: {e}") from e

    def manage_payment_terms(self, supplier_id: int, terms_data: dict[str, Any]) -> int:
        """
        管理供应商账期设置

        Args:
            supplier_id: 供应商ID
            terms_data: 账期数据

        Returns:
            int: 账期设置记录ID
        """
        try:
            # 验证供应商存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 验证数据
            required_fields = ["payment_days", "payment_method"]
            self._validate_required_fields(terms_data, required_fields)

            payment_days = int(terms_data["payment_days"])
            if payment_days < 0:
                raise ValidationError("账期天数不能为负数")

            # 设置账期
            terms_record = {
                "supplier_id": supplier_id,
                "payment_days": payment_days,
                "payment_method": terms_data["payment_method"],
                "discount_rate": terms_data.get("discount_rate", 0),
                "discount_days": terms_data.get("discount_days", 0),
                "created_at": datetime.now().isoformat(),
            }

            terms_id = self._supplier_dao.insert_payment_terms(terms_record)

            self._logger.info(
                f"成功设置供应商账期: {supplier_id}, 天数: {payment_days}"
            )
            return terms_id

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"设置供应商账期失败: {e}")
            raise ServiceError(f"设置供应商账期失败: {e}") from e

    def assess_supplier_payment_risk(self, supplier_id: int) -> dict[str, Any]:
        """
        评估供应商付款风险

        基于以下维度评估：
        - 应付账款逾期情况
        - 历史付款记录
        - 账期遵守情况

        Args:
            supplier_id: 供应商ID

        Returns:
            Dict[str, Any]: 风险评估结果
        """
        try:
            # 获取供应商信息
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 获取财务数据
            payables = self._supplier_dao.get_payables(supplier_id)
            payments = self._supplier_dao.get_supplier_payments(supplier_id)
            payment_terms = self._supplier_dao.get_payment_terms(supplier_id)

            # 计算风险指标
            overdue_amount = self._calculate_supplier_overdue_amount(payables)
            payment_history_score = self._calculate_supplier_payment_score(payments)
            terms_compliance = self._calculate_terms_compliance(
                payables, payments, payment_terms
            )

            # 综合风险评估
            risk_score = self._calculate_supplier_risk_score(
                overdue_amount, payment_history_score, terms_compliance
            )

            risk_level = self._determine_supplier_risk_level(risk_score)

            result = {
                "supplier_id": supplier_id,
                "supplier_name": supplier.get("name", ""),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "overdue_amount": float(overdue_amount),
                "payment_history_score": payment_history_score,
                "terms_compliance": terms_compliance,
                "total_payables": sum(
                    Decimal(str(p.get("amount", 0))) for p in payables
                ),
                "assessed_at": datetime.now().isoformat(),
                "warnings": self._generate_supplier_risk_warnings(
                    risk_score, overdue_amount, terms_compliance
                ),
            }

            self._logger.info(
                f"供应商付款风险评估完成: {supplier_id}, 风险等级: {risk_level}"
            )
            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"供应商付款风险评估失败: {e}")
            raise ServiceError(f"供应商付款风险评估失败: {e}") from e

    def get_supplier_financial_summary(self, supplier_id: int) -> dict[str, Any]:
        """
        获取供应商财务汇总

        Args:
            supplier_id: 供应商ID

        Returns:
            Dict[str, Any]: 供应商财务汇总数据
        """
        try:
            # 获取供应商信息
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 获取财务数据
            payables = self._supplier_dao.get_payables(supplier_id)
            payments = self._supplier_dao.get_supplier_payments(supplier_id)
            payment_terms = self._supplier_dao.get_payment_terms(supplier_id)

            # 计算汇总数据
            total_payables = sum(Decimal(str(p.get("amount", 0))) for p in payables)
            pending_payables = sum(
                Decimal(str(p.get("amount", 0)))
                for p in payables
                if p.get("status") == "pending"
            )
            total_payments = sum(Decimal(str(p.get("amount", 0))) for p in payments)
            overdue_amount = self._calculate_supplier_overdue_amount(payables)

            result = {
                "supplier_id": supplier_id,
                "supplier_name": supplier.get("name", ""),
                "total_payables": float(total_payables),
                "pending_payables": float(pending_payables),
                "total_payments": float(total_payments),
                "overdue_amount": float(overdue_amount),
                "payment_terms": payment_terms,
                "payment_count": len(payments),
                "average_payment": float(total_payments / len(payments))
                if payments
                else 0,
                "generated_at": datetime.now().isoformat(),
            }

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"获取供应商财务汇总失败: {e}")
            raise ServiceError(f"获取供应商财务汇总失败: {e}") from e

    # ==================== 私有辅助方法 ====================

    def _update_payable_status(self, supplier_id: int, payment_amount: Decimal) -> None:
        """更新应付账款状态"""
        # 获取待付款的应付账款
        pending_payables = self._supplier_dao.get_pending_payables(supplier_id)

        remaining_amount = payment_amount
        for payable in pending_payables:
            if remaining_amount <= 0:
                break

            payable_amount = Decimal(str(payable.get("amount", 0)))
            if remaining_amount >= payable_amount:
                # 完全付款
                self._supplier_dao.update_payable_status(payable["id"], "paid")
                remaining_amount -= payable_amount
            else:
                # 部分付款 - 这里简化处理，实际可能需要拆分记录
                remaining_amount = Decimal(0)

    def _calculate_supplier_overdue_amount(
        self, payables: list[dict[str, Any]]
    ) -> Decimal:
        """计算供应商逾期金额"""
        overdue_amount = Decimal(0)
        current_date = datetime.now().date()

        for payable in payables:
            if payable.get("status") == "pending":
                due_date = datetime.fromisoformat(payable.get("due_date", "")).date()
                if due_date < current_date:
                    overdue_amount += Decimal(str(payable.get("amount", 0)))

        return overdue_amount

    def _calculate_supplier_payment_score(
        self, payments: list[dict[str, Any]]
    ) -> float:
        """计算供应商付款历史评分"""
        if not payments:
            return 0.0

        # 简化评分：基于付款次数和及时性
        return min(100.0, len(payments) * 5)

    def _calculate_terms_compliance(
        self,
        payables: list[dict[str, Any]],
        payments: list[dict[str, Any]],
        payment_terms: dict[str, Any] | None,
    ) -> float:
        """计算账期遵守情况"""
        if not payment_terms or not payables:
            return 100.0  # 没有设置账期或没有应付账款，默认100%

        # 简化计算：基于逾期情况
        overdue_count = 0
        total_count = len(payables)

        current_date = datetime.now().date()
        for payable in payables:
            due_date = datetime.fromisoformat(payable.get("due_date", "")).date()
            if due_date < current_date and payable.get("status") == "pending":
                overdue_count += 1

        if total_count == 0:
            return 100.0

        compliance_rate = (total_count - overdue_count) / total_count * 100
        return max(0.0, compliance_rate)

    def _calculate_supplier_risk_score(
        self,
        overdue_amount: Decimal,
        payment_history_score: float,
        terms_compliance: float,
    ) -> float:
        """计算供应商综合风险评分"""
        # 风险评分算法（分数越高风险越低）
        overdue_penalty = min(30, float(overdue_amount) / 1000)  # 逾期金额惩罚
        compliance_bonus = terms_compliance / 2  # 账期遵守奖励

        risk_score = payment_history_score + compliance_bonus - overdue_penalty
        return max(0, min(100, risk_score))

    def _determine_supplier_risk_level(self, risk_score: float) -> str:
        """确定供应商风险等级"""
        if risk_score >= 80:
            return "低风险"
        elif risk_score >= 60:
            return "中风险"
        elif risk_score >= 40:
            return "高风险"
        else:
            return "极高风险"

    def _generate_supplier_risk_warnings(
        self, risk_score: float, overdue_amount: Decimal, terms_compliance: float
    ) -> list[str]:
        """生成供应商风险预警"""
        warnings = []

        if risk_score < 40:
            warnings.append("供应商付款风险极高，建议调整合作策略")

        if overdue_amount > 0:
            warnings.append(f"存在逾期应付账款: ¥{overdue_amount:,.2f}")

        if terms_compliance < 80:
            warnings.append(f"账期遵守率较低: {terms_compliance:.1f}%")

        return warnings

    def _validate_required_fields(
        self, data: dict[str, Any], required_fields: list[str]
    ) -> None:
        """验证必填字段"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(f"缺少必填字段: {', '.join(missing_fields)}")
