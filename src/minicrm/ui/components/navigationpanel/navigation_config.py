"""
MiniCRM 导航面板配置

定义导航结构和默认配置数据
"""

from .navigation_types import NavigationItem


class NavigationConfig:
    """导航配置管理器"""

    @staticmethod
    def get_default_navigation_items() -> list[NavigationItem]:
        """获取默认导航项配置"""
        return [
            NavigationItem(
                name="dashboard",
                display_name="📊 数据仪表盘",
                page_name="dashboard",
            ),
            NavigationItem(
                name="customers",
                display_name="👥 客户管理",
                children=[
                    NavigationItem(
                        name="customer_list",
                        display_name="客户列表",
                        parent="customers",
                        page_name="customer_list",
                    ),
                    NavigationItem(
                        name="customer_types",
                        display_name="客户类型",
                        parent="customers",
                        page_name="customer_types",
                    ),
                    NavigationItem(
                        name="customer_interactions",
                        display_name="互动记录",
                        parent="customers",
                        page_name="customer_interactions",
                    ),
                ],
            ),
            NavigationItem(
                name="suppliers",
                display_name="🏭 供应商管理",
                children=[
                    NavigationItem(
                        name="supplier_list",
                        display_name="供应商列表",
                        parent="suppliers",
                        page_name="supplier_list",
                    ),
                    NavigationItem(
                        name="supplier_quotes",
                        display_name="供应商报价",
                        parent="suppliers",
                        page_name="supplier_quotes",
                    ),
                    NavigationItem(
                        name="supplier_quality",
                        display_name="质量跟踪",
                        parent="suppliers",
                        page_name="supplier_quality",
                    ),
                ],
            ),
            NavigationItem(
                name="business",
                display_name="💼 业务管理",
                children=[
                    NavigationItem(
                        name="quotes",
                        display_name="报价管理",
                        parent="business",
                        page_name="quotes",
                    ),
                    NavigationItem(
                        name="contracts",
                        display_name="合同管理",
                        parent="business",
                        page_name="contracts",
                    ),
                    NavigationItem(
                        name="service_tickets",
                        display_name="售后工单",
                        parent="business",
                        page_name="service_tickets",
                    ),
                ],
            ),
            NavigationItem(
                name="finance",
                display_name="💰 财务管理",
                children=[
                    NavigationItem(
                        name="receivables",
                        display_name="应收账款",
                        parent="finance",
                        page_name="receivables",
                    ),
                    NavigationItem(
                        name="payables",
                        display_name="应付账款",
                        parent="finance",
                        page_name="payables",
                    ),
                    NavigationItem(
                        name="financial_reports",
                        display_name="财务报表",
                        parent="finance",
                        page_name="financial_reports",
                    ),
                ],
            ),
            NavigationItem(
                name="reports",
                display_name="📊 报表分析",
                children=[
                    NavigationItem(
                        name="customer_reports",
                        display_name="客户分析",
                        parent="reports",
                        page_name="customer_reports",
                    ),
                    NavigationItem(
                        name="sales_reports",
                        display_name="销售分析",
                        parent="reports",
                        page_name="sales_reports",
                    ),
                    NavigationItem(
                        name="supplier_reports",
                        display_name="供应商分析",
                        parent="reports",
                        page_name="supplier_reports",
                    ),
                ],
            ),
            NavigationItem(
                name="settings",
                display_name="⚙️ 系统设置",
                children=[
                    NavigationItem(
                        name="general_settings",
                        display_name="常规设置",
                        parent="settings",
                        page_name="general_settings",
                    ),
                    NavigationItem(
                        name="database_settings",
                        display_name="数据库设置",
                        parent="settings",
                        page_name="database_settings",
                    ),
                    NavigationItem(
                        name="backup_settings",
                        display_name="备份设置",
                        parent="settings",
                        page_name="backup_settings",
                    ),
                ],
            ),
        ]
