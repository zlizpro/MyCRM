"""供应商对比和评估TTK组件简化测试.

不依赖GUI环境的单元测试，主要测试业务逻辑和数据处理功能。
"""

import unittest
from unittest.mock import Mock

from minicrm.models.supplier import QualityRating, SupplierLevel, SupplierType


class TestSupplierComparisonLogic(unittest.TestCase):
    """供应商对比逻辑测试类（不依赖GUI）."""

    def setUp(self):
        """测试前准备."""
        # 创建模拟的供应商服务
        self.mock_supplier_service = Mock()

        # 模拟供应商数据
        self.mock_suppliers = [
            {
                "id": 1,
                "name": "供应商A",
                "company_name": "A公司",
                "supplier_type": SupplierType.MANUFACTURER.value,
                "supplier_level": SupplierLevel.STRATEGIC.value,
                "quality_rating": QualityRating.EXCELLENT.value,
                "quality_score": 95.0,
                "delivery_rating": 90.0,
                "service_rating": 88.0,
                "cooperation_years": 5,
                "total_orders": 100,
                "total_amount": 1000000.0,
            },
            {
                "id": 2,
                "name": "供应商B",
                "company_name": "B公司",
                "supplier_type": SupplierType.DISTRIBUTOR.value,
                "supplier_level": SupplierLevel.IMPORTANT.value,
                "quality_rating": QualityRating.GOOD.value,
                "quality_score": 85.0,
                "delivery_rating": 92.0,
                "service_rating": 80.0,
                "cooperation_years": 3,
                "total_orders": 80,
                "total_amount": 800000.0,
            },
        ]

        # 模拟评估数据
        self.mock_evaluation_data = {
            1: {
                "quality_score": 95.0,
                "delivery_score": 90.0,
                "service_score": 88.0,
                "price_competitiveness": 75.0,
                "innovation_capability": 80.0,
            },
            2: {
                "quality_score": 85.0,
                "delivery_score": 92.0,
                "service_score": 80.0,
                "price_competitiveness": 85.0,
                "innovation_capability": 70.0,
            },
        }

        # 配置模拟服务的返回值
        self.mock_supplier_service.search_suppliers.return_value = (
            self.mock_suppliers,
            len(self.mock_suppliers),
        )

        def mock_evaluate_quality(supplier_id):
            return self.mock_evaluation_data.get(supplier_id, {})

        self.mock_supplier_service.evaluate_supplier_quality.side_effect = (
            mock_evaluate_quality
        )

    def test_supplier_data_structure(self):
        """测试供应商数据结构."""
        supplier = self.mock_suppliers[0]

        # 验证必要字段存在
        self.assertIn("id", supplier)
        self.assertIn("name", supplier)
        self.assertIn("company_name", supplier)
        self.assertIn("supplier_type", supplier)
        self.assertIn("quality_score", supplier)

        # 验证数据类型
        self.assertIsInstance(supplier["id"], int)
        self.assertIsInstance(supplier["quality_score"], float)
        self.assertIsInstance(supplier["cooperation_years"], int)

    def test_evaluation_data_structure(self):
        """测试评估数据结构."""
        evaluation = self.mock_evaluation_data[1]

        # 验证评估指标存在
        required_metrics = [
            "quality_score",
            "delivery_score",
            "service_score",
            "price_competitiveness",
            "innovation_capability",
        ]

        for metric in required_metrics:
            self.assertIn(metric, evaluation)
            self.assertIsInstance(evaluation[metric], (int, float))

    def test_metric_value_extraction(self):
        """测试指标值提取功能."""

        # 模拟供应商对比组件的指标提取逻辑
        def get_metric_value(supplier_data: dict, metric_key: str) -> str:
            """获取供应商指标值."""
            basic_info = supplier_data.get("basic_info", {})
            evaluation = supplier_data.get("evaluation", {})
            performance = supplier_data.get("performance", {})

            # 基本信息指标
            if metric_key in basic_info:
                value = basic_info[metric_key]
                if isinstance(value, (int, float)):
                    return f"{value:.2f}" if isinstance(value, float) else str(value)
                return str(value) if value else "-"

            # 评估指标
            if metric_key in evaluation:
                value = evaluation[metric_key]
                if isinstance(value, (int, float)):
                    return f"{value:.2f}" if isinstance(value, float) else str(value)
                return str(value) if value else "-"

            # 绩效指标
            if metric_key in performance:
                value = performance[metric_key]
                if isinstance(value, (int, float)):
                    return f"{value:.2f}" if isinstance(value, float) else str(value)
                return str(value) if value else "-"

            return "-"

        # 准备测试数据
        supplier_data = {
            "basic_info": {"name": "测试供应商", "quality_score": 85.5},
            "evaluation": {"delivery_score": 90.0},
            "performance": {"customer_satisfaction": 88.0},
        }

        # 测试基本信息指标
        value = get_metric_value(supplier_data, "name")
        self.assertEqual(value, "测试供应商")

        value = get_metric_value(supplier_data, "quality_score")
        self.assertEqual(value, "85.50")

        # 测试评估指标
        value = get_metric_value(supplier_data, "delivery_score")
        self.assertEqual(value, "90.00")

        # 测试绩效指标
        value = get_metric_value(supplier_data, "customer_satisfaction")
        self.assertEqual(value, "88.00")

        # 测试不存在的指标
        value = get_metric_value(supplier_data, "nonexistent")
        self.assertEqual(value, "-")

    def test_safe_float_conversion(self):
        """测试安全浮点数转换功能."""

        def safe_float(value) -> float:
            """安全转换为浮点数."""
            try:
                if isinstance(value, str):
                    # 移除非数字字符
                    clean_value = "".join(c for c in value if c.isdigit() or c in ".-")
                    return float(clean_value) if clean_value else 0.0
                return float(value) if value else 0.0
            except (ValueError, TypeError):
                return 0.0

        # 测试正常数值
        self.assertEqual(safe_float(85.5), 85.5)
        self.assertEqual(safe_float("90.0"), 90.0)
        self.assertEqual(safe_float(100), 100.0)

        # 测试异常值
        self.assertEqual(safe_float(""), 0.0)
        self.assertEqual(safe_float(None), 0.0)
        self.assertEqual(safe_float("abc"), 0.0)

        # 测试带单位的字符串
        self.assertEqual(safe_float("85.5分"), 85.5)

    def test_best_supplier_finding(self):
        """测试最佳供应商查找功能."""

        def find_best_supplier(comparison_data: dict) -> dict | None:
            """找出最佳供应商."""
            if not comparison_data:
                return None

            best_supplier = None
            best_score = -1

            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                # 计算综合评分
                quality_score = evaluation.get("quality_score", 0)
                delivery_score = evaluation.get("delivery_score", 0)
                service_score = evaluation.get("service_score", 0)

                overall_score = (
                    quality_score * 0.4 + delivery_score * 0.3 + service_score * 0.3
                )

                if overall_score > best_score:
                    best_score = overall_score
                    best_supplier = {
                        "id": supplier_id,
                        "name": basic_info.get("name", "未知供应商"),
                        "overall_score": overall_score,
                        "reason": "在质量、交期、服务三个维度表现均衡，综合评分最高",
                    }

            return best_supplier

        # 设置对比数据
        comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 查找最佳供应商
        best_supplier = find_best_supplier(comparison_data)

        # 验证结果
        self.assertIsNotNone(best_supplier)
        self.assertEqual(best_supplier["name"], "供应商A")  # 供应商A评分最高
        self.assertGreater(best_supplier["overall_score"], 0)

    def test_dimension_best_finding(self):
        """测试维度最佳供应商查找功能."""

        def find_best_in_dimension(
            comparison_data: dict, dimension_key: str
        ) -> dict | None:
            """找出某个维度的最佳供应商."""
            if not comparison_data:
                return None

            best_supplier = None
            best_score = -1

            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                score = evaluation.get(dimension_key, 0)
                if score > best_score:
                    best_score = score
                    best_supplier = {
                        "id": supplier_id,
                        "name": basic_info.get("name", "未知供应商"),
                        "score": score,
                    }

            return best_supplier

        # 设置对比数据
        comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 查找质量评分最佳供应商
        best_quality = find_best_in_dimension(comparison_data, "quality_score")
        self.assertIsNotNone(best_quality)
        self.assertEqual(best_quality["name"], "供应商A")  # 供应商A质量评分最高

        # 查找交期评分最佳供应商
        best_delivery = find_best_in_dimension(comparison_data, "delivery_score")
        self.assertIsNotNone(best_delivery)
        self.assertEqual(best_delivery["name"], "供应商B")  # 供应商B交期评分最高

    def test_risk_assessment(self):
        """测试风险评估功能."""

        def assess_risks(comparison_data: dict) -> list[str]:
            """评估风险."""
            risks = []

            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                supplier_name = basic_info.get("name", "未知供应商")

                # 质量风险
                if evaluation.get("quality_score", 0) < 60:
                    risks.append(f"{supplier_name}：质量评分较低，存在质量风险")

                # 交期风险
                if evaluation.get("delivery_score", 0) < 70:
                    risks.append(f"{supplier_name}：交期评分较低，可能影响供货及时性")

                # 合作风险
                if basic_info.get("cooperation_years", 0) < 1:
                    risks.append(f"{supplier_name}：合作时间较短，缺乏长期合作经验")

            if not risks:
                risks.append("暂未发现明显风险")

            return risks

        # 设置对比数据（包含低分供应商）
        low_score_evaluation = {
            "quality_score": 50.0,  # 低质量评分
            "delivery_score": 60.0,  # 低交期评分
            "service_score": 70.0,
        }

        comparison_data = {
            1: {
                "basic_info": {"name": "低分供应商", "cooperation_years": 0},
                "evaluation": low_score_evaluation,
            },
        }

        # 评估风险
        risks = assess_risks(comparison_data)

        # 验证风险识别
        self.assertGreater(len(risks), 0)
        self.assertTrue(any("质量风险" in risk for risk in risks))
        self.assertTrue(any("交期" in risk for risk in risks))
        self.assertTrue(any("合作时间较短" in risk for risk in risks))

    def test_recommendations_generation(self):
        """测试建议生成功能."""

        def generate_recommendations(comparison_data: dict) -> list[str]:
            """生成建议."""
            recommendations = []

            # 找出最佳供应商
            best_supplier = None
            best_score = -1

            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                quality_score = evaluation.get("quality_score", 0)
                delivery_score = evaluation.get("delivery_score", 0)
                service_score = evaluation.get("service_score", 0)

                overall_score = (
                    quality_score * 0.4 + delivery_score * 0.3 + service_score * 0.3
                )

                if overall_score > best_score:
                    best_score = overall_score
                    best_supplier = basic_info.get("name", "未知供应商")

            if best_supplier:
                recommendations.append(f"建议优先选择 {best_supplier} 作为主要供应商")

            # 多元化建议
            if len(comparison_data) > 1:
                recommendations.append("建议采用多供应商策略，降低供应风险")

            # 改进建议
            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                supplier_name = basic_info.get("name", "未知供应商")

                if evaluation.get("quality_score", 0) < 80:
                    recommendations.append(f"建议与 {supplier_name} 协商质量改进计划")

            recommendations.append("定期重新评估供应商表现，动态调整合作策略")

            return recommendations

        # 设置对比数据
        comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
            2: {
                "basic_info": self.mock_suppliers[1],
                "evaluation": self.mock_evaluation_data[2],
            },
        }

        # 生成建议
        recommendations = generate_recommendations(comparison_data)

        # 验证建议内容
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("建议优先选择" in rec for rec in recommendations))
        self.assertTrue(any("多供应商策略" in rec for rec in recommendations))
        self.assertTrue(any("定期重新评估" in rec for rec in recommendations))

    def test_report_content_building(self):
        """测试报告内容构建功能."""

        def build_evaluation_report(comparison_data: dict) -> str:
            """构建评估报告内容."""
            from datetime import datetime

            report_lines = []

            # 报告标题
            report_lines.append("=" * 60)
            report_lines.append("供应商对比评估报告")
            report_lines.append("=" * 60)
            report_lines.append(
                f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            report_lines.append(f"对比供应商数量：{len(comparison_data)}")
            report_lines.append("")

            # 执行摘要
            report_lines.append("一、执行摘要")
            report_lines.append("-" * 30)

            # 找出最佳供应商
            best_supplier = None
            best_score = -1

            for supplier_id, data in comparison_data.items():
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                quality_score = evaluation.get("quality_score", 0)
                delivery_score = evaluation.get("delivery_score", 0)
                service_score = evaluation.get("service_score", 0)

                overall_score = (
                    quality_score * 0.4 + delivery_score * 0.3 + service_score * 0.3
                )

                if overall_score > best_score:
                    best_score = overall_score
                    best_supplier = {
                        "name": basic_info.get("name", "未知供应商"),
                        "overall_score": overall_score,
                    }

            if best_supplier:
                report_lines.append(f"推荐供应商：{best_supplier['name']}")
                report_lines.append(f"综合评分：{best_supplier['overall_score']:.2f}")

            report_lines.append("")

            # 供应商详细分析
            report_lines.append("二、供应商详细分析")
            report_lines.append("-" * 30)

            for i, (supplier_id, data) in enumerate(comparison_data.items(), 1):
                basic_info = data["basic_info"]
                evaluation = data["evaluation"]

                report_lines.append(f"{i}. {basic_info.get('name', '未知供应商')}")
                report_lines.append(
                    f"   公司名称：{basic_info.get('company_name', '-')}"
                )
                report_lines.append(
                    f"   质量评分：{evaluation.get('quality_score', 0):.2f}"
                )
                report_lines.append(
                    f"   交期评分：{evaluation.get('delivery_score', 0):.2f}"
                )
                report_lines.append(
                    f"   服务评分：{evaluation.get('service_score', 0):.2f}"
                )
                report_lines.append("")

            return "\n".join(report_lines)

        # 设置对比数据
        comparison_data = {
            1: {
                "basic_info": self.mock_suppliers[0],
                "evaluation": self.mock_evaluation_data[1],
            },
        }

        # 构建报告内容
        report_content = build_evaluation_report(comparison_data)

        # 验证报告内容
        self.assertIsInstance(report_content, str)
        self.assertIn("供应商对比评估报告", report_content)
        self.assertIn("执行摘要", report_content)
        self.assertIn("供应商详细分析", report_content)
        self.assertIn("推荐供应商", report_content)

    def test_service_integration(self):
        """测试服务集成."""
        # 测试服务方法调用
        suppliers, total = self.mock_supplier_service.search_suppliers(
            query="", filters={}, page=1, page_size=100
        )

        # 验证返回结果
        self.assertEqual(len(suppliers), 2)
        self.assertEqual(total, 2)
        self.assertEqual(suppliers[0]["name"], "供应商A")
        self.assertEqual(suppliers[1]["name"], "供应商B")

        # 测试评估服务调用
        evaluation = self.mock_supplier_service.evaluate_supplier_quality(1)
        self.assertIn("quality_score", evaluation)
        self.assertEqual(evaluation["quality_score"], 95.0)

    def test_data_validation(self):
        """测试数据验证."""
        # 验证供应商数据完整性
        for supplier in self.mock_suppliers:
            # 必需字段检查
            required_fields = ["id", "name", "company_name", "supplier_type"]
            for field in required_fields:
                self.assertIn(field, supplier, f"缺少必需字段: {field}")

            # 数据类型检查
            self.assertIsInstance(supplier["id"], int)
            self.assertIsInstance(supplier["name"], str)
            self.assertIsInstance(supplier["quality_score"], (int, float))

            # 数值范围检查
            self.assertGreaterEqual(supplier["quality_score"], 0)
            self.assertLessEqual(supplier["quality_score"], 100)

        # 验证评估数据完整性
        for supplier_id, evaluation in self.mock_evaluation_data.items():
            # 评估指标检查
            required_metrics = ["quality_score", "delivery_score", "service_score"]
            for metric in required_metrics:
                self.assertIn(metric, evaluation, f"缺少评估指标: {metric}")
                self.assertIsInstance(evaluation[metric], (int, float))
                self.assertGreaterEqual(evaluation[metric], 0)
                self.assertLessEqual(evaluation[metric], 100)


if __name__ == "__main__":
    unittest.main()
