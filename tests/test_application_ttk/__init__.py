"""
MiniCRM TTK应用程序测试包

包含MiniCRMApplicationTTK类的完整测试套件，包括：
- 单元测试
- 集成测试
- 性能测试
- 错误处理测试

作者: MiniCRM开发团队
"""

from .test_minicrm_application_ttk import (
    TestMiniCRMApplicationTTK,
    TestMiniCRMApplicationTTKIntegration,
)


__all__ = [
    "TestMiniCRMApplicationTTK",
    "TestMiniCRMApplicationTTKIntegration",
]
