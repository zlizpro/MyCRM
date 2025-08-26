"""MiniCRM 自动备份调度器 - TTK版本

负责自动备份的调度和管理,包括:
- 定时备份执行
- 备份策略管理
- 清理策略执行
- 备份状态监控

TTK版本特点:
- 使用Python标准库的threading.Timer替代Qt定时器
- 基于回调函数的事件通知机制
- 完全兼容tkinter/ttk环境
"""

from datetime import datetime, timedelta
import threading
from typing import Any, Callable

from ..core import get_logger
from ..services.backup_service import BackupService
from ..services.settings_service import SettingsService


class BackupSchedulerTTK:
    """自动备份调度器 - TTK版本

    使用Python标准库定时器实现定期备份调度,支持多种备份策略.
    """

    def __init__(
        self,
        backup_service: BackupService,
        settings_service: SettingsService,
    ):
        """初始化备份调度器

        Args:
            backup_service: 备份服务
            settings_service: 设置服务
        """
        self._backup_service = backup_service
        self._settings_service = settings_service
        self._logger = get_logger(self.__class__.__name__)

        # 定时器
        self._backup_timer: threading.Timer | None = None
        self._cleanup_timer: threading.Timer | None = None

        # 状态
        self._is_running = False
        self._last_backup_time: datetime | None = None
        self._backup_in_progress = False

        # 回调函数集合 - 替代Qt信号
        self._backup_started_callbacks: set[Callable[[], None]] = set()
        self._backup_completed_callbacks: set[Callable[[str], None]] = set()
        self._backup_failed_callbacks: set[Callable[[str], None]] = set()
        self._cleanup_completed_callbacks: set[Callable[[int], None]] = set()

    def connect_backup_started(self, callback: Callable[[], None]) -> None:
        """连接备份开始回调函数"""
        self._backup_started_callbacks.add(callback)

    def disconnect_backup_started(self, callback: Callable[[], None]) -> None:
        """断开备份开始回调函数"""
        self._backup_started_callbacks.discard(callback)

    def connect_backup_completed(self, callback: Callable[[str], None]) -> None:
        """连接备份完成回调函数"""
        self._backup_completed_callbacks.add(callback)

    def disconnect_backup_completed(self, callback: Callable[[str], None]) -> None:
        """断开备份完成回调函数"""
        self._backup_completed_callbacks.discard(callback)

    def connect_backup_failed(self, callback: Callable[[str], None]) -> None:
        """连接备份失败回调函数"""
        self._backup_failed_callbacks.add(callback)

    def disconnect_backup_failed(self, callback: Callable[[str], None]) -> None:
        """断开备份失败回调函数"""
        self._backup_failed_callbacks.discard(callback)

    def connect_cleanup_completed(self, callback: Callable[[int], None]) -> None:
        """连接清理完成回调函数"""
        self._cleanup_completed_callbacks.add(callback)

    def disconnect_cleanup_completed(self, callback: Callable[[int], None]) -> None:
        """断开清理完成回调函数"""
        self._cleanup_completed_callbacks.discard(callback)

    def _emit_backup_started(self) -> None:
        """触发备份开始回调"""
        for callback in self._backup_started_callbacks.copy():
            try:
                callback()
            except Exception as e:
                self._logger.error(f"备份开始回调执行失败: {e}")

    def _emit_backup_completed(self, backup_path: str) -> None:
        """触发备份完成回调"""
        for callback in self._backup_completed_callbacks.copy():
            try:
                callback(backup_path)
            except Exception as e:
                self._logger.error(f"备份完成回调执行失败: {e}")

    def _emit_backup_failed(self, error_message: str) -> None:
        """触发备份失败回调"""
        for callback in self._backup_failed_callbacks.copy():
            try:
                callback(error_message)
            except Exception as e:
                self._logger.error(f"备份失败回调执行失败: {e}")

    def _emit_cleanup_completed(self, cleaned_count: int) -> None:
        """触发清理完成回调"""
        for callback in self._cleanup_completed_callbacks.copy():
            try:
                callback(cleaned_count)
            except Exception as e:
                self._logger.error(f"清理完成回调执行失败: {e}")

    def start(self) -> None:
        """启动备份调度器"""
        if self._is_running:
            return

        try:
            # 加载设置
            self._load_settings()

            # 启动定时器
            self._start_backup_timer()
            self._start_cleanup_timer()

            self._is_running = True
            self._logger.info("备份调度器已启动")

        except Exception as e:
            self._logger.error(f"启动备份调度器失败: {e}")

    def stop(self) -> None:
        """停止备份调度器"""
        if not self._is_running:
            return

        try:
            # 停止定时器
            self._stop_backup_timer()
            self._stop_cleanup_timer()

            self._is_running = False
            self._logger.info("备份调度器已停止")

        except Exception as e:
            self._logger.error(f"停止备份调度器失败: {e}")

    def _start_backup_timer(self) -> None:
        """启动备份定时器"""
        if self._backup_timer:
            self._backup_timer.cancel()

        self._backup_timer = threading.Timer(60.0, self._check_backup_schedule)
        self._backup_timer.daemon = True
        self._backup_timer.start()

    def _stop_backup_timer(self) -> None:
        """停止备份定时器"""
        if self._backup_timer:
            self._backup_timer.cancel()
            self._backup_timer = None

    def _start_cleanup_timer(self) -> None:
        """启动清理定时器"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()

        self._cleanup_timer = threading.Timer(3600.0, self._perform_cleanup)
        self._cleanup_timer.daemon = True
        self._cleanup_timer.start()

    def _stop_cleanup_timer(self) -> None:
        """停止清理定时器"""
        if self._cleanup_timer:
            self._cleanup_timer.cancel()
            self._cleanup_timer = None

    def _load_settings(self) -> None:
        """加载备份设置"""
        try:
            self._auto_backup_enabled = self._get_setting("auto_backup", True)
            self._backup_interval = self._get_setting("backup_interval", "daily")
            self._max_backups = self._get_setting("max_backups", 10)
            self._compress_backups = self._get_setting("compress_backups", True)

            self._logger.debug(
                f"备份设置已加载: 自动备份={self._auto_backup_enabled}, "
                f"间隔={self._backup_interval}, 最大备份数={self._max_backups}"
            )

        except Exception as e:
            self._logger.error(f"加载备份设置失败: {e}")
            # 使用默认设置
            self._auto_backup_enabled = True
            self._backup_interval = "daily"
            self._max_backups = 10
            self._compress_backups = True

    def _get_setting(self, key: str, default_value: Any) -> Any:
        """获取设置值"""
        try:
            return self._settings_service.get_setting("database", key)
        except Exception:
            return default_value

    def _check_backup_schedule(self) -> None:
        """检查备份调度"""
        try:
            if not self._auto_backup_enabled or self._backup_in_progress:
                return

            if self._should_create_backup():
                self._perform_backup()

        except Exception as e:
            self._logger.error(f"检查备份调度失败: {e}")
        finally:
            # 重新启动定时器
            if self._is_running:
                self._start_backup_timer()

    def _should_create_backup(self) -> bool:
        """检查是否应该创建备份"""
        try:
            # 获取最近的自动备份时间
            backups = self._backup_service.list_backups()
            auto_backups = [
                b
                for b in backups
                if f"auto_backup_{self._backup_interval}" in b["name"]
            ]

            if not auto_backups:
                return True

            # 获取最近的自动备份时间
            latest_backup = max(auto_backups, key=lambda x: x["created_time"])
            latest_time = latest_backup["created_time"]

            # 计算时间间隔
            now = datetime.now()
            if self._backup_interval == "daily":
                return (now - latest_time) >= timedelta(days=1)
            if self._backup_interval == "weekly":
                return (now - latest_time) >= timedelta(weeks=1)
            if self._backup_interval == "monthly":
                return (now - latest_time) >= timedelta(days=30)

            return False

        except Exception as e:
            self._logger.error(f"检查备份条件失败: {e}")
            return True  # 出错时默认创建备份

    def _perform_backup(self) -> None:
        """执行备份"""
        if self._backup_in_progress:
            return

        self._backup_in_progress = True
        self._emit_backup_started()

        try:
            # 生成备份名称
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_backup_{self._backup_interval}_{timestamp}"

            # 在后台线程中执行备份
            backup_thread = threading.Thread(
                target=self._backup_worker, args=(backup_name,), daemon=True
            )
            backup_thread.start()

        except Exception as e:
            self._backup_in_progress = False
            error_msg = f"启动备份失败: {e}"
            self._logger.error(error_msg)
            self._emit_backup_failed(error_msg)

    def _backup_worker(self, backup_name: str) -> None:
        """备份工作线程"""
        try:
            # 创建备份
            backup_path = self._backup_service.create_backup(
                backup_name, compress=self._compress_backups
            )

            self._last_backup_time = datetime.now()
            self._logger.info(f"自动备份完成: {backup_path}")
            self._emit_backup_completed(backup_path)

        except Exception as e:
            error_msg = f"自动备份失败: {e}"
            self._logger.error(error_msg)
            self._emit_backup_failed(error_msg)

        finally:
            self._backup_in_progress = False

    def _perform_cleanup(self) -> None:
        """执行清理"""
        try:
            # 清理旧备份
            cleaned_count = self._backup_service.cleanup_old_backups(self._max_backups)

            if cleaned_count > 0:
                self._logger.info(f"清理完成,删除了 {cleaned_count} 个旧备份")
                self._emit_cleanup_completed(cleaned_count)

        except Exception as e:
            self._logger.error(f"清理备份失败: {e}")
        finally:
            # 重新启动清理定时器
            if self._is_running:
                self._start_cleanup_timer()

    def force_backup(self) -> None:
        """强制执行备份"""
        if self._backup_in_progress:
            self._logger.warning("备份正在进行中,无法强制执行")
            return

        try:
            self._perform_backup()
        except Exception as e:
            self._logger.error(f"强制备份失败: {e}")

    def update_settings(self) -> None:
        """更新设置"""
        try:
            self._load_settings()
            self._logger.info("备份设置已更新")
        except Exception as e:
            self._logger.error(f"更新备份设置失败: {e}")

    def get_status(self) -> dict[str, Any]:
        """获取调度器状态"""
        return {
            "is_running": self._is_running,
            "auto_backup_enabled": getattr(self, "_auto_backup_enabled", False),
            "backup_interval": getattr(self, "_backup_interval", "daily"),
            "max_backups": getattr(self, "_max_backups", 10),
            "last_backup_time": self._last_backup_time,
            "backup_in_progress": self._backup_in_progress,
        }

    def get_next_backup_time(self) -> datetime | None:
        """获取下次备份时间"""
        if not self._auto_backup_enabled:
            return None

        try:
            # 获取最近的自动备份时间
            backups = self._backup_service.list_backups()
            auto_backups = [
                b
                for b in backups
                if f"auto_backup_{self._backup_interval}" in b["name"]
            ]

            if not auto_backups:
                return datetime.now()  # 立即备份

            # 计算下次备份时间
            latest_backup = max(auto_backups, key=lambda x: x["created_time"])
            latest_time = latest_backup["created_time"]

            if self._backup_interval == "daily":
                return latest_time + timedelta(days=1)
            if self._backup_interval == "weekly":
                return latest_time + timedelta(weeks=1)
            if self._backup_interval == "monthly":
                return latest_time + timedelta(days=30)

            return None

        except Exception as e:
            self._logger.error(f"计算下次备份时间失败: {e}")
            return None

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running

    @property
    def backup_in_progress(self) -> bool:
        """是否正在备份"""
        return self._backup_in_progress


# 为了兼容性,创建一个别名
BackupScheduler = BackupSchedulerTTK
