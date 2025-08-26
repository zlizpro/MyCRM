"""
MiniCRM 合同管理服务

提供完整的合同管理功能,包括:
- 合同生命周期管理
- 合同到期提醒和续约管理
- 合同模板管理
- 与报价系统的集成
- 财务记录关联

设计原则:
- 继承自CRUDService提供基础CRUD功能
- 集成transfunctions进行数据验证和格式化
- 支持客户合同和供应商合同
- 提供完善的业务规则验证
- 实现合同状态转换管理
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from transfunctions import (
    format_currency,
    format_date,
)

from ..core.exceptions import BusinessLogicError, ServiceError, ValidationError
from ..models.contract import Contract, ContractStatus, ContractType
from ..models.contract_template import ContractTemplate, TemplateType
from .base_service import CRUDService, register_service


class ContractServiceError(ServiceError):
    """合同服务专用异常"""

    pass


class ContractStatusError(BusinessLogicError):
    """合同状态错误"""

    pass


class ContractTemplateError(BusinessLogicError):
    """合同模板错误"""

    pass


@register_service("contract_service")
class ContractService(CRUDService):
    """
    合同管理服务

    提供合同的完整生命周期管理,包括创建、状态管理、到期提醒、
    模板管理等功能.支持客户合同和供应商合同两种类型.
    """

    def __init__(self, dao=None):
        """
        初始化合同服务

        Args:
            dao: 数据访问对象
        """
        super().__init__(dao, Contract)
        self._template_cache = {}  # 模板缓存

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "合同管理服务"

    # ==================== 基础CRUD操作 ====================

    def _validate_create_data(self, data: dict[str, Any]) -> None:
        """验证创建合同数据"""
        # 先验证合同类型,以便进行业务逻辑验证
        if "contract_type" in data and isinstance(data["contract_type"], str):
            try:
                ContractType(data["contract_type"])
            except ValueError as e:
                raise ValidationError(f"无效的合同类型: {data['contract_type']}") from e

        # 验证关联方信息(业务逻辑验证)
        contract_type = data.get("contract_type")
        if contract_type == ContractType.SALES or contract_type == "sales":
            if not data.get("customer_id") and not data.get("party_name"):
                raise ValidationError("销售合同必须关联客户")
        elif (
            (contract_type == ContractType.PURCHASE or contract_type == "purchase")
            and not data.get("supplier_id")
            and not data.get("party_name")
        ):
            raise ValidationError("采购合同必须关联供应商")

        # 验证必填字段
        required_fields = [
            "contract_number",
            "party_name",
            "contract_amount",
            "contract_type",
        ]
        self._validate_required_fields(data, required_fields)

        # 验证合同金额
        if "contract_amount" in data:
            try:
                amount = Decimal(str(data["contract_amount"]))
                if amount < 0:
                    raise ValidationError("合同金额不能为负数")
            except (ValueError, TypeError) as e:
                raise ValidationError("合同金额格式不正确") from e

    def _validate_update_data(self, data: dict[str, Any]) -> None:
        """验证更新合同数据"""
        # 更新时不需要所有必填字段,但需要验证提供的字段
        if "contract_amount" in data:
            try:
                amount = Decimal(str(data["contract_amount"]))
                if amount < 0:
                    raise ValidationError("合同金额不能为负数")
            except (ValueError, TypeError) as e:
                raise ValidationError("合同金额格式不正确") from e

        if "contract_type" in data and isinstance(data["contract_type"], str):
            try:
                ContractType(data["contract_type"])
            except ValueError as e:
                raise ValidationError(f"无效的合同类型: {data['contract_type']}") from e

    def _perform_create(self, data: dict[str, Any]) -> Contract:
        """执行创建合同操作"""
        try:
            # 创建合同实例
            contract = Contract.from_dict(data)
            contract.validate()

            # 调用DAO保存到数据库
            if self._dao:
                contract_id = self._dao.insert(contract.to_dict())
                contract.id = contract_id
            else:
                # 临时模拟ID分配(当没有DAO时)
                contract.id = hash(contract.contract_number) % 100000

            self._log_operation(
                "创建合同",
                {
                    "contract_id": contract.id,
                    "contract_number": contract.contract_number,
                    "party_name": contract.party_name,
                    "amount": str(contract.contract_amount),
                },
            )

            return contract

        except (ValidationError, BusinessLogicError) as e:
            # 业务逻辑错误直接抛出
            raise e
        except ContractServiceError:
            # 已经是ContractServiceError,直接抛出
            raise
        except Exception as e:
            raise ContractServiceError(f"创建合同失败: {e}") from e

    def _perform_get_by_id(self, contract_id: int) -> Contract | None:
        """执行根据ID获取合同操作"""
        try:
            # 这里应该调用DAO从数据库获取
            # contract_data = self._dao.get_by_id(contract_id)
            # if contract_data:
            #     return Contract.from_dict(contract_data)
            # return None

            # 临时返回None
            return None

        except Exception as e:
            raise ContractServiceError(f"获取合同失败: {e}") from e

    def _perform_update(self, contract_id: int, data: dict[str, Any]) -> Contract:
        """执行更新合同操作"""
        try:
            # 获取现有合同
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 更新字段
            for key, value in data.items():
                if hasattr(contract, key):
                    setattr(contract, key, value)

            # 验证更新后的数据
            contract.validate()

            # 这里应该调用DAO更新数据库
            # self._dao.update(contract_id, contract.to_dict())

            self._log_operation(
                "更新合同",
                {"contract_id": contract_id, "updated_fields": list(data.keys())},
            )

            return contract

        except Exception as e:
            raise ContractServiceError(f"更新合同失败: {e}") from e

    def _perform_delete(self, contract_id: int) -> bool:
        """执行删除合同操作"""
        try:
            # 检查合同是否存在
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 检查是否可以删除
            if contract.contract_status in [
                ContractStatus.SIGNED,
                ContractStatus.ACTIVE,
                ContractStatus.COMPLETED,
            ]:
                raise BusinessLogicError("已签署或执行中的合同不能删除")

            # 这里应该调用DAO删除
            # result = self._dao.delete(contract_id)

            self._log_operation("删除合同", {"contract_id": contract_id})

            return True

        except Exception as e:
            raise ContractServiceError(f"删除合同失败: {e}") from e

    def _perform_list_all(
        self, filters: dict[str, Any] | None = None
    ) -> list[Contract]:
        """执行获取所有合同操作"""
        try:
            # 这里应该调用DAO查询数据库
            # contracts_data = self._dao.list_all(filters)
            # return [Contract.from_dict(data) for data in contracts_data]

            # 临时返回空列表
            return []

        except Exception as e:
            raise ContractServiceError(f"获取合同列表失败: {e}") from e

    # ==================== 合同生命周期管理 ====================

    def create_contract(
        self,
        contract_data: dict[str, Any],
        from_quote_id: int | None = None,
        template_id: int | None = None,
    ) -> Contract:
        """
        创建合同

        Args:
            contract_data: 合同数据
            from_quote_id: 关联的报价ID
            template_id: 使用的模板ID

        Returns:
            Contract: 创建的合同实例

        Raises:
            ValidationError: 当数据验证失败时
            ContractServiceError: 当创建失败时
        """
        try:
            # 如果指定了模板,应用模板
            if template_id:
                template = self.get_template_by_id(template_id)
                if template and template.is_usable():
                    contract_data = self._apply_template(contract_data, template)
                    template.increment_usage()

            # 如果从报价创建,填充报价信息
            if from_quote_id:
                contract_data = self._fill_from_quote(contract_data, from_quote_id)

            # 创建合同
            contract = self.create(contract_data)

            self._log_operation(
                "创建合同成功",
                {
                    "contract_id": contract.id,
                    "from_quote": from_quote_id,
                    "template_id": template_id,
                },
            )

            return contract

        except Exception as e:
            self._handle_service_error("创建合同", e)

    def update_contract_status(
        self, contract_id: int, new_status: ContractStatus, reason: str = ""
    ) -> Contract:
        """
        更新合同状态

        Args:
            contract_id: 合同ID
            new_status: 新状态
            reason: 状态变更原因

        Returns:
            Contract: 更新后的合同

        Raises:
            ContractStatusError: 当状态转换不合法时
            ContractServiceError: 当更新失败时
        """
        try:
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 验证状态转换
            if not self._is_valid_status_transition(
                contract.contract_status, new_status
            ):
                raise ContractStatusError(
                    f"不能从{contract.contract_status.value}转换到{new_status.value}"
                )

            # 更新状态
            old_status = contract.contract_status
            contract.contract_status = new_status

            # 记录状态变更原因
            if reason:
                status_note = (
                    f"状态变更: {old_status.value} → {new_status.value}, 原因: {reason}"
                )
                contract.notes = f"{contract.notes}\n{status_note}".strip()

            # 保存更新
            updated_contract = self.update(contract_id, contract.to_dict())

            self._log_operation(
                "更新合同状态",
                {
                    "contract_id": contract_id,
                    "old_status": old_status.value,
                    "new_status": new_status.value,
                    "reason": reason,
                },
            )

            return updated_contract

        except Exception as e:
            self._handle_service_error("更新合同状态", e)

    def sign_contract(
        self, contract_id: int, sign_date: datetime | None = None, signer: str = ""
    ) -> Contract:
        """
        签署合同

        Args:
            contract_id: 合同ID
            sign_date: 签署日期
            signer: 签署人

        Returns:
            Contract: 签署后的合同

        Raises:
            ContractStatusError: 当合同状态不允许签署时
            ContractServiceError: 当签署失败时
        """
        try:
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 签署合同
            contract.sign_contract(sign_date)

            # 记录签署信息
            if signer:
                sign_note = f"合同签署人: {signer}"
                contract.notes = f"{contract.notes}\n{sign_note}".strip()

            # 保存更新
            updated_contract = self.update(contract_id, contract.to_dict())

            self._log_operation(
                "签署合同",
                {
                    "contract_id": contract_id,
                    "sign_date": contract.get_formatted_sign_date(),
                    "signer": signer,
                },
            )

            return updated_contract

        except Exception as e:
            self._handle_service_error("签署合同", e)

    def terminate_contract(
        self, contract_id: int, reason: str, termination_date: datetime | None = None
    ) -> Contract:
        """
        终止合同

        Args:
            contract_id: 合同ID
            reason: 终止原因
            termination_date: 终止日期

        Returns:
            Contract: 终止后的合同

        Raises:
            ContractStatusError: 当合同状态不允许终止时
            ContractServiceError: 当终止失败时
        """
        try:
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 终止合同
            contract.terminate_contract(reason)

            # 记录终止日期
            if termination_date:
                termination_note = (
                    f"终止日期: {format_date(termination_date, '%Y-%m-%d')}"
                )
                contract.notes = f"{contract.notes}\n{termination_note}".strip()

            # 保存更新
            updated_contract = self.update(contract_id, contract.to_dict())

            self._log_operation(
                "终止合同",
                {
                    "contract_id": contract_id,
                    "reason": reason,
                    "termination_date": termination_date,
                },
            )

            return updated_contract

        except Exception as e:
            self._handle_service_error("终止合同", e)

    def update_contract_progress(
        self, contract_id: int, percentage: float, actual_amount: Decimal | None = None
    ) -> Contract:
        """
        更新合同执行进度

        Args:
            contract_id: 合同ID
            percentage: 执行进度百分比
            actual_amount: 实际执行金额

        Returns:
            Contract: 更新后的合同

        Raises:
            ValidationError: 当进度数据无效时
            ContractServiceError: 当更新失败时
        """
        try:
            contract = self.get_by_id(contract_id)
            if not contract:
                raise BusinessLogicError(f"合同不存在: {contract_id}")

            # 更新进度
            contract.update_progress(percentage, actual_amount)

            # 保存更新
            updated_contract = self.update(contract_id, contract.to_dict())

            self._log_operation(
                "更新合同进度",
                {
                    "contract_id": contract_id,
                    "progress": percentage,
                    "actual_amount": str(actual_amount) if actual_amount else None,
                },
            )

            return updated_contract

        except Exception as e:
            self._handle_service_error("更新合同进度", e)

    # ==================== 合同到期提醒和续约管理 ====================

    def get_expiring_contracts(self, days_ahead: int = 30) -> list[Contract]:
        """
        获取即将到期的合同

        Args:
            days_ahead: 提前天数

        Returns:
            List[Contract]: 即将到期的合同列表
        """
        try:
            # 获取所有活跃合同
            active_contracts = self.list_all(
                {"contract_status": [ContractStatus.SIGNED, ContractStatus.ACTIVE]}
            )

            # 筛选即将到期的合同
            expiring_contracts = [
                contract
                for contract in active_contracts
                if contract.is_expiring_soon(days_ahead)
            ]

            self._log_operation(
                "获取即将到期合同",
                {"days_ahead": days_ahead, "count": len(expiring_contracts)},
            )

            return expiring_contracts

        except Exception as e:
            self._handle_service_error("获取即将到期合同", e)

    def get_expired_contracts(self) -> list[Contract]:
        """
        获取已过期的合同

        Returns:
            List[Contract]: 已过期的合同列表
        """
        try:
            # 获取所有活跃合同
            active_contracts = self.list_all(
                {"contract_status": [ContractStatus.SIGNED, ContractStatus.ACTIVE]}
            )

            # 筛选已过期的合同
            expired_contracts = [
                contract for contract in active_contracts if contract.is_expired()
            ]

            self._log_operation("获取已过期合同", {"count": len(expired_contracts)})

            return expired_contracts

        except Exception as e:
            self._handle_service_error("获取已过期合同", e)

    def process_expired_contracts(self) -> dict[str, int]:
        """
        处理已过期的合同

        Returns:
            Dict[str, int]: 处理结果统计
        """
        try:
            expired_contracts = self.get_expired_contracts()
            processed_count = 0
            error_count = 0

            for contract in expired_contracts:
                try:
                    # 更新合同状态为已过期
                    self.update_contract_status(
                        contract.id, ContractStatus.EXPIRED, "合同已过期"
                    )
                    processed_count += 1
                except Exception as e:
                    self.logger.error(f"处理过期合同失败 {contract.id}: {e}")
                    error_count += 1

            result = {"processed": processed_count, "errors": error_count}

            self._log_operation("处理过期合同", result)

            return result

        except Exception as e:
            self._handle_service_error("处理过期合同", e)

    def create_renewal_contract(
        self, original_contract_id: int, renewal_data: dict[str, Any]
    ) -> Contract:
        """
        创建续约合同

        Args:
            original_contract_id: 原合同ID
            renewal_data: 续约数据

        Returns:
            Contract: 新的续约合同

        Raises:
            BusinessLogicError: 当原合同不存在或不能续约时
            ContractServiceError: 当创建失败时
        """
        try:
            original_contract = self.get_by_id(original_contract_id)
            if not original_contract:
                raise BusinessLogicError(f"原合同不存在: {original_contract_id}")

            # 检查是否可以续约
            if not original_contract.is_active():
                raise BusinessLogicError("只有活跃状态的合同才能续约")

            # 基于原合同创建续约合同数据
            renewal_contract_data = {
                "contract_type": original_contract.contract_type,
                "customer_id": original_contract.customer_id,
                "supplier_id": original_contract.supplier_id,
                "party_name": original_contract.party_name,
                "contract_amount": original_contract.contract_amount,
                "currency": original_contract.currency,
                "payment_method": original_contract.payment_method,
                "payment_terms": original_contract.payment_terms,
                "terms_and_conditions": original_contract.terms_and_conditions,
                "delivery_terms": original_contract.delivery_terms,
                "warranty_terms": original_contract.warranty_terms,
                "reminder_days": original_contract.reminder_days,
                "auto_renewal": original_contract.auto_renewal,
            }

            # 应用续约数据覆盖
            renewal_contract_data.update(renewal_data)

            # 创建续约合同
            renewal_contract = self.create_contract(renewal_contract_data)

            # 在原合同中记录续约信息
            renewal_note = f"续约合同: {renewal_contract.contract_number}"
            original_contract.notes = (
                f"{original_contract.notes}\n{renewal_note}".strip()
            )
            self.update(original_contract_id, {"notes": original_contract.notes})

            self._log_operation(
                "创建续约合同",
                {
                    "original_contract_id": original_contract_id,
                    "renewal_contract_id": renewal_contract.id,
                },
            )

            return renewal_contract

        except Exception as e:
            self._handle_service_error("创建续约合同", e)

    # ==================== 合同模板管理 ====================

    def create_template(self, template_data: dict[str, Any]) -> ContractTemplate:
        """
        创建合同模板

        Args:
            template_data: 模板数据

        Returns:
            ContractTemplate: 创建的模板

        Raises:
            ValidationError: 当数据验证失败时
            ContractTemplateError: 当创建失败时
        """
        try:
            # 验证模板数据
            required_fields = ["template_name", "contract_type", "created_by"]
            self._validate_required_fields(template_data, required_fields)

            # 创建模板实例
            template = ContractTemplate.from_dict(template_data)
            template.validate()

            # 这里应该调用DAO保存到数据库
            # template_id = self._dao.insert_template(template.to_dict())
            # template.id = template_id

            # 临时模拟ID分配
            template.id = hash(template.template_name) % 100000

            # 清除模板缓存
            self._cache_clear("template_")

            self._log_operation(
                "创建合同模板",
                {"template_id": template.id, "template_name": template.template_name},
            )

            return template

        except (ValidationError, BusinessLogicError) as e:
            # 业务逻辑错误直接抛出
            raise e
        except Exception as e:
            raise ContractTemplateError(f"创建合同模板失败: {e}") from e

    def get_template_by_id(self, template_id: int) -> ContractTemplate | None:
        """
        根据ID获取模板

        Args:
            template_id: 模板ID

        Returns:
            Optional[ContractTemplate]: 模板实例或None
        """
        try:
            # 检查缓存
            cache_key = f"template_{template_id}"
            cached_template = self._cache_get(cache_key)
            if cached_template:
                return cached_template

            # 这里应该调用DAO从数据库获取
            # template_data = self._dao.get_template_by_id(template_id)
            # if template_data:
            #     template = ContractTemplate.from_dict(template_data)
            #     self._cache_set(cache_key, template)
            #     return template

            return None

        except Exception as e:
            self._handle_service_error("获取合同模板", e)

    def get_templates(
        self,
        contract_type: ContractType | None = None,
        template_type: TemplateType | None = None,
    ) -> list[ContractTemplate]:
        """
        获取合同模板列表

        Args:
            contract_type: 合同类型筛选
            template_type: 模板类型筛选

        Returns:
            List[ContractTemplate]: 模板列表
        """
        try:
            # 构建筛选条件
            filters = {}
            if contract_type:
                filters["contract_type"] = contract_type
            if template_type:
                filters["template_type"] = template_type

            # 这里应该调用DAO查询数据库
            # templates_data = self._dao.list_templates(filters)
            # return [ContractTemplate.from_dict(data) for data in templates_data]

            # 临时返回空列表
            return []

        except Exception as e:
            self._handle_service_error("获取合同模板列表", e)

    def create_from_template(
        self, template_id: int, contract_data: dict[str, Any]
    ) -> Contract:
        """
        基于模板创建合同

        Args:
            template_id: 模板ID
            contract_data: 合同数据

        Returns:
            Contract: 创建的合同

        Raises:
            ContractTemplateError: 当模板不存在或不可用时
            ContractServiceError: 当创建失败时
        """
        try:
            template = self.get_template_by_id(template_id)
            if not template:
                raise ContractTemplateError(f"模板不存在: {template_id}")

            if not template.is_usable():
                raise ContractTemplateError(f"模板不可用: {template.template_name}")

            # 应用模板
            merged_data = self._apply_template(contract_data, template)

            # 创建合同
            contract = self.create_contract(merged_data, template_id=template_id)

            return contract

        except Exception as e:
            self._handle_service_error("基于模板创建合同", e)

    # ==================== 辅助方法 ====================

    def _is_valid_status_transition(
        self, current_status: ContractStatus, new_status: ContractStatus
    ) -> bool:
        """
        验证合同状态转换是否合法

        Args:
            current_status: 当前状态
            new_status: 新状态

        Returns:
            bool: 是否合法
        """
        # 定义合法的状态转换
        valid_transitions = {
            ContractStatus.DRAFT: [
                ContractStatus.PENDING,
                ContractStatus.APPROVED,
                ContractStatus.SIGNED,
                ContractStatus.TERMINATED,
            ],
            ContractStatus.PENDING: [
                ContractStatus.DRAFT,
                ContractStatus.APPROVED,
                ContractStatus.TERMINATED,
            ],
            ContractStatus.APPROVED: [
                ContractStatus.SIGNED,
                ContractStatus.TERMINATED,
            ],
            ContractStatus.SIGNED: [
                ContractStatus.ACTIVE,
                ContractStatus.COMPLETED,
                ContractStatus.TERMINATED,
                ContractStatus.EXPIRED,
            ],
            ContractStatus.ACTIVE: [
                ContractStatus.COMPLETED,
                ContractStatus.TERMINATED,
                ContractStatus.EXPIRED,
            ],
            ContractStatus.COMPLETED: [],  # 已完成的合同不能再转换
            ContractStatus.TERMINATED: [],  # 已终止的合同不能再转换
            ContractStatus.EXPIRED: [ContractStatus.TERMINATED],  # 过期合同只能终止
        }

        return new_status in valid_transitions.get(current_status, [])

    def _apply_template(
        self, contract_data: dict[str, Any], template: ContractTemplate
    ) -> dict[str, Any]:
        """
        应用模板到合同数据

        Args:
            contract_data: 原始合同数据
            template: 合同模板

        Returns:
            Dict[str, Any]: 应用模板后的合同数据
        """
        # 复制原始数据
        merged_data = contract_data.copy()

        # 应用模板默认值(不覆盖已有值)
        if hasattr(template, "default_values") and template.default_values:
            for field, default_value in template.default_values.items():
                if field not in merged_data or merged_data[field] is None:
                    merged_data[field] = default_value

        # 应用模板内容
        if (
            hasattr(template, "terms_template")
            and template.terms_template
            and not merged_data.get("terms_and_conditions")
        ):
            merged_data["terms_and_conditions"] = template.terms_template

        if (
            hasattr(template, "delivery_terms_template")
            and template.delivery_terms_template
            and not merged_data.get("delivery_terms")
        ):
            merged_data["delivery_terms"] = template.delivery_terms_template

        if (
            hasattr(template, "warranty_terms_template")
            and template.warranty_terms_template
            and not merged_data.get("warranty_terms")
        ):
            merged_data["warranty_terms"] = template.warranty_terms_template

        # 设置模板ID
        merged_data["template_id"] = template.id

        return merged_data

    def _fill_from_quote(
        self, contract_data: dict[str, Any], quote_id: int
    ) -> dict[str, Any]:
        """
        从报价填充合同数据

        Args:
            contract_data: 原始合同数据
            quote_id: 报价ID

        Returns:
            Dict[str, Any]: 填充后的合同数据
        """
        # 这里应该调用报价服务获取报价信息
        # quote_service = ServiceRegistry.get_service("quote_service")
        # if quote_service:
        #     quote = quote_service.get_by_id(quote_id)
        #     if quote:
        #         contract_data.update({
        #             "customer_id": quote.customer_id,
        #             "party_name": quote.customer_name,
        #             "contract_amount": quote.total_amount,
        #             "quote_id": quote_id,
        #         })

        # 临时实现
        contract_data["quote_id"] = quote_id

        return contract_data

    def get_contract_statistics(self) -> dict[str, Any]:
        """
        获取合同统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            all_contracts = self.list_all()

            # 按状态统计
            status_stats = {}
            for status in ContractStatus:
                status_stats[status.value] = sum(
                    1 for c in all_contracts if c.contract_status == status
                )

            # 按类型统计
            type_stats = {}
            for contract_type in ContractType:
                type_stats[contract_type.value] = sum(
                    1 for c in all_contracts if c.contract_type == contract_type
                )

            # 金额统计
            total_amount = sum(c.contract_amount for c in all_contracts)
            active_amount = sum(
                c.contract_amount
                for c in all_contracts
                if c.contract_status in [ContractStatus.SIGNED, ContractStatus.ACTIVE]
            )

            # 到期统计
            expiring_count = len(self.get_expiring_contracts())
            expired_count = len(self.get_expired_contracts())

            return {
                "total_contracts": len(all_contracts),
                "status_distribution": status_stats,
                "type_distribution": type_stats,
                "total_amount": format_currency(float(total_amount)),
                "active_amount": format_currency(float(active_amount)),
                "expiring_contracts": expiring_count,
                "expired_contracts": expired_count,
            }

        except Exception as e:
            self._handle_service_error("获取合同统计", e)
