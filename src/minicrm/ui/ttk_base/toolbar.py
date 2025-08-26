"""TTK工具栏系统

提供TTK应用程序的工具栏功能,包括:
- 工具按钮的创建和管理
- 工具栏布局和分组
- 按钮状态管理和事件处理
- 工具栏自定义和配置
- 图标和工具提示支持

设计目标:
1. 提供灵活的工具栏构建功能
2. 支持多种按钮类型和样式
3. 简化工具栏管理和维护
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

import json
import logging
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class ToolButtonConfig:
    """工具按钮配置类"""

    def __init__(
        self,
        button_id: str,
        text: str = "",
        command: Optional[Callable] = None,
        icon: Optional[str] = None,
        tooltip: str = "",
        state: str = "normal",
        button_type: str = "button",
        variable: Optional[tk.Variable] = None,
        value: Any = None,
        separator_before: bool = False,
        separator_after: bool = False,
        width: Optional[int] = None,
        style: Optional[str] = None,
    ):
        """初始化工具按钮配置

        Args:
            button_id: 按钮唯一标识
            text: 按钮文本
            command: 点击命令
            icon: 图标路径或名称
            tooltip: 工具提示
            state: 按钮状态 ("normal", "disabled", "active")
            button_type: 按钮类型 ("button", "checkbutton", "radiobutton", "separator")
            variable: 关联的变量(用于checkbutton和radiobutton)
            value: 变量值(用于radiobutton)
            separator_before: 在此按钮前添加分隔符
            separator_after: 在此按钮后添加分隔符
            width: 按钮宽度
            style: 按钮样式
        """
        self.button_id = button_id
        self.text = text
        self.command = command
        self.icon = icon
        self.tooltip = tooltip
        self.state = state
        self.button_type = button_type
        self.variable = variable
        self.value = value
        self.separator_before = separator_before
        self.separator_after = separator_after
        self.width = width
        self.style = style


class ToolBarTTK:
    """TTK工具栏类

    提供完整的工具栏功能,支持多种按钮类型、
    布局管理、状态控制等功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        orientation: str = "horizontal",
        height: Optional[int] = None,
        width: Optional[int] = None,
        relief: str = "flat",
        borderwidth: int = 1,
        config_file: Optional[str] = None,
        auto_save_config: bool = True,
    ):
        """初始化工具栏

        Args:
            parent: 父组件
            orientation: 工具栏方向 ("horizontal", "vertical")
            height: 工具栏高度(水平工具栏)
            width: 工具栏宽度(垂直工具栏)
            relief: 边框样式
            borderwidth: 边框宽度
            config_file: 配置文件路径
            auto_save_config: 是否自动保存配置
        """
        self.parent = parent
        self.orientation = orientation
        self.config_file = config_file
        self.auto_save_config = auto_save_config

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 工具栏框架
        self.toolbar_frame: Optional[ttk.Frame] = None

        # 按钮管理
        self.buttons: Dict[str, tk.Widget] = {}
        self.button_configs: Dict[str, ToolButtonConfig] = {}
        self.separators: List[ttk.Separator] = []

        # 状态管理
        self.button_states: Dict[str, str] = {}

        # 变量管理
        self.button_variables: Dict[str, tk.Variable] = {}

        # 工具提示管理
        self.tooltips: Dict[str, Any] = {}

        # 初始化工具栏
        self._initialize_toolbar(height, width, relief, borderwidth)

        # 加载配置
        if self.config_file:
            self._load_config()

    def _initialize_toolbar(
        self, height: Optional[int], width: Optional[int], relief: str, borderwidth: int
    ) -> None:
        """初始化工具栏框架"""
        try:
            # 创建工具栏框架
            self.toolbar_frame = ttk.Frame(
                self.parent, relief=relief, borderwidth=borderwidth
            )

            # 设置大小
            if self.orientation == "horizontal" and height:
                self.toolbar_frame.configure(height=height)
                self.toolbar_frame.pack_propagate(False)
            elif self.orientation == "vertical" and width:
                self.toolbar_frame.configure(width=width)
                self.toolbar_frame.pack_propagate(False)

            self.logger.debug(f"工具栏初始化完成: {self.orientation}")

        except Exception as e:
            self.logger.error(f"工具栏初始化失败: {e}")
            raise

    def get_frame(self) -> ttk.Frame:
        """获取工具栏框架

        Returns:
            工具栏框架对象
        """
        return self.toolbar_frame

    def add_button(self, button_config: ToolButtonConfig) -> Optional[tk.Widget]:
        """添加工具按钮

        Args:
            button_config: 按钮配置

        Returns:
            创建的按钮组件
        """
        try:
            if not self.toolbar_frame:
                raise ValueError("工具栏框架未初始化")

            # 添加前置分隔符
            if button_config.separator_before:
                self._add_separator()

            # 创建按钮
            button = None
            if button_config.button_type == "separator":
                button = self._add_separator()
            elif button_config.button_type == "button":
                button = self._create_button(button_config)
            elif button_config.button_type == "checkbutton":
                button = self._create_checkbutton(button_config)
            elif button_config.button_type == "radiobutton":
                button = self._create_radiobutton(button_config)

            if button and button_config.button_type != "separator":
                # 保存按钮引用
                self.buttons[button_config.button_id] = button
                self.button_configs[button_config.button_id] = button_config
                self.button_states[button_config.button_id] = button_config.state

                # 添加工具提示
                if button_config.tooltip:
                    self._add_tooltip(button, button_config.tooltip)

                # 布局按钮
                self._layout_button(button)

            # 添加后置分隔符
            if button_config.separator_after:
                self._add_separator()

            self.logger.debug(f"工具按钮添加完成: {button_config.button_id}")
            return button

        except Exception as e:
            self.logger.error(f"工具按钮添加失败: {e}")
            raise

    def _create_button(self, config: ToolButtonConfig) -> ttk.Button:
        """创建普通按钮

        Args:
            config: 按钮配置

        Returns:
            按钮组件
        """
        button = ttk.Button(
            self.toolbar_frame,
            text=config.text,
            command=config.command,
            state=config.state,
            width=config.width,
            style=config.style,
        )

        # 设置图标
        if config.icon:
            self._set_button_icon(button, config.icon)

        return button

    def _create_checkbutton(self, config: ToolButtonConfig) -> ttk.Checkbutton:
        """创建复选按钮

        Args:
            config: 按钮配置

        Returns:
            复选按钮组件
        """
        button = ttk.Checkbutton(
            self.toolbar_frame,
            text=config.text,
            variable=config.variable,
            command=config.command,
            state=config.state,
            width=config.width,
            style=config.style,
        )

        # 设置图标
        if config.icon:
            self._set_button_icon(button, config.icon)

        return button

    def _create_radiobutton(self, config: ToolButtonConfig) -> ttk.Radiobutton:
        """创建单选按钮

        Args:
            config: 按钮配置

        Returns:
            单选按钮组件
        """
        button = ttk.Radiobutton(
            self.toolbar_frame,
            text=config.text,
            variable=config.variable,
            value=config.value,
            command=config.command,
            state=config.state,
            width=config.width,
            style=config.style,
        )

        # 设置图标
        if config.icon:
            self._set_button_icon(button, config.icon)

        return button

    def _add_separator(self) -> ttk.Separator:
        """添加分隔符

        Returns:
            分隔符组件
        """
        if self.orientation == "horizontal":
            separator = ttk.Separator(self.toolbar_frame, orient="vertical")
        else:
            separator = ttk.Separator(self.toolbar_frame, orient="horizontal")

        self.separators.append(separator)
        self._layout_separator(separator)

        return separator

    def _layout_button(self, button: tk.Widget) -> None:
        """布局按钮

        Args:
            button: 按钮组件
        """
        if self.orientation == "horizontal":
            button.pack(side=tk.LEFT, padx=2, pady=2)
        else:
            button.pack(side=tk.TOP, padx=2, pady=2, fill=tk.X)

    def _layout_separator(self, separator: ttk.Separator) -> None:
        """布局分隔符

        Args:
            separator: 分隔符组件
        """
        if self.orientation == "horizontal":
            separator.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        else:
            separator.pack(side=tk.TOP, fill=tk.X, padx=2, pady=5)

    def _set_button_icon(self, button: tk.Widget, icon: str) -> None:
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

        # 保存工具提示引用
        button_id = self._get_button_id_by_widget(widget)
        if button_id:
            self.tooltips[button_id] = text

    def _get_button_id_by_widget(self, widget: tk.Widget) -> Optional[str]:
        """根据组件获取按钮ID

        Args:
            widget: 组件对象

        Returns:
            按钮ID,如果不存在则返回None
        """
        for button_id, button in self.buttons.items():
            if button == widget:
                return button_id
        return None

    def get_button(self, button_id: str) -> Optional[tk.Widget]:
        """获取按钮组件

        Args:
            button_id: 按钮ID

        Returns:
            按钮组件,如果不存在则返回None
        """
        return self.buttons.get(button_id)

    def set_button_state(self, button_id: str, state: str) -> None:
        """设置按钮状态

        Args:
            button_id: 按钮ID
            state: 状态 ("normal", "disabled", "active")
        """
        try:
            button = self.buttons.get(button_id)
            if not button:
                self.logger.warning(f"按钮不存在: {button_id}")
                return

            # 设置状态
            button.configure(state=state)

            # 更新状态记录
            self.button_states[button_id] = state

            self.logger.debug(f"按钮状态更新: {button_id} -> {state}")

        except Exception as e:
            self.logger.error(f"按钮状态设置失败: {e}")

    def get_button_state(self, button_id: str) -> Optional[str]:
        """获取按钮状态

        Args:
            button_id: 按钮ID

        Returns:
            按钮状态,如果不存在则返回None
        """
        return self.button_states.get(button_id)

    def enable_button(self, button_id: str) -> None:
        """启用按钮

        Args:
            button_id: 按钮ID
        """
        self.set_button_state(button_id, "normal")

    def disable_button(self, button_id: str) -> None:
        """禁用按钮

        Args:
            button_id: 按钮ID
        """
        self.set_button_state(button_id, "disabled")

    def update_button_command(self, button_id: str, command: Callable) -> None:
        """更新按钮命令

        Args:
            button_id: 按钮ID
            command: 新的命令函数
        """
        try:
            button = self.buttons.get(button_id)
            if not button:
                self.logger.warning(f"按钮不存在: {button_id}")
                return

            # 更新命令
            button.configure(command=command)

            # 更新配置
            if button_id in self.button_configs:
                self.button_configs[button_id].command = command

            self.logger.debug(f"按钮命令更新: {button_id}")

        except Exception as e:
            self.logger.error(f"按钮命令更新失败: {e}")

    def update_button_text(self, button_id: str, text: str) -> None:
        """更新按钮文本

        Args:
            button_id: 按钮ID
            text: 新的文本
        """
        try:
            button = self.buttons.get(button_id)
            if not button:
                self.logger.warning(f"按钮不存在: {button_id}")
                return

            # 更新文本
            button.configure(text=text)

            # 更新配置
            if button_id in self.button_configs:
                self.button_configs[button_id].text = text

            self.logger.debug(f"按钮文本更新: {button_id} -> {text}")

        except Exception as e:
            self.logger.error(f"按钮文本更新失败: {e}")

    def remove_button(self, button_id: str) -> None:
        """移除按钮

        Args:
            button_id: 按钮ID
        """
        try:
            button = self.buttons.get(button_id)
            if not button:
                self.logger.warning(f"按钮不存在: {button_id}")
                return

            # 销毁按钮
            button.destroy()

            # 清理引用
            del self.buttons[button_id]
            del self.button_configs[button_id]
            del self.button_states[button_id]

            # 清理工具提示
            if button_id in self.tooltips:
                del self.tooltips[button_id]

            self.logger.debug(f"按钮移除完成: {button_id}")

        except Exception as e:
            self.logger.error(f"按钮移除失败: {e}")

    def clear_all_buttons(self) -> None:
        """清除所有按钮"""
        try:
            # 销毁所有按钮
            for button in self.buttons.values():
                button.destroy()

            # 销毁所有分隔符
            for separator in self.separators:
                separator.destroy()

            # 清理所有引用
            self.buttons.clear()
            self.button_configs.clear()
            self.button_states.clear()
            self.separators.clear()
            self.tooltips.clear()

            self.logger.debug("所有按钮清除完成")

        except Exception as e:
            self.logger.error(f"按钮清除失败: {e}")

    def set_button_variable(self, variable_name: str, variable: tk.Variable) -> None:
        """设置按钮变量

        Args:
            variable_name: 变量名称
            variable: 变量对象
        """
        self.button_variables[variable_name] = variable

    def get_button_variable(self, variable_name: str) -> Optional[tk.Variable]:
        """获取按钮变量

        Args:
            variable_name: 变量名称

        Returns:
            变量对象,如果不存在则返回None
        """
        return self.button_variables.get(variable_name)

    def _load_config(self) -> None:
        """加载工具栏配置"""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                self.logger.debug("工具栏配置文件不存在,跳过加载")
                return

            with open(self.config_file, encoding="utf-8") as f:
                config_data = json.load(f)

            # 加载按钮配置
            buttons_config = config_data.get("buttons", [])
            for button_data in buttons_config:
                button_config = self._create_button_config_from_data(button_data)
                if button_config:
                    self.add_button(button_config)

            self.logger.info(f"工具栏配置加载完成: {self.config_file}")

        except Exception as e:
            self.logger.error(f"工具栏配置加载失败: {e}")

    def _create_button_config_from_data(
        self, button_data: Dict[str, Any]
    ) -> Optional[ToolButtonConfig]:
        """从数据创建按钮配置

        Args:
            button_data: 按钮数据

        Returns:
            按钮配置对象
        """
        try:
            # 注意:从配置文件加载时,command需要通过其他方式设置
            button_config = ToolButtonConfig(
                button_id=button_data.get("id", ""),
                text=button_data.get("text", ""),
                icon=button_data.get("icon", ""),
                tooltip=button_data.get("tooltip", ""),
                state=button_data.get("state", "normal"),
                button_type=button_data.get("type", "button"),
                separator_before=button_data.get("separator_before", False),
                separator_after=button_data.get("separator_after", False),
                width=button_data.get("width"),
                style=button_data.get("style"),
            )

            return button_config

        except Exception as e:
            self.logger.error(f"按钮配置创建失败: {e}")
            return None

    def save_config(self, config_file: Optional[str] = None) -> None:
        """保存工具栏配置

        Args:
            config_file: 配置文件路径,如果为None则使用默认路径
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                self.logger.warning("未指定配置文件路径")
                return

            # 构建配置数据
            config_data = {"orientation": self.orientation, "buttons": []}

            for button_id, button_config in self.button_configs.items():
                button_data = {
                    "id": button_config.button_id,
                    "text": button_config.text,
                    "icon": button_config.icon,
                    "tooltip": button_config.tooltip,
                    "state": button_config.state,
                    "type": button_config.button_type,
                    "separator_before": button_config.separator_before,
                    "separator_after": button_config.separator_after,
                    "width": button_config.width,
                    "style": button_config.style,
                }
                config_data["buttons"].append(button_data)

            # 确保目录存在
            config_dir = os.path.dirname(save_path)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"工具栏配置保存完成: {save_path}")

        except Exception as e:
            self.logger.error(f"工具栏配置保存失败: {e}")

    def get_toolbar_info(self) -> Dict[str, Any]:
        """获取工具栏信息

        Returns:
            工具栏信息字典
        """
        return {
            "orientation": self.orientation,
            "button_count": len(self.buttons),
            "separator_count": len(self.separators),
            "buttons": {
                button_id: {
                    "text": config.text,
                    "type": config.button_type,
                    "state": self.button_states.get(button_id, "normal"),
                    "tooltip": config.tooltip,
                }
                for button_id, config in self.button_configs.items()
            },
        }

    def cleanup(self) -> None:
        """清理工具栏资源"""
        try:
            # 自动保存配置
            if self.auto_save_config and self.config_file:
                self.save_config()

            # 清理所有按钮
            self.clear_all_buttons()

            # 清理变量
            self.button_variables.clear()

            self.logger.debug("工具栏资源清理完成")

        except Exception as e:
            self.logger.error(f"工具栏资源清理失败: {e}")
