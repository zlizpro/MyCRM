"""
互动服务单元测试

测试InteractionService的所有核心功能，包括：
- 互动记录管理
- 任务管理
- 提醒功能
- 事件跟踪
- 数据验证和异常处理
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from minicrm.core.exceptions import ServiceError
from minicrm.services.interaction_service import InteractionService
from transfunctions.validation.business import ValidationError


class TestInteractionService(unittest.TestCase):
    """互动服务测试类"""

    def setUp(self):
        """测试准备"""
        # 创建Mock DAO
        self.mock_dao = MagicMock()

        # 创建服务实例
        self.service = InteractionService(self.mock_dao)

    def test_create_interaction_success(self):
        """测试创建互动记录成功"""
        # 准备测试数据
        interaction_data = {
            "party_name": "测试客户",
            "subject": "电话沟通",
            "interaction_type": "phone_call",
            "scheduled_date": (datetime.now() + timedelta(hours=1)).isoformat(),
        }

        # 设置Mock返回值
        self.mock_dao.insert.return_value = 1

        # 执行测试
        result = self.service.create_interaction(interaction_data)

        # 验证结果
        self.assertEqual(result, 1)
        self.mock_dao.insert.assert_called_once()

    def test_create_interaction_validation_error(self):
        """测试创建互动记录验证错误"""
        # 准备无效数据（缺少必填字段）
        interaction_data = {
            "subject": "测试",
            # 缺少party_name
        }

        # 执行测试并验证异常
        with self.assertRaises(ValidationError):
            self.service.create_interaction(interaction_data)

    def test_update_interaction_success(self):
        """测试更新互动记录成功"""
        # 准备测试数据
        interaction_id = 1
        update_data = {
            "subject": "更新后的主题",
            "content": "更新后的内容",
        }

        # 设置Mock返回值
        self.mock_dao.get_by_id.return_value = {
            "id": 1,
            "party_name": "测试客户",
            "subject": "原主题",
        }
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.service.update_interaction(interaction_id, update_data)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.get_by_id.assert_called_once_with(interaction_id)
        self.mock_dao.update.assert_called_once()

    def test_complete_interaction_success(self):
        """测试完成互动记录成功"""
        # 准备测试数据
        interaction_id = 1
        outcome = "沟通顺利"

        # 设置Mock返回值
        self.mock_dao.get_by_id.return_value = {
            "id": 1,
            "party_name": "测试客户",
            "subject": "电话沟通",
            "interaction_status": "planned",
            "scheduled_date": datetime.now().isoformat(),
        }
        self.mock_dao.update.return_value = True

        # 执行测试
        result = self.service.complete_interaction(interaction_id, outcome)

        # 验证结果
        self.assertTrue(result)
        self.mock_dao.update.assert_called_once()

    def test_create_task_success(self):
        """测试创建任务成功"""
        # 准备测试数据
        task_data = {
            "title": "跟进客户需求",
            "description": "了解客户具体需求",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "party_id": 123,
            "party_name": "测试客户",
        }

        # 设置Mock返回值
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
                "subject": "跟进客户需求",
                "interaction_type": "follow_up",
                "follow_up_required": True,
                "interaction_status": "planned",
            }
        ]

        # 设置Mock返回值
        self.mock_dao.search.return_value = mock_tasks

        # 执行测试
        result = self.service.get_pending_tasks()

        # 验证结果
        self.assertEqual(result, mock_tasks)

    def test_service_error_handling(self):
        """测试服务错误处理"""
        # 设置Mock抛出异常
        self.mock_dao.insert.side_effect = Exception("数据库错误")

        # 准备测试数据
        interaction_data = {
            "party_name": "测试客户",
            "subject": "电话沟通",
            "interaction_type": "phone_call",
        }

        # 执行测试并验证异常
        with self.assertRaises(ServiceError):
            self.service.create_interaction(interaction_data)


if __name__ == "__main__":
    unittest.main()
