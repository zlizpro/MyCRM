#!/usr/bin/env python3
"""中文标点符号修复脚本

自动检测和修复Python代码中的中文标点符号，将其替换为对应的英文标点符号。
支持批量处理多个文件，并提供详细的修复报告。

主要功能:
- 自动检测中文标点符号
- 批量替换为英文标点符号
- 生成修复报告
- 验证修复后的语法正确性
"""

import ast
from pathlib import Path
import sys
from typing import Dict, List, Tuple


class ChinesePunctuationFixer:
    """中文标点符号修复器"""

    # 中文标点符号到英文标点符号的映射
    PUNCTUATION_MAP = {
        "，": ",",  # 中文逗号 -> 英文逗号
        "。": ".",  # 中文句号 -> 英文句号
        "；": ";",  # 中文分号 -> 英文分号
        "：": ":",  # 中文冒号 -> 英文冒号
        "？": "?",  # 中文问号 -> 英文问号
        "！": "!",  # 中文感叹号 -> 英文感叹号
        "（": "(",  # 中文左括号 -> 英文左括号
        "）": ")",  # 中文右括号 -> 英文右括号
        "【": "[",  # 中文左方括号 -> 英文左方括号
        "】": "]",  # 中文右方括号 -> 英文右方括号
        "《": "<",  # 中文左书名号 -> 英文小于号
        "》": ">",  # 中文右书名号 -> 英文大于号
        '"': '"',  # 中文左双引号 -> 英文双引号
        '"': '"',  # 中文右双引号 -> 英文双引号
        """: "'",  # 中文左单引号 -> 英文单引号
        """: "'",  # 中文右单引号 -> 英文单引号
    }

    def __init__(self):
        """初始化修复器"""
        self.fixes_applied = []
        self.files_processed = []

    def detect_chinese_punctuation(self, content: str) -> List[Tuple[int, str, str]]:
        """检测文本中的中文标点符号

        Args:
            content: 文件内容

        Returns:
            List[Tuple[int, str, str]]: (行号, 中文标点, 英文标点) 的列表
        """
        issues = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for chinese_punct, english_punct in self.PUNCTUATION_MAP.items():
                if chinese_punct in line:
                    issues.append((line_num, chinese_punct, english_punct))

        return issues

    def fix_content(self, content: str) -> Tuple[str, List[Dict]]:
        """修复文件内容中的中文标点符号

        Args:
            content: 原始文件内容

        Returns:
            Tuple[str, List[Dict]]: (修复后的内容, 修复记录列表)
        """
        fixed_content = content
        fixes = []

        for chinese_punct, english_punct in self.PUNCTUATION_MAP.items():
            if chinese_punct in fixed_content:
                # 计算替换次数
                count = fixed_content.count(chinese_punct)
                if count > 0:
                    fixed_content = fixed_content.replace(chinese_punct, english_punct)
                    fixes.append(
                        {
                            "chinese": chinese_punct,
                            "english": english_punct,
                            "count": count,
                        }
                    )

        return fixed_content, fixes

    def validate_syntax(self, content: str, file_path: str) -> Tuple[bool, str]:
        """验证Python代码语法正确性

        Args:
            content: Python代码内容
            file_path: 文件路径

        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, f"语法错误 (行 {e.lineno}): {e.msg}"
        except Exception as e:
            return False, f"解析错误: {e!s}"

    def fix_file(self, file_path: Path) -> Dict:
        """修复单个文件

        Args:
            file_path: 文件路径

        Returns:
            Dict: 修复结果
        """
        try:
            # 读取原始文件
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            # 检测中文标点符号
            issues = self.detect_chinese_punctuation(original_content)

            if not issues:
                return {
                    "file": str(file_path),
                    "status": "no_issues",
                    "message": "未发现中文标点符号问题",
                    "fixes": [],
                }

            # 修复内容
            fixed_content, fixes = self.fix_content(original_content)

            # 验证语法
            is_valid, error_msg = self.validate_syntax(fixed_content, str(file_path))

            if not is_valid:
                return {
                    "file": str(file_path),
                    "status": "syntax_error",
                    "message": f"修复后语法错误: {error_msg}",
                    "fixes": fixes,
                }

            # 写入修复后的文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_content)

            self.files_processed.append(str(file_path))
            self.fixes_applied.extend(fixes)

            return {
                "file": str(file_path),
                "status": "fixed",
                "message": f"成功修复 {len(fixes)} 种中文标点符号",
                "fixes": fixes,
                "issues_detected": len(issues),
            }

        except Exception as e:
            return {
                "file": str(file_path),
                "status": "error",
                "message": f"处理文件时出错: {e!s}",
                "fixes": [],
            }

    def fix_files(self, file_paths: List[Path]) -> Dict:
        """批量修复多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            Dict: 批量修复结果
        """
        results = []

        for file_path in file_paths:
            if file_path.suffix == ".py" and file_path.exists():
                result = self.fix_file(file_path)
                results.append(result)

        # 统计结果
        fixed_count = sum(1 for r in results if r["status"] == "fixed")
        error_count = sum(1 for r in results if r["status"] == "error")
        no_issues_count = sum(1 for r in results if r["status"] == "no_issues")
        syntax_error_count = sum(1 for r in results if r["status"] == "syntax_error")

        return {
            "results": results,
            "summary": {
                "total_files": len(results),
                "fixed": fixed_count,
                "no_issues": no_issues_count,
                "syntax_errors": syntax_error_count,
                "errors": error_count,
            },
        }

    def generate_report(self, results: Dict) -> str:
        """生成修复报告

        Args:
            results: 修复结果

        Returns:
            str: 格式化的报告
        """
        report = []
        report.append("=" * 60)
        report.append("中文标点符号修复报告")
        report.append("=" * 60)
        report.append("")

        # 总结
        summary = results["summary"]
        report.append("修复总结:")
        report.append(f"  总文件数: {summary['total_files']}")
        report.append(f"  成功修复: {summary['fixed']}")
        report.append(f"  无需修复: {summary['no_issues']}")
        report.append(f"  语法错误: {summary['syntax_errors']}")
        report.append(f"  处理错误: {summary['errors']}")
        report.append("")

        # 详细结果
        report.append("详细结果:")
        for result in results["results"]:
            report.append(f"  文件: {result['file']}")
            report.append(f"    状态: {result['status']}")
            report.append(f"    信息: {result['message']}")

            if result["fixes"]:
                report.append("    修复详情:")
                for fix in result["fixes"]:
                    report.append(
                        f"      '{fix['chinese']}' -> '{fix['english']}' ({fix['count']} 处)"
                    )

            report.append("")

        return "\n".join(report)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python fix_chinese_punctuation.py <文件路径1> [文件路径2] ...")
        print(
            "示例: python fix_chinese_punctuation.py src/minicrm/data/dao/enhanced_customer_dao.py"
        )
        sys.exit(1)

    # 获取文件路径
    file_paths = [Path(path) for path in sys.argv[1:]]

    # 验证文件存在
    for file_path in file_paths:
        if not file_path.exists():
            print(f"错误: 文件不存在 - {file_path}")
            sys.exit(1)

    # 创建修复器并执行修复
    fixer = ChinesePunctuationFixer()
    results = fixer.fix_files(file_paths)

    # 生成并显示报告
    report = fixer.generate_report(results)
    print(report)

    # 保存报告到文件
    report_file = Path("chinese_punctuation_fix_report.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"详细报告已保存到: {report_file}")


if __name__ == "__main__":
    main()
