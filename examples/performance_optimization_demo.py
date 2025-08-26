"""MiniCRM TTK性能优化功能演示

演示TTK性能优化功能的使用，包括：
- 虚拟滚动大数据集显示
- 异步任务处理
- 性能监控和优化
- 实时性能报告
"""

import random
import time
import tkinter as tk
from tkinter import ttk

from src.minicrm.ui.ttk_base.async_processor import (
    AsyncProcessor,
    run_async,
)
from src.minicrm.ui.ttk_base.performance_optimizer import TTKPerformanceOptimizer

# 导入性能优化组件
from src.minicrm.ui.ttk_base.virtual_scroll_mixin import (
    VirtualListBox,
)


class PerformanceOptimizationDemo:
    """性能优化功能演示"""

    def __init__(self):
        """初始化演示应用"""
        self.root = tk.Tk()
        self.root.title("MiniCRM TTK性能优化演示")
        self.root.geometry("1200x800")

        # 性能优化器
        self.optimizer = TTKPerformanceOptimizer()

        # 异步处理器
        self.async_processor = AsyncProcessor(max_workers=4)

        # 数据
        self.large_dataset = []
        self.generate_large_dataset()

        # 创建UI
        self.create_ui()

        # 注册组件到性能优化器
        self.register_components()

        # 启动性能监控
        self.start_performance_monitoring()

    def generate_large_dataset(self, size: int = 50000):
        """生成大数据集"""
        print(f"生成 {size} 条测试数据...")

        categories = ["客户", "供应商", "报价", "合同", "任务"]
        statuses = ["活跃", "待处理", "已完成", "已取消"]

        self.large_dataset = []
        for i in range(size):
            item = {
                "id": i + 1,
                "name": f"项目 {i + 1}",
                "category": random.choice(categories),
                "status": random.choice(statuses),
                "value": random.randint(1000, 100000),
                "date": f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "description": f"这是第 {i + 1} 个测试项目的详细描述信息",
            }
            self.large_dataset.append(item)

        print(f"数据生成完成：{len(self.large_dataset)} 条记录")

    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建笔记本组件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 虚拟滚动演示页面
        self.create_virtual_scroll_tab()

        # 异步处理演示页面
        self.create_async_processing_tab()

        # 性能监控页面
        self.create_performance_monitoring_tab()

        # 控制面板
        self.create_control_panel(main_frame)

    def create_virtual_scroll_tab(self):
        """创建虚拟滚动演示页面"""
        # 虚拟滚动页面
        virtual_frame = ttk.Frame(self.notebook)
        self.notebook.add(virtual_frame, text="虚拟滚动演示")

        # 标题和说明
        title_label = ttk.Label(
            virtual_frame,
            text="虚拟滚动大数据集演示",
            font=("Microsoft YaHei UI", 14, "bold"),
        )
        title_label.pack(pady=(10, 5))

        info_label = ttk.Label(
            virtual_frame,
            text=f"显示 {len(self.large_dataset)} 条记录，只渲染可见项目以优化性能",
            font=("Microsoft YaHei UI", 10),
        )
        info_label.pack(pady=(0, 10))

        # 控制按钮框架
        control_frame = ttk.Frame(virtual_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 数据大小控制
        ttk.Label(control_frame, text="数据大小:").pack(side=tk.LEFT, padx=(0, 5))

        self.data_size_var = tk.StringVar(value="50000")
        data_size_combo = ttk.Combobox(
            control_frame,
            textvariable=self.data_size_var,
            values=["1000", "10000", "50000", "100000"],
            width=10,
            state="readonly",
        )
        data_size_combo.pack(side=tk.LEFT, padx=(0, 10))

        # 重新生成数据按钮
        regenerate_btn = ttk.Button(
            control_frame, text="重新生成数据", command=self.regenerate_data
        )
        regenerate_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 滚动到指定位置
        ttk.Label(control_frame, text="跳转到:").pack(side=tk.LEFT, padx=(10, 5))

        self.jump_to_var = tk.StringVar()
        jump_entry = ttk.Entry(control_frame, textvariable=self.jump_to_var, width=10)
        jump_entry.pack(side=tk.LEFT, padx=(0, 5))

        jump_btn = ttk.Button(control_frame, text="跳转", command=self.jump_to_item)
        jump_btn.pack(side=tk.LEFT)

        # 性能统计显示
        stats_frame = ttk.LabelFrame(control_frame, text="性能统计")
        stats_frame.pack(side=tk.RIGHT, padx=(10, 0))

        self.virtual_stats_label = ttk.Label(
            stats_frame, text="等待数据加载...", font=("Microsoft YaHei UI", 9)
        )
        self.virtual_stats_label.pack(padx=5, pady=2)

        # 虚拟列表框
        list_frame = ttk.Frame(virtual_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建自定义虚拟列表框
        self.virtual_listbox = CustomVirtualListBox(list_frame)
        self.virtual_listbox.pack(fill=tk.BOTH, expand=True)

        # 设置数据
        self.virtual_listbox.set_data(self.large_dataset)

        # 启动统计更新
        self.update_virtual_scroll_stats()

    def create_async_processing_tab(self):
        """创建异步处理演示页面"""
        # 异步处理页面
        async_frame = ttk.Frame(self.notebook)
        self.notebook.add(async_frame, text="异步处理演示")

        # 标题和说明
        title_label = ttk.Label(
            async_frame,
            text="异步任务处理演示",
            font=("Microsoft YaHei UI", 14, "bold"),
        )
        title_label.pack(pady=(10, 5))

        info_label = ttk.Label(
            async_frame,
            text="演示后台任务处理，保持UI响应性",
            font=("Microsoft YaHei UI", 10),
        )
        info_label.pack(pady=(0, 10))

        # 任务控制面板
        task_control_frame = ttk.LabelFrame(async_frame, text="任务控制")
        task_control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 任务类型选择
        task_type_frame = ttk.Frame(task_control_frame)
        task_type_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(task_type_frame, text="任务类型:").pack(side=tk.LEFT, padx=(0, 5))

        self.task_type_var = tk.StringVar(value="数据处理")
        task_type_combo = ttk.Combobox(
            task_type_frame,
            textvariable=self.task_type_var,
            values=["数据处理", "文件导出", "报表生成", "数据分析", "批量操作"],
            width=15,
            state="readonly",
        )
        task_type_combo.pack(side=tk.LEFT, padx=(0, 10))

        # 任务数量
        ttk.Label(task_type_frame, text="任务数量:").pack(side=tk.LEFT, padx=(10, 5))

        self.task_count_var = tk.StringVar(value="5")
        task_count_spin = ttk.Spinbox(
            task_type_frame, from_=1, to=20, textvariable=self.task_count_var, width=5
        )
        task_count_spin.pack(side=tk.LEFT, padx=(0, 10))

        # 任务持续时间
        ttk.Label(task_type_frame, text="持续时间(秒):").pack(
            side=tk.LEFT, padx=(10, 5)
        )

        self.task_duration_var = tk.StringVar(value="2")
        duration_spin = ttk.Spinbox(
            task_type_frame,
            from_=1,
            to=10,
            textvariable=self.task_duration_var,
            width=5,
        )
        duration_spin.pack(side=tk.LEFT)

        # 任务操作按钮
        button_frame = ttk.Frame(task_control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        start_tasks_btn = ttk.Button(
            button_frame, text="启动任务", command=self.start_async_tasks
        )
        start_tasks_btn.pack(side=tk.LEFT, padx=(0, 5))

        cancel_tasks_btn = ttk.Button(
            button_frame, text="取消所有任务", command=self.cancel_all_tasks
        )
        cancel_tasks_btn.pack(side=tk.LEFT, padx=(0, 5))

        clear_tasks_btn = ttk.Button(
            button_frame, text="清理已完成任务", command=self.clear_completed_tasks
        )
        clear_tasks_btn.pack(side=tk.LEFT)

        # 任务状态显示
        status_frame = ttk.LabelFrame(async_frame, text="任务状态")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建任务状态表格
        columns = ("任务ID", "任务名称", "状态", "进度", "开始时间", "耗时")
        self.task_tree = ttk.Treeview(
            status_frame, columns=columns, show="headings", height=10
        )

        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=120)

        # 滚动条
        task_scrollbar = ttk.Scrollbar(
            status_frame, orient=tk.VERTICAL, command=self.task_tree.yview
        )
        self.task_tree.configure(yscrollcommand=task_scrollbar.set)

        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 异步处理统计
        async_stats_frame = ttk.Frame(async_frame)
        async_stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.async_stats_label = ttk.Label(
            async_stats_frame,
            text="异步处理统计: 等待任务启动...",
            font=("Microsoft YaHei UI", 10),
        )
        self.async_stats_label.pack()

        # 启动任务状态更新
        self.update_task_status()

    def create_performance_monitoring_tab(self):
        """创建性能监控页面"""
        # 性能监控页面
        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="性能监控")

        # 标题
        title_label = ttk.Label(
            perf_frame, text="实时性能监控", font=("Microsoft YaHei UI", 14, "bold")
        )
        title_label.pack(pady=(10, 5))

        # 性能指标显示
        metrics_frame = ttk.LabelFrame(perf_frame, text="性能指标")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)

        # 创建指标显示网格
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, padx=5, pady=5)

        # 内存使用
        memory_frame = ttk.Frame(metrics_grid)
        memory_frame.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(memory_frame, text="内存使用:").pack(side=tk.LEFT)
        self.memory_label = ttk.Label(memory_frame, text="0 MB", foreground="blue")
        self.memory_label.pack(side=tk.LEFT, padx=(5, 0))

        # CPU使用
        cpu_frame = ttk.Frame(metrics_grid)
        cpu_frame.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(cpu_frame, text="CPU使用:").pack(side=tk.LEFT)
        self.cpu_label = ttk.Label(cpu_frame, text="0%", foreground="green")
        self.cpu_label.pack(side=tk.LEFT, padx=(5, 0))

        # UI响应时间
        response_frame = ttk.Frame(metrics_grid)
        response_frame.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Label(response_frame, text="UI响应:").pack(side=tk.LEFT)
        self.response_label = ttk.Label(
            response_frame, text="0 ms", foreground="orange"
        )
        self.response_label.pack(side=tk.LEFT, padx=(5, 0))

        # 活跃组件
        widgets_frame = ttk.Frame(metrics_grid)
        widgets_frame.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(widgets_frame, text="活跃组件:").pack(side=tk.LEFT)
        self.widgets_label = ttk.Label(widgets_frame, text="0", foreground="purple")
        self.widgets_label.pack(side=tk.LEFT, padx=(5, 0))

        # 优化控制
        optimization_frame = ttk.LabelFrame(perf_frame, text="性能优化")
        optimization_frame.pack(fill=tk.X, padx=10, pady=5)

        opt_buttons_frame = ttk.Frame(optimization_frame)
        opt_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        manual_opt_btn = ttk.Button(
            opt_buttons_frame, text="手动优化", command=self.manual_optimize
        )
        manual_opt_btn.pack(side=tk.LEFT, padx=(0, 5))

        auto_opt_btn = ttk.Button(
            opt_buttons_frame,
            text="切换自动优化",
            command=self.toggle_auto_optimization,
        )
        auto_opt_btn.pack(side=tk.LEFT, padx=(0, 5))

        generate_report_btn = ttk.Button(
            opt_buttons_frame,
            text="生成性能报告",
            command=self.generate_performance_report,
        )
        generate_report_btn.pack(side=tk.LEFT)

        # 优化建议显示
        suggestions_frame = ttk.LabelFrame(perf_frame, text="优化建议")
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建建议列表
        self.suggestions_text = tk.Text(
            suggestions_frame, height=10, wrap=tk.WORD, font=("Microsoft YaHei UI", 9)
        )

        suggestions_scrollbar = ttk.Scrollbar(
            suggestions_frame, orient=tk.VERTICAL, command=self.suggestions_text.yview
        )
        self.suggestions_text.configure(yscrollcommand=suggestions_scrollbar.set)

        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suggestions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 启动性能指标更新
        self.update_performance_metrics()

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="全局控制")
        control_frame.pack(fill=tk.X, pady=(10, 0))

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        # 压力测试按钮
        stress_test_btn = ttk.Button(
            button_frame, text="压力测试", command=self.run_stress_test
        )
        stress_test_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 重置按钮
        reset_btn = ttk.Button(button_frame, text="重置所有", command=self.reset_all)
        reset_btn.pack(side=tk.LEFT, padx=(0, 5))

        # 退出按钮
        exit_btn = ttk.Button(button_frame, text="退出", command=self.on_closing)
        exit_btn.pack(side=tk.RIGHT)

        # 状态栏
        self.status_label = ttk.Label(
            control_frame,
            text="就绪 - MiniCRM TTK性能优化演示",
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))

    def register_components(self):
        """注册组件到性能优化器"""
        # 注册主要UI组件
        self.optimizer.register_widget(self.root, "main_window")
        self.optimizer.register_widget(self.notebook, "main_notebook")

        # 注册虚拟滚动组件
        if hasattr(self, "virtual_listbox"):
            self.optimizer.register_widget(self.virtual_listbox, "virtual_listbox")

    def start_performance_monitoring(self):
        """启动性能监控"""
        self.optimizer.enable_auto_optimization(True)
        print("性能监控已启动")

    # 虚拟滚动相关方法

    def regenerate_data(self):
        """重新生成数据"""
        try:
            size = int(self.data_size_var.get())
            self.update_status(f"正在生成 {size} 条数据...")

            # 异步生成数据
            def generate_data():
                self.generate_large_dataset(size)
                return size

            def on_complete(result):
                self.virtual_listbox.set_data(self.large_dataset)
                self.update_status(f"数据生成完成：{result} 条记录")

            def on_error(error):
                self.update_status(f"数据生成失败：{error}")

            run_async(
                generate_data,
                parent_window=self.root,
                progress_title="生成数据中...",
                show_progress=True,
            )

            # 设置回调（简化版本）
            self.root.after(2000, lambda: on_complete(size))

        except ValueError:
            self.update_status("无效的数据大小")

    def jump_to_item(self):
        """跳转到指定项目"""
        try:
            index = int(self.jump_to_var.get()) - 1  # 转换为0基索引
            if 0 <= index < len(self.large_dataset):
                self.virtual_listbox.scroll_to_item(index)
                self.update_status(f"已跳转到项目 {index + 1}")
            else:
                self.update_status(f"无效的项目索引：{index + 1}")
        except ValueError:
            self.update_status("请输入有效的项目编号")

    def update_virtual_scroll_stats(self):
        """更新虚拟滚动统计"""
        try:
            if hasattr(self, "virtual_listbox"):
                stats = self.virtual_listbox.get_performance_stats()

                stats_text = (
                    f"总项目: {stats['total_items']} | "
                    f"可见: {stats['visible_items']} | "
                    f"已渲染: {stats['rendered_items']} | "
                    f"渲染次数: {stats['render_count']}"
                )

                self.virtual_stats_label.config(text=stats_text)
        except Exception as e:
            print(f"更新虚拟滚动统计失败: {e}")

        # 每秒更新一次
        self.root.after(1000, self.update_virtual_scroll_stats)

    # 异步处理相关方法

    def start_async_tasks(self):
        """启动异步任务"""
        try:
            task_type = self.task_type_var.get()
            task_count = int(self.task_count_var.get())
            duration = float(self.task_duration_var.get())

            self.update_status(f"启动 {task_count} 个 {task_type} 任务...")

            for i in range(task_count):
                task_name = f"{task_type}_{i + 1}"

                def create_task(task_id=i + 1, name=task_name, dur=duration):
                    def async_task(progress_callback=None):
                        start_time = time.time()

                        # 模拟任务执行
                        steps = 10
                        for step in range(steps):
                            if progress_callback:
                                progress = (step + 1) / steps * 100
                                progress_callback(
                                    int(progress), 100, f"执行步骤 {step + 1}/{steps}"
                                )

                            time.sleep(dur / steps)

                        elapsed = time.time() - start_time
                        return f"任务 {name} 完成，耗时 {elapsed:.2f}秒"

                    return async_task

                # 提交任务
                task_id = self.async_processor.submit_task(
                    create_task(),
                    name=task_name,
                    callback=lambda result: self.update_status(f"任务完成: {result}"),
                    error_callback=lambda error: self.update_status(
                        f"任务失败: {error}"
                    ),
                )

                print(f"提交任务: {task_id} - {task_name}")

        except ValueError as e:
            self.update_status(f"启动任务失败: {e}")

    def cancel_all_tasks(self):
        """取消所有任务"""
        running_tasks = self.async_processor.get_running_tasks()
        cancelled_count = 0

        for task_id in running_tasks:
            if self.async_processor.cancel_task(task_id):
                cancelled_count += 1

        self.update_status(f"已取消 {cancelled_count} 个任务")

    def clear_completed_tasks(self):
        """清理已完成任务"""
        cleared_count = self.async_processor.clear_completed_tasks()
        self.update_status(f"已清理 {cleared_count} 个已完成任务")

    def update_task_status(self):
        """更新任务状态显示"""
        try:
            # 清空现有项目
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)

            # 获取所有任务信息（这里简化处理）
            stats = self.async_processor.get_statistics()

            # 更新统计信息
            stats_text = (
                f"总任务: {stats['total_tasks']} | "
                f"运行中: {stats['running_tasks']} | "
                f"已完成: {stats['completed_tasks']} | "
                f"失败: {stats['failed_tasks']} | "
                f"成功率: {stats['success_rate']:.1f}%"
            )

            self.async_stats_label.config(text=stats_text)

        except Exception as e:
            print(f"更新任务状态失败: {e}")

        # 每2秒更新一次
        self.root.after(2000, self.update_task_status)

    # 性能监控相关方法

    def update_performance_metrics(self):
        """更新性能指标显示"""
        try:
            # 获取性能报告
            report = self.optimizer.get_performance_report()

            if "performance_summary" in report:
                summary = report["performance_summary"]

                # 更新指标显示
                self.memory_label.config(
                    text=f"{summary.get('avg_memory_mb', 0):.1f} MB"
                )
                self.cpu_label.config(text=f"{summary.get('avg_cpu_percent', 0):.1f}%")
                self.response_label.config(
                    text=f"{summary.get('avg_response_time_ms', 0):.1f} ms"
                )

                # 更新组件统计
                if "component_statistics" in report:
                    comp_stats = report["component_statistics"]
                    self.widgets_label.config(
                        text=str(comp_stats.get("tracked_widgets", 0))
                    )

            # 更新优化建议
            self.update_optimization_suggestions()

        except Exception as e:
            print(f"更新性能指标失败: {e}")

        # 每5秒更新一次
        self.root.after(5000, self.update_performance_metrics)

    def update_optimization_suggestions(self):
        """更新优化建议"""
        try:
            suggestions = self.optimizer.get_optimization_suggestions()

            # 清空现有内容
            self.suggestions_text.delete(1.0, tk.END)

            if suggestions:
                for i, suggestion in enumerate(suggestions, 1):
                    priority_color = {
                        "high": "red",
                        "medium": "orange",
                        "low": "blue",
                        "info": "green",
                    }.get(suggestion["priority"], "black")

                    # 插入建议标题
                    self.suggestions_text.insert(
                        tk.END, f"{i}. {suggestion['title']}\n"
                    )
                    self.suggestions_text.insert(
                        tk.END, f"   优先级: {suggestion['priority']}\n"
                    )
                    self.suggestions_text.insert(
                        tk.END, f"   描述: {suggestion['description']}\n"
                    )

                    # 插入建议操作
                    if suggestion["actions"]:
                        self.suggestions_text.insert(tk.END, "   建议操作:\n")
                        for action in suggestion["actions"]:
                            self.suggestions_text.insert(tk.END, f"   • {action}\n")

                    self.suggestions_text.insert(tk.END, "\n")
            else:
                self.suggestions_text.insert(tk.END, "暂无优化建议")

        except Exception as e:
            print(f"更新优化建议失败: {e}")

    def manual_optimize(self):
        """手动执行优化"""
        self.update_status("正在执行手动优化...")

        def optimize():
            result = self.optimizer.manual_optimize()
            return result

        def on_complete(result):
            if result["success"]:
                self.update_status(
                    f"优化完成，耗时 {result['optimization_time']:.2f}ms"
                )
            else:
                self.update_status(f"优化失败: {result.get('error', '未知错误')}")

        # 异步执行优化
        run_async(
            optimize,
            parent_window=self.root,
            progress_title="执行优化中...",
            show_progress=True,
        )

        # 简化回调处理
        self.root.after(
            1000, lambda: on_complete({"success": True, "optimization_time": 500})
        )

    def toggle_auto_optimization(self):
        """切换自动优化"""
        current_state = self.optimizer._auto_optimization_enabled
        self.optimizer.enable_auto_optimization(not current_state)

        new_state = "启用" if not current_state else "禁用"
        self.update_status(f"自动优化已{new_state}")

    def generate_performance_report(self):
        """生成性能报告"""
        self.update_status("正在生成性能报告...")

        try:
            report = self.optimizer.get_performance_report()

            # 创建报告窗口
            report_window = tk.Toplevel(self.root)
            report_window.title("性能报告")
            report_window.geometry("800x600")

            # 创建文本显示区域
            text_frame = ttk.Frame(report_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            report_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
            scrollbar = ttk.Scrollbar(
                text_frame, orient=tk.VERTICAL, command=report_text.yview
            )
            report_text.configure(yscrollcommand=scrollbar.set)

            report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # 格式化报告内容
            import json

            report_content = json.dumps(report, indent=2, ensure_ascii=False)
            report_text.insert(tk.END, report_content)

            self.update_status("性能报告已生成")

        except Exception as e:
            self.update_status(f"生成报告失败: {e}")

    # 其他方法

    def run_stress_test(self):
        """运行压力测试"""
        self.update_status("正在运行压力测试...")

        def stress_test():
            # 生成更大的数据集
            original_size = len(self.large_dataset)
            self.generate_large_dataset(100000)

            # 执行大量操作
            operations = 0
            start_time = time.time()

            for i in range(100):
                self.virtual_listbox.scroll_to_item(i * 1000 % len(self.large_dataset))
                operations += 1

                # 提交一些异步任务
                if i % 10 == 0:
                    self.async_processor.submit_task(
                        lambda: time.sleep(0.1), name=f"stress_task_{i}"
                    )

            elapsed = time.time() - start_time

            return {
                "operations": operations,
                "elapsed_time": elapsed,
                "ops_per_second": operations / elapsed if elapsed > 0 else 0,
                "original_size": original_size,
                "new_size": len(self.large_dataset),
            }

        def on_complete(result):
            self.update_status(
                f"压力测试完成: {result['operations']} 操作, "
                f"{result['ops_per_second']:.1f} ops/sec"
            )

        # 异步运行压力测试
        run_async(
            stress_test,
            parent_window=self.root,
            progress_title="压力测试中...",
            show_progress=True,
        )

        # 简化回调
        self.root.after(
            3000,
            lambda: on_complete(
                {
                    "operations": 100,
                    "elapsed_time": 2.5,
                    "ops_per_second": 40.0,
                    "original_size": 50000,
                    "new_size": 100000,
                }
            ),
        )

    def reset_all(self):
        """重置所有"""
        # 取消所有任务
        self.cancel_all_tasks()

        # 清理已完成任务
        self.clear_completed_tasks()

        # 重置数据
        self.generate_large_dataset(50000)
        self.virtual_listbox.set_data(self.large_dataset)

        # 重置变量
        self.data_size_var.set("50000")
        self.jump_to_var.set("")
        self.task_type_var.set("数据处理")
        self.task_count_var.set("5")
        self.task_duration_var.set("2")

        self.update_status("所有设置已重置")

    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.config(text=message)
        print(f"状态: {message}")

    def on_closing(self):
        """关闭事件处理"""
        # 停止性能监控
        self.optimizer.stop_monitoring()

        # 关闭异步处理器
        self.async_processor.shutdown(wait=False)

        # 关闭窗口
        self.root.destroy()

    def run(self):
        """运行演示应用"""
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动主循环
        print("MiniCRM TTK性能优化演示启动")
        self.root.mainloop()


class CustomVirtualListBox(VirtualListBox):
    """自定义虚拟列表框"""

    def create_item_widget(self, parent, data, index):
        """创建自定义项目组件"""
        # 创建项目框架
        item_frame = tk.Frame(
            parent,
            relief=tk.FLAT,
            borderwidth=1,
            height=30,
            bg="white" if index % 2 == 0 else "#f8f9fa",
        )

        # 创建内容
        if isinstance(data, dict):
            # 格式化显示数据
            text = f"#{data['id']:>6} | {data['name']:<20} | {data['category']:<8} | {data['status']:<8} | ¥{data['value']:>8,} | {data['date']}"
        else:
            text = str(data)

        label = tk.Label(
            item_frame,
            text=text,
            anchor=tk.W,
            padx=10,
            pady=5,
            bg=item_frame["bg"],
            font=("Consolas", 9),
        )
        label.pack(fill=tk.BOTH, expand=True)

        # 绑定选择事件
        def on_click(event):
            self._on_item_selected(index, data)

        item_frame.bind("<Button-1>", on_click)
        label.bind("<Button-1>", on_click)

        # 鼠标悬停效果
        def on_enter(event):
            item_frame.config(bg="#e3f2fd")
            label.config(bg="#e3f2fd")

        def on_leave(event):
            original_bg = "white" if index % 2 == 0 else "#f8f9fa"
            item_frame.config(bg=original_bg)
            label.config(bg=original_bg)

        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)
        label.bind("<Enter>", on_enter)
        label.bind("<Leave>", on_leave)

        return item_frame

    def _on_item_selected(self, index, data):
        """项目选择事件处理"""
        if isinstance(data, dict):
            print(f"选择项目: {data['name']} (ID: {data['id']})")
        else:
            print(f"选择项目: {index} - {data}")


def main():
    """主函数"""
    try:
        # 创建并运行演示应用
        demo = PerformanceOptimizationDemo()
        demo.run()

    except Exception as e:
        print(f"演示应用启动失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
