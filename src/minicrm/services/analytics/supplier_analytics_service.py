"""
MiniCRM 供应商分析服务 - 修复版本

负责供应商相关的数据分析:
- 供应商质量分析
- 供应商类别分布
- 顶级供应商识别
- 供应商绩效评估

严格遵循业务逻辑层职责:
- 只处理供应商分析相关的业务逻辑
- 通过DAO接口访问数据
- 不包含UI逻辑

注意:此文件已修复所有方法缺失问题,但仍需要拆分以符合文件大小标准
"""

import logging
from typing import Any

from minicrm.core.exceptions import ServiceError
from minicrm.core.interfaces.dao_interfaces import ISupplierDAO
from minicrm.models.analytics_models import SupplierAnalysis


class SupplierAnalyticsService:
    """
    供应商分析服务

    提供完整的供应商分析功能:
    - 供应商质量评估和分布
    - 供应商类别统计
    - 顶级供应商识别
    - 供应商绩效分析
    """

    def __init__(self, supplier_dao: ISupplierDAO):
        """
        初始化供应商分析服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        self._supplier_dao = supplier_dao
        self._logger = logging.getLogger(__name__)

        self._logger.debug("供应商分析服务初始化完成")

    def get_supplier_analysis(self, time_period_months: int = 12) -> SupplierAnalysis:
        """
        获取供应商分析数据

        Args:
            time_period_months: 分析时间段(月)

        Returns:
            SupplierAnalysis: 供应商分析结果

        Raises:
            ServiceError: 当分析失败时
        """
        try:
            self._logger.info(f"开始供应商分析,时间段: {time_period_months}个月")

            # 获取供应商统计数据
            supplier_stats = self._supplier_dao.get_statistics()

            # 获取所有供应商数据
            all_suppliers = self._supplier_dao.search()

            # 计算质量分布
            quality_distribution = self.calculate_supplier_quality_distribution(
                all_suppliers
            )

            # 获取顶级供应商
            top_suppliers = self.get_top_suppliers(all_suppliers, limit=10)

            # 计算类别分布
            category_distribution = self.calculate_supplier_category_distribution(
                all_suppliers
            )

            analysis = SupplierAnalysis(
                total_suppliers=supplier_stats.get("total_suppliers", 0),
                active_suppliers=supplier_stats.get("active_suppliers", 0),
                quality_distribution=quality_distribution,
                top_suppliers=top_suppliers,
                category_distribution=category_distribution,
            )

            self._logger.info("供应商分析完成")
            return analysis

        except Exception as e:
            self._logger.error(f"供应商分析失败: {e}")
            raise ServiceError(
                f"供应商分析失败: {e}", "SupplierAnalyticsService"
            ) from e

    def calculate_supplier_quality_distribution(
        self, suppliers: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        计算供应商质量分布

        基于供应商的综合质量评分进行等级分布统计.

        Args:
            suppliers: 供应商数据列表

        Returns:
            Dict[str, int]: 供应商质量分布统计
        """
        distribution = {"优秀": 0, "良好": 0, "一般": 0, "需改进": 0}

        for supplier in suppliers:
            # 使用优化的供应商质量评估算法
            try:
                quality_score = self._calculate_enhanced_supplier_quality_score(
                    supplier
                )

                # 优化的质量分级阈值
                if quality_score >= 88:
                    distribution["优秀"] += 1
                elif quality_score >= 75:
                    distribution["良好"] += 1
                elif quality_score >= 60:
                    distribution["一般"] += 1
                else:
                    distribution["需改进"] += 1
            except Exception as e:
                self._logger.warning(f"计算供应商质量失败: {e}")
                distribution["需改进"] += 1

        return distribution

    def _calculate_enhanced_supplier_quality_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """
        计算增强的供应商质量评分 - 优化版本

        采用多层次评估体系和动态权重分配:
        1. 产品质量 (25-35%权重,根据供应商类型调整)
        2. 交付能力 (20-30%权重,根据业务需求调整)
        3. 服务质量 (15-25%权重,根据合作深度调整)
        4. 价格竞争力 (10-20%权重,根据市场环境调整)
        5. 合作稳定性 (10-15%权重,根据合作历史调整)
        6. 创新能力 (5-10%权重,新增维度)
        7. 可持续发展 (5%权重,新增维度)

        Args:
            supplier: 供应商数据

        Returns:
            float: 供应商质量评分 (0-100)
        """
        try:
            # 获取供应商基本信息
            supplier_type = supplier.get("supplier_type", "standard")
            category = supplier.get("category", "general")
            cooperation_years = supplier.get("cooperation_years", 0)

            # 动态权重计算
            weights = self._calculate_supplier_dynamic_weights(
                supplier_type, category, cooperation_years
            )

            # 1. 产品质量评分
            product_score = self._calculate_enhanced_product_quality_score(supplier)

            # 2. 交付能力评分
            delivery_score = self._calculate_enhanced_delivery_capability_score(
                supplier
            )

            # 3. 服务质量评分
            service_score = self._calculate_enhanced_service_quality_score(supplier)

            # 4. 价格竞争力评分
            price_score = self._calculate_enhanced_price_competitiveness_score(supplier)

            # 5. 合作稳定性评分
            stability_score = self._calculate_enhanced_supplier_stability_score(
                supplier
            )

            # 6. 创新能力评分
            innovation_score = self._calculate_innovation_capability_score(supplier)

            # 7. 可持续发展评分
            sustainability_score = self._calculate_sustainability_score(supplier)

            # 加权总分计算
            total_score = (
                product_score * weights["product"]
                + delivery_score * weights["delivery"]
                + service_score * weights["service"]
                + price_score * weights["price"]
                + stability_score * weights["stability"]
                + innovation_score * weights["innovation"]
                + sustainability_score * weights["sustainability"]
            )

            # 应用风险调整因子
            risk_factor = self._calculate_supplier_risk_factor(supplier)
            adjusted_score = total_score * risk_factor

            # 应用行业标准调整
            industry_factor = self._calculate_industry_standard_factor(supplier)
            final_score = adjusted_score * industry_factor

            return min(100, max(0, final_score))

        except Exception as e:
            self._logger.error(f"计算增强供应商质量评分失败: {e}")
            return 70  # 默认中等评分

    def _calculate_supplier_dynamic_weights(
        self, supplier_type: str, category: str, cooperation_years: int
    ) -> dict[str, float]:
        """
        计算供应商动态权重

        根据供应商类型、类别和合作历史动态调整各维度权重

        Args:
            supplier_type: 供应商类型
            category: 供应商类别
            cooperation_years: 合作年限

        Returns:
            Dict[str, float]: 各维度权重
        """
        # 基础权重
        base_weights = {
            "product": 0.30,
            "delivery": 0.25,
            "service": 0.20,
            "price": 0.15,
            "stability": 0.10,
            "innovation": 0.07,
            "sustainability": 0.05,
        }

        # 供应商类型调整
        if supplier_type == "strategic":
            base_weights["product"] += 0.05
            base_weights["innovation"] += 0.03
            base_weights["stability"] += 0.02
        elif supplier_type == "preferred":
            base_weights["delivery"] += 0.05
            base_weights["service"] += 0.03
        elif supplier_type == "transactional":
            base_weights["price"] += 0.08
            base_weights["delivery"] += 0.02

        # 类别调整 (板材行业特定)
        if category in ["raw_materials", "core_materials"]:
            base_weights["product"] += 0.05
            base_weights["delivery"] += 0.03
        elif category in ["auxiliary_materials", "packaging"]:
            base_weights["price"] += 0.05
            base_weights["service"] += 0.03

        # 合作年限调整
        if cooperation_years < 1:  # 新供应商
            base_weights["service"] += 0.05
            base_weights["delivery"] += 0.03
        elif cooperation_years > 3:  # 长期合作
            base_weights["stability"] += 0.05
            base_weights["innovation"] += 0.03

        # 归一化权重
        total_weight = sum(base_weights.values())
        return {k: v / total_weight for k, v in base_weights.items()}

    # 注意:以下方法需要完整实现,这里提供简化版本以修复编译错误
    def _calculate_enhanced_product_quality_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """计算增强的产品质量评分 (0-100分)"""
        defect_rate = supplier.get("defect_rate", 0.05)
        return_rate = supplier.get("return_rate", 0.03)

        # 简化实现 - 实际项目中需要完整的算法
        import math

        defect_score = 50 * math.exp(-defect_rate * 20)
        return_score = 50 * math.exp(-return_rate * 30)

        return min(100, defect_score + return_score)

    def _calculate_enhanced_delivery_capability_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """计算增强的交付能力评分 (0-100分)"""
        on_time_rate = supplier.get("on_time_rate", 0.85)
        lead_time_accuracy = supplier.get("lead_time_accuracy", 0.80)

        # 简化实现
        return (on_time_rate * 50) + (lead_time_accuracy * 50)

    def _calculate_enhanced_service_quality_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """计算增强的服务质量评分 (0-100分)"""
        service_rating = supplier.get("service_rating", 3.5)
        response_time = supplier.get("avg_response_time_hours", 24)

        # 简化实现
        rating_score = ((service_rating - 1) / 4) * 70
        response_score = max(0, 30 - response_time)

        return rating_score + response_score

    def _calculate_enhanced_price_competitiveness_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """计算增强的价格竞争力评分 (0-100分)"""
        price_level = supplier.get("price_level", "medium")

        # 简化实现
        price_mapping = {"low": 100, "medium": 70, "high": 40}
        return price_mapping.get(price_level, 70)

    def _calculate_enhanced_supplier_stability_score(
        self, supplier: dict[str, Any]
    ) -> float:
        """计算增强的供应商稳定性评分 (0-100分)"""
        cooperation_years = supplier.get("cooperation_years", 0)
        financial_stability = supplier.get("financial_stability", "stable")

        # 简化实现
        years_score = min(50, cooperation_years * 10)
        stability_mapping = {"excellent": 50, "stable": 35, "unstable": 10}
        financial_score = stability_mapping.get(financial_stability, 35)

        return years_score + financial_score

    def _calculate_innovation_capability_score(self, supplier: dict[str, Any]) -> float:
        """计算创新能力评分 (0-100分)"""
        rd_investment = supplier.get("rd_investment_rate", 0.02)

        # 简化实现
        return min(100, rd_investment * 5000)

    def _calculate_sustainability_score(self, supplier: dict[str, Any]) -> float:
        """计算可持续发展评分 (0-100分)"""
        environmental_certifications = supplier.get("environmental_certifications", [])

        # 简化实现
        return min(100, len(environmental_certifications) * 25)

    def _calculate_supplier_risk_factor(self, supplier: dict[str, Any]) -> float:
        """计算供应商风险调整因子 (0.7-1.1)"""
        financial_health = supplier.get("financial_health", "stable")

        # 简化实现
        health_mapping = {"excellent": 1.05, "good": 1.02, "stable": 1.0, "poor": 0.85}
        return health_mapping.get(financial_health, 1.0)

    def _calculate_industry_standard_factor(self, supplier: dict[str, Any]) -> float:
        """计算行业标准调整因子 (0.9-1.1)"""
        industry_category = supplier.get("industry_category", "general")

        # 简化实现
        if industry_category in ["wood_processing", "furniture_materials"]:
            return 1.05
        return 1.0

    def get_top_suppliers(
        self, suppliers: list[dict[str, Any]], limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取顶级供应商

        基于质量评分排序,返回质量最高的供应商列表.

        Args:
            suppliers: 供应商数据列表
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 顶级供应商列表
        """
        try:
            # 按质量评分排序
            sorted_suppliers = sorted(
                suppliers, key=lambda x: x.get("quality_score", 0), reverse=True
            )
            return sorted_suppliers[:limit]

        except Exception as e:
            self._logger.error(f"获取顶级供应商失败: {e}")
            return suppliers[:limit]

    def calculate_supplier_category_distribution(
        self, suppliers: list[dict[str, Any]]
    ) -> dict[str, int]:
        """
        计算供应商类别分布

        统计不同类别供应商的数量分布.

        Args:
            suppliers: 供应商数据列表

        Returns:
            Dict[str, int]: 供应商类别分布统计
        """
        distribution: dict[str, int] = {}

        for supplier in suppliers:
            category = supplier.get("category", "其他")
            distribution[category] = distribution.get(category, 0) + 1

        return distribution

    def analyze_supplier_performance(
        self, suppliers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        分析供应商绩效

        对供应商列表进行综合绩效分析,包括质量、交付、服务等维度.

        Args:
            suppliers: 供应商数据列表

        Returns:
            Dict[str, Any]: 供应商绩效分析结果
        """
        try:
            self._logger.info(f"开始分析{len(suppliers)}个供应商的绩效")

            if not suppliers:
                return {
                    "total_suppliers": 0,
                    "average_performance": 0,
                    "performance_distribution": {},
                    "top_performers": [],
                    "improvement_needed": [],
                }

            # 计算每个供应商的绩效评分
            performance_scores = []
            for supplier in suppliers:
                score = self._calculate_enhanced_supplier_quality_score(supplier)
                supplier_with_score = supplier.copy()
                supplier_with_score["performance_score"] = score
                performance_scores.append(supplier_with_score)

            # 计算平均绩效
            avg_performance = sum(
                s["performance_score"] for s in performance_scores
            ) / len(performance_scores)

            # 绩效分布统计
            performance_distribution = {"优秀": 0, "良好": 0, "一般": 0, "需改进": 0}
            for supplier in performance_scores:
                score = supplier["performance_score"]
                if score >= 85:
                    performance_distribution["优秀"] += 1
                elif score >= 70:
                    performance_distribution["良好"] += 1
                elif score >= 55:
                    performance_distribution["一般"] += 1
                else:
                    performance_distribution["需改进"] += 1

            # 排序获取顶级和需改进的供应商
            sorted_suppliers = sorted(
                performance_scores, key=lambda x: x["performance_score"], reverse=True
            )
            top_performers = sorted_suppliers[:5]  # 前5名
            improvement_needed = [
                s for s in sorted_suppliers if s["performance_score"] < 55
            ]

            result = {
                "total_suppliers": len(suppliers),
                "average_performance": round(avg_performance, 2),
                "performance_distribution": performance_distribution,
                "top_performers": top_performers,
                "improvement_needed": improvement_needed,
                "analysis_summary": {
                    "excellent_count": performance_distribution["优秀"],
                    "good_count": performance_distribution["良好"],
                    "average_count": performance_distribution["一般"],
                    "poor_count": performance_distribution["需改进"],
                },
            }

            self._logger.info(f"供应商绩效分析完成,平均绩效: {avg_performance:.2f}")
            return result

        except Exception as e:
            self._logger.error(f"供应商绩效分析失败: {e}")
            raise ServiceError(
                f"供应商绩效分析失败: {e}", "SupplierAnalyticsService"
            ) from e

    def get_supplier_risk_analysis(
        self, suppliers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        获取供应商风险分析

        分析供应商的各种风险因素,包括财务风险、供应风险、质量风险等.

        Args:
            suppliers: 供应商数据列表

        Returns:
            Dict[str, Any]: 供应商风险分析结果
        """
        try:
            self._logger.info(f"开始分析{len(suppliers)}个供应商的风险")

            if not suppliers:
                return {
                    "total_suppliers": 0,
                    "overall_risk_level": "低",
                    "risk_distribution": {},
                    "high_risk_suppliers": [],
                    "risk_factors": {},
                }

            # 分析每个供应商的风险
            risk_analysis = []
            for supplier in suppliers:
                risk_score = self._calculate_supplier_risk_score(supplier)
                risk_level = self._determine_risk_level(risk_score)

                supplier_risk = {
                    "supplier_id": supplier.get("id"),
                    "supplier_name": supplier.get("name", "未知"),
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "risk_factors": self._identify_risk_factors(supplier),
                }
                risk_analysis.append(supplier_risk)

            # 风险分布统计
            risk_distribution = {"高": 0, "中": 0, "低": 0}
            for analysis in risk_analysis:
                risk_distribution[analysis["risk_level"]] += 1

            # 识别高风险供应商
            high_risk_suppliers = [s for s in risk_analysis if s["risk_level"] == "高"]

            # 计算整体风险水平
            avg_risk_score = sum(s["risk_score"] for s in risk_analysis) / len(
                risk_analysis
            )
            overall_risk_level = self._determine_risk_level(avg_risk_score)

            # 统计主要风险因素
            all_risk_factors: dict[str, int] = {}
            for analysis in risk_analysis:
                for factor in analysis["risk_factors"]:
                    all_risk_factors[factor] = all_risk_factors.get(factor, 0) + 1

            result = {
                "total_suppliers": len(suppliers),
                "overall_risk_level": overall_risk_level,
                "average_risk_score": round(avg_risk_score, 2),
                "risk_distribution": risk_distribution,
                "high_risk_suppliers": high_risk_suppliers,
                "risk_factors": all_risk_factors,
                "detailed_analysis": risk_analysis,
                "recommendations": self._generate_risk_recommendations(risk_analysis),
            }

            self._logger.info(f"供应商风险分析完成,整体风险水平: {overall_risk_level}")
            return result

        except Exception as e:
            self._logger.error(f"供应商风险分析失败: {e}")
            raise ServiceError(
                f"供应商风险分析失败: {e}", "SupplierAnalyticsService"
            ) from e

    def _calculate_supplier_risk_score(self, supplier: dict[str, Any]) -> float:
        """
        计算供应商风险评分

        Args:
            supplier: 供应商数据

        Returns:
            float: 风险评分 (0-100,分数越高风险越大)
        """
        risk_score = 0

        # 财务风险 (30%权重)
        financial_health = supplier.get("financial_health", "stable")
        financial_risk = {
            "poor": 30,
            "unstable": 20,
            "stable": 10,
            "good": 5,
            "excellent": 0,
        }
        risk_score += financial_risk.get(financial_health, 15)

        # 质量风险 (25%权重)
        defect_rate = supplier.get("defect_rate", 0.05)
        quality_risk = min(25, defect_rate * 500)  # 缺陷率转换为风险分数
        risk_score += quality_risk

        # 交付风险 (20%权重)
        on_time_rate = supplier.get("on_time_rate", 0.85)
        delivery_risk = max(0, (1 - on_time_rate) * 20)
        risk_score += delivery_risk

        # 依赖风险 (15%权重)
        dependency_level = supplier.get("dependency_level", "medium")
        dependency_risk = {"high": 15, "medium": 8, "low": 3}
        risk_score += dependency_risk.get(dependency_level, 8)

        # 地理风险 (10%权重)
        geographic_risk = supplier.get("geographic_risk", "low")
        geo_risk = {"high": 10, "medium": 6, "low": 2}
        risk_score += geo_risk.get(geographic_risk, 4)

        return min(100, risk_score)

    def _determine_risk_level(self, risk_score: float) -> str:
        """
        根据风险评分确定风险等级

        Args:
            risk_score: 风险评分

        Returns:
            str: 风险等级
        """
        if risk_score >= 60:
            return "高"
        elif risk_score >= 30:
            return "中"
        else:
            return "低"

    def _identify_risk_factors(self, supplier: dict[str, Any]) -> list[str]:
        """
        识别供应商的风险因素

        Args:
            supplier: 供应商数据

        Returns:
            List[str]: 风险因素列表
        """
        risk_factors = []

        # 检查各种风险因素
        if supplier.get("financial_health") in ["poor", "unstable"]:
            risk_factors.append("财务状况不佳")

        if supplier.get("defect_rate", 0) > 0.03:
            risk_factors.append("产品质量问题")

        if supplier.get("on_time_rate", 1) < 0.8:
            risk_factors.append("交付延迟风险")

        if supplier.get("dependency_level") == "high":
            risk_factors.append("高度依赖风险")

        if supplier.get("geographic_risk") == "high":
            risk_factors.append("地理位置风险")

        if supplier.get("cooperation_years", 0) < 1:
            risk_factors.append("合作经验不足")

        return risk_factors

    def _generate_risk_recommendations(
        self, risk_analysis: list[dict[str, Any]]
    ) -> list[str]:
        """
        生成风险管理建议

        Args:
            risk_analysis: 风险分析结果

        Returns:
            List[str]: 风险管理建议
        """
        recommendations = []

        high_risk_count = len([s for s in risk_analysis if s["risk_level"] == "高"])

        if high_risk_count > 0:
            recommendations.append(
                f"发现{high_risk_count}个高风险供应商,建议立即制定风险缓解计划"
            )

        # 基于风险因素生成建议
        all_factors = {}
        for analysis in risk_analysis:
            for factor in analysis["risk_factors"]:
                all_factors[factor] = all_factors.get(factor, 0) + 1

        if all_factors.get("财务状况不佳", 0) > 0:
            recommendations.append("建议加强对财务状况不佳供应商的监控和评估")

        if all_factors.get("产品质量问题", 0) > 0:
            recommendations.append("建议实施更严格的质量控制和检验程序")

        if all_factors.get("交付延迟风险", 0) > 0:
            recommendations.append("建议建立备用供应商网络以降低交付风险")

        if not recommendations:
            recommendations.append("当前供应商风险水平较低,建议保持现有管理策略")

        return recommendations
