"""DAO异常处理器现代化单元测试

使用pytest风格的现代化测试, 测试DAOExceptionHandler类的各种异常处理功能:
1. 不同类型异常的转换和处理
2. 错误消息格式化
3. 日志记录功能
4. 装饰器模式
5. 便捷函数

确保异常处理器能够正确处理各种异常情况, 并生成标准化的错误消息。
"""

import logging
import sqlite3
from unittest.mock import patch

import pytest

from minicrm.core.exceptions import DatabaseError, ValidationError
from minicrm.data.dao.dao_exception_handler import (
    DAOExceptionHandler,
    dao_exception_handler,
    handle_create_error,
    handle_query_error,
    handle_update_error,
)
from transfunctions import ValidationError as TransValidationError


class TestDAOExceptionHandler:
    """DAO异常处理器测试类"""

    def setup_method(self):
        """测试准备"""
        self.handler = DAOExceptionHandler()
        self.operation = "创建"
        self.entity_type = "客户"
        self.context = {"user_id": 123, "session_id": "abc123"}

    def test_format_error_message(self):
        """测试错误消息格式化"""
        # 测试标准格式
        message = DAOExceptionHandler.format_error_message(
            "创建", "客户", "数据验证失败"
        )
        assert message == "创建客户失败: 数据验证失败"

        # 测试英文操作类型映射
        message = DAOExceptionHandler.format_error_message(
            "create", "customer", "validation failed"
        )
        assert message == "创建客户失败: validation failed"

        # 测试未映射的类型
        message = DAOExceptionHandler.format_error_message(
            "自定义操作", "自定义实体", "错误详情"
        )
        assert message == "自定义操作自定义实体失败: 错误详情"

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_handle_validation_error_trans_validation(self, mock_logger):
        """测试处理TransValidationError"""
        error_msg = "字段不能为空"
        original_error = TransValidationError(error_msg)

        with pytest.raises(ValidationError) as exc_info:
            DAOExceptionHandler.handle_dao_error(
                original_error, self.operation, self.entity_type, self.context
            )

        # 验证异常转换
        raised_error = exc_info.value
        assert isinstance(raised_error, ValidationError)
        assert raised_error.message == "创建客户失败: 字段不能为空"
        assert raised_error.error_code == "客户_VALIDATION_ERROR"
        assert raised_error.details == self.context
        assert raised_error.original_exception == original_error

        # 验证日志记录
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING  # 日志级别

    def test_handle_validation_error_already_validation(self):
        """测试处理已经是ValidationError的异常"""
        error_msg = "已经是验证错误"
        original_error = ValidationError(error_msg)

        with pytest.raises(ValidationError) as exc_info:
            DAOExceptionHandler.handle_dao_error(
                original_error, self.operation, self.entity_type, self.context
            )

        # 验证直接重新抛出
        raised_error = exc_info.value
        assert raised_error is original_error

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_handle_database_error_sqlite(self, mock_logger):
        """测试处理sqlite3.Error"""
        error_msg = "UNIQUE constraint failed"
        original_error = sqlite3.IntegrityError(error_msg)
        sql_info = {"sql": "INSERT INTO customers...", "params": ("test",)}

        with pytest.raises(DatabaseError) as exc_info:
            DAOExceptionHandler.handle_dao_error(
                original_error, self.operation, self.entity_type, self.context, sql_info
            )

        # 验证异常转换
        raised_error = exc_info.value
        assert isinstance(raised_error, DatabaseError)
        assert raised_error.message == "创建客户失败: UNIQUE constraint failed"
        assert raised_error.error_code == "客户_DATABASE_ERROR"
        assert raised_error.details == self.context
        assert raised_error.original_exception == original_error

        # 验证日志记录
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.ERROR  # 日志级别

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_handle_database_error_already_database(self):
        """测试处理已经是DatabaseError的异常"""
        error_msg = "已经是数据库错误"
        original_error = DatabaseError(error_msg)

        with pytest.raises(DatabaseError) as exc_info:
            DAOExceptionHandler.handle_dao_error(
                original_error, self.operation, self.entity_type, self.context
            )

        # 验证直接重新抛出
        raised_error = exc_info.value
        assert raised_error is original_error

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_handle_general_error(self, mock_logger):
        """测试处理通用异常"""
        error_msg = "通用错误"
        original_error = ValueError(error_msg)

        with pytest.raises(DatabaseError) as exc_info:
            DAOExceptionHandler.handle_dao_error(
                original_error, self.operation, self.entity_type, self.context
            )

        # 验证异常转换
        raised_error = exc_info.value
        assert isinstance(raised_error, DatabaseError)
        assert raised_error.message == "创建客户失败: 通用错误"
        assert raised_error.error_code == "客户_OPERATION_ERROR"
        assert raised_error.details == self.context
        assert raised_error.original_exception == original_error

        # 验证日志记录
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.ERROR  # 日志级别

    def test_dao_exception_handler_decorator_success(self):
        """测试装饰器模式 - 成功情况"""

        @dao_exception_handler("创建", "客户")
        def test_function(value):
            return value * 2

        result = test_function(5)
        assert result == 10

    def test_dao_exception_handler_decorator_exception(self):
        """测试装饰器模式 - 异常情况"""
        error_msg = "测试异常"

        @dao_exception_handler("创建", "客户")
        def test_function():
            raise ValueError(error_msg)

        with pytest.raises(DatabaseError) as exc_info:
            test_function()

        raised_error = exc_info.value
        assert raised_error.message == "创建客户失败: 测试异常"
        assert "function_name" in raised_error.details
        assert raised_error.details["function_name"] == "test_function"

    def test_dao_exception_handler_decorator_with_context(self):
        """测试装饰器模式 - 带上下文"""
        custom_context = {"custom_key": "custom_value"}
        error_msg = "测试异常"

        @dao_exception_handler("更新", "供应商", custom_context)
        def test_function():
            raise ValueError(error_msg)

        with pytest.raises(DatabaseError) as exc_info:
            test_function()

        raised_error = exc_info.value
        assert raised_error.message == "更新供应商失败: 测试异常"
        assert "custom_key" in raised_error.details
        assert raised_error.details["custom_key"] == "custom_value"

    def test_convenience_functions(self):
        """测试便捷函数"""
        # 测试handle_create_error
        error_msg = "创建错误"
        with pytest.raises(DatabaseError) as exc_info:
            handle_create_error(ValueError(error_msg), "客户", user_id=123)

        raised_error = exc_info.value
        assert raised_error.message == "创建客户失败: 创建错误"
        assert raised_error.details["user_id"] == 123

        # 测试handle_update_error
        error_msg = "更新错误"
        with pytest.raises(DatabaseError) as exc_info:
            handle_update_error(ValueError(error_msg), "供应商", session_id="abc")

        raised_error = exc_info.value
        assert raised_error.message == "更新供应商失败: 更新错误"
        assert raised_error.details["session_id"] == "abc"

        # 测试handle_query_error
        error_msg = "查询错误"
        with pytest.raises(DatabaseError) as exc_info:
            handle_query_error(ValueError(error_msg), "报价")

        raised_error = exc_info.value
        assert raised_error.message == "查询报价失败: 查询错误"

    def test_operation_mapping(self):
        """测试操作类型映射"""
        test_cases = [
            ("create", "创建"),
            ("update", "更新"),
            ("delete", "删除"),
            ("query", "查询"),
            ("search", "搜索"),
            ("get", "获取"),
            ("list", "列表"),
            ("count", "统计"),
            ("exists", "检查存在性"),
        ]

        for english_op, chinese_op in test_cases:
            message = DAOExceptionHandler.format_error_message(
                english_op, "客户", "测试错误"
            )
            expected = f"{chinese_op}客户失败: 测试错误"
            assert message == expected

    def test_entity_mapping(self):
        """测试实体类型映射"""
        test_cases = [
            ("customer", "客户"),
            ("supplier", "供应商"),
            ("quote", "报价"),
            ("contract", "合同"),
            ("order", "订单"),
            ("interaction", "互动记录"),
            ("task", "任务"),
            ("customer_type", "客户类型"),
            ("supplier_type", "供应商类型"),
        ]

        for english_entity, chinese_entity in test_cases:
            message = DAOExceptionHandler.format_error_message(
                "创建", english_entity, "测试错误"
            )
            expected = f"创建{chinese_entity}失败: 测试错误"
            assert message == expected

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_log_error_with_context(self, mock_logger):
        """测试日志记录功能"""
        error_msg = "测试错误"
        error = ValueError(error_msg)
        context = {"key1": "value1", "key2": "value2"}

        DAOExceptionHandler._log_error(logging.ERROR, "测试消息", error, context)

        # 验证日志调用
        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args

        # 验证日志级别和消息
        assert call_args[0][0] == logging.ERROR
        assert call_args[0][1] == "测试消息"

        # 验证extra参数
        extra = call_args[1]["extra"]
        assert extra["exception_type"] == "ValueError"
        assert extra["exception_message"] == "测试错误"
        assert extra["context"] == context

        # 验证exc_info参数
        assert call_args[1]["exc_info"] is True

    @patch("minicrm.data.dao.dao_exception_handler.logger")
    def test_log_error_warning_level(self, mock_logger):
        """测试警告级别日志记录"""
        error_msg = "测试错误"
        error = ValueError(error_msg)

        DAOExceptionHandler._log_error(logging.WARNING, "警告消息", error, {})

        # 验证日志调用
        call_args = mock_logger.log.call_args
        assert call_args[0][0] == logging.WARNING

        # 验证exc_info参数 - WARNING级别不应该记录异常堆栈
        assert call_args[1]["exc_info"] is False
