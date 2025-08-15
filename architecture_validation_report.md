# MiniCRM 架构验证报告

生成时间: 2025-08-13 12:17:55

## ❌ 架构错误

- ❌ 依赖方向错误: src/minicrm/ui/main_window.py 不应该导入 minicrm.ui.components.dashboard
- ❌ 依赖方向错误: src/minicrm/ui/main_window.py 不应该导入 minicrm.ui.components.navigation_panel
- ❌ 依赖方向错误: src/minicrm/ui/main_window.py 不应该导入 minicrm.ui.themes.theme_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/form_data_binder.py 不应该导入 minicrm.ui.components.form_field_factory
- ❌ 依赖方向错误: src/minicrm/ui/components/search_history_manager.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/search_filter_manager.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard_refactored.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard_refactored.py 不应该导入 minicrm.ui.components.chart_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard_refactored.py 不应该导入 minicrm.ui.components.loading_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard_refactored.py 不应该导入 minicrm.ui.components.metric_card
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_core.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_core.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_core.py 不应该导入 minicrm.ui.components.search_filter_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_core.py 不应该导入 minicrm.ui.components.search_history_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_core.py 不应该导入 minicrm.ui.components.search_styles
- ❌ 依赖方向错误: src/minicrm/ui/components/form_panel_core.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/form_panel_core.py 不应该导入 minicrm.ui.components.form_data_binder
- ❌ 依赖方向错误: src/minicrm/ui/components/form_panel_core.py 不应该导入 minicrm.ui.components.form_field_factory
- ❌ 依赖方向错误: src/minicrm/ui/components/form_panel_core.py 不应该导入 minicrm.ui.components.form_validator
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_simplified.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_simplified.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_simplified.py 不应该导入 minicrm.ui.components.search_filter_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_simplified.py 不应该导入 minicrm.ui.components.search_history_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_old.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_old.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_old.py 不应该导入 minicrm.ui.components.search_filter_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_old.py 不应该导入 minicrm.ui.components.search_history_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar_old.py 不应该导入 minicrm.ui.components.search_styles
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard.py 不应该导入 minicrm.ui.components.chart_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/dashboard.py 不应该导入 minicrm.ui.components.metric_card
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar.py 不应该导入 minicrm.ui.components.search_config
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar.py 不应该导入 minicrm.ui.components.search_filter_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar.py 不应该导入 minicrm.ui.components.search_history_manager
- ❌ 依赖方向错误: src/minicrm/ui/components/search_bar.py 不应该导入 minicrm.ui.components.search_styles
- ❌ 依赖方向错误: src/minicrm/ui/components/table/data_table.py 不应该导入 minicrm.ui.components.base_widget
- ❌ 依赖方向错误: src/minicrm/data/dao/base_dao.py 不应该导入 minicrm.data.database
- ❌ 依赖方向错误: src/minicrm/data/dao/supplier_dao.py 不应该导入 minicrm.data.database
- ❌ 依赖方向错误: src/minicrm/data/dao/customer_dao.py 不应该导入 minicrm.data.database
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.core.exceptions
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.core.interfaces.dao_interfaces
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.core.interfaces.service_interfaces
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.data.dao.customer_dao
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.data.dao.supplier_dao
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.data.database
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.services.analytics_service
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.services.customer_service
- ❌ 依赖方向错误: src/minicrm/core/dependency_injection.py 不应该导入 minicrm.services.supplier_service

## ⚠️ 架构警告

- ⚠️ 可能违反单一职责原则: src/minicrm/ui/main_window.py 中的类 MainWindow 有 29 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/base_widget.py 中的类 BaseWidget 有 20 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/base_panel.py 中的类 BasePanel 有 27 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/base_widget.py 中的类 BaseWidget 有 24 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/form_validator.py 中的类 FormValidator 有 26 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/base_dialog.py 中的类 BaseDialog 有 29 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/search_filter_manager.py 中的类 SearchFilterManager 有 20 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/dashboard_refactored.py 中的类 Dashboard 有 24 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/search_bar_core.py 中的类 SearchBar 有 23 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/form_panel_core.py 中的类 FormPanelCore 有 19 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/search_bar_simplified.py 中的类 SearchBar 有 20 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/table_filter_manager.py 中的类 TableFilterManager 有 24 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/notification_widget.py 中的类 NotificationWidget 有 17 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/search_bar_old.py 中的类 SearchBar 有 25 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/table_pagination_manager.py 中的类 TablePaginationManager 有 26 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/dashboard.py 中的类 Dashboard 有 22 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/pagination_widget.py 中的类 PaginationWidget 有 25 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/table_data_manager.py 中的类 TableDataManager 有 26 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/metric_card.py 中的类 MetricCard 有 24 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/chart_widget.py 中的类 ChartWidget 有 24 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/search_widget.py 中的类 SearchWidget 有 28 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/table/data_table.py 中的类 DataTable 有 25 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/ui/components/table/table_data_manager.py 中的类 TableDataManager 有 16 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/services/analytics_service.py 中的类 AnalyticsService 有 21 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/data/database.py 中的类 DatabaseManager 有 16 个方法
- ⚠️ 可能违反单一职责原则: src/minicrm/core/config.py 中的类 AppConfig 有 24 个方法
- ⚠️ 建议使用接口: src/minicrm/services/base_service.py 应该实现相应的接口
- ⚠️ 文件过大: src/minicrm/ui/main_window.py 有 528 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/base_widget.py 有 430 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/base_panel.py 有 552 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/form_validator.py 有 402 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/loading_widget.py 有 471 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/base_dialog.py 有 502 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/dashboard_refactored.py 有 463 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/table_filter_manager.py 有 466 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/notification_widget.py 有 626 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/table_pagination_manager.py 有 471 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/dashboard.py 有 528 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/pagination_widget.py 有 652 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/navigation_panel.py 有 587 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/table_data_manager.py 有 448 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/metric_card.py 有 479 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/chart_widget.py 有 641 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/ui/components/search_widget.py 有 658 行，建议不超过 400 行
- ⚠️ 文件过大: src/minicrm/services/base_service.py 有 496 行，建议不超过 300 行
- ⚠️ 文件过大: src/minicrm/services/analytics_service.py 有 351 行，建议不超过 300 行
- ⚠️ 文件过大: src/minicrm/data/database.py 有 399 行，建议不超过 250 行
- ⚠️ 文件过大: src/minicrm/data/dao/supplier_dao.py 有 273 行，建议不超过 250 行
- ⚠️ 文件过大: src/minicrm/data/dao/customer_dao.py 有 382 行，建议不超过 250 行
- ⚠️ 文件过大: src/minicrm/models/enums.py 有 230 行，建议不超过 200 行
- ⚠️ 文件过大: src/minicrm/models/base.py 有 369 行，建议不超过 200 行
- ⚠️ 文件过大: src/minicrm/core/constants.py 有 359 行，建议不超过 300 行
- ⚠️ 文件过大: src/minicrm/core/utils.py 有 360 行，建议不超过 300 行
- ⚠️ 文件过大: src/minicrm/core/architecture_validator.py 有 391 行，建议不超过 300 行

## 📊 验证总结

- 错误数量: 48
- 警告数量: 54
- 信息数量: 0

❌ **架构验证失败！请修复上述错误。**