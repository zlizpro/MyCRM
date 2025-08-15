"""
Transfunctions - 数据转换工具

提供数据格式转换功能，支持数据库行与字典、模型对象之间的转换。
"""

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import Any, TypeVar


# 泛型类型变量
T = TypeVar("T")


def convert_row_to_dict(
    row: sqlite3.Row | tuple | dict, column_names: list[str] | None = None
) -> dict[str, Any]:
    """
    将数据库行转换为字典

    Args:
        row: 数据库行（sqlite3.Row、元组或字典）
        column_names: 列名列表（当row为元组时需要）

    Returns:
        Dict[str, Any]: 字典格式的数据

    Raises:
        ValueError: 当row为元组但未提供column_names时
    """
    if isinstance(row, dict):
        return row.copy()

    if hasattr(row, "keys"):
        # sqlite3.Row对象
        return dict(row)

    if isinstance(row, (tuple, list)):
        if not column_names:
            raise ValueError("元组/列表行需要提供column_names参数")
        if len(row) != len(column_names):
            raise ValueError(
                f"行数据长度({len(row)})与列名长度({len(column_names)})不匹配"
            )
        return dict(zip(column_names, row, strict=False))

    raise TypeError(f"不支持的行类型: {type(row)}")


def convert_dict_to_model(
    data: dict[str, Any], model_class: type[T], strict: bool = False
) -> T:
    """
    将字典转换为模型对象

    Args:
        data: 字典数据
        model_class: 目标模型类
        strict: 是否严格模式（严格模式下，字典中的所有键都必须是模型的属性）

    Returns:
        T: 模型对象实例

    Raises:
        ValueError: 严格模式下发现未知属性时
        TypeError: 模型类不支持从字典创建时
    """
    try:
        # 尝试使用模型类的from_dict方法
        if hasattr(model_class, "from_dict"):
            return model_class.from_dict(data)

        # 尝试直接使用字典参数创建实例
        if hasattr(model_class, "__init__"):
            # 获取构造函数参数
            import inspect

            sig = inspect.signature(model_class.__init__)
            params = list(sig.parameters.keys())[1:]  # 排除self参数

            # 过滤数据，只保留构造函数需要的参数
            filtered_data = {}
            for key, value in data.items():
                if key in params:
                    filtered_data[key] = value
                elif strict:
                    raise ValueError(f"模型{model_class.__name__}不支持属性: {key}")

            return model_class(**filtered_data)

        raise TypeError(f"模型类{model_class.__name__}不支持从字典创建")

    except Exception as e:
        raise TypeError(f"无法将字典转换为{model_class.__name__}对象: {e}") from e


def convert_model_to_dict(
    model: Any, exclude_none: bool = True, exclude_private: bool = True
) -> dict[str, Any]:
    """
    将模型对象转换为字典

    Args:
        model: 模型对象
        exclude_none: 是否排除None值
        exclude_private: 是否排除私有属性（以_开头）

    Returns:
        Dict[str, Any]: 字典格式的数据
    """
    if hasattr(model, "to_dict"):
        return model.to_dict()

    if hasattr(model, "__dict__"):
        data = {}
        for key, value in model.__dict__.items():
            # 排除私有属性
            if exclude_private and key.startswith("_"):
                continue

            # 排除None值
            if exclude_none and value is None:
                continue

            # 转换特殊类型
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)
            else:
                data[key] = value

        return data

    raise TypeError(f"对象{type(model).__name__}不支持转换为字典")


def normalize_database_value(value: Any) -> Any:
    """
    标准化数据库值

    将数据库中的值转换为Python中更合适的类型。

    Args:
        value: 数据库值

    Returns:
        Any: 标准化后的值
    """
    if value is None:
        return None

    # 处理布尔值（SQLite中存储为0/1）
    if isinstance(value, int) and value in (0, 1):
        # 这里需要根据具体字段判断是否应该转换为布尔值
        # 为了安全起见，保持原值
        return value

    # 处理时间戳字符串
    if isinstance(value, str):
        # 尝试解析ISO格式的时间戳
        try:
            if "T" in value or " " in value:
                return datetime.fromisoformat(value.replace("T", " ").replace("Z", ""))
        except ValueError:
            pass

    return value


def prepare_database_value(value: Any) -> Any:
    """
    准备数据库值

    将Python值转换为适合存储到数据库的格式。

    Args:
        value: Python值

    Returns:
        Any: 适合数据库存储的值
    """
    if value is None:
        return None

    # 处理datetime对象
    if isinstance(value, datetime):
        return value.isoformat()

    # 处理Decimal对象
    if isinstance(value, Decimal):
        return float(value)

    # 处理布尔值
    if isinstance(value, bool):
        return 1 if value else 0

    return value


def batch_convert_rows_to_dicts(
    rows: list[sqlite3.Row | tuple | dict], column_names: list[str] | None = None
) -> list[dict[str, Any]]:
    """
    批量将数据库行转换为字典列表

    Args:
        rows: 数据库行列表
        column_names: 列名列表（当行为元组时需要）

    Returns:
        List[Dict[str, Any]]: 字典列表
    """
    if not rows:
        return []

    return [convert_row_to_dict(row, column_names) for row in rows]


def batch_convert_dicts_to_models(
    data_list: list[dict[str, Any]], model_class: type[T], strict: bool = False
) -> list[T]:
    """
    批量将字典列表转换为模型对象列表

    Args:
        data_list: 字典数据列表
        model_class: 目标模型类
        strict: 是否严格模式

    Returns:
        List[T]: 模型对象列表
    """
    if not data_list:
        return []

    return [convert_dict_to_model(data, model_class, strict) for data in data_list]


def extract_changed_fields(
    original: dict[str, Any], updated: dict[str, Any]
) -> dict[str, Any]:
    """
    提取变更的字段

    比较两个字典，返回发生变更的字段。

    Args:
        original: 原始数据
        updated: 更新后的数据

    Returns:
        Dict[str, Any]: 变更的字段字典
    """
    changes = {}

    # 检查更新的字段
    for key, value in updated.items():
        if key not in original or original[key] != value:
            changes[key] = value

    return changes


def merge_dicts(*dicts: dict[str, Any], overwrite: bool = True) -> dict[str, Any]:
    """
    合并多个字典

    Args:
        *dicts: 要合并的字典列表
        overwrite: 是否覆盖重复的键

    Returns:
        Dict[str, Any]: 合并后的字典
    """
    result = {}

    for d in dicts:
        if not isinstance(d, dict):
            continue

        for key, value in d.items():
            if overwrite or key not in result:
                result[key] = value

    return result
