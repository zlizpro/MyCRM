#!/usr/bin/env python3
"""TTK对话框系统演示.

演示MiniCRM TTK对话框系统的各种功能, 包括:
- 基础对话框
- 消息对话框(信息、警告、错误、成功)
- 确认对话框
- 输入对话框(单行、多行、密码)
- 进度对话框
- 文件对话框(打开、保存、目录选择)

使用方法:
    python examples/dialog_system_demo.py

作者: MiniCRM开发团队
"""

from pathlib import Path
import sys
import time
import tkinter as tk
from tkinter import ttk


# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / ".."))

try:
    from src.minicrm.ui.ttk_base.dialogs import (
        confirm,
        get_input,
        get_multiline_input,
        get_password,
        open_file_dialog,
        save_file_dialog,
        select_directory_dialog,
        show_error,
        show_info,
        show_progress_dialog,
        show_success,
        show_warning,
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


class DialogDemoApp:
    """对话框演示应用程序."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MiniCRM TTK对话框系统演示")
        self.root.geometry("600x500")

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面."""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="MiniCRM TTK对话框系统演示",
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # 创建按钮区域
        self.create_message_buttons(main_frame)
        self.create_input_buttons(main_frame)
        self.create_file_buttons(main_frame)
        self.create_progress_buttons(main_frame)

        # 退出按钮
        ttk.Button(
            main_frame, text="退出演示", command=self.root.quit, style="Accent.TButton"
        ).pack(pady=20)

    def create_message_buttons(self, parent):
        """创建消息对话框按钮."""
        group = ttk.LabelFrame(parent, text="消息对话框", padding="10")
        group.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(group)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="信息消息", command=self.show_info_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="警告消息", command=self.show_warning_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="错误消息", command=self.show_error_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="成功消息", command=self.show_success_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            button_frame, text="确认对话框", command=self.show_confirm_demo
        ).pack(side=tk.LEFT)

    def create_input_buttons(self, parent):
        """创建输入对话框按钮."""
        group = ttk.LabelFrame(parent, text="输入对话框", padding="10")
        group.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(group)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="单行输入", command=self.show_input_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(button_frame, text="密码输入", command=self.show_password_demo).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        ttk.Button(
            button_frame, text="多行输入", command=self.show_multiline_demo
        ).pack(side=tk.LEFT)

    def create_file_buttons(self, parent):
        """创建文件对话框按钮."""
        group = ttk.LabelFrame(parent, text="文件对话框", padding="10")
        group.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(group)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame, text="打开文件", command=self.show_open_file_demo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="保存文件", command=self.show_save_file_demo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="选择目录", command=self.show_select_dir_demo
        ).pack(side=tk.LEFT)

    def create_progress_buttons(self, parent):
        """创建进度对话框按钮."""
        group = ttk.LabelFrame(parent, text="进度对话框", padding="10")
        group.pack(fill=tk.X, pady=(0, 10))

        button_frame = ttk.Frame(group)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame, text="确定进度", command=self.show_determinate_progress_demo
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame,
            text="不确定进度",
            command=self.show_indeterminate_progress_demo,
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="可取消进度", command=self.show_cancelable_progress_demo
        ).pack(side=tk.LEFT)

    # 消息对话框演示方法
    def show_info_demo(self):
        """演示信息消息."""
        show_info(self.root, "这是一条信息消息\n用于向用户提供一般性信息", "信息")

    def show_warning_demo(self):
        """演示警告消息."""
        show_warning(self.root, "这是一条警告消息\n提醒用户注意某些情况", "警告")

    def show_error_demo(self):
        """演示错误消息."""
        show_error(self.root, "这是一条错误消息\n告知用户发生了错误", "错误")

    def show_success_demo(self):
        """演示成功消息."""
        show_success(self.root, "操作成功完成!\n数据已保存", "成功")

    def show_confirm_demo(self):
        """演示确认对话框."""
        result = confirm(
            self.root,
            "确定要删除选中的项目吗?\n此操作无法撤销",
            "确认删除",
            "删除",
            "取消",
        )

        if result:
            show_info(self.root, "用户选择了删除", "结果")
        else:
            show_info(self.root, "用户取消了操作", "结果")

    # 输入对话框演示方法
    def show_input_demo(self):
        """演示单行输入."""

        def validate_name(value):
            return len(value.strip()) >= 2

        result = get_input(
            self.root,
            "输入姓名",
            "请输入您的姓名:",
            "张三",
            validation_func=validate_name,
        )

        if result:
            show_info(self.root, f"您输入的姓名是: {result}", "输入结果")
        else:
            show_info(self.root, "用户取消了输入", "输入结果")

    def show_password_demo(self):
        """演示密码输入."""

        def validate_password(value):
            return len(value) >= 6

        result = get_password(
            self.root,
            "输入密码",
            "请输入密码(至少6位):",
            validation_func=validate_password,
        )

        if result:
            show_info(self.root, f"密码长度: {len(result)} 位", "密码输入结果")
        else:
            show_info(self.root, "用户取消了密码输入", "密码输入结果")

    def show_multiline_demo(self):
        """演示多行输入."""
        initial_text = "这是一个多行输入示例\n您可以输入多行文本\n支持换行和长文本"

        result = get_multiline_input(
            self.root, "多行输入", "请输入您的意见或建议:", initial_text
        )

        if result:
            line_count = len(result.split("\n"))
            char_count = len(result)
            show_info(
                self.root,
                f"输入了 {line_count} 行, 共 {char_count} 个字符",
                "多行输入结果",
            )
        else:
            show_info(self.root, "用户取消了多行输入", "多行输入结果")

    # 文件对话框演示方法
    def show_open_file_demo(self):
        """演示打开文件对话框."""
        file_types = [
            ("文本文件", "*.txt"),
            ("Python文件", "*.py"),
            ("所有文件", "*.*"),
        ]

        result = open_file_dialog(self.root, "选择要打开的文件", file_types=file_types)

        if result:
            filename = Path(result).name
            show_info(
                self.root, f"选择的文件: {filename}\n路径: {result}", "文件选择结果"
            )
        else:
            show_info(self.root, "用户取消了文件选择", "文件选择结果")

    def show_save_file_demo(self):
        """演示保存文件对话框."""
        file_types = [("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")]

        result = save_file_dialog(
            self.root,
            "保存文件",
            initial_file="新建文件.txt",
            file_types=file_types,
            default_extension=".txt",
        )

        if result:
            filename = Path(result).name
            show_info(
                self.root, f"保存文件: {filename}\n路径: {result}", "文件保存结果"
            )
        else:
            show_info(self.root, "用户取消了文件保存", "文件保存结果")

    def show_select_dir_demo(self):
        """演示选择目录对话框."""
        result = select_directory_dialog(self.root, "选择目录")

        if result:
            dirname = Path(result).name
            show_info(
                self.root, f"选择的目录: {dirname}\n路径: {result}", "目录选择结果"
            )
        else:
            show_info(self.root, "用户取消了目录选择", "目录选择结果")

    # 进度对话框演示方法
    def show_determinate_progress_demo(self):
        """演示确定进度对话框."""

        def long_task(updater):
            """模拟长时间运行的任务."""
            total_steps = 100

            for i in range(total_steps + 1):
                # 检查是否被取消
                if updater.is_cancelled():
                    break

                # 更新进度
                updater.update_progress(i, total_steps)
                updater.update_message(f"正在处理步骤 {i}/{total_steps}")
                updater.update_detail(f"当前进度: {i / total_steps * 100:.1f}%")

                # 模拟工作
                time.sleep(0.05)

            return "任务完成"

        try:
            result = show_progress_dialog(
                self.root,
                long_task,
                title="处理中",
                message="正在执行任务...",
                determinate=True,
                cancelable=True,
            )
            show_info(self.root, f"任务结果: {result}", "进度任务完成")
        except (RuntimeError, ValueError) as e:
            show_error(self.root, f"任务执行失败: {e}", "进度任务错误")

    def show_indeterminate_progress_demo(self):
        """演示不确定进度对话框."""

        def unknown_task(updater):
            """模拟未知进度的任务."""
            steps = ["初始化...", "连接服务器...", "下载数据...", "处理数据...", "完成"]

            for i, step in enumerate(steps):
                # 检查是否被取消
                if updater.is_cancelled():
                    break

                updater.update_message(step)
                updater.update_detail(f"步骤 {i + 1}/{len(steps)}")

                # 模拟不同长度的工作
                time.sleep(1 + i * 0.5)

            return "未知进度任务完成"

        try:
            result = show_progress_dialog(
                self.root,
                unknown_task,
                title="连接中",
                message="正在连接服务器...",
                determinate=False,
                cancelable=True,
            )
            show_info(self.root, f"任务结果: {result}", "不确定进度任务完成")
        except (RuntimeError, ValueError) as e:
            show_error(self.root, f"任务执行失败: {e}", "不确定进度任务错误")

    def show_cancelable_progress_demo(self):
        """演示可取消的进度对话框."""

        def cancelable_task(updater):
            """模拟可取消的长任务."""
            total_time = 10  # 10秒的任务

            for i in range(total_time * 10):  # 每0.1秒更新一次
                # 检查取消状态
                updater.check_cancelled()  # 如果被取消会抛出异常

                progress = (i + 1) / (total_time * 10) * 100
                updater.update_percentage(progress)
                updater.update_message(f"正在执行长时间任务... ({progress:.1f}%)")
                updater.update_detail(f"剩余时间: {total_time - i / 10:.1f} 秒")

                time.sleep(0.1)

            return "长任务完成"

        try:
            result = show_progress_dialog(
                self.root,
                cancelable_task,
                title="长时间任务",
                message="正在执行长时间任务...",
                determinate=True,
                cancelable=True,
            )
            show_info(self.root, f"任务结果: {result}", "可取消任务完成")
        except InterruptedError:
            show_warning(self.root, "任务被用户取消", "任务取消")
        except (RuntimeError, ValueError) as e:
            show_error(self.root, f"任务执行失败: {e}", "可取消任务错误")

    def run(self):
        """运行演示应用."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        except Exception:
            pass
        finally:
            pass


def main():
    """主函数."""
    try:
        app = DialogDemoApp()
        app.run()
    except (ImportError, RuntimeError) as e:
        print(f"启动演示失败: {e}")
        print("可能的原因:")
        print("1. 缺少图形界面支持")
        print("2. Tkinter未正确安装")
        print("3. 依赖模块导入失败")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
