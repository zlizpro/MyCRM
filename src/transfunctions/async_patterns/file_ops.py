"""
统一文件操作接口

提供同步和异步文件操作的统一接口。
"""

from .core import AsyncPatternMixin


class UnifiedFileOperations(AsyncPatternMixin):
    """统一的文件操作接口"""

    def __init__(self):
        super().__init__()

    def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """统一的文件读取接口"""

        def sync_read():
            with open(file_path, encoding=encoding) as f:
                return f.read()

        async def async_read():
            try:
                import aiofiles

                async with aiofiles.open(file_path, encoding=encoding) as f:
                    return await f.read()
            except ImportError:
                return await self._wrap_sync_to_async(sync_read)()

        return self.sync_or_async(sync_read, async_read)()

    def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> None:
        """统一的文件写入接口"""

        def sync_write():
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)

        async def async_write():
            try:
                import aiofiles

                async with aiofiles.open(file_path, "w", encoding=encoding) as f:
                    await f.write(content)
            except ImportError:
                await self._wrap_sync_to_async(sync_write)()

        return self.sync_or_async(sync_write, async_write)()


def create_unified_file_ops():
    """创建统一文件操作实例"""
    return UnifiedFileOperations()
