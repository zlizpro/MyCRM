"""
MiniCRM 报价模板管理服务

提供报价模板的管理功能,包括:
- 模板的创建、编辑、删除
- 模板样式和布局配置
- 模板预览和应用
- 默认模板管理

设计原则:
- 支持多种模板样式
- 可配置的模板参数
- 遵循MiniCRM开发标准
- 提供清晰的接口和错误处理
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from minicrm.core.exceptions import ServiceError, ValidationError


class QuoteTemplateService:
    """
    报价模板管理服务

    管理报价PDF模板的创建、编辑、删除和应用.
    """

    def __init__(self, templates_dir: str | None = None):
        """
        初始化模板服务

        Args:
            templates_dir: 模板存储目录,默认为用户数据目录
        """
        self._logger = logging.getLogger(__name__)

        # 设置模板存储目录
        if templates_dir:
            self._templates_dir = Path(templates_dir)
        else:
            # 使用用户数据目录
            import os

            if os.name == "nt":  # Windows
                base_dir = Path.home() / "AppData" / "Local" / "MiniCRM"
            else:  # macOS/Linux
                base_dir = Path.home() / ".minicrm"

            self._templates_dir = base_dir / "templates"

        # 确保目录存在
        self._templates_dir.mkdir(parents=True, exist_ok=True)

        # 初始化默认模板
        self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """初始化默认模板"""
        try:
            default_templates = self._get_default_template_configs()

            for template_id, template_config in default_templates.items():
                template_file = self._templates_dir / f"{template_id}.json"

                # 如果模板文件不存在,创建默认模板
                if not template_file.exists():
                    self._save_template_config(template_id, template_config)
                    self._logger.info(f"创建默认模板: {template_id}")

        except Exception as e:
            self._logger.error(f"初始化默认模板失败: {e}")

    def _get_default_template_configs(self) -> dict[str, dict[str, Any]]:
        """获取默认模板配置"""
        return {
            "standard": {
                "id": "standard",
                "name": "标准模板",
                "description": "适用于一般报价的标准模板",
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_default": True,
                "is_system": True,
                "config": {
                    "page_size": "A4",
                    "margins": {"top": 2.0, "bottom": 2.0, "left": 2.0, "right": 2.0},
                    "fonts": {
                        "default": "SimHei",
                        "title": "SimHei",
                        "content": "SimHei",
                    },
                    "colors": {
                        "primary": "#1f4e79",
                        "secondary": "#4472c4",
                        "accent": "#70ad47",
                        "text": "#000000",
                        "background": "#ffffff",
                    },
                    "header": {
                        "show_logo": True,
                        "company_name": "MiniCRM 板材销售管理系统",
                        "title": "产品报价单",
                        "title_size": 18,
                        "subtitle_size": 12,
                    },
                    "customer_info": {
                        "show_section": True,
                        "title": "客户信息",
                        "fields": [
                            "customer_name",
                            "contact_person",
                            "quote_number",
                            "quote_date",
                            "valid_until",
                        ],
                    },
                    "quote_info": {
                        "show_section": True,
                        "title": "报价详情",
                        "fields": [
                            "quote_type",
                            "quote_status",
                            "validity_days",
                            "remaining_days",
                        ],
                    },
                    "items_table": {
                        "show_section": True,
                        "title": "产品清单",
                        "columns": [
                            {"key": "sequence", "title": "序号", "width": 1.0},
                            {"key": "product_name", "title": "产品名称", "width": 4.0},
                            {"key": "specification", "title": "规格型号", "width": 3.0},
                            {"key": "unit", "title": "单位", "width": 1.5},
                            {"key": "quantity", "title": "数量", "width": 1.5},
                            {"key": "unit_price", "title": "单价", "width": 2.0},
                            {"key": "total", "title": "小计", "width": 2.0},
                        ],
                        "row_height": 0.8,
                        "header_color": "#1f4e79",
                        "alternate_row_color": "#f2f2f2",
                    },
                    "totals": {
                        "show_section": True,
                        "title": "汇总信息",
                        "fields": ["subtotal_amount", "tax_amount", "total_amount"],
                        "highlight_total": True,
                    },
                    "terms": {
                        "show_section": True,
                        "title": "条款信息",
                        "fields": ["payment_terms", "delivery_terms", "notes"],
                    },
                    "footer": {
                        "show_section": True,
                        "show_signature": True,
                        "show_company_info": True,
                        "show_timestamp": True,
                    },
                },
            },
            "professional": {
                "id": "professional",
                "name": "专业模板",
                "description": "适用于正式商务报价的专业模板",
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_default": False,
                "is_system": True,
                "config": {
                    "page_size": "A4",
                    "margins": {"top": 2.5, "bottom": 2.5, "left": 2.5, "right": 2.5},
                    "fonts": {
                        "default": "Microsoft-YaHei",
                        "title": "Microsoft-YaHei",
                        "content": "Microsoft-YaHei",
                    },
                    "colors": {
                        "primary": "#2c3e50",
                        "secondary": "#34495e",
                        "accent": "#3498db",
                        "text": "#2c3e50",
                        "background": "#ffffff",
                    },
                    "header": {
                        "show_logo": True,
                        "company_name": "MiniCRM 专业版",
                        "title": "商务报价书",
                        "title_size": 20,
                        "subtitle_size": 14,
                    },
                    "customer_info": {
                        "show_section": True,
                        "title": "客户信息",
                        "fields": [
                            "customer_name",
                            "contact_person",
                            "quote_number",
                            "quote_date",
                            "valid_until",
                        ],
                    },
                    "quote_info": {
                        "show_section": True,
                        "title": "报价信息",
                        "fields": ["quote_type", "quote_status", "validity_days"],
                    },
                    "items_table": {
                        "show_section": True,
                        "title": "产品明细",
                        "columns": [
                            {"key": "sequence", "title": "项目", "width": 1.0},
                            {"key": "product_name", "title": "产品名称", "width": 4.5},
                            {"key": "specification", "title": "规格", "width": 3.0},
                            {"key": "unit", "title": "单位", "width": 1.0},
                            {"key": "quantity", "title": "数量", "width": 1.5},
                            {"key": "unit_price", "title": "单价", "width": 2.0},
                            {"key": "total", "title": "金额", "width": 2.0},
                        ],
                        "row_height": 1.0,
                        "header_color": "#2c3e50",
                        "alternate_row_color": "#ecf0f1",
                    },
                    "totals": {
                        "show_section": True,
                        "title": "费用汇总",
                        "fields": ["subtotal_amount", "tax_amount", "total_amount"],
                        "highlight_total": True,
                    },
                    "terms": {
                        "show_section": True,
                        "title": "商务条款",
                        "fields": ["payment_terms", "delivery_terms", "notes"],
                    },
                    "footer": {
                        "show_section": True,
                        "show_signature": True,
                        "show_company_info": True,
                        "show_timestamp": True,
                    },
                },
            },
            "simple": {
                "id": "simple",
                "name": "简洁模板",
                "description": "适用于快速报价的简洁模板",
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "is_default": False,
                "is_system": True,
                "config": {
                    "page_size": "A4",
                    "margins": {"top": 1.5, "bottom": 1.5, "left": 1.5, "right": 1.5},
                    "fonts": {
                        "default": "SimSun",
                        "title": "SimSun",
                        "content": "SimSun",
                    },
                    "colors": {
                        "primary": "#333333",
                        "secondary": "#666666",
                        "accent": "#999999",
                        "text": "#000000",
                        "background": "#ffffff",
                    },
                    "header": {
                        "show_logo": False,
                        "company_name": "MiniCRM",
                        "title": "报价单",
                        "title_size": 16,
                        "subtitle_size": 10,
                    },
                    "customer_info": {
                        "show_section": True,
                        "title": "基本信息",
                        "fields": ["customer_name", "quote_number", "quote_date"],
                    },
                    "quote_info": {"show_section": False},
                    "items_table": {
                        "show_section": True,
                        "title": "产品列表",
                        "columns": [
                            {"key": "sequence", "title": "No.", "width": 0.8},
                            {"key": "product_name", "title": "产品", "width": 5.0},
                            {"key": "quantity", "title": "数量", "width": 1.5},
                            {"key": "unit_price", "title": "单价", "width": 2.0},
                            {"key": "total", "title": "小计", "width": 2.0},
                        ],
                        "row_height": 0.6,
                        "header_color": "#666666",
                        "alternate_row_color": "#f9f9f9",
                    },
                    "totals": {
                        "show_section": True,
                        "title": "合计",
                        "fields": ["total_amount"],
                        "highlight_total": True,
                    },
                    "terms": {
                        "show_section": True,
                        "title": "备注",
                        "fields": ["notes"],
                    },
                    "footer": {
                        "show_section": True,
                        "show_signature": False,
                        "show_company_info": False,
                        "show_timestamp": True,
                    },
                },
            },
        }

    def get_all_templates(self) -> list[dict[str, Any]]:
        """获取所有模板列表"""
        try:
            templates = []

            for template_file in self._templates_dir.glob("*.json"):
                try:
                    template_config = self._load_template_config(template_file.stem)
                    if template_config:
                        # 只返回基本信息,不包含详细配置
                        template_info = {
                            "id": template_config.get("id"),
                            "name": template_config.get("name"),
                            "description": template_config.get("description"),
                            "version": template_config.get("version"),
                            "created_at": template_config.get("created_at"),
                            "updated_at": template_config.get("updated_at"),
                            "is_default": template_config.get("is_default", False),
                            "is_system": template_config.get("is_system", False),
                        }
                        templates.append(template_info)
                except Exception as e:
                    self._logger.warning(f"加载模板失败 {template_file}: {e}")

            # 按创建时间排序
            templates.sort(key=lambda x: x.get("created_at", ""), reverse=True)

            return templates

        except Exception as e:
            self._logger.error(f"获取模板列表失败: {e}")
            raise ServiceError(f"获取模板列表失败: {e}") from e

    def get_template(self, template_id: str) -> dict[str, Any] | None:
        """获取指定模板的完整配置"""
        try:
            return self._load_template_config(template_id)
        except Exception as e:
            self._logger.error(f"获取模板失败 {template_id}: {e}")
            return None

    def create_template(
        self, template_data: dict[str, Any], base_template_id: str | None = None
    ) -> str:
        """
        创建新模板

        Args:
            template_data: 模板数据
            base_template_id: 基础模板ID(用于复制)

        Returns:
            str: 新模板的ID
        """
        try:
            # 验证模板数据
            self._validate_template_data(template_data)

            template_id = template_data.get("id")
            if not template_id:
                # 生成模板ID
                template_id = self._generate_template_id(template_data.get("name", ""))
                template_data["id"] = template_id

            # 检查模板是否已存在
            if self._template_exists(template_id):
                raise ValidationError(f"模板ID已存在: {template_id}")

            # 如果指定了基础模板,复制其配置
            if base_template_id:
                base_template = self.get_template(base_template_id)
                if base_template:
                    # 合并配置
                    template_data["config"] = {
                        **base_template.get("config", {}),
                        **template_data.get("config", {}),
                    }

            # 设置创建时间
            now = datetime.now().isoformat()
            template_data.update(
                {
                    "created_at": now,
                    "updated_at": now,
                    "version": template_data.get("version", "1.0"),
                    "is_default": False,
                    "is_system": False,
                }
            )

            # 保存模板
            self._save_template_config(template_id, template_data)

            self._logger.info(f"创建模板成功: {template_id}")
            return template_id

        except Exception as e:
            self._logger.error(f"创建模板失败: {e}")
            raise ServiceError(f"创建模板失败: {e}") from e

    def update_template(self, template_id: str, template_data: dict[str, Any]) -> bool:
        """更新模板"""
        try:
            # 检查模板是否存在
            if not self._template_exists(template_id):
                raise ValidationError(f"模板不存在: {template_id}")

            # 获取现有模板
            existing_template = self.get_template(template_id)
            if not existing_template:
                raise ServiceError(f"无法加载现有模板: {template_id}")

            # 检查是否为系统模板
            if existing_template.get("is_system", False):
                raise ValidationError("系统模板不能修改")

            # 验证模板数据
            self._validate_template_data(template_data)

            # 合并数据
            updated_template = {
                **existing_template,
                **template_data,
                "id": template_id,  # 确保ID不变
                "updated_at": datetime.now().isoformat(),
            }

            # 保存模板
            self._save_template_config(template_id, updated_template)

            self._logger.info(f"更新模板成功: {template_id}")
            return True

        except Exception as e:
            self._logger.error(f"更新模板失败 {template_id}: {e}")
            raise ServiceError(f"更新模板失败: {e}") from e

    def delete_template(self, template_id: str) -> bool:
        """删除模板"""
        try:
            # 检查模板是否存在
            if not self._template_exists(template_id):
                raise ValidationError(f"模板不存在: {template_id}")

            # 获取模板信息
            template = self.get_template(template_id)
            if not template:
                raise ServiceError(f"无法加载模板: {template_id}")

            # 检查是否为系统模板
            if template.get("is_system", False):
                raise ValidationError("系统模板不能删除")

            # 检查是否为默认模板
            if template.get("is_default", False):
                raise ValidationError("默认模板不能删除")

            # 删除模板文件
            template_file = self._templates_dir / f"{template_id}.json"
            template_file.unlink()

            self._logger.info(f"删除模板成功: {template_id}")
            return True

        except Exception as e:
            self._logger.error(f"删除模板失败 {template_id}: {e}")
            raise ServiceError(f"删除模板失败: {e}") from e

    def duplicate_template(
        self, source_template_id: str, new_name: str, new_description: str | None = None
    ) -> str:
        """复制模板"""
        try:
            # 获取源模板
            source_template = self.get_template(source_template_id)
            if not source_template:
                raise ValidationError(f"源模板不存在: {source_template_id}")

            # 创建新模板数据
            new_template_data = {
                **source_template,
                "name": new_name,
                "description": new_description
                or f"复制自 {source_template.get('name', '')}",
                "is_default": False,
                "is_system": False,
            }

            # 移除ID,让系统自动生成
            new_template_data.pop("id", None)

            # 创建新模板
            return self.create_template(new_template_data)

        except Exception as e:
            self._logger.error(f"复制模板失败 {source_template_id}: {e}")
            raise ServiceError(f"复制模板失败: {e}") from e

    def set_default_template(self, template_id: str) -> bool:
        """设置默认模板"""
        try:
            # 检查模板是否存在
            if not self._template_exists(template_id):
                raise ValidationError(f"模板不存在: {template_id}")

            # 清除所有模板的默认标记
            for template_file in self._templates_dir.glob("*.json"):
                try:
                    template_config = self._load_template_config(template_file.stem)
                    if template_config and template_config.get("is_default", False):
                        template_config["is_default"] = False
                        self._save_template_config(template_file.stem, template_config)
                except Exception as e:
                    self._logger.warning(f"清除默认标记失败 {template_file}: {e}")

            # 设置新的默认模板
            template = self.get_template(template_id)
            if template:
                template["is_default"] = True
                template["updated_at"] = datetime.now().isoformat()
                self._save_template_config(template_id, template)

            self._logger.info(f"设置默认模板成功: {template_id}")
            return True

        except Exception as e:
            self._logger.error(f"设置默认模板失败 {template_id}: {e}")
            raise ServiceError(f"设置默认模板失败: {e}") from e

    def get_default_template(self) -> dict[str, Any] | None:
        """获取默认模板"""
        try:
            templates = self.get_all_templates()

            for template in templates:
                if template.get("is_default", False):
                    return self.get_template(template["id"])

            # 如果没有默认模板,返回第一个系统模板
            for template in templates:
                if template.get("is_system", False):
                    return self.get_template(template["id"])

            return None

        except Exception as e:
            self._logger.error(f"获取默认模板失败: {e}")
            return None

    def _load_template_config(self, template_id: str) -> dict[str, Any] | None:
        """加载模板配置"""
        try:
            template_file = self._templates_dir / f"{template_id}.json"

            if not template_file.exists():
                return None

            with open(template_file, encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            self._logger.error(f"加载模板配置失败 {template_id}: {e}")
            return None

    def _save_template_config(
        self, template_id: str, template_config: dict[str, Any]
    ) -> None:
        """保存模板配置"""
        try:
            template_file = self._templates_dir / f"{template_id}.json"

            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(template_config, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self._logger.error(f"保存模板配置失败 {template_id}: {e}")
            raise ServiceError(f"保存模板配置失败: {e}") from e

    def _template_exists(self, template_id: str) -> bool:
        """检查模板是否存在"""
        template_file = self._templates_dir / f"{template_id}.json"
        return template_file.exists()

    def _generate_template_id(self, template_name: str) -> str:
        """生成模板ID"""
        import re

        # 基于模板名称生成ID
        base_id = re.sub(r"[^\w\-_]", "", template_name.lower().replace(" ", "_"))

        if not base_id:
            base_id = "template"

        # 确保ID唯一
        template_id = base_id
        counter = 1

        while self._template_exists(template_id):
            template_id = f"{base_id}_{counter}"
            counter += 1

        return template_id

    def _validate_template_data(self, template_data: dict[str, Any]) -> None:
        """验证模板数据"""
        required_fields = ["name", "description"]

        for field in required_fields:
            if not template_data.get(field):
                raise ValidationError(f"缺少必要字段: {field}")

        # 验证模板名称长度
        name = template_data.get("name", "")
        if len(name) < 2 or len(name) > 50:
            raise ValidationError("模板名称长度必须在2-50个字符之间")

        # 验证描述长度
        description = template_data.get("description", "")
        if len(description) > 200:
            raise ValidationError("模板描述不能超过200个字符")
