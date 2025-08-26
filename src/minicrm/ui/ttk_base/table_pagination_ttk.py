"""MiniCRM TTK表格分页组件

提供完整的分页控制功能,包括页面导航、页面大小设置、跳转功能等.
支持大数据集的分页显示,提供良好的用户体验.

设计特点:
- 灵活的页面大小设置
- 完整的页面导航控件
- 页面跳转功能
- 总数统计显示
- 响应式布局设计
"""

import logging
import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.ui.ttk_base.base_widget import BaseWidget


class TablePaginationTTK(BaseWidget):
    """TTK表格分页控件

    提供完整的分页功能,包括页面导航、页面大小设置、跳转等功能.
    可以独立使用,也可以集成到DataTableTTK中.
    """

    def __init__(
        self,
        parent,
        page_size: int = 50,
        page_size_options: List[int] = None,
        show_page_size_selector: bool = True,
        show_page_jumper: bool = True,
        show_total_info: bool = True,
        **kwargs,
    ):
        """初始化分页控件

        Args:
            parent: 父组件
            page_size: 默认每页显示的记录数
            page_size_options: 页面大小选项列表
            show_page_size_selector: 是否显示页面大小选择器
            show_page_jumper: 是否显示页面跳转功能
            show_total_info: 是否显示总数信息
        """
        # 分页配置
        self.page_size = page_size
        self.page_size_options = page_size_options or [10, 20, 50, 100, 200]
        self.show_page_size_selector = show_page_size_selector
        self.show_page_jumper = show_page_jumper
        self.show_total_info = show_total_info

        # 分页状态
        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0

        # UI组件
        self.page_info_label = None
        self.first_btn = None
        self.prev_btn = None
        self.next_btn = None
        self.last_btn = None
        self.page_size_combo = None
        self.page_jumper_entry = None
        self.jump_btn = None

        # 事件回调
        self.on_page_changed: Optional[Callable[[int, int], None]] = None
        self.on_page_size_changed: Optional[Callable[[int], None]] = None

        # 日志记录
        self.logger = logging.getLogger(__name__)

        super().__init__(parent, **kwargs)

    def _setup_ui(self) -> None:
        """设置UI布局"""
        # 创建主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.X, padx=5, pady=5)

        # 左侧:总数信息和页面大小选择器
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 总数信息
        if self.show_total_info:
            self._create_total_info(left_frame)

        # 页面大小选择器
        if self.show_page_size_selector:
            self._create_page_size_selector(left_frame)

        # 右侧:分页控件
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT)

        # 页面导航按钮
        self._create_navigation_buttons(right_frame)

        # 页面跳转功能
        if self.show_page_jumper:
            self._create_page_jumper(right_frame)

    def _create_total_info(self, parent) -> None:
        """创建总数信息显示"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(info_frame, text="总计:").pack(side=tk.LEFT)
        self.page_info_label = ttk.Label(info_frame, text="0 条记录")
        self.page_info_label.pack(side=tk.LEFT, padx=(5, 0))

    def _create_page_size_selector(self, parent) -> None:
        """创建页面大小选择器"""
        size_frame = ttk.Frame(parent)
        size_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(size_frame, text="每页显示:").pack(side=tk.LEFT)

        self.page_size_combo = ttk.Combobox(
            size_frame,
            values=[str(size) for size in self.page_size_options],
            width=8,
            state="readonly",
        )
        self.page_size_combo.set(str(self.page_size))
        self.page_size_combo.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(size_frame, text="条").pack(side=tk.LEFT, padx=(5, 0))

    def _create_navigation_buttons(self, parent) -> None:
        """创建页面导航按钮"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(side=tk.LEFT, padx=(0, 10))

        # 首页按钮
        self.first_btn = ttk.Button(
            nav_frame, text="首页", width=6, command=self._go_first_page
        )
        self.first_btn.pack(side=tk.LEFT, padx=2)

        # 上一页按钮
        self.prev_btn = ttk.Button(
            nav_frame, text="上页", width=6, command=self._go_prev_page
        )
        self.prev_btn.pack(side=tk.LEFT, padx=2)

        # 页面信息
        self.current_page_label = ttk.Label(nav_frame, text="第 1 页")
        self.current_page_label.pack(side=tk.LEFT, padx=5)

        # 下一页按钮
        self.next_btn = ttk.Button(
            nav_frame, text="下页", width=6, command=self._go_next_page
        )
        self.next_btn.pack(side=tk.LEFT, padx=2)

        # 末页按钮
        self.last_btn = ttk.Button(
            nav_frame, text="末页", width=6, command=self._go_last_page
        )
        self.last_btn.pack(side=tk.LEFT, padx=2)

    def _create_page_jumper(self, parent) -> None:
        """创建页面跳转功能"""
        jump_frame = ttk.Frame(parent)
        jump_frame.pack(side=tk.LEFT)

        ttk.Label(jump_frame, text="跳转到:").pack(side=tk.LEFT)

        self.page_jumper_entry = ttk.Entry(jump_frame, width=6)
        self.page_jumper_entry.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Label(jump_frame, text="页").pack(side=tk.LEFT, padx=(5, 0))

        self.jump_btn = ttk.Button(
            jump_frame, text="跳转", width=6, command=self._jump_to_page
        )
        self.jump_btn.pack(side=tk.LEFT, padx=(5, 0))

    def _bind_events(self) -> None:
        """绑定事件"""
        # 页面大小变化事件
        if self.page_size_combo:
            self.page_size_combo.bind(
                "<<ComboboxSelected>>", self._on_page_size_changed
            )

        # 页面跳转回车事件
        if self.page_jumper_entry:
            self.page_jumper_entry.bind("<Return>", lambda e: self._jump_to_page())

    def update_pagination(self, total_records: int) -> None:
        """更新分页信息

        Args:
            total_records: 总记录数
        """
        self.total_records = total_records
        self.total_pages = max(1, math.ceil(total_records / self.page_size))

        # 确保当前页在有效范围内
        self.current_page = min(self.current_page, self.total_pages)

        self._update_ui()

        self.logger.info(
            f"更新分页信息: 总记录数={total_records}, 总页数={self.total_pages}, 当前页={self.current_page}"
        )

    def _update_ui(self) -> None:
        """更新UI显示"""
        # 更新总数信息
        if self.page_info_label:
            start_record = (self.current_page - 1) * self.page_size + 1
            end_record = min(self.current_page * self.page_size, self.total_records)

            if self.total_records == 0:
                info_text = "0 条记录"
            else:
                info_text = (
                    f"{start_record}-{end_record} 条,共 {self.total_records} 条记录"
                )

            self.page_info_label.config(text=info_text)

        # 更新当前页信息
        if self.current_page_label:
            self.current_page_label.config(
                text=f"第 {self.current_page} 页,共 {self.total_pages} 页"
            )

        # 更新按钮状态
        self._update_button_states()

    def _update_button_states(self) -> None:
        """更新按钮状态"""
        is_first_page = self.current_page == 1
        is_last_page = self.current_page == self.total_pages
        has_data = self.total_records > 0

        if self.first_btn:
            self.first_btn.config(
                state="disabled" if is_first_page or not has_data else "normal"
            )

        if self.prev_btn:
            self.prev_btn.config(
                state="disabled" if is_first_page or not has_data else "normal"
            )

        if self.next_btn:
            self.next_btn.config(
                state="disabled" if is_last_page or not has_data else "normal"
            )

        if self.last_btn:
            self.last_btn.config(
                state="disabled" if is_last_page or not has_data else "normal"
            )

        if self.jump_btn:
            self.jump_btn.config(state="disabled" if not has_data else "normal")

    def _go_first_page(self) -> None:
        """跳转到首页"""
        if self.current_page != 1:
            self.current_page = 1
            self._update_ui()
            self._emit_page_changed()

    def _go_prev_page(self) -> None:
        """跳转到上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self._update_ui()
            self._emit_page_changed()

    def _go_next_page(self) -> None:
        """跳转到下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._update_ui()
            self._emit_page_changed()

    def _go_last_page(self) -> None:
        """跳转到末页"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self._update_ui()
            self._emit_page_changed()

    def _jump_to_page(self) -> None:
        """跳转到指定页面"""
        if not self.page_jumper_entry:
            return

        try:
            target_page = int(self.page_jumper_entry.get())

            if 1 <= target_page <= self.total_pages:
                if target_page != self.current_page:
                    self.current_page = target_page
                    self._update_ui()
                    self._emit_page_changed()

                # 清空输入框
                self.page_jumper_entry.delete(0, tk.END)
            else:
                messagebox.showwarning(
                    "页面跳转", f"请输入有效的页面号 (1-{self.total_pages})"
                )

        except ValueError:
            messagebox.showwarning("页面跳转", "请输入有效的数字")

    def _on_page_size_changed(self, event) -> None:
        """处理页面大小变化"""
        if not self.page_size_combo:
            return

        try:
            new_page_size = int(self.page_size_combo.get())

            if new_page_size != self.page_size:
                # 计算当前显示的第一条记录的索引
                current_first_record = (self.current_page - 1) * self.page_size + 1

                # 更新页面大小
                self.page_size = new_page_size

                # 重新计算页面信息
                self.total_pages = max(
                    1, math.ceil(self.total_records / self.page_size)
                )

                # 计算新的当前页,尽量保持显示相同的记录
                self.current_page = max(
                    1, math.ceil(current_first_record / self.page_size)
                )

                # 确保当前页在有效范围内
                self.current_page = min(self.current_page, self.total_pages)

                self._update_ui()

                # 触发页面大小变化事件
                if self.on_page_size_changed:
                    self.on_page_size_changed(self.page_size)

                # 触发页面变化事件
                self._emit_page_changed()

                self.logger.info(f"页面大小已更改为: {self.page_size}")

        except ValueError:
            self.logger.error("无效的页面大小值")

    def _emit_page_changed(self) -> None:
        """发送页面变化事件"""
        if self.on_page_changed:
            self.on_page_changed(self.current_page, self.page_size)

    def get_current_page_range(self) -> tuple[int, int]:
        """获取当前页的数据范围

        Returns:
            (start_index, end_index): 数据的起始和结束索引
        """
        start_index = (self.current_page - 1) * self.page_size
        end_index = min(start_index + self.page_size, self.total_records)
        return start_index, end_index

    def reset_to_first_page(self) -> None:
        """重置到第一页"""
        if self.current_page != 1:
            self.current_page = 1
            self._update_ui()
            self._emit_page_changed()

    def set_page_size(self, page_size: int) -> None:
        """设置页面大小

        Args:
            page_size: 新的页面大小
        """
        if page_size > 0 and page_size != self.page_size:
            self.page_size = page_size

            # 更新页面大小选择器
            if self.page_size_combo:
                self.page_size_combo.set(str(page_size))

            # 重新计算分页信息
            self.update_pagination(self.total_records)

            # 触发页面大小变化回调
            if self.on_page_size_changed:
                self.on_page_size_changed(self.page_size)

    def get_pagination_info(self) -> Dict[str, Any]:
        """获取分页信息

        Returns:
            包含分页信息的字典
        """
        return {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "page_size": self.page_size,
            "total_records": self.total_records,
            "start_record": (self.current_page - 1) * self.page_size + 1,
            "end_record": min(self.current_page * self.page_size, self.total_records),
        }

    def cleanup(self) -> None:
        """清理资源"""
        self.on_page_changed = None
        self.on_page_size_changed = None
        self.logger.info("分页控件资源已清理")
