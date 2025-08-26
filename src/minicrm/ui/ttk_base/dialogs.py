"""TTK对话框模块

统一的TTK对话框接口,包括:
- 基础对话框类
- 消息对话框
- 进度对话框
- 文件对话框
- 便利函数

使用示例:
    from minicrm.ui.ttk_base.dialogs import show_info, confirm, get_input

    # 显示信息
    show_info(parent, "操作完成")

    # 确认操作
    if confirm(parent, "确定要删除吗?"):
        # 执行删除
        pass

    # 获取输入
    name = get_input(parent, "输入姓名", "请输入您的姓名:")
    if name:
        print(f"您好, {name}!")

作者: MiniCRM开发团队
"""

# 导入基础对话框类
from .base_dialog import BaseDialogTTK, DialogResult

# 导入具体对话框类
from .file_dialog_ttk import (
    FileDialogMode,
    FileDialogTTK,
    open_file_dialog,
    open_multiple_files_dialog,
    save_file_dialog,
    select_directory_dialog,
)

# 导入便利函数
from .message_dialogs_ttk import (
    ConfirmDialogTTK,
    InputDialogTTK,
    MessageBoxTTK,
    MessageType,
    confirm,
    get_input,
    get_multiline_input,
    get_password,
    show_error,
    show_info,
    show_message,
    show_success,
    show_warning,
)
from .progress_dialog_ttk import (
    ProgressDialogTTK,
    ProgressTask,
    ProgressUpdater,
    show_progress_dialog,
)


# 导出所有公共接口
__all__ = [
    # 基础类
    "BaseDialogTTK",
    "DialogResult",
    # 对话框类
    "MessageBoxTTK",
    "ConfirmDialogTTK",
    "InputDialogTTK",
    "ProgressDialogTTK",
    "FileDialogTTK",
    "SettingsDialogTTK",
    "ImportDialogTTK",
    "ExportDialogTTK",
    # 辅助类
    "ProgressTask",
    "ProgressUpdater",
    "MessageType",
    "FileDialogMode",
    # 便利函数 - 消息对话框
    "show_message",
    "show_info",
    "show_warning",
    "show_error",
    "show_success",
    "confirm",
    # 便利函数 - 输入对话框
    "get_input",
    "get_password",
    "get_multiline_input",
    # 便利函数 - 进度对话框
    "show_progress_dialog",
    # 便利函数 - 文件对话框
    "open_file_dialog",
    "save_file_dialog",
    "select_directory_dialog",
    "open_multiple_files_dialog",
    # 便利函数 - 业务对话框
    "show_settings_dialog",
    "show_import_dialog",
    "show_export_dialog",
]


# 版本信息
__version__ = "1.0.0"
__author__ = "MiniCRM开发团队"
__description__ = "MiniCRM TTK对话框模块"


def get_version() -> str:
    """获取模块版本"""
    return __version__


def get_available_dialogs() -> dict:
    """获取可用的对话框类型"""
    return {
        "message_dialogs": {
            "MessageBoxTTK": "通用消息对话框",
            "ConfirmDialogTTK": "确认对话框",
            "InputDialogTTK": "输入对话框",
        },
        "progress_dialogs": {"ProgressDialogTTK": "进度对话框"},
        "file_dialogs": {"FileDialogTTK": "文件选择对话框"},
        "convenience_functions": {
            "show_info": "显示信息消息",
            "show_warning": "显示警告消息",
            "show_error": "显示错误消息",
            "show_success": "显示成功消息",
            "confirm": "显示确认对话框",
            "get_input": "获取用户输入",
            "get_password": "获取密码输入",
            "get_multiline_input": "获取多行输入",
            "open_file_dialog": "打开文件对话框",
            "save_file_dialog": "保存文件对话框",
            "select_directory_dialog": "选择目录对话框",
            "open_multiple_files_dialog": "多文件选择对话框",
            "show_progress_dialog": "显示进度对话框",
            "show_settings_dialog": "显示设置对话框",
            "show_import_dialog": "显示导入对话框",
            "show_export_dialog": "显示导出对话框",
        },
    }


def create_custom_dialog(dialog_class, parent=None, **kwargs):
    """创建自定义对话框的便利函数

    Args:
        dialog_class: 对话框类
        parent: 父窗口
        **kwargs: 对话框参数

    Returns:
        对话框实例
    """
    return dialog_class(parent=parent, **kwargs)


# 快捷别名
info = show_info
warning = show_warning
error = show_error
success = show_success
ask = confirm
input_text = get_input
input_password = get_password
input_multiline = get_multiline_input
open_file = open_file_dialog
save_file = save_file_dialog
select_folder = select_directory_dialog
open_files = open_multiple_files_dialog
progress = show_progress_dialog
