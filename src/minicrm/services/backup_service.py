"""
MiniCRM 备份管理服务

负责数据库备份和恢复功能,包括:
- 手动备份
- 自动备份调度
- 备份文件管理
- 数据恢复
- 备份压缩和验证
"""

import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..core import BusinessLogicError, ValidationError
from ..data.database import DatabaseManager
from ..services.base_service import BaseService


class BackupService(BaseService):
    """
    备份管理服务

    提供完整的数据库备份和恢复功能,支持自动备份调度和备份文件管理.
    """

    def __init__(self, database_manager: DatabaseManager):
        """
        初始化备份服务

        Args:
            database_manager: 数据库管理器
        """
        super().__init__()
        self._db_manager = database_manager
        self._backup_dir = self._get_backup_directory()
        self._ensure_backup_directory()

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "BackupService"

    def _get_backup_directory(self) -> Path:
        """
        获取备份目录路径

        Returns:
            Path: 备份目录路径
        """
        backup_dir = (
            Path.home() / "Library" / "Application Support" / "MiniCRM" / "backups"
        )
        return backup_dir

    def _ensure_backup_directory(self) -> None:
        """确保备份目录存在"""
        try:
            self._backup_dir.mkdir(parents=True, exist_ok=True)
            self._logger.info(f"备份目录已准备: {self._backup_dir}")
        except Exception as e:
            self._logger.error(f"创建备份目录失败: {e}")
            raise BusinessLogicError(f"创建备份目录失败: {e}")

    def create_backup(self, backup_name: str = None, compress: bool = True) -> str:
        """
        创建数据库备份

        Args:
            backup_name: 备份名称,如果为None则自动生成
            compress: 是否压缩备份文件

        Returns:
            str: 备份文件路径

        Raises:
            BusinessLogicError: 当备份失败时
        """
        try:
            # 生成备份文件名
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"minicrm_backup_{timestamp}"

            # 确定文件扩展名
            if compress:
                backup_file = self._backup_dir / f"{backup_name}.db.gz"
            else:
                backup_file = self._backup_dir / f"{backup_name}.db"

            # 获取数据库文件路径
            db_path = self._db_manager.get_database_path()
            if not db_path.exists():
                raise BusinessLogicError("数据库文件不存在,无法创建备份")

            self._logger.info(f"开始创建备份: {backup_file}")

            # 创建备份
            if compress:
                self._create_compressed_backup(db_path, backup_file)
            else:
                self._create_uncompressed_backup(db_path, backup_file)

            # 验证备份文件
            if not self._verify_backup(backup_file, compress):
                backup_file.unlink(missing_ok=True)
                raise BusinessLogicError("备份文件验证失败")

            self._logger.info(f"备份创建成功: {backup_file}")
            return str(backup_file)

        except Exception as e:
            self._logger.error(f"创建备份失败: {e}")
            raise BusinessLogicError(f"创建备份失败: {e}")

    def _create_compressed_backup(self, source_path: Path, backup_path: Path) -> None:
        """
        创建压缩备份

        Args:
            source_path: 源数据库文件路径
            backup_path: 备份文件路径
        """
        with open(source_path, "rb") as source_file:
            with gzip.open(backup_path, "wb") as backup_file:
                shutil.copyfileobj(source_file, backup_file)

    def _create_uncompressed_backup(self, source_path: Path, backup_path: Path) -> None:
        """
        创建未压缩备份

        Args:
            source_path: 源数据库文件路径
            backup_path: 备份文件路径
        """
        shutil.copy2(source_path, backup_path)

    def _verify_backup(self, backup_path: Path, compressed: bool) -> bool:
        """
        验证备份文件完整性

        Args:
            backup_path: 备份文件路径
            compressed: 是否为压缩文件

        Returns:
            bool: 验证是否成功
        """
        try:
            if compressed:
                # 验证压缩文件
                with gzip.open(backup_path, "rb") as f:
                    # 尝试读取文件头验证是否为有效的SQLite文件
                    header = f.read(16)
                    if not header.startswith(b"SQLite format 3"):
                        return False
            else:
                # 验证未压缩文件
                with open(backup_path, "rb") as f:
                    header = f.read(16)
                    if not header.startswith(b"SQLite format 3"):
                        return False

            return True

        except Exception as e:
            self._logger.error(f"验证备份文件失败: {e}")
            return False

    def restore_backup(self, backup_path: str, confirm: bool = False) -> bool:
        """
        从备份恢复数据库

        Args:
            backup_path: 备份文件路径
            confirm: 是否确认恢复(这会覆盖当前数据库)

        Returns:
            bool: 恢复是否成功

        Raises:
            ValidationError: 当备份文件不存在或无效时
            BusinessLogicError: 当恢复失败时
        """
        if not confirm:
            raise ValidationError("恢复数据库需要明确确认,这将覆盖当前所有数据")

        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise ValidationError(f"备份文件不存在: {backup_path}")

            # 检查备份文件是否有效
            compressed = backup_file.suffix == ".gz"
            if not self._verify_backup(backup_file, compressed):
                raise ValidationError("备份文件无效或已损坏")

            # 获取当前数据库路径
            db_path = self._db_manager.get_database_path()

            # 创建当前数据库的临时备份
            temp_backup = None
            if db_path.exists():
                temp_backup = db_path.with_suffix(".db.temp")
                shutil.copy2(db_path, temp_backup)

            try:
                # 关闭数据库连接
                self._db_manager.close()

                # 恢复备份
                if compressed:
                    with gzip.open(backup_file, "rb") as source:
                        with open(db_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                else:
                    shutil.copy2(backup_file, db_path)

                # 重新连接数据库
                self._db_manager._connect()

                # 验证恢复的数据库
                if not self._verify_restored_database():
                    raise BusinessLogicError("恢复的数据库验证失败")

                # 删除临时备份
                if temp_backup and temp_backup.exists():
                    temp_backup.unlink()

                self._logger.info(f"数据库恢复成功: {backup_path}")
                return True

            except Exception as e:
                # 恢复失败,回滚到原数据库
                if temp_backup and temp_backup.exists():
                    shutil.copy2(temp_backup, db_path)
                    temp_backup.unlink()
                    self._db_manager._connect()
                raise BusinessLogicError(f"数据库恢复失败: {e}")

        except Exception as e:
            self._logger.error(f"恢复备份失败: {e}")
            if isinstance(e, ValidationError | BusinessLogicError):
                raise
            else:
                raise BusinessLogicError(f"恢复备份失败: {e}")

    def _verify_restored_database(self) -> bool:
        """
        验证恢复的数据库

        Returns:
            bool: 验证是否成功
        """
        try:
            # 尝试执行简单查询验证数据库完整性
            if not self._db_manager._connection:
                self._db_manager._connect()

            cursor = self._db_manager._connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            # 如果能成功查询sqlite_master,说明数据库是有效的
            return True

        except Exception as e:
            self._logger.error(f"验证恢复的数据库失败: {e}")
            return False

    def list_backups(self) -> list[dict[str, Any]]:
        """
        列出所有备份文件

        Returns:
            List[Dict[str, Any]]: 备份文件信息列表
        """
        backups = []

        try:
            # 查找所有备份文件
            for backup_file in self._backup_dir.glob("*.db*"):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    compressed = backup_file.suffix == ".gz"

                    backup_info = {
                        "name": backup_file.stem.replace(".db", ""),
                        "path": str(backup_file),
                        "size": stat.st_size,
                        "created_time": datetime.fromtimestamp(stat.st_ctime),
                        "modified_time": datetime.fromtimestamp(stat.st_mtime),
                        "compressed": compressed,
                        "valid": self._verify_backup(backup_file, compressed),
                    }
                    backups.append(backup_info)

            # 按创建时间排序(最新的在前)
            backups.sort(key=lambda x: x["created_time"], reverse=True)

        except Exception as e:
            self._logger.error(f"列出备份文件失败: {e}")

        return backups

    def delete_backup(self, backup_path: str) -> bool:
        """
        删除备份文件

        Args:
            backup_path: 备份文件路径

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 当备份文件不存在时
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise ValidationError(f"备份文件不存在: {backup_path}")

            # 确保文件在备份目录中
            if not backup_file.is_relative_to(self._backup_dir):
                raise ValidationError("只能删除备份目录中的文件")

            backup_file.unlink()
            self._logger.info(f"备份文件已删除: {backup_path}")
            return True

        except Exception as e:
            self._logger.error(f"删除备份文件失败: {e}")
            if isinstance(e, ValidationError):
                raise
            else:
                raise BusinessLogicError(f"删除备份文件失败: {e}")

    def cleanup_old_backups(self, max_backups: int = 10) -> int:
        """
        清理旧的备份文件

        Args:
            max_backups: 保留的最大备份数量

        Returns:
            int: 删除的备份文件数量
        """
        try:
            backups = self.list_backups()

            if len(backups) <= max_backups:
                return 0

            # 删除多余的备份文件
            deleted_count = 0
            for backup in backups[max_backups:]:
                try:
                    self.delete_backup(backup["path"])
                    deleted_count += 1
                except Exception as e:
                    self._logger.warning(f"删除备份文件失败: {e}")

            self._logger.info(f"清理完成,删除了 {deleted_count} 个旧备份文件")
            return deleted_count

        except Exception as e:
            self._logger.error(f"清理旧备份失败: {e}")
            return 0

    def get_backup_statistics(self) -> dict[str, Any]:
        """
        获取备份统计信息

        Returns:
            Dict[str, Any]: 备份统计信息
        """
        try:
            backups = self.list_backups()

            total_size = sum(backup["size"] for backup in backups)
            valid_backups = sum(1 for backup in backups if backup["valid"])
            compressed_backups = sum(1 for backup in backups if backup["compressed"])

            oldest_backup = (
                min(backups, key=lambda x: x["created_time"]) if backups else None
            )
            newest_backup = (
                max(backups, key=lambda x: x["created_time"]) if backups else None
            )

            return {
                "total_backups": len(backups),
                "valid_backups": valid_backups,
                "compressed_backups": compressed_backups,
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "backup_directory": str(self._backup_dir),
                "oldest_backup": oldest_backup["created_time"]
                if oldest_backup
                else None,
                "newest_backup": newest_backup["created_time"]
                if newest_backup
                else None,
            }

        except Exception as e:
            self._logger.error(f"获取备份统计信息失败: {e}")
            return {
                "total_backups": 0,
                "valid_backups": 0,
                "compressed_backups": 0,
                "total_size": 0,
                "total_size_mb": 0,
                "backup_directory": str(self._backup_dir),
                "oldest_backup": None,
                "newest_backup": None,
            }

    def schedule_auto_backup(self, interval: str = "daily") -> bool:
        """
        调度自动备份

        Args:
            interval: 备份间隔 (daily, weekly, monthly)

        Returns:
            bool: 调度是否成功

        Note:
            这是一个简化的实现,实际的自动备份调度需要与应用程序的定时器系统集成
        """
        try:
            # 检查是否需要创建备份
            if self._should_create_auto_backup(interval):
                backup_name = (
                    f"auto_backup_{interval}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                self.create_backup(backup_name, compress=True)

                # 清理旧的自动备份
                self._cleanup_auto_backups(interval)

                return True

            return False

        except Exception as e:
            self._logger.error(f"自动备份调度失败: {e}")
            return False

    def _should_create_auto_backup(self, interval: str) -> bool:
        """
        检查是否应该创建自动备份

        Args:
            interval: 备份间隔

        Returns:
            bool: 是否应该创建备份
        """
        try:
            # 查找最近的自动备份
            backups = self.list_backups()
            auto_backups = [
                b for b in backups if f"auto_backup_{interval}" in b["name"]
            ]

            if not auto_backups:
                return True

            # 获取最近的自动备份时间
            latest_backup = max(auto_backups, key=lambda x: x["created_time"])
            latest_time = latest_backup["created_time"]

            # 计算时间间隔
            now = datetime.now()
            if interval == "daily":
                return (now - latest_time) >= timedelta(days=1)
            elif interval == "weekly":
                return (now - latest_time) >= timedelta(weeks=1)
            elif interval == "monthly":
                return (now - latest_time) >= timedelta(days=30)

            return False

        except Exception as e:
            self._logger.error(f"检查自动备份条件失败: {e}")
            return True  # 出错时默认创建备份

    def _cleanup_auto_backups(self, interval: str, max_auto_backups: int = 5) -> None:
        """
        清理旧的自动备份

        Args:
            interval: 备份间隔
            max_auto_backups: 保留的最大自动备份数量
        """
        try:
            backups = self.list_backups()
            auto_backups = [
                b for b in backups if f"auto_backup_{interval}" in b["name"]
            ]

            if len(auto_backups) > max_auto_backups:
                # 删除多余的自动备份
                auto_backups.sort(key=lambda x: x["created_time"])
                for backup in auto_backups[:-max_auto_backups]:
                    self.delete_backup(backup["path"])

        except Exception as e:
            self._logger.error(f"清理自动备份失败: {e}")
