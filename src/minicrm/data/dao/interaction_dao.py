"""
互动记录数据访问对象

提供互动记录相关的数据访问功能，包括：
- 基本CRUD操作
- 复杂查询和搜索
- 统计和分析功能
- 与transfunctions的集成

严格遵循DAO模式和数据访问层职责：
- 只处理数据访问逻辑，不包含业务逻辑
- 使用transfunctions的CRUD模板
- 提供高效的查询接口
- 文件大小控制在推荐范围内
"""

import logging
from datetime import datetime
from typing import Any

from minicrm.data.database import DatabaseManager

from .base_dao import BaseDAO


class InteractionDAO(BaseDAO):
    """
    互动记录数据访问对象

    继承自BaseDAO，提供互动记录特有的数据访问功能。
    专注于数据访问层的职责，不包含业务逻辑。
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化互动记录DAO

        Args:
            database_manager: 数据库管理器
        """
        super().__init__(database_manager, "interactions")
        self._logger = logging.getLogger(__name__)

    def get_by_party(
        self,
        party_id: int,
        party_type: str = "customer",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        根据关联方获取互动记录

        Args:
            party_id: 关联方ID
            party_type: 关联方类型
            limit: 限制数量
            offset: 偏移量

        Returns:
            List[Dict[str, Any]]: 互动记录列表
        """
        conditions = {
            "party_id": party_id,
            "party_type": party_type,
        }

        return self.search(
            conditions=conditions,
            order_by="scheduled_date DESC",
            limit=limit,
            offset=offset,
        )

    def get_recent_interactions(
        self, party_id: int, party_type: str = "customer", days: int = 30
    ) -> list[dict[str, Any]]:
        """
        获取最近的互动记录

        Args:
            party_id: 关联方ID
            party_type: 关联方类型
            days: 天数

        Returns:
            List[Dict[str, Any]]: 最近的互动记录列表
        """
        start_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - datetime.timedelta(days=days)

        conditions = {
            "party_id": party_id,
            "party_type": party_type,
            "actual_date__gte": start_date.isoformat(),
        }

        return self.search(
            conditions=conditions,
            order_by="actual_date DESC",
        )

    def get_pending_interactions(self, party_id: int = None) -> list[dict[str, Any]]:
        """
        获取待处理的互动记录

        Args:
            party_id: 关联方ID（可选）

        Returns:
            List[Dict[str, Any]]: 待处理的互动记录列表
        """
        conditions = {
            "interaction_status__in": ["planned", "in_progress"],
        }

        if party_id:
            conditions["party_id"] = party_id

        return self.search(
            conditions=conditions,
            order_by="scheduled_date ASC",
        )

    def get_overdue_interactions(self) -> list[dict[str, Any]]:
        """
        获取逾期的互动记录

        Returns:
            List[Dict[str, Any]]: 逾期的互动记录列表
        """
        current_time = datetime.now().isoformat()
        conditions = {
            "interaction_status": "planned",
            "scheduled_date__lt": current_time,
        }

        return self.search(
            conditions=conditions,
            order_by="scheduled_date ASC",
        )

    def get_interactions_by_type(
        self, interaction_type: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        根据类型获取互动记录

        Args:
            interaction_type: 互动类型
            limit: 限制数量

        Returns:
            List[Dict[str, Any]]: 指定类型的互动记录列表
        """
        conditions = {"interaction_type": interaction_type}

        return self.search(
            conditions=conditions,
            order_by="scheduled_date DESC",
            limit=limit,
        )

    def get_interactions_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        party_id: int = None,
    ) -> list[dict[str, Any]]:
        """
        根据日期范围获取互动记录

        Args:
            start_date: 开始日期
            end_date: 结束日期
            party_id: 关联方ID（可选）

        Returns:
            List[Dict[str, Any]]: 指定日期范围的互动记录列表
        """
        conditions = {
            "scheduled_date__gte": start_date.isoformat(),
            "scheduled_date__lte": end_date.isoformat(),
        }

        if party_id:
            conditions["party_id"] = party_id

        return self.search(
            conditions=conditions,
            order_by="scheduled_date ASC",
        )

    def get_follow_up_required(self) -> list[dict[str, Any]]:
        """
        获取需要跟进的互动记录

        Returns:
            List[Dict[str, Any]]: 需要跟进的互动记录列表
        """
        conditions = {
            "follow_up_required": True,
            "interaction_status": "completed",
        }

        return self.search(
            conditions=conditions,
            order_by="follow_up_date ASC",
        )

    def get_reminder_enabled(self) -> list[dict[str, Any]]:
        """
        获取启用提醒的互动记录

        Returns:
            List[Dict[str, Any]]: 启用提醒的互动记录列表
        """
        conditions = {
            "reminder_enabled": True,
            "interaction_status": "planned",
        }

        return self.search(
            conditions=conditions,
            order_by="scheduled_date ASC",
        )

    def search_by_content(
        self, query: str, party_id: int = None
    ) -> list[dict[str, Any]]:
        """
        根据内容搜索互动记录

        Args:
            query: 搜索关键词
            party_id: 关联方ID（可选）

        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        # 这里需要根据实际数据库实现全文搜索
        # 暂时使用简单的LIKE查询
        conditions = {}
        if party_id:
            conditions["party_id"] = party_id

        # 注意：这里需要根据实际数据库实现来调整搜索逻辑
        # SQLite的全文搜索需要特殊处理
        all_interactions = self.search(conditions)

        # 在内存中进行简单的文本匹配
        results = []
        query_lower = query.lower()

        for interaction in all_interactions:
            searchable_text = " ".join(
                [
                    interaction.get("subject", ""),
                    interaction.get("content", ""),
                    interaction.get("outcome", ""),
                    interaction.get("party_name", ""),
                ]
            ).lower()

            if query_lower in searchable_text:
                results.append(interaction)

        return results

    def get_interaction_statistics(
        self, party_id: int = None, days: int = 30
    ) -> dict[str, Any]:
        """
        获取互动统计信息

        Args:
            party_id: 关联方ID（可选）
            days: 统计天数

        Returns:
            Dict[str, Any]: 统计信息
        """
        start_date = datetime.now() - datetime.timedelta(days=days)
        conditions = {
            "created_at__gte": start_date.isoformat(),
        }

        if party_id:
            conditions["party_id"] = party_id

        interactions = self.search(conditions)

        # 统计各种指标
        total_count = len(interactions)
        type_counts = {}
        status_counts = {}
        priority_counts = {}

        for interaction in interactions:
            # 统计类型分布
            interaction_type = interaction.get("interaction_type", "unknown")
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1

            # 统计状态分布
            status = interaction.get("interaction_status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            # 统计优先级分布
            priority = interaction.get("priority", "unknown")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        return {
            "total_interactions": total_count,
            "type_distribution": type_counts,
            "status_distribution": status_counts,
            "priority_distribution": priority_counts,
            "period_days": days,
            "start_date": start_date.isoformat(),
        }

    def bulk_update_status(self, interaction_ids: list[int], new_status: str) -> int:
        """
        批量更新互动记录状态

        Args:
            interaction_ids: 互动记录ID列表
            new_status: 新状态

        Returns:
            int: 更新的记录数量
        """
        if not interaction_ids:
            return 0

        updated_count = 0
        update_data = {
            "interaction_status": new_status,
            "updated_at": datetime.now().isoformat(),
        }

        for interaction_id in interaction_ids:
            if self.update(interaction_id, update_data):
                updated_count += 1

        self._logger.info(f"批量更新状态完成: {updated_count}/{len(interaction_ids)}")
        return updated_count

    def delete_old_interactions(self, days: int = 365) -> int:
        """
        删除旧的互动记录

        Args:
            days: 保留天数

        Returns:
            int: 删除的记录数量
        """
        cutoff_date = datetime.now() - datetime.timedelta(days=days)
        conditions = {
            "created_at__lt": cutoff_date.isoformat(),
            "interaction_status__in": ["completed", "cancelled"],
        }

        old_interactions = self.search(conditions)
        deleted_count = 0

        for interaction in old_interactions:
            if self.delete(interaction["id"]):
                deleted_count += 1

        self._logger.info(f"清理旧互动记录完成: 删除 {deleted_count} 条记录")
        return deleted_count

    def _row_to_dict(self, row) -> dict[str, Any]:
        """
        将数据库行转换为字典

        Args:
            row: 数据库行

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        if hasattr(row, "keys"):
            return dict(row)
        else:
            # 如果是元组格式，需要提供字段映射
            # 这里需要根据实际的数据库表结构来定义字段
            fields = [
                "id",
                "party_type",
                "party_id",
                "party_name",
                "contact_person",
                "interaction_type",
                "interaction_status",
                "priority",
                "scheduled_date",
                "actual_date",
                "duration_minutes",
                "subject",
                "content",
                "outcome",
                "follow_up_required",
                "follow_up_date",
                "follow_up_notes",
                "related_quote_id",
                "related_contract_id",
                "related_order_id",
                "attachments",
                "tags",
                "reminder_enabled",
                "reminder_minutes",
                "notes",
                "created_at",
                "updated_at",
            ]

            return (
                dict(zip(fields, row, strict=False)) if len(row) == len(fields) else {}
            )
