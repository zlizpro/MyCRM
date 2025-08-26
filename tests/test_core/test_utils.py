"""
工具函数测试模块

测试MiniCRM工具函数的功能和正确性。
"""

import tempfile
import unittest
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from src.minicrm.core.exceptions import ValidationError
from src.minicrm.core.utils import (
    calculate_age_in_days,
    dict_get_nested,
    # 文件操作函数
    ensure_directory_exists,
    format_currency,
    format_date,
    format_file_size,
    # 格式化函数
    format_phone_number,
    generate_hash_id,
    # ID生成函数
    generate_id,
    generate_sequence_id,
    get_current_timestamp,
    get_file_extension,
    is_valid_file_extension,
    mask_sensitive_data,
    normalize_whitespace,
    # 日期时间处理函数
    parse_date,
    safe_float,
    # 数据转换函数
    safe_int,
    safe_str,
    sanitize_filename,
    # 字符串处理函数
    truncate_text,
    # 数据验证函数
    validate_email,
    validate_phone_number,
    validate_required_fields,
    validate_text_length,
)


class TestDataValidation(unittest.TestCase):
    """测试数据验证函数"""

    def test_validate_email_valid(self):
        """测试有效邮箱验证"""
        valid_emails = [
            "user@example.com",
            "test.email@domain.co.uk",
            "user+tag@example.org",
            "123@test.com",
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(validate_email(email))

    def test_validate_email_invalid(self):
        """测试无效邮箱验证"""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            None,
            123,
        ]

        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(validate_email(email))

    def test_validate_phone_number_valid(self):
        """测试有效手机号验证"""
        valid_phones = ["13812345678", "15987654321", "18666666666", "19123456789"]

        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(validate_phone_number(phone))

    def test_validate_phone_number_invalid(self):
        """测试无效手机号验证"""
        invalid_phones = [
            "",
            "12345678901",  # 以1开头但第二位不是3-9
            "1234567890",  # 长度不够
            "138123456789",  # 长度过长
            "abc12345678",  # 包含字母
            None,
            123,
        ]

        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(validate_phone_number(phone))

    def test_validate_required_fields_success(self):
        """测试必填字段验证 - 成功"""
        data = {"name": "张三", "phone": "13812345678", "email": "zhangsan@example.com"}
        required_fields = ["name", "phone"]

        # 不应该抛出异常
        validate_required_fields(data, required_fields)

    def test_validate_required_fields_missing(self):
        """测试必填字段验证 - 缺失字段"""
        data = {
            "name": "张三",
            "phone": "",  # 空值
        }
        required_fields = ["name", "phone", "email"]

        with self.assertRaises(ValidationError) as context:
            validate_required_fields(data, required_fields)

        error = context.exception
        self.assertEqual(error.error_code, "REQUIRED_FIELDS_MISSING")
        self.assertIn("missing_fields", error.details)

    def test_validate_text_length_success(self):
        """测试文本长度验证 - 成功"""
        text = "这是一个测试文本"

        # 不应该抛出异常
        validate_text_length(text, max_length=50)

    def test_validate_text_length_too_long(self):
        """测试文本长度验证 - 超长"""
        text = "这是一个很长的测试文本" * 10

        with self.assertRaises(ValidationError) as context:
            validate_text_length(text, max_length=10, field_name="测试字段")

        error = context.exception
        self.assertEqual(error.error_code, "TEXT_TOO_LONG")
        self.assertIn("测试字段", error.message)


class TestFormatting(unittest.TestCase):
    """测试格式化函数"""

    def test_format_phone_number_valid(self):
        """测试手机号格式化 - 有效号码"""
        test_cases = [
            ("13812345678", "138-1234-5678"),
            ("138 1234 5678", "138-1234-5678"),
            ("138-1234-5678", "138-1234-5678"),
        ]

        for input_phone, expected in test_cases:
            with self.subTest(input_phone=input_phone):
                result = format_phone_number(input_phone)
                self.assertEqual(result, expected)

    def test_format_phone_number_invalid(self):
        """测试手机号格式化 - 无效号码"""
        invalid_phones = ["", "123", "abcdefghijk", None]

        for phone in invalid_phones:
            with self.subTest(phone=phone):
                result = format_phone_number(phone)
                # 无效号码应该返回原始值或空字符串
                if phone is None:
                    self.assertEqual(result, "")
                else:
                    self.assertEqual(result, phone)

    def test_format_currency_various_types(self):
        """测试货币格式化 - 各种类型"""
        test_cases = [
            (1234.56, "¥1,234.56"),
            (1000000, "¥1,000,000.00"),
            ("1234.56", "¥1,234.56"),
            (Decimal("1234.56"), "¥1,234.56"),
            (0, "¥0.00"),
        ]

        for amount, expected in test_cases:
            with self.subTest(amount=amount):
                result = format_currency(amount)
                self.assertEqual(result, expected)

    def test_format_currency_invalid(self):
        """测试货币格式化 - 无效输入"""
        invalid_amounts = [None, "abc", ""]

        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                result = format_currency(amount)
                if amount is None:
                    self.assertEqual(result, "")
                else:
                    self.assertEqual(result, str(amount))

    def test_format_date_various_formats(self):
        """测试日期格式化 - 各种格式"""
        test_date = datetime(2025, 1, 15, 14, 30, 0)

        test_cases = [
            ("default", "2025-01-15"),
            ("display", "2025年01月15日"),
            ("datetime", "2025-01-15 14:30:00"),
            ("datetime_display", "2025年01月15日 14:30:00"),
            ("time", "14:30:00"),
        ]

        for format_type, expected in test_cases:
            with self.subTest(format_type=format_type):
                result = format_date(test_date, format_type)
                self.assertEqual(result, expected)

    def test_format_file_size(self):
        """测试文件大小格式化"""
        test_cases = [
            (0, "0 B"),
            (1024, "1.00 KB"),
            (1048576, "1.00 MB"),
            (1073741824, "1.00 GB"),
            (1500, "1.46 KB"),
        ]

        for size_bytes, expected in test_cases:
            with self.subTest(size_bytes=size_bytes):
                result = format_file_size(size_bytes)
                self.assertEqual(result, expected)


class TestDateTimeProcessing(unittest.TestCase):
    """测试日期时间处理函数"""

    def test_parse_date_various_formats(self):
        """测试日期解析 - 各种格式"""
        test_cases = [
            ("2025-01-15", datetime(2025, 1, 15)),
            ("2025/01/15", datetime(2025, 1, 15)),
            ("2025年01月15日", datetime(2025, 1, 15)),
            ("2025-01-15 14:30:00", datetime(2025, 1, 15, 14, 30, 0)),
        ]

        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = parse_date(date_str)
                self.assertEqual(result, expected)

    def test_parse_date_invalid(self):
        """测试日期解析 - 无效格式"""
        invalid_dates = ["", "invalid", "2025-13-01", None, 123]

        for date_str in invalid_dates:
            with self.subTest(date_str=date_str):
                result = parse_date(date_str)
                self.assertIsNone(result)

    def test_get_current_timestamp(self):
        """测试获取当前时间戳"""
        timestamp = get_current_timestamp()

        # 验证格式 YYYYMMDD_HHMMSS
        self.assertRegex(timestamp, r"^\d{8}_\d{6}$")

    def test_calculate_age_in_days(self):
        """测试计算天数差"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 15)

        result = calculate_age_in_days(start_date, end_date)
        self.assertEqual(result, 14)

        # 测试datetime对象
        start_datetime = datetime(2025, 1, 1, 10, 0, 0)
        end_datetime = datetime(2025, 1, 15, 15, 30, 0)

        result = calculate_age_in_days(start_datetime, end_datetime)
        self.assertEqual(result, 14)


class TestIDGeneration(unittest.TestCase):
    """测试ID生成函数"""

    def test_generate_id_with_prefix(self):
        """测试带前缀的ID生成"""
        prefix = "CUST"
        length = 6

        result = generate_id(prefix, length)

        self.assertTrue(result.startswith(prefix))
        self.assertEqual(len(result), len(prefix) + length)

    def test_generate_id_without_prefix(self):
        """测试不带前缀的ID生成"""
        length = 8

        result = generate_id(length=length)

        self.assertEqual(len(result), length)
        self.assertTrue(result.isalnum())

    def test_generate_sequence_id(self):
        """测试序列ID生成"""
        test_cases = [
            ("Q", 1, 6, "Q000001"),
            ("CUST", 123, 4, "CUST0123"),
            ("", 99, 3, "099"),
        ]

        for prefix, seq_num, length, expected in test_cases:
            with self.subTest(prefix=prefix, seq_num=seq_num):
                result = generate_sequence_id(prefix, seq_num, length)
                self.assertEqual(result, expected)

    def test_generate_hash_id(self):
        """测试哈希ID生成"""
        data = "test_data"
        length = 8

        result = generate_hash_id(data, length)

        self.assertEqual(len(result), length)
        self.assertTrue(result.isalnum())

        # 相同数据应该生成相同的哈希
        result2 = generate_hash_id(data, length)
        self.assertEqual(result, result2)


class TestFileOperations(unittest.TestCase):
    """测试文件操作函数"""

    def test_ensure_directory_exists(self):
        """测试确保目录存在"""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test" / "nested" / "directory"

            result = ensure_directory_exists(test_dir)

            self.assertTrue(result.exists())
            self.assertTrue(result.is_dir())
            self.assertEqual(result, test_dir)

    def test_sanitize_filename(self):
        """测试文件名清理"""
        test_cases = [
            ("客户报表<2025-01-15>.xlsx", "客户报表_2025-01-15_.xlsx"),
            ("file/with\\bad:chars", "file_with_bad_chars"),
            ("normal_filename.txt", "normal_filename.txt"),
            ("", "untitled"),
            ("   ", "untitled"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        test_cases = [
            ("document.pdf", ".pdf"),
            ("archive.tar.gz", ".gz"),
            ("file", ""),
            ("file.TXT", ".txt"),  # 应该转换为小写
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = get_file_extension(filename)
                self.assertEqual(result, expected)

    def test_is_valid_file_extension(self):
        """测试文件扩展名验证"""
        allowed_extensions = [".pdf", ".docx", ".xlsx"]

        valid_files = ["document.pdf", "report.docx", "data.xlsx"]
        invalid_files = ["file.txt", "image.jpg", "archive.zip"]

        for filename in valid_files:
            with self.subTest(filename=filename):
                self.assertTrue(is_valid_file_extension(filename, allowed_extensions))

        for filename in invalid_files:
            with self.subTest(filename=filename):
                self.assertFalse(is_valid_file_extension(filename, allowed_extensions))


class TestStringProcessing(unittest.TestCase):
    """测试字符串处理函数"""

    def test_truncate_text(self):
        """测试文本截断"""
        test_cases = [
            ("这是一个很长的文本内容", 10, "这是一个很长的文...", "..."),
            ("短文本", 10, "短文本", "..."),
            ("", 10, "", "..."),
            ("正好十个字符的文本", 10, "正好十个字符的文本", "..."),
        ]

        for text, max_len, expected, suffix in test_cases:
            with self.subTest(text=text):
                result = truncate_text(text, max_len, suffix)
                self.assertEqual(result, expected)

    def test_normalize_whitespace(self):
        """测试空白字符标准化"""
        test_cases = [
            ("  hello   world  \n\t  ", "hello world"),
            ("normal text", "normal text"),
            ("", ""),
            ("   ", ""),
            ("multiple\n\nlines\t\twith\r\nspaces", "multiple lines with spaces"),
        ]

        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = normalize_whitespace(input_text)
                self.assertEqual(result, expected)

    def test_mask_sensitive_data(self):
        """测试敏感数据遮蔽"""
        test_cases = [
            ("13812345678", "138****5678", "*", 4),
            ("user@example.com", "us*****com", "*", 4),
            ("short", "short", "*", 4),  # 太短不遮蔽
            ("1234567890", "12****7890", "*", 4),
        ]

        for data, expected, mask_char, visible_chars in test_cases:
            with self.subTest(data=data):
                result = mask_sensitive_data(data, mask_char, visible_chars)
                self.assertEqual(result, expected)


class TestDataConversion(unittest.TestCase):
    """测试数据转换函数"""

    def test_safe_int(self):
        """测试安全整数转换"""
        test_cases = [
            ("123", 123, 0),
            (123.45, 123, 0),
            ("abc", 0, 0),
            (None, 5, 5),
            ("", 10, 10),
        ]

        for value, expected, default in test_cases:
            with self.subTest(value=value):
                result = safe_int(value, default)
                self.assertEqual(result, expected)

    def test_safe_float(self):
        """测试安全浮点数转换"""
        test_cases = [
            ("123.45", 123.45, 0.0),
            (123, 123.0, 0.0),
            ("abc", 0.0, 0.0),
            (None, 5.5, 5.5),
            ("", 10.0, 10.0),
        ]

        for value, expected, default in test_cases:
            with self.subTest(value=value):
                result = safe_float(value, default)
                self.assertEqual(result, expected)

    def test_safe_str(self):
        """测试安全字符串转换"""
        test_cases = [
            (123, "123", ""),
            (None, "N/A", "N/A"),
            ("", "", "default"),
            (123.45, "123.45", ""),
        ]

        for value, expected, default in test_cases:
            with self.subTest(value=value):
                result = safe_str(value, default)
                self.assertEqual(result, expected)

    def test_dict_get_nested(self):
        """测试嵌套字典取值"""
        data = {
            "user": {
                "profile": {"name": "张三", "age": 30},
                "settings": {"theme": "dark"},
            }
        }

        test_cases = [
            ("user.profile.name", "张三"),
            ("user.profile.age", 30),
            ("user.settings.theme", "dark"),
            ("user.profile.email", None),  # 不存在的键
            ("nonexistent.key", None),  # 不存在的路径
            ("user.profile.nonexistent", "default"),  # 使用默认值
        ]

        for key_path, expected in test_cases:
            with self.subTest(key_path=key_path):
                if expected == "default":
                    result = dict_get_nested(data, key_path, "default")
                    self.assertEqual(result, "default")
                else:
                    result = dict_get_nested(data, key_path)
                    self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
