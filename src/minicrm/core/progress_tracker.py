"""
MiniCRM 进度跟踪工具

提供详细的进度跟踪功能,包括:
- 嵌套进度管理
- 步骤跟踪
- 时间估算
- 状态管理

设计原则:
- 支持多层级的进度跟踪
- 提供准确的时间估算
- 线程安全的进度更新
- 详细的状态信息记录
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Any


class ProgressStatus(Enum):
    """进度状态枚举"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ProgressStep:
    """进度步骤数据类"""

    name: str
    description: str = ""
    weight: float = 1.0  # 步骤权重,用于计算总体进度
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    progress: float = 0.0  # 0.0 - 1.0
    start_time: float | None = None
    end_time: float | None = None
    error_message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


class ProgressTracker:
    """
    进度跟踪器

    提供详细的进度跟踪功能,支持嵌套进度、步骤管理和时间估算.
    """

    def __init__(
        self,
        name: str = "操作进度",
        total_items: int = 0,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        """
        初始化进度跟踪器

        Args:
            name: 操作名称
            total_items: 总项目数量
            callback: 进度更新回调函数
        """
        self._name = name
        self._total_items = total_items
        self._callback = callback
        self._logger = logging.getLogger(__name__)

        # 进度状态
        self._status = ProgressStatus.NOT_STARTED
        self._current_item = 0
        self._start_time: float | None = None
        self._end_time: float | None = None

        # 步骤管理
        self._steps: list[ProgressStep] = []
        self._current_step_index = -1
        self._overall_progress = 0.0

        # 统计信息
        self._success_count = 0
        self._warning_count = 0
        self._error_count = 0
        self._error_messages: list[str] = []

        # 线程安全
        self._lock = Lock()

        self._logger.debug(f"进度跟踪器初始化: {name}")

    def add_step(self, name: str, description: str = "", weight: float = 1.0) -> int:
        """
        添加进度步骤

        Args:
            name: 步骤名称
            description: 步骤描述
            weight: 步骤权重

        Returns:
            int: 步骤索引
        """
        with self._lock:
            step = ProgressStep(name=name, description=description, weight=weight)
            self._steps.append(step)
            step_index = len(self._steps) - 1

            self._logger.debug(f"添加步骤 {step_index}: {name}")
            return step_index

    def start(self) -> None:
        """开始进度跟踪"""
        with self._lock:
            self._status = ProgressStatus.IN_PROGRESS
            self._start_time = time.time()
            self._current_item = 0
            self._overall_progress = 0.0

            self._logger.info(f"开始进度跟踪: {self._name}")
            self._notify_progress()

    def start_step(
        self, step_index: int, details: dict[str, Any] | None = None
    ) -> None:
        """
        开始执行步骤

        Args:
            step_index: 步骤索引
            details: 步骤详细信息
        """
        with self._lock:
            if 0 <= step_index < len(self._steps):
                step = self._steps[step_index]
                step.status = ProgressStatus.IN_PROGRESS
                step.start_time = time.time()
                step.progress = 0.0
                if details:
                    step.details.update(details)

                self._current_step_index = step_index

                self._logger.debug(f"开始步骤 {step_index}: {step.name}")
                self._notify_progress()

    def update_step_progress(
        self, step_index: int, progress: float, details: dict[str, Any] | None = None
    ) -> None:
        """
        更新步骤进度

        Args:
            step_index: 步骤索引
            progress: 进度值 (0.0 - 1.0)
            details: 更新的详细信息
        """
        with self._lock:
            if 0 <= step_index < len(self._steps):
                step = self._steps[step_index]
                step.progress = max(0.0, min(1.0, progress))
                if details:
                    step.details.update(details)

                # 更新总体进度
                self._calculate_overall_progress()
                self._notify_progress()

    def complete_step(
        self, step_index: int, success: bool = True, error_message: str = ""
    ) -> None:
        """
        完成步骤

        Args:
            step_index: 步骤索引
            success: 是否成功
            error_message: 错误消息(如果失败)
        """
        with self._lock:
            if 0 <= step_index < len(self._steps):
                step = self._steps[step_index]
                step.end_time = time.time()
                step.progress = 1.0

                if success:
                    step.status = ProgressStatus.COMPLETED
                else:
                    step.status = ProgressStatus.FAILED
                    step.error_message = error_message
                    self._error_messages.append(f"步骤 {step.name}: {error_message}")

                status_text = "成功" if success else "失败"
                self._logger.debug(
                    f"完成步骤 {step_index}: {step.name} ({status_text})"
                )
                self._calculate_overall_progress()
                self._notify_progress()

    def update_item_progress(self, current_item: int, item_details: str = "") -> None:
        """
        更新项目进度

        Args:
            current_item: 当前项目数
            item_details: 项目详细信息
        """
        with self._lock:
            self._current_item = current_item

            # 如果有当前步骤,更新步骤进度
            if self._current_step_index >= 0 and self._total_items > 0:
                step_progress = current_item / self._total_items
                self.update_step_progress(
                    self._current_step_index,
                    step_progress,
                    {"current_item": current_item, "item_details": item_details},
                )

    def add_success(self, message: str = "") -> None:
        """
        添加成功记录

        Args:
            message: 成功消息
        """
        with self._lock:
            self._success_count += 1
            if message:
                self._logger.debug(f"成功: {message}")
            self._notify_progress()

    def add_warning(self, message: str) -> None:
        """
        添加警告记录

        Args:
            message: 警告消息
        """
        with self._lock:
            self._warning_count += 1
            self._logger.warning(f"警告: {message}")
            self._notify_progress()

    def add_error(self, message: str) -> None:
        """
        添加错误记录

        Args:
            message: 错误消息
        """
        with self._lock:
            self._error_count += 1
            self._error_messages.append(message)
            self._logger.error(f"错误: {message}")
            self._notify_progress()

    def complete(self, success: bool = True, message: str = "") -> None:
        """
        完成进度跟踪

        Args:
            success: 是否成功完成
            message: 完成消息
        """
        with self._lock:
            self._end_time = time.time()
            self._overall_progress = 1.0

            if success:
                self._status = ProgressStatus.COMPLETED
            else:
                self._status = ProgressStatus.FAILED
                if message:
                    self._error_messages.append(message)

            self._logger.info(
                f"完成进度跟踪: {self._name} ({'成功' if success else '失败'})"
            )
            self._notify_progress()

    def cancel(self) -> None:
        """取消进度跟踪"""
        with self._lock:
            self._status = ProgressStatus.CANCELLED
            self._end_time = time.time()

            self._logger.info(f"取消进度跟踪: {self._name}")
            self._notify_progress()

    def pause(self) -> None:
        """暂停进度跟踪"""
        with self._lock:
            if self._status == ProgressStatus.IN_PROGRESS:
                self._status = ProgressStatus.PAUSED
                self._logger.info(f"暂停进度跟踪: {self._name}")
                self._notify_progress()

    def resume(self) -> None:
        """恢复进度跟踪"""
        with self._lock:
            if self._status == ProgressStatus.PAUSED:
                self._status = ProgressStatus.IN_PROGRESS
                self._logger.info(f"恢复进度跟踪: {self._name}")
                self._notify_progress()

    def _calculate_overall_progress(self) -> None:
        """计算总体进度"""
        if not self._steps:
            return

        total_weight = sum(step.weight for step in self._steps)
        if total_weight == 0:
            return

        weighted_progress = sum(step.progress * step.weight for step in self._steps)
        self._overall_progress = weighted_progress / total_weight

    def _notify_progress(self) -> None:
        """通知进度更新"""
        if self._callback:
            try:
                progress_data = self.get_progress_data()
                self._callback(progress_data)
            except Exception as e:
                self._logger.error(f"进度回调失败: {e}")

    def get_progress_data(self) -> dict[str, Any]:
        """
        获取进度数据

        Returns:
            Dict[str, Any]: 完整的进度数据
        """
        with self._lock:
            # 计算时间信息
            elapsed_time = 0.0
            estimated_total_time = 0.0
            estimated_remaining_time = 0.0

            if self._start_time:
                elapsed_time = time.time() - self._start_time

                if self._overall_progress > 0:
                    estimated_total_time = elapsed_time / self._overall_progress
                    estimated_remaining_time = max(
                        0, estimated_total_time - elapsed_time
                    )

            # 获取当前步骤信息
            current_step_info = None
            if 0 <= self._current_step_index < len(self._steps):
                step = self._steps[self._current_step_index]
                current_step_info = {
                    "name": step.name,
                    "description": step.description,
                    "progress": step.progress,
                    "status": step.status.value,
                    "details": step.details,
                }

            return {
                "name": self._name,
                "status": self._status.value,
                "overall_progress": self._overall_progress,
                "current_item": self._current_item,
                "total_items": self._total_items,
                "success_count": self._success_count,
                "warning_count": self._warning_count,
                "error_count": self._error_count,
                "error_messages": self._error_messages.copy(),
                "elapsed_time": elapsed_time,
                "estimated_total_time": estimated_total_time,
                "estimated_remaining_time": estimated_remaining_time,
                "current_step": current_step_info,
                "steps": [
                    {
                        "name": step.name,
                        "description": step.description,
                        "progress": step.progress,
                        "status": step.status.value,
                        "weight": step.weight,
                    }
                    for step in self._steps
                ],
            }

    def get_status(self) -> ProgressStatus:
        """获取当前状态"""
        return self._status

    def get_overall_progress(self) -> float:
        """获取总体进度 (0.0 - 1.0)"""
        return self._overall_progress

    def get_statistics(self) -> dict[str, int]:
        """
        获取统计信息

        Returns:
            Dict[str, int]: 统计数据
        """
        with self._lock:
            return {
                "success_count": self._success_count,
                "warning_count": self._warning_count,
                "error_count": self._error_count,
                "total_processed": self._current_item,
            }

    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self._status in [
            ProgressStatus.COMPLETED,
            ProgressStatus.FAILED,
            ProgressStatus.CANCELLED,
        ]

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._status == ProgressStatus.IN_PROGRESS
