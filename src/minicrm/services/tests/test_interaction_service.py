"""MiniCRM 互动服务单元测试.

测试互动记录和任务管理服务的所有功能,包括:
- 互动记录的CRUD操作
- 任务管理功能
- 时间线视图数据处理
- 提醒和通知功能
- transfunctions集成

遵循测试最佳实践:
- 使用Mock对象隔离依赖
- 测试覆盖正常和异常情况
- 验证transfunctions的正确使用
"""

from datetime import datetime, timedelta, timezone
import unittest
from unittest.mock import MagicMock, patch

from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from minicrm.models.interaction import InteractionStatus, InteractionType, Priority
from minicrm.services.interaction_service import InteractionService


class TestInteractionService(unittest.TestCase):
    """互动服务测试类."""

    def setUp(self):
        """测试准备."""
        self.mock_dao = MagicMock()
        self.service = InteractionService(self.mock_dao)

    def test_create_interaction_success(self):
        """测试创建互动记录成功."""
        # 准备测试数据
        interaction_data = {
            "party_name": "测试客户",
            "subject": "电话沟通",
            "interaction_type": InteractionType.PHONE_CALL.value,
            "scheduled_date": (
                datetime.now(timezone.utc) + timedelta(hours=1)
            ).isoformat(),
        }

        # 模拟DAO返回
        self.mock_dao.insert.return_value = 1
        self.mock_dao.search.return_value = []  # 无时间冲突

        # 执行测试
        result = self.service.create_interaction(interaction_data)

        # 验证结果
        assert result == 1
        self.mock_dao.insert.assert_called_once()

    def test_create_interaction_validation_error(self):
        """测试创建互动记录验证错误."""
        # 准备无效数据(缺少必填字段)
        interaction_data = {"subject": "没有关联方的互动"}

        # 执行测试并验证异常
        try:
            self.service.create_interaction(interaction_data)
            assert False, "应该抛出ValidationError异常"
        except ValidationError as e:
            assert "party_name" in str(e)

    def test_create_interaction_time_conflict(self):
        """测试创建互动记录时间冲突"""
        # 准备测试数据(高优先级)
        interaction_data = {
            "party_name": "测试客户",
            "subject": "重要会议",
            "interaction_type": InteractionType.MEETING.value,
            "priority": Priority.HIGH.value,
            "scheduled_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        # 模拟存在时间冲突
        self.mock_dao.search.return_value = [{"id": 1, "subject": "冲突的互动"}]

        # 执行测试并验证异常
        with self.assertRaises(BusinessLogicError) as context:
            self.service.create_interaction(interaction_data)

        self.assertIn("时间冲突", str(context.exception))

    def test_update_interaction_success(self):
        """测试更新互动记录成功"""
        # 准备测试数据
        interaction_id = 1
        update_data = {"subject": "更新后的标题"}

        # 模拟DAO返回
        self.mock_dao.get_by_id.return_value = {"id": 1, "subject": "原标题"}
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.service.update_interaction(interaction_id, update_data)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    def test_complete_interaction_success(self):
        """测试完成互动记录成功"""
        # 准备测试数据
        interaction_id = 1
        outcome = "沟通顺利"

        # 模拟DAO返回
        mock_interaction_data = {
            "id": 1,
            "subject": "测试互动",
            "interaction_status": InteractionStatus.PLANNED.value,
            "scheduled_date": datetime.now().isoformat(),
        }
        self.mock_dao.get_by_id.return_value = mock_interaction_data
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.service.complete_interaction(interaction_id, outcome)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    def test_get_pending_reminders(self):
        """测试获取待处理提醒"""
        # 准备测试数据
        mock_interactions = [
            {
                "id": 1,
                "subject": "需要提醒的互动",
                "reminder_enabled": True,
                "interaction_status": InteractionStatus.PLANNED.value,
                "scheduled_date": (datetime.now() + timedelta(minutes=30)).isoformat(),
            }
        ]

        # 模拟DAO返回
        self.mock_dao.search.return_value = mock_interactions

        # 执行测试
        result = self.service.get_pending_reminders()

        # 验证结果
        self.assertIsInstance(result, list)
        self.mock_dao.search.assert_called_once()

    def test_get_overdue_interactions(self):
        """测试获取逾期互动记录"""
        # 准备测试数据
        mock_interactions = [
            {
                "id": 1,
                "subject": "逾期的互动",
                "interaction_status": InteractionStatus.PLANNED.value,
                "scheduled_date": (datetime.now() - timedelta(days=1)).isoformat(),
            }
        ]

        # 模拟DAO返回
        self.mock_dao.search.return_value = mock_interactions

        # 执行测试
        result = self.service.get_overdue_interactions()

        # 验证结果
        self.assertIsInstance(result, list)
        self.mock_dao.search.assert_called_once()

    def test_search_interactions(self):
        """测试搜索互动记录"""
        # 准备测试数据
        query = "电话"
        filters = {"interaction_type": InteractionType.PHONE_CALL.value}

        # 模拟分页搜索结果
        mock_result = MagicMock()
        mock_result.items = [{"id": 1, "subject": "电话沟通"}]
        mock_result.total = 1

        with patch(
            "minicrm.services.interaction_service.paginated_search_template",
            return_value=mock_result,
        ):
            # 执行测试
            items, total = self.service.search_interactions(query, filters)

            # 验证结果
            self.assertEqual(len(items), 1)
            self.assertEqual(total, 1)
            self.assertEqual(items[0]["subject"], "电话沟通")

    def test_get_timeline_data(self):
        """测试获取时间线数据"""
        # 准备测试数据
        party_id = 1
        party_type = "customer"

        # 模拟互动记录
        mock_interactions = [
            {
                "id": 1,
                "subject": "第一次沟通",
                "interaction_type": InteractionType.PHONE_CALL.value,
                "interaction_status": InteractionStatus.COMPLETED.value,
                "scheduled_date": (datetime.now() - timedelta(days=10)).isoformat(),
                "content": "讨论了产品需求",
            },
            {
                "id": 2,
                "subject": "跟进会议",
                "interaction_type": InteractionType.MEETING.value,
                "interaction_status": InteractionStatus.PLANNED.value,
                "scheduled_date": (datetime.now() + timedelta(days=5)).isoformat(),
                "content": "安排产品演示",
            },
        ]

        # 模拟DAO返回
        self.mock_dao.search.return_value = mock_interactions

        # 执行测试
        result = self.service.get_timeline_data(party_id, party_type)

        # 验证结果
        self.assertEqual(result["party_id"], party_id)
        self.assertEqual(result["party_type"], party_type)
        self.assertEqual(result["total_interactions"], 2)
        self.assertIn("timeline", result)
        self.assertIn("statistics", result)
        self.assertEqual(len(result["timeline"]), 2)

    def test_create_task_success(self):
        """测试创建任务成功"""
        # 准备测试数据
        task_data = {
            "title": "跟进客户需求",
            "description": "了解客户的具体需求",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "party_id": 1,
        }

        # 模拟DAO返回
        self.mock_dao.insert.return_value = 1

        # 执行测试
        result = self.service.create_task(task_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.mock_dao.insert.assert_called_once()

    def test_get_pending_tasks(self):
        """测试获取待办任务"""
        # 准备测试数据
        mock_tasks = [
            {
                "id": 1,
                "subject": "跟进客户",
                "interaction_type": InteractionType.FOLLOW_UP.value,
                "follow_up_required": True,
                "interaction_status": InteractionStatus.PLANNED.value,
            }
        ]

        # 模拟DAO返回
        self.mock_dao.search.return_value = mock_tasks

        # 执行测试
        result = self.service.get_pending_tasks()

        # 验证结果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["subject"], "跟进客户")

    def test_complete_task_success(self):
        """测试完成任务成功"""
        # 准备测试数据
        task_id = 1
        completion_notes = "任务已完成"

        # 模拟DAO返回
        mock_task_data = {
            "id": 1,
            "subject": "测试任务",
            "interaction_status": InteractionStatus.PLANNED.value,
            "follow_up_required": True,
        }
        self.mock_dao.get_by_id.return_value = mock_task_data
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.service.complete_task(task_id, completion_notes)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    def test_get_notification_reminders(self):
        """测试获取通知提醒"""
        # 模拟待处理提醒
        mock_pending = [
            {
                "id": 1,
                "subject": "重要会议",
                "priority": Priority.HIGH.value,
                "scheduled_date": (datetime.now() + timedelta(hours=1)).isoformat(),
                "party_name": "重要客户",
            }
        ]

        # 模拟逾期互动
        mock_overdue = [
            {
                "id": 2,
                "subject": "逾期跟进",
                "scheduled_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "party_name": "普通客户",
            }
        ]

        # 模拟方法返回
        self.service.get_pending_reminders = MagicMock(return_value=mock_pending)
        self.service.get_overdue_interactions = MagicMock(return_value=mock_overdue)

        # 执行测试
        result = self.service.get_notification_reminders()

        # 验证结果
        self.assertEqual(len(result), 2)

        # 验证提醒通知
        reminder_notification = next(
            (n for n in result if n["type"] == "reminder"), None
        )
        self.assertIsNotNone(reminder_notification)
        self.assertEqual(reminder_notification["interaction_id"], 1)

        # 验证逾期通知
        overdue_notification = next((n for n in result if n["type"] == "overdue"), None)
        self.assertIsNotNone(overdue_notification)
        self.assertEqual(overdue_notification["interaction_id"], 2)

    def test_validate_interaction_data_valid(self):
        """测试有效数据验证"""
        # 准备有效数据
        valid_data = {
            "party_name": "测试客户",
            "subject": "有效的互动",
            "interaction_type": InteractionType.PHONE_CALL.value,
            "scheduled_date": (datetime.now() + timedelta(hours=1)).isoformat(),
            "duration_minutes": 30,
        }

        # 执行验证(不应抛出异常)
        try:
            self.service._validate_interaction_data(valid_data)
        except ValidationError:
            self.fail("有效数据验证失败")

    def test_validate_interaction_data_invalid_date(self):
        """测试无效日期验证"""
        # 测试过去时间
        with self.assertRaises(ValidationError):
            self.service._validate_interaction_data(
                {
                    "party_name": "测试客户",
                    "subject": "测试",
                    "interaction_type": InteractionType.PHONE_CALL.value,
                    "scheduled_date": (datetime.now() - timedelta(days=1)).isoformat(),
                }
            )

    def test_validate_interaction_data_invalid_duration(self):
        """测试无效持续时间验证"""
        # 测试负数持续时间
        with self.assertRaises(ValidationError):
            self.service._validate_interaction_data(
                {
                    "party_name": "测试客户",
                    "subject": "测试",
                    "interaction_type": InteractionType.PHONE_CALL.value,
                    "duration_minutes": -10,
                }
            )

    def test_apply_interaction_defaults(self):
        """测试应用默认值"""
        # 准备测试数据
        data = {"party_name": "测试客户", "subject": "测试互动"}

        # 执行默认值应用
        self.service._apply_interaction_defaults(data)

        # 验证默认值
        self.assertEqual(data["interaction_status"], InteractionStatus.PLANNED.value)
        self.assertEqual(data["priority"], Priority.NORMAL.value)
        self.assertEqual(data["interaction_type"], InteractionType.PHONE_CALL.value)
        self.assertEqual(data["party_type"], "customer")
        self.assertEqual(data["reminder_minutes"], 30)
        self.assertIn("created_at", data)
        self.assertIn("scheduled_date", data)

    def test_process_timeline_data(self):
        """测试处理时间线数据"""
        # 准备测试数据
        interactions = [
            {
                "id": 1,
                "subject": "电话沟通",
                "interaction_type": InteractionType.PHONE_CALL.value,
                "interaction_status": InteractionStatus.COMPLETED.value,
                "scheduled_date": "2025-01-15T10:00:00",
                "content": "讨论了产品需求和价格",
                "duration_minutes": 30,
            }
        ]

        # 执行测试
        result = self.service._process_timeline_data(interactions)

        # 验证结果
        self.assertIn("timeline", result)
        self.assertIn("statistics", result)
        self.assertEqual(len(result["timeline"]), 1)

        timeline_item = result["timeline"][0]
        self.assertEqual(timeline_item["id"], 1)
        self.assertEqual(timeline_item["subject"], "电话沟通")
        self.assertEqual(timeline_item["duration"], 30)

    def test_get_content_preview(self):
        """测试获取内容预览"""
        # 测试短内容
        short_content = "短内容"
        result = self.service._get_content_preview(short_content)
        self.assertEqual(result, "短内容")

        # 测试长内容
        long_content = "这是一个很长的内容,需要被截断以显示预览效果"
        result = self.service._get_content_preview(long_content, 10)
        self.assertEqual(result, "这是一个很长的内容,需...")

        # 测试空内容
        result = self.service._get_content_preview("")
        self.assertEqual(result, "")

    def test_calculate_overdue_days(self):
        """测试计算逾期天数"""
        # 测试逾期2天
        past_date = (datetime.now() - timedelta(days=2)).isoformat()
        result = self.service._calculate_overdue_days(past_date)
        self.assertEqual(result, 2)

        # 测试未来日期
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        result = self.service._calculate_overdue_days(future_date)
        self.assertEqual(result, 0)

        # 测试无效日期
        result = self.service._calculate_overdue_days("invalid_date")
        self.assertEqual(result, 0)

        # 测试空日期
        result = self.service._calculate_overdue_days(None)
        self.assertEqual(result, 0)

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 模拟DAO抛出异常
        self.mock_dao.insert.side_effect = Exception("数据库错误")

        # 执行测试并验证ServiceError被抛出
        with self.assertRaises(ServiceError) as context:
            self.service.create_interaction(
                {
                    "party_name": "测试客户",
                    "subject": "测试互动",
                    "interaction_type": InteractionType.PHONE_CALL.value,
                }
            )

        self.assertIn("创建互动记录失败", str(context.exception))

    def test_get_service_name(self):
        """测试获取服务名称"""
        self.assertEqual(self.service.get_service_name(), "InteractionService")


if __name__ == "__main__":
    unittest.main()
