"""MiniCRM TTK页面配置系统

为任务8提供统一的页面配置管理:
- 配置所有TTK面板的页面管理策略
- 定义缓存、懒加载和切换策略
- 提供性能优化配置
- 支持动态配置调整

设计特点:
1. 配置驱动 - 通过配置文件管理所有页面策略
2. 分层配置 - 全局配置、页面类型配置、单页面配置
3. 动态调整 - 运行时可调整配置参数
4. 性能优化 - 针对不同页面类型的优化策略
5. 监控集成 - 配置与性能监控的集成

作者: MiniCRM开发团队
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from minicrm.core.exceptions import ConfigurationError
from minicrm.ui.ttk_base.enhanced_page_manager import (
    CacheStrategy,
    LoadingStrategy,
    PageCacheConfig,
    PageLoadConfig,
    PageTransitionConfig,
)


@dataclass
class PageTypeConfig:
    """页面类型配置"""

    # 基础配置
    cache_enabled: bool = True
    preload_enabled: bool = False
    preload_priority: int = 0

    # 缓存配置
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    cache_ttl_seconds: float = 300.0
    max_cache_size: int = 5

    # 加载配置
    loading_strategy: LoadingStrategy = LoadingStrategy.LAZY
    preload_delay: float = 0.1
    timeout_seconds: float = 10.0

    # 切换配置
    transition_enabled: bool = True
    transition_duration_ms: int = 200
    fade_effect: bool = True

    # 性能配置
    memory_threshold_mb: float = 50.0
    load_time_warning_seconds: float = 2.0
    show_time_warning_seconds: float = 0.5


@dataclass
class GlobalPageConfig:
    """全局页面配置"""

    # 全局缓存配置
    global_cache_enabled: bool = True
    global_max_cache_size: int = 20
    global_cache_strategy: CacheStrategy = CacheStrategy.LRU
    global_cache_ttl: float = 600.0  # 10分钟
    memory_threshold_mb: float = 200.0

    # 全局加载配置
    preload_enabled: bool = True
    background_loading: bool = True
    max_concurrent_loads: int = 3

    # 全局切换配置
    transitions_enabled: bool = True
    default_transition_duration: int = 200
    loading_indicator_enabled: bool = True

    # 性能监控配置
    performance_monitoring: bool = True
    memory_check_interval: float = 30.0
    performance_logging: bool = True

    # 清理配置
    auto_cleanup: bool = True
    cleanup_interval: float = 60.0
    idle_cleanup_threshold: float = 1800.0  # 30分钟


class PageConfigurationManager:
    """页面配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        """初始化配置管理器

        Args:
            config_file: 配置文件路径
        """
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

        # 配置文件路径
        self.config_file = config_file or "config/page_config.json"

        # 全局配置
        self.global_config = GlobalPageConfig()

        # 页面类型配置
        self.page_type_configs: Dict[str, PageTypeConfig] = {}

        # 单页面配置
        self.page_configs: Dict[str, PageTypeConfig] = {}

        # 初始化默认配置
        self._initialize_default_configs()

        # 加载配置文件
        self._load_config_file()

        self.logger.debug("页面配置管理器初始化完成")

    def _initialize_default_configs(self) -> None:
        """初始化默认配置"""
        try:
            # 仪表盘页面配置 - 高优先级预加载
            self.page_type_configs["dashboard"] = PageTypeConfig(
                cache_enabled=True,
                preload_enabled=True,
                preload_priority=10,
                cache_strategy=CacheStrategy.LRU,
                cache_ttl_seconds=600.0,  # 10分钟
                max_cache_size=1,  # 只缓存一个仪表盘
                loading_strategy=LoadingStrategy.PRELOAD,
                preload_delay=0.0,  # 立即预加载
                timeout_seconds=15.0,  # 仪表盘可能需要更长加载时间
                transition_enabled=True,
                transition_duration_ms=300,
                fade_effect=True,
                memory_threshold_mb=80.0,  # 仪表盘可能占用更多内存
                load_time_warning_seconds=3.0,
                show_time_warning_seconds=0.8,
            )

            # 业务管理页面配置 - 中等优先级
            business_config = PageTypeConfig(
                cache_enabled=True,
                preload_enabled=True,
                preload_priority=5,
                cache_strategy=CacheStrategy.LRU,
                cache_ttl_seconds=300.0,  # 5分钟
                max_cache_size=3,  # 缓存3个业务页面
                loading_strategy=LoadingStrategy.LAZY,
                preload_delay=0.2,
                timeout_seconds=10.0,
                transition_enabled=True,
                transition_duration_ms=200,
                fade_effect=True,
                memory_threshold_mb=60.0,
                load_time_warning_seconds=2.0,
                show_time_warning_seconds=0.5,
            )

            # 应用到所有业务页面
            for page_type in [
                "customers",
                "suppliers",
                "finance",
                "contracts",
                "quotes",
                "tasks",
            ]:
                self.page_type_configs[page_type] = business_config

            # 数据管理页面配置 - 不缓存,按需加载
            self.page_type_configs["import_export"] = PageTypeConfig(
                cache_enabled=False,  # 数据导入导出不需要缓存
                preload_enabled=False,
                preload_priority=0,
                cache_strategy=CacheStrategy.LRU,
                cache_ttl_seconds=0.0,
                max_cache_size=0,
                loading_strategy=LoadingStrategy.ON_DEMAND,
                preload_delay=0.0,
                timeout_seconds=8.0,
                transition_enabled=True,
                transition_duration_ms=150,
                fade_effect=False,  # 快速切换
                memory_threshold_mb=40.0,
                load_time_warning_seconds=1.5,
                show_time_warning_seconds=0.3,
            )

            # 设置页面配置 - 低优先级,不缓存
            self.page_type_configs["settings"] = PageTypeConfig(
                cache_enabled=False,  # 设置页面不需要缓存
                preload_enabled=False,
                preload_priority=0,
                cache_strategy=CacheStrategy.LRU,
                cache_ttl_seconds=0.0,
                max_cache_size=0,
                loading_strategy=LoadingStrategy.ON_DEMAND,
                preload_delay=0.0,
                timeout_seconds=5.0,
                transition_enabled=True,
                transition_duration_ms=150,
                fade_effect=False,
                memory_threshold_mb=30.0,
                load_time_warning_seconds=1.0,
                show_time_warning_seconds=0.3,
            )

            self.logger.debug("默认页面配置初始化完成")

        except Exception as e:
            self.logger.error(f"默认配置初始化失败: {e}")
            raise ConfigurationError(f"默认配置初始化失败: {e}")

    def _load_config_file(self) -> None:
        """加载配置文件"""
        try:
            config_path = Path(self.config_file)

            if not config_path.exists():
                self.logger.info(f"配置文件不存在,使用默认配置: {self.config_file}")
                return

            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            # 加载全局配置
            if "global" in config_data:
                self._load_global_config(config_data["global"])

            # 加载页面类型配置
            if "page_types" in config_data:
                self._load_page_type_configs(config_data["page_types"])

            # 加载单页面配置
            if "pages" in config_data:
                self._load_page_configs(config_data["pages"])

            self.logger.info(f"配置文件加载完成: {self.config_file}")

        except Exception as e:
            self.logger.error(f"配置文件加载失败: {e}")
            # 不抛出异常,使用默认配置

    def _load_global_config(self, config_data: Dict[str, Any]) -> None:
        """加载全局配置"""
        try:
            # 更新全局配置
            for key, value in config_data.items():
                if hasattr(self.global_config, key):
                    # 处理枚举类型
                    if key == "global_cache_strategy":
                        value = CacheStrategy(value)

                    setattr(self.global_config, key, value)

            self.logger.debug("全局配置加载完成")

        except Exception as e:
            self.logger.error(f"全局配置加载失败: {e}")

    def _load_page_type_configs(self, config_data: Dict[str, Any]) -> None:
        """加载页面类型配置"""
        try:
            for page_type, type_config in config_data.items():
                config = PageTypeConfig()

                # 更新配置
                for key, value in type_config.items():
                    if hasattr(config, key):
                        # 处理枚举类型
                        if key == "cache_strategy":
                            value = CacheStrategy(value)
                        elif key == "loading_strategy":
                            value = LoadingStrategy(value)

                        setattr(config, key, value)

                self.page_type_configs[page_type] = config

            self.logger.debug(f"页面类型配置加载完成: {len(config_data)} 个类型")

        except Exception as e:
            self.logger.error(f"页面类型配置加载失败: {e}")

    def _load_page_configs(self, config_data: Dict[str, Any]) -> None:
        """加载单页面配置"""
        try:
            for page_id, page_config in config_data.items():
                config = PageTypeConfig()

                # 更新配置
                for key, value in page_config.items():
                    if hasattr(config, key):
                        # 处理枚举类型
                        if key == "cache_strategy":
                            value = CacheStrategy(value)
                        elif key == "loading_strategy":
                            value = LoadingStrategy(value)

                        setattr(config, key, value)

                self.page_configs[page_id] = config

            self.logger.debug(f"单页面配置加载完成: {len(config_data)} 个页面")

        except Exception as e:
            self.logger.error(f"单页面配置加载失败: {e}")

    def get_page_config(
        self, page_id: str, page_type: Optional[str] = None
    ) -> PageTypeConfig:
        """获取页面配置

        Args:
            page_id: 页面ID
            page_type: 页面类型

        Returns:
            页面配置
        """
        # 优先级:单页面配置 > 页面类型配置 > 默认配置
        if page_id in self.page_configs:
            return self.page_configs[page_id]

        if page_type and page_type in self.page_type_configs:
            return self.page_type_configs[page_type]

        # 返回默认配置
        return PageTypeConfig()

    def get_cache_config(
        self, page_id: str, page_type: Optional[str] = None
    ) -> PageCacheConfig:
        """获取页面缓存配置

        Args:
            page_id: 页面ID
            page_type: 页面类型

        Returns:
            缓存配置
        """
        page_config = self.get_page_config(page_id, page_type)

        return PageCacheConfig(
            enabled=page_config.cache_enabled
            and self.global_config.global_cache_enabled,
            strategy=page_config.cache_strategy,
            max_size=min(
                page_config.max_cache_size, self.global_config.global_max_cache_size
            ),
            ttl_seconds=page_config.cache_ttl_seconds,
            memory_threshold_mb=page_config.memory_threshold_mb,
            auto_cleanup=self.global_config.auto_cleanup,
            cleanup_interval=self.global_config.cleanup_interval,
        )

    def get_load_config(
        self, page_id: str, page_type: Optional[str] = None
    ) -> PageLoadConfig:
        """获取页面加载配置

        Args:
            page_id: 页面ID
            page_type: 页面类型

        Returns:
            加载配置
        """
        page_config = self.get_page_config(page_id, page_type)

        return PageLoadConfig(
            strategy=page_config.loading_strategy,
            preload_priority=page_config.preload_priority,
            preload_delay=page_config.preload_delay,
            timeout_seconds=page_config.timeout_seconds,
            retry_count=3,  # 固定重试次数
            background_load=self.global_config.background_loading,
        )

    def get_transition_config(
        self, page_id: str, page_type: Optional[str] = None
    ) -> PageTransitionConfig:
        """获取页面切换配置

        Args:
            page_id: 页面ID
            page_type: 页面类型

        Returns:
            切换配置
        """
        page_config = self.get_page_config(page_id, page_type)

        return PageTransitionConfig(
            enabled=page_config.transition_enabled
            and self.global_config.transitions_enabled,
            duration_ms=page_config.transition_duration_ms,
            fade_effect=page_config.fade_effect,
            loading_indicator=self.global_config.loading_indicator_enabled,
            smooth_scroll=True,  # 默认启用平滑滚动
        )

    def get_global_config(self) -> GlobalPageConfig:
        """获取全局配置

        Returns:
            全局配置
        """
        return self.global_config

    def update_page_config(self, page_id: str, config_updates: Dict[str, Any]) -> bool:
        """更新页面配置

        Args:
            page_id: 页面ID
            config_updates: 配置更新

        Returns:
            是否更新成功
        """
        try:
            # 获取当前配置
            if page_id not in self.page_configs:
                self.page_configs[page_id] = PageTypeConfig()

            config = self.page_configs[page_id]

            # 更新配置
            for key, value in config_updates.items():
                if hasattr(config, key):
                    # 处理枚举类型
                    if key == "cache_strategy" and isinstance(value, str):
                        value = CacheStrategy(value)
                    elif key == "loading_strategy" and isinstance(value, str):
                        value = LoadingStrategy(value)

                    setattr(config, key, value)

            self.logger.debug(f"页面配置更新成功: {page_id}")
            return True

        except Exception as e:
            self.logger.error(f"页面配置更新失败 [{page_id}]: {e}")
            return False

    def update_global_config(self, config_updates: Dict[str, Any]) -> bool:
        """更新全局配置

        Args:
            config_updates: 配置更新

        Returns:
            是否更新成功
        """
        try:
            # 更新全局配置
            for key, value in config_updates.items():
                if hasattr(self.global_config, key):
                    # 处理枚举类型
                    if key == "global_cache_strategy" and isinstance(value, str):
                        value = CacheStrategy(value)

                    setattr(self.global_config, key, value)

            self.logger.debug("全局配置更新成功")
            return True

        except Exception as e:
            self.logger.error(f"全局配置更新失败: {e}")
            return False

    def save_config_file(self) -> bool:
        """保存配置到文件

        Returns:
            是否保存成功
        """
        try:
            config_data = {
                "global": asdict(self.global_config),
                "page_types": {},
                "pages": {},
            }

            # 转换页面类型配置
            for page_type, config in self.page_type_configs.items():
                config_dict = asdict(config)
                # 转换枚举为字符串
                config_dict["cache_strategy"] = config.cache_strategy.value
                config_dict["loading_strategy"] = config.loading_strategy.value
                config_data["page_types"][page_type] = config_dict

            # 转换单页面配置
            for page_id, config in self.page_configs.items():
                config_dict = asdict(config)
                # 转换枚举为字符串
                config_dict["cache_strategy"] = config.cache_strategy.value
                config_dict["loading_strategy"] = config.loading_strategy.value
                config_data["pages"][page_id] = config_dict

            # 转换全局配置中的枚举
            config_data["global"]["global_cache_strategy"] = (
                self.global_config.global_cache_strategy.value
            )

            # 确保目录存在
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存文件
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"配置文件保存成功: {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"配置文件保存失败: {e}")
            return False

    def get_preload_pages(self) -> List[tuple[str, int]]:
        """获取需要预加载的页面列表

        Returns:
            预加载页面列表 [(page_id, priority), ...]
        """
        preload_pages = []

        # 检查页面类型配置
        for page_type, config in self.page_type_configs.items():
            if config.preload_enabled and self.global_config.preload_enabled:
                preload_pages.append((page_type, config.preload_priority))

        # 检查单页面配置
        for page_id, config in self.page_configs.items():
            if config.preload_enabled and self.global_config.preload_enabled:
                preload_pages.append((page_id, config.preload_priority))

        # 按优先级排序
        preload_pages.sort(key=lambda x: x[1], reverse=True)

        return preload_pages

    def get_configuration_summary(self) -> Dict[str, Any]:
        """获取配置摘要

        Returns:
            配置摘要字典
        """
        return {
            "global_config": {
                "cache_enabled": self.global_config.global_cache_enabled,
                "max_cache_size": self.global_config.global_max_cache_size,
                "cache_strategy": self.global_config.global_cache_strategy.value,
                "preload_enabled": self.global_config.preload_enabled,
                "transitions_enabled": self.global_config.transitions_enabled,
                "performance_monitoring": self.global_config.performance_monitoring,
            },
            "page_type_count": len(self.page_type_configs),
            "page_config_count": len(self.page_configs),
            "preload_pages": len(self.get_preload_pages()),
            "page_types": list(self.page_type_configs.keys()),
            "configured_pages": list(self.page_configs.keys()),
        }


# 全局配置管理器实例
_config_manager: Optional[PageConfigurationManager] = None


def get_page_config_manager() -> PageConfigurationManager:
    """获取全局页面配置管理器实例

    Returns:
        配置管理器实例
    """
    global _config_manager

    if _config_manager is None:
        _config_manager = PageConfigurationManager()

    return _config_manager


def initialize_page_config(
    config_file: Optional[str] = None,
) -> PageConfigurationManager:
    """初始化页面配置管理器

    Args:
        config_file: 配置文件路径

    Returns:
        配置管理器实例
    """
    global _config_manager

    _config_manager = PageConfigurationManager(config_file)
    return _config_manager
