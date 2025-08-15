"""
统一API客户端接口

提供同步和异步HTTP请求的统一接口。
"""

from typing import Any

from .core import AsyncPatternMixin


class UnifiedAPIClient(AsyncPatternMixin):
    """统一的API客户端接口"""

    def __init__(self, base_url: str = ""):
        super().__init__()
        self.base_url = base_url

    def request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """统一的HTTP请求接口"""

        def sync_request():
            import requests

            response = requests.request(method, f"{self.base_url}{url}", **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}

        async def async_request():
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, f"{self.base_url}{url}", **kwargs
                ) as response:
                    response.raise_for_status()
                    return await response.json() if response.content_length else {}

        return self.sync_or_async(sync_request, async_request)()

    def get(self, url: str, **kwargs) -> dict[str, Any]:
        """GET请求"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> dict[str, Any]:
        """POST请求"""
        return self.request("POST", url, **kwargs)


def create_unified_api_client(base_url: str = ""):
    """创建统一API客户端实例"""
    return UnifiedAPIClient(base_url)
