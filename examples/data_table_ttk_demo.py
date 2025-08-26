#!/usr/bin/env python3
"""MiniCRM TTK数据表格组件演示

展示DataTableTTK组件的完整功能，包括：
- 数据加载和显示
- 排序功能
- 筛选功能
- 分页功能
- 导出功能
- 多选和单选
"""

import os
import sys
import tkinter as tk
from tkinter import ttk


# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.minicrm.ui.ttk_base.data_table_ttk import DataTableTTK


def create_sample_data():
    """创建示例数据"""
    data = []
    cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉"]
    departments = ["技术部", "销售部", "市场部", "人事部", "财务部"]

    for i in range(50):
        data.append(
            {
                "id": str(i + 1),
                "name": f"员工{i + 1:02d}",
                "age": str(25 + (i % 30)),
                "city": cities[i % len(cities)],
                "department": departments[i % len(departments)],
                "salary": str(5000 + (i % 20) * 1000),
                "phone": f"138{i:04d}{(i * 7) % 10000:04d}",
                "email": f"user{i + 1:02d}@company.com",
            }
        )

    return data


class DataTableDemo:
    """数据表格演示应用"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MiniCRM TTK数据表格组件演示")
        self.root.geometry("1200x800")

        # 设置样式
        self.setup_styles()

        # 创建UI
        self.setup_ui()

        # 加载示例数据
        self.load_sample_data()

    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()

        # 设置主题
        try:
            style.theme_use("clam")
        except:
            pass

        # 自定义样式
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 10))

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame, text="MiniCRM TTK数据表格组件演示", style="Title.TLabel"
        )
        title_label.pack(pady=(0, 10))

        # 说明文字
        desc_label = ttk.Label(
            main_frame,
            text="此演示展示了TTK数据表格的完整功能：数据显示、排序、筛选、分页、导出等",
            style="Subtitle.TLabel",
        )
        desc_label.pack(pady=(0, 20))

        # 控制面板
        self.create_control_panel(main_frame)

        # 数据表格
        self.create_data_table(main_frame)

    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行控件
        row1_frame = ttk.Frame(control_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))

        # 数据操作按钮
        ttk.Button(row1_frame, text="重新加载数据", command=self.load_sample_data).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(row1_frame, text="清空数据", command=self.clear_data).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(row1_frame, text="添加随机数据", command=self.add_random_data).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        # 分隔符
        ttk.Separator(row1_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=10
        )

        # 选择操作按钮
        ttk.Button(row1_frame, text="全选", command=self.select_all).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(row1_frame, text="清除选择", command=self.clear_selection).pack(
            side=tk.LEFT, padx=(0, 5)
        )

        ttk.Button(
            row1_frame, text="获取选中数据", command=self.show_selected_data
        ).pack(side=tk.LEFT, padx=(0, 5))

        # 第二行控件
        row2_frame = ttk.Frame(control_frame)
        row2_frame.pack(fill=tk.X, pady=(5, 0))

        # 状态信息
        self.status_label = ttk.Label(row2_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)

        # 右侧信息
        info_frame = ttk.Frame(row2_frame)
        info_frame.pack(side=tk.RIGHT)

        self.info_label = ttk.Label(info_frame, text="")
        self.info_label.pack()

    def create_data_table(self, parent):
        """创建数据表格"""
        # 定义列
        columns = [
            {"id": "id", "text": "ID", "width": 60},
            {"id": "name", "text": "姓名", "width": 100},
            {"id": "age", "text": "年龄", "width": 60},
            {"id": "city", "text": "城市", "width": 80},
            {"id": "department", "text": "部门", "width": 100},
            {"id": "salary", "text": "薪资", "width": 80},
            {"id": "phone", "text": "电话", "width": 120},
            {"id": "email", "text": "邮箱", "width": 180},
        ]

        # 创建数据表格
        self.data_table = DataTableTTK(
            parent,
            columns=columns,
            editable=False,
            multi_select=True,
            show_pagination=True,
            page_size=15,
            enable_virtual_scroll=False,
        )
        self.data_table.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.data_table.on_row_selected = self.on_row_selected
        self.data_table.on_row_double_clicked = self.on_row_double_clicked
        self.data_table.on_selection_changed = self.on_selection_changed

    def load_sample_data(self):
        """加载示例数据"""
        data = create_sample_data()
        self.data_table.load_data(data)
        self.update_status(f"已加载 {len(data)} 条示例数据")
        self.update_info()

    def clear_data(self):
        """清空数据"""
        self.data_table.load_data([])
        self.update_status("数据已清空")
        self.update_info()

    def add_random_data(self):
        """添加随机数据"""
        import random

        new_data = {
            "id": str(len(self.data_table.data) + 1),
            "name": f"新员工{random.randint(1, 999):03d}",
            "age": str(random.randint(22, 55)),
            "city": random.choice(["北京", "上海", "广州", "深圳"]),
            "department": random.choice(["技术部", "销售部", "市场部"]),
            "salary": str(random.randint(5000, 20000)),
            "phone": f"138{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            "email": f"newuser{random.randint(1, 999)}@company.com",
        }

        # 添加到现有数据
        current_data = self.data_table.data.copy()
        current_data.append(new_data)
        self.data_table.load_data(current_data)

        self.update_status("已添加一条随机数据")
        self.update_info()

    def select_all(self):
        """全选"""
        self.data_table.select_all()
        self.update_status("已全选当前页数据")

    def clear_selection(self):
        """清除选择"""
        self.data_table.clear_selection()
        self.update_status("已清除选择")

    def show_selected_data(self):
        """显示选中的数据"""
        selected_data = self.data_table.get_selected_data()

        if not selected_data:
            self.update_status("没有选中任何数据")
            return

        # 创建显示窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("选中的数据")
        dialog.geometry("600x400")
        dialog.transient(self.root)

        # 创建文本框显示数据
        text_frame = ttk.Frame(dialog, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=text_widget.yview
        )
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 插入数据
        text_widget.insert(tk.END, f"选中了 {len(selected_data)} 条数据:\n\n")
        for i, row in enumerate(selected_data, 1):
            text_widget.insert(tk.END, f"第 {i} 条:\n")
            for key, value in row.items():
                text_widget.insert(tk.END, f"  {key}: {value}\n")
            text_widget.insert(tk.END, "\n")

        text_widget.config(state=tk.DISABLED)

        # 关闭按钮
        ttk.Button(dialog, text="关闭", command=dialog.destroy).pack(pady=10)

        self.update_status(f"显示了 {len(selected_data)} 条选中数据")

    def on_row_selected(self, row_data):
        """行选择事件"""
        self.update_status(f"选中了: {row_data.get('name', 'Unknown')}")

    def on_row_double_clicked(self, row_data):
        """行双击事件"""
        # 显示详细信息
        dialog = tk.Toplevel(self.root)
        dialog.title("详细信息")
        dialog.geometry("400x300")
        dialog.transient(self.root)

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main_frame,
            text=f"{row_data.get('name', 'Unknown')} 的详细信息",
            font=("Microsoft YaHei UI", 12, "bold"),
        ).pack(pady=(0, 10))

        # 显示所有字段
        for key, value in row_data.items():
            row_frame = ttk.Frame(main_frame)
            row_frame.pack(fill=tk.X, pady=2)

            ttk.Label(row_frame, text=f"{key}:", width=10).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value)).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Button(main_frame, text="关闭", command=dialog.destroy).pack(pady=(20, 0))

        self.update_status(f"查看 {row_data.get('name', 'Unknown')} 的详细信息")

    def on_selection_changed(self, selected_data):
        """选择变化事件"""
        count = len(selected_data)
        if count == 0:
            self.update_status("没有选中任何数据")
        else:
            self.update_status(f"选中了 {count} 条数据")

    def update_status(self, message):
        """更新状态信息"""
        self.status_label.config(text=f"状态: {message}")

    def update_info(self):
        """更新信息显示"""
        total = len(self.data_table.data)
        filtered = len(self.data_table.filtered_data)

        if total == filtered:
            info_text = f"总计: {total} 条记录"
        else:
            info_text = f"显示: {filtered} / {total} 条记录"

        self.info_label.config(text=info_text)

    def run(self):
        """运行应用"""
        self.root.mainloop()


def main():
    """主函数"""
    print("启动MiniCRM TTK数据表格组件演示...")

    try:
        app = DataTableDemo()
        app.run()
    except Exception as e:
        print(f"演示运行出错: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
