#!/usr/bin/env python3
"""
Kiro IDE 集成脚本
处理来自Kiro IDE的hook触发请求，执行代码质量检查
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from code_quality_checker import CodeQualityChecker, generate_report


class KiroHookHandler:
    """Kiro IDE Hook处理器"""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.config_path = self.script_dir / "quality_config.json"
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"警告: 无法加载配置文件 {self.config_path}: {e}", file=sys.stderr)
            self.config = self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'check_pep8': True,
            'check_type_hints': True,
            'check_docstrings': True,
            'check_imports': True,
            'max_line_length': 88
        }

    def handle_file_save(self, file_path: str) -> Dict[str, Any]:
        """处理文件保存事件"""
        try:
            path = Path(file_path)

            # 检查文件是否为Python文件
            if path.suffix != '.py':
                return self._create_response("skipped", "非Python文件，跳过检查")

            # 检查文件是否存在
            if not path.exists():
                return self._create_response("error", f"文件不存在: {file_path}")

            # 检查是否在排除列表中
            if self._should_exclude(path):
                return self._create_response("skipped", "文件在排除列表中")

            # 执行质量检查
            checker = CodeQualityChecker(self.config)
            issues = checker.check_file(path)

            # 生成报告
            report_data = {
                'file_path': str(path),
                'total_issues': len(issues),
                'issues_by_severity': {
                    'error': len([i for i in issues if i.severity == 'error']),
                    'warning': len([i for i in issues if i.severity == 'warning']),
                    'info': len([i for i in issues if i.severity == 'info'])
                },
                'auto_fixable_count': len([i for i in issues if i.auto_fixable]),
                'issues': [
                    {
                        'line_number': issue.line_number,
                        'column': issue.column,
                        'issue_type': issue.issue_type,
                        'severity': issue.severity,
                        'message': issue.message,
                        'suggestion': issue.suggestion,
                        'auto_fixable': issue.auto_fixable
                    }
                    for issue in issues
                ]
            }

            return self._create_response("success", "代码质量检查完成", report_data)

        except Exception as e:
            return self._create_response("error", f"检查过程中出错: {str(e)}")

    def handle_manual_trigger(self, files: List[str]) -> Dict[str, Any]:
        """处理手动触发的检查"""
        try:
            all_issues = []
            processed_files = []

            for file_path in files:
                path = Path(file_path)
                if path.suffix == '.py' and path.exists() and not self._should_exclude(path):
                    checker = CodeQualityChecker(self.config)
                    issues = checker.check_file(path)
                    all_issues.extend(issues)
                    processed_files.append(str(path))

            report_data = {
                'processed_files': processed_files,
                'total_files': len(processed_files),
                'total_issues': len(all_issues),
                'issues_by_severity': {
                    'error': len([i for i in all_issues if i.severity == 'error']),
                    'warning': len([i for i in all_issues if i.severity == 'warning']),
                    'info': len([i for i in all_issues if i.severity == 'info'])
                },
                'auto_fixable_count': len([i for i in all_issues if i.auto_fixable]),
                'issues_by_file': {}
            }

            # 按文件分组问题
            for issue in all_issues:
                file_path = issue.file_path
                if file_path not in report_data['issues_by_file']:
                    report_data['issues_by_file'][file_path] = []

                report_data['issues_by_file'][file_path].append({
                    'line_number': issue.line_number,
                    'column': issue.column,
                    'issue_type': issue.issue_type,
                    'severity': issue.severity,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'auto_fixable': issue.auto_fixable
                })

            return self._create_response("success", f"批量检查完成，处理了{len(processed_files)}个文件", report_data)

        except Exception as e:
            return self._create_response("error", f"批量检查过程中出错: {str(e)}")

    def _should_exclude(self, path: Path) -> bool:
        """检查文件是否应该被排除"""
        exclude_patterns = self.config.get('exclude_patterns', [])
        path_str = str(path)

        for pattern in exclude_patterns:
            if pattern in path_str or path.match(pattern):
                return True

        return False

    def _create_response(self, status: str, message: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建标准响应格式"""
        response = {
            'status': status,
            'message': message,
            'timestamp': str(Path(__file__).stat().st_mtime),
            'hook_name': 'code-quality-check'
        }

        if data:
            response['data'] = data

        return response


def main():
    """主函数 - 处理Kiro IDE的调用"""
    if len(sys.argv) < 2:
        print(
            "用法: python kiro_integration.py <command> [args...]", file=sys.stderr)
        sys.exit(1)

    handler = KiroHookHandler()
    command = sys.argv[1]

    try:
        if command == "file_save":
            if len(sys.argv) < 3:
                print("错误: file_save命令需要文件路径参数", file=sys.stderr)
                sys.exit(1)

            file_path = sys.argv[2]
            result = handler.handle_file_save(file_path)

        elif command == "manual":
            files = sys.argv[2:] if len(sys.argv) > 2 else []
            if not files:
                print("错误: manual命令需要至少一个文件路径", file=sys.stderr)
                sys.exit(1)

            result = handler.handle_manual_trigger(files)

        elif command == "test":
            # 测试模式
            test_file = sys.argv[2] if len(sys.argv) > 2 else "test_sample.py"
            result = handler.handle_file_save(test_file)

        else:
            result = {
                'status': 'error',
                'message': f'未知命令: {command}',
                'available_commands': ['file_save', 'manual', 'test']
            }

        # 输出JSON结果
        print(json.dumps(result, ensure_ascii=False, indent=2))

        # 设置退出码
        if result['status'] == 'error':
            sys.exit(1)
        elif result['status'] == 'success' and result.get('data', {}).get('issues_by_severity', {}).get('error', 0) > 0:
            sys.exit(2)  # 有错误级别的问题
        else:
            sys.exit(0)

    except Exception as e:
        error_result = {
            'status': 'error',
            'message': f'处理命令时出错: {str(e)}',
            'command': command
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
