"""
MiniCRM 供应商服务重构后的单元测试

验证拆分后的供应商服务功能正常：
- 服务协调器功能
- 各子服务的基本功能
- 模块化架构的正确性
"""

import unittest
from unittest.mock import Mock, patch

from minicrm.services.supplier import (
    CommunicationEventType,
    EventPriority,
    EventStatus,
    SupplierCoreService,
    SupplierEventService,
    SupplierQualityService,
    SupplierStatisticsService,
    SupplierTaskService,
)
from minicrm.services.supplier_service import SupplierService


class TestSupplierServiceRefactored(unittest.TestCase):
    """测试重构后的供应商服务"""

    def setUp(self):
        """测试准备"""
        self.mock_dao = Mock()
        self.supplier_service = SupplierService(self.mock_dao)

    def test_service_initialization(self):
        """测试服务初始化"""
        # 验证协调器正确初始化了所有子服务
        self.assertIsInstance(self.supplier_service.core, SupplierCoreService)
        self.assertIsInstance(self.supplier_service.quality, SupplierQualityService)
        self.assertIsInstance(self.supplier_service.events, SupplierEventService)
        self.assertIsInstance(
            self.supplier_service.statistics, SupplierStatisticsService
        )
        self.assertIsInstance(self.supplier_service.tasks, SupplierTaskService)

    def test_service_delegation(self):
        """测试服务委托功能"""
        # 测试核心服务委托
        with patch.object(self.supplier_service.core, "create_supplier") as mock_create:
            mock_create.return_value = 123
            result = self.supplier_service.create_supplier({"name": "测试供应商"})
            self.assertEqual(result, 123)
            mock_create.assert_called_once_with({"name": "测试供应商"})

    def test_enum_imports(self):
        """测试枚举类型导入"""
        # 验证枚举类型可以正常使用
        self.assertEqual(CommunicationEventType.QUALITY_ISSUE.value, "quality_issue")
        self.assertEqual(EventStatus.PENDING.value, "pending")
        self.assertEqual(EventPriority.HIGH.value, "high")

    def test_service_names(self):
        """测试服务名称"""
        self.assertEqual(self.supplier_service.get_service_name(), "SupplierService")
        self.assertEqual(
            self.supplier_service.core.get_service_name(), "SupplierCoreService"
        )
        self.assertEqual(
            self.supplier_service.quality.get_service_name(), "SupplierQualityService"
        )

    @patch("minicrm.services.supplier.supplier_core_service.validate_supplier_data")
    def test_core_service_validation(self, mock_validate):
        """测试核心服务的验证功能"""
        # 模拟验证成功
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validate.return_value = mock_validation_result

        # 模拟DAO操作
        self.mock_dao.get_by_id.return_value = None  # 供应商不存在
        self.mock_dao.search_by_name_or_contact.return_value = []  # 无重复
        self.mock_dao.insert.return_value = 456

        # 测试创建供应商
        supplier_data = {"name": "新供应商", "phone": "13800138000"}
        result = self.supplier_service.core.create_supplier(supplier_data)

        self.assertEqual(result, 456)
        mock_validate.assert_called_once_with(supplier_data)

    def test_quality_service_grade_determination(self):
        """测试质量服务的等级确定功能"""
        quality_service = self.supplier_service.quality

        # 测试不同评分对应的等级
        self.assertEqual(quality_service._determine_supplier_grade(95), "战略供应商")
        self.assertEqual(quality_service._determine_supplier_grade(85), "重要供应商")
        self.assertEqual(quality_service._determine_supplier_grade(75), "普通供应商")
        self.assertEqual(quality_service._determine_supplier_grade(65), "备选供应商")

    def test_event_service_priority_determination(self):
        """测试事件服务的优先级确定功能"""
        event_service = self.supplier_service.events

        # 测试质量问题的优先级
        quality_issue_data = {"event_type": "quality_issue", "urgency_level": "urgent"}
        priority = event_service._determine_event_priority(quality_issue_data)
        self.assertEqual(priority, EventPriority.URGENT)

        # 测试普通询价的优先级
        inquiry_data = {"event_type": "inquiry", "urgency_level": "medium"}
        priority = event_service._determine_event_priority(inquiry_data)
        self.assertEqual(priority, EventPriority.MEDIUM)

    def test_statistics_service_calculations(self):
        """测试统计服务的计算功能"""
        stats_service = self.supplier_service.statistics

        # 测试准时交付率计算
        transactions = [
            {"delivery_status": "on_time"},
            {"delivery_status": "on_time"},
            {"delivery_status": "delayed"},
        ]
        rate = stats_service._calculate_delivery_rate(transactions)
        self.assertAlmostEqual(rate, 66.67, places=1)

        # 测试空交易列表
        empty_rate = stats_service._calculate_delivery_rate([])
        self.assertEqual(empty_rate, 0.0)

    def test_handle_quality_issue_workflow(self):
        """测试质量问题处理完整工作流"""
        # 模拟DAO返回
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "测试供应商"}
        self.mock_dao.insert_communication_event.return_value = 100

        # 模拟事件服务和任务服务
        with (
            patch.object(
                self.supplier_service.events, "create_communication_event"
            ) as mock_create_event,
            patch.object(
                self.supplier_service.tasks, "create_follow_up_task"
            ) as mock_create_task,
            patch.object(
                self.supplier_service.quality, "evaluate_supplier_quality"
            ) as mock_evaluate,
        ):
            mock_create_event.return_value = 100
            mock_create_task.return_value = 200
            mock_evaluate.return_value = {"quality_score": 75}

            # 执行质量问题处理
            issue_data = {
                "title": "产品质量问题",
                "description": "发现产品缺陷",
                "urgency": "high",
                "reporter": "质检员",
            }

            result = self.supplier_service.handle_quality_issue(1, issue_data)

            # 验证结果
            self.assertEqual(result["status"], "created")
            self.assertEqual(result["event_id"], 100)
            self.assertEqual(result["task_id"], 200)
            self.assertIn("quality_assessment", result)

    def test_supplier_overview_integration(self):
        """测试供应商概览集成功能"""
        # 模拟各种数据
        self.mock_dao.get_by_id.return_value = {"id": 1, "name": "测试供应商"}

        with (
            patch.object(
                self.supplier_service.quality, "evaluate_supplier_quality"
            ) as mock_quality,
            patch.object(
                self.supplier_service.statistics, "get_supplier_performance_metrics"
            ) as mock_metrics,
            patch.object(
                self.supplier_service.statistics, "get_event_statistics"
            ) as mock_stats,
            patch.object(
                self.supplier_service.tasks, "get_pending_tasks"
            ) as mock_tasks,
        ):
            mock_quality.return_value = {"quality_score": 85}
            mock_metrics.return_value = {"performance_score": 80}
            mock_stats.return_value = {"total_events": 5}
            mock_tasks.return_value = [{"id": 1, "title": "跟进任务"}]

            # 获取供应商概览
            overview = self.supplier_service.get_supplier_overview(1)

            # 验证概览包含所有必要信息
            self.assertIn("basic_info", overview)
            self.assertIn("quality_assessment", overview)
            self.assertIn("performance_metrics", overview)
            self.assertIn("recent_events", overview)
            self.assertIn("pending_tasks", overview)


class TestModularArchitecture(unittest.TestCase):
    """测试模块化架构"""

    def test_file_size_compliance(self):
        """测试文件大小合规性"""
        import os

        # 定义文件大小限制
        limits = {
            "supplier_core_service.py": 300,
            "supplier_quality_service.py": 250,
            "supplier_event_service.py": 500,  # 事件服务相对复杂，允许更大
            "supplier_statistics_service.py": 350,
            "supplier_task_service.py": 250,
            "supplier_enums.py": 100,
        }

        base_path = "src/minicrm/services/supplier"

        for filename, max_lines in limits.items():
            filepath = os.path.join(base_path, filename)
            if os.path.exists(filepath):
                with open(filepath, encoding="utf-8") as f:
                    line_count = len(f.readlines())

                self.assertLessEqual(
                    line_count,
                    max_lines,
                    f"{filename} 有 {line_count} 行，超过限制 {max_lines} 行",
                )

    def test_import_structure(self):
        """测试导入结构"""
        # 测试可以正确导入所有模块
        try:
            from minicrm.services.supplier import (
                CommunicationEventType,
                EventPriority,
                EventStatus,
                SupplierCoreService,
                SupplierEventService,
                SupplierQualityService,
                SupplierStatisticsService,
                SupplierTaskService,
            )

            # 如果能执行到这里，说明导入成功
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"导入失败: {e}")

    def test_service_independence(self):
        """测试服务独立性"""
        # 每个服务都应该能够独立实例化
        moMoc

        services = [
            SupplierCoreService(mock_dao),
            SupplierQualityService(mock_dao),
            SupplierEventService(mock_dao),
            SupplierStatisticsService(mock_dao),
            SupplierTaskService(mock_dao),
        ]

        # 验证每个服务都有正确的服务名称
        expected_names = [
            "SupplierCoreService",
            "SupplierQualityService",
            "SupplierEventService",
            "SupplierStatisticsService",
            "SupplierTaskService",
        ]

        for service, expected_name in zip(services, expected_names, strict=False):
            self.assertEqual(service.get_service_name(), expected_name)


if __name__ == "__main__":
    unittest.main()
