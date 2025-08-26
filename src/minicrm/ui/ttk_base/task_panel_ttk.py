"""MiniCRM 任务管理TTK面板.

基于tkinter/ttk实现的任务管理面板,替换Qt版本的TaskPanel.
提供完整的任务管理功能,包括:
- 任务列表显示和管理
- 任务创建、编辑和状态跟踪功能
- 任务提醒和通知管理
- 日历视图和时间线视图
- 任务筛选和搜索功能

设计特点:
- 继承BaseWidget提供统一的组件基础
- 使用DataTableTTK显示任务列表
- 集成InteractionService处理任务业务逻辑
- 支持多视图切换(列表、日历、时间线)
- 模块化设计,保持代码清晰
- 遵循MiniCRM开发标准

作者: MiniCRM开发团队
"""

from __future__ import annotations

from datetime import datetime, timedelta
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Optional

from minicrm.core.exceptions import ServiceError
from minicrm.services.interaction_service import InteractionService
from minicrm.ui.ttk_base.base_widget import BaseWidget
from minicrm.ui.ttk_base.data_table_ttk import DataTableTTK


class TaskPanelTTK(BaseWidget):
    """TTK任务管理面板.

    提供完整的任务管理界面,包括任务列表、搜索筛选、
    状态管理、编辑操作等功能.
    """

    def __init__(
        self, parent: tk.Widget, interaction_service: InteractionService, **kwargs
    ):
        """初始化任务管理面板.

        Args:
            parent: 父容器组件
            interaction_service: 互动服务实例
            **kwargs: 其他参数
        """
        self.interaction_service = interaction_service

        # 数据存储
        self.tasks: list[dict[str, Any]] = []
        self.filtered_tasks: list[dict[str, Any]] = []
        self.selected_task_id: Optional[int] = None

        # UI组件
        self.main_notebook: Optional[ttk.Notebook] = None
        self.search_frame: Optional[ttk.Frame] = None
        self.search_entry: Optional[ttk.Entry] = None
        self.status_filter: Optional[ttk.Combobox] = None
        self.priority_filter: Optional[ttk.Combobox] = None
        self.task_table: Optional[DataTableTTK] = None
        self.calendar_frame: Optional[ttk.Frame] = None
        self.timeline_frame: Optional[ttk.Frame] = None

        # 统计信息标签
        self.stats_labels: dict[str, ttk.Label] = {}

        # 定时器
        self.reminder_timer: Optional[threading.Timer] = None
        self.auto_refresh_timer: Optional[threading.Timer] = None

        # 事件回调
        self.on_task_selected: Optional[Callable] = None
        self.on_task_created: Optional[Callable] = None
        self.on_task_updated: Optional[Callable] = None
        self.on_task_completed: Optional[Callable] = None

        # 初始化基础组件
        super().__init__(parent, **kwargs)

        # 加载初始数据
        self._load_tasks()

        # 启动定时器
        self._start_reminder_timer()
        self._start_auto_refresh()

    def _setup_ui(self) -> None:
        """设置UI布局."""
        # 创建主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建标题栏
        self._create_title_bar(main_container)

        # 创建搜索筛选区域
        self._create_search_area(main_container)

        # 创建操作按钮区域
        self._create_button_area(main_container)

        # 创建主标签页
        self._create_main_notebook(main_container)

        # 创建各个视图标签页
        self._create_list_view_tab()
        self._create_calendar_view_tab()
        self._create_timeline_view_tab()

    def _create_title_bar(self, parent: ttk.Frame) -> None:
        """创建标题栏."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        # 左侧:标题和统计
        left_frame = ttk.Frame(title_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 主标题
        title_label = ttk.Label(
            left_frame, text="任务管理", font=("Microsoft YaHei UI", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # 统计信息
        stats_frame = ttk.Frame(left_frame)
        stats_frame.pack(side=tk.LEFT, padx=(20, 0))

        # 待办任务统计
        self.stats_labels["pending"] = ttk.Label(
            stats_frame, text="待办: 0", foreground="blue"
        )
        self.stats_labels["pending"].pack(side=tk.LEFT, padx=(0, 10))

        # 逾期任务统计
        self.stats_labels["overdue"] = ttk.Label(
            stats_frame, text="逾期: 0", foreground="red"
        )
        self.stats_labels["overdue"].pack(side=tk.LEFT, padx=(0, 10))

        # 今日任务统计
        self.stats_labels["today"] = ttk.Label(
            stats_frame, text="今日: 0", foreground="green"
        )
        self.stats_labels["today"].pack(side=tk.LEFT)

        # 右侧:快速操作按钮
        right_frame = ttk.Frame(title_frame)
        right_frame.pack(side=tk.RIGHT)

        # 刷新按钮
        refresh_btn = ttk.Button(
            right_frame, text="🔄 刷新", command=self._refresh_tasks
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 新建任务按钮
        new_task_btn = ttk.Button(
            right_frame, text="➕ 新建任务", command=self._create_task
        )
        new_task_btn.pack(side=tk.LEFT)

    def _create_search_area(self, parent: ttk.Frame) -> None:
        """创建搜索筛选区域."""
        self.search_frame = ttk.LabelFrame(parent, text="搜索筛选", padding=10)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行:搜索框
        search_row = ttk.Frame(self.search_frame)
        search_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_row, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_row, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        search_btn = ttk.Button(
            search_row, text="🔍 搜索", command=self._perform_search
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_btn = ttk.Button(search_row, text="清除", command=self._clear_search)
        clear_btn.pack(side=tk.LEFT)

        # 第二行:筛选器
        filter_row = ttk.Frame(self.search_frame)
        filter_row.pack(fill=tk.X)

        # 状态筛选
        ttk.Label(filter_row, text="状态:").pack(side=tk.LEFT, padx=(0, 5))

        self.status_filter = ttk.Combobox(filter_row, width=15, state="readonly")
        self.status_filter["values"] = [
            "全部",
            "计划中",
            "进行中",
            "已完成",
            "已取消",
            "已延期",
        ]
        self.status_filter.set("全部")
        self.status_filter.pack(side=tk.LEFT, padx=(0, 15))

        # 优先级筛选
        ttk.Label(filter_row, text="优先级:").pack(side=tk.LEFT, padx=(0, 5))

        self.priority_filter = ttk.Combobox(filter_row, width=15, state="readonly")
        self.priority_filter["values"] = ["全部", "低", "普通", "高", "紧急"]
        self.priority_filter.set("全部")
        self.priority_filter.pack(side=tk.LEFT, padx=(0, 15))

        # 时间筛选
        ttk.Label(filter_row, text="时间:").pack(side=tk.LEFT, padx=(0, 5))

        self.time_filter = ttk.Combobox(filter_row, width=15, state="readonly")
        self.time_filter["values"] = ["全部", "今日", "本周", "本月", "逾期"]
        self.time_filter.set("全部")
        self.time_filter.pack(side=tk.LEFT)

    def _create_button_area(self, parent: ttk.Frame) -> None:
        """创建操作按钮区域."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # 左侧按钮组
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side=tk.LEFT)

        # 编辑任务
        edit_btn = ttk.Button(left_buttons, text="✏️ 编辑", command=self._edit_task)
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 完成任务
        complete_btn = ttk.Button(
            left_buttons, text="✅ 完成", command=self._complete_task
        )
        complete_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 删除任务
        delete_btn = ttk.Button(left_buttons, text="🗑️ 删除", command=self._delete_task)
        delete_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 右侧按钮组
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side=tk.RIGHT)

        # 导出任务
        export_btn = ttk.Button(
            right_buttons, text="📤 导出", command=self._export_tasks
        )
        export_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _create_main_notebook(self, parent: ttk.Frame) -> None:
        """创建主标签页容器."""
        self.main_notebook = ttk.Notebook(parent)
        self.main_notebook.pack(fill=tk.BOTH, expand=True)

    def _create_list_view_tab(self) -> None:
        """创建任务列表视图标签页."""
        list_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(list_frame, text="📋 任务列表")

        # 定义表格列
        columns = [
            {"id": "id", "text": "ID", "width": 60, "visible": False},
            {"id": "subject", "text": "任务标题", "width": 200, "sortable": True},
            {"id": "party_name", "text": "关联方", "width": 150, "sortable": True},
            {"id": "priority", "text": "优先级", "width": 80, "sortable": True},
            {"id": "interaction_status", "text": "状态", "width": 80, "sortable": True},
            {
                "id": "scheduled_date",
                "text": "计划时间",
                "width": 150,
                "sortable": True,
            },
            {
                "id": "follow_up_date",
                "text": "跟进日期",
                "width": 120,
                "sortable": True,
            },
            {"id": "created_at", "text": "创建时间", "width": 120, "sortable": True},
        ]

        # 创建任务表格
        self.task_table = DataTableTTK(
            list_frame,
            columns=columns,
            multi_select=True,
            show_pagination=True,
            page_size=50,
        )
        self.task_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 设置事件回调
        self.task_table.on_row_selected = self._on_task_selected
        self.task_table.on_row_double_clicked = self._on_task_double_clicked
        self.task_table.on_selection_changed = self._on_selection_changed

    def _create_calendar_view_tab(self) -> None:
        """创建日历视图标签页."""
        self.calendar_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.calendar_frame, text="📅 日历视图")

        # 创建日历视图内容
        calendar_content = ttk.Frame(self.calendar_frame)
        calendar_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 日历控制栏
        calendar_toolbar = ttk.Frame(calendar_content)
        calendar_toolbar.pack(fill=tk.X, pady=(0, 10))

        # 月份导航
        ttk.Button(calendar_toolbar, text="◀ 上月", command=self._previous_month).pack(
            side=tk.LEFT
        )

        self.month_label = ttk.Label(
            calendar_toolbar,
            text=datetime.now().strftime("%Y年%m月"),
            font=("Microsoft YaHei UI", 12, "bold"),
        )
        self.month_label.pack(side=tk.LEFT, padx=(10, 10))

        ttk.Button(calendar_toolbar, text="下月 ▶", command=self._next_month).pack(
            side=tk.LEFT
        )

        # 今日按钮
        ttk.Button(calendar_toolbar, text="今日", command=self._goto_today).pack(
            side=tk.RIGHT
        )

        # 日历网格(简化实现)
        calendar_grid = ttk.Frame(calendar_content)
        calendar_grid.pack(fill=tk.BOTH, expand=True)

        # 创建日历网格
        self._create_calendar_grid(calendar_grid)

    def _create_timeline_view_tab(self) -> None:
        """创建时间线视图标签页."""
        self.timeline_frame = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.timeline_frame, text="📈 时间线")

        # 时间线内容
        timeline_content = ttk.Frame(self.timeline_frame)
        timeline_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 时间线工具栏
        timeline_toolbar = ttk.Frame(timeline_content)
        timeline_toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            timeline_toolbar, text="时间线视图", font=("Microsoft YaHei UI", 12, "bold")
        ).pack(side=tk.LEFT)

        # 时间范围选择
        ttk.Label(timeline_toolbar, text="时间范围:").pack(side=tk.RIGHT, padx=(0, 5))

        self.timeline_range = ttk.Combobox(timeline_toolbar, width=10, state="readonly")
        self.timeline_range["values"] = ["7天", "30天", "90天", "180天"]
        self.timeline_range.set("30天")
        self.timeline_range.pack(side=tk.RIGHT)

        # 时间线画布
        timeline_canvas = tk.Canvas(timeline_content, bg="white", height=400)
        timeline_canvas.pack(fill=tk.BOTH, expand=True)

        # 滚动条
        timeline_scrollbar = ttk.Scrollbar(
            timeline_content, orient="vertical", command=timeline_canvas.yview
        )
        timeline_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        timeline_canvas.configure(yscrollcommand=timeline_scrollbar.set)

        # 存储画布引用
        self.timeline_canvas = timeline_canvas

    def _create_calendar_grid(self, parent: ttk.Frame) -> None:
        """创建日历网格(简化实现)."""
        # 星期标题
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i, day in enumerate(weekdays):
            label = ttk.Label(
                parent,
                text=day,
                font=("Microsoft YaHei UI", 10, "bold"),
                anchor="center",
            )
            label.grid(row=0, column=i, sticky="ew", padx=1, pady=1)

        # 日期网格(6行7列)
        self.calendar_cells = {}
        for row in range(1, 7):
            for col in range(7):
                cell_frame = ttk.Frame(parent, relief="solid", borderwidth=1)
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                # 日期标签
                date_label = ttk.Label(cell_frame, text="", anchor="nw")
                date_label.pack(anchor="nw", padx=2, pady=2)

                # 任务指示器
                task_frame = ttk.Frame(cell_frame)
                task_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

                self.calendar_cells[(row - 1, col)] = {
                    "frame": cell_frame,
                    "date_label": date_label,
                    "task_frame": task_frame,
                }

        # 配置网格权重
        for i in range(7):
            parent.grid_columnconfigure(i, weight=1)
        for i in range(7):
            parent.grid_rowconfigure(i, weight=1)

    def _bind_events(self) -> None:
        """绑定事件."""
        # 搜索框回车事件
        if self.search_entry:
            self.search_entry.bind("<Return>", lambda e: self._perform_search())

        # 筛选器变化事件
        if self.status_filter:
            self.status_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        if self.priority_filter:
            self.priority_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        if self.time_filter:
            self.time_filter.bind("<<ComboboxSelected>>", self._on_filter_changed)

        # 时间线范围变化事件
        if hasattr(self, "timeline_range"):
            self.timeline_range.bind(
                "<<ComboboxSelected>>", self._on_timeline_range_changed
            )

    def _load_tasks(self) -> None:
        """加载任务数据."""
        try:
            # 获取所有待办任务
            tasks = self.interaction_service.get_pending_tasks()

            # 转换为显示格式
            self.tasks = []
            for task in tasks:
                display_data = self._format_task_for_display(task)
                self.tasks.append(display_data)

            # 应用筛选
            self._apply_filters()

            # 更新表格数据
            if self.task_table:
                self.task_table.load_data(self.filtered_tasks)

            # 更新统计信息
            self._update_statistics()

            # 更新日历视图
            self._update_calendar_view()

            # 更新时间线视图
            self._update_timeline_view()

            self.logger.info(f"加载了 {len(self.tasks)} 个任务")

        except ServiceError as e:
            self.logger.error(f"加载任务数据失败: {e}")
            messagebox.showerror("错误", f"加载任务数据失败: {e}")

    def _format_task_for_display(self, task: dict[str, Any]) -> dict[str, Any]:
        """格式化任务数据用于显示."""
        # 格式化优先级
        priority = task.get("priority", "")
        priority_map = {"low": "低", "normal": "普通", "high": "高", "urgent": "紧急"}
        task["priority"] = priority_map.get(priority, priority)

        # 格式化状态
        status = task.get("interaction_status", "")
        status_map = {
            "planned": "计划中",
            "in_progress": "进行中",
            "completed": "已完成",
            "cancelled": "已取消",
            "delayed": "已延期",
        }
        task["interaction_status"] = status_map.get(status, status)

        # 格式化日期
        for date_field in ["scheduled_date", "follow_up_date", "created_at"]:
            date_value = task.get(date_field)
            if date_value:
                try:
                    if isinstance(date_value, str):
                        date_obj = datetime.fromisoformat(date_value)
                        task[date_field] = date_obj.strftime("%Y-%m-%d %H:%M")
                    else:
                        task[date_field] = str(date_value)
                except:
                    task[date_field] = ""
            else:
                task[date_field] = ""

        return task

    def _apply_filters(self) -> None:
        """应用筛选条件."""
        self.filtered_tasks = self.tasks.copy()

        # 搜索文本筛选
        if self.search_entry:
            search_text = self.search_entry.get().strip().lower()
            if search_text:
                self.filtered_tasks = [
                    task
                    for task in self.filtered_tasks
                    if (
                        search_text in task.get("subject", "").lower()
                        or search_text in task.get("party_name", "").lower()
                    )
                ]

        # 状态筛选
        if self.status_filter:
            status_filter = self.status_filter.get()
            if status_filter != "全部":
                self.filtered_tasks = [
                    task
                    for task in self.filtered_tasks
                    if task.get("interaction_status") == status_filter
                ]

        # 优先级筛选
        if self.priority_filter:
            priority_filter = self.priority_filter.get()
            if priority_filter != "全部":
                self.filtered_tasks = [
                    task
                    for task in self.filtered_tasks
                    if task.get("priority") == priority_filter
                ]

        # 时间筛选
        if hasattr(self, "time_filter"):
            time_filter = self.time_filter.get()
            if time_filter != "全部":
                self.filtered_tasks = self._apply_time_filter(
                    self.filtered_tasks, time_filter
                )

    def _apply_time_filter(
        self, tasks: list[dict[str, Any]], time_filter: str
    ) -> list[dict[str, Any]]:
        """应用时间筛选."""
        now = datetime.now()
        today = now.date()

        filtered_tasks = []

        for task in tasks:
            scheduled_date = task.get("scheduled_date", "")
            if not scheduled_date:
                continue

            try:
                # 解析日期
                if isinstance(scheduled_date, str):
                    task_date = datetime.strptime(
                        scheduled_date, "%Y-%m-%d %H:%M"
                    ).date()
                else:
                    continue

                # 应用时间筛选
                if time_filter == "今日" and task_date == today:
                    filtered_tasks.append(task)
                elif time_filter == "本周":
                    week_start = today - timedelta(days=today.weekday())
                    week_end = week_start + timedelta(days=6)
                    if week_start <= task_date <= week_end:
                        filtered_tasks.append(task)
                elif (time_filter == "本月" and task_date.month == today.month) or (
                    time_filter == "逾期" and task_date < today
                ):
                    filtered_tasks.append(task)

            except (ValueError, TypeError):
                continue

        return filtered_tasks

    def _update_statistics(self) -> None:
        """更新统计信息."""
        pending_count = 0
        overdue_count = 0
        today_count = 0

        today = datetime.now().date()

        for task in self.tasks:
            status = task.get("interaction_status", "")
            if status in ["计划中", "进行中"]:
                pending_count += 1

                # 检查是否为今日任务
                scheduled_date = task.get("scheduled_date", "")
                if scheduled_date:
                    try:
                        task_date = datetime.strptime(
                            scheduled_date, "%Y-%m-%d %H:%M"
                        ).date()
                        if task_date == today:
                            today_count += 1
                        elif task_date < today:
                            overdue_count += 1
                    except (ValueError, TypeError):
                        pass

        # 更新统计标签
        if "pending" in self.stats_labels:
            self.stats_labels["pending"].config(text=f"待办: {pending_count}")

        if "overdue" in self.stats_labels:
            self.stats_labels["overdue"].config(text=f"逾期: {overdue_count}")

        if "today" in self.stats_labels:
            self.stats_labels["today"].config(text=f"今日: {today_count}")

    def _update_calendar_view(self) -> None:
        """更新日历视图."""
        # 简化实现:清空所有日历单元格
        for cell_info in self.calendar_cells.values():
            cell_info["date_label"].config(text="")
            # 清空任务框架
            for widget in cell_info["task_frame"].winfo_children():
                widget.destroy()

        # 获取当前月份的任务
        current_month = datetime.now().replace(day=1)
        month_tasks = [
            task for task in self.tasks if self._is_task_in_month(task, current_month)
        ]

        # 更新月份标签
        if hasattr(self, "month_label"):
            self.month_label.config(text=current_month.strftime("%Y年%m月"))

        # 在日历中显示任务(简化实现)
        # 这里可以实现更复杂的日历布局逻辑

    def _update_timeline_view(self) -> None:
        """更新时间线视图."""
        if not hasattr(self, "timeline_canvas"):
            return

        # 清空画布
        self.timeline_canvas.delete("all")

        # 获取时间范围
        range_text = getattr(self, "timeline_range", None)
        if range_text:
            range_value = range_text.get()
            days = int(range_value.replace("天", ""))
        else:
            days = 30

        # 获取时间范围内的任务
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        timeline_tasks = [
            task
            for task in self.tasks
            if self._is_task_in_range(task, start_date, end_date)
        ]

        # 绘制时间线(简化实现)
        self._draw_timeline(timeline_tasks, start_date, end_date)

    def _is_task_in_month(self, task: dict[str, Any], month: datetime) -> bool:
        """检查任务是否在指定月份."""
        scheduled_date = task.get("scheduled_date", "")
        if not scheduled_date:
            return False

        try:
            task_date = datetime.strptime(scheduled_date, "%Y-%m-%d %H:%M")
            return task_date.year == month.year and task_date.month == month.month
        except (ValueError, TypeError):
            return False

    def _is_task_in_range(
        self, task: dict[str, Any], start_date: datetime, end_date: datetime
    ) -> bool:
        """检查任务是否在指定时间范围内."""
        scheduled_date = task.get("scheduled_date", "")
        if not scheduled_date:
            return False

        try:
            task_date = datetime.strptime(scheduled_date, "%Y-%m-%d %H:%M")
            return start_date <= task_date <= end_date
        except (ValueError, TypeError):
            return False

    def _draw_timeline(
        self, tasks: list[dict[str, Any]], start_date: datetime, end_date: datetime
    ) -> None:
        """绘制时间线(简化实现)."""
        if not tasks:
            return

        canvas = self.timeline_canvas
        canvas_width = canvas.winfo_width() or 800
        canvas_height = canvas.winfo_height() or 400

        # 绘制时间轴
        y_center = canvas_height // 2
        canvas.create_line(50, y_center, canvas_width - 50, y_center, width=2)

        # 绘制任务点
        total_days = (end_date - start_date).days
        if total_days == 0:
            return

        for i, task in enumerate(tasks):
            scheduled_date = task.get("scheduled_date", "")
            if not scheduled_date:
                continue

            try:
                task_date = datetime.strptime(scheduled_date, "%Y-%m-%d %H:%M")
                days_from_start = (task_date - start_date).days
                x = 50 + (days_from_start / total_days) * (canvas_width - 100)

                # 绘制任务点
                color = self._get_task_color(task)
                canvas.create_oval(x - 5, y_center - 5, x + 5, y_center + 5, fill=color)

                # 绘制任务标题
                subject = task.get("subject", "")[:20]
                canvas.create_text(
                    x,
                    y_center - 20,
                    text=subject,
                    font=("Microsoft YaHei UI", 8),
                    anchor="center",
                )

            except (ValueError, TypeError):
                continue

    def _get_task_color(self, task: dict[str, Any]) -> str:
        """获取任务颜色."""
        priority = task.get("priority", "")
        status = task.get("interaction_status", "")

        if status == "已完成":
            return "green"
        if status == "已取消":
            return "gray"
        if priority == "紧急":
            return "red"
        if priority == "高":
            return "orange"
        return "blue"

    # 事件处理方法
    def _on_task_selected(self, task_data: dict[str, Any]) -> None:
        """处理任务选择事件."""
        self.selected_task_id = task_data.get("id")

        # 触发外部回调
        if self.on_task_selected:
            self.on_task_selected(task_data)

    def _on_task_double_clicked(self, task_data: dict[str, Any]) -> None:
        """处理任务双击事件."""
        self._edit_task()

    def _on_selection_changed(self, selected_data: list[dict[str, Any]]) -> None:
        """处理选择变化事件."""
        if selected_data:
            self._on_task_selected(selected_data[0])

    def _on_filter_changed(self, event=None) -> None:
        """处理筛选器变化."""
        self._apply_filters()

        # 更新表格
        if self.task_table:
            self.task_table.load_data(self.filtered_tasks)

        # 更新统计
        self._update_statistics()

    def _on_timeline_range_changed(self, event=None) -> None:
        """处理时间线范围变化."""
        self._update_timeline_view()

    # 操作方法
    def _perform_search(self) -> None:
        """执行搜索."""
        self._apply_filters()

        # 更新表格
        if self.task_table:
            self.task_table.load_data(self.filtered_tasks)

    def _clear_search(self) -> None:
        """清除搜索."""
        if self.search_entry:
            self.search_entry.delete(0, tk.END)

        if self.status_filter:
            self.status_filter.set("全部")

        if self.priority_filter:
            self.priority_filter.set("全部")

        if hasattr(self, "time_filter"):
            self.time_filter.set("全部")

        # 重新加载数据
        self._load_tasks()

    def _refresh_tasks(self) -> None:
        """刷新任务数据."""
        self._load_tasks()

    def _create_task(self) -> None:
        """创建新任务."""
        try:
            # 导入任务编辑对话框
            from minicrm.ui.task_edit_dialog import TaskEditDialog

            dialog = TaskEditDialog(self)
            # 这里需要实现对话框的显示逻辑
            # 由于是TTK版本,可能需要创建TTK版本的对话框

            # 暂时显示提示信息
            messagebox.showinfo("提示", "任务创建功能将在后续实现")

        except ImportError:
            messagebox.showinfo("提示", "任务编辑对话框组件正在开发中")

    def _edit_task(self) -> None:
        """编辑选中的任务."""
        if not self.selected_task_id:
            messagebox.showwarning("警告", "请先选择要编辑的任务")
            return

        try:
            # 获取任务详情
            task_data = next(
                (
                    task
                    for task in self.tasks
                    if task.get("id") == self.selected_task_id
                ),
                None,
            )

            if not task_data:
                messagebox.showerror("错误", "任务不存在")
                return

            # 导入任务编辑对话框
            from minicrm.ui.task_edit_dialog import TaskEditDialog

            dialog = TaskEditDialog(self, task_data)
            # 这里需要实现对话框的显示逻辑

            # 暂时显示提示信息
            messagebox.showinfo("提示", "任务编辑功能将在后续实现")

        except ImportError:
            messagebox.showinfo("提示", "任务编辑对话框组件正在开发中")

    def _complete_task(self) -> None:
        """完成选中的任务."""
        if not self.selected_task_id:
            messagebox.showwarning("警告", "请先选择要完成的任务")
            return

        # 确认完成
        if not messagebox.askyesno("确认", "确定要完成选中的任务吗?"):
            return

        try:
            # 完成任务
            success = self.interaction_service.complete_task(
                self.selected_task_id, "任务已完成"
            )

            if success:
                # 刷新数据
                self._load_tasks()

                # 触发回调
                if self.on_task_completed:
                    self.on_task_completed(self.selected_task_id)

                messagebox.showinfo("成功", "任务已完成")
            else:
                messagebox.showerror("错误", "完成任务失败")

        except ServiceError as e:
            messagebox.showerror("错误", f"完成任务失败: {e}")

    def _delete_task(self) -> None:
        """删除选中的任务."""
        if not self.selected_task_id:
            messagebox.showwarning("警告", "请先选择要删除的任务")
            return

        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的任务吗?此操作不可撤销."):
            return

        try:
            # 通过更新状态来"删除"任务
            success = self.interaction_service.update_interaction(
                self.selected_task_id, {"interaction_status": "cancelled"}
            )

            if success:
                # 清除选择
                self.selected_task_id = None

                # 刷新数据
                self._load_tasks()

                messagebox.showinfo("成功", "任务已删除")
            else:
                messagebox.showerror("错误", "删除任务失败")

        except ServiceError as e:
            messagebox.showerror("错误", f"删除任务失败: {e}")

    def _export_tasks(self) -> None:
        """导出任务数据."""
        try:
            import csv
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialvalue=f"任务列表_{datetime.now().strftime('%Y%m%d')}.csv",
            )

            if filename:
                # 导出筛选后的任务数据
                with open(filename, "w", newline="", encoding="utf-8-sig") as csvfile:
                    if self.filtered_tasks:
                        fieldnames = self.filtered_tasks[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.filtered_tasks)

                messagebox.showinfo("导出成功", f"任务数据已导出到:\n{filename}")

        except Exception as e:
            self.logger.error(f"导出任务失败: {e}")
            messagebox.showerror("导出失败", f"导出失败: {e}")

    # 日历操作方法
    def _previous_month(self) -> None:
        """上一个月."""
        # 简化实现
        self._update_calendar_view()

    def _next_month(self) -> None:
        """下一个月."""
        # 简化实现
        self._update_calendar_view()

    def _goto_today(self) -> None:
        """跳转到今日."""
        # 简化实现
        self._update_calendar_view()

    # 定时器方法
    def _start_reminder_timer(self) -> None:
        """启动提醒检查定时器."""
        self._check_reminders()

        # 每分钟检查一次
        self.reminder_timer = threading.Timer(60.0, self._start_reminder_timer)
        self.reminder_timer.start()

    def _start_auto_refresh(self) -> None:
        """启动自动刷新定时器."""
        # 每5分钟自动刷新一次
        self.auto_refresh_timer = threading.Timer(300.0, self._auto_refresh_callback)
        self.auto_refresh_timer.start()

    def _auto_refresh_callback(self) -> None:
        """自动刷新回调."""
        try:
            self._load_tasks()
        except Exception as e:
            self.logger.error(f"自动刷新失败: {e}")
        finally:
            # 重新启动定时器
            self._start_auto_refresh()

    def _check_reminders(self) -> None:
        """检查并显示提醒."""
        try:
            # 获取待处理的提醒
            reminders = self.interaction_service.get_pending_reminders()

            for reminder in reminders:
                self._show_reminder_notification(reminder)

        except ServiceError as e:
            self.logger.error(f"检查提醒失败: {e}")

    def _show_reminder_notification(self, reminder: dict[str, Any]) -> None:
        """显示提醒通知."""
        subject = reminder.get("subject", "任务提醒")
        party_name = reminder.get("party_name", "")
        scheduled_date = reminder.get("scheduled_date", "")

        message = f"任务: {subject}\n"
        if party_name:
            message += f"关联方: {party_name}\n"
        if scheduled_date:
            message += f"计划时间: {scheduled_date}"

        # 显示提醒对话框
        messagebox.showinfo("任务提醒", message)

    # 公共方法
    def get_selected_task_id(self) -> Optional[int]:
        """获取选中的任务ID."""
        return self.selected_task_id

    def refresh_data(self) -> None:
        """刷新数据(公共接口)."""
        self._load_tasks()

    def cleanup(self) -> None:
        """清理资源."""
        try:
            # 停止定时器
            if self.reminder_timer:
                self.reminder_timer.cancel()

            if self.auto_refresh_timer:
                self.auto_refresh_timer.cancel()

            # 清理数据
            self.tasks.clear()
            self.filtered_tasks.clear()
            self.selected_task_id = None

            # 清理表格组件
            if self.task_table:
                self.task_table.cleanup()

            # 调用父类清理
            super().cleanup()

        except Exception as e:
            self.logger.error(f"清理任务面板失败: {e}")

    def __str__(self) -> str:
        """返回面板的字符串表示."""
        return f"TaskPanelTTK(tasks={len(self.tasks)}, filtered={len(self.filtered_tasks)})"


# 导出类
__all__ = ["TaskPanelTTK"]
