"""Transfunctions - 报表模板

提供统一的报表生成功能,包括仪表盘数据生成、客户报表、供应商报表等.
"""

from datetime import datetime
import logging
from typing import Any, Dict, List

from .calculations import calculate_customer_value_score, calculate_growth_rate
from .formatting import format_currency, format_date


# 配置日志
logger = logging.getLogger(__name__)


class ReportError(Exception):
    """报表生成异常类"""

    def __init__(self, message: str, context=None):
        """初始化报表异常

        Args:
            message: 错误消息
            context: 错误上下文信息
        """
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


def generate_dashboard_summary(
    customer_dao, supplier_dao, analytics_service=None, include_charts: bool = True
) -> Dict[str, Any]:
    """生成仪表盘摘要数据

    使用transfunctions统一生成仪表盘所需的所有数据,包括关键指标、
    图表数据和系统预警信息.

    Args:
        customer_dao: 客户数据访问对象
        supplier_dao: 供应商数据访问对象
        analytics_service: 分析服务实例(可选)
        include_charts: 是否包含图表数据

    Returns:
        Dict[str, Any]: 仪表盘摘要数据

    Raises:
        ReportError: 当数据生成失败时

    Example:
        >>> from minicrm.data.dao.customer_dao import CustomerDAO
        >>> from minicrm.data.dao.supplier_dao import SupplierDAO
        >>> customer_dao = CustomerDAO(db_manager)
        >>> supplier_dao = SupplierDAO(db_manager)
        >>> summary = generate_dashboard_summary(customer_dao, supplier_dao)
        >>> print(f"客户总数: {summary['metrics'][0]['value']}")
    """
    try:
        logger.info("开始生成仪表盘摘要数据")

        # 获取基础统计数据
        customer_stats = _get_customer_statistics(customer_dao)
        supplier_stats = _get_supplier_statistics(supplier_dao)
        financial_stats = _get_financial_statistics(customer_dao, supplier_dao)

        # 生成关键指标
        metrics = _generate_key_metrics(customer_stats, supplier_stats, financial_stats)

        # 生成图表数据(如果需要)
        charts = {}
        if include_charts:
            charts = _generate_chart_data(customer_dao, supplier_dao)

        # 生成快速操作
        quick_actions = _generate_quick_actions()

        # 生成系统预警
        alerts = _generate_system_alerts(customer_stats, financial_stats)

        # 构建完整的仪表盘数据
        dashboard_summary = {
            "metrics": metrics,
            "charts": charts,
            "quick_actions": quick_actions,
            "alerts": alerts,
            "generated_at": format_date(datetime.now(), "chinese_datetime"),
            "cache_expires_at": format_date(
                datetime.now().replace(minute=datetime.now().minute + 5),
                "chinese_datetime",
            ),
            "summary_stats": {
                "total_customers": customer_stats.get("total_customers", 0),
                "total_suppliers": supplier_stats.get("total_suppliers", 0),
                "total_receivables": financial_stats.get("total_receivables", 0),
                "total_payables": financial_stats.get("total_payables", 0),
            },
        }

        logger.info("仪表盘摘要数据生成完成")
        return dashboard_summary

    except Exception as e:
        logger.error(f"生成仪表盘摘要数据失败: {e}")
        raise ReportError(
            f"生成仪表盘摘要数据失败: {e}", {"include_charts": include_charts}
        ) from e


def _get_customer_statistics(customer_dao) -> Dict[str, Any]:
    """获取客户统计数据"""
    try:
        # 获取基础统计
        total_customers = customer_dao.count()

        # 获取本月新增客户数
        from datetime import datetime, timedelta

        start_of_month = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        new_this_month = customer_dao.count_by_date_range(
            start_of_month, datetime.now()
        )

        # 计算增长率
        last_month_start = (start_of_month - timedelta(days=1)).replace(day=1)
        last_month_end = start_of_month - timedelta(days=1)
        last_month_count = customer_dao.count_by_date_range(
            last_month_start, last_month_end
        )

        growth_rate = calculate_growth_rate(new_this_month, last_month_count)

        # 获取活跃客户数(最近30天有互动的客户)
        active_customers = customer_dao.count_active_customers(30)

        return {
            "total_customers": total_customers,
            "new_this_month": new_this_month,
            "growth_rate": growth_rate,
            "active_customers": active_customers,
        }
    except Exception as e:
        logger.warning(f"获取客户统计数据失败: {e}")
        return {
            "total_customers": 0,
            "new_this_month": 0,
            "growth_rate": 0,
            "active_customers": 0,
        }


def _get_supplier_statistics(supplier_dao) -> Dict[str, Any]:
    """获取供应商统计数据"""
    try:
        total_suppliers = supplier_dao.count()
        active_suppliers = supplier_dao.count_active_suppliers(30)

        return {
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
        }
    except Exception as e:
        logger.warning(f"获取供应商统计数据失败: {e}")
        return {
            "total_suppliers": 0,
            "active_suppliers": 0,
        }


def _get_financial_statistics(customer_dao, supplier_dao) -> Dict[str, Any]:
    """获取财务统计数据"""
    try:
        # 这里应该从财务相关的DAO获取数据
        # 暂时使用模拟数据
        return {
            "total_receivables": 502000.0,
            "total_payables": 321000.0,
            "overdue_receivables": 3,
            "pending_payments": 5,
        }
    except Exception as e:
        logger.warning(f"获取财务统计数据失败: {e}")
        return {
            "total_receivables": 0.0,
            "total_payables": 0.0,
            "overdue_receivables": 0,
            "pending_payments": 0,
        }


def _generate_key_metrics(
    customer_stats: Dict[str, Any],
    supplier_stats: Dict[str, Any],
    financial_stats: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """生成关键指标卡片数据"""
    metrics = []

    # 客户总数
    total_customers = customer_stats.get("total_customers", 0)
    customer_growth = customer_stats.get("growth_rate", 0)
    metrics.append(
        {
            "title": "客户总数",
            "value": total_customers,
            "unit": "个",
            "trend": "up"
            if customer_growth > 0
            else "down"
            if customer_growth < 0
            else "stable",
            "trend_value": customer_growth,
            "color": "primary",
            "icon": "users",
        }
    )

    # 本月新增客户
    new_customers = customer_stats.get("new_this_month", 0)
    metrics.append(
        {
            "title": "本月新增客户",
            "value": new_customers,
            "unit": "个",
            "color": "success" if new_customers > 0 else "warning",
            "icon": "user-plus",
        }
    )

    # 待办任务数(模拟数据)
    pending_tasks = 8
    metrics.append(
        {
            "title": "待办任务",
            "value": pending_tasks,
            "unit": "项",
            "color": "warning" if pending_tasks > 10 else "primary",
            "icon": "clipboard-list",
        }
    )

    # 应收账款
    receivables = financial_stats.get("total_receivables", 0)
    metrics.append(
        {
            "title": "应收账款",
            "value": format_currency(receivables),
            "color": "success" if receivables > 0 else "primary",
            "icon": "dollar-sign",
        }
    )

    # 应付账款
    payables = financial_stats.get("total_payables", 0)
    metrics.append(
        {
            "title": "应付账款",
            "value": format_currency(payables),
            "color": "danger" if payables > receivables else "primary",
            "icon": "credit-card",
        }
    )

    # 供应商总数
    total_suppliers = supplier_stats.get("total_suppliers", 0)
    metrics.append(
        {
            "title": "供应商总数",
            "value": total_suppliers,
            "unit": "个",
            "color": "primary",
            "icon": "building",
        }
    )

    return metrics


def _generate_chart_data(customer_dao, supplier_dao) -> Dict[str, Any]:
    """生成图表数据"""
    charts = {}

    try:
        # 客户增长趋势图数据
        charts["customer_growth_trend"] = _get_customer_growth_trend_data(customer_dao)

        # 客户类型分布饼图数据
        charts["customer_type_distribution"] = _get_customer_type_distribution_data(
            customer_dao
        )

        # 月度互动频率柱状图数据
        charts["monthly_interaction_frequency"] = _get_monthly_interaction_data(
            customer_dao
        )

        # 应收账款状态图数据
        charts["receivables_status"] = _get_receivables_status_data()

    except Exception as e:
        logger.warning(f"生成图表数据失败: {e}")
        charts = {}

    return charts


def _get_customer_growth_trend_data(customer_dao) -> Dict[str, Any]:
    """获取客户增长趋势数据"""
    # 模拟最近6个月的数据
    months = ["7月", "8月", "9月", "10月", "11月", "12月"]
    values = [120, 135, 142, 148, 152, 156]

    return {
        "type": "line",
        "title": "客户增长趋势",
        "labels": months,
        "datasets": [
            {
                "label": "客户总数",
                "data": values,
                "borderColor": "#007BFF",
                "backgroundColor": "rgba(0, 123, 255, 0.1)",
                "tension": 0.4,
            }
        ],
    }


def _get_customer_type_distribution_data(customer_dao) -> Dict[str, Any]:
    """获取客户类型分布数据"""
    # 模拟数据
    return {
        "type": "pie",
        "title": "客户类型分布",
        "labels": ["生态板客户", "家具板客户", "阻燃板客户", "其他"],
        "datasets": [
            {
                "data": [45, 35, 15, 5],
                "backgroundColor": ["#28A745", "#007BFF", "#FFC107", "#6C757D"],
            }
        ],
    }


def _get_monthly_interaction_data(customer_dao) -> Dict[str, Any]:
    """获取月度互动频率数据"""
    # 模拟数据
    months = ["7月", "8月", "9月", "10月", "11月", "12月"]
    values = [85, 92, 78, 105, 98, 112]

    return {
        "type": "bar",
        "title": "月度互动频率",
        "labels": months,
        "datasets": [
            {
                "label": "互动次数",
                "data": values,
                "backgroundColor": "#28A745",
                "borderColor": "#1E7E34",
                "borderWidth": 1,
            }
        ],
    }


def _get_receivables_status_data() -> Dict[str, Any]:
    """获取应收账款状态数据"""
    # 模拟数据
    return {
        "type": "doughnut",
        "title": "应收账款状态",
        "labels": ["正常", "逾期30天内", "逾期30-60天", "逾期60天以上"],
        "datasets": [
            {
                "data": [70, 20, 7, 3],
                "backgroundColor": ["#28A745", "#FFC107", "#FD7E14", "#DC3545"],
            }
        ],
    }


def _generate_quick_actions() -> List[Dict[str, Any]]:
    """生成快速操作按钮配置"""
    return [
        {"title": "新增客户", "icon": "user-plus", "action": "create_customer"},
        {"title": "新增供应商", "icon": "building-plus", "action": "create_supplier"},
        {"title": "创建报价", "icon": "file-text", "action": "create_quote"},
        {"title": "记录收款", "icon": "dollar-sign", "action": "record_payment"},
        {"title": "查看报表", "icon": "bar-chart", "action": "view_reports"},
    ]


def _generate_system_alerts(
    customer_stats: Dict[str, Any], financial_stats: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """生成系统预警信息"""
    alerts = []

    # 检查逾期应收账款
    overdue_receivables = financial_stats.get("overdue_receivables", 0)
    if overdue_receivables > 0:
        alerts.append(
            {
                "type": "warning",
                "title": "逾期应收账款提醒",
                "message": f"有{overdue_receivables}笔应收账款已逾期,请及时跟进",
                "action": "view_overdue_receivables",
                "icon": "alert-triangle",
            }
        )

    # 检查待处理任务
    pending_tasks = 8  # 模拟数据
    if pending_tasks > 20:
        alerts.append(
            {
                "type": "info",
                "title": "待办任务较多",
                "message": f"当前有{pending_tasks}项待办任务,建议优先处理",
                "action": "view_tasks",
                "icon": "info",
            }
        )

    # 检查合同到期
    expiring_contracts = 2  # 模拟数据
    if expiring_contracts > 0:
        alerts.append(
            {
                "type": "warning",
                "title": "合同即将到期",
                "message": f"有{expiring_contracts}个合同即将到期,请及时续约",
                "action": "view_expiring_contracts",
                "icon": "calendar",
            }
        )

    return alerts


def generate_customer_report(
    customers: List[Dict[str, Any]], options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成客户分析报表

    Args:
        customers: 客户数据列表
        options: 报表选项

    Returns:
        Dict[str, Any]: 客户分析报表数据
    """
    options = options or {}

    try:
        # 基础统计
        total_customers = len(customers)

        # 客户价值分析
        high_value_customers = []
        for customer in customers:
            # 使用transfunctions计算客户价值
            value_score = calculate_customer_value_score(
                customer,
                customer.get("transactions", []),
                customer.get("interactions", []),
            )
            if value_score.total_score >= 80:
                high_value_customers.append(
                    {"customer": customer, "value_score": value_score.total_score}
                )

        return {
            "total_customers": total_customers,
            "high_value_customers": len(high_value_customers),
            "high_value_list": high_value_customers[:10],  # 前10名
            "generated_at": format_date(datetime.now(), "chinese_datetime"),
        }

    except Exception as e:
        logger.error(f"生成客户报表失败: {e}")
        raise ReportError(f"生成客户报表失败: {e}") from e


def generate_sales_report(
    sales_data: List[Dict[str, Any]], options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成销售分析报表

    Args:
        sales_data: 销售数据列表
        options: 报表选项

    Returns:
        Dict[str, Any]: 销售分析报表数据
    """
    options = options or {}

    try:
        # 基础统计
        total_sales = len(sales_data)
        total_amount = sum(sale.get("amount", 0) for sale in sales_data)

        # 月度趋势
        monthly_sales = {}
        for sale in sales_data:
            month = sale.get("date", "")[:7]  # YYYY-MM
            if month not in monthly_sales:
                monthly_sales[month] = {"count": 0, "amount": 0}
            monthly_sales[month]["count"] += 1
            monthly_sales[month]["amount"] += sale.get("amount", 0)

        return {
            "total_sales": total_sales,
            "total_amount": format_currency(total_amount),
            "monthly_trends": monthly_sales,
            "generated_at": format_date(datetime.now(), "chinese_datetime"),
        }

    except Exception as e:
        logger.error(f"生成销售报表失败: {e}")
        raise ReportError(f"生成销售报表失败: {e}") from e


def generate_supplier_report(
    suppliers: List[Dict[str, Any]], options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成供应商分析报表

    Args:
        suppliers: 供应商数据列表
        options: 报表选项

    Returns:
        Dict[str, Any]: 供应商分析报表数据
    """
    options = options or {}

    try:
        # 基础统计
        total_suppliers = len(suppliers)
        active_suppliers = len([s for s in suppliers if s.get("status") == "active"])

        return {
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
            "activity_rate": (active_suppliers / total_suppliers * 100)
            if total_suppliers > 0
            else 0,
            "generated_at": format_date(datetime.now(), "chinese_datetime"),
        }

    except Exception as e:
        logger.error(f"生成供应商报表失败: {e}")
        raise ReportError(f"生成供应商报表失败: {e}") from e
