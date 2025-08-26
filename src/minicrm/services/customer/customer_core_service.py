"""MiniCRM 客户核心服务.

提供客户基础CRUD操作的业务逻辑处理:
- 客户信息管理(CRUD操作)
- 业务规则验证
- 数据验证和异常处理

严格遵循分层架构和模块化原则:
- 只处理核心业务逻辑,不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
"""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from minicrm.data.dao.customer_dao import CustomerDAO


# 导入transfunctions模块
try:
    from minicrm.transfunctions.business_validation import validate_customer_data
    from minicrm.transfunctions.crud_templates import build_crud_service
except ImportError:
    # 如果transfunctions模块不存在,提供临时实现
    def validate_customer_data(data: dict[str, Any]) -> dict[str, Any]:
        """临时验证函数."""
        if not data.get("name", "").strip():
            msg = "客户名称不能为空"
            raise ValidationError(msg)
        if not data.get("phone", "").strip():
            msg = "客户电话不能为空"
            raise ValidationError(msg)
        return data

    def build_crud_service(dao_instance, entity_type: str, validation_func=None):
        """临时CRUD服务构建函数."""
        return


class CustomerCoreService:
    """客户核心服务实现.

    负责客户相关的核心CRUD业务逻辑:
    - 客户CRUD操作的业务规则
    - 数据验证和异常处理
    - 业务规则验证

    严格遵循单一职责原则和模块化标准.
    """

    def __init__(self, customer_dao: CustomerDAO):
        """初始化客户核心服务.

        Args:
            customer_dao: 客户数据访问对象
        """
        self._customer_dao = customer_dao
        self._logger = logging.getLogger(__name__)

        # 使用transfunctions创建CRUD模板
        self._crud_template = None
        if customer_dao:
            self._crud_template = build_crud_service(
                dao_instance=customer_dao,
                entity_type="客户",
                validation_func=validate_customer_data,
            )
        self._logger.info("客户核心服务初始化完成")

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """创建新客户.

        实现完整的客户创建业务规则:
        1. 使用transfunctions验证数据
        2. 检查重复客户
        3. 应用业务规则和默认值
        4. 保存到数据库

        Args:
            customer_data: 客户数据字典,包含姓名、电话等信息

        Returns:
            int: 新创建的客户ID

        Raises:
            ValidationError: 当客户数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            # 1. 强制使用transfunctions验证数据
            validated_data = validate_customer_data(customer_data)

            # 2. 执行创建前的业务逻辑检查
            self._execute_pre_create_checks(validated_data)

            # 3. 应用业务规则设置默认值
            self._apply_customer_defaults(validated_data)

            # 4. 使用transfunctions CRUD模板或直接DAO保存
            if self._crud_template and hasattr(self._crud_template, "create"):
                customer_id = self._crud_template["create"](validated_data)
            else:
                customer_id = self._customer_dao.insert(validated_data)

            success_msg = f"成功创建客户,ID: {customer_id}"
            self._logger.info(success_msg)
            return customer_id

        except (ValidationError, BusinessLogicError) as e:
            warning_msg = f"客户创建业务异常: {e}"
            self._logger.warning(warning_msg)
            raise
        except Exception as e:
            error_msg = f"客户创建系统异常: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"创建客户失败: {e}"
            raise ServiceError(service_error_msg) from e

    def update_customer(self, customer_id: int, data: dict[str, Any]) -> bool:
        """更新客户信息.

        Args:
            customer_id: 客户ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            validated_data = validate_customer_data(data)

            # 检查客户是否存在
            if not self._customer_dao.get_by_id(customer_id):
                not_found_msg = f"客户不存在: {customer_id}"
                raise BusinessLogicError(not_found_msg)

            # 更新数据库
            validated_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = self._customer_dao.update(customer_id, validated_data)

            if result:
                success_msg = f"成功更新客户: {customer_id}"
                self._logger.info(success_msg)

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            error_msg = f"更新客户失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"更新客户失败: {e}"
            raise ServiceError(service_error_msg) from e

    def delete_customer(self, customer_id: int) -> bool:
        """删除客户.

        Args:
            customer_id: 客户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查客户是否存在
            customer = self._customer_dao.get_by_id(customer_id)
            if not customer:
                error_msg = f"客户不存在: {customer_id}"
                raise BusinessLogicError(error_msg)

            # 执行删除
            result = self._customer_dao.delete(customer_id)

            if result:
                success_msg = f"成功删除客户: {customer_id}"
                self._logger.info(success_msg)

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            error_msg = f"删除客户失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"删除客户失败: {e}"
            raise ServiceError(service_error_msg) from e

    def get_customer_by_id(self, customer_id: int) -> dict[str, Any] | None:
        """根据ID获取客户信息.

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any] | None: 客户信息,不存在时返回None

        Raises:
            ServiceError: 当获取失败时
        """
        try:
            return self._customer_dao.get_by_id(customer_id)

        except Exception as e:
            error_msg = f"获取客户信息失败: {e}"
            self._logger.exception(error_msg)
            service_error_msg = f"获取客户信息失败: {e}"
            raise ServiceError(service_error_msg) from e

    def _execute_pre_create_checks(self, customer_data: dict[str, Any]) -> None:
        """执行创建前的业务逻辑检查.

        Args:
            customer_data: 客户数据
        """
        try:
            # 检查1: 数据预处理
            self._preprocess_customer_data(customer_data)

            # 检查2: 业务规则验证
            self._validate_business_rules(customer_data)

            # 检查3: 重复检查
            if self._check_customer_exists(customer_data):
                error_msg = "客户已存在,无法重复创建"
                raise BusinessLogicError(error_msg)

        except Exception as e:
            error_msg = f"创建前检查失败: {e}"
            self._logger.error(error_msg)
            raise

    def _check_customer_exists(self, customer_data: dict[str, Any]) -> bool:
        """检查客户是否已存在.

        业务规则: 根据客户名称和电话号码判断是否重复

        Args:
            customer_data: 客户数据

        Returns:
            bool: 客户是否已存在
        """
        name = customer_data.get("name", "").strip()
        phone = customer_data.get("phone", "").strip()

        if not name and not phone:
            return False

        # 使用DAO的搜索方法检查重复
        existing_customers = self._customer_dao.search_by_name_or_phone(
            f"{name} {phone}"
        )
        return len(existing_customers) > 0

    def _apply_customer_defaults(self, customer_data: dict[str, Any]) -> None:
        """应用客户默认值的业务规则.

        Args:
            customer_data: 客户数据字典(会被修改)
        """
        # 设置默认客户等级
        customer_data.setdefault("level", "普通")

        # 设置默认状态
        customer_data.setdefault("status", "active")

        # 设置创建时间
        customer_data.setdefault("created_at", datetime.now(timezone.utc).isoformat())

        # 根据客户类型设置默认等级(业务规则)
        customer_type = customer_data.get("customer_type", "")
        if customer_type in ["生态板客户", "家具板客户"]:
            customer_data["level"] = "重要"  # 强制设置,不使用setdefault
        elif customer_type == "阻燃板客户":
            customer_data["level"] = "VIP"

    def _preprocess_customer_data(self, customer_data: dict[str, Any]) -> None:
        """预处理客户数据."""
        # 清理和标准化数据
        if "name" in customer_data:
            customer_data["name"] = customer_data["name"].strip()

        if "phone" in customer_data:
            # 标准化电话号码格式
            phone = customer_data["phone"].strip()
            # 移除常见分隔符
            phone = (
                phone.replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
            )
            customer_data["phone"] = phone

    def _validate_business_rules(self, customer_data: dict[str, Any]) -> None:
        """验证业务规则."""
        # 业务规则1: VIP客户必须有公司名称
        if customer_data.get("customer_level") == "vip" and not customer_data.get(
            "company_name"
        ):
            error_msg = "VIP客户必须填写公司名称"
            raise BusinessLogicError(error_msg)

        # 业务规则2: 企业客户必须有税号
        if customer_data.get("customer_type") == "enterprise" and not customer_data.get(
            "tax_id"
        ):
            error_msg = "企业客户必须填写税号"
            raise BusinessLogicError(error_msg)
