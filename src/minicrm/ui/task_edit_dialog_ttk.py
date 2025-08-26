"""MiniCRM 任务编辑对话框TTK版本

提供任务创建和编辑功能,包括:
- 任务基本信息编辑
- 关联方选择(客户或供应商)
- 时间和提醒设置
- 优先级和状态管理
- 数据验证和保存

设计原则:
- 继承BaseDialogTTK提供一致的对话框体验
- 集成表单验证和错误提示
- 支持创建和编辑两种模式
- 遵循MiniCRM开发标准
"""

from datetime import datetime, timedelta
import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from minicrm.core.exceptions import ValidationError
from minicrm.ui.ttk_base.base_dialog import (
    BaseDialogTTK,
    SimpleDialogMixin,
)
from transfunctions.validation import validate_required_fields


class TaskEditDialogTTK(BaseDialogTTK, SimpleDialogMixin):
    """任务编辑对话框TTK版本

    提供任务创建和编辑的完整界面:
    - 任务基本信息(标题、描述、优先级)
    - 关联方信息(客户或供应商)
    - 时间设置(计划时间、截止日期)
    - 提醒设置(是否提醒、提前时间)
    - 状态管理(仅编辑模式)
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        task_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """初始化任务编辑对话框

        Args:
            parent: 父组件
            task_data: 任务数据(编辑模式时提供)
            **kwargs: 其他参数
        """
        # 保存任务数据
        self._task_data = task_data or {}
        self._is_edit_mode = bool(task_data)

        # 设置对话框标题
        title = "编辑任务" if self._is_edit_mode else "新建任务"

        # 日志记录器
        self._logger = logging.getLogger(__name__)

        # UI组件引用 - 必须在基类初始化前创建
        self._title_var = tk.StringVar()
        self._description_text: Optional[tk.Text] = None
        self._party_type_var = tk.StringVar(value="客户")
        self._party_name_var = tk.StringVar()
        self._priority_var = tk.StringVar(value="普通")
        self._status_var = tk.StringVar(value="计划中")
        self._scheduled_date_var = tk.StringVar()
        self._due_date_var = tk.StringVar()
        self._reminder_enabled_var = tk.BooleanVar(value=True)
        self._reminder_minutes_var = tk.IntVar(value=30)

        # 初始化基类
        super().__init__(
            parent=parent, title=title, size=(500, 600), min_size=(450, 550), **kwargs
        )

        # 加载数据
        self._load_task_data()

        self._logger.info(f"任务编辑对话框初始化完成 (编辑模式: {self._is_edit_mode})")

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 创建滚动区域
        canvas = tk.Canvas(self.content_frame)
        scrollbar = ttk.Scrollbar(
            self.content_frame, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 创建表单内容
        self._create_form_content(scrollable_frame)

        # 布局滚动区域
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

    def _create_form_content(self, parent: tk.Widget) -> None:
        """创建表单内容"""
        # 基本信息组
        self._create_basic_info_group(parent)

        # 关联方信息组
        self._create_party_info_group(parent)

        # 时间设置组
        self._create_time_settings_group(parent)

        # 提醒设置组
        self._create_reminder_settings_group(parent)

        # 状态设置组(仅编辑模式)
        if self._is_edit_mode:
            self._create_status_group(parent)

    def _create_basic_info_group(self, parent: tk.Widget) -> None:
        """创建基本信息组"""
        group = ttk.LabelFrame(parent, text="基本信息", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 任务标题
        self.create_label_entry_pair(group, "任务标题", self._title_var, required=True)

        # 任务描述
        desc_frame = ttk.Frame(group)
        desc_frame.pack(fill=tk.X, pady=2)

        ttk.Label(desc_frame, text="任务描述:").pack(side=tk.LEFT)

        self._description_text = tk.Text(desc_frame, height=4, wrap=tk.WORD)
        self._description_text.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # 优先级
        self.create_label_combobox_pair(
            group, "优先级", ["低", "普通", "高", "紧急"], self._priority_var
        )

    def _create_party_info_group(self, parent: tk.Widget) -> None:
        """创建关联方信息组"""
        group = ttk.LabelFrame(parent, text="关联方信息", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 关联方类型
        self.create_label_combobox_pair(
            group, "关联方类型", ["客户", "供应商"], self._party_type_var
        )

        # 关联方名称
        self.create_label_entry_pair(
            group, "关联方名称", self._party_name_var, required=True
        )

    def _create_time_settings_group(self, parent: tk.Widget) -> None:
        """创建时间设置组"""
        group = ttk.LabelFrame(parent, text="时间设置", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 计划时间
        self.create_label_entry_pair(group, "计划时间", self._scheduled_date_var)

        # 截止日期
        self.create_label_entry_pair(group, "截止日期", self._due_date_var)

        # 设置默认时间
        now = datetime.now()
        self._scheduled_date_var.set(now.strftime("%Y-%m-%d %H:%M"))
        self._due_date_var.set((now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"))

    def _create_reminder_settings_group(self, parent: tk.Widget) -> None:
        """创建提醒设置组"""
        group = ttk.LabelFrame(parent, text="提醒设置", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 启用提醒
        reminder_frame = ttk.Frame(group)
        reminder_frame.pack(fill=tk.X, pady=2)

        reminder_check = ttk.Checkbutton(
            reminder_frame, text="启用提醒", variable=self._reminder_enabled_var
        )
        reminder_check.pack(side=tk.LEFT)

        # 提前时间
        ttk.Label(reminder_frame, text="提前").pack(side=tk.LEFT, padx=(20, 5))

        minutes_spin = ttk.Spinbox(
            reminder_frame,
            from_=1,
            to=1440,
            textvariable=self._reminder_minutes_var,
            width=10,
        )
        minutes_spin.pack(side=tk.LEFT)

        ttk.Label(reminder_frame, text="分钟").pack(side=tk.LEFT, padx=(5, 0))

    def _create_status_group(self, parent: tk.Widget) -> None:
        """创建状态设置组(仅编辑模式)"""
        group = ttk.LabelFrame(parent, text="状态设置", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 任务状态
        self.create_label_combobox_pair(
            group,
            "任务状态",
            ["计划中", "进行中", "已完成", "已取消", "已延期"],
            self._status_var,
        )

    def _load_task_data(self) -> None:
        """加载任务数据到表单"""
        if not self._is_edit_mode or not self._task_data:
            return

        try:
            # 加载基本信息
            self._title_var.set(self._task_data.get("subject", ""))

            # 加载描述(需要在UI创建后设置)
            self.after_idle(self._load_description)

            # 加载关联方信息
            party_type = self._task_data.get("party_type", "customer")
            self._party_type_var.set("客户" if party_type == "customer" else "供应商")
            self._party_name_var.set(self._task_data.get("party_name", ""))

            # 加载优先级
            priority = self._task_data.get("priority", "normal")
            priority_map = {
                "low": "低",
                "normal": "普通",
                "high": "高",
                "urgent": "紧急",
            }
            self._priority_var.set(priority_map.get(priority, "普通"))

            # 加载状态
            status = self._task_data.get("interaction_status", "planned")
            status_map = {
                "planned": "计划中",
                "in_progress": "进行中",
                "completed": "已完成",
                "cancelled": "已取消",
                "postponed": "已延期",
            }
            self._status_var.set(status_map.get(status, "计划中"))

            # 加载时间
            scheduled_date = self._task_data.get("scheduled_date")
            if scheduled_date:
                try:
                    dt = datetime.fromisoformat(scheduled_date)
                    self._scheduled_date_var.set(dt.strftime("%Y-%m-%d %H:%M"))
                except ValueError:
                    pass

            due_date = self._task_data.get("follow_up_date")
            if due_date:
                try:
                    dt = datetime.fromisoformat(due_date)
                    self._due_date_var.set(dt.strftime("%Y-%m-%d %H:%M"))
                except ValueError:
                    pass

            # 加载提醒设置
            self._reminder_enabled_var.set(
                self._task_data.get("reminder_enabled", False)
            )
            self._reminder_minutes_var.set(self._task_data.get("reminder_minutes", 30))

        except Exception as e:
            self._logger.error(f"加载任务数据失败: {e}")
            self.show_error(f"加载任务数据失败: {e}")

    def _load_description(self) -> None:
        """延迟加载描述内容"""
        if self._description_text and self._task_data:
            content = self._task_data.get("content", "")
            self._description_text.delete("1.0", tk.END)
            self._description_text.insert("1.0", content)

    def _validate_input(self) -> bool:
        """验证输入数据"""
        try:
            # 获取表单数据
            task_data = self._get_form_data()

            # 使用transfunctions验证必填字段
            required_fields = ["subject", "party_name"]
            errors = validate_required_fields(task_data, required_fields)

            if errors:
                raise ValidationError("; ".join(errors))

            # 验证时间逻辑
            scheduled_str = self._scheduled_date_var.get().strip()
            due_str = self._due_date_var.get().strip()

            if scheduled_str and due_str:
                try:
                    scheduled_time = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
                    due_time = datetime.strptime(due_str, "%Y-%m-%d %H:%M")

                    if due_time <= scheduled_time:
                        raise ValidationError("截止日期必须晚于计划时间")

                    # 验证计划时间不能是过去时间(允许1小时误差)
                    if scheduled_time < datetime.now() - timedelta(hours=1):
                        raise ValidationError("计划时间不能早于当前时间")

                except ValueError:
                    raise ValidationError(
                        "时间格式不正确,请使用 YYYY-MM-DD HH:MM 格式"
                    )

            return True

        except ValidationError as e:
            self.show_error(str(e))
            return False
        except Exception as e:
            self._logger.error(f"验证输入失败: {e}")
            self.show_error(f"验证输入失败: {e}")
            return False

    def _get_result_data(self) -> Dict[str, Any]:
        """获取结果数据"""
        return self._get_form_data()

    def _get_form_data(self) -> Dict[str, Any]:
        """获取表单数据"""
        # 基本信息
        data = {
            "subject": self._title_var.get().strip(),
            "party_name": self._party_name_var.get().strip(),
        }

        # 描述
        if self._description_text:
            data["content"] = self._description_text.get("1.0", tk.END).strip()
        else:
            data["content"] = ""

        # 关联方类型
        party_type_text = self._party_type_var.get()
        data["party_type"] = "customer" if party_type_text == "客户" else "supplier"

        # 优先级
        priority_text = self._priority_var.get()
        priority_map = {"低": "low", "普通": "normal", "高": "high", "紧急": "urgent"}
        data["priority"] = priority_map.get(priority_text, "normal")

        # 状态
        if self._is_edit_mode:
            status_text = self._status_var.get()
            status_map = {
                "计划中": "planned",
                "进行中": "in_progress",
                "已完成": "completed",
                "已取消": "cancelled",
                "已延期": "postponed",
            }
            data["interaction_status"] = status_map.get(status_text, "planned")
        else:
            data["interaction_status"] = "planned"

        # 时间信息
        scheduled_str = self._scheduled_date_var.get().strip()
        due_str = self._due_date_var.get().strip()

        if scheduled_str:
            try:
                dt = datetime.strptime(scheduled_str, "%Y-%m-%d %H:%M")
                data["scheduled_date"] = dt.isoformat()
            except ValueError:
                data["scheduled_date"] = datetime.now().isoformat()
        else:
            data["scheduled_date"] = datetime.now().isoformat()

        if due_str:
            try:
                dt = datetime.strptime(due_str, "%Y-%m-%d %H:%M")
                data["follow_up_date"] = dt.isoformat()
            except ValueError:
                data["follow_up_date"] = (
                    datetime.now() + timedelta(days=1)
                ).isoformat()
        else:
            data["follow_up_date"] = (datetime.now() + timedelta(days=1)).isoformat()

        data["follow_up_required"] = True

        # 提醒设置
        data["reminder_enabled"] = self._reminder_enabled_var.get()
        data["reminder_minutes"] = self._reminder_minutes_var.get()

        # 任务特定设置
        data["interaction_type"] = "follow_up"  # 任务使用跟进类型

        # 如果是编辑模式,保留ID
        if self._is_edit_mode and "id" in self._task_data:
            data["id"] = self._task_data["id"]

        return data

    def set_party_info(
        self, party_type: str, party_name: str, party_id: Optional[int] = None
    ) -> None:
        """设置关联方信息

        Args:
            party_type: 关联方类型 ("customer" 或 "supplier")
            party_name: 关联方名称
            party_id: 关联方ID(可选)
        """
        # 设置关联方类型
        if party_type == "customer":
            self._party_type_var.set("客户")
        else:
            self._party_type_var.set("供应商")

        # 设置关联方名称
        self._party_name_var.set(party_name)

        # 保存关联方ID
        if party_id is not None:
            self.set_data("party_id", party_id)

    def get_party_info(self) -> Dict[str, Any]:
        """获取关联方信息"""
        party_type_text = self._party_type_var.get()
        return {
            "party_type": "customer" if party_type_text == "客户" else "supplier",
            "party_name": self._party_name_var.get().strip(),
            "party_id": self.get_data("party_id"),
        }
