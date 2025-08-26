"""TTK主题系统演示

演示TTK主题系统的各项功能，包括：
- 主题切换演示
- 自定义主题创建
- 主题编辑器使用
- 主题导入导出
- 实时主题预览

使用方法:
    python examples/theme_system_demo.py

作者: MiniCRM开发团队
"""

import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, ttk


# 添加src路径以便导入模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from minicrm.ui.ttk_base.style_manager import ThemeType
from minicrm.ui.ttk_base.theme_editor import show_theme_editor
from minicrm.ui.ttk_base.theme_manager import TTKThemeManager


class ThemeSystemDemo:
    """TTK主题系统演示应用"""

    def __init__(self):
        """初始化演示应用"""
        self.root = tk.Tk()
        self.root.title("MiniCRM TTK主题系统演示")
        self.root.geometry("800x600")

        # 创建主题管理器
        self.theme_manager = TTKThemeManager(self.root)

        # 设置UI
        self._setup_ui()

        # 绑定主题变化回调
        self.theme_manager.add_theme_change_callback(self._on_theme_changed)

    def _setup_ui(self):
        """设置用户界面"""
        # 创建主容器
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="MiniCRM TTK主题系统演示",
            font=("Microsoft YaHei UI", 16, "bold"),
        )
        title_label.pack(pady=(0, 20))

        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 主题切换选项卡
        self._create_theme_switch_tab(notebook)

        # 自定义主题选项卡
        self._create_custom_theme_tab(notebook)

        # 组件预览选项卡
        self._create_preview_tab(notebook)

        # 主题管理选项卡
        self._create_management_tab(notebook)

    def _create_theme_switch_tab(self, parent):
        """创建主题切换选项卡"""
        frame = ttk.Frame(parent, padding=20)
        parent.add(frame, text="主题切换")

        # 说明文本
        desc_label = ttk.Label(
            frame,
            text="选择不同的主题来查看界面效果变化：",
            font=("Microsoft YaHei UI", 10),
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # 主题选择区域
        theme_frame = ttk.LabelFrame(frame, text="可用主题", padding=15)
        theme_frame.pack(fill=tk.X, pady=(0, 20))

        # 获取可用主题
        available_themes = self.theme_manager.get_available_themes()

        # 创建主题选择按钮
        self.theme_var = tk.StringVar(value=self.theme_manager.get_current_theme())

        for theme_id, theme_name in available_themes.items():
            radio = ttk.Radiobutton(
                theme_frame,
                text=f"{theme_name} ({theme_id})",
                variable=self.theme_var,
                value=theme_id,
                command=lambda: self._switch_theme(self.theme_var.get()),
            )
            radio.pack(anchor="w", pady=2)

        # 当前主题信息
        info_frame = ttk.LabelFrame(frame, text="当前主题信息", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        self.current_theme_label = ttk.Label(info_frame, text="")
        self.current_theme_label.pack(anchor="w")

        # 更新当前主题信息
        self._update_theme_info()

    def _create_custom_theme_tab(self, parent):
        """创建自定义主题选项卡"""
        frame = ttk.Frame(parent, padding=20)
        parent.add(frame, text="自定义主题")

        # 说明文本
        desc_label = ttk.Label(
            frame, text="创建和管理自定义主题：", font=("Microsoft YaHei UI", 10)
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # 快速创建区域
        quick_frame = ttk.LabelFrame(frame, text="快速创建主题", padding=15)
        quick_frame.pack(fill=tk.X, pady=(0, 20))

        # 主题名称
        name_frame = ttk.Frame(quick_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="主题名称:").pack(side=tk.LEFT, padx=(0, 10))
        self.custom_name_var = tk.StringVar(value="我的自定义主题")
        ttk.Entry(name_frame, textvariable=self.custom_name_var, width=30).pack(
            side=tk.LEFT
        )

        # 基础主题
        base_frame = ttk.Frame(quick_frame)
        base_frame.pack(fill=tk.X, pady=5)

        ttk.Label(base_frame, text="基础主题:").pack(side=tk.LEFT, padx=(0, 10))
        self.base_theme_var = tk.StringVar(value=ThemeType.DEFAULT.value)
        base_combo = ttk.Combobox(
            base_frame,
            textvariable=self.base_theme_var,
            values=list(self.theme_manager.get_available_themes().keys()),
            state="readonly",
            width=25,
        )
        base_combo.pack(side=tk.LEFT)

        # 主色调
        color_frame = ttk.Frame(quick_frame)
        color_frame.pack(fill=tk.X, pady=5)

        ttk.Label(color_frame, text="主色调:").pack(side=tk.LEFT, padx=(0, 10))
        self.primary_color_var = tk.StringVar(value="#2196F3")
        ttk.Entry(color_frame, textvariable=self.primary_color_var, width=10).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # 创建按钮
        ttk.Button(
            quick_frame, text="创建自定义主题", command=self._create_custom_theme
        ).pack(pady=10)

        # 高级编辑区域
        advanced_frame = ttk.LabelFrame(frame, text="高级编辑", padding=15)
        advanced_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(advanced_frame, text="使用主题编辑器进行详细的主题自定义：").pack(
            anchor="w", pady=(0, 10)
        )

        ttk.Button(
            advanced_frame, text="打开主题编辑器", command=self._open_theme_editor
        ).pack()

    def _create_preview_tab(self, parent):
        """创建组件预览选项卡"""
        frame = ttk.Frame(parent, padding=20)
        parent.add(frame, text="组件预览")

        # 说明文本
        desc_label = ttk.Label(
            frame,
            text="预览各种TTK组件在当前主题下的效果：",
            font=("Microsoft YaHei UI", 10),
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # 创建滚动区域
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 按钮组件
        button_frame = ttk.LabelFrame(scrollable_frame, text="按钮组件", padding=10)
        button_frame.pack(fill=tk.X, pady=5)

        buttons_row = ttk.Frame(button_frame)
        buttons_row.pack(fill=tk.X)

        ttk.Button(buttons_row, text="普通按钮").pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_row, text="禁用按钮", state="disabled").pack(
            side=tk.LEFT, padx=5
        )

        # 输入组件
        input_frame = ttk.LabelFrame(scrollable_frame, text="输入组件", padding=10)
        input_frame.pack(fill=tk.X, pady=5)

        # 文本框
        entry_row = ttk.Frame(input_frame)
        entry_row.pack(fill=tk.X, pady=2)
        ttk.Label(entry_row, text="文本框:", width=10).pack(side=tk.LEFT)
        entry = ttk.Entry(entry_row, width=30)
        entry.pack(side=tk.LEFT, padx=5)
        entry.insert(0, "示例文本")

        # 下拉框
        combo_row = ttk.Frame(input_frame)
        combo_row.pack(fill=tk.X, pady=2)
        ttk.Label(combo_row, text="下拉框:", width=10).pack(side=tk.LEFT)
        combo = ttk.Combobox(
            combo_row, values=["选项1", "选项2", "选项3"], width=27, state="readonly"
        )
        combo.pack(side=tk.LEFT, padx=5)
        combo.set("选项1")

        # 选择组件
        choice_frame = ttk.LabelFrame(scrollable_frame, text="选择组件", padding=10)
        choice_frame.pack(fill=tk.X, pady=5)

        # 复选框
        check_row = ttk.Frame(choice_frame)
        check_row.pack(fill=tk.X, pady=2)
        ttk.Label(check_row, text="复选框:", width=10).pack(side=tk.LEFT)
        ttk.Checkbutton(check_row, text="选项A").pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(check_row, text="选项B").pack(side=tk.LEFT, padx=5)

        # 单选框
        radio_row = ttk.Frame(choice_frame)
        radio_row.pack(fill=tk.X, pady=2)
        ttk.Label(radio_row, text="单选框:", width=10).pack(side=tk.LEFT)
        radio_var = tk.StringVar(value="选项1")
        ttk.Radiobutton(
            radio_row, text="选项1", variable=radio_var, value="选项1"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            radio_row, text="选项2", variable=radio_var, value="选项2"
        ).pack(side=tk.LEFT, padx=5)

        # 进度条
        progress_frame = ttk.LabelFrame(scrollable_frame, text="进度组件", padding=10)
        progress_frame.pack(fill=tk.X, pady=5)

        progress_row = ttk.Frame(progress_frame)
        progress_row.pack(fill=tk.X, pady=2)
        ttk.Label(progress_row, text="进度条:", width=10).pack(side=tk.LEFT)
        progress = ttk.Progressbar(progress_row, length=300, mode="determinate")
        progress.pack(side=tk.LEFT, padx=5)
        progress["value"] = 65

        # 表格组件
        tree_frame = ttk.LabelFrame(scrollable_frame, text="表格组件", padding=10)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 创建表格
        columns = ("列1", "列2", "列3", "列4")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)

        # 配置列
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 添加示例数据
        for i in range(8):
            tree.insert(
                "",
                "end",
                values=(
                    f"数据{i + 1}A",
                    f"数据{i + 1}B",
                    f"数据{i + 1}C",
                    f"数据{i + 1}D",
                ),
            )

        tree.pack(fill=tk.BOTH, expand=True)

        # 配置滚动
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _create_management_tab(self, parent):
        """创建主题管理选项卡"""
        frame = ttk.Frame(parent, padding=20)
        parent.add(frame, text="主题管理")

        # 说明文本
        desc_label = ttk.Label(
            frame, text="管理主题配置和导入导出：", font=("Microsoft YaHei UI", 10)
        )
        desc_label.pack(anchor="w", pady=(0, 10))

        # 导入导出区域
        io_frame = ttk.LabelFrame(frame, text="导入导出", padding=15)
        io_frame.pack(fill=tk.X, pady=(0, 20))

        # 导出当前主题
        export_frame = ttk.Frame(io_frame)
        export_frame.pack(fill=tk.X, pady=5)

        ttk.Label(export_frame, text="导出当前主题:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            export_frame, text="导出主题", command=self._export_current_theme
        ).pack(side=tk.LEFT)

        # 导入主题
        import_frame = ttk.Frame(io_frame)
        import_frame.pack(fill=tk.X, pady=5)

        ttk.Label(import_frame, text="导入主题文件:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(import_frame, text="导入主题", command=self._import_theme).pack(
            side=tk.LEFT
        )

        # 主题列表区域
        list_frame = ttk.LabelFrame(frame, text="已安装主题", padding=15)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # 创建主题列表
        self.theme_listbox = tk.Listbox(list_frame, height=8)
        self.theme_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 刷新主题列表
        self._refresh_theme_list()

        # 主题操作按钮
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame, text="应用选中主题", command=self._apply_selected_theme
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="删除选中主题", command=self._delete_selected_theme
        ).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            button_frame, text="刷新列表", command=self._refresh_theme_list
        ).pack(side=tk.LEFT)

    def _switch_theme(self, theme_id):
        """切换主题"""
        success = self.theme_manager.set_theme(theme_id)
        if success:
            self._update_theme_info()
        else:
            messagebox.showerror("错误", f"切换主题失败: {theme_id}")

    def _update_theme_info(self):
        """更新当前主题信息"""
        current_theme = self.theme_manager.get_current_theme()
        theme_config = self.theme_manager.get_theme_config(current_theme)

        info_text = f"当前主题: {current_theme}\n"
        info_text += f"主题名称: {theme_config.get('name', '未知')}\n"

        colors = theme_config.get("colors", {})
        info_text += f"主色调: {colors.get('primary', '未设置')}\n"
        info_text += f"背景色: {colors.get('bg_primary', '未设置')}\n"

        fonts = theme_config.get("fonts", {})
        default_font = fonts.get("default", {})
        info_text += f"默认字体: {default_font.get('family', '未设置')} {default_font.get('size', '')}px"

        self.current_theme_label.configure(text=info_text)

    def _create_custom_theme(self):
        """创建自定义主题"""
        theme_name = self.custom_name_var.get().strip()
        if not theme_name:
            messagebox.showerror("错误", "请输入主题名称！")
            return

        base_theme = self.base_theme_var.get()
        primary_color = self.primary_color_var.get().strip()

        # 验证颜色格式
        if not primary_color.startswith("#") or len(primary_color) != 7:
            messagebox.showerror("错误", "请输入有效的颜色值（如 #FF0000）！")
            return

        # 生成主题ID
        theme_id = (
            theme_name.lower().replace(" ", "_").replace("的", "").replace("主题", "")
        )

        # 创建自定义主题
        success = self.theme_manager.create_custom_theme(
            theme_id,
            theme_name,
            base_theme=base_theme,
            colors={"primary": primary_color},
        )

        if success:
            messagebox.showinfo("成功", f"自定义主题 '{theme_name}' 创建成功！")

            # 刷新主题列表和选择
            self._refresh_theme_list()

            # 询问是否应用新主题
            if messagebox.askyesno("应用主题", "是否立即应用新创建的主题？"):
                self.theme_manager.set_theme(theme_id)
                self.theme_var.set(theme_id)
                self._update_theme_info()
        else:
            messagebox.showerror("错误", "创建自定义主题失败！")

    def _open_theme_editor(self):
        """打开主题编辑器"""
        try:
            show_theme_editor(self.root, self.theme_manager)
            # 编辑器关闭后刷新界面
            self._refresh_theme_list()
            self._update_theme_info()
        except Exception as e:
            messagebox.showerror("错误", f"打开主题编辑器失败: {e}")

    def _export_current_theme(self):
        """导出当前主题"""
        from tkinter import filedialog

        current_theme = self.theme_manager.get_current_theme()

        file_path = filedialog.asksaveasfilename(
            title="导出主题",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
            initialvalue=f"{current_theme}_theme.json",
        )

        if file_path:
            success = self.theme_manager.export_theme(current_theme, file_path)
            if success:
                messagebox.showinfo("成功", f"主题已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出主题失败！")

    def _import_theme(self):
        """导入主题"""
        from tkinter import filedialog

        file_path = filedialog.askopenfilename(
            title="导入主题", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )

        if file_path:
            # 获取文件名作为主题ID
            theme_id = Path(file_path).stem

            success = self.theme_manager.import_theme(file_path, theme_id)
            if success:
                messagebox.showinfo("成功", f"主题 '{theme_id}' 导入成功！")
                self._refresh_theme_list()
            else:
                messagebox.showerror("错误", "导入主题失败！")

    def _refresh_theme_list(self):
        """刷新主题列表"""
        self.theme_listbox.delete(0, tk.END)

        available_themes = self.theme_manager.get_available_themes()
        for theme_id, theme_name in available_themes.items():
            display_text = f"{theme_name} ({theme_id})"
            self.theme_listbox.insert(tk.END, display_text)

    def _apply_selected_theme(self):
        """应用选中的主题"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个主题！")
            return

        # 从显示文本中提取主题ID
        selected_text = self.theme_listbox.get(selection[0])
        theme_id = selected_text.split("(")[-1].rstrip(")")

        success = self.theme_manager.set_theme(theme_id)
        if success:
            self.theme_var.set(theme_id)
            self._update_theme_info()
            messagebox.showinfo("成功", f"主题 '{theme_id}' 应用成功！")
        else:
            messagebox.showerror("错误", f"应用主题 '{theme_id}' 失败！")

    def _delete_selected_theme(self):
        """删除选中的主题"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个主题！")
            return

        # 从显示文本中提取主题ID
        selected_text = self.theme_listbox.get(selection[0])
        theme_id = selected_text.split("(")[-1].rstrip(")")

        # 不能删除内置主题
        if theme_id in [
            ThemeType.DEFAULT.value,
            ThemeType.DARK.value,
            ThemeType.LIGHT.value,
            ThemeType.HIGH_CONTRAST.value,
        ]:
            messagebox.showwarning("警告", "不能删除内置主题！")
            return

        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除主题 '{theme_id}' 吗？"):
            success = self.theme_manager.delete_custom_theme(theme_id)
            if success:
                messagebox.showinfo("成功", f"主题 '{theme_id}' 删除成功！")
                self._refresh_theme_list()

                # 如果删除的是当前主题，切换到默认主题
                if self.theme_manager.get_current_theme() == theme_id:
                    self.theme_manager.reset_to_default()
                    self.theme_var.set(ThemeType.DEFAULT.value)
                    self._update_theme_info()
            else:
                messagebox.showerror("错误", f"删除主题 '{theme_id}' 失败！")

    def _on_theme_changed(self, theme_id):
        """主题变化回调"""
        print(f"主题已切换到: {theme_id}")

    def run(self):
        """运行演示应用"""
        self.root.mainloop()


def main():
    """主函数"""
    print("🎨 启动MiniCRM TTK主题系统演示...")

    try:
        # 创建并运行演示应用
        demo = ThemeSystemDemo()
        demo.run()

    except Exception as e:
        print(f"❌ 演示应用启动失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
