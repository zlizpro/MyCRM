"""MiniCRM应用程序主入口.

负责应用程序的启动、初始化和主要生命周期管理.
"""

from pathlib import Path
import sys


# 添加src目录到Python路径
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入MiniCRM模块 - 必须在路径设置后导入
from minicrm.config.settings import get_config, load_config  # noqa: E402
from minicrm.core.constants import APP_NAME, APP_VERSION  # noqa: E402
from minicrm.core.exceptions import ConfigurationError, MiniCRMError  # noqa: E402
from minicrm.core.hooks import shutdown_hooks  # noqa: E402
from minicrm.core.logging import (  # noqa: E402
    get_logger,
    initialize_logging,
    shutdown_logging,
)


def setup_application() -> None:
    """设置应用程序环境.

    包括日志系统、配置管理等基础设施的初始化.
    """
    try:
        # 加载配置
        config_manager = load_config()

        # 初始化日志系统
        log_config = config_manager.logging.__dict__
        initialize_logging(log_config)

        logger = get_logger("main")
        logger.info("启动 %s v%s", APP_NAME, APP_VERSION)
        logger.info("应用程序环境设置完成")

    except ConfigurationError as e:
        print(f"配置加载失败: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"系统资源访问失败: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"模块导入失败: {e}")
        sys.exit(1)
    except (ValueError, TypeError) as e:
        print(f"配置数据错误: {e}")
        sys.exit(1)


def cleanup_application() -> None:
    """清理应用程序资源.

    在应用程序退出时清理所有资源.
    """
    try:
        logger = get_logger("main")
        logger.info("正在关闭应用程序...")

        # 关闭钩子系统
        shutdown_hooks()

        # 关闭日志系统
        shutdown_logging()

    except OSError as e:
        print(f"系统资源清理失败: {e}")
    except (ImportError, AttributeError) as e:
        print(f"模块清理失败: {e}")


def main() -> int:
    """主函数.

    应用程序的主入口点.

    Returns:
        应用程序退出代码
    """
    exit_code = 0
    app = None

    try:
        # 设置应用程序
        setup_application()

        logger = get_logger("main")
        logger.info("启动MiniCRM TTK应用程序...")

        # 获取配置管理器
        config = get_config()
        logger.info("配置加载完成")
        logger.info("数据库路径: %s", config.database.path)
        logger.info("日志级别: %s", config.logging.level)
        logger.info("UI主题: %s", config.ui.theme)

        # 创建并运行TTK应用程序
        from minicrm.application_ttk import MiniCRMApplicationTTK

        logger.info("正在创建TTK应用程序实例...")
        app = MiniCRMApplicationTTK(config)

        logger.info("TTK应用程序创建成功,开始运行...")
        print(f"\n🎉 {APP_NAME} v{APP_VERSION} TTK版本启动成功!")
        print("📋 所有业务面板已加载")
        print("⚙️  服务层连接正常")
        print("📝 数据库连接就绪")
        print("🎨 TTK界面系统运行中")
        print("\n✨ 欢迎使用MiniCRM!")

        # 运行应用程序主循环
        app.run()

    except KeyboardInterrupt:
        logger = get_logger("main")
        logger.info("用户中断应用程序")
        exit_code = 130

    except MiniCRMError as e:
        logger = get_logger("main")
        logger.exception("MiniCRM错误")
        print(f"错误: {e}")
        exit_code = 1

    except (OSError, ImportError, ValueError, TypeError) as e:
        logger = get_logger("main")
        logger.exception("系统错误")
        print(f"严重错误: {e}")
        exit_code = 2

    finally:
        # 清理应用程序资源
        if app:
            try:
                app.shutdown()
                logger.info("TTK应用程序已关闭")
            except Exception as e:
                logger.error("TTK应用程序关闭时发生错误: %s", e)

        # 清理其他资源
        cleanup_application()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
