"""TTK菜单栏系统.

提供TTK应用程序的菜单栏功能,包括:
- 完整的菜单功能实现
- 快捷键绑定和菜单项状态管理
- 菜单配置化和动态更新
- 菜单项的启用/禁用状态管理
- 可选择菜单项(复选框、单选按钮)支持

设计目标:
1. 提供与Qt菜单栏相当的功能
2. 支持配置化的菜单结构
3. 简化菜单管理和维护
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
from pathlib import Path
import tkinter as tk
from typing import Any, Callable


class MenuItemConfig:
    """菜单项配置类."""

    def __init__(
        self,
        label: str,
        command: Callable | None = None,
        accelerator: str = "",
        underline: int = -1,
        state: str = "normal",
        item_type: str = "command",
        variable: tk.Variable | None = None,
        value: Any = None,
        separator_before: bool = False,
        separator_after: bool = False,
        tooltip: str = "",
        icon: str | None = None,
    ):
        """初始化菜单项配置.

        Args:
            label: 菜单项标签
            command: 点击命令
            accelerator: 快捷键显示文本
            underline: 下划线字符位置
            state: 菜单项状态 ("normal", "disabled", "active")
            item_type: 菜单项类型 ("command", "checkbutton", "radiobutton", "separator")
            variable: 关联的变量(用于checkbutton和radiobutton)
            value: 变量值(用于radiobutton)
            separator_before: 在此项前添加分隔符
            separator_after: 在此项后添加分隔符
            tooltip: 工具提示
            icon: 图标路径
        """
        self.label = label
        self.command = command
        self.accelerator = accelerator
        self.underline = underline
        self.state = state
        self.item_type = item_type
        self.variable = variable
        self.value = value
        self.separator_before = separator_before
        self.separator_after = separator_after
        self.tooltip = tooltip
        self.icon = icon


class MenuConfig:
    """菜单配置类."""

    def __init__(self, label: str, underline: int = -1):
        """初始化菜单配置.

        Args:
            label: 菜单标签
            underline: 下划线字符位置
        """
        self.label = label
        self.underline = underline
        self.items: list[MenuItemConfig] = []

    def add_item(self, item: MenuItemConfig) -> None:
        """添加菜单项.

        Args:
            item: 菜单项配置
        """
        self.items.append(item)

    def add_separator(self) -> None:
        """添加分隔符."""
        separator = MenuItemConfig("", item_type="separator")
        self.items.append(separator)

    def add_command(
        self,
        label: str,
        command: Callable,
        accelerator: str = "",
        underline: int = -1,
        state: str = "normal",
        **kwargs,
    ) -> None:
        """添加命令菜单项.

        Args:
            label: 菜单项标签
            command: 点击命令
            accelerator: 快捷键显示文本
            underline: 下划线字符位置
            state: 菜单项状态
            **kwargs: 其他参数
        """
        item = MenuItemConfig(
            label=label,
            command=command,
            accelerator=accelerator,
            underline=underline,
            state=state,
            item_type="command",
            **kwargs,
        )
        self.add_item(item)

    def add_checkbutton(
        self,
        label: str,
        variable: tk.BooleanVar,
        command: Callable | None = None,
        accelerator: str = "",
        underline: int = -1,
        state: str = "normal",
        **kwargs,
    ) -> None:
        """添加复选框菜单项.

        Args:
            label: 菜单项标签
            variable: 关联的布尔变量
            command: 点击命令
            accelerator: 快捷键显示文本
            underline: 下划线字符位置
            state: 菜单项状态
            **kwargs: 其他参数
        """
        item = MenuItemConfig(
            label=label,
            command=command,
            accelerator=accelerator,
            underline=underline,
            state=state,
            item_type="checkbutton",
            variable=variable,
            **kwargs,
        )
        self.add_item(item)

    def add_radiobutton(
        self,
        label: str,
        variable: tk.Variable,
        value: Any,
        command: Callable | None = None,
        accelerator: str = "",
        underline: int = -1,
        state: str = "normal",
        **kwargs,
    ) -> None:
        """添加单选按钮菜单项.

        Args:
            label: 菜单项标签
            variable: 关联的变量
            value: 变量值
            command: 点击命令
            accelerator: 快捷键显示文本
            underline: 下划线字符位置
            state: 菜单项状态
            **kwargs: 其他参数
        """
        item = MenuItemConfig(
            label=label,
            command=command,
            accelerator=accelerator,
            underline=underline,
            state=state,
            item_type="radiobutton",
            variable=variable,
            value=value,
            **kwargs,
        )
        self.add_item(item)


class MenuBarTTK:
    """TTK菜单栏类.

    提供完整的菜单栏功能,支持菜单配置化、快捷键绑定、
    状态管理等功能.
    """

    def __init__(
        self,
        parent: tk.Tk,
        config_file: str | None = None,
        auto_save_config: bool = True,
    ):
        """初始化菜单栏.

        Args:
            parent: 父窗口
            config_file: 菜单配置文件路径
            auto_save_config: 是否自动保存配置
        """
        self.parent = parent
        self.config_file = config_file
        self.auto_save_config = auto_save_config

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 菜单栏和菜单
        self.menu_bar: tk.Menu | None = None
        self.menus: dict[str, tk.Menu] = {}
        self.menu_configs: dict[str, MenuConfig] = {}

        # 菜单项引用(用于状态管理)
        self.menu_items: dict[
            str, dict[str, int]
        ] = {}  # {menu_name: {item_label: index}}

        # 快捷键绑定
        self.accelerator_bindings: dict[str, Callable] = {}

        # 状态管理
        self.menu_states: dict[
            str, dict[str, str]
        ] = {}  # {menu_name: {item_label: state}}

        # 变量管理(用于checkbutton和radiobutton)
        self.menu_variables: dict[str, tk.Variable] = {}

        # 初始化菜单栏
        self._initialize_menu_bar()

        # 加载配置
        if self.config_file:
            self._load_config()

    def _initialize_menu_bar(self) -> None:
        """初始化菜单栏."""
        try:
            # 创建菜单栏
            self.menu_bar = tk.Menu(self.parent)
            self.parent.config(menu=self.menu_bar)

            self.logger.debug("菜单栏初始化完成")

        except Exception as e:
            self.logger.exception(f"菜单栏初始化失败: {e}")
            raise

    def add_menu(self, menu_config: MenuConfig) -> tk.Menu:
        """添加菜单.

        Args:
            menu_config: 菜单配置

        Returns:
            创建的菜单对象
        """
        try:
            if not self.menu_bar:
                msg = "菜单栏未初始化"
                raise ValueError(msg)

            # 创建菜单
            menu = tk.Menu(self.menu_bar, tearoff=0)

            # 添加到菜单栏
            self.menu_bar.add_cascade(
                label=menu_config.label, menu=menu, underline=menu_config.underline
            )

            # 保存菜单引用
            self.menus[menu_config.label] = menu
            self.menu_configs[menu_config.label] = menu_config
            self.menu_items[menu_config.label] = {}
            self.menu_states[menu_config.label] = {}

            # 添加菜单项
            self._populate_menu(menu, menu_config)

            self.logger.debug(f"菜单添加完成: {menu_config.label}")
            return menu

        except Exception as e:
            self.logger.exception(f"菜单添加失败: {e}")
            raise

    def _populate_menu(self, menu: tk.Menu, menu_config: MenuConfig) -> None:
        """填充菜单项.

        Args:
            menu: 菜单对象
            menu_config: 菜单配置
        """
        try:
            item_index = 0

            for item_config in menu_config.items:
                # 添加前置分隔符
                if item_config.separator_before:
                    menu.add_separator()
                    item_index += 1

                # 添加菜单项
                if item_config.item_type == "separator":
                    menu.add_separator()
                elif item_config.item_type == "command":
                    menu.add_command(
                        label=item_config.label,
                        command=item_config.command,
                        accelerator=item_config.accelerator,
                        underline=item_config.underline,
                        state=item_config.state,
                    )
                elif item_config.item_type == "checkbutton":
                    menu.add_checkbutton(
                        label=item_config.label,
                        variable=item_config.variable,
                        command=item_config.command,
                        accelerator=item_config.accelerator,
                        underline=item_config.underline,
                        state=item_config.state,
                    )
                elif item_config.item_type == "radiobutton":
                    menu.add_radiobutton(
                        label=item_config.label,
                        variable=item_config.variable,
                        value=item_config.value,
                        command=item_config.command,
                        accelerator=item_config.accelerator,
                        underline=item_config.underline,
                        state=item_config.state,
                    )

                # 保存菜单项索引和状态
                if item_config.item_type != "separator":
                    self.menu_items[menu_config.label][item_config.label] = item_index
                    self.menu_states[menu_config.label][item_config.label] = (
                        item_config.state
                    )

                    # 绑定快捷键
                    if item_config.accelerator and item_config.command:
                        self._bind_accelerator(
                            item_config.accelerator, item_config.command
                        )

                item_index += 1

                # 添加后置分隔符
                if item_config.separator_after:
                    menu.add_separator()
                    item_index += 1

        except Exception as e:
            self.logger.exception(f"菜单项填充失败: {e}")
            raise

    def _bind_accelerator(self, accelerator: str, command: Callable) -> None:
        """绑定快捷键.

        Args:
            accelerator: 快捷键字符串
            command: 命令函数
        """
        try:
            # 转换快捷键格式
            key_binding = self._convert_accelerator_to_binding(accelerator)
            if key_binding:
                self.parent.bind_all(key_binding, lambda event: command())
                self.accelerator_bindings[key_binding] = command
                self.logger.debug(f"快捷键绑定: {accelerator} -> {key_binding}")

        except Exception as e:
            self.logger.warning(f"快捷键绑定失败 [{accelerator}]: {e}")

    def _convert_accelerator_to_binding(self, accelerator: str) -> str | None:
        """转换快捷键格式.

        Args:
            accelerator: 快捷键显示文本(如 "Ctrl+N")

        Returns:
            tkinter绑定格式(如 "<Control-n>")
        """
        if not accelerator:
            return None

        try:
            # 常见快捷键映射
            key_mappings = {
                "Ctrl": "Control",
                "Alt": "Alt",
                "Shift": "Shift",
                "Cmd": "Command",  # macOS
                "Meta": "Meta",
            }

            # 解析快捷键
            parts = accelerator.split("+")
            if len(parts) < 2:
                return None

            modifiers = []
            key = parts[-1]

            # 处理修饰键
            for part in parts[:-1]:
                part = part.strip()
                if part in key_mappings:
                    modifiers.append(key_mappings[part])

            # 处理特殊键(保持大写)和普通键(转小写)
            if key.startswith("F") and key[1:].isdigit():  # 功能键 F1, F2, etc.
                key = key
            elif len(key) == 1 and key.isalpha():  # 单个字母
                key = key.lower()
            # 其他特殊键保持原样

            # 构建绑定字符串
            return f"<{'-'.join(modifiers)}-{key}>" if modifiers else f"<{key}>"

        except Exception as e:
            self.logger.warning(f"快捷键格式转换失败 [{accelerator}]: {e}")
            return None

    def get_menu(self, menu_name: str) -> tk.Menu | None:
        """获取菜单对象.

        Args:
            menu_name: 菜单名称

        Returns:
            菜单对象,如果不存在则返回None
        """
        return self.menus.get(menu_name)

    def set_menu_item_state(self, menu_name: str, item_label: str, state: str) -> None:
        """设置菜单项状态.

        Args:
            menu_name: 菜单名称
            item_label: 菜单项标签
            state: 状态 ("normal", "disabled", "active")
        """
        try:
            menu = self.menus.get(menu_name)
            if not menu:
                self.logger.warning(f"菜单不存在: {menu_name}")
                return

            item_index = self.menu_items.get(menu_name, {}).get(item_label)
            if item_index is None:
                self.logger.warning(f"菜单项不存在: {menu_name}.{item_label}")
                return

            # 设置状态
            menu.entryconfig(item_index, state=state)

            # 更新状态记录
            self.menu_states[menu_name][item_label] = state

            self.logger.debug(f"菜单项状态更新: {menu_name}.{item_label} -> {state}")

        except Exception as e:
            self.logger.exception(f"菜单项状态设置失败: {e}")

    def get_menu_item_state(self, menu_name: str, item_label: str) -> str | None:
        """获取菜单项状态.

        Args:
            menu_name: 菜单名称
            item_label: 菜单项标签

        Returns:
            菜单项状态,如果不存在则返回None
        """
        return self.menu_states.get(menu_name, {}).get(item_label)

    def enable_menu_item(self, menu_name: str, item_label: str) -> None:
        """启用菜单项.

        Args:
            menu_name: 菜单名称
            item_label: 菜单项标签
        """
        self.set_menu_item_state(menu_name, item_label, "normal")

    def disable_menu_item(self, menu_name: str, item_label: str) -> None:
        """禁用菜单项.

        Args:
            menu_name: 菜单名称
            item_label: 菜单项标签
        """
        self.set_menu_item_state(menu_name, item_label, "disabled")

    def set_menu_item_variable(self, variable_name: str, variable: tk.Variable) -> None:
        """设置菜单项变量.

        Args:
            variable_name: 变量名称
            variable: 变量对象
        """
        self.menu_variables[variable_name] = variable

    def get_menu_item_variable(self, variable_name: str) -> tk.Variable | None:
        """获取菜单项变量.

        Args:
            variable_name: 变量名称

        Returns:
            变量对象,如果不存在则返回None
        """
        return self.menu_variables.get(variable_name)

    def update_menu_item_command(
        self, menu_name: str, item_label: str, command: Callable
    ) -> None:
        """更新菜单项命令.

        Args:
            menu_name: 菜单名称
            item_label: 菜单项标签
            command: 新的命令函数
        """
        try:
            menu = self.menus.get(menu_name)
            if not menu:
                self.logger.warning(f"菜单不存在: {menu_name}")
                return

            item_index = self.menu_items.get(menu_name, {}).get(item_label)
            if item_index is None:
                self.logger.warning(f"菜单项不存在: {menu_name}.{item_label}")
                return

            # 更新命令
            menu.entryconfig(item_index, command=command)

            self.logger.debug(f"菜单项命令更新: {menu_name}.{item_label}")

        except Exception as e:
            self.logger.exception(f"菜单项命令更新失败: {e}")

    def remove_menu(self, menu_name: str) -> None:
        """移除菜单.

        Args:
            menu_name: 菜单名称
        """
        try:
            if menu_name not in self.menus:
                self.logger.warning(f"菜单不存在: {menu_name}")
                return

            # 从菜单栏移除
            if self.menu_bar:
                # 查找菜单在菜单栏中的索引
                menu_count = self.menu_bar.index(tk.END)
                if menu_count is not None:
                    for i in range(menu_count + 1):
                        try:
                            label = self.menu_bar.entrycget(i, "label")
                            if label == menu_name:
                                self.menu_bar.delete(i)
                                break
                        except tk.TclError:
                            continue

            # 清理引用
            del self.menus[menu_name]
            del self.menu_configs[menu_name]
            del self.menu_items[menu_name]
            del self.menu_states[menu_name]

            self.logger.debug(f"菜单移除完成: {menu_name}")

        except Exception as e:
            self.logger.exception(f"菜单移除失败: {e}")

    def clear_all_menus(self) -> None:
        """清除所有菜单."""
        try:
            if self.menu_bar:
                # 删除所有菜单
                menu_count = self.menu_bar.index(tk.END)
                if menu_count is not None:
                    for i in range(menu_count, -1, -1):
                        try:
                            self.menu_bar.delete(i)
                        except tk.TclError:
                            continue

            # 清理所有引用
            self.menus.clear()
            self.menu_configs.clear()
            self.menu_items.clear()
            self.menu_states.clear()

            # 清理快捷键绑定
            for key_binding in self.accelerator_bindings:
                with contextlib.suppress(tk.TclError):
                    self.parent.unbind_all(key_binding)
            self.accelerator_bindings.clear()

            self.logger.debug("所有菜单清除完成")

        except Exception as e:
            self.logger.exception(f"菜单清除失败: {e}")

    def _load_config(self) -> None:
        """加载菜单配置."""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                self.logger.debug("菜单配置文件不存在,跳过加载")
                return

            with open(self.config_file, encoding="utf-8") as f:
                config_data = json.load(f)

            # 加载菜单配置
            menus_config = config_data.get("menus", [])
            for menu_data in menus_config:
                menu_config = self._create_menu_config_from_data(menu_data)
                if menu_config:
                    self.add_menu(menu_config)

            self.logger.info(f"菜单配置加载完成: {self.config_file}")

        except Exception as e:
            self.logger.exception(f"菜单配置加载失败: {e}")

    def _create_menu_config_from_data(
        self, menu_data: dict[str, Any]
    ) -> MenuConfig | None:
        """从数据创建菜单配置.

        Args:
            menu_data: 菜单数据

        Returns:
            菜单配置对象
        """
        try:
            menu_config = MenuConfig(
                label=menu_data.get("label", ""),
                underline=menu_data.get("underline", -1),
            )

            # 添加菜单项
            items_data = menu_data.get("items", [])
            for item_data in items_data:
                item_config = self._create_menu_item_config_from_data(item_data)
                if item_config:
                    menu_config.add_item(item_config)

            return menu_config

        except Exception as e:
            self.logger.exception(f"菜单配置创建失败: {e}")
            return None

    def _create_menu_item_config_from_data(
        self, item_data: dict[str, Any]
    ) -> MenuItemConfig | None:
        """从数据创建菜单项配置.

        Args:
            item_data: 菜单项数据

        Returns:
            菜单项配置对象
        """
        try:
            # 注意:从配置文件加载时,command需要通过其他方式设置
            return MenuItemConfig(
                label=item_data.get("label", ""),
                accelerator=item_data.get("accelerator", ""),
                underline=item_data.get("underline", -1),
                state=item_data.get("state", "normal"),
                item_type=item_data.get("type", "command"),
                separator_before=item_data.get("separator_before", False),
                separator_after=item_data.get("separator_after", False),
                tooltip=item_data.get("tooltip", ""),
                icon=item_data.get("icon", ""),
            )

        except Exception as e:
            self.logger.exception(f"菜单项配置创建失败: {e}")
            return None

    def save_config(self, config_file: str | None = None) -> None:
        """保存菜单配置.

        Args:
            config_file: 配置文件路径,如果为None则使用默认路径
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                self.logger.warning("未指定配置文件路径")
                return

            # 构建配置数据
            config_data = {"menus": []}

            for menu_config in self.menu_configs.values():
                menu_data = {
                    "label": menu_config.label,
                    "underline": menu_config.underline,
                    "items": [],
                }

                for item_config in menu_config.items:
                    item_data = {
                        "label": item_config.label,
                        "accelerator": item_config.accelerator,
                        "underline": item_config.underline,
                        "state": item_config.state,
                        "type": item_config.item_type,
                        "separator_before": item_config.separator_before,
                        "separator_after": item_config.separator_after,
                        "tooltip": item_config.tooltip,
                        "icon": item_config.icon,
                    }
                    menu_data["items"].append(item_data)

                config_data["menus"].append(menu_data)

            # 确保目录存在
            config_dir = os.path.dirname(save_path)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"菜单配置保存完成: {save_path}")

        except Exception as e:
            self.logger.exception(f"菜单配置保存失败: {e}")

    def get_menu_structure(self) -> dict[str, Any]:
        """获取菜单结构信息.

        Returns:
            菜单结构字典
        """
        structure = {}

        for menu_name, menu_config in self.menu_configs.items():
            menu_info = {
                "label": menu_config.label,
                "underline": menu_config.underline,
                "items": [],
            }

            for item_config in menu_config.items:
                item_info = {
                    "label": item_config.label,
                    "type": item_config.item_type,
                    "accelerator": item_config.accelerator,
                    "state": self.menu_states.get(menu_name, {}).get(
                        item_config.label, "normal"
                    ),
                    "tooltip": item_config.tooltip,
                }
                menu_info["items"].append(item_info)

            structure[menu_name] = menu_info

        return structure

    def cleanup(self) -> None:
        """清理菜单栏资源."""
        try:
            # 自动保存配置
            if self.auto_save_config and self.config_file:
                self.save_config()

            # 清理快捷键绑定
            for key_binding in self.accelerator_bindings:
                with contextlib.suppress(tk.TclError):
                    self.parent.unbind_all(key_binding)

            # 清理引用
            self.menus.clear()
            self.menu_configs.clear()
            self.menu_items.clear()
            self.menu_states.clear()
            self.accelerator_bindings.clear()
            self.menu_variables.clear()

            self.logger.debug("菜单栏资源清理完成")

        except Exception as e:
            self.logger.exception(f"菜单栏资源清理失败: {e}")
