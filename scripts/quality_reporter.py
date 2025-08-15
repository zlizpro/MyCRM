#!/usr/bin/env python3
"""
MiniCRM 定期质量报告生成器

定期生成详细的代码质量报告，包括趋势分析、团队评分等。
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


class QualityReporter:
    """质量报告生成器"""

    def __init__(self, data_file: str = "quality_metrics.json"):
        """
        初始化质量报告生成器

        Args:
            data_file: 质量指标数据文件
        """
        self.data_file = Path(data_file)
        self.project_root = Path.cwd()
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def load_quality_history(self) -> list[dict]:
        """加载质量历史数据"""
        if not self.data_file.exists():
            return []

        try:
            with open(self.data_file, encoding="utf-8") as f:
                data = json.load(f)
                return data.get("history", [])
        except Exception as e:
            print(f"❌ 加载质量历史数据失败: {e}")
            return []

    def generate_daily_report(self) -> str:
        """生成每日质量报告"""
        history = self.load_quality_history()
        if not history:
            return "📊 暂无质量数据"

        today = datetime.now().date()
        latest_metrics = history[-1]
        latest_date = datetime.fromisoformat(latest_metrics["timestamp"]).date()

        # 获取昨天的数据（如果有）
        yesterday_metrics = None
        for metrics in reversed(history[:-1]):
            metrics_date = datetime.fromisoformat(metrics["timestamp"]).date()
            if metrics_date < latest_date:
                yesterday_metrics = metrics
                break

        report = f"""# MiniCRM 每日质量报告

**报告日期**: {today.strftime("%Y年%m月%d日")}
**数据时间**: {latest_date.strftime("%Y年%m月%d日")}

## 📊 当日质量概览

### 核心指标

| 指标 | 当前值 | 昨日值 | 变化 | 状态 |
|------|--------|--------|------|------|
| Ruff问题 | {latest_metrics.get("ruff_issues", 0)} | {yesterday_metrics.get("ruff_issues", 0) if yesterday_metrics else "N/A"} | {self._format_change(latest_metrics.get("ruff_issues", 0), yesterday_metrics.get("ruff_issues", 0) if yesterday_metrics else 0)} | {self._get_status_emoji(latest_metrics.get("ruff_issues", 0), 50, reverse=True)} |
| MyPy错误 | {latest_metrics.get("mypy_errors", 0)} | {yesterday_metrics.get("mypy_errors", 0) if yesterday_metrics else "N/A"} | {self._format_change(latest_metrics.get("mypy_errors", 0), yesterday_metrics.get("mypy_errors", 0) if yesterday_metrics else 0)} | {self._get_status_emoji(latest_metrics.get("mypy_errors", 0), 20, reverse=True)} |
| 文件大小违规 | {latest_metrics.get("file_size_violations", 0)} | {yesterday_metrics.get("file_size_violations", 0) if yesterday_metrics else "N/A"} | {self._format_change(latest_metrics.get("file_size_violations", 0), yesterday_metrics.get("file_size_violations", 0) if yesterday_metrics else 0)} | {self._get_status_emoji(latest_metrics.get("file_size_violations", 0), 5, reverse=True)} |
| Transfunctions违规 | {latest_metrics.get("transfunctions_violations", 0)} | {yesterday_metrics.get("transfunctions_violations", 0) if yesterday_metrics else "N/A"} | {self._format_change(latest_metrics.get("transfunctions_violations", 0), yesterday_metrics.get("transfunctions_violations", 0) if yesterday_metrics else 0)} | {self._get_status_emoji(latest_metrics.get("transfunctions_violations", 0), 10, reverse=True)} |
| 代码覆盖率 | {latest_metrics.get("coverage_percentage", 0):.1f}% | {yesterday_metrics.get("coverage_percentage", 0):.1f}% if yesterday_metrics else 'N/A' | {self._format_change(latest_metrics.get("coverage_percentage", 0), yesterday_metrics.get("coverage_percentage", 0) if yesterday_metrics else 0, is_percentage=True)} | {self._get_status_emoji(latest_metrics.get("coverage_percentage", 0), 80)} |

### 代码统计

- **总代码行数**: {latest_metrics.get("total_lines", 0):,} 行
- **总文件数**: {latest_metrics.get("total_files", 0)} 个
- **平均文件大小**: {latest_metrics.get("total_lines", 0) // max(latest_metrics.get("total_files", 1), 1)} 行/文件

### 质量评分

"""

        # 计算质量评分
        quality_score = self._calculate_quality_score(latest_metrics)
        yesterday_score = (
            self._calculate_quality_score(yesterday_metrics)
            if yesterday_metrics
            else quality_score
        )

        report += f"- **当前评分**: {quality_score:.1f}/100 {self._get_score_emoji(quality_score)}\n"
        if yesterday_metrics:
            report += f"- **昨日评分**: {yesterday_score:.1f}/100\n"
            report += f"- **评分变化**: {self._format_change(quality_score, yesterday_score, is_percentage=False)}\n"

        report += "\n"

        # 添加改进建议
        report += self._generate_daily_recommendations(
            latest_metrics, yesterday_metrics
        )

        return report

    def generate_weekly_report(self) -> str:
        """生成每周质量报告"""
        history = self.load_quality_history()
        if not history:
            return "📊 暂无质量数据"

        # 获取最近7天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        weekly_data = [
            metrics
            for metrics in history
            if start_date <= datetime.fromisoformat(metrics["timestamp"]) <= end_date
        ]

        if not weekly_data:
            return "📊 本周暂无质量数据"

        report = f"""# MiniCRM 每周质量报告

**报告周期**: {start_date.strftime("%Y年%m月%d日")} - {end_date.strftime("%Y年%m月%d日")}
**数据点数**: {len(weekly_data)} 个

## 📈 本周质量趋势

### 趋势分析

"""

        # 分析趋势
        if len(weekly_data) >= 2:
            first_metrics = weekly_data[0]
            last_metrics = weekly_data[-1]

            trends = {
                "Ruff问题": (
                    last_metrics.get("ruff_issues", 0)
                    - first_metrics.get("ruff_issues", 0)
                ),
                "MyPy错误": (
                    last_metrics.get("mypy_errors", 0)
                    - first_metrics.get("mypy_errors", 0)
                ),
                "文件大小违规": (
                    last_metrics.get("file_size_violations", 0)
                    - first_metrics.get("file_size_violations", 0)
                ),
                "Transfunctions违规": (
                    last_metrics.get("transfunctions_violations", 0)
                    - first_metrics.get("transfunctions_violations", 0)
                ),
                "代码覆盖率": (
                    last_metrics.get("coverage_percentage", 0)
                    - first_metrics.get("coverage_percentage", 0)
                ),
            }

            for metric, change in trends.items():
                if metric == "代码覆盖率":
                    trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                    report += f"- **{metric}**: {change:+.1f}% {trend_emoji}\n"
                else:
                    trend_emoji = "📉" if change < 0 else "📈" if change > 0 else "➡️"
                    report += f"- **{metric}**: {change:+d} {trend_emoji}\n"

        # 计算平均值
        avg_metrics = self._calculate_average_metrics(weekly_data)
        report += "\n### 本周平均指标\n\n"
        report += f"- **平均Ruff问题**: {avg_metrics['ruff_issues']:.1f}\n"
        report += f"- **平均MyPy错误**: {avg_metrics['mypy_errors']:.1f}\n"
        report += f"- **平均文件大小违规**: {avg_metrics['file_size_violations']:.1f}\n"
        report += f"- **平均Transfunctions违规**: {avg_metrics['transfunctions_violations']:.1f}\n"
        report += f"- **平均代码覆盖率**: {avg_metrics['coverage_percentage']:.1f}%\n"
        report += f"- **平均质量评分**: {avg_metrics['quality_score']:.1f}/100\n"

        # 添加周度建议
        report += self._generate_weekly_recommendations(weekly_data)

        return report

    def generate_monthly_report(self) -> str:
        """生成每月质量报告"""
        history = self.load_quality_history()
        if not history:
            return "📊 暂无质量数据"

        # 获取最近30天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        monthly_data = [
            metrics
            for metrics in history
            if start_date <= datetime.fromisoformat(metrics["timestamp"]) <= end_date
        ]

        if not monthly_data:
            return "📊 本月暂无质量数据"

        report = f"""# MiniCRM 每月质量报告

**报告月份**: {end_date.strftime("%Y年%m月")}
**报告周期**: {start_date.strftime("%Y年%m月%d日")} - {end_date.strftime("%Y年%m月%d日")}
**数据点数**: {len(monthly_data)} 个

## 📊 月度质量总结

### 整体表现

"""

        # 计算月度统计
        monthly_stats = self._calculate_monthly_stats(monthly_data)

        report += f"- **最佳质量评分**: {monthly_stats['max_quality_score']:.1f}/100\n"
        report += f"- **最低质量评分**: {monthly_stats['min_quality_score']:.1f}/100\n"
        report += f"- **平均质量评分**: {monthly_stats['avg_quality_score']:.1f}/100\n"
        report += f"- **质量改善天数**: {monthly_stats['improvement_days']} 天\n"
        report += f"- **质量下降天数**: {monthly_stats['decline_days']} 天\n"

        report += "\n### 问题统计\n\n"
        report += f"- **Ruff问题总数**: {monthly_stats['total_ruff_issues']}\n"
        report += f"- **MyPy错误总数**: {monthly_stats['total_mypy_errors']}\n"
        report += (
            f"- **文件大小违规总数**: {monthly_stats['total_file_size_violations']}\n"
        )
        report += f"- **Transfunctions违规总数**: {monthly_stats['total_transfunctions_violations']}\n"

        # 添加月度建议
        report += self._generate_monthly_recommendations(monthly_data, monthly_stats)

        return report

    def _format_change(
        self, current: float, previous: float, is_percentage: bool = False
    ) -> str:
        """格式化变化值"""
        if previous == 0 and current == 0:
            return "无变化"

        change = current - previous
        if is_percentage:
            return f"{change:+.1f}%"
        else:
            return f"{change:+.0f}" if change == int(change) else f"{change:+.1f}"

    def _get_status_emoji(
        self, value: float, threshold: float, reverse: bool = False
    ) -> str:
        """获取状态表情符号"""
        if reverse:
            # 对于问题数量，越少越好
            if value == 0:
                return "🟢"
            elif value <= threshold * 0.5:
                return "🟡"
            elif value <= threshold:
                return "🟠"
            else:
                return "🔴"
        else:
            # 对于覆盖率等，越高越好
            if value >= threshold * 1.2:
                return "🟢"
            elif value >= threshold:
                return "🟡"
            elif value >= threshold * 0.8:
                return "🟠"
            else:
                return "🔴"

    def _get_score_emoji(self, score: float) -> str:
        """获取评分表情符号"""
        if score >= 90:
            return "🏆"
        elif score >= 80:
            return "🥇"
        elif score >= 70:
            return "🥈"
        elif score >= 60:
            return "🥉"
        else:
            return "⚠️"

    def _calculate_quality_score(self, metrics: dict) -> float:
        """计算质量评分"""
        score = 100.0

        # 扣分项
        score -= min(metrics.get("ruff_issues", 0) * 0.5, 20)
        score -= min(metrics.get("mypy_errors", 0) * 1.0, 25)
        score -= min(metrics.get("file_size_violations", 0) * 2.0, 15)
        score -= min(metrics.get("transfunctions_violations", 0) * 1.5, 10)

        # 覆盖率加分/扣分
        coverage = metrics.get("coverage_percentage", 0)
        if coverage >= 90:
            score += 10
        elif coverage >= 80:
            score += 5
        elif coverage < 60:
            score -= 10

        return max(0, min(100, score))

    def _calculate_average_metrics(self, data: list[dict]) -> dict:
        """计算平均指标"""
        if not data:
            return {}

        totals = {
            "ruff_issues": 0,
            "mypy_errors": 0,
            "file_size_violations": 0,
            "transfunctions_violations": 0,
            "coverage_percentage": 0,
            "quality_score": 0,
        }

        for metrics in data:
            totals["ruff_issues"] += metrics.get("ruff_issues", 0)
            totals["mypy_errors"] += metrics.get("mypy_errors", 0)
            totals["file_size_violations"] += metrics.get("file_size_violations", 0)
            totals["transfunctions_violations"] += metrics.get(
                "transfunctions_violations", 0
            )
            totals["coverage_percentage"] += metrics.get("coverage_percentage", 0)
            totals["quality_score"] += self._calculate_quality_score(metrics)

        count = len(data)
        return {key: value / count for key, value in totals.items()}

    def _calculate_monthly_stats(self, data: list[dict]) -> dict:
        """计算月度统计"""
        if not data:
            return {}

        quality_scores = [self._calculate_quality_score(metrics) for metrics in data]

        stats = {
            "max_quality_score": max(quality_scores),
            "min_quality_score": min(quality_scores),
            "avg_quality_score": sum(quality_scores) / len(quality_scores),
            "improvement_days": 0,
            "decline_days": 0,
            "total_ruff_issues": sum(metrics.get("ruff_issues", 0) for metrics in data),
            "total_mypy_errors": sum(metrics.get("mypy_errors", 0) for metrics in data),
            "total_file_size_violations": sum(
                metrics.get("file_size_violations", 0) for metrics in data
            ),
            "total_transfunctions_violations": sum(
                metrics.get("transfunctions_violations", 0) for metrics in data
            ),
        }

        # 计算改善和下降天数
        for i in range(1, len(quality_scores)):
            if quality_scores[i] > quality_scores[i - 1]:
                stats["improvement_days"] += 1
            elif quality_scores[i] < quality_scores[i - 1]:
                stats["decline_days"] += 1

        return stats

    def _generate_daily_recommendations(
        self, current: dict, previous: dict | None
    ) -> str:
        """生成每日改进建议"""
        recommendations = "## 🎯 今日改进建议\n\n"

        # 基于当前指标的建议
        if current.get("ruff_issues", 0) > 0:
            recommendations += f"- 🔧 修复 {current['ruff_issues']} 个Ruff问题: `uv run ruff check --fix src/`\n"

        if current.get("mypy_errors", 0) > 0:
            recommendations += f"- 🏷️  修复 {current['mypy_errors']} 个MyPy类型错误\n"

        if current.get("file_size_violations", 0) > 0:
            recommendations += (
                f"- 📏 拆分 {current['file_size_violations']} 个过大文件\n"
            )

        if current.get("transfunctions_violations", 0) > 0:
            recommendations += f"- 🔄 使用transfunctions替换 {current['transfunctions_violations']} 个重复实现\n"

        if current.get("coverage_percentage", 0) < 80:
            recommendations += f"- 🧪 提高代码覆盖率到80%以上（当前: {current['coverage_percentage']:.1f}%）\n"

        # 基于变化趋势的建议
        if previous:
            if current.get("ruff_issues", 0) > previous.get("ruff_issues", 0):
                recommendations += "- ⚠️  Ruff问题增加，建议在提交前运行代码检查\n"

            if current.get("coverage_percentage", 0) < previous.get(
                "coverage_percentage", 0
            ):
                recommendations += "- 📉 代码覆盖率下降，建议为新代码添加测试\n"

        return recommendations

    def _generate_weekly_recommendations(self, data: list[dict]) -> str:
        """生成每周改进建议"""
        recommendations = "\n## 🎯 本周改进重点\n\n"

        avg_metrics = self._calculate_average_metrics(data)

        # 基于平均指标的建议
        if avg_metrics.get("quality_score", 0) < 80:
            recommendations += "- 📊 整体质量评分偏低，建议制定质量改进计划\n"

        if avg_metrics.get("ruff_issues", 0) > 20:
            recommendations += "- 🔧 Ruff问题较多，建议配置pre-commit hooks\n"

        if avg_metrics.get("coverage_percentage", 0) < 75:
            recommendations += "- 🧪 代码覆盖率需要提升，建议增加单元测试\n"

        recommendations += "- 📈 建议每日运行质量检查，及时发现问题\n"
        recommendations += "- 👥 建议团队进行代码质量培训\n"

        return recommendations

    def _generate_monthly_recommendations(self, data: list[dict], stats: dict) -> str:
        """生成每月改进建议"""
        recommendations = "\n## 🎯 下月改进计划\n\n"

        if stats.get("avg_quality_score", 0) < 80:
            recommendations += "- 📋 制定质量改进路线图，设定月度目标\n"

        if stats.get("decline_days", 0) > stats.get("improvement_days", 0):
            recommendations += "- 📉 质量下降天数较多，需要加强质量管控\n"

        recommendations += "- 🎯 建议设定下月质量目标:\n"
        recommendations += "  - Ruff问题 < 30个\n"
        recommendations += "  - MyPy错误 < 15个\n"
        recommendations += "  - 代码覆盖率 > 85%\n"
        recommendations += "  - 质量评分 > 85分\n"

        recommendations += "- 🔄 建议优化开发流程:\n"
        recommendations += "  - 强制使用pre-commit hooks\n"
        recommendations += "  - 增加代码审查环节\n"
        recommendations += "  - 定期进行重构\n"

        return recommendations

    def save_report(self, report: str, report_type: str) -> str:
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{timestamp}.md"
        filepath = self.reports_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report)
            return str(filepath)
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")
            return ""

    def generate_all_reports(self) -> dict[str, str]:
        """生成所有类型的报告"""
        reports = {}

        print("📊 生成每日质量报告...")
        daily_report = self.generate_daily_report()
        daily_path = self.save_report(daily_report, "daily")
        if daily_path:
            reports["daily"] = daily_path

        print("📈 生成每周质量报告...")
        weekly_report = self.generate_weekly_report()
        weekly_path = self.save_report(weekly_report, "weekly")
        if weekly_path:
            reports["weekly"] = weekly_path

        print("📅 生成每月质量报告...")
        monthly_report = self.generate_monthly_report()
        monthly_path = self.save_report(monthly_report, "monthly")
        if monthly_path:
            reports["monthly"] = monthly_path

        return reports


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM 质量报告生成器")
    parser.add_argument(
        "--type",
        choices=["daily", "weekly", "monthly", "all"],
        default="daily",
        help="报告类型",
    )
    parser.add_argument(
        "--data-file", default="quality_metrics.json", help="质量指标数据文件"
    )
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    reporter = QualityReporter(args.data_file)

    if args.type == "all":
        reports = reporter.generate_all_reports()
        print("\n✅ 所有报告生成完成:")
        for report_type, path in reports.items():
            print(f"   {report_type}: {path}")
    else:
        print(f"📊 生成{args.type}质量报告...")

        if args.type == "daily":
            report = reporter.generate_daily_report()
        elif args.type == "weekly":
            report = reporter.generate_weekly_report()
        elif args.type == "monthly":
            report = reporter.generate_monthly_report()

        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"✅ 报告已保存到: {args.output}")
            except Exception as e:
                print(f"❌ 保存报告失败: {e}")
                print(report)
        else:
            saved_path = reporter.save_report(report, args.type)
            if saved_path:
                print(f"✅ 报告已保存到: {saved_path}")
            else:
                print(report)


if __name__ == "__main__":
    main()
