"""
MiniCRM 供应商核心服务

提供供应商基础CRUD操作：
- 创建供应商
- 更新供应商
- 删除供应商
- 搜索供应商
"""

from datetime import datetime
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.services.base_service import BaseService
from transfunctions import ValidationError, validate_supplier_data


class SupplierCoreService(BaseService):
    """
    供应商核心服务实现

    负责供应商基础CRUD操作的业务逻辑：
    - 供应商创建、更新、删除
    - 供应商搜索和查询
    - 数据验证和业务规则检查

    严格遵循单一职责原则。
    """

    def __init__(self, supplier_dao: SupplierDAO):
        """
        初始化供应商核心服务

        Args:
            supplier_dao: 供应商数据访问对象
        """
        super().__init__(supplier_dao)
        self._supplier_dao = supplier_dao

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "SupplierCoreService"

    def create_supplier(self, supplier_data: dict[str, Any]) -> int:
        """
        创建新供应商

        实现完整的供应商创建业务规则：
        1. 使用transfunctions验证数据
        2. 检查重复供应商
        3. 应用业务规则和默认值
        4. 保存到数据库

        Args:
            supplier_data: 供应商数据字典，包含名称、联系方式等信息

        Returns:
            int: 新创建的供应商ID

        Raises:
            ValidationError: 当供应商数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            # 1. 强制使用transfunctions验证数据
            validation_result = validate_supplier_data(supplier_data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"供应商数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 2. 业务规则：检查供应商是否已存在
            if self._check_supplier_exists(supplier_data):
                raise BusinessLogicError("供应商已存在，无法重复创建")

            # 3. 应用业务规则设置默认值
            self._apply_supplier_defaults(supplier_data)

            # 4. 保存到数据库
            supplier_id = self._supplier_dao.insert(supplier_data)

            self._logger.info(f"成功创建供应商，ID: {supplier_id}")
            return supplier_id

        except (ValidationError, BusinessLogicError) as e:
            self._logger.warning(f"供应商创建业务异常: {e}")
            raise
        except Exception as e:
            self._logger.error(f"供应商创建系统异常: {e}")
            raise ServiceError(f"创建供应商失败: {e}") from e

    def update_supplier(self, supplier_id: int, data: dict[str, Any]) -> bool:
        """
        更新供应商信息

        Args:
            supplier_id: 供应商ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            validation_result = validate_supplier_data(data)
            if not validation_result.is_valid:
                raise ValidationError(
                    f"供应商数据验证失败: {', '.join(validation_result.errors)}"
                )

            # 检查供应商是否存在
            if not self._supplier_dao.get_by_id(supplier_id):
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 更新数据库
            data["updated_at"] = datetime.now().isoformat()
            result = self._supplier_dao.update(supplier_id, data)

            if result:
                self._logger.info(f"成功更新供应商: {supplier_id}")

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新供应商失败: {e}")
            raise ServiceError(f"更新供应商失败: {e}") from e

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        删除供应商

        Args:
            supplier_id: 供应商ID

        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查供应商是否存在
            supplier = self._supplier_dao.get_by_id(supplier_id)
            if not supplier:
                raise BusinessLogicError(f"供应商不存在: {supplier_id}")

            # 执行删除
            result = self._supplier_dao.delete(supplier_id)

            if result:
                self._logger.info(f"成功删除供应商: {supplier_id}")

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除供应商失败: {e}")
            raise ServiceError(f"删除供应商失败: {e}") from e

    def search_suppliers(
        self,
        query: str = "",
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        搜索供应商

        Args:
            query: 搜索关键词
            filters: 筛选条件
            page: 页码
            page_size: 每页大小

        Returns:
            Tuple[List[Dict[str, Any]], int]: (供应商列表, 总数)
        """
        try:
            conditions = {}
            if query:
                suppliers = self._supplier_dao.search_by_name_or_contact(query)
            else:
                if filters:
                    conditions.update(filters)

                offset = (page - 1) * page_size
                suppliers = self._supplier_dao.search(
                    conditions=conditions, limit=page_size, offset=offset
                )

            total = self._supplier_dao.count(conditions)
            return suppliers, total

        except Exception as e:
            self._logger.error(f"搜索供应商失败: {e}")
            raise ServiceError(f"搜索供应商失败: {e}") from e

    def _check_supplier_exists(self, supplier_data: dict[str, Any]) -> bool:
        """
        检查供应商是否已存在

        Args:
            supplier_data: 供应商数据

        Returns:
            bool: 供应商是否已存在
        """
        name = supplier_data.get("name", "").strip()
        phone = supplier_data.get("phone", "").strip()

        if not name and not phone:
            return False

        existing_suppliers = self._supplier_dao.search_by_name_or_contact(
            f"{name} {phone}"
        )
        return len(existing_suppliers) > 0

    def _apply_supplier_defaults(self, supplier_data: dict[str, Any]) -> None:
        """
        应用供应商默认值的业务规则

        Args:
            supplier_data: 供应商数据字典（会被修改）
        """
        # 设置默认供应商等级
        supplier_data.setdefault("grade", "普通供应商")

        # 设置默认状态
        supplier_data.setdefault("status", "active")

        # 设置创建时间
        supplier_data.setdefault("created_at", datetime.now().isoformat())

        # 根据供应商类型设置默认等级（业务规则）
        supplier_type = supplier_data.get("supplier_type", "")
        if supplier_type in ["原材料供应商", "核心供应商"]:
            supplier_data["grade"] = "重要供应商"  # 强制设置，不使用setdefault
        elif supplier_type == "战略合作伙伴":
            supplier_data["grade"] = "战略供应商"
