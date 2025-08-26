"""TTK导航面板系统

提供TTK应用程序的导航面板功能,包括:
- 导航按钮的创建和管理
- 页面切换和路由功能
- 折叠展开功能
- 导航状态保存和恢复
- 导航项分组和层级管理

设计目标:
1. 提供直观的导航界面
2. 支持多级导航结构
3. 简化导航管理和维护
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class NavigationItemConfig:
    """导航项配置类"""

    def __init__(
        self,
        item_id: str,
        text: str,
        command: Optional[Callable] = None,
        icon: Optional[str] = None,
        tooltip: str = "",
        parent_id: Optional[str] = None,
        item_type: str = "button",
        state: str = "normal",
        separator_before: bool = False,
        separator_after: bool = False,
        collapsible: bool = False,
        expanded: bool = True,
        badge_text: str = "",
        badge_color: str = "red",
    ):
        """初始化导航项配置

        Args:
            item_id: 导航项唯一标识
            text: 显示文本
            command: 点击命令
            icon: 图标路径或名称
            tooltip: 工具提示
            parent_id: 父级导航项ID(用于层级结构)
            item_type: 项目类型 ("button", "separator", "group")
            state: 状态 ("normal", "disabled", "active", "selected")
            separator_before: 在此项前添加分隔符
            separator_after: 在此项后添加分隔符
            collapsible: 是否可折叠(用于分组)
            expanded: 是否展开(用于分组)
            badge_text: 徽章文本
            badge_color: 徽章颜色
        """
        self.item_id = item_id
        self.text = text
        self.command = command
        self.icon = icon
        self.tooltip = tooltip
        self.parent_id = parent_id
        self.item_type = item_type
        self.state = state
        self.separator_before = separator_before
        self.separator_after = separator_after
        self.collapsible = collapsible
        self.expanded = expanded
        self.badge_text = badge_text
        self.badge_color = badge_color


class NavigationPanelTTK:
    """TTK导航面板类

    提供完整的导航面板功能,支持多级导航、
    折叠展开、状态管理等功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        width: int = 250,
        min_width: int = 50,
        collapsible: bool = True,
        auto_collapse: bool = False,
        config_file: Optional[str] = None,
        auto_save_config: bool = True,
    ):
        """初始化导航面板

        Args:
            parent: 父组件
            width: 面板宽度
            min_width: 最小宽度(折叠时)
            collapsible: 是否可折叠
            auto_collapse: 是否自动折叠
            config_file: 配置文件路径
            auto_save_config: 是否自动保存配置
        """
        self.parent = parent
        self.width = width
        self.min_width = min_width
        self.collapsible = collapsible
        self.auto_collapse = auto_collapse
        self.config_file = config_file
        self.auto_save_config = auto_save_config

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 导航面板框架
        self.navigation_frame: Optional[ttk.Frame] = None
        self.scroll_frame: Optional[ttk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.scrollbar: Optional[ttk.Scrollbar] = None

        # 导航项管理
        self.navigation_items: Dict[str, tk.Widget] = {}
        self.item_configs: Dict[str, NavigationItemConfig] = {}
        self.item_states: Dict[str, str] = {}
        self.separators: List[ttk.Separator] = []

        # 层级管理
        self.item_hierarchy: Dict[str, List[str]] = {}  # parent_id -> [child_ids]
        self.item_levels: Dict[str, int] = {}  # item_id -> level

        # 状态管理
        self.selected_item: Optional[str] = None
        self.collapsed_groups: set = set()
        self.is_collapsed = False

        # 事件回调
        self.selection_callbacks: List[Callable] = []
        self.collapse_callbacks: List[Callable] = []

        # 初始化导航面板
        self._initialize_navigation_panel()

        # 加载配置
        if self.config_file:
            self._load_config()

    def _initialize_navigation_panel(self) -> None:
        """初始化导航面板框架"""
        try:
            # 创建主框架
            self.navigation_frame = ttk.Frame(self.parent, width=self.width)
            self.navigation_frame.pack_propagate(False)

            # 创建滚动画布
            self.canvas = tk.Canvas(
                self.navigation_frame, highlightthickness=0, width=self.width
            )

            # 创建滚动条
            self.scrollbar = ttk.Scrollbar(
                self.navigation_frame, orient="vertical", command=self.canvas.yview
            )
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

            # 创建滚动框架
            self.scroll_frame = ttk.Frame(self.canvas)
            self.canvas_window = self.canvas.create_window(
                (0, 0), window=self.scroll_frame, anchor="nw"
            )

            # 布局组件
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")

            # 绑定事件
            self.scroll_frame.bind("<Configure>", self._on_frame_configure)
            self.canvas.bind("<Configure>", self._on_canvas_configure)
            self.canvas.bind("<MouseWheel>", self._on_mousewheel)

            self.logger.debug("导航面板初始化完成")

        except Exception as e:
            self.logger.error(f"导航面板初始化失败: {e}")
            raise

    def _on_frame_configure(self, event) -> None:
        """滚动框架配置变化事件"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event) -> None:
        """画布配置变化事件"""
        # 更新滚动框架宽度
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _on_mousewheel(self, event) -> None:
        """鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def get_frame(self) -> ttk.Frame:
        """获取导航面板框架

        Returns:
            导航面板框架对象
        """
        return self.navigation_frame

    def add_navigation_item(
        self, item_config: NavigationItemConfig
    ) -> Optional[tk.Widget]:
        """添加导航项

        Args:
            item_config: 导航项配置

        Returns:
            创建的导航项组件
        """
        try:
            if not self.scroll_frame:
                raise ValueError("导航面板框架未初始化")

            # 添加前置分隔符
            if item_config.separator_before:
                self._add_separator()

            # 创建导航项
            item = None
            if item_config.item_type == "separator":
                item = self._add_separator()
            elif item_config.item_type == "button":
                item = self._create_navigation_button(item_config)
            elif item_config.item_type == "group":
                item = self._create_navigation_group(item_config)

            if item and item_config.item_type != "separator":
                # 保存导航项引用
                self.navigation_items[item_config.item_id] = item
                self.item_configs[item_config.item_id] = item_config
                self.item_states[item_config.item_id] = item_config.state

                # 建立层级关系
                self._build_hierarchy(item_config)

                # 布局导航项
                self._layout_navigation_item(item, item_config)

                # 添加工具提示
                if item_config.tooltip:
                    self._add_tooltip(item, item_config.tooltip)

            # 添加后置分隔符
            if item_config.separator_after:
                self._add_separator()

            self.logger.debug(f"导航项添加完成: {item_config.item_id}")
            return item

        except Exception as e:
            self.logger.error(f"导航项添加失败: {e}")
            raise

    def _create_navigation_button(self, config: NavigationItemConfig) -> ttk.Button:
        """创建导航按钮

        Args:
            config: 导航项配置

        Returns:
            导航按钮组件
        """
        # 创建按钮框架
        button_frame = ttk.Frame(self.scroll_frame)

        # 创建按钮
        button = ttk.Button(
            button_frame,
            text=config.text,
            command=lambda: self._on_navigation_click(config.item_id),
            state=config.state,
        )

        # 设置按钮样式
        self._apply_button_style(button, config)

        # 布局按钮
        button.pack(fill="x", padx=5, pady=2)

        # 添加徽章
        if config.badge_text:
            self._add_badge(button_frame, config.badge_text, config.badge_color)

        return button_frame

    def _create_navigation_group(self, config: NavigationItemConfig) -> ttk.Frame:
        """创建导航分组

        Args:
            config: 导航项配置

        Returns:
            导航分组框架
        """
        # 创建分组框架
        group_frame = ttk.Frame(self.scroll_frame)

        # 创建分组标题
        if config.collapsible:
            # 可折叠分组
            title_button = ttk.Button(
                group_frame,
                text=f"{'▼' if config.expanded else '▶'} {config.text}",
                command=lambda: self._toggle_group(config.item_id),
                style="Toolbutton",
            )
        else:
            # 普通分组标题
            title_button = ttk.Label(
                group_frame, text=config.text, font=("TkDefaultFont", 9, "bold")
            )

        title_button.pack(fill="x", padx=5, pady=2)

        # 创建子项容器
        children_frame = ttk.Frame(group_frame)
        if config.expanded:
            children_frame.pack(fill="x", padx=10)

        # 保存子项容器引用
        group_frame.children_frame = children_frame
        group_frame.title_button = title_button

        return group_frame

    def _apply_button_style(
        self, button: ttk.Button, config: NavigationItemConfig
    ) -> None:
        """应用按钮样式

        Args:
            button: 按钮组件
            config: 导航项配置
        """
        # 根据状态应用不同样式
        if config.state == "selected":
            button.configure(style="Selected.TButton")
        elif config.state == "active":
            button.configure(style="Active.TButton")
        elif config.state == "disabled":
            button.configure(style="Disabled.TButton")

        # 设置图标
        if config.icon:
            self._set_button_icon(button, config.icon)

    def _set_button_icon(self, button: ttk.Button, icon: str) -> None:
        """设置按钮图标

        Args:
            button: 按钮组件
            icon: 图标路径或名称
        """
        try:
            # 这里可以实现图标加载逻辑
            # 由于TTK的限制,图标支持可能需要使用PhotoImage
            if os.path.exists(icon):
                # 加载图标文件
                pass
            else:
                # 使用内置图标或字符
                pass

        except Exception as e:
            self.logger.warning(f"设置按钮图标失败 [{icon}]: {e}")

    def _add_badge(self, parent: tk.Widget, text: str, color: str) -> None:
        """添加徽章

        Args:
            parent: 父组件
            text: 徽章文本
            color: 徽章颜色
        """
        try:
            badge = ttk.Label(
                parent,
                text=text,
                background=color,
                foreground="white",
                font=("TkDefaultFont", 7),
                padding=(2, 1),
            )
            badge.place(relx=1.0, rely=0.0, anchor="ne")

        except Exception as e:
            self.logger.warning(f"添加徽章失败: {e}")

    def _add_separator(self) -> ttk.Separator:
        """添加分隔符

        Returns:
            分隔符组件
        """
        separator = ttk.Separator(self.scroll_frame, orient="horizontal")
        self.separators.append(separator)
        separator.pack(fill="x", padx=5, pady=5)
        return separator

    def _layout_navigation_item(
        self, item: tk.Widget, config: NavigationItemConfig
    ) -> None:
        """布局导航项

        Args:
            item: 导航项组件
            config: 导航项配置
        """
        # 计算缩进级别
        level = self.item_levels.get(config.item_id, 0)
        padx = (5 + level * 15, 5)

        # 布局项目
        item.pack(fill="x", padx=padx, pady=1)

    def _build_hierarchy(self, config: NavigationItemConfig) -> None:
        """建立层级关系

        Args:
            config: 导航项配置
        """
        # 设置层级
        if config.parent_id:
            parent_level = self.item_levels.get(config.parent_id, 0)
            self.item_levels[config.item_id] = parent_level + 1

            # 添加到父级的子项列表
            if config.parent_id not in self.item_hierarchy:
                self.item_hierarchy[config.parent_id] = []
            self.item_hierarchy[config.parent_id].append(config.item_id)
        else:
            self.item_levels[config.item_id] = 0

    def _add_tooltip(self, widget: tk.Widget, text: str) -> None:
        """为组件添加工具提示

        Args:
            widget: 目标组件
            text: 提示文本
        """

        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = ttk.Label(
                tooltip,
                text=text,
                background="lightyellow",
                relief="solid",
                borderwidth=1,
            )
            label.pack()

            widget.tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, "tooltip"):
                widget.tooltip.destroy()
                del widget.tooltip

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def _on_navigation_click(self, item_id: str) -> None:
        """导航项点击事件处理

        Args:
            item_id: 导航项ID
        """
        try:
            # 更新选中状态
            self.select_item(item_id)

            # 触发选择回调
            for callback in self.selection_callbacks:
                try:
                    callback(item_id)
                except Exception as e:
                    self.logger.error(f"选择回调执行失败: {e}")

            self.logger.debug(f"导航项点击: {item_id}")

        except Exception as e:
            self.logger.error(f"导航项点击处理失败: {e}")

    def _toggle_group(self, group_id: str) -> None:
        """切换分组展开/折叠状态

        Args:
            group_id: 分组ID
        """
        try:
            group_frame = self.navigation_items.get(group_id)
            if not group_frame:
                return

            config = self.item_configs.get(group_id)
            if not config:
                return

            # 切换展开状态
            config.expanded = not config.expanded

            # 更新标题按钮
            title_button = getattr(group_frame, "title_button", None)
            if title_button:
                icon = "▼" if config.expanded else "▶"
                title_button.configure(text=f"{icon} {config.text}")

            # 显示/隐藏子项
            children_frame = getattr(group_frame, "children_frame", None)
            if children_frame:
                if config.expanded:
                    children_frame.pack(fill="x", padx=10)
                    self.collapsed_groups.discard(group_id)
                else:
                    children_frame.pack_forget()
                    self.collapsed_groups.add(group_id)

            # 触发折叠回调
            for callback in self.collapse_callbacks:
                try:
                    callback(group_id, config.expanded)
                except Exception as e:
                    self.logger.error(f"折叠回调执行失败: {e}")

            self.logger.debug(
                f"分组切换: {group_id} -> {'展开' if config.expanded else '折叠'}"
            )

        except Exception as e:
            self.logger.error(f"分组切换失败: {e}")

    def select_item(self, item_id: str) -> None:
        """选择导航项

        Args:
            item_id: 导航项ID
        """
        try:
            # 取消之前的选择
            if self.selected_item:
                self._update_item_state(self.selected_item, "normal")

            # 设置新的选择
            self.selected_item = item_id
            self._update_item_state(item_id, "selected")

            self.logger.debug(f"导航项选择: {item_id}")

        except Exception as e:
            self.logger.error(f"导航项选择失败: {e}")

    def _update_item_state(self, item_id: str, state: str) -> None:
        """更新导航项状态

        Args:
            item_id: 导航项ID
            state: 新状态
        """
        try:
            item = self.navigation_items.get(item_id)
            config = self.item_configs.get(item_id)

            if not item or not config:
                return

            # 更新配置状态
            config.state = state
            self.item_states[item_id] = state

            # 更新组件状态
            if config.item_type == "button":
                # 查找按钮组件
                button = None
                for child in item.winfo_children():
                    if isinstance(child, ttk.Button):
                        button = child
                        break

                if button:
                    self._apply_button_style(button, config)

        except Exception as e:
            self.logger.error(f"导航项状态更新失败: {e}")

    def get_selected_item(self) -> Optional[str]:
        """获取当前选中的导航项

        Returns:
            选中的导航项ID,如果没有选中则返回None
        """
        return self.selected_item

    def set_item_state(self, item_id: str, state: str) -> None:
        """设置导航项状态

        Args:
            item_id: 导航项ID
            state: 状态 ("normal", "disabled", "active", "selected")
        """
        self._update_item_state(item_id, state)

    def get_item_state(self, item_id: str) -> Optional[str]:
        """获取导航项状态

        Args:
            item_id: 导航项ID

        Returns:
            导航项状态,如果不存在则返回None
        """
        return self.item_states.get(item_id)

    def enable_item(self, item_id: str) -> None:
        """启用导航项

        Args:
            item_id: 导航项ID
        """
        self.set_item_state(item_id, "normal")

    def disable_item(self, item_id: str) -> None:
        """禁用导航项

        Args:
            item_id: 导航项ID
        """
        self.set_item_state(item_id, "disabled")

    def update_item_text(self, item_id: str, text: str) -> None:
        """更新导航项文本

        Args:
            item_id: 导航项ID
            text: 新文本
        """
        try:
            config = self.item_configs.get(item_id)
            if not config:
                self.logger.warning(f"导航项不存在: {item_id}")
                return

            # 更新配置
            config.text = text

            # 更新组件文本
            item = self.navigation_items.get(item_id)
            if item:
                if config.item_type == "button":
                    # 查找按钮组件
                    for child in item.winfo_children():
                        if isinstance(child, ttk.Button):
                            child.configure(text=text)
                            break
                elif config.item_type == "group":
                    # 更新分组标题
                    title_button = getattr(item, "title_button", None)
                    if title_button:
                        icon = "▼" if config.expanded else "▶"
                        if config.collapsible:
                            title_button.configure(text=f"{icon} {text}")
                        else:
                            title_button.configure(text=text)

            self.logger.debug(f"导航项文本更新: {item_id} -> {text}")

        except Exception as e:
            self.logger.error(f"导航项文本更新失败: {e}")

    def update_item_badge(
        self, item_id: str, badge_text: str, badge_color: str = "red"
    ) -> None:
        """更新导航项徽章

        Args:
            item_id: 导航项ID
            badge_text: 徽章文本
            badge_color: 徽章颜色
        """
        try:
            config = self.item_configs.get(item_id)
            if not config:
                self.logger.warning(f"导航项不存在: {item_id}")
                return

            # 更新配置
            config.badge_text = badge_text
            config.badge_color = badge_color

            # 更新徽章显示
            item = self.navigation_items.get(item_id)
            if item and config.item_type == "button":
                # 移除旧徽章
                for child in item.winfo_children():
                    if isinstance(child, ttk.Label) and child.winfo_class() == "Label":
                        child.destroy()

                # 添加新徽章
                if badge_text:
                    self._add_badge(item, badge_text, badge_color)

            self.logger.debug(f"导航项徽章更新: {item_id} -> {badge_text}")

        except Exception as e:
            self.logger.error(f"导航项徽章更新失败: {e}")

    def remove_item(self, item_id: str) -> None:
        """移除导航项

        Args:
            item_id: 导航项ID
        """
        try:
            item = self.navigation_items.get(item_id)
            if not item:
                self.logger.warning(f"导航项不存在: {item_id}")
                return

            # 移除子项
            if item_id in self.item_hierarchy:
                for child_id in self.item_hierarchy[item_id][:]:
                    self.remove_item(child_id)

            # 销毁组件
            item.destroy()

            # 清理引用
            del self.navigation_items[item_id]
            del self.item_configs[item_id]
            del self.item_states[item_id]

            # 清理层级关系
            if item_id in self.item_hierarchy:
                del self.item_hierarchy[item_id]
            if item_id in self.item_levels:
                del self.item_levels[item_id]

            # 从父级移除
            for parent_id, children in self.item_hierarchy.items():
                if item_id in children:
                    children.remove(item_id)

            # 更新选中状态
            if self.selected_item == item_id:
                self.selected_item = None

            self.logger.debug(f"导航项移除完成: {item_id}")

        except Exception as e:
            self.logger.error(f"导航项移除失败: {e}")

    def clear_all_items(self) -> None:
        """清除所有导航项"""
        try:
            # 销毁所有导航项
            for item in self.navigation_items.values():
                item.destroy()

            # 销毁所有分隔符
            for separator in self.separators:
                separator.destroy()

            # 清理所有引用
            self.navigation_items.clear()
            self.item_configs.clear()
            self.item_states.clear()
            self.separators.clear()
            self.item_hierarchy.clear()
            self.item_levels.clear()
            self.collapsed_groups.clear()
            self.selected_item = None

            self.logger.debug("所有导航项清除完成")

        except Exception as e:
            self.logger.error(f"导航项清除失败: {e}")

    def collapse_panel(self) -> None:
        """折叠导航面板"""
        if not self.collapsible or self.is_collapsed:
            return

        try:
            # 保存当前宽度
            self.width = self.navigation_frame.winfo_width()

            # 设置为最小宽度
            self.navigation_frame.configure(width=self.min_width)
            self.is_collapsed = True

            # 隐藏文本,只显示图标
            self._update_collapsed_display()

            # 触发折叠回调
            for callback in self.collapse_callbacks:
                try:
                    callback("panel", False)
                except Exception as e:
                    self.logger.error(f"折叠回调执行失败: {e}")

            self.logger.debug("导航面板折叠")

        except Exception as e:
            self.logger.error(f"导航面板折叠失败: {e}")

    def expand_panel(self) -> None:
        """展开导航面板"""
        if not self.is_collapsed:
            return

        try:
            # 恢复原始宽度
            self.navigation_frame.configure(width=self.width)
            self.is_collapsed = False

            # 显示完整内容
            self._update_expanded_display()

            # 触发展开回调
            for callback in self.collapse_callbacks:
                try:
                    callback("panel", True)
                except Exception as e:
                    self.logger.error(f"展开回调执行失败: {e}")

            self.logger.debug("导航面板展开")

        except Exception as e:
            self.logger.error(f"导航面板展开失败: {e}")

    def toggle_panel(self) -> None:
        """切换导航面板折叠/展开状态"""
        if self.is_collapsed:
            self.expand_panel()
        else:
            self.collapse_panel()

    def _update_collapsed_display(self) -> None:
        """更新折叠显示"""
        # 在折叠状态下,可以只显示图标或简化显示
        # 这里可以根据需要实现具体的折叠显示逻辑

    def _update_expanded_display(self) -> None:
        """更新展开显示"""
        # 在展开状态下,显示完整内容
        # 这里可以根据需要实现具体的展开显示逻辑

    def add_selection_callback(self, callback: Callable) -> None:
        """添加选择回调

        Args:
            callback: 回调函数,接收选中的item_id参数
        """
        self.selection_callbacks.append(callback)

    def remove_selection_callback(self, callback: Callable) -> None:
        """移除选择回调

        Args:
            callback: 回调函数
        """
        try:
            self.selection_callbacks.remove(callback)
        except ValueError:
            self.logger.warning("选择回调不存在")

    def add_collapse_callback(self, callback: Callable) -> None:
        """添加折叠回调

        Args:
            callback: 回调函数,接收item_id和expanded参数
        """
        self.collapse_callbacks.append(callback)

    def remove_collapse_callback(self, callback: Callable) -> None:
        """移除折叠回调

        Args:
            callback: 回调函数
        """
        try:
            self.collapse_callbacks.remove(callback)
        except ValueError:
            self.logger.warning("折叠回调不存在")

    def _load_config(self) -> None:
        """加载导航面板配置"""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                self.logger.debug("导航面板配置文件不存在,跳过加载")
                return

            with open(self.config_file, encoding="utf-8") as f:
                config_data = json.load(f)

            # 加载面板状态
            panel_config = config_data.get("panel", {})
            self.is_collapsed = panel_config.get("collapsed", False)
            self.collapsed_groups = set(panel_config.get("collapsed_groups", []))

            # 加载导航项配置
            items_config = config_data.get("items", [])
            for item_data in items_config:
                item_config = self._create_item_config_from_data(item_data)
                if item_config:
                    self.add_navigation_item(item_config)

            # 恢复选中状态
            selected_item = config_data.get("selected_item")
            if selected_item and selected_item in self.navigation_items:
                self.select_item(selected_item)

            self.logger.info(f"导航面板配置加载完成: {self.config_file}")

        except Exception as e:
            self.logger.error(f"导航面板配置加载失败: {e}")

    def _create_item_config_from_data(
        self, item_data: Dict[str, Any]
    ) -> Optional[NavigationItemConfig]:
        """从数据创建导航项配置

        Args:
            item_data: 导航项数据

        Returns:
            导航项配置对象
        """
        try:
            # 注意:从配置文件加载时,command需要通过其他方式设置
            item_config = NavigationItemConfig(
                item_id=item_data.get("id", ""),
                text=item_data.get("text", ""),
                icon=item_data.get("icon", ""),
                tooltip=item_data.get("tooltip", ""),
                parent_id=item_data.get("parent_id"),
                item_type=item_data.get("type", "button"),
                state=item_data.get("state", "normal"),
                separator_before=item_data.get("separator_before", False),
                separator_after=item_data.get("separator_after", False),
                collapsible=item_data.get("collapsible", False),
                expanded=item_data.get("expanded", True),
                badge_text=item_data.get("badge_text", ""),
                badge_color=item_data.get("badge_color", "red"),
            )

            return item_config

        except Exception as e:
            self.logger.error(f"导航项配置创建失败: {e}")
            return None

    def save_config(self, config_file: Optional[str] = None) -> None:
        """保存导航面板配置

        Args:
            config_file: 配置文件路径,如果为None则使用默认路径
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                self.logger.warning("未指定配置文件路径")
                return

            # 构建配置数据
            config_data = {
                "panel": {
                    "width": self.width,
                    "collapsed": self.is_collapsed,
                    "collapsed_groups": list(self.collapsed_groups),
                },
                "selected_item": self.selected_item,
                "items": [],
            }

            for item_id, item_config in self.item_configs.items():
                item_data = {
                    "id": item_config.item_id,
                    "text": item_config.text,
                    "icon": item_config.icon,
                    "tooltip": item_config.tooltip,
                    "parent_id": item_config.parent_id,
                    "type": item_config.item_type,
                    "state": item_config.state,
                    "separator_before": item_config.separator_before,
                    "separator_after": item_config.separator_after,
                    "collapsible": item_config.collapsible,
                    "expanded": item_config.expanded,
                    "badge_text": item_config.badge_text,
                    "badge_color": item_config.badge_color,
                }
                config_data["items"].append(item_data)

            # 确保目录存在
            config_dir = os.path.dirname(save_path)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"导航面板配置保存完成: {save_path}")

        except Exception as e:
            self.logger.error(f"导航面板配置保存失败: {e}")

    def get_navigation_info(self) -> Dict[str, Any]:
        """获取导航面板信息

        Returns:
            导航面板信息字典
        """
        return {
            "width": self.width,
            "min_width": self.min_width,
            "is_collapsed": self.is_collapsed,
            "collapsible": self.collapsible,
            "item_count": len(self.navigation_items),
            "selected_item": self.selected_item,
            "collapsed_groups": list(self.collapsed_groups),
            "items": {
                item_id: {
                    "text": config.text,
                    "type": config.item_type,
                    "state": config.state,
                    "parent_id": config.parent_id,
                    "level": self.item_levels.get(item_id, 0),
                    "badge_text": config.badge_text,
                }
                for item_id, config in self.item_configs.items()
            },
        }

    def cleanup(self) -> None:
        """清理导航面板资源"""
        try:
            # 自动保存配置
            if self.auto_save_config and self.config_file:
                self.save_config()

            # 清理所有导航项
            self.clear_all_items()

            # 清理回调
            self.selection_callbacks.clear()
            self.collapse_callbacks.clear()

            self.logger.debug("导航面板资源清理完成")

        except Exception as e:
            self.logger.error(f"导航面板资源清理失败: {e}")
