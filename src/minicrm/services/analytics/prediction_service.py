"""
MiniCRM 预测分析服务

负责业务预测相关的数据分析:
- 业务指标预测
- 移动平均预测
- 历史数据处理
- 预测结果评估

严格遵循业务逻辑层职责:
- 只处理预测分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from minicrm.core.exceptions import ServiceError, ValidationError
from minicrm.core.interfaces.dao_interfaces import ICustomerDAO, ISupplierDAO
from minicrm.models.analytics_models import PredictionResult
from transfunctions.calculations import calculate_average


class PredictionService:
    """
    预测分析服务

    提供完整的预测分析功能:
    - 业务指标预测
    - 多种预测算法
    - 预测结果评估
    - 置信度计算
    """

    def __init__(self, customer_dao: ICustomerDAO, supplier_dao: ISupplierDAO):
        """
        初始化预测服务

        Args:
            customer_dao: 客户数据访问对象
            supplier_dao: 供应商数据访问对象
        """
        self._customer_dao = customer_dao
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        self._logger.debug("预测分析服务初始化完成")

    def get_prediction(
        self, metric: str, prediction_months: int = 6
    ) -> PredictionResult:
        """
        获取业务预测

        Args:
            metric: 预测指标
            prediction_months: 预测月数

        Returns:
            PredictionResult: 预测结果

        Raises:
            ServiceError: 当预测失败时
        """
        try:
            self._logger.info(f"开始预测分析: {metric}, 预测{prediction_months}个月")

            # 获取历史数据
            historical_data = self._get_historical_data_for_prediction(metric)

            if len(historical_data) < 3:
                raise ValidationError("历史数据不足,无法进行预测")

            # 使用简单移动平均进行预测
            predicted_values = self._simple_moving_average_prediction(
                historical_data, prediction_months
            )

            # 计算置信度
            confidence_level = self._calculate_confidence_level(historical_data)

            result = PredictionResult(
                metric_name=metric,
                prediction_period=f"{prediction_months}个月",
                predicted_values=predicted_values,
                confidence_level=confidence_level,
                method_used="简单移动平均",
            )

            self._logger.info(f"预测分析完成: {metric}")
            return result

        except Exception as e:
            self._logger.error(f"预测分析失败: {e}")
            raise ServiceError(f"预测分析失败: {e}", "PredictionService") from e

    def get_advanced_prediction(
        self, metric: str, prediction_months: int = 6, method: str = "linear_regression"
    ) -> PredictionResult:
        """
        获取高级预测分析

        使用更复杂的预测算法进行分析.

        Args:
            metric: 预测指标
            prediction_months: 预测月数
            method: 预测方法
                ("linear_regression", "exponential_smoothing", "trend_analysis")

        Returns:
            PredictionResult: 预测结果
        """
        try:
            self._logger.info(f"开始高级预测分析: {metric}, 方法: {method}")

            historical_data = self._get_historical_data_for_prediction(metric)

            if len(historical_data) < 6:
                raise ValidationError("历史数据不足,建议至少6个数据点")

            if method == "linear_regression":
                predicted_values = self._linear_regression_prediction(
                    historical_data, prediction_months
                )
                confidence_level = 0.85
            elif method == "exponential_smoothing":
                predicted_values = self._exponential_smoothing_prediction(
                    historical_data, prediction_months
                )
                confidence_level = 0.80
            elif method == "trend_analysis":
                predicted_values = self._trend_analysis_prediction(
                    historical_data, prediction_months
                )
                confidence_level = 0.75
            else:
                raise ValidationError(f"不支持的预测方法: {method}")

            result = PredictionResult(
                metric_name=metric,
                prediction_period=f"{prediction_months}个月",
                predicted_values=predicted_values,
                confidence_level=confidence_level,
                method_used=method,
            )

            return result

        except Exception as e:
            self._logger.error(f"高级预测分析失败: {e}")
            raise ServiceError(f"高级预测分析失败: {e}", "PredictionService") from e

    def _get_historical_data_for_prediction(self, metric: str) -> list[dict[str, Any]]:
        """
        获取用于预测的历史数据

        Args:
            metric: 指标名称

        Returns:
            List[Dict[str, Any]]: 历史数据
        """
        if metric == "customer_growth":
            return self._get_customer_growth_historical_data()
        elif metric == "revenue":
            return self._get_revenue_historical_data()
        elif metric == "supplier_performance":
            return self._get_supplier_performance_historical_data()
        else:
            return []

    def _get_customer_growth_historical_data(self) -> list[dict[str, Any]]:
        """获取客户增长历史数据"""
        # 模拟数据,实际应从数据库获取
        return [
            {"date": "2024-01", "value": 100},
            {"date": "2024-02", "value": 105},
            {"date": "2024-03", "value": 110},
            {"date": "2024-04", "value": 115},
            {"date": "2024-05", "value": 118},
            {"date": "2024-06", "value": 122},
            {"date": "2024-07", "value": 125},
            {"date": "2024-08", "value": 130},
            {"date": "2024-09", "value": 135},
            {"date": "2024-10", "value": 140},
            {"date": "2024-11", "value": 145},
            {"date": "2024-12", "value": 150},
        ]

    def _get_revenue_historical_data(self) -> list[dict[str, Any]]:
        """获取收入历史数据"""
        # 模拟数据,实际应从财务模块获取
        return [
            {"date": "2024-01", "value": 800000},
            {"date": "2024-02", "value": 820000},
            {"date": "2024-03", "value": 850000},
            {"date": "2024-04", "value": 880000},
            {"date": "2024-05", "value": 900000},
            {"date": "2024-06", "value": 920000},
            {"date": "2024-07", "value": 950000},
            {"date": "2024-08", "value": 980000},
            {"date": "2024-09", "value": 1000000},
            {"date": "2024-10", "value": 1020000},
            {"date": "2024-11", "value": 1050000},
            {"date": "2024-12", "value": 1080000},
        ]

    def _get_supplier_performance_historical_data(self) -> list[dict[str, Any]]:
        """获取供应商绩效历史数据"""
        # 模拟数据
        return [
            {"date": "2024-01", "value": 82.5},
            {"date": "2024-02", "value": 83.2},
            {"date": "2024-03", "value": 84.1},
            {"date": "2024-04", "value": 84.8},
            {"date": "2024-05", "value": 85.5},
            {"date": "2024-06", "value": 86.2},
            {"date": "2024-07", "value": 86.8},
            {"date": "2024-08", "value": 87.5},
            {"date": "2024-09", "value": 88.1},
            {"date": "2024-10", "value": 88.8},
            {"date": "2024-11", "value": 89.2},
            {"date": "2024-12", "value": 89.8},
        ]

    def _simple_moving_average_prediction(
        self, historical_data: list[dict[str, Any]], prediction_months: int
    ) -> list[dict[str, Any]]:
        """
        简单移动平均预测

        Args:
            historical_data: 历史数据
            prediction_months: 预测月数

        Returns:
            List[Dict[str, Any]]: 预测结果
        """
        if len(historical_data) < 3:
            return []

        # 计算最近3个月的平均值作为基础
        recent_values = [point["value"] for point in historical_data[-3:]]
        avg_value = calculate_average(recent_values)

        # 计算增长趋势
        if len(historical_data) >= 2:
            growth_rate = (
                historical_data[-1]["value"] - historical_data[-2]["value"]
            ) / historical_data[-2]["value"]
        else:
            growth_rate = 0.05  # 默认5%增长

        predictions = []
        last_date = datetime.strptime(historical_data[-1]["date"], "%Y-%m")

        for i in range(1, prediction_months + 1):
            pred_date = last_date + timedelta(days=i * 30)
            pred_value = avg_value * (1 + growth_rate) ** i

            predictions.append(
                {
                    "date": pred_date.strftime("%Y-%m"),
                    "value": round(pred_value, 2),
                    "confidence": 0.75,  # 简单移动平均的置信度
                }
            )

        return predictions

    def _linear_regression_prediction(
        self, historical_data: list[dict[str, Any]], prediction_months: int
    ) -> list[dict[str, Any]]:
        """
        增强的线性回归预测

        优化后的算法特点:
        - 考虑季节性因素
        - 动态置信度计算
        - 异常值处理
        - 趋势变化检测

        Args:
            historical_data: 历史数据
            prediction_months: 预测月数

        Returns:
            List[Dict[str, Any]]: 预测结果
        """
        # 数据预处理:异常值检测和处理
        cleaned_data = self._remove_outliers(historical_data)
        n = len(cleaned_data)

        if n < 3:
            # 数据不足时使用简单平均
            return self._simple_moving_average_prediction(
                historical_data, prediction_months
            )

        x_values = list(range(n))
        y_values = [point["value"] for point in cleaned_data]

        # 计算线性回归参数
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n

        numerator = sum(
            (x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n)
        )
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        slope = 0 if denominator == 0 else numerator / denominator
        intercept = y_mean - slope * x_mean

        # 计算R²决定系数来评估模型质量
        r_squared = self._calculate_r_squared(x_values, y_values, slope, intercept)

        # 检测季节性模式
        seasonal_factors = self._detect_seasonal_pattern(cleaned_data)

        # 生成预测值
        predictions = []
        last_date = datetime.strptime(cleaned_data[-1]["date"], "%Y-%m")

        for i in range(1, prediction_months + 1):
            pred_date = last_date + timedelta(days=i * 30)

            # 基础线性预测
            base_pred_value = slope * (n + i - 1) + intercept

            # 应用季节性调整
            month_index = (pred_date.month - 1) % 12
            seasonal_factor = seasonal_factors.get(month_index, 1.0)
            adjusted_pred_value = base_pred_value * seasonal_factor

            # 动态置信度计算
            confidence = self._calculate_dynamic_confidence(r_squared, i, n)

            predictions.append(
                {
                    "date": pred_date.strftime("%Y-%m"),
                    "value": round(max(adjusted_pred_value, 0), 2),
                    "confidence": confidence,
                    "seasonal_factor": seasonal_factor,
                    "base_prediction": round(base_pred_value, 2),
                }
            )

        return predictions

    def _remove_outliers(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        移除异常值

        使用IQR方法检测和处理异常值

        Args:
            data: 原始数据

        Returns:
            List[Dict[str, Any]]: 处理后的数据
        """
        if len(data) < 4:
            return data

        values = [point["value"] for point in data]
        values.sort()

        n = len(values)
        q1_index = n // 4
        q3_index = 3 * n // 4

        q1 = values[q1_index]
        q3 = values[q3_index]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # 过滤异常值
        cleaned_data = []
        for point in data:
            if lower_bound <= point["value"] <= upper_bound:
                cleaned_data.append(point)
            else:
                # 用中位数替换异常值
                median_value = values[n // 2]
                cleaned_point = point.copy()
                cleaned_point["value"] = median_value
                cleaned_data.append(cleaned_point)

        return cleaned_data

    def _calculate_r_squared(
        self,
        x_values: list[float],
        y_values: list[float],
        slope: float,
        intercept: float,
    ) -> float:
        """
        计算R²决定系数

        Args:
            x_values: X值列表
            y_values: Y值列表
            slope: 斜率
            intercept: 截距

        Returns:
            float: R²值
        """
        y_mean = sum(y_values) / len(y_values)

        # 计算总平方和
        ss_tot = sum((y - y_mean) ** 2 for y in y_values)

        # 计算残差平方和
        ss_res = sum(
            (y_values[i] - (slope * x_values[i] + intercept)) ** 2
            for i in range(len(y_values))
        )

        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def _detect_seasonal_pattern(self, data: list[dict[str, Any]]) -> dict[int, float]:
        """
        检测季节性模式

        Args:
            data: 历史数据

        Returns:
            Dict[int, float]: 月份季节性因子
        """
        if len(data) < 12:
            return dict.fromkeys(range(12), 1.0)  # 无季节性调整

        # 按月份分组计算平均值
        monthly_values: dict[int, list[float]] = {i: [] for i in range(12)}

        for point in data:
            try:
                date = datetime.strptime(point["date"], "%Y-%m")
                month_index = date.month - 1
                monthly_values[month_index].append(point["value"])
            except ValueError:
                continue

        # 计算每月平均值
        monthly_averages = {}
        overall_average = sum(point["value"] for point in data) / len(data)

        for month, values in monthly_values.items():
            if values:
                monthly_avg = sum(values) / len(values)
                seasonal_factor = (
                    monthly_avg / overall_average if overall_average > 0 else 1.0
                )
                monthly_averages[month] = seasonal_factor
            else:
                monthly_averages[month] = 1.0

        return monthly_averages

    def _calculate_dynamic_confidence(
        self, r_squared: float, prediction_step: int, data_points: int
    ) -> float:
        """
        计算动态置信度

        Args:
            r_squared: R²决定系数
            prediction_step: 预测步数
            data_points: 历史数据点数

        Returns:
            float: 置信度
        """
        # 基础置信度基于模型拟合度
        base_confidence = 0.5 + (r_squared * 0.4)

        # 数据量调整
        data_adjustment = min(0.1, data_points / 100)

        # 预测距离调整(预测越远置信度越低)
        distance_penalty = prediction_step * 0.02

        confidence = base_confidence + data_adjustment - distance_penalty

        return max(0.3, min(0.95, confidence))

    def _exponential_smoothing_prediction(
        self, historical_data: list[dict[str, Any]], prediction_months: int
    ) -> list[dict[str, Any]]:
        """
        指数平滑预测

        Args:
            historical_data: 历史数据
            prediction_months: 预测月数

        Returns:
            List[Dict[str, Any]]: 预测结果
        """
        alpha = 0.3  # 平滑参数
        values = [point["value"] for point in historical_data]

        # 计算指数平滑值
        smoothed_values = [values[0]]
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed_values[i - 1]
            smoothed_values.append(smoothed_value)

        # 使用最后的平滑值作为预测基础
        last_smoothed = smoothed_values[-1]

        predictions = []
        last_date = datetime.strptime(historical_data[-1]["date"], "%Y-%m")

        for i in range(1, prediction_months + 1):
            pred_date = last_date + timedelta(days=i * 30)
            # 简化实现:假设趋势保持稳定
            pred_value = last_smoothed

            predictions.append(
                {
                    "date": pred_date.strftime("%Y-%m"),
                    "value": round(pred_value, 2),
                    "confidence": 0.80,
                }
            )

        return predictions

    def _trend_analysis_prediction(
        self, historical_data: list[dict[str, Any]], prediction_months: int
    ) -> list[dict[str, Any]]:
        """
        趋势分析预测

        Args:
            historical_data: 历史数据
            prediction_months: 预测月数

        Returns:
            List[Dict[str, Any]]: 预测结果
        """
        values = [point["value"] for point in historical_data]

        # 计算趋势
        if len(values) >= 3:
            recent_trend = (values[-1] - values[-3]) / 2  # 最近3个月的平均变化
        else:
            recent_trend = values[-1] - values[-2] if len(values) >= 2 else 0

        predictions = []
        last_date = datetime.strptime(historical_data[-1]["date"], "%Y-%m")
        last_value = values[-1]

        for i in range(1, prediction_months + 1):
            pred_date = last_date + timedelta(days=i * 30)
            pred_value = last_value + recent_trend * i

            predictions.append(
                {
                    "date": pred_date.strftime("%Y-%m"),
                    "value": round(max(pred_value, 0), 2),
                    "confidence": 0.75,
                }
            )

        return predictions

    def _calculate_confidence_level(
        self, historical_data: list[dict[str, Any]]
    ) -> float:
        """
        计算预测置信度

        Args:
            historical_data: 历史数据

        Returns:
            float: 置信度 (0-1)
        """
        if len(historical_data) < 3:
            return 0.5

        # 基于数据稳定性计算置信度
        values = [point["value"] for point in historical_data]
        mean_value = calculate_average(values)

        # 计算变异系数
        variance = sum((v - mean_value) ** 2 for v in values) / len(values)
        std_dev = variance**0.5
        cv = std_dev / mean_value if mean_value > 0 else 1

        # 变异系数越小,置信度越高
        confidence = max(0.5, min(0.95, 1 - cv))

        return round(confidence, 2)

    def get_prediction_accuracy_analysis(
        self, metric: str, actual_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        获取预测准确性分析

        Args:
            metric: 指标名称
            actual_data: 实际数据

        Returns:
            Dict[str, Any]: 预测准确性分析结果
        """
        try:
            # 简化实现,实际应该比较历史预测与实际结果
            accuracy_analysis = {
                "metric": metric,
                "prediction_accuracy": 0.82,  # 模拟准确率
                "average_error_rate": 0.18,
                "best_prediction_method": "linear_regression",
                "recommendations": [
                    "增加历史数据样本量以提高预测准确性",
                    "考虑季节性因素对预测的影响",
                    "定期更新预测模型参数",
                ],
            }

            return accuracy_analysis

        except Exception as e:
            self._logger.error(f"预测准确性分析失败: {e}")
            raise ServiceError(f"预测准确性分析失败: {e}", "PredictionService") from e
