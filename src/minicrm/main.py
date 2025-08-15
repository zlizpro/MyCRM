#!/usr/bin/env python3
"""
MiniCRM 主应用程序入口

这是MiniCRM系统的主入口文件，负责初始化Qt应用程序、
设置应用程序配置、创建主窗口并启动事件循环。

作者: MiniCRM Team
版本: 0.1.0
"""

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from minicrm.application import MiniCRMApplication
from minicrm.core.config import AppConfig
from minicrm.core.logger import setup_logging
from minicrm.ui.main_window import MainWindow


def setup_application() -> QApplication:
    """
    设置Qt应用程序的基础配置

    配置包括：
    - 应用程序基本信息
    - 高DPI显示支持
    - 样式和主题设置
    - 图标和资源路径

    Returns:
        QApplication: 配置完成的Qt应用程序实例
    """
    # 启用高DPI显示支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    # 注意：在PySide6中，高DPI支持默认启用，这些属性已被弃用
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 已弃用
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # 已弃用

    # 创建Qt应用程序实例
    app = QApplication(sys.argv)

    # 设置应用程序基本信息
    app.setApplicationName("MiniCRM")
    app.setApplicationVersion("0.1.0")
    app.setApplicationDisplayName("MiniCRM - 客户关系管理系统")
    app.setOrganizationName("MiniCRM Team")
    app.setOrganizationDomain("minicrm.com")

    # 设置应用程序图标
    icon_path = Path(__file__).parent / "resources" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        # 如果图标文件不存在，生成程序化图标
        try:
            from minicrm.resources.icon_generator import create_app_icon, save_app_icon

            # 生成并设置图标
            app_icon = create_app_icon(64)
            app.setWindowIcon(app_icon)

            # 尝试保存图标文件供下次使用
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            save_app_icon(str(icon_path), 64)

        except Exception:
            # 如果生成失败，使用Qt内置图标作为备选方案
            from PySide6.QtWidgets import QStyle

            style = app.style()
            if style:
                icon = style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
                app.setWindowIcon(icon)

    return app


def main() -> int:
    """
    主函数 - 应用程序入口点

    执行流程：
    1. 设置日志系统
    2. 加载应用程序配置
    3. 创建Qt应用程序
    4. 初始化MiniCRM应用程序
    5. 创建并显示主窗口
    6. 启动事件循环

    Returns:
        int: 应用程序退出代码
    """
    try:
        # 设置日志系统
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("正在启动MiniCRM应用程序...")

        # 加载应用程序配置
        config = AppConfig()
        logger.info("应用程序配置加载完成")

        # 创建Qt应用程序
        qt_app = setup_application()
        logger.info("Qt应用程序初始化完成")

        # 创建MiniCRM应用程序实例
        minicrm_app = MiniCRMApplication(config)
        logger.info("MiniCRM应用程序实例创建完成")

        # 创建主窗口
        main_window = MainWindow(minicrm_app)
        main_window.show()
        logger.info("主窗口创建并显示完成")

        # 启动事件循环
        logger.info("启动Qt事件循环...")
        exit_code = qt_app.exec()

        logger.info(f"应用程序退出，退出代码: {exit_code}")
        return exit_code

    except Exception as e:
        # 处理启动过程中的异常
        logging.error(f"应用程序启动失败: {e}", exc_info=True)
        return 1

    finally:
        # 清理资源
        logging.info("正在清理应用程序资源...")


if __name__ == "__main__":
    sys.exit(main())
