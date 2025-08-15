#!/usr/bin/env python3
"""
MiniCRM 代码质量报警系统

监控代码质量指标，当指标超出阈值时发送报警通知。
"""

import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


try:
    import requests
except ImportError:
    requests = None


class AlertConfig:
    """报警配置类"""

    def __init__(self, config_file: str = "alert_config.json"):
        """
        初始化报警配置

        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "thresholds": {
                "ruff_issues": 50,
                "mypy_errors": 20,
                "file_size_violations": 5,
                "transfunctions_violations": 10,
                "min_coverage": 60.0,
                "min_quality_score": 70.0,
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_emails": [],
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel": "#code-quality",
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {},
                },
            },
            "alert_cooldown": 3600,  # 1小时内不重复发送相同报警
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    user_config = json.load(f)
                    # 合并配置
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  加载配置文件失败: {e}")

        return default_config

    def save_config(self) -> None:
        """保存配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存配置文件失败: {e}")

    def create_default_config(self) -> None:
        """创建默认配置文件"""
        self.save_config()
        print(f"✅ 已创建默认配置文件: {self.config_file}")


class QualityAlert:
    """质量报警类"""

    def __init__(self, alert_type: str, message: str, severity: str = "warning"):
        """
        初始化质量报警

        Args:
            alert_type: 报警类型
            message: 报警消息
            severity: 严重程度 (info, warning, error, critical)
        """
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = datetime.now()

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "alert_type": self.alert_type,
            "message": self.message,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat(),
        }


class AlertManager:
    """报警管理器"""

    def __init__(self, config: AlertConfig):
        """
        初始化报警管理器

        Args:
            config: 报警配置
        """
        self.config = config
        self.alert_history_file = Path("alert_history.json")
        self.alert_history = self._load_alert_history()

    def _load_alert_history(self) -> list[dict]:
        """加载报警历史"""
        if self.alert_history_file.exists():
            try:
                with open(self.alert_history_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_alert_history(self) -> None:
        """保存报警历史"""
        try:
            with open(self.alert_history_file, "w", encoding="utf-8") as f:
                json.dump(self.alert_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存报警历史失败: {e}")

    def _should_send_alert(self, alert: QualityAlert) -> bool:
        """检查是否应该发送报警（避免重复报警）"""
        cooldown = self.config.config.get("alert_cooldown", 3600)
        cutoff_time = datetime.now().timestamp() - cooldown

        # 检查最近是否有相同类型的报警
        for history_item in self.alert_history:
            if (
                history_item.get("alert_type") == alert.alert_type
                and datetime.fromisoformat(
                    history_item.get("timestamp", "")
                ).timestamp()
                > cutoff_time
            ):
                return False

        return True

    def send_email_alert(self, alert: QualityAlert) -> bool:
        """发送邮件报警"""
        email_config = self.config.config["notifications"]["email"]
        if not email_config.get("enabled", False):
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = email_config["from_email"]
            msg["To"] = ", ".join(email_config["to_emails"])
            msg["Subject"] = f"MiniCRM 代码质量报警 - {alert.severity.upper()}"

            # 邮件内容
            body = f"""
代码质量报警通知

报警类型: {alert.alert_type}
严重程度: {alert.severity.upper()}
时间: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

详细信息:
{alert.message}

请及时处理相关问题。

---
MiniCRM 代码质量监控系统
"""

            msg.attach(MIMEText(body, "plain", "utf-8"))

            # 发送邮件
            server = smtplib.SMTP(
                email_config["smtp_server"], email_config["smtp_port"]
            )
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()

            print(f"📧 邮件报警已发送: {alert.alert_type}")
            return True

        except Exception as e:
            print(f"❌ 发送邮件报警失败: {e}")
            return False

    def send_slack_alert(self, alert: QualityAlert) -> bool:
        """发送Slack报警"""
        if not requests:
            print("❌ 需要安装requests库才能发送Slack通知")
            return False

        slack_config = self.config.config["notifications"]["slack"]
        if not slack_config.get("enabled", False):
            return False

        try:
            # Slack消息格式
            severity_colors = {
                "info": "#36a64f",
                "warning": "#ff9500",
                "error": "#ff0000",
                "critical": "#8b0000",
            }

            payload = {
                "channel": slack_config.get("channel", "#code-quality"),
                "username": "MiniCRM Quality Bot",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "color": severity_colors.get(alert.severity, "#ff9500"),
                        "title": f"代码质量报警 - {alert.severity.upper()}",
                        "fields": [
                            {
                                "title": "报警类型",
                                "value": alert.alert_type,
                                "short": True,
                            },
                            {
                                "title": "时间",
                                "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                "short": True,
                            },
                            {
                                "title": "详细信息",
                                "value": alert.message,
                                "short": False,
                            },
                        ],
                        "footer": "MiniCRM 代码质量监控系统",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ],
            }

            response = requests.post(slack_config["webhook_url"], json=payload)
            response.raise_for_status()

            print(f"💬 Slack报警已发送: {alert.alert_type}")
            return True

        except Exception as e:
            print(f"❌ 发送Slack报警失败: {e}")
            return False

    def send_webhook_alert(self, alert: QualityAlert) -> bool:
        """发送Webhook报警"""
        if not requests:
            print("❌ 需要安装requests库才能发送Webhook通知")
            return False

        webhook_config = self.config.config["notifications"]["webhook"]
        if not webhook_config.get("enabled", False):
            return False

        try:
            payload = {
                "alert_type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity,
                "timestamp": alert.timestamp.isoformat(),
                "project": "MiniCRM",
            }

            headers = webhook_config.get("headers", {})
            headers.setdefault("Content-Type", "application/json")

            response = requests.post(
                webhook_config["url"], json=payload, headers=headers
            )
            response.raise_for_status()

            print(f"🔗 Webhook报警已发送: {alert.alert_type}")
            return True

        except Exception as e:
            print(f"❌ 发送Webhook报警失败: {e}")
            return False

    def send_alert(self, alert: QualityAlert) -> bool:
        """发送报警通知"""
        if not self._should_send_alert(alert):
            print(f"⏰ 跳过重复报警: {alert.alert_type}")
            return False

        print(f"🚨 发送报警: {alert.alert_type} ({alert.severity})")

        # 记录到历史
        self.alert_history.append(alert.to_dict())
        self._save_alert_history()

        # 发送通知
        success = False
        if self.send_email_alert(alert):
            success = True
        if self.send_slack_alert(alert):
            success = True
        if self.send_webhook_alert(alert):
            success = True

        return success


class QualityAlertSystem:
    """质量报警系统"""

    def __init__(self, config_file: str = "alert_config.json"):
        """
        初始化质量报警系统

        Args:
            config_file: 配置文件路径
        """
        self.config = AlertConfig(config_file)
        self.alert_manager = AlertManager(self.config)

    def check_quality_metrics(
        self, metrics_file: str = "quality_metrics.json"
    ) -> list[QualityAlert]:
        """
        检查质量指标并生成报警

        Args:
            metrics_file: 质量指标文件路径

        Returns:
            生成的报警列表
        """
        alerts = []

        try:
            with open(metrics_file, encoding="utf-8") as f:
                data = json.load(f)
                history = data.get("history", [])

            if not history:
                return alerts

            # 获取最新指标
            latest_metrics = history[-1]
            thresholds = self.config.config["thresholds"]

            # 检查各项指标
            if latest_metrics.get("ruff_issues", 0) > thresholds["ruff_issues"]:
                alerts.append(
                    QualityAlert(
                        "ruff_issues",
                        f"Ruff问题数量过多: {latest_metrics['ruff_issues']} > {thresholds['ruff_issues']}",
                        "warning",
                    )
                )

            if latest_metrics.get("mypy_errors", 0) > thresholds["mypy_errors"]:
                alerts.append(
                    QualityAlert(
                        "mypy_errors",
                        f"MyPy错误数量过多: {latest_metrics['mypy_errors']} > {thresholds['mypy_errors']}",
                        "error",
                    )
                )

            if (
                latest_metrics.get("file_size_violations", 0)
                > thresholds["file_size_violations"]
            ):
                alerts.append(
                    QualityAlert(
                        "file_size_violations",
                        f"文件大小违规过多: {latest_metrics['file_size_violations']} > {thresholds['file_size_violations']}",
                        "warning",
                    )
                )

            if (
                latest_metrics.get("transfunctions_violations", 0)
                > thresholds["transfunctions_violations"]
            ):
                alerts.append(
                    QualityAlert(
                        "transfunctions_violations",
                        f"Transfunctions违规过多: {latest_metrics['transfunctions_violations']} > {thresholds['transfunctions_violations']}",
                        "warning",
                    )
                )

            if (
                latest_metrics.get("coverage_percentage", 0)
                < thresholds["min_coverage"]
            ):
                alerts.append(
                    QualityAlert(
                        "low_coverage",
                        f"代码覆盖率过低: {latest_metrics['coverage_percentage']:.1f}% < {thresholds['min_coverage']}%",
                        "error",
                    )
                )

            # 计算质量评分
            quality_score = self._calculate_quality_score(latest_metrics)
            if quality_score < thresholds["min_quality_score"]:
                alerts.append(
                    QualityAlert(
                        "low_quality_score",
                        f"整体质量评分过低: {quality_score:.1f} < {thresholds['min_quality_score']}",
                        "critical",
                    )
                )

        except Exception as e:
            alerts.append(
                QualityAlert("system_error", f"检查质量指标时出错: {e}", "error")
            )

        return alerts

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

    def run_alert_check(self) -> None:
        """运行报警检查"""
        print("🔔 开始质量报警检查...")

        alerts = self.check_quality_metrics()

        if not alerts:
            print("✅ 所有质量指标正常，无需报警")
            return

        print(f"⚠️  发现 {len(alerts)} 个质量问题:")
        for alert in alerts:
            print(f"   - {alert.alert_type}: {alert.message}")
            self.alert_manager.send_alert(alert)

    def setup_config(self) -> None:
        """设置报警配置"""
        print("🔧 设置质量报警配置...")

        # 创建默认配置
        if not self.config.config_file.exists():
            self.config.create_default_config()

        print(f"📝 请编辑配置文件: {self.config.config_file}")
        print("配置项说明:")
        print("- thresholds: 各项质量指标的报警阈值")
        print("- notifications.email: 邮件通知配置")
        print("- notifications.slack: Slack通知配置")
        print("- notifications.webhook: Webhook通知配置")
        print("- alert_cooldown: 报警冷却时间（秒）")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM 代码质量报警系统")
    parser.add_argument("--config", default="alert_config.json", help="报警配置文件")
    parser.add_argument("--setup", action="store_true", help="设置报警配置")
    parser.add_argument("--test", action="store_true", help="发送测试报警")

    args = parser.parse_args()

    alert_system = QualityAlertSystem(args.config)

    if args.setup:
        alert_system.setup_config()
    elif args.test:
        # 发送测试报警
        test_alert = QualityAlert(
            "test_alert",
            "这是一个测试报警，用于验证报警系统是否正常工作。",
            "info",
        )
        alert_system.alert_manager.send_alert(test_alert)
    else:
        alert_system.run_alert_check()


if __name__ == "__main__":
    main()
