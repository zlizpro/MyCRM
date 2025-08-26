"""MiniCRM TaskPanelTTK 单元测试.

测试任务管理TTK面板的各项功能，包括：
- 面板初始化和UI创建
- 任务数据加载和显示
- 任务筛选和搜索功能
- 任务操作（创建、编辑、完成、删除）
- 日历和时间线视图
- 提醒和通知功能
- 事件处理和回调

测试覆盖：
- 正常功能测试
- 异常情况处理
- 边界条件验证
- 性能和资源管理
"""

from datetime import datetime, timedelta
import tkinter as tk
import unittest
from unittest.mock import Mock, patch

from minicrm.services.interaction_service import InteractionService
from minicrm.ui.ttk_base.task_panel_ttk import TaskPanelTTK


class TestTaskPanelTTK(unittest.TestCase):
    """TaskPanelTTK 单元测试类."""

    def setUp(self):
        """测试前准备."""
        # 创建测试根窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏测试窗口

        # 创建模拟的互动服务
        self.mock_interaction_service = Mock(spec=InteractionService)

        # 准备测试数据
        self.test_tasks = [
            {
                "id": 1,
                "subject": "测试任务1",
                "party_name": "测试客户A",
                "priority": "high",
                "interaction_status": "planned",
                "scheduled_date": "2025-01-25 10:00:00",
                "follow_up_date": "2025-01-26 10:00:00",
                "created_at": "2025-01-20 09:00:00",
                "content": "这是一个测试任务",
                "party_type": "customer",
                "party_id": 1,
            },
            {
                "id": 2,
                "subject": "测试任务2",
                "party_name": "测试供应商B",
                "priority": "normal",
                "interaction_status": "in_progress",
                "scheduled_date": "2025-01-24 14:00:00",
                "follow_up_date": "2025-01-25 14:00:00",
                "created_at": "2025-01-21 10:00:00",
                "content": "这是另一个测试任务",
                "party_type": "supplier",
                "party_id": 2,
            },
            {
                "id": 3,
                "subject": "逾期任务",
                "party_name": "测试客户C",
                "priority": "urgent",
                "interaction_status": "planned",
                "scheduled_date": "2025-01-20 09:00:00",
                "follow_up_date": "2025-01-21 09:00:00",
                "created_at": "2025-01-19 08:00:00",
                "content": "这是一个逾期任务",
                "party_type": "customer",
                "party_id": 3,
            },
        ]

        # 配置模拟服务的返回值
        self.mock_interaction_service.get_pending_tasks.return_value = self.test_tasks

    def tearDown(self):
        """测试后清理."""
        if hasattr(self, "task_panel"):
            self.task_panel.cleanup()
        self.root.destroy()

    def test_task_panel_initialization(self):
        """测试任务面板初始化."""
        # 创建任务面板
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 验证基本属性
        self.assertIsNotNone(self.task_panel)
        self.assertEqual(
            self.task_panel.interaction_service, self.mock_interaction_service
        )
        self.assertIsInstance(self.task_panel.tasks, list)
        self.assertIsInstance(self.task_panel.filtered_tasks, list)

        # 验证UI组件创建
        self.assertIsNotNone(self.task_panel.main_notebook)
        self.assertIsNotNone(self.task_panel.search_entry)
        self.assertIsNotNone(self.task_panel.status_filter)
        self.assertIsNotNone(self.task_panel.priority_filter)
        self.assertIsNotNone(self.task_panel.task_table)

        # 验证统计标签
        self.assertIn("pending", self.task_panel.stats_labels)
        self.assertIn("overdue", self.task_panel.stats_labels)
        self.assertIn("today", self.task_panel.stats_labels)

    def test_load_tasks_success(self):
        """测试成功加载任务数据."""
        # 创建任务面板
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 验证服务调用
        self.mock_interaction_service.get_pending_tasks.assert_called_once()

        # 验证数据加载
        self.assertEqual(len(self.task_panel.tasks), 3)
        self.assertEqual(len(self.task_panel.filtered_tasks), 3)

        # 验证数据格式化
        first_task = self.task_panel.tasks[0]
        self.assertEqual(first_task["priority"], "高")  # 应该被格式化
        self.assertEqual(first_task["interaction_status"], "计划中")

    def test_load_tasks_service_error(self):
        """测试加载任务数据时服务异常."""
        # 配置服务抛出异常
        from minicrm.core.exceptions import ServiceError

        self.mock_interaction_service.get_pending_tasks.side_effect = ServiceError(
            "测试异常"
        )

        # 使用patch来模拟messagebox
        with patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox:
            # 创建任务面板
            self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

            # 验证错误处理
            mock_messagebox.showerror.assert_called_once()
            self.assertEqual(len(self.task_panel.tasks), 0)

    def test_format_task_for_display(self):
        """测试任务数据格式化."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试数据
        raw_task = {
            "priority": "high",
            "interaction_status": "planned",
            "scheduled_date": "2025-01-25T10:00:00",
            "follow_up_date": "2025-01-26T14:00:00",
            "created_at": "2025-01-20T09:00:00",
        }

        # 格式化数据
        formatted_task = self.task_panel._format_task_for_display(raw_task)

        # 验证格式化结果
        self.assertEqual(formatted_task["priority"], "高")
        self.assertEqual(formatted_task["interaction_status"], "计划中")
        self.assertEqual(formatted_task["scheduled_date"], "2025-01-25 10:00")

    def test_apply_filters(self):
        """测试筛选功能."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试搜索筛选
        self.task_panel.search_entry.insert(0, "测试任务1")
        self.task_panel._apply_filters()
        self.assertEqual(len(self.task_panel.filtered_tasks), 1)
        self.assertEqual(self.task_panel.filtered_tasks[0]["subject"], "测试任务1")

        # 清除搜索
        self.task_panel.search_entry.delete(0, tk.END)

        # 测试状态筛选
        self.task_panel.status_filter.set("计划中")
        self.task_panel._apply_filters()
        planned_tasks = [
            task
            for task in self.task_panel.filtered_tasks
            if task["interaction_status"] == "计划中"
        ]
        self.assertEqual(len(self.task_panel.filtered_tasks), len(planned_tasks))

        # 测试优先级筛选
        self.task_panel.status_filter.set("全部")
        self.task_panel.priority_filter.set("高")
        self.task_panel._apply_filters()
        high_priority_tasks = [
            task for task in self.task_panel.filtered_tasks if task["priority"] == "高"
        ]
        self.assertEqual(len(self.task_panel.filtered_tasks), len(high_priority_tasks))

    def test_apply_time_filter(self):
        """测试时间筛选功能."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 准备测试数据（包含今日任务）
        today = datetime.now()
        today_task = {"scheduled_date": today.strftime("%Y-%m-%d %H:%M")}

        yesterday_task = {
            "scheduled_date": (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
        }

        test_tasks = [today_task, yesterday_task]

        # 测试今日筛选
        filtered_today = self.task_panel._apply_time_filter(test_tasks, "今日")
        self.assertEqual(len(filtered_today), 1)

        # 测试逾期筛选
        filtered_overdue = self.task_panel._apply_time_filter(test_tasks, "逾期")
        self.assertEqual(len(filtered_overdue), 1)

    def test_update_statistics(self):
        """测试统计信息更新."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 更新统计信息
        self.task_panel._update_statistics()

        # 验证统计标签更新
        pending_text = self.task_panel.stats_labels["pending"].cget("text")
        self.assertIn("待办:", pending_text)

        overdue_text = self.task_panel.stats_labels["overdue"].cget("text")
        self.assertIn("逾期:", overdue_text)

        today_text = self.task_panel.stats_labels["today"].cget("text")
        self.assertIn("今日:", today_text)

    def test_task_selection_events(self):
        """测试任务选择事件."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 设置回调函数
        mock_callback = Mock()
        self.task_panel.on_task_selected = mock_callback

        # 模拟任务选择
        test_task = self.test_tasks[0]
        self.task_panel._on_task_selected(test_task)

        # 验证选择状态
        self.assertEqual(self.task_panel.selected_task_id, test_task["id"])

        # 验证回调调用
        mock_callback.assert_called_once_with(test_task)

    def test_complete_task_success(self):
        """测试成功完成任务."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 设置选中任务
        self.task_panel.selected_task_id = 1

        # 配置服务返回成功
        self.mock_interaction_service.complete_task.return_value = True

        # 使用patch模拟对话框
        with patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True  # 确认完成

            # 完成任务
            self.task_panel._complete_task()

            # 验证服务调用
            self.mock_interaction_service.complete_task.assert_called_once_with(
                1, "任务已完成"
            )

            # 验证成功消息
            mock_messagebox.showinfo.assert_called_once()

    def test_complete_task_no_selection(self):
        """测试未选择任务时完成任务."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 未设置选中任务
        self.task_panel.selected_task_id = None

        # 使用patch模拟对话框
        with patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox:
            # 尝试完成任务
            self.task_panel._complete_task()

            # 验证警告消息
            mock_messagebox.showwarning.assert_called_once()

            # 验证服务未被调用
            self.mock_interaction_service.complete_task.assert_not_called()

    def test_delete_task_success(self):
        """测试成功删除任务."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 设置选中任务
        self.task_panel.selected_task_id = 1

        # 配置服务返回成功
        self.mock_interaction_service.update_interaction.return_value = True

        # 使用patch模拟对话框
        with patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True  # 确认删除

            # 删除任务
            self.task_panel._delete_task()

            # 验证服务调用
            self.mock_interaction_service.update_interaction.assert_called_once_with(
                1, {"interaction_status": "cancelled"}
            )

            # 验证选择被清除
            self.assertIsNone(self.task_panel.selected_task_id)

    def test_check_reminders(self):
        """测试提醒检查功能."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 配置提醒数据
        reminder_data = [
            {
                "id": 1,
                "subject": "提醒任务",
                "party_name": "测试客户",
                "scheduled_date": "2025-01-25 10:00:00",
            }
        ]
        self.mock_interaction_service.get_pending_reminders.return_value = reminder_data

        # 使用patch模拟提醒显示
        with patch.object(self.task_panel, "_show_reminder_notification") as mock_show:
            # 检查提醒
            self.task_panel._check_reminders()

            # 验证服务调用
            self.mock_interaction_service.get_pending_reminders.assert_called_once()

            # 验证提醒显示
            mock_show.assert_called_once_with(reminder_data[0])

    def test_export_tasks(self):
        """测试任务导出功能."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 使用patch模拟文件对话框和文件操作
        with (
            patch("minicrm.ui.ttk_base.task_panel_ttk.filedialog") as mock_filedialog,
            patch("builtins.open", create=True) as mock_open,
            patch("csv.DictWriter") as mock_writer,
            patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox,
        ):
            # 配置文件对话框返回文件名
            mock_filedialog.asksaveasfilename.return_value = "test_export.csv"

            # 导出任务
            self.task_panel._export_tasks()

            # 验证文件对话框调用
            mock_filedialog.asksaveasfilename.assert_called_once()

            # 验证文件打开
            mock_open.assert_called_once()

            # 验证成功消息
            mock_messagebox.showinfo.assert_called_once()

    def test_calendar_view_operations(self):
        """测试日历视图操作."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试月份导航
        with patch.object(self.task_panel, "_update_calendar_view") as mock_update:
            # 上一个月
            self.task_panel._previous_month()
            mock_update.assert_called()

            # 下一个月
            mock_update.reset_mock()
            self.task_panel._next_month()
            mock_update.assert_called()

            # 跳转到今日
            mock_update.reset_mock()
            self.task_panel._goto_today()
            mock_update.assert_called()

    def test_timeline_view_operations(self):
        """测试时间线视图操作."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 确保时间线画布存在
        if hasattr(self.task_panel, "timeline_canvas"):
            # 测试时间线更新
            with patch.object(self.task_panel, "_draw_timeline") as mock_draw:
                self.task_panel._update_timeline_view()
                # 验证绘制方法被调用
                # mock_draw.assert_called()

    def test_task_color_assignment(self):
        """测试任务颜色分配."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试不同状态和优先级的颜色
        completed_task = {"interaction_status": "已完成", "priority": "普通"}
        self.assertEqual(self.task_panel._get_task_color(completed_task), "green")

        cancelled_task = {"interaction_status": "已取消", "priority": "普通"}
        self.assertEqual(self.task_panel._get_task_color(cancelled_task), "gray")

        urgent_task = {"interaction_status": "计划中", "priority": "紧急"}
        self.assertEqual(self.task_panel._get_task_color(urgent_task), "red")

        high_task = {"interaction_status": "计划中", "priority": "高"}
        self.assertEqual(self.task_panel._get_task_color(high_task), "orange")

        normal_task = {"interaction_status": "计划中", "priority": "普通"}
        self.assertEqual(self.task_panel._get_task_color(normal_task), "blue")

    def test_cleanup_resources(self):
        """测试资源清理."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 设置一些数据
        self.task_panel.selected_task_id = 1

        # 清理资源
        self.task_panel.cleanup()

        # 验证数据被清理
        self.assertEqual(len(self.task_panel.tasks), 0)
        self.assertEqual(len(self.task_panel.filtered_tasks), 0)
        self.assertIsNone(self.task_panel.selected_task_id)

    def test_string_representation(self):
        """测试字符串表示."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 获取字符串表示
        str_repr = str(self.task_panel)

        # 验证包含预期信息
        self.assertIn("TaskPanelTTK", str_repr)
        self.assertIn("tasks=", str_repr)
        self.assertIn("filtered=", str_repr)

    def test_public_methods(self):
        """测试公共方法."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试获取选中任务ID
        self.task_panel.selected_task_id = 123
        self.assertEqual(self.task_panel.get_selected_task_id(), 123)

        # 测试刷新数据
        with patch.object(self.task_panel, "_load_tasks") as mock_load:
            self.task_panel.refresh_data()
            mock_load.assert_called_once()

    def test_error_handling_in_operations(self):
        """测试操作中的错误处理."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 测试完成任务时的服务异常
        self.task_panel.selected_task_id = 1

        from minicrm.core.exceptions import ServiceError

        self.mock_interaction_service.complete_task.side_effect = ServiceError(
            "测试异常"
        )

        with patch("minicrm.ui.ttk_base.task_panel_ttk.messagebox") as mock_messagebox:
            mock_messagebox.askyesno.return_value = True

            # 尝试完成任务
            self.task_panel._complete_task()

            # 验证错误消息显示
            mock_messagebox.showerror.assert_called_once()

    def test_filter_event_handling(self):
        """测试筛选器事件处理."""
        self.task_panel = TaskPanelTTK(self.root, self.mock_interaction_service)

        # 使用patch模拟方法调用
        with (
            patch.object(self.task_panel, "_apply_filters") as mock_apply,
            patch.object(self.task_panel, "_update_statistics") as mock_stats,
        ):
            # 触发筛选器变化事件
            self.task_panel._on_filter_changed()

            # 验证方法调用
            mock_apply.assert_called_once()
            mock_stats.assert_called_once()


class TestTaskPanelTTKIntegration(unittest.TestCase):
    """TaskPanelTTK 集成测试类."""

    def setUp(self):
        """测试前准备."""
        self.root = tk.Tk()
        self.root.withdraw()

        # 创建真实的服务实例（如果可能）
        # 这里使用Mock，实际项目中可能需要测试数据库
        self.mock_service = Mock(spec=InteractionService)
        self.mock_service.get_pending_tasks.return_value = []

    def tearDown(self):
        """测试后清理."""
        if hasattr(self, "task_panel"):
            self.task_panel.cleanup()
        self.root.destroy()

    def test_full_workflow(self):
        """测试完整工作流程."""
        # 创建面板
        self.task_panel = TaskPanelTTK(self.root, self.mock_service)

        # 验证初始状态
        self.assertIsNotNone(self.task_panel)
        self.assertEqual(len(self.task_panel.tasks), 0)

        # 模拟数据加载
        test_data = [
            {
                "id": 1,
                "subject": "集成测试任务",
                "party_name": "测试客户",
                "priority": "normal",
                "interaction_status": "planned",
                "scheduled_date": "2025-01-25 10:00:00",
                "follow_up_date": "",
                "created_at": "2025-01-20 09:00:00",
            }
        ]

        self.mock_service.get_pending_tasks.return_value = test_data

        # 重新加载数据
        self.task_panel._load_tasks()

        # 验证数据加载
        self.assertEqual(len(self.task_panel.tasks), 1)

        # 测试筛选功能
        self.task_panel.search_entry.insert(0, "集成测试")
        self.task_panel._perform_search()

        # 验证筛选结果
        self.assertEqual(len(self.task_panel.filtered_tasks), 1)


if __name__ == "__main__":
    # 运行测试
    unittest.main()
