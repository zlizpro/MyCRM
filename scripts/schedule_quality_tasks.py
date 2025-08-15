#!/usr/bin/env python3
"""
MiniCRM 质量任务调度器

定期运行质量监控、报警检查和报告生成任务。
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class QualityTaskScheduler:
    """质量任务调度器"""

    def __init__(self):
        """初始化调度器"""
        self.project_root = Path.cwd()
        self.last_run_file = Path("last_quality_run.txt")
        self.tasks = {
            "monitor": {
                "script": "scripts/quality_monitor.py",
                "interval": 3600,  # 1小时
                "description": "质量监控",
            },
            "alerts": {
                "script": "scripts/quality_alerts.py",
                "interval": 1800,  # 30分钟
                "description": "质量报警检查",
            },
            "daily_report": {
                "script": "scripts/quality_reporter.py --type daily",
                "interval": 86400,  # 24小时
                "description": "每日质量报告",
            },
            "weekly_report": {
                "script": "scripts/quality_reporter.py --type weekly",
                "interval": 604800,  # 7天
                "description": "每周质量报告",
            },
            "monthly_report": {
                "script": "scripts/quality_reporter.py --type monthly",
                "interval": 2592000,  # 30天
                "description": "每月质量报告",
            },
        }

    def load_last_run_times(self) -> dict[str, float]:
        """加载上次运行时间"""
        if not self.last_run_file.exists():
            return {}

        try:
            with open(self.last_run_file) as f:
                lines = f.readlines()
                return {
                    line.split(":")[0]: float(line.split(":")[1].strip())
                    for line in lines
                    if ":" in line
                }
        except Exception:
            return {}

    def save_last_run_times(self, run_times: dict[str, float]) -> None:
        """保存上次运行时间"""
        try:
            with open(self.last_run_file, "w") as f:
                for task, timestamp in run_times.items():
                    f.write(f"{task}:{timestamp}\n")
        except Exception as e:
            print(f"❌ 保存运行时间失败: {e}")

    def should_run_task(self, task_name: str, last_run_times: dict[str, float]) -> bool:
        """检查任务是否应该运行"""
        if task_name not in last_run_times:
            return True

        last_run = last_run_times[task_name]
        interval = self.tasks[task_name]["interval"]
        return time.time() - last_run >= interval

    def run_task(self, task_name: str) -> bool:
        """运行指定任务"""
        task_config = self.tasks[task_name]
        script = task_config["script"]
        description = task_config["description"]

        print(f"🚀 运行任务: {description}")

        try:
            # 分割命令和参数
            cmd_parts = script.split()
            if cmd_parts[0].endswith(".py"):
                cmd_parts = ["python"] + cmd_parts

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
            )

            if result.returncode == 0:
                print(f"✅ 任务完成: {description}")
                if result.stdout:
                    print(f"输出: {result.stdout[:200]}...")
                return True
            else:
                print(f"❌ 任务失败: {description}")
                print(f"错误: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"⏰ 任务超时: {description}")
            return False
        except Exception as e:
            print(f"❌ 运行任务时出错: {e}")
            return False

    def run_scheduler_cycle(self) -> None:
        """运行一次调度周期"""
        print(f"🔄 开始质量任务调度 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        last_run_times = self.load_last_run_times()
        current_time = time.time()

        for task_name, task_config in self.tasks.items():
            if self.should_run_task(task_name, last_run_times):
                if self.run_task(task_name):
                    last_run_times[task_name] = current_time

        self.save_last_run_times(last_run_times)
        print("✅ 调度周期完成\n")

    def run_continuous_scheduler(self, check_interval: int = 300) -> None:
        """运行持续调度器"""
        print("🔄 启动持续质量任务调度器")
        print(f"检查间隔: {check_interval} 秒")
        print("任务配置:")
        for task_name, task_config in self.tasks.items():
            interval_hours = task_config["interval"] / 3600
            print(f"  - {task_config['description']}: 每 {interval_hours} 小时")

        try:
            while True:
                self.run_scheduler_cycle()
                print(f"⏰ 等待 {check_interval} 秒后进行下次检查...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\n👋 调度器已停止")

    def show_task_status(self) -> None:
        """显示任务状态"""
        print("📊 质量任务状态")
        print("=" * 60)

        last_run_times = self.load_last_run_times()
        current_time = time.time()

        for task_name, task_config in self.tasks.items():
            description = task_config["description"]
            interval = task_config["interval"]

            if task_name in last_run_times:
                last_run = last_run_times[task_name]
                time_since_last = current_time - last_run
                next_run_in = max(0, interval - time_since_last)

                last_run_str = datetime.fromtimestamp(last_run).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                next_run_str = (
                    datetime.fromtimestamp(current_time + next_run_in).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if next_run_in > 0
                    else "现在"
                )

                status = "⏰ 等待中" if next_run_in > 0 else "🚀 准备运行"
            else:
                last_run_str = "从未运行"
                next_run_str = "现在"
                status = "🚀 准备运行"

            print(f"任务: {description}")
            print(f"  上次运行: {last_run_str}")
            print(f"  下次运行: {next_run_str}")
            print(f"  状态: {status}")
            print()

    def run_specific_task(self, task_name: str) -> None:
        """运行指定的任务"""
        if task_name not in self.tasks:
            print(f"❌ 未知任务: {task_name}")
            print(f"可用任务: {', '.join(self.tasks.keys())}")
            return

        print(f"🚀 手动运行任务: {task_name}")
        success = self.run_task(task_name)

        if success:
            # 更新运行时间
            last_run_times = self.load_last_run_times()
            last_run_times[task_name] = time.time()
            self.save_last_run_times(last_run_times)


def create_systemd_service() -> None:
    """创建systemd服务文件（Linux）"""
    service_content = f"""[Unit]
Description=MiniCRM Quality Task Scheduler
After=network.target

[Service]
Type=simple
User={os.getenv("USER", "minicrm")}
WorkingDirectory={Path.cwd()}
ExecStart={sys.executable} {Path.cwd() / "scripts/schedule_quality_tasks.py"} --continuous
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""

    service_file = Path("/etc/systemd/system/minicrm-quality.service")
    print(f"创建systemd服务文件: {service_file}")
    print("请以root权限运行以下命令:")
    print(f"sudo tee {service_file} << 'EOF'")
    print(service_content)
    print("EOF")
    print("sudo systemctl daemon-reload")
    print("sudo systemctl enable minicrm-quality.service")
    print("sudo systemctl start minicrm-quality.service")


def create_cron_job() -> None:
    """创建cron任务"""
    script_path = Path.cwd() / "scripts/schedule_quality_tasks.py"
    cron_entry = f"*/5 * * * * cd {Path.cwd()} && {sys.executable} {script_path} --once"

    print("创建cron任务:")
    print("运行以下命令添加到crontab:")
    print(f"echo '{cron_entry}' | crontab -")
    print("\n或者手动编辑crontab:")
    print("crontab -e")
    print("然后添加以下行:")
    print(cron_entry)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniCRM 质量任务调度器")
    parser.add_argument("--continuous", action="store_true", help="持续运行调度器")
    parser.add_argument("--once", action="store_true", help="运行一次调度周期")
    parser.add_argument("--status", action="store_true", help="显示任务状态")
    parser.add_argument("--run", help="运行指定任务")
    parser.add_argument("--setup-service", action="store_true", help="设置系统服务")
    parser.add_argument("--setup-cron", action="store_true", help="设置cron任务")
    parser.add_argument("--interval", type=int, default=300, help="检查间隔（秒）")

    args = parser.parse_args()

    scheduler = QualityTaskScheduler()

    if args.setup_service:
        create_systemd_service()
    elif args.setup_cron:
        create_cron_job()
    elif args.status:
        scheduler.show_task_status()
    elif args.run:
        scheduler.run_specific_task(args.run)
    elif args.once:
        scheduler.run_scheduler_cycle()
    elif args.continuous:
        scheduler.run_continuous_scheduler(args.interval)
    else:
        print("请指定操作模式，使用 --help 查看帮助")


if __name__ == "__main__":
    main()
