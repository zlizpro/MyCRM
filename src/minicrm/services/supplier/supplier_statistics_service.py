"""
MiniCRM 供应商统计分析服务

提供供应商统计分析功能：
- 事件统计分析
- 供应商绩效指标
- 统计报告生成
"""

from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.base_service import BaseService


class SupplierStatisticsService(BaseService):
    """
    供应商统计分析服务实现

    负责供应商统计分析相关的业务逻辑：
    - 事件统计分析
    - 绩效指标计算
    - 报告生成

    严格遵循单一职责原则。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商统计分析服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierStatisticsService"

    def get_event_statistics(
        self, supplier_id: int | None = None, time_period: int = 30
    ) -> dict[str, Any]:
        """
        获取交流事件统计信息

        Args:
            supplier_id: 供应商ID，如果为None则统计所有供应商
            time_period: 统计时间段（天）

        Returns:
            Dict[str, Any]: 统计结果

        Raises:
            ServiceError: 当统计失败时
        """
        try:
            start_date = datetime.now() - timedelta(days=time_period)

            # 获取事件数据
            if supplier_id is not None:
                events = self._supplier_dao.get_communication_events(
                    supplier_id=supplier_id, start_date=start_date
                )
            else:
                events = self._supplier_dao.get_communication_events(
                    start_date=start_date
                )

            # 统计分析
            stats: dict[str, Any] = {
                "total_events": len(events),
                "by_type": {},
                "by_status": {},
                "by_priority": {},
                "average_processing_time": 0.0,
                "satisfaction_rating": 0.0,
                "overdue_events": 0,
            }

            if not events:
                return stats

            # 按类型统计
            for event in events:
                event_type = event.get("event_type", "unknown")
                stats["by_type"][event_type] = stats["by_type"].get(event_type, 0) + 1

            # 按状态统计
            for event in events:
                status = event.get("status", "unknown")
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # 按优先级统计
            for event in events:
                priority = event.get("priority", "unknown")
                stats["by_priority"][priority] = (
                    stats["by_priority"].get(priority, 0) + 1
                )

            # 计算平均处理时间和满意度
            completed_events = [e for e in events if e.get("status") == "completed"]
            if completed_events:
                processing_times = []
                satisfaction_ratings = []

                for event in completed_events:
                    created_at = datetime.fromisoformat(event.get("created_at", ""))
                    completed_at = datetime.fromisoformat(event.get("completed_at", ""))
                    processing_time = (
                        completed_at - created_at
                    ).total_seconds() / 3600  # 小时
                    processing_times.append(processing_time)

                    # 获取满意度评分
                    satisfaction = event.get("satisfaction_rating", 0)
                    if satisfaction > 0:
                        satisfaction_ratings.append(satisfaction)

                stats["average_processing_time"] = sum(processing_times) / len(
                    processing_times
                )
                if satisfaction_ratings:
                    stats["satisfaction_rating"] = sum(satisfaction_ratings) / len(
                        satisfaction_ratings
                    )

            # 统计超时事件
            now = datetime.now()
            for event in events:
                if event.get("status") not in ["completed", "closed"]:
                    due_time = datetime.fromisoformat(event.get("due_time", ""))
                    if now > due_time:
                        stats["overdue_events"] += 1

            return stats

        except Exception as e:
            self._logger.error(f"获取事件统计失败: {e}")
            raise ServiceError(f"获取事件统计失败: {e}") from e

    def get_supplier_performance_metrics(
        self, supplier_id: int, time_period: int = 90
    ) -> dict[str, Any]:
        """
        获取供应商绩效指标

        Args:
            supplier_id: 供应商ID
            time_period: 统计时间段（天）

        Returns:
            Dict[str, Any]: 绩效指标

        Raises:
            ServiceError: 当获取失败时
        """
        try:
            start_date = datetime.now() - timedelta(days=time_period)

            # 获取供应商基本信息
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise ServiceError(f"供应商不存在: {supplier_id}")

            # 获取交易历史
            transactions = self._supplier_dao.get_transaction_history(supplier_id)

            # 获取交流事件
            events = self._supplier_dao.get_communication_events(
                supplier_id=supplier_id, start_date=start_date
            )

            # 计算绩效指标
            metrics = {
                "supplier_id": supplier_id,
                "supplier_name": supplier.get("name", ""),
                "period_days": time_period,
                "transaction_count": len(transactions),
                "event_count": len(events),
                "quality_issues": len(
                    [e for e in events if e.get("event_type") == "quality_issue"]
                ),
                "complaints": len(
                    [e for e in events if e.get("event_type") == "complaint"]
                ),
                "on_time_delivery_rate": self._calculate_delivery_rate(transactions),
                "average_response_time": self._calculate_response_time(events),
                "satisfaction_score": self._calculate_satisfaction_score(events),
                "cooperation_score": self._calculate_cooperation_score(
                    supplier_id, time_period
                ),
            }

            return metrics

        except Exception as e:
            self._logger.error(f"获取供应商绩效指标失败: {e}")
            raise ServiceError(f"获取供应商绩效指标失败: {e}") from e

    def generate_supplier_report(
        self, supplier_id: int, report_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        生成供应商报告

        Args:
            supplier_id: 供应商ID
            report_type: 报告类型 (comprehensive, quality, performance)

        Returns:
            Dict[str, Any]: 报告数据

        Raises:
            ServiceError: 当生成失败时
        """
        try:
            # 获取基础数据
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise ServiceError(f"供应商不存在: {supplier_id}")

            report = {
                "supplier_id": supplier_id,
                "supplier_name": supplier.get("name", ""),
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
            }

            if report_type in ["comprehensive", "performance"]:
                # 添加绩效数据
                report["performance_metrics"] = self.get_supplier_performance_metrics(
                    supplier_id
                )

            if report_type in ["comprehensive", "quality"]:
                # 添加质量数据 (需要质量服务支持)
                report["quality_assessment"] = {"note": "质量评估数据需要质量服务支持"}

            if report_type == "comprehensive":
                # 添加统计数据
                report["statistics"] = self.get_event_statistics(supplier_id)

            return report

        except Exception as e:
            self._logger.error(f"生成供应商报告失败: {e}")
            raise ServiceError(f"生成供应商报告失败: {e}") from e

    def _calculate_delivery_rate(self, transactions: list[dict[str, Any]]) -> float:
        """计算准时交付率"""
        if not transactions:
            return 0.0

        on_time_count = sum(
            1 for t in transactions if t.get("delivery_status") == "on_time"
        )
        return (on_time_count / len(transactions)) * 100

    def _calculate_response_time(self, events: list[dict[str, Any]]) -> float:
        """计算平均响应时间（小时）"""
        if not events:
            return 0.0

        response_times = []
        for event in events:
            if event.get("status") in ["completed", "closed"]:
                created_at = datetime.fromisoformat(event.get("created_at", ""))
                completed_at = datetime.fromisoformat(event.get("completed_at", ""))
                response_time = (completed_at - created_at).total_seconds() / 3600
                response_times.append(response_time)

        return sum(response_times) / len(response_times) if response_times else 0.0

    def _calculate_satisfaction_score(self, events: list[dict[str, Any]]) -> float:
        """计算满意度评分"""
        ratings = [
            event.get("satisfaction_rating", 0)
            for event in events
            if event.get("satisfaction_rating", 0) > 0
        ]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def _calculate_cooperation_score(self, supplier_id: int, time_period: int) -> float:
        """计算合作评分"""
        # 这里应该基于合作历史、合同履行等计算
        # 暂时返回默认值
        return 75.0
