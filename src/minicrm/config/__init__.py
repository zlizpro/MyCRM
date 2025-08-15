"""MiniCRM 配置模块"""

from .performance_config import (
    DevelopmentPerformanceConfig,
    PerformanceConfig,
    ProductionPerformanceConfig,
    current_config,
    get_performance_config,
)

__all__ = [
    "DevelopmentPerformanceConfig",
    "PerformanceConfig",
    "ProductionPerformanceConfig",
    "current_config",
    "get_performance_config",
]
