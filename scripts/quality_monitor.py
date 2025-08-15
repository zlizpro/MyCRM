#!/usr/bin/env python3
"""
MiniCRM 实时代码质量监控脚本

监控代码质量指标变化，生成趋势报告和预警。
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path


class QualityMetrics:
    """代码质量指标数据类"""

    def __init__(self):
        self.timestamp = datetime.now()
        self.ruff_issues = 0
        self.mypy_errors = 0
        self.file_size_violations = 0
        self.transfunctions_violations = 0
        self.coverage_percentage = 0.0
        self.total_lines = 0
        self.total_files = 0

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "ruff_issues": self.ruff_issues,
            "mypy_errors": self.mypy_errors,
            "file_size_violations": self.file_size_violations,
            "transfunctions_violations": self.transfunctions_violations,
            "coverage_percentage": self.coverage_percentage,
            "total_lines": self.total_lines,
            "total_files": self.total_files,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "QualityMetrics":
        """从字典创建实例"""
        metrics = cls()
        metrics.timestamp = datetime.fromisoformat(data["timestamp"])
        metrics.ruff_issues = data.get("ruff_issues", 0)
        metrics.mypy_errors = data.get("mypy_errors", 0)
        metrics.file_size_violations = data.get("file_size_violations", 0)
        metrics.transfunctions_violations = data.get("transfunctions_violations", 0)
        metrics.coverage_percentage = data.get("coverage_percentage", 0.0)
        metrics.total_lines = data.get("total_lines", 0)
        metrics.total_files = data.get("total_files", 0)
        return metrics


class QualityMonitor:
    """代码质量监控器"""

    def __init__(self, data_file: str = "quality_metrics.json"):
        """
        初始化质量监控器

        Args:
            data_file: 质量指标数据文件路径
        """
        self.data_file = Path(data_file)
        self.project_root = Path.cwd()
        self.history: list[QualityMetrics] = []
        self._load_history()

    def _load_history(self) -> None:
        """加载历史质量指标数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.history = [
                        QualityMetrics.from_dict(item)
                        for item in data.get("history", [])
                    ]
            except Exception as e:
                print(f"⚠️  加载历史数据失败: {e}")
                self.history = []

    def _save_history(self) -> None:
        """保存历史质量指标数据"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "history": [metrics.to_dict() for metrics in self.history],
            }
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存历史数据失败: {e}")

    def collect_current_metrics(self) -> QualityMetrics:
        """收集当前的质量指标"""
        print("📊 收集当前质量指标...")
        metrics = QualityMetrics()

        # 收集Ruff问题数量
        metrics.ruff_issues = self._count_ruff_issues()

        # 收集MyPy错误数量
        metrics.mypy_errors = self._count_mypy_errors()

        # 收集文件大小违规数量
        metrics.file_size_violations = self._count_file_size_violations()

        # 收集Transfunctions违规数量
        metrics.transfunctions_violations = self._count_transfunctions_violations()

        # 收集代码覆盖率
        metrics.coverage_percentage = self._get_coverage_percentage()

        # 收集代码统计
        metrics.total_lines, metrics.total_files = self._count_code_stats()

        return metrics

    def _count_ruff_issues(self) -> int:
        """统计Ruff问题数量"""
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "check", "--config", "ruff.toml", "src/"],
                capture_output=True,
                text=True,
            )
            # Ruff输出每行一个问题
            if result.stdout:
                return len(result.stdout.strip().split("\n"))
            return 0
        except Exception:
            return -1

    def _count_mypy_errors(self) -> int:
        """统计MyPy错误数量"""
        try:
            result = subprocess.run(
                ["uv", "run", "mypy", "--config-file=mypy.ini", "src/minicrm/"],
                capture_output=True,
                text=True,
            )
            # 统计错误行数
            if result.stdout:
                error_lines = [
                    line for line in result.stdout.split("\n") if ": error:" in line
                ]
                return len(error_lines)
            return 0
        except Exception:
            return -1

    def _count_file_size_violations(self) -> int:
        """统计文件大小违规数量"""
        try:
            result = subprocess.run(
                ["python", "scripts/check_file_sizes.py"],
                capture_output=True,
                text=True,
            )
            # 统计违规文件数量
            if result.stdout:
                violation_lines = [
                    line for line in result.stdout.split("\n") if "❌" in line
                ]
                return len(violation_lines)
            return 0
        except Exception:
            return -1

    def _count_transfunctions_violations(self) -> int:
        """统计Transfunctions违规数量"""
        try:
            result = subprocess.run(
                ["python", "scripts/check_transfunctions_usage.py"],
                capture_output=True,
                text=True,
            )
            # 统计违规数量
            if result.stdout:
                violation_lines = [
                    line for line in result.stdout.split("\n") if "❌" in line
                ]
                return len(violation_lines)
            return 0
        except Exception:
            return -1

    def _get_coverage_percentage(self) -> float:
        """获取代码覆盖率"""
        try:
            # 尝试从coverage.json读取
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)
                    return data.get("totals", {}).get("percent_covered", 0.0)
            return 0.0
        except Exception:
            return 0.0

    def _count_code_stats(self) -> tuple[int, int]:
        """统计代码行数和文件数"""
        try:
            total_lines = 0
            total_files = 0

            for py_file in Path("src").glob("**/*.py"):
                if py_file.name != "__init__.py":
                    try:
                        with open(py_file, encoding="utf-8") as f:
                            lines = len(f.readlines())
                            total_lines += lines
                            total_files += 1
                    except Exception:
                        continue

            return total_lines, total_files
        except Exception:
            return 0, 0

    def add_metrics(self, metrics: QualityMetrics) -> None:
        """添加新的质量指标"""
        self.history.append(metrics)

        # 保留最近30天的数据
        cutoff_date = datetime.now() - timedelta(days=30)
        self.history = [m for m in self.history if m.timestamp > cutoff_date]

        self._save_history()

    def generate_trend_report(self) -> str:
        """生成趋势报告"""
        if len(self.history) < 2:
            return "📊 数据不足，无法生成趋势报告"

        current = self.history[-1]
        previous = self.history[-2]

        report = f"""# 代码质量趋势报告

## 📈 总体趋势 ({previous.timestamp.strftime("%Y-%m-%d")} → {current.timestamp.strftime("%Y-%m-%d")})

### 质量指标变化

| 指标 | 之前 | 当前 | 变化 | 趋势 |
|------|------|------|------|------|
| Ruff问题 | {previous.ruff_issues} | {current.ruff_issues} | {current.ruff_issues - previous.ruff_issues:+d} | {"📈" if current.ruff_issues > previous.ruff_issues else "📉" if current.ruff_issues < previous.ruff_issues else "➡️"} |
| MyPy错误 | {previous.mypy_errors} | {current.mypy_errors} | {current.mypy_errors - previous.mypy_errors:+d} | {"📈" if current.mypy_errors > previous.mypy_errors else "📉" if current.mypy_errors < previous.mypy_errors else "➡️"} |
| 文件大小违规 | {previous.file_size_violations} | {current.file_size_violations} | {current.file_size_violations - previous.file_size_violations:+d} | {"📈" if current.file_size_violations > previous.file_size_violations else "📉" if current.file_size_violations < previous.file_size_violations else "➡️"} |
| Transfunctions违规 | {previous.transfunctions_violations} | {current.transfunctions_violations} | {current.transfunctions_violations - previous.transfunctions_violations:+d} | {"📈" if current.transfunctions_violations > previous.transfunctions_violations else "📉" if current.transfunctions_violations < previous.transfunctions_violations else "➡️"} |
| 代码覆盖率 | {previous.coverage_percentage:.1f}% | {current.coverage_percentage:.1f}% | {current.coverage_percentage - previous.coverage_percentage:+.1f}% | {"📈" if current.coverage_percentage > previous.coverage_percentage else "📉" if current.coverage_percentage < previous.coverage_percentage else "➡️"} |
| 总代码行数 | {previous.total_lines} | {current.total_lines} | {current.total_lines - previous.total_lines:+d} | {"📈" if current.total_lines > previous.total_lines else "📉" if current.total_lines < previous.total_lines else "➡️"} |
| 总文件数 | {previous.total_files} | {current.total_files} | {current.total_files - previous.total_files:+d} | {"📈" if current.total_files > previous.total_files else "📉" if current.total_files < previous.total_files else "➡️"} |

### 质量评分

"""

        # 计算质量评分
        quality_score = self._calculate_quality_score(current)
        previous_score = self._calculate_quality_score(previous)

        report += f"- 当前质量评分: {quality_score:.1f}/100\n"
        report += f"- 之前质量评分: {previous_score:.1f}/100\n"
        report += f"- 评分变化: {quality_score - previous_score:+.1f}\n\n"

        # 添加建议
        report += self._generate_recommendations(current, previous)

        return report

    def _calculate_quality_score(self, metrics: QualityMetrics) -> float:
        """计算质量评分"""
        score = 100.0

        # 扣分项
        score -= min(metrics.ruff_issues * 0.5, 20)  # Ruff问题，最多扣20分
        score -= min(metrics.mypy_errors * 1.0, 25)  # MyPy错误，最多扣25分
        score -= min(metrics.file_size_violations * 2.0, 15)  # 文件大小违规，最多扣15分
        score -= min(
            metrics.transfunctions_violations * 1.5, 10
        )  # Transfunctions违规，最多扣10分

        # 覆盖率加分/扣分
        if metrics.coverage_percentage >= 90:
            score += 10
        elif metrics.coverage_percentage >= 80:
            score += 5
        elif metrics.coverage_percentage < 60:
            score -= 10

        return max(0, min(100, score))

    def _generate_recommendations(
        self, current: QualityMetrics, previous: QualityMetrics
    ) -> str:
        """生成改进建议"""
        recommendations = "### 🎯 改进建议\n\n"

        if current.ruff_issues > previous.ruff_issues:
            recommendations += (
                "- ⚠️  Ruff问题增加，建议运行 `uv run ruff check --fix src/` 自动修复\n"
            )

        if current.mypy_errors > previous.mypy_errors:
            recommendations += "- ⚠️  MyPy错误增加，建议检查类型注解和导入\n"

        if current.file_size_violations > previous.file_size_violations:
            recommendations += "- ⚠️  文件大小违规增加，建议拆分大文件\n"

        if current.transfunctions_violations > previous.transfunctions_violations:
            recommendations += "- ⚠️  Transfunctions违规增加，建议使用可复用函数\n"

        if current.coverage_percentage < previous.coverage_percentage:
            recommendations += "- ⚠️  代码覆盖率下降，建议添加测试用例\n"

        if current.coverage_percentage < 80:
            recommendations += "- 📝 代码覆盖率偏低，建议提高到80%以上\n"

        # 正面反馈
        improvements = []
        if current.ruff_issues < previous.ruff_issues:
            improvements.append("Ruff问题减少")
        if current.mypy_errors < previous.mypy_errors:
            improvements.append("MyPy错误减少")
        if current.coverage_percentage > previous.coverage_percentage:
            improvements.append("代码覆盖率提高")

        if improvements:
            recommendations += "\n### ✅ 改进成果\n\n"
            for improvement in improvements:
                recommendations += f"- 🎉 {improvement}\n"

        return recommendations

    def check_quality_alerts(self, metrics: QualityMetrics) -> list[str]:
        """检查质量预警"""
        alerts = []

        if metrics.ruff_issues > 50:
            alerts.append(f"🚨 Ruff问题过多: {metrics.ruff_issues} 个")

        if metrics.mypy_errors > 20:
            alerts.append(f"🚨 MyPy错误过多: {metrics.mypy_errors} 个")

        if metrics.file_size_violations > 5:
            alerts.append(f"🚨 文件大小违规过多: {metrics.file_size_violations} 个")

        if metrics.coverage_percentage < 60:
            alerts.append(f"🚨 代码覆盖率过低: {metrics.coverage_percentage:.1f}%")

        quality_score = self._calculate_quality_score(metrics)
        if quality_score < 70:
            alerts.append(f"🚨 整体质量评分过低: {quality_score:.1f}/100")

        return alerts

    def run_monitoring_cycle(self) -> None:
        """运行一次监控周期"""
        print("🔍 开始代码质量监控...")

        # 收集当前指标
        current_metrics = self.collect_current_metrics()

        # 添加到历史记录
        self.add_metrics(current_metrics)

        # 生成趋势报告
        trend_report = self.generate_trend_report()

        # 检查预警
        alerts = self.check_quality_alerts(current_metrics)

        # 输出结果
        print("\n" + "=" * 60)
        print("📊 当前质量指标:")
        print(f"   Ruff问题: {current_metrics.ruff_issues}")
        print(f"   MyPy错误: {current_metrics.mypy_errors}")
        print(f"   文件大小违规: {current_metrics.file_size_violations}")
        print(f"   Transfunctions违规: {current_metrics.transfunctions_violations}")
        print(f"   代码覆盖率: {current_metrics.coverage_percentage:.1f}%")
        print(f"   代码行数: {current_metrics.total_lines}")
        print(f"   文件数量: {current_metrics.total_files}")

        quality_score = self._calculate_quality_score(current_metrics)
        print(f"   质量评分: {quality_score:.1f}/100")

        if alerts:
            print("\n🚨 质量预警:")
            for alert in alerts:
                print(f"   {alert}")

        # 保存报告
        with open("quality-trend-report.md", "w", encoding="utf-8") as f:
            f.write(trend_report)

        print("\n📄 趋势报告已保存到: quality-trend-report.md")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM 代码质量监控")
    parser.add_argument(
        "--data-file", default="quality_metrics.json", help="质量指标数据文件"
    )
    parser.add_argument(
        "--continuous", action="store_true", help="持续监控模式（每小时运行一次）"
    )
    parser.add_argument(
        "--interval", type=int, default=3600, help="持续监控间隔（秒，默认3600）"
    )

    args = parser.parse_args()

    monitor = QualityMonitor(args.data_file)

    if args.continuous:
        print(f"🔄 启动持续监控模式，间隔: {args.interval} 秒")
        try:
            while True:
                monitor.run_monitoring_cycle()
                print(f"⏰ 等待 {args.interval} 秒后进行下次监控...")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 监控已停止")
    else:
        monitor.run_monitoring_cycle()


if __name__ == "__main__":
    main()
