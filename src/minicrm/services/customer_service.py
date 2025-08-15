"""
MiniCRM 客户管理服务

提供客户相关的业务逻辑处理，包括：
- 客户信息管理（CRUD操作）
- 客户价值评分算法
- 业务规则验证

严格遵循分层架构和模块化原则：
- 只处理业务逻辑，不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
- 文件大小控制在推荐范围内
"""

import logging
from datetime import datetime
from typing import Any

import transfunctions.calculations as calculations
import transfunctions.validation as validation
from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from minicrm.data.dao.customer_dao import CustomerDAO


class CustomerService:
    """
    客户管理服务实现

    负责客户相关的核心业务逻辑：
    - 客户CRUD操作的业务规则
    - 客户价值评分算法
    - 数据验证和异常处理

    严格遵循单一职责原则和模块化标准。
    """

    def __init__(self, customer_dao: CustomerDAO):
        """
        初始化客户服务

        Args:
            customer_dao: 客户数据访问对象
        """
        self._customer_dao = customer_dao
        self._logger = logging.getLogger(__name__)
        self._logger.info("客户服务初始化完成")

    def create_customer(self, customer_data: dict[str, Any]) -> int:
        """
        创建新客户

        实现完整的客户创建业务规则：
        1. 使用transfunctions验证数据
        2. 检查重复客户
        3. 应用业务规则和默认值
        4. 保存到数据库

        Args:
            customer_data: 客户数据字典，包含姓名、电话等信息

        Returns:
            int: 新创建的客户ID

        Raises:
            ValidationError: 当客户数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            # 1. 强制使用transfunctions验证数据
            validation_result = validation.validate_customer_data(customer_data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"客户数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 2. 业务规则：检查客户是否已存在
            if self._check_customer_exists(customer_data):
                raise BusinessLogicError("客户已存在，无法重复创建")

            # 3. 应用业务规则设置默认值
            self._apply_customer_defaults(customer_data)

            # 4. 保存到数据库
            customer_id = self._customer_dao.insert(customer_data)

            self._logger.info(f"成功创建客户，ID: {customer_id}")
            return customer_id

        except (ValidationError, BusinessLogicError) as e:
            self._logger.warning(f"客户创建业务异常: {e}")
            raise
        except Exception as e:
            self._logger.error(f"客户创建系统异常: {e}")
            raise ServiceError(f"创建客户失败: {e}") from e

    def update_customer(self, customer_id: int, data: dict[str, Any]) -> bool:
        """
        更新客户信息

        Args:
            customer_id: 客户ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            validation_result = validation.validate_customer_data(data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"客户数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 检查客户是否存在
            if not self._customer_dao.get_by_id(customer_id):
                raise BusinessLogicError(f"客户不存在: {customer_id}")

            # 更新数据库
            data["updated_at"] = datetime.now().isoformat()
            result = self._customer_dao.update(customer_id, data)

            if result:
                self._logger.info(f"成功更新客户: {customer_id}")

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新客户失败: {e}")
            raise ServiceError(f"更新客户失败: {e}") from e

    def delete_customer(self, customer_id: int) -> bool:
        """
        删除客户

        Args:
            customer_id: 客户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查客户是否存在
            customer = self._customer_dao.get_by_id(customer_id)
            if not customer:
                raise BusinessLogicError(f"客户不存在: {customer_id}")

            # 执行删除
            result = self._customer_dao.delete(customer_id)

            if result:
                self._logger.info(f"成功删除客户: {customer_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除客户失败: {e}")
            raise ServiceError(f"删除客户失败: {e}") from e

    def calculate_customer_value_score(self, customer_id: int) -> dict[str, Any]:
        """
        计算客户价值评分

        使用transfunctions中的客户价值评分算法，基于：
        - 交易历史和金额
        - 互动频率和质量
        - 合作时长和忠诚度
        - 客户潜力和增长趋势

        Args:
            customer_id: 客户ID

        Returns:
            Dict[str, Any]: 包含详细评分指标的字典

        Raises:
            BusinessLogicError: 当客户不存在时
            ServiceError: 当计算失败时
        """
        try:
            # 获取客户基本信息
            customer_data = self._customer_dao.get_by_id(customer_id)
            if not customer_data:
                raise BusinessLogicError(f"客户不存在: {customer_id}")

            # 获取交易历史（暂时使用空列表，待实现）
            transaction_history: list[dict[str, Any]] = []

            # 获取互动历史
            interaction_history = self._customer_dao.get_recent_interactions(
                customer_id
            )

            # 使用transfunctions计算客户价值评分
            value_metrics = calculations.calculate_customer_value_score(
                customer_data, transaction_history, interaction_history
            )

            # 转换为字典格式并添加额外信息
            metrics_dict = value_metrics.to_dict()
            result: dict[str, Any] = {
                **metrics_dict,
                "customer_id": customer_id,
                "customer_name": customer_data.get("name", ""),
                "calculated_at": datetime.now().isoformat(),
                "transaction_count": len(transaction_history),
                "interaction_count": len(interaction_history),
            }

            self._logger.info(
                f"客户价值评分计算完成: {customer_id}, "
                f"评分: {value_metrics.total_score:.1f}"
            )
            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"客户价值评分计算失败: {e}")
            raise ServiceError(f"计算客户价值评分失败: {e}") from e

    def search_customers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        搜索客户

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (客户列表, 总数)
        """
        try:
            conditions = {}
            if query:
                customers = self._customer_dao.search_by_name_or_phone(query)
            else:
                if filters:
                    conditions.update(filters)

                offset = (page - 1) * page_size
                customers = self._customer_dao.search(
                    conditions=conditions, limit=page_size, offset=offset
                )

            total = self._customer_dao.count(conditions)
            return customers, total

        except Exception as e:
            self._logger.error(f"搜索客户失败: {e}")
            raise ServiceError(f"搜索客户失败: {e}") from e

    def _check_customer_exists(self, customer_data: dict[str, Any]) -> bool:
        """
        检查客户是否已存在

        业务规则：根据客户名称和电话号码判断是否重复

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
        """
        应用客户默认值的业务规则

        Args:
            customer_data: 客户数据字典（会被修改）
        """
        # 设置默认客户等级
        customer_data.setdefault("level", "普通")

        # 设置默认状态
        customer_data.setdefault("status", "active")

        # 设置创建时间
        customer_data.setdefault("created_at", datetime.now().isoformat())

        # 根据客户类型设置默认等级（业务规则）
        customer_type = customer_data.get("customer_type", "")
        if customer_type in ["生态板客户", "家具板客户"]:
            customer_data["level"] = "重要"  # 强制设置，不使用setdefault
        elif customer_type == "阻燃板客户":
            customer_data["level"] = "VIP"
