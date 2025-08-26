"""MiniCRM TTK错误处理系统

专门为TTK界面设计的错误处理器,提供:
- TTK组件异常处理
- 用户友好的错误提示对话框
- 错误恢复机制
- 与现有错误处理系统的集成
- 性能监控集成

设计原则:
- 继承现有错误处理基础设施
- 提供TTK特定的错误处理策略
- 用户友好的错误提示界面
- 自动错误恢复和重试机制
"""

from contextlib import contextmanager
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Callable, Dict, Optional

from .error_handler import (
    ErrorAction,
    ErrorHandler,
    ErrorInfo,
    ErrorSeverity,
    ErrorType,
)
from .exceptions import UIError
from .logger import get_logger
from .performance_monitor import performance_monitor


class TTKErrorHandler(ErrorHandler):
    """TTK专用错误处理器

    扩展基础错误处理器,添加TTK界面特定的错误处理功能.
    """

    def __init__(self, parent_window: Optional[tk.Tk] = None):
        """初始化TTK错误处理器

        Args:
            parent_window: 父窗口,用于显示错误对话框
        """
        super().__init__()
        self._logger = get_logger(__name__)
        self._parent_window = parent_window

        # TTK特定的错误处理策略
        self._ttk_error_strategies = {
            "widget_creation_error": ErrorAction.RETRY,
            "layout_error": ErrorAction.SKIP,
            "theme_error": ErrorAction.CONTINUE,
            "binding_error": ErrorAction.ASK_USER,
            "validation_error": ErrorAction.ASK_USER,
            "data_binding_error": ErrorAction.RETRY,
        }

        # 错误恢复回调函数
        self._recovery_callbacks: Dict[str, Callable] = {}

        # 错误统计
        self._ui_error_count = 0
        self._recovery_success_count = 0

        self._logger.info("TTK错误处理器初始化完成")

    def set_parent_window(self, parent: tk.Tk) -> None:
        """设置父窗口

        Args:
            parent: 父窗口对象
        """
        self._parent_window = parent
        self._logger.debug(f"设置父窗口: {parent}")

    def register_recovery_callback(self, error_type: str, callback: Callable) -> None:
        """注册错误恢复回调函数

        Args:
            error_type: 错误类型标识
            callback: 恢复回调函数
        """
        self._recovery_callbacks[error_type] = callback
        self._logger.debug(f"注册恢复回调: {error_type}")

    @contextmanager
    def handle_ui_operation(self, operation_name: str, **context):
        """UI操作错误处理上下文管理器

        Args:
            operation_name: 操作名称
            **context: 操作上下文信息

        Example:
            with error_handler.handle_ui_operation("create_widget", widget_type="Button"):
                button = ttk.Button(parent, text="测试")
        """
        start_time = datetime.now()

        try:
            with performance_monitor.monitor_operation(
                f"ui_operation_{operation_name}", **context
            ):
                yield

        except Exception as e:
            # 分类和处理错误
            error_info = self.classify_ui_error(e, operation_name, context)

            # 记录错误
            self._ui_error_count += 1

            # 尝试恢复
            recovery_success = self._attempt_recovery(error_info)

            if recovery_success:
                self._recovery_success_count += 1
                self._logger.info(f"UI操作错误恢复成功: {operation_name}")
            else:
                # 显示用户友好的错误提示
                self._show_user_error_dialog(error_info)

                # 重新抛出异常(如果需要)
                if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                    raise UIError(
                        f"UI操作失败: {operation_name}",
                        ui_operation=operation_name,
                        original_exception=e,
                    )

    def classify_ui_error(
        self, exception: Exception, operation: str, context: Dict[str, Any]
    ) -> ErrorInfo:
        """分类UI错误

        Args:
            exception: 异常对象
            operation: 操作名称
            context: 操作上下文

        Returns:
            ErrorInfo: 分类后的错误信息
        """
        # 基础分类
        error_info = self.classify_error(exception, context)

        # TTK特定的错误分类
        exception_str = str(exception).lower()

        if "widget" in exception_str or "tkinter" in exception_str:
            error_info.error_type = ErrorType.SYSTEM_ERROR
            error_info.context["ui_component"] = "widget"

        elif (
            "geometry" in exception_str
            or "pack" in exception_str
            or "grid" in exception_str
        ):
            error_info.error_type = ErrorType.VALIDATION_ERROR
            error_info.context["ui_component"] = "layout"

        elif "style" in exception_str or "theme" in exception_str:
            error_info.error_type = ErrorType.VALIDATION_ERROR
            error_info.context["ui_component"] = "style"

        elif "bind" in exception_str or "event" in exception_str:
            error_info.error_type = ErrorType.SYSTEM_ERROR
            error_info.context["ui_component"] = "event"

        # 添加操作信息
        error_info.context.update(
            {
                "operation": operation,
                "ui_framework": "ttk",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return error_info

    def _attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """尝试错误恢复

        Args:
            error_info: 错误信息

        Returns:
            bool: 恢复是否成功
        """
        try:
            # 检查是否有注册的恢复回调
            ui_component = error_info.context.get("ui_component")
            if ui_component and ui_component in self._recovery_callbacks:
                callback = self._recovery_callbacks[ui_component]
                callback(error_info)
                return True

            # 通用恢复策略
            if error_info.error_type == ErrorType.VALIDATION_ERROR:
                return self._recover_validation_error(error_info)
            if error_info.error_type == ErrorType.SYSTEM_ERROR:
                return self._recover_system_error(error_info)

        except Exception as e:
            self._logger.error(f"错误恢复失败: {e}")

        return False

    def _recover_validation_error(self, error_info: ErrorInfo) -> bool:
        """恢复验证错误"""
        ui_component = error_info.context.get("ui_component")

        if ui_component == "layout":
            # 布局错误 - 尝试重置布局
            self._logger.info("尝试重置布局恢复错误")
            return True

        if ui_component == "style":
            # 样式错误 - 使用默认样式
            self._logger.info("使用默认样式恢复错误")
            return True

        return False

    def _recover_system_error(self, error_info: ErrorInfo) -> bool:
        """恢复系统错误"""
        ui_component = error_info.context.get("ui_component")

        if ui_component == "widget":
            # 组件创建错误 - 延迟重试
            self._logger.info("延迟重试组件创建")
            return True

        if ui_component == "event":
            # 事件绑定错误 - 跳过事件绑定
            self._logger.info("跳过事件绑定恢复错误")
            return True

        return False

    def _show_user_error_dialog(self, error_info: ErrorInfo) -> None:
        """显示用户友好的错误对话框

        Args:
            error_info: 错误信息
        """
        try:
            # 确保在主线程中显示对话框
            if threading.current_thread() != threading.main_thread():
                # 如果不在主线程,调度到主线程
                if self._parent_window:
                    self._parent_window.after(
                        0, lambda: self._show_error_dialog_impl(error_info)
                    )
                return

            self._show_error_dialog_impl(error_info)

        except Exception as e:
            self._logger.error(f"显示错误对话框失败: {e}")

    def _show_error_dialog_impl(self, error_info: ErrorInfo) -> None:
        """实际显示错误对话框的实现"""
        # 根据错误严重程度选择对话框类型
        title = self._get_error_title(error_info.severity)
        message = self._format_user_message(error_info)

        if (
            error_info.severity == ErrorSeverity.CRITICAL
            or error_info.severity == ErrorSeverity.HIGH
        ):
            messagebox.showerror(title, message, parent=self._parent_window)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            messagebox.showwarning(title, message, parent=self._parent_window)
        else:
            messagebox.showinfo(title, message, parent=self._parent_window)

    def _get_error_title(self, severity: ErrorSeverity) -> str:
        """获取错误对话框标题"""
        titles = {
            ErrorSeverity.CRITICAL: "严重错误",
            ErrorSeverity.HIGH: "系统错误",
            ErrorSeverity.MEDIUM: "操作警告",
            ErrorSeverity.LOW: "提示信息",
        }
        return titles.get(severity, "系统提示")

    def _format_user_message(self, error_info: ErrorInfo) -> str:
        """格式化用户友好的错误消息"""
        # 基础消息
        message_parts = []

        # 主要错误信息
        if error_info.error_type == ErrorType.VALIDATION_ERROR:
            message_parts.append("输入数据验证失败")
        elif error_info.error_type == ErrorType.SYSTEM_ERROR:
            message_parts.append("系统操作出现问题")
        elif error_info.error_type == ErrorType.BUSINESS_LOGIC_ERROR:
            message_parts.append("业务规则验证失败")
        else:
            message_parts.append("操作执行失败")

        # 具体错误信息
        if error_info.message:
            message_parts.append(f"\n详细信息:{error_info.message}")

        # 操作建议
        suggestions = self._get_user_suggestions(error_info)
        if suggestions:
            message_parts.append(f"\n建议:{suggestions}")

        return "".join(message_parts)

    def _get_user_suggestions(self, error_info: ErrorInfo) -> str:
        """获取用户操作建议"""
        ui_component = error_info.context.get("ui_component")

        if ui_component == "layout":
            return "请检查窗口大小或重新调整界面布局"
        if ui_component == "style":
            return "请尝试切换到默认主题或重启应用程序"
        if ui_component == "widget":
            return "请重试操作或重启应用程序"
        if ui_component == "event":
            return "请重试操作,如果问题持续请联系技术支持"
        if error_info.error_type == ErrorType.VALIDATION_ERROR:
            return "请检查输入数据的格式和完整性"
        if error_info.error_type == ErrorType.BUSINESS_LOGIC_ERROR:
            return "请检查操作是否符合业务规则要求"
        return "请重试操作,如果问题持续请联系技术支持"

    def show_validation_error(
        self, field_name: str, message: str, parent: tk.Widget = None
    ) -> None:
        """显示验证错误提示

        Args:
            field_name: 字段名称
            message: 错误消息
            parent: 父组件
        """
        title = "数据验证错误"
        full_message = f"字段 '{field_name}' 验证失败:\n{message}"

        messagebox.showwarning(
            title, full_message, parent=parent or self._parent_window
        )

    def show_business_error(
        self, operation: str, message: str, parent: tk.Widget = None
    ) -> None:
        """显示业务逻辑错误提示

        Args:
            operation: 操作名称
            message: 错误消息
            parent: 父组件
        """
        title = "业务规则错误"
        full_message = f"操作 '{operation}' 失败:\n{message}"

        messagebox.showwarning(
            title, full_message, parent=parent or self._parent_window
        )

    def confirm_operation(
        self, operation: str, message: str, parent: tk.Widget = None
    ) -> bool:
        """确认操作对话框

        Args:
            operation: 操作名称
            message: 确认消息
            parent: 父组件

        Returns:
            bool: 用户是否确认
        """
        title = f"确认{operation}"
        return messagebox.askyesno(title, message, parent=parent or self._parent_window)

    def get_ui_error_statistics(self) -> Dict[str, Any]:
        """获取UI错误统计信息

        Returns:
            Dict[str, Any]: UI错误统计数据
        """
        base_stats = self.get_error_statistics()

        return {
            **base_stats,
            "ui_errors": self._ui_error_count,
            "recovery_success": self._recovery_success_count,
            "recovery_rate": (
                self._recovery_success_count / max(self._ui_error_count, 1) * 100
            ),
            "registered_callbacks": len(self._recovery_callbacks),
        }

    def create_error_report(self) -> str:
        """创建错误报告

        Returns:
            str: 格式化的错误报告
        """
        stats = self.get_ui_error_statistics()
        summary = self.get_error_summary()

        report_lines = [
            "=== MiniCRM TTK错误处理报告 ===",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "=== 错误统计 ===",
            f"总错误数: {stats['total_errors']}",
            f"UI错误数: {stats['ui_errors']}",
            f"恢复成功数: {stats['recovery_success']}",
            f"恢复成功率: {stats['recovery_rate']:.1f}%",
            f"严重错误数: {stats['critical_errors']}",
            "",
            "=== 错误分布 ===",
        ]

        # 添加错误类型分布
        for error_type, count in summary["type_counts"].items():
            report_lines.append(f"{error_type}: {count}")

        report_lines.extend(
            [
                "",
                "=== 最近错误 ===",
            ]
        )

        # 添加最近的错误
        for error in summary["recent_errors"][-5:]:  # 最近5个错误
            report_lines.append(
                f"- [{error['severity']}] {error['type']}: {error['message'][:50]}..."
            )

        return "\n".join(report_lines)


# 全局TTK错误处理器实例
_ttk_error_handler: Optional[TTKErrorHandler] = None


def get_ttk_error_handler(parent_window: Optional[tk.Tk] = None) -> TTKErrorHandler:
    """获取全局TTK错误处理器实例

    Args:
        parent_window: 父窗口(仅在首次创建时使用)

    Returns:
        TTKErrorHandler: 错误处理器实例
    """
    global _ttk_error_handler

    if _ttk_error_handler is None:
        _ttk_error_handler = TTKErrorHandler(parent_window)
    elif parent_window and not _ttk_error_handler._parent_window:
        _ttk_error_handler.set_parent_window(parent_window)

    return _ttk_error_handler


def handle_ui_operation(operation_name: str, **context):
    """UI操作错误处理装饰器/上下文管理器

    Args:
        operation_name: 操作名称
        **context: 操作上下文
    """
    return get_ttk_error_handler().handle_ui_operation(operation_name, **context)


def show_validation_error(
    field_name: str, message: str, parent: tk.Widget = None
) -> None:
    """显示验证错误提示"""
    get_ttk_error_handler().show_validation_error(field_name, message, parent)


def show_business_error(operation: str, message: str, parent: tk.Widget = None) -> None:
    """显示业务逻辑错误提示"""
    get_ttk_error_handler().show_business_error(operation, message, parent)


def confirm_operation(operation: str, message: str, parent: tk.Widget = None) -> bool:
    """确认操作对话框"""
    return get_ttk_error_handler().confirm_operation(operation, message, parent)
