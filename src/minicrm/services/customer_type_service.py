"""MiniCRM 客户类型管理服务

提供客户类型的完整管理功能,包括:
- 客户类型的增删改查操作
- 类型使用统计和限制检查
- 类型创建、编辑、删除的业务逻辑
- 与transfunctions的集成

严格遵循分层架构和模块化原则:
- 只处理业务逻辑,不包含UI逻辑
- 通过DAO接口访问数据
- 强制使用transfunctions进行验证和计算
- 文件大小控制在推荐范围内(目标300行以内)
"""

from datetime import datetime
import logging
from typing import Any

from minicrm.core.exceptions import BusinessLogicError, ServiceError, ValidationError
from transfunctions.validation import validate_required_fields

from .base_service import BaseService


class CustomerTypeService(BaseService):
    """客户类型管理服务实现

    负责客户类型管理的核心业务逻辑:
    - 客户类型的CRUD操作和业务规则
    - 类型使用统计和限制检查
    - 类型创建、编辑、删除的业务逻辑
    - 数据验证和异常处理

    严格遵循单一职责原则和模块化标准.
    """

    def __init__(self, customer_type_dao=None):
        """初始化客户类型服务

        Args:
            customer_type_dao: 客户类型数据访问对象
        """
        super().__init__(customer_type_dao)
        self._logger = logging.getLogger(__name__)
        self._logger.info("客户类型服务初始化完成")

    def get_service_name(self) -> str:
        """获取服务名称"""
        return "CustomerTypeService"

    def create_customer_type(self, type_data: dict[str, Any]) -> int:
        """创建新的客户类型

        实现完整的客户类型创建业务规则:
        1. 使用transfunctions验证数据
        2. 检查类型名称重复
        3. 应用业务规则和默认值
        4. 保存到数据库

        Args:
            type_data: 客户类型数据字典

        Returns:
            int: 新创建的客户类型ID

        Raises:
            ValidationError: 当数据验证失败时
            BusinessLogicError: 当业务规则检查失败时
            ServiceError: 当数据库操作失败时
        """
        try:
            self._log_operation("创建客户类型", {"service": self.get_service_name()})

            # 1. 强制使用transfunctions验证数据
            self._validate_customer_type_data(type_data)

            # 2. 检查类型名称是否重复
            if self._check_type_name_exists(type_data.get("name", "")):
                raise BusinessLogicError(f"客户类型名称已存在: {type_data.get('name')}")

            # 3. 应用业务规则设置默认值
            self._apply_customer_type_defaults(type_data)

            # 4. 保存到数据库
            type_id = self._dao.insert(type_data)

            self._log_operation("客户类型创建成功", {"id": type_id})
            return type_id

        except (ValidationError, BusinessLogicError) as e:
            self._logger.warning(f"客户类型创建业务异常: {e}")
            raise
        except Exception as e:
            self._logger.error(f"客户类型创建系统异常: {e}")
            raise ServiceError(f"创建客户类型失败: {e}") from e

    def update_customer_type(self, type_id: int, data: dict[str, Any]) -> bool:
        """更新客户类型

        Args:
            type_id: 客户类型ID
            data: 更新数据

        Returns:
            bool: 更新是否成功
        """
        try:
            # 验证数据
            self._validate_customer_type_data(data, is_update=True)

            # 检查客户类型是否存在
            existing_type = self._dao.get_by_id(type_id)
            if not existing_type:
                raise BusinessLogicError(f"客户类型不存在: {type_id}")

            # 检查名称重复(排除自己)
            if "name" in data:
                if self._check_type_name_exists(data["name"], exclude_id=type_id):
                    raise BusinessLogicError(f"客户类型名称已存在: {data['name']}")

            # 更新时间戳
            data["updated_at"] = datetime.now().isoformat()

            # 更新数据库
            result = self._dao.update(type_id, data)

            if result:
                self._log_operation("客户类型更新成功", {"id": type_id})

            return result

        except (ValidationError, BusinessLogicError):
            raise
        except Exception as e:
            self._logger.error(f"更新客户类型失败: {e}")
            raise ServiceError(f"更新客户类型失败: {e}") from e

    def delete_customer_type(self, type_id: int, force: bool = False) -> bool:
        """删除客户类型

        Args:
            type_id: 客户类型ID
            force: 是否强制删除(即使有客户使用)

        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查客户类型是否存在
            existing_type = self._dao.get_by_id(type_id)
            if not existing_type:
                raise BusinessLogicError(f"客户类型不存在: {type_id}")

            # 检查是否有客户使用此类型
            usage_count = self.get_type_usage_count(type_id)
            if usage_count > 0 and not force:
                raise BusinessLogicError(
                    f"无法删除客户类型,仍有 {usage_count} 个客户使用此类型."
                    f"请先更改这些客户的类型,或使用强制删除."
                )

            # 执行删除
            result = self._dao.delete(type_id)

            if result:
                self._log_operation(
                    "客户类型删除成功",
                    {"id": type_id, "force": force, "usage_count": usage_count},
                )

            return result

        except BusinessLogicError:
            raise
        except Exception as e:
            self._logger.error(f"删除客户类型失败: {e}")
            raise ServiceError(f"删除客户类型失败: {e}") from e

    def get_customer_type_by_id(self, type_id: int) -> dict[str, Any] | None:
        """根据ID获取客户类型

        Args:
            type_id: 客户类型ID

        Returns:
            Dict[str, Any] | None: 客户类型信息,不存在时返回None
        """
        try:
            type_data = self._dao.get_by_id(type_id)
            if type_data:
                # 添加使用统计信息
                type_data["usage_count"] = self.get_type_usage_count(type_id)
                type_data["can_delete"] = type_data["usage_count"] == 0

            return type_data

        except Exception as e:
            self._logger.error(f"获取客户类型失败: {e}")
            raise ServiceError(f"获取客户类型失败: {e}") from e

    def get_all_customer_types(self) -> list[dict[str, Any]]:
        """获取所有客户类型

        Returns:
            List[Dict[str, Any]]: 客户类型列表
        """
        try:
            types = self._dao.get_all()

            # 为每个类型添加使用统计信息
            for type_data in types:
                type_id = type_data.get("id")
                if type_id:
                    type_data["usage_count"] = self.get_type_usage_count(type_id)
                    type_data["can_delete"] = type_data["usage_count"] == 0

            return types

        except Exception as e:
            self._logger.error(f"获取所有客户类型失败: {e}")
            raise ServiceError(f"获取所有客户类型失败: {e}") from e

    def search_customer_types(
        self, query: str = "", filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """搜索客户类型

        Args:
            query: 搜索关键词
            filters: 筛选条件

        Returns:
            List[Dict[str, Any]]: 匹配的客户类型列表
        """
        try:
            # 构建搜索条件
            conditions = filters.copy() if filters else {}

            if query:
                # 在名称和描述中搜索
                conditions["name__contains"] = query

            # 执行搜索
            types = self._dao.search(conditions)

            # 添加使用统计信息
            for type_data in types:
                type_id = type_data.get("id")
                if type_id:
                    type_data["usage_count"] = self.get_type_usage_count(type_id)
                    type_data["can_delete"] = type_data["usage_count"] == 0

            return types

        except Exception as e:
            self._logger.error(f"搜索客户类型失败: {e}")
            raise ServiceError(f"搜索客户类型失败: {e}") from e

    def get_type_usage_count(self, type_id: int) -> int:
        """获取客户类型的使用数量

        Args:
            type_id: 客户类型ID

        Returns:
            int: 使用此类型的客户数量
        """
        try:
            # 这里需要查询客户表中使用此类型的数量
            # 由于没有直接的客户DAO引用,使用简化实现
            # 实际实现中应该注入CustomerDAO或通过服务间调用

            # 模拟查询结果(实际应该查询数据库)
            # TODO: 实现真实的客户类型使用统计查询
            return 0

        except Exception as e:
            self._logger.error(f"获取客户类型使用数量失败: {e}")
            return 0

    def get_type_statistics(self) -> dict[str, Any]:
        """获取客户类型统计信息

        Returns:
            Dict[str, Any]: 统计信息
        """
        try:
            all_types = self.get_all_customer_types()

            total_types = len(all_types)
            used_types = len([t for t in all_types if t.get("usage_count", 0) > 0])
            unused_types = total_types - used_types

            # 计算使用分布
            usage_distribution = {}
            for type_data in all_types:
                usage_count = type_data.get("usage_count", 0)
                type_name = type_data.get("name", "未知")
                usage_distribution[type_name] = usage_count

            return {
                "total_types": total_types,
                "used_types": used_types,
                "unused_types": unused_types,
                "usage_distribution": usage_distribution,
                "most_used_type": max(
                    usage_distribution.items(), key=lambda x: x[1], default=("无", 0)
                )[0]
                if usage_distribution
                else "无",
            }

        except Exception as e:
            self._logger.error(f"获取客户类型统计失败: {e}")
            raise ServiceError(f"获取客户类型统计失败: {e}") from e

    def _validate_customer_type_data(
        self, data: dict[str, Any], is_update: bool = False
    ) -> None:
        """验证客户类型数据 - 使用transfunctions统一验证

        Args:
            data: 客户类型数据
            is_update: 是否为更新操作
        """
        # 必填字段验证(创建时)- 使用transfunctions
        if not is_update:
            required_fields = ["name"]
            errors = validate_required_fields(data, required_fields)
            if errors:
                raise ValidationError("; ".join(errors))

        # 名称验证
        if "name" in data:
            name = data["name"].strip()
            if not name:
                raise ValidationError("客户类型名称不能为空")
            if len(name) > 50:
                raise ValidationError("客户类型名称长度不能超过50个字符")
            data["name"] = name

        # 描述验证
        if data.get("description"):
            description = data["description"].strip()
            if len(description) > 200:
                raise ValidationError("客户类型描述长度不能超过200个字符")
            data["description"] = description

        # 颜色代码验证
        if data.get("color_code"):
            color_code = data["color_code"].strip()
            if not color_code.startswith("#") or len(color_code) != 7:
                raise ValidationError("颜色代码格式不正确,应为 #RRGGBB 格式")
            data["color_code"] = color_code

        # 排序值验证
        if "sort_order" in data:
            try:
                sort_order = int(data["sort_order"])
                if sort_order < 0:
                    raise ValidationError("排序值不能为负数")
                data["sort_order"] = sort_order
            except (ValueError, TypeError):
                raise ValidationError("排序值必须为整数")

    def _apply_customer_type_defaults(self, data: dict[str, Any]) -> None:
        """应用客户类型默认值的业务规则

        Args:
            data: 客户类型数据字典(会被修改)
        """
        # 设置默认描述
        data.setdefault("description", "")

        # 设置默认颜色(蓝色)
        data.setdefault("color_code", "#007BFF")

        # 设置默认排序值
        data.setdefault("sort_order", 0)

        # 设置默认状态
        data.setdefault("is_active", True)

        # 设置创建时间
        data.setdefault("created_at", datetime.now().isoformat())

    def _check_type_name_exists(self, name: str, exclude_id: int | None = None) -> bool:
        """检查客户类型名称是否已存在

        Args:
            name: 类型名称
            exclude_id: 排除的ID(用于更新时检查)

        Returns:
            bool: 名称是否已存在
        """
        if not name:
            return False

        try:
            # 搜索同名的客户类型
            conditions = {"name": name.strip()}
            existing_types = self._dao.search(conditions)

            # 如果有排除ID,过滤掉该记录
            if exclude_id is not None:
                existing_types = [
                    t for t in existing_types if t.get("id") != exclude_id
                ]

            return len(existing_types) > 0

        except Exception as e:
            self._logger.error(f"检查客户类型名称重复失败: {e}")
            return False
