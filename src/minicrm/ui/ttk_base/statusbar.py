"""TTK状态栏系统

提供TTK应用程序的状态栏功能,包括:
- 状态信息显示和更新
- 进度条显示和控制
- 多分区状态栏支持
- 状态栏组件管理
- 实时状态更新

设计目标:
1. 提供灵活的状态信息显示
2. 支持多种状态栏组件
3. 简化状态栏管理和维护
4. 提供良好的用户体验

作者: MiniCRM开发团队
"""

import json
import logging
import os
from pathlib import Path
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class StatusSectionConfig:
    """状态栏分区配置类"""

    def __init__(
        self,
        section_id: str,
        section_type: str = "label",
        text: str = "",
        width: Optional[int] = None,
        anchor: str = "w",
        relief: str = "flat",
        borderwidth: int = 0,
        font: Optional[tuple] = None,
        foreground: Optional[str] = None,
        background: Optional[str] = None,
        sticky: str = "ew",
        padx: int = 5,
        pady: int = 2,
        weight: int = 0,
    ):
        """初始化状态栏分区配置

        Args:
            section_id: 分区唯一标识
            section_type: 分区类型 ("label", "progressbar", "button", "separator")
            text: 显示文本
            width: 分区宽度
            anchor: 文本对齐方式
            relief: 边框样式
            borderwidth: 边框宽度
            font: 字体设置
            foreground: 前景色
            background: 背景色
            sticky: 网格布局粘性
            padx: 水平内边距
            pady: 垂直内边距
            weight: 网格权重
        """
        self.section_id = section_id
        self.section_type = section_type
        self.text = text
        self.width = width
        self.anchor = anchor
        self.relief = relief
        self.borderwidth = borderwidth
        self.font = font
        self.foreground = foreground
        self.background = background
        self.sticky = sticky
        self.padx = padx
        self.pady = pady
        self.weight = weight


class StatusBarTTK:
    """TTK状态栏类

    提供完整的状态栏功能,支持多分区显示、
    进度条、实时更新等功能.
    """

    def __init__(
        self,
        parent: tk.Widget,
        height: int = 25,
        relief: str = "sunken",
        borderwidth: int = 1,
        config_file: Optional[str] = None,
        auto_save_config: bool = True,
    ):
        """初始化状态栏

        Args:
            parent: 父组件
            height: 状态栏高度
            relief: 边框样式
            borderwidth: 边框宽度
            config_file: 配置文件路径
            auto_save_config: 是否自动保存配置
        """
        self.parent = parent
        self.height = height
        self.config_file = config_file
        self.auto_save_config = auto_save_config

        # 日志记录器
        self.logger = logging.getLogger(self.__class__.__name__)

        # 状态栏框架
        self.statusbar_frame: Optional[ttk.Frame] = None

        # 分区管理
        self.sections: Dict[str, tk.Widget] = {}
        self.section_configs: Dict[str, StatusSectionConfig] = {}

        # 状态管理
        self.section_texts: Dict[str, str] = {}
        self.progress_values: Dict[str, float] = {}

        # 更新管理
        self.update_callbacks: Dict[str, List[Callable]] = {}
        self.auto_update_enabled = False
        self.update_interval = 1.0  # 秒
        self.update_thread: Optional[threading.Thread] = None
        self.update_stop_event = threading.Event()

        # 初始化状态栏
        self._initialize_statusbar(relief, borderwidth)

        # 加载配置
        if self.config_file:
            self._load_config()

    def _initialize_statusbar(self, relief: str, borderwidth: int) -> None:
        """初始化状态栏框架"""
        try:
            # 创建状态栏框架
            self.statusbar_frame = ttk.Frame(
                self.parent, relief=relief, borderwidth=borderwidth, height=self.height
            )
            self.statusbar_frame.pack_propagate(False)

            # 配置网格权重
            self.statusbar_frame.columnconfigure(0, weight=1)

            self.logger.debug("状态栏初始化完成")

        except Exception as e:
            self.logger.error(f"状态栏初始化失败: {e}")
            raise

    def get_frame(self) -> ttk.Frame:
        """获取状态栏框架

        Returns:
            状态栏框架对象
        """
        return self.statusbar_frame

    def add_section(self, section_config: StatusSectionConfig) -> Optional[tk.Widget]:
        """添加状态栏分区

        Args:
            section_config: 分区配置

        Returns:
            创建的分区组件
        """
        try:
            if not self.statusbar_frame:
                raise ValueError("状态栏框架未初始化")

            # 创建分区组件
            section = None
            if section_config.section_type == "label":
                section = self._create_label_section(section_config)
            elif section_config.section_type == "progressbar":
                section = self._create_progressbar_section(section_config)
            elif section_config.section_type == "button":
                section = self._create_button_section(section_config)
            elif section_config.section_type == "separator":
                section = self._create_separator_section(section_config)

            if section:
                # 保存分区引用
                self.sections[section_config.section_id] = section
                self.section_configs[section_config.section_id] = section_config
                self.section_texts[section_config.section_id] = section_config.text

                # 布局分区
                self._layout_section(section, section_config)

                self.logger.debug(f"状态栏分区添加完成: {section_config.section_id}")

            return section

        except Exception as e:
            self.logger.error(f"状态栏分区添加失败: {e}")
            raise

    def _create_label_section(self, config: StatusSectionConfig) -> ttk.Label:
        """创建标签分区

        Args:
            config: 分区配置

        Returns:
            标签组件
        """
        label = ttk.Label(
            self.statusbar_frame,
            text=config.text,
            anchor=config.anchor,
            relief=config.relief,
            borderwidth=config.borderwidth,
            font=config.font,
            foreground=config.foreground,
            background=config.background,
            width=config.width,
        )
        return label

    def _create_progressbar_section(
        self, config: StatusSectionConfig
    ) -> ttk.Progressbar:
        """创建进度条分区

        Args:
            config: 分区配置

        Returns:
            进度条组件
        """
        progressbar = ttk.Progressbar(
            self.statusbar_frame,
            mode="determinate",
            length=config.width or 100,
        )

        # 初始化进度值
        self.progress_values[config.section_id] = 0.0

        return progressbar

    def _create_button_section(self, config: StatusSectionConfig) -> ttk.Button:
        """创建按钮分区

        Args:
            config: 分区配置

        Returns:
            按钮组件
        """
        button = ttk.Button(
            self.statusbar_frame,
            text=config.text,
            width=config.width,
        )
        return button

    def _create_separator_section(self, config: StatusSectionConfig) -> ttk.Separator:
        """创建分隔符分区

        Args:
            config: 分区配置

        Returns:
            分隔符组件
        """
        separator = ttk.Separator(self.statusbar_frame, orient="vertical")
        return separator

    def _layout_section(self, section: tk.Widget, config: StatusSectionConfig) -> None:
        """布局分区

        Args:
            section: 分区组件
            config: 分区配置
        """
        # 计算列索引
        column = len(self.sections) - 1

        # 配置列权重
        if config.weight > 0:
            self.statusbar_frame.columnconfigure(column, weight=config.weight)

        # 网格布局
        section.grid(
            row=0,
            column=column,
            sticky=config.sticky,
            padx=config.padx,
            pady=config.pady,
        )

    def get_section(self, section_id: str) -> Optional[tk.Widget]:
        """获取分区组件

        Args:
            section_id: 分区ID

        Returns:
            分区组件,如果不存在则返回None
        """
        return self.sections.get(section_id)

    def set_text(self, section_id: str, text: str) -> None:
        """设置分区文本

        Args:
            section_id: 分区ID
            text: 文本内容
        """
        try:
            section = self.sections.get(section_id)
            if not section:
                self.logger.warning(f"分区不存在: {section_id}")
                return

            # 更新文本
            if hasattr(section, "configure"):
                section.configure(text=text)

            # 更新文本记录
            self.section_texts[section_id] = text

            self.logger.debug(f"分区文本更新: {section_id} -> {text}")

        except Exception as e:
            self.logger.error(f"分区文本设置失败: {e}")

    def get_text(self, section_id: str) -> Optional[str]:
        """获取分区文本

        Args:
            section_id: 分区ID

        Returns:
            分区文本,如果不存在则返回None
        """
        return self.section_texts.get(section_id)

    def set_progress(
        self, section_id: str, value: float, maximum: float = 100.0
    ) -> None:
        """设置进度条值

        Args:
            section_id: 分区ID
            value: 进度值
            maximum: 最大值
        """
        try:
            section = self.sections.get(section_id)
            if not section or not isinstance(section, ttk.Progressbar):
                self.logger.warning(f"进度条分区不存在: {section_id}")
                return

            # 设置最大值
            section.configure(maximum=maximum)

            # 设置进度值
            section.configure(value=value)

            # 更新进度记录
            self.progress_values[section_id] = value / maximum * 100.0

            self.logger.debug(f"进度条更新: {section_id} -> {value}/{maximum}")

        except Exception as e:
            self.logger.error(f"进度条设置失败: {e}")

    def get_progress(self, section_id: str) -> Optional[float]:
        """获取进度条值

        Args:
            section_id: 分区ID

        Returns:
            进度值(百分比),如果不存在则返回None
        """
        return self.progress_values.get(section_id)

    def start_progress(self, section_id: str) -> None:
        """启动进度条动画

        Args:
            section_id: 分区ID
        """
        try:
            section = self.sections.get(section_id)
            if not section or not isinstance(section, ttk.Progressbar):
                self.logger.warning(f"进度条分区不存在: {section_id}")
                return

            # 设置为不确定模式并启动
            section.configure(mode="indeterminate")
            section.start()

            self.logger.debug(f"进度条动画启动: {section_id}")

        except Exception as e:
            self.logger.error(f"进度条动画启动失败: {e}")

    def stop_progress(self, section_id: str) -> None:
        """停止进度条动画

        Args:
            section_id: 分区ID
        """
        try:
            section = self.sections.get(section_id)
            if not section or not isinstance(section, ttk.Progressbar):
                self.logger.warning(f"进度条分区不存在: {section_id}")
                return

            # 停止动画并设置为确定模式
            section.stop()
            section.configure(mode="determinate")

            self.logger.debug(f"进度条动画停止: {section_id}")

        except Exception as e:
            self.logger.error(f"进度条动画停止失败: {e}")

    def set_button_command(self, section_id: str, command: Callable) -> None:
        """设置按钮命令

        Args:
            section_id: 分区ID
            command: 命令函数
        """
        try:
            section = self.sections.get(section_id)
            if not section or not isinstance(section, ttk.Button):
                self.logger.warning(f"按钮分区不存在: {section_id}")
                return

            # 设置命令
            section.configure(command=command)

            self.logger.debug(f"按钮命令设置: {section_id}")

        except Exception as e:
            self.logger.error(f"按钮命令设置失败: {e}")

    def remove_section(self, section_id: str) -> None:
        """移除分区

        Args:
            section_id: 分区ID
        """
        try:
            section = self.sections.get(section_id)
            if not section:
                self.logger.warning(f"分区不存在: {section_id}")
                return

            # 销毁分区
            section.destroy()

            # 清理引用
            del self.sections[section_id]
            del self.section_configs[section_id]
            del self.section_texts[section_id]

            # 清理进度值
            if section_id in self.progress_values:
                del self.progress_values[section_id]

            # 清理更新回调
            if section_id in self.update_callbacks:
                del self.update_callbacks[section_id]

            self.logger.debug(f"分区移除完成: {section_id}")

        except Exception as e:
            self.logger.error(f"分区移除失败: {e}")

    def clear_all_sections(self) -> None:
        """清除所有分区"""
        try:
            # 销毁所有分区
            for section in self.sections.values():
                section.destroy()

            # 清理所有引用
            self.sections.clear()
            self.section_configs.clear()
            self.section_texts.clear()
            self.progress_values.clear()
            self.update_callbacks.clear()

            self.logger.debug("所有分区清除完成")

        except Exception as e:
            self.logger.error(f"分区清除失败: {e}")

    def add_update_callback(self, section_id: str, callback: Callable) -> None:
        """添加更新回调

        Args:
            section_id: 分区ID
            callback: 回调函数
        """
        if section_id not in self.update_callbacks:
            self.update_callbacks[section_id] = []
        self.update_callbacks[section_id].append(callback)

    def remove_update_callback(self, section_id: str, callback: Callable) -> None:
        """移除更新回调

        Args:
            section_id: 分区ID
            callback: 回调函数
        """
        if section_id in self.update_callbacks:
            try:
                self.update_callbacks[section_id].remove(callback)
            except ValueError:
                self.logger.warning(f"更新回调不存在: {section_id}")

    def start_auto_update(self, interval: float = 1.0) -> None:
        """启动自动更新

        Args:
            interval: 更新间隔(秒)
        """
        if self.auto_update_enabled:
            self.logger.warning("自动更新已启动")
            return

        self.update_interval = interval
        self.auto_update_enabled = True
        self.update_stop_event.clear()

        # 启动更新线程
        self.update_thread = threading.Thread(
            target=self._auto_update_worker, daemon=True
        )
        self.update_thread.start()

        self.logger.info(f"自动更新启动,间隔: {interval}秒")

    def stop_auto_update(self) -> None:
        """停止自动更新"""
        if not self.auto_update_enabled:
            return

        self.auto_update_enabled = False
        self.update_stop_event.set()

        # 等待更新线程结束
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2.0)

        self.logger.info("自动更新停止")

    def _auto_update_worker(self) -> None:
        """自动更新工作线程"""
        while self.auto_update_enabled and not self.update_stop_event.is_set():
            try:
                # 执行更新回调
                for section_id, callbacks in self.update_callbacks.items():
                    for callback in callbacks:
                        try:
                            callback(section_id)
                        except Exception as e:
                            self.logger.error(f"更新回调执行失败 [{section_id}]: {e}")

                # 等待下次更新
                self.update_stop_event.wait(self.update_interval)

            except Exception as e:
                self.logger.error(f"自动更新工作线程错误: {e}")

    def show_message(
        self, message: str, duration: float = 3.0, section_id: str = "main"
    ) -> None:
        """显示临时消息

        Args:
            message: 消息内容
            duration: 显示时长(秒)
            section_id: 目标分区ID
        """
        try:
            # 保存原始文本
            original_text = self.get_text(section_id)

            # 显示消息
            self.set_text(section_id, message)

            # 定时恢复原始文本
            def restore_text():
                time.sleep(duration)
                if original_text is not None:
                    self.set_text(section_id, original_text)
                else:
                    self.set_text(section_id, "")

            # 启动恢复线程
            restore_thread = threading.Thread(target=restore_text, daemon=True)
            restore_thread.start()

            self.logger.debug(f"临时消息显示: {message} ({duration}秒)")

        except Exception as e:
            self.logger.error(f"临时消息显示失败: {e}")

    def _load_config(self) -> None:
        """加载状态栏配置"""
        try:
            if not self.config_file or not os.path.exists(self.config_file):
                self.logger.debug("状态栏配置文件不存在,跳过加载")
                return

            with open(self.config_file, encoding="utf-8") as f:
                config_data = json.load(f)

            # 加载分区配置
            sections_config = config_data.get("sections", [])
            for section_data in sections_config:
                section_config = self._create_section_config_from_data(section_data)
                if section_config:
                    self.add_section(section_config)

            self.logger.info(f"状态栏配置加载完成: {self.config_file}")

        except Exception as e:
            self.logger.error(f"状态栏配置加载失败: {e}")

    def _create_section_config_from_data(
        self, section_data: Dict[str, Any]
    ) -> Optional[StatusSectionConfig]:
        """从数据创建分区配置

        Args:
            section_data: 分区数据

        Returns:
            分区配置对象
        """
        try:
            section_config = StatusSectionConfig(
                section_id=section_data.get("id", ""),
                section_type=section_data.get("type", "label"),
                text=section_data.get("text", ""),
                width=section_data.get("width"),
                anchor=section_data.get("anchor", "w"),
                relief=section_data.get("relief", "flat"),
                borderwidth=section_data.get("borderwidth", 0),
                font=section_data.get("font"),
                foreground=section_data.get("foreground"),
                background=section_data.get("background"),
                sticky=section_data.get("sticky", "ew"),
                padx=section_data.get("padx", 5),
                pady=section_data.get("pady", 2),
                weight=section_data.get("weight", 0),
            )

            return section_config

        except Exception as e:
            self.logger.error(f"分区配置创建失败: {e}")
            return None

    def save_config(self, config_file: Optional[str] = None) -> None:
        """保存状态栏配置

        Args:
            config_file: 配置文件路径,如果为None则使用默认路径
        """
        try:
            save_path = config_file or self.config_file
            if not save_path:
                self.logger.warning("未指定配置文件路径")
                return

            # 构建配置数据
            config_data = {"height": self.height, "sections": []}

            for section_id, section_config in self.section_configs.items():
                section_data = {
                    "id": section_config.section_id,
                    "type": section_config.section_type,
                    "text": section_config.text,
                    "width": section_config.width,
                    "anchor": section_config.anchor,
                    "relief": section_config.relief,
                    "borderwidth": section_config.borderwidth,
                    "font": section_config.font,
                    "foreground": section_config.foreground,
                    "background": section_config.background,
                    "sticky": section_config.sticky,
                    "padx": section_config.padx,
                    "pady": section_config.pady,
                    "weight": section_config.weight,
                }
                config_data["sections"].append(section_data)

            # 确保目录存在
            config_dir = os.path.dirname(save_path)
            if config_dir:
                Path(config_dir).mkdir(parents=True, exist_ok=True)

            # 保存配置
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"状态栏配置保存完成: {save_path}")

        except Exception as e:
            self.logger.error(f"状态栏配置保存失败: {e}")

    def get_statusbar_info(self) -> Dict[str, Any]:
        """获取状态栏信息

        Returns:
            状态栏信息字典
        """
        return {
            "height": self.height,
            "section_count": len(self.sections),
            "auto_update_enabled": self.auto_update_enabled,
            "update_interval": self.update_interval,
            "sections": {
                section_id: {
                    "type": config.section_type,
                    "text": self.section_texts.get(section_id, ""),
                    "progress": self.progress_values.get(section_id),
                }
                for section_id, config in self.section_configs.items()
            },
        }

    def cleanup(self) -> None:
        """清理状态栏资源"""
        try:
            # 停止自动更新
            self.stop_auto_update()

            # 自动保存配置
            if self.auto_save_config and self.config_file:
                self.save_config()

            # 清理所有分区
            self.clear_all_sections()

            self.logger.debug("状态栏资源清理完成")

        except Exception as e:
            self.logger.error(f"状态栏资源清理失败: {e}")
