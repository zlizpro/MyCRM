"""MiniCRM 性能配置
集中管理所有性能相关的配置参数
"""

import os
from typing import Any


class PerformanceConfig:
    """性能配置类"""

    # 数据库性能配置
    DB_CONNECTION_POOL_SIZE = int(os.getenv("MINICRM_DB_POOL_SIZE", "5"))
    DB_QUERY_TIMEOUT = int(os.getenv("MINICRM_DB_TIMEOUT", "30"))
    DB_BATCH_SIZE = int(os.getenv("MINICRM_DB_BATCH_SIZE", "1000"))
    DB_CACHE_SIZE = int(os.getenv("MINICRM_DB_CACHE_SIZE", "10000"))

    # UI性能配置
    UI_UPDATE_INTERVAL = int(os.getenv("MINICRM_UI_UPDATE_INTERVAL", "50"))  # ms
    TABLE_PAGE_SIZE = int(os.getenv("MINICRM_TABLE_PAGE_SIZE", "50"))
    CHART_MAX_POINTS = int(os.getenv("MINICRM_CHART_MAX_POINTS", "1000"))
    UI_THREAD_POOL_SIZE = int(os.getenv("MINICRM_UI_THREAD_POOL", "4"))

    # 缓存配置
    CACHE_SIZE = int(os.getenv("MINICRM_CACHE_SIZE", "128"))
    CACHE_TTL = int(os.getenv("MINICRM_CACHE_TTL", "300"))  # seconds
    ENABLE_QUERY_CACHE = (
        os.getenv("MINICRM_ENABLE_QUERY_CACHE", "true").lower() == "true"
    )

    # 内存管理配置
    MEMORY_WARNING_THRESHOLD = int(os.getenv("MINICRM_MEMORY_WARNING", "200"))  # MB
    MEMORY_CRITICAL_THRESHOLD = int(os.getenv("MINICRM_MEMORY_CRITICAL", "400"))  # MB
    AUTO_GC_THRESHOLD = int(
        os.getenv("MINICRM_AUTO_GC_THRESHOLD", "100")
    )  # MB增长触发GC

    # 性能监控配置
    ENABLE_PROFILING = os.getenv("MINICRM_ENABLE_PROFILING", "false").lower() == "true"
    PROFILE_SLOW_QUERIES = (
        os.getenv("MINICRM_PROFILE_SLOW_QUERIES", "true").lower() == "true"
    )
    SLOW_QUERY_THRESHOLD = float(
        os.getenv("MINICRM_SLOW_QUERY_THRESHOLD", "0.5")
    )  # seconds
    PERFORMANCE_LOG_LEVEL = os.getenv("MINICRM_PERF_LOG_LEVEL", "INFO")

    # 文件处理配置
    MAX_FILE_SIZE_MB = int(os.getenv("MINICRM_MAX_FILE_SIZE", "50"))  # MB
    CHUNK_SIZE_KB = int(os.getenv("MINICRM_CHUNK_SIZE", "1024"))  # KB

    # 并发配置
    MAX_CONCURRENT_OPERATIONS = int(os.getenv("MINICRM_MAX_CONCURRENT_OPS", "10"))
    BACKGROUND_TASK_TIMEOUT = int(os.getenv("MINICRM_BG_TASK_TIMEOUT", "60"))  # seconds

    @classmethod
    def get_config_dict(cls) -> dict[str, Any]:
        """获取所有配置的字典形式"""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("_") and not callable(getattr(cls, attr))
        }

    @classmethod
    def print_config(cls) -> None:
        """打印当前配置"""
        print("=== MiniCRM 性能配置 ===")
        config = cls.get_config_dict()

        categories = {
            "DB_": "数据库配置",
            "UI_": "UI配置",
            "CACHE_": "缓存配置",
            "MEMORY_": "内存配置",
            "ENABLE_": "功能开关",
            "MAX_": "限制配置",
        }

        for prefix, category in categories.items():
            print(f"\n{category}:")
            for key, value in config.items():
                if key.startswith(prefix):
                    print(f"  {key}: {value}")

    @classmethod
    def validate_config(cls) -> dict[str, str]:
        """验证配置的合理性"""
        issues = []

        # 检查内存配置
        if cls.MEMORY_WARNING_THRESHOLD >= cls.MEMORY_CRITICAL_THRESHOLD:
            issues.append("内存警告阈值应小于临界阈值")

        # 检查数据库配置
        if cls.DB_CONNECTION_POOL_SIZE < 1:
            issues.append("数据库连接池大小至少为1")

        if cls.DB_BATCH_SIZE < 100:
            issues.append("数据库批量大小建议至少100")

        # 检查UI配置
        if cls.UI_UPDATE_INTERVAL < 16:  # 60 FPS
            issues.append("UI更新间隔过小可能影响性能")

        # 检查缓存配置
        if cls.CACHE_SIZE < 10:
            issues.append("缓存大小过小可能影响性能")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }


# 开发环境配置
class DevelopmentPerformanceConfig(PerformanceConfig):
    """开发环境性能配置"""

    ENABLE_PROFILING = True
    MEMORY_WARNING_THRESHOLD = 100  # MB，开发时更严格
    CACHE_TTL = 60  # 更短的缓存时间便于测试
    PERFORMANCE_LOG_LEVEL = "DEBUG"


# 生产环境配置
class ProductionPerformanceConfig(PerformanceConfig):
    """生产环境性能配置"""

    ENABLE_PROFILING = False
    DB_CONNECTION_POOL_SIZE = 10  # 更大的连接池
    CACHE_SIZE = 256  # 更大的缓存
    MEMORY_WARNING_THRESHOLD = 300  # MB
    MEMORY_CRITICAL_THRESHOLD = 500  # MB


# 根据环境选择配置
def get_performance_config():
    """根据环境变量选择性能配置"""
    env = os.getenv("MINICRM_ENV", "development").lower()

    if env == "production":
        return ProductionPerformanceConfig
    if env == "development":
        return DevelopmentPerformanceConfig
    return PerformanceConfig


# 当前使用的配置
current_config = get_performance_config()


if __name__ == "__main__":
    # 配置验证和打印
    config = get_performance_config()
    config.print_config()

    print("\n=== 配置验证 ===")
    validation = config.validate_config()
    if validation["valid"]:
        print("✅ 配置验证通过")
    else:
        print("❌ 配置存在问题:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
