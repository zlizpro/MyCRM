"""
MiniCRM 模型转换器

负责模型与数据库记录之间的转换
"""

import logging
from typing import Any, TypeVar

from ...models import BaseModel


# 泛型类型变量
T = TypeVar("T", bound=BaseModel)


class ModelConverter:
    """模型转换器"""

    def __init__(self):
        """初始化模型转换器"""
        self._logger = logging.getLogger(__name__)

    def row_to_model(self, row_data: dict[str, Any], model_class: type[T]) -> T:
        """
        将数据库行转换为模型实例

        Args:
            row_data: 数据库行数据
            model_class: 模型类

        Returns:
            T: 模型实例
        """
        try:
            if not row_data:
                return None

            return model_class.from_dict(row_data)

        except Exception as e:
            self._logger.error(f"行数据转换为模型失败: {e}")
            raise

    def model_to_dict(self, model: T) -> dict[str, Any]:
        """
        将模型实例转换为字典

        Args:
            model: 模型实例

        Returns:
            dict: 数据字典
        """
        try:
            if not model:
                return {}

            return model.to_dict()

        except Exception as e:
            self._logger.error(f"模型转换为字典失败: {e}")
            raise

    def models_to_dicts(self, models: list[T]) -> list[dict[str, Any]]:
        """
        将模型列表转换为字典列表

        Args:
            models: 模型列表

        Returns:
            list: 字典列表
        """
        try:
            if not models:
                return []

            return [self.model_to_dict(model) for model in models]

        except Exception as e:
            self._logger.error(f"模型列表转换为字典列表失败: {e}")
            raise

    def rows_to_models(
        self, rows_data: list[dict[str, Any]], model_class: type[T]
    ) -> list[T]:
        """
        将数据库行列表转换为模型列表

        Args:
            rows_data: 数据库行数据列表
            model_class: 模型类

        Returns:
            list[T]: 模型列表
        """
        try:
            if not rows_data:
                return []

            models = []
            for row_data in rows_data:
                model = self.row_to_model(row_data, model_class)
                if model:
                    models.append(model)

            return models

        except Exception as e:
            self._logger.error(f"行数据列表转换为模型列表失败: {e}")
            raise

    def validate_model_data(self, data: dict[str, Any], model_class: type[T]) -> bool:
        """
        验证数据是否符合模型要求

        Args:
            data: 数据字典
            model_class: 模型类

        Returns:
            bool: 验证结果
        """
        try:
            # 尝试创建模型实例来验证数据
            model_class.from_dict(data)
            return True

        except Exception as e:
            self._logger.warning(f"模型数据验证失败: {e}")
            return False

    def prepare_model_for_insert(self, model: T) -> dict[str, Any]:
        """
        准备模型数据用于插入操作

        Args:
            model: 模型实例

        Returns:
            dict: 准备好的数据字典
        """
        try:
            data = self.model_to_dict(model)

            # 移除ID字段（由数据库自动生成）
            if "id" in data:
                del data["id"]

            # 移除None值字段（可选）
            data = {k: v for k, v in data.items() if v is not None}

            return data

        except Exception as e:
            self._logger.error(f"准备插入数据失败: {e}")
            raise

    def prepare_model_for_update(self, model: T) -> dict[str, Any]:
        """
        准备模型数据用于更新操作

        Args:
            model: 模型实例

        Returns:
            dict: 准备好的数据字典
        """
        try:
            data = self.model_to_dict(model)

            # 移除ID字段（不应该更新ID）
            if "id" in data:
                del data["id"]

            # 移除None值字段（避免覆盖现有数据）
            data = {k: v for k, v in data.items() if v is not None}

            return data

        except Exception as e:
            self._logger.error(f"准备更新数据失败: {e}")
            raise
