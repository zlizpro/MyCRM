"""
MiniCRM 报价核心服务

负责报价的基础CRUD操作，保持单一职责原则。
从原始的quote_service.py中提取核心功能。
"""

from datetime import datetime
from typing import Any

from transfunctions import ValidationError
from transfunctions.validation.core import validate_required_fields

from ...core import BusinessLogicError, ServiceError
from ...models import Quote
from ...models.quote import QuoteStatus
from ..base_service import CRUDService, register_service


@register_service("quote_core_service")
class QuoteCoreService(CRUDService):
    """
    报价核心服务

    专注于报价的基础CRUD操作，遵循单一职责原则。
    """

    def __init__(self, dao=None):
        """初始化报价核心服务"""
        super().__init__(dao)
        self._model_class = Quote

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "报价核心服务"

    # ==================== 数据验证 ====================

    def _validate_create_data(self, data: dict[str, Any]) -> None:
        """验证创建报价数据"""
        required_fields = ["customer_name", "items"]
        validate_required_fields(data, required_fields)

        # 验证报价项目
        if not isinstance(data.get("items"), list) or not data["items"]:
            raise ValidationError("报价项目不能为空")

        for i, item in enumerate(data["items"]):
            item_errors = []
            if not item.get("product_name"):
                item_errors.append("产品名称不能为空")
            if not item.get("unit_price") or float(item["unit_price"]) <= 0:
                item_errors.append("单价必须大于0")
            if not item.get("quantity") or float(item["quantity"]) <= 0:
                item_errors.append("数量必须大于0")

            if item_errors:
                raise ValidationError(f"报价项目{i + 1}: {'; '.join(item_errors)}")

    def _validate_update_data(self, data: dict[str, Any]) -> None:
        """验证更新报价数据"""
        # 更新时不要求所有字段都存在
        if "items" in data:
            if not isinstance(data["items"], list):
                raise ValidationError("报价项目格式不正确")
            for i, item in enumerate(data["items"]):
                if not isinstance(item, dict):
                    raise ValidationError(f"报价项目{i + 1}数据格式不正确")

    # ==================== CRUD操作 ====================

    def _perform_create(self, data: dict[str, Any]) -> Quote:
        """执行创建报价操作"""
        try:
            # 设置默认值
            data.setdefault("quote_date", datetime.now())
            data.setdefault(
                "valid_until", datetime.now().replace(day=datetime.now().day + 30)
            )
            data.setdefault("quote_status", QuoteStatus.DRAFT.value)

            # 生成报价编号
            if not data.get("quote_number"):
                data["quote_number"] = self._generate_quote_number()

            # 计算总金额
            if "items" in data:
                total_amount = sum(
                    float(item.get("unit_price", 0)) * float(item.get("quantity", 0))
                    for item in data["items"]
                )
                data["total_amount"] = total_amount

            # 创建报价对象
            quote = Quote.from_dict(data)

            # 保存到数据库
            if self._dao:
                quote_id = self._dao.create(quote.to_dict())
                quote.id = quote_id

            return quote

        except Exception as e:
            raise ServiceError(f"创建报价失败: {e}") from e

    def _perform_get_by_id(self, record_id: int) -> Quote | None:
        """执行根据ID获取报价操作"""
        if not self._dao:
            raise ServiceError("数据访问对象未初始化")

        try:
            quote_data = self._dao.get_by_id(record_id)
            return Quote.from_dict(quote_data) if quote_data else None

        except Exception as e:
            raise ServiceError(f"获取报价失败: {e}") from e

    def _perform_update(self, record_id: int, data: dict[str, Any]) -> Quote:
        """执行更新报价操作"""
        try:
            # 获取现有报价
            existing_quote = self._perform_get_by_id(record_id)
            if not existing_quote:
                raise BusinessLogicError("报价不存在")

            # 检查业务规则
            if existing_quote.quote_status in [
                QuoteStatus.ACCEPTED,
                QuoteStatus.CONVERTED,
            ]:
                # 已接受或已转换的报价不能修改关键信息
                restricted_fields = ["items", "total_amount", "customer_name"]
                if any(field in data for field in restricted_fields):
                    raise BusinessLogicError("已接受的报价不能修改关键信息")

            # 更新数据
            updated_data = existing_quote.to_dict()
            updated_data.update(data)
            updated_data["updated_at"] = datetime.now()

            # 重新计算总金额（如果项目有变化）
            if "items" in data:
                total_amount = sum(
                    float(item.get("unit_price", 0)) * float(item.get("quantity", 0))
                    for item in updated_data["items"]
                )
                updated_data["total_amount"] = total_amount

            # 保存更新
            if self._dao:
                self._dao.update(record_id, updated_data)

            return Quote.from_dict(updated_data)

        except Exception as e:
            raise ServiceError(f"更新报价失败: {e}") from e

    def _perform_delete(self, record_id: int) -> bool:
        """执行删除报价操作"""
        try:
            # 检查报价状态
            quote = self._perform_get_by_id(record_id)
            if quote and quote.quote_status in [
                QuoteStatus.ACCEPTED,
                QuoteStatus.CONVERTED,
            ]:
                raise BusinessLogicError("已接受或已转换的报价不能删除")

            # 执行删除
            if self._dao:
                return self._dao.delete(record_id)
            return False

        except Exception as e:
            raise ServiceError(f"删除报价失败: {e}") from e

    def _perform_list_all(self, filters: dict[str, Any] | None = None) -> list[Quote]:
        """执行获取所有报价操作"""
        if not self._dao:
            raise ServiceError("数据访问对象未初始化")

        try:
            quotes_data = self._dao.list_all(filters or {})
            return [Quote.from_dict(data) for data in quotes_data]

        except Exception as e:
            raise ServiceError(f"获取报价列表失败: {e}") from e

    # ==================== 辅助方法 ====================

    def _generate_quote_number(self) -> str:
        """生成报价编号"""
        today = datetime.now()
        prefix = f"QT{today.strftime('%Y%m%d')}"

        # 获取今日已有报价数量
        filters = {
            "quote_date_start": today.replace(hour=0, minute=0, second=0),
            "quote_date_end": today.replace(hour=23, minute=59, second=59),
        }

        try:
            existing_quotes = self._perform_list_all(filters)
            sequence = len(existing_quotes) + 1
            return f"{prefix}{sequence:03d}"
        except Exception:
            # 如果获取失败，使用时间戳
            return f"{prefix}{today.strftime('%H%M%S')}"

    def get_quote_by_number(self, quote_number: str) -> Quote | None:
        """根据报价编号获取报价"""
        try:
            filters = {"quote_number": quote_number}
            quotes = self._perform_list_all(filters)
            return quotes[0] if quotes else None
        except Exception as e:
            raise ServiceError(f"根据编号获取报价失败: {e}") from e

    def update_quote_status(self, quote_id: int, new_status: QuoteStatus) -> Quote:
        """更新报价状态"""
        try:
            quote = self._perform_get_by_id(quote_id)
            if not quote:
                raise BusinessLogicError("报价不存在")

            # 验证状态转换的合法性
            self._validate_status_transition(quote.quote_status, new_status)

            # 更新状态
            update_data = {
                "quote_status": new_status.value,
                "status_updated_at": datetime.now(),
            }

            return self._perform_update(quote_id, update_data)

        except Exception as e:
            raise ServiceError(f"更新报价状态失败: {e}") from e

    def _validate_status_transition(
        self, current_status: QuoteStatus, new_status: QuoteStatus
    ) -> None:
        """验证状态转换的合法性"""
        # 定义允许的状态转换
        allowed_transitions = {
            QuoteStatus.DRAFT: [QuoteStatus.SENT, QuoteStatus.CANCELLED],
            QuoteStatus.SENT: [
                QuoteStatus.ACCEPTED,
                QuoteStatus.REJECTED,
                QuoteStatus.EXPIRED,
            ],
            QuoteStatus.ACCEPTED: [QuoteStatus.CONVERTED],
            QuoteStatus.REJECTED: [],  # 拒绝状态不能转换
            QuoteStatus.EXPIRED: [QuoteStatus.CANCELLED],
            QuoteStatus.CONVERTED: [],  # 已转换状态不能转换
            QuoteStatus.CANCELLED: [],  # 已取消状态不能转换
        }

        if new_status not in allowed_transitions.get(current_status, []):
            raise BusinessLogicError(
                f"不能从状态 {current_status.value} 转换到 {new_status.value}"
            )
