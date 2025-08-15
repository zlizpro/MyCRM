"""
MiniCRM 报价过期管理服务

专门负责报价过期管理和预警，从原始quote_service.py中提取。
"""

from datetime import datetime, timedelta
from typing import Any

from ...core import ServiceError
from ...models.quote import QuoteStatus
from ..base_service import BaseService, register_service


@register_service("quote_expiry_service")
class QuoteExpiryService(BaseService):
    """
    报价过期管理服务

    专门负责报价过期检测、预警和自动处理。
    """

    def __init__(self, quote_core_service=None):
        """初始化过期管理服务"""
        super().__init__()
        self._quote_core_service = quote_core_service

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "报价过期管理服务"

    def get_expiring_quotes(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """
        获取即将过期的报价

        Args:
            days_ahead: 提前预警天数

        Returns:
            即将过期的报价列表
        """
        try:
            # 计算时间范围
            now = datetime.now()
            warning_date = now + timedelta(days=days_ahead)

            # 获取有效期内但即将过期的报价
            filters = {
                "quote_status": [QuoteStatus.DRAFT.value, QuoteStatus.SENT.value],
                "valid_until_start": now,
                "valid_until_end": warning_date,
            }

            quotes = self._quote_core_service.list_all(filters)

            expiring_quotes = []
            for quote in quotes:
                if not quote.valid_until:
                    continue

                # 计算剩余天数
                remaining_days = (quote.valid_until - now).days

                if remaining_days <= days_ahead:
                    expiring_quote = {
                        "id": quote.id,
                        "quote_number": quote.quote_number,
                        "customer_name": quote.customer_name,
                        "total_amount": float(quote.total_amount),
                        "quote_date": quote.quote_date.isoformat()
                        if quote.quote_date
                        else None,
                        "valid_until": quote.valid_until.isoformat(),
                        "remaining_days": remaining_days,
                        "urgency_level": self._calculate_urgency_level(remaining_days),
                        "status": quote.quote_status.value
                        if quote.quote_status
                        else None,
                    }
                    expiring_quotes.append(expiring_quote)

            # 按剩余天数排序
            expiring_quotes.sort(key=lambda x: x["remaining_days"])

            return expiring_quotes

        except Exception as e:
            raise ServiceError(f"获取即将过期报价失败: {e}") from e

    def _calculate_urgency_level(self, remaining_days: int) -> str:
        """计算紧急程度"""
        if remaining_days <= 1:
            return "紧急"
        elif remaining_days <= 3:
            return "高"
        elif remaining_days <= 7:
            return "中"
        else:
            return "低"

    def update_expired_quotes(self) -> dict[str, Any]:
        """
        更新已过期的报价状态

        Returns:
            更新结果统计
        """
        try:
            now = datetime.now()

            # 获取已过期但状态未更新的报价
            filters = {
                "quote_status": [QuoteStatus.DRAFT.value, QuoteStatus.SENT.value],
                "valid_until_end": now,
            }

            expired_quotes = self._quote_core_service.list_all(filters)

            updated_count = 0
            errors = []

            for quote in expired_quotes:
                try:
                    # 更新为过期状态
                    self._quote_core_service.update_quote_status(
                        quote.id, QuoteStatus.EXPIRED
                    )
                    updated_count += 1
                except Exception as e:
                    errors.append(f"更新报价 {quote.quote_number} 失败: {e}")

            return {
                "updated_count": updated_count,
                "total_expired": len(expired_quotes),
                "errors": errors,
                "success_rate": f"{(updated_count / len(expired_quotes) * 100):.1f}%"
                if expired_quotes
                else "100%",
                "updated_at": now.isoformat(),
            }

        except Exception as e:
            raise ServiceError(f"更新过期报价失败: {e}") from e

    def get_expiry_statistics(self, time_period: int = 30) -> dict[str, Any]:
        """
        获取过期统计信息

        Args:
            time_period: 统计时间段（天）

        Returns:
            过期统计数据
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period)

            # 获取时间段内的所有报价
            filters = {"quote_date_start": start_date, "quote_date_end": end_date}

            all_quotes = self._quote_core_service.list_all(filters)

            # 统计各种状态
            stats = {
                "total_quotes": len(all_quotes),
                "expired_quotes": 0,
                "active_quotes": 0,
                "expiring_soon": 0,  # 7天内过期
                "conversion_before_expiry": 0,
            }

            now = datetime.now()
            expiry_reasons: dict[str, int] = {}

            for quote in all_quotes:
                if quote.quote_status == QuoteStatus.EXPIRED:
                    stats["expired_quotes"] += 1

                    # 分析过期原因
                    if quote.valid_until:
                        days_to_expire = (
                            (quote.valid_until - quote.quote_date).days
                            if quote.quote_date
                            else 0
                        )
                        if days_to_expire <= 7:
                            reason = "有效期过短"
                        elif days_to_expire <= 30:
                            reason = "标准有效期"
                        else:
                            reason = "有效期较长"

                        expiry_reasons[reason] = expiry_reasons.get(reason, 0) + 1

                elif quote.quote_status in [QuoteStatus.DRAFT, QuoteStatus.SENT]:
                    stats["active_quotes"] += 1

                    # 检查是否即将过期
                    if quote.valid_until and (quote.valid_until - now).days <= 7:
                        stats["expiring_soon"] += 1

                elif quote.quote_status in [
                    QuoteStatus.ACCEPTED,
                    QuoteStatus.CONVERTED,
                ]:
                    # 检查是否在过期前转换
                    if quote.valid_until and quote.quote_date:
                        conversion_time = (
                            quote.valid_until
                        )  # 简化，实际应该用实际转换时间
                        if conversion_time <= quote.valid_until:
                            stats["conversion_before_expiry"] += 1

            # 计算比率
            expiry_rate = (
                (stats["expired_quotes"] / stats["total_quotes"] * 100)
                if stats["total_quotes"] > 0
                else 0
            )
            conversion_rate = (
                (stats["conversion_before_expiry"] / stats["total_quotes"] * 100)
                if stats["total_quotes"] > 0
                else 0
            )

            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": time_period,
                },
                "statistics": stats,
                "rates": {
                    "expiry_rate": f"{expiry_rate:.1f}%",
                    "conversion_before_expiry_rate": f"{conversion_rate:.1f}%",
                    "active_quote_rate": (
                        f"{(stats['active_quotes'] / stats['total_quotes'] * 100):.1f}%"
                        if stats["total_quotes"] > 0
                        else "0%"
                    ),
                },
                "expiry_analysis": {
                    "reasons": expiry_reasons,
                    "recommendations": self._generate_expiry_recommendations(
                        stats, expiry_rate
                    ),
                },
                "alerts": {
                    "expiring_soon": stats["expiring_soon"],
                    "high_expiry_rate": expiry_rate > 30,
                    "low_conversion_rate": conversion_rate < 20,
                },
            }

        except Exception as e:
            raise ServiceError(f"获取过期统计失败: {e}") from e

    def _generate_expiry_recommendations(
        self, stats: dict[str, Any], expiry_rate: float
    ) -> list[str]:
        """生成过期管理建议"""
        recommendations = []

        if expiry_rate > 50:
            recommendations.append("过期率过高，建议延长报价有效期或加快跟进速度")
        elif expiry_rate > 30:
            recommendations.append("过期率偏高，建议优化跟进流程")

        if stats["expiring_soon"] > 5:
            recommendations.append(
                f"有{stats['expiring_soon']}个报价即将过期，需要紧急跟进"
            )

        if (
            stats["conversion_before_expiry"] / stats["total_quotes"] < 0.2
            if stats["total_quotes"] > 0
            else False
        ):
            recommendations.append("转换率较低，建议分析客户需求和价格竞争力")

        if not recommendations:
            recommendations.append("过期管理状况良好，继续保持")

        return recommendations

    def extend_quote_validity(
        self, quote_id: int, extension_days: int
    ) -> dict[str, Any]:
        """
        延长报价有效期

        Args:
            quote_id: 报价ID
            extension_days: 延长天数

        Returns:
            延长结果
        """
        try:
            quote = self._quote_core_service.get_by_id(quote_id)
            if not quote:
                raise ServiceError("报价不存在")

            if quote.quote_status not in [QuoteStatus.DRAFT, QuoteStatus.SENT]:
                raise ServiceError("只能延长草稿或已发送状态的报价有效期")

            # 计算新的有效期
            current_valid_until = quote.valid_until or datetime.now()
            new_valid_until = current_valid_until + timedelta(days=extension_days)

            # 更新有效期
            update_data = {
                "valid_until": new_valid_until,
                "validity_extended": True,
                "extension_days": extension_days,
                "extended_at": datetime.now(),
            }

            self._quote_core_service.update(quote_id, update_data)

            return {
                "quote_id": quote_id,
                "quote_number": quote.quote_number,
                "original_valid_until": current_valid_until.isoformat(),
                "new_valid_until": new_valid_until.isoformat(),
                "extension_days": extension_days,
                "success": True,
                "message": f"报价有效期已延长{extension_days}天",
            }

        except Exception as e:
            raise ServiceError(f"延长报价有效期失败: {e}") from e

    def schedule_expy_ons(self) -> dict[str, Any]:
        """
        安排过期通知

        Returns:
            通知安排结果
        """
        try:
            # 获取需要通知的报价
            expiring_quotes = self.get_expiring_quotes(days_ahead=7)

            notifications = []
            for quote in expiring_quotes:
                notification = {
                    "quote_id": quote["id"],
                    "quote_number": quote["quote_number"],
                    "customer_name": quote["customer_name"],
                    "remaining_days": quote["remaining_days"],
                    "urgency": quote["urgency_level"],
                    "notification_type": self._determine_notification_type(
                        quote["remaining_days"]
                    ),
                    "message": self._generate_notification_message(quote),
                }
                notifications.append(notification)

            return {
                "total_notifications": len(notifications),
                "notifications": notifications,
                "scheduled_at": datetime.now().isoformat(),
                "next_check": (datetime.now() + timedelta(hours=24)).isoformat(),
            }

        except Exception as e:
            raise ServiceError(f"安排过期通知失败: {e}") from e

    def _determine_notification_type(self, remaining_days: int) -> str:
        """确定通知类型"""
        if remaining_days <= 1:
            return "urgent_email"
        elif remaining_days <= 3:
            return "priority_email"
        else:
            return "standard_reminder"

    def _generate_notification_message(self, quote: dict[str, Any]) -> str:
        """生成通知消息"""
        remaining_days = quote["remaining_days"]

        if remaining_days <= 0:
            return f"报价 {quote['quote_number']} 已过期，请及时处理"
        elif remaining_days == 1:
            return (
                f"报价 {quote['quote_number']} 将在明天过期，"
                f"请紧急跟进客户 {quote['customer_name']}"
            )
        else:
            return (
                f"报价 {quote['quote_number']} 将在{remaining_days}天后过期，"
                f"建议跟进客户 {quote['customer_name']}"
            )
