"""异常类测试模块.

测试MiniCRM异常类的功能和行为。
"""

from unittest.mock import patch

import pytest

from src.minicrm.core.exceptions import (
    BusinessLogicError,
    ConfigurationError,
    DatabaseError,
    MiniCRMError,
    UIError,
    ValidationError,
    handle_exception,
    log_exception,
)


class TestMiniCRMError:
    """测试MiniCRMError基础异常类"""

    def setup_method(self):
        """测试准备"""
        self.test_message = "测试错误消息"
        self.test_error_code = "TEST_ERROR"
        self.test_details = {"field": "value"}

    def test_basic_exception_creation(self):
        """测试基本异常创建"""
        error = MiniCRMError(self.test_message)

        assert error.message == self.test_message
        assert error.error_code == "MiniCRMError"
        assert error.details == {}
        assert error.original_exception is None

    def test_exception_with_all_parameters(self):
        """测试带所有参数的异常创建"""
        original_error = ValueError("原始错误")

        error = MiniCRMError(
            message=self.test_message,
            error_code=self.test_error_code,
            details=self.test_details,
            original_exception=original_error,
        )

        assert error.message == self.test_message
        assert error.error_code == self.test_error_code
        assert error.details == self.test_details
        assert error.original_exception == original_error

    def test_exception_string_representation(self):
        """测试异常字符串表示"""
        error = MiniCRMError(self.test_message, self.test_error_code)
        expected_str = f"[{self.test_error_code}] {self.test_message}"

        assert str(error) == expected_str

    def test_exception_to_dict(self):
        """测试异常转换为字典"""
        original_error = ValueError("原始错误")
        error = MiniCRMError(
            message=self.test_message,
            error_code=self.test_error_code,
            details=self.test_details,
            original_exception=original_error,
        )

        result_dict = error.to_dict()

        expected_dict = {
            "error_type": "MiniCRMError",
            "error_code": self.test_error_code,
            "message": self.test_message,
            "details": self.test_details,
            "original_exception": str(original_error),
        }

        assert result_dict == expected_dict

    @patch("src.minicrm.core.exceptions.logger")
    def test_exception_logging(self, mock_logger):
        """测试异常日志记录"""
        MiniCRMError(self.test_message, self.test_error_code)

        # 验证日志记录被调用
        mock_logger.error.assert_called_once()


class TestValidationError:
    """测试ValidationError验证异常类"""

    def test_validation_error_with_field_info(self):
        """测试带字段信息的验证异常"""
        field_name = "customer_name"
        field_value = ""
        message = "客户名称不能为空"

        error = ValidationError(
            message=message, field_name=field_name, field_value=field_value
        )

        assert error.message == message
        assert error.details["field_name"] == field_name
        assert error.details["field_value"] == str(field_value)

    def test_validation_error_inheritance(self):
        """测试ValidationError继承关系"""
        error = ValidationError("测试验证错误")

        assert isinstance(error, MiniCRMError)
        assert isinstance(error, ValidationError)


class TestDatabaseError:
    """测试DatabaseError数据库异常类"""

    def test_database_error_with_sql_info(self):
        """测试带SQL信息的数据库异常"""
        message = "数据库查询失败"
        sql_statement = "SELECT * FROM customers WHERE id = ?"
        sql_params = (123,)

        error = DatabaseError(
            message=message, sql_statement=sql_statement, sql_params=sql_params
        )

        assert error.message == message
        assert error.details["sql_statement"] == sql_statement
        assert error.details["sql_params"] == str(sql_params)

    def test_database_error_inheritance(self):
        """测试DatabaseError继承关系"""
        error = DatabaseError("测试数据库错误")

        assert isinstance(error, MiniCRMError)
        assert isinstance(error, DatabaseError)


class TestBusinessLogicError:
    """测试BusinessLogicError业务逻辑异常类"""

    def test_business_logic_error_with_context(self):
        """测试带业务上下文的业务逻辑异常"""
        message = "客户已存在"
        business_rule = "UNIQUE_CUSTOMER_NAME"
        context = {"customer_name": "ABC公司"}

        error = BusinessLogicError(
            message=message, business_rule=business_rule, context=context
        )

        assert error.message == message
        assert error.details["business_rule"] == business_rule
        assert error.details["context"] == context


class TestConfigurationError:
    """测试ConfigurationError配置异常类"""

    def test_configuration_error_with_config_info(self):
        """测试带配置信息的配置异常"""
        message = "配置文件不存在"
        config_key = "database.path"
        config_file = "/path/to/config.json"

        error = ConfigurationError(
            message=message, config_key=config_key, config_file=config_file
        )

        assert error.message == message
        assert error.details["config_key"] == config_key
        assert error.details["config_file"] == config_file


class TestUIError:
    """测试UIError界面异常类"""

    def test_ui_error_with_widget_info(self):
        """测试带控件信息的UI异常"""
        message = "窗口显示失败"
        widget_name = "MainWindow"
        ui_operation = "show"

        error = UIError(
            message=message, widget_name=widget_name, ui_operation=ui_operation
        )

        assert error.message == message
        assert error.details["widget_name"] == widget_name
        assert error.details["ui_operation"] == ui_operation


class TestExceptionHandling:
    """测试异常处理工具函数"""

    def test_handle_exception_decorator_success(self):
        """测试异常处理装饰器 - 成功情况"""

        @handle_exception
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    def test_handle_exception_decorator_minicrm_error(self):
        """测试异常处理装饰器 - MiniCRM异常"""
        test_error_message = "测试验证错误"

        @handle_exception
        def test_function():
            raise ValidationError(test_error_message)

        with pytest.raises(ValidationError):
            test_function()

    @patch("src.minicrm.core.exceptions.logger")
    def test_handle_exception_decorator_general_error(self, mock_logger):
        """测试异常处理装饰器 - 一般异常"""
        test_error_message = "测试错误"

        @handle_exception
        def test_function():
            raise ValueError(test_error_message)

        with pytest.raises(MiniCRMError) as exc_info:
            test_function()

        # 验证异常被转换为MiniCRMError
        assert "test_function" in str(exc_info.value)
        assert exc_info.value.error_code == "UNHANDLED_EXCEPTION"

        # 验证日志记录
        mock_logger.error.assert_called()

    @patch("src.minicrm.core.exceptions.logger")
    def test_log_exception_minicrm_error(self, mock_logger):
        """测试记录MiniCRM异常"""
        error = ValidationError("测试验证错误", error_code="TEST_VALIDATION")
        context = {"user_id": 123}

        log_exception(error, context)

        # 验证日志记录被调用
        mock_logger.error.assert_called_once()

    @patch("src.minicrm.core.exceptions.logger")
    def test_log_exception_general_error(self, mock_logger):
        """测试记录一般异常"""
        error = ValueError("测试错误")
        context = {"operation": "test"}

        log_exception(error, context)

        # 验证日志记录被调用
        mock_logger.error.assert_called_once()
