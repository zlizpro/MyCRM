"""
MiniCRM 分析模型定义

定义数据分析相关的数据模型:
- 客户分析结果模型
- 供应商分析结果模型
- 趋势分析结果模型
- 预测结果模型
- 指标卡片模型
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CustomerAnalysis:
    """客户分析结果模型"""

    total_customers: int
    new_customers_this_month: int
    active_customers: int
    customer_value_distribution: dict[str, int]
    top_customers: list[dict[str, Any]]
    growth_trend: list[dict[str, Any]]


@dataclass
class SupplierAnalysis:
    """供应商分析结果模型"""

    total_suppliers: int
    active_suppliers: int
    quality_distribution: dict[str, int]
    top_suppliers: list[dict[str, Any]]
    category_distribution: dict[str, int]


@dataclass
class TrendAnalysis:
    """趋势分析结果模型"""

    metric_name: str
    period: str
    data_points: list[dict[str, Any]]
    trend_direction: str
    growth_rate: float
    prediction: dict[str, Any] | None = None


@dataclass
class PredictionResult:
    """预测结果模型"""

    metric_name: str
    prediction_period: str
    predicted_values: list[dict[str, Any]]
    confidence_level: float
    method_used: str


@dataclass
class MetricCard:
    """指标卡片模型"""

    title: str
    value: Any
    unit: str = ""
    trend: str = "stable"  # "up", "down", "stable"
    trend_value: float = 0.0
    color: str = "primary"  # "primary", "success", "warning", "danger"


@dataclass
class ChartData:
    """图表数据模型"""

    chart_type: str  # "line", "bar", "pie", "doughnut"
    title: str
    labels: list[str]
    datasets: list[dict[str, Any]]
    options: dict[str, Any] | None = None
