"""
MiniCRM 数据库初始化器

负责插入初始数据和配置。
"""

import sqlite3
from datetime import datetime

from ...core.exceptions import DatabaseError


class DatabaseInitializer:
    """
    数据库初始化器

    负责插入系统运行所需的初始数据。
    """

    def __init__(self, connection: sqlite3.Connection):
        """
        初始化数据库初始化器

        Args:
            connection: 数据库连接
        """
        self._connection = connection

    def insert_initial_data(self) -> None:
        """插入初始数据"""
        try:
            self._insert_customer_types()
            self._insert_quote_statuses()
            self._insert_interaction_types()

        except Exception as e:
            raise DatabaseError(f"插入初始数据失败: {e}") from e

    def _insert_customer_types(self) -> None:
        """插入客户类型初始数据"""
        customer_types = [
            ("生态板客户", "主要采购生态板材的客户"),
            ("家具板客户", "主要采购家具板材的客户"),
            ("阻燃板客户", "主要采购阻燃板材的客户"),
            ("综合客户", "采购多种板材的综合性客户"),
            ("零售客户", "小批量采购的零售客户"),
            ("批发客户", "大批量采购的批发客户"),
        ]

        for name, description in customer_types:
            # 检查是否已存在
            existing = self._connection.execute(
                "SELECT id FROM customer_types WHERE name = ?", (name,)
            ).fetchone()

            if not existing:
                self._connection.execute(
                    "INSERT INTO customer_types (name, description) VALUES (?, ?)",
                    (name, description),
                )

    def _insert_quote_statuses(self) -> None:
        """插入报价状态初始数据"""
        quote_statuses = [
            ("draft", "草稿 - 报价正在编辑中"),
            ("sent", "已发送 - 报价已发送给客户"),
            ("accepted", "已接受 - 客户已接受报价"),
            ("rejected", "已拒绝 - 客户拒绝了报价"),
            ("expired", "已过期 - 报价已过有效期"),
            ("converted", "已转换 - 报价已转换为合同"),
            ("cancelled", "已取消 - 报价被取消"),
        ]

        for name, description in quote_statuses:
            # 检查是否已存在
            existing = self._connection.execute(
                "SELECT id FROM quote_statuses WHERE name = ?", (name,)
            ).fetchone()

            if not existing:
                self._connection.execute(
                    "INSERT INTO quote_statuses (name, description) VALUES (?, ?)",
                    (name, description),
                )

    def _insert_interaction_types(self) -> None:
        """插入互动类型初始数据"""
        interaction_types = [
            ("phone_call", "电话沟通 - 通过电话进行的沟通"),
            ("email", "邮件沟通 - 通过邮件进行的沟通"),
            ("meeting", "会面 - 面对面的会议或拜访"),
            ("quote_request", "报价请求 - 客户请求报价"),
            ("order_inquiry", "订单咨询 - 关于订单的咨询"),
            ("complaint", "投诉 - 客户投诉或问题反馈"),
            ("follow_up", "跟进 - 主动跟进客户"),
            ("contract_negotiation", "合同谈判 - 合同条款谈判"),
            ("payment_reminder", "付款提醒 - 提醒客户付款"),
            ("delivery_coordination", "交付协调 - 协调产品交付"),
            ("quality_feedback", "质量反馈 - 产品质量相关反馈"),
            ("technical_support", "技术支持 - 提供技术支持服务"),
            ("market_research", "市场调研 - 市场信息收集"),
            ("relationship_maintenance", "关系维护 - 客户关系维护活动"),
        ]

        for name, description in interaction_types:
            # 检查是否已存在
            existing = self._connection.execute(
                "SELECT id FROM interaction_types WHERE name = ?", (name,)
            ).fetchone()

            if not existing:
                self._connection.execute(
                    "INSERT INTO interaction_types (name, description) VALUES (?, ?)",
                    (name, description),
                )

    def insert_sample_data(self) -> None:
        """插入示例数据（用于开发和测试）"""
        try:
            self._insert_sample_customers()
            self._insert_sample_suppliers()
            self._insert_sample_quotes()

        except Exception as e:
            raise DatabaseError(f"插入示例数据失败: {e}") from e

    def _insert_sample_customers(self) -> None:
        """插入示例客户数据"""
        # 获取客户类型ID
        customer_type_ids = {}
        types = self._connection.execute(
            "SELECT id, name FROM customer_types"
        ).fetchall()
        for type_row in types:
            customer_type_ids[type_row["name"]] = type_row["id"]

        sample_customers = [
            {
                "name": "绿色家居有限公司",
                "phone": "021-12345678",
                "email": "contact@greenhome.com",
                "address": "上海市浦东新区张江高科技园区",
                "customer_type_id": customer_type_ids.get("生态板客户"),
                "contact_person": "张经理",
                "notes": "长期合作客户，信誉良好",
            },
            {
                "name": "美式家具制造厂",
                "phone": "0755-87654321",
                "email": "info@americanfurniture.com",
                "address": "深圳市宝安区西乡街道",
                "customer_type_id": customer_type_ids.get("家具板客户"),
                "contact_person": "李总",
                "notes": "高端家具制造商，对质量要求严格",
            },
            {
                "name": "安全建材贸易公司",
                "phone": "010-98765432",
                "email": "sales@safebuild.com",
                "address": "北京市朝阳区建国门外大街",
                "customer_type_id": customer_type_ids.get("阻燃板客户"),
                "contact_person": "王主任",
                "notes": "专注于阻燃材料，政府项目较多",
            },
        ]

        for customer in sample_customers:
            # 检查是否已存在
            existing = self._connection.execute(
                "SELECT id FROM customers WHERE name = ?", (customer["name"],)
            ).fetchone()

            if not existing:
                self._connection.execute(
                    """
                    INSERT INTO customers (
                        name, phone, email, address, customer_type_id,
                        contact_person, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        customer["name"],
                        customer["phone"],
                        customer["email"],
                        customer["address"],
                        customer["customer_type_id"],
                        customer["contact_person"],
                        customer["notes"],
                    ),
                )

    def _insert_sample_suppliers(self) -> None:
        """插入示例供应商数据"""
        sample_suppliers = [
            {
                "name": "优质木材供应商",
                "phone": "0571-11111111",
                "email": "supply@qualitywood.com",
                "address": "浙江省杭州市余杭区",
                "contact_person": "陈总",
                "quality_rating": 4.5,
                "cooperation_years": 3,
                "notes": "木材质量稳定，交期准时",
            },
            {
                "name": "环保胶水厂",
                "phone": "0532-22222222",
                "email": "info@ecoglue.com",
                "address": "山东省青岛市城阳区",
                "contact_person": "刘厂长",
                "quality_rating": 4.2,
                "cooperation_years": 2,
                "notes": "环保胶水专业生产商",
            },
        ]

        for supplier in sample_suppliers:
            # 检查是否已存在
            existing = self._connection.execute(
                "SELECT id FROM suppliers WHERE name = ?", (supplier["name"],)
            ).fetchone()

            if not existing:
                self._connection.execute(
                    """
                    INSERT INTO suppliers (
                        name, phone, email, address, contact_person,
                        quality_rating, cooperation_years, notes
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        supplier["name"],
                        supplier["phone"],
                        supplier["email"],
                        supplier["address"],
                        supplier["contact_person"],
                        supplier["quality_rating"],
                        supplier["cooperation_years"],
                        supplier["notes"],
                    ),
                )

    def _insert_sample_quotes(self) -> None:
        """插入示例报价数据"""
        # 获取客户ID和状态ID
        customers = self._connection.execute(
            "SELECT id, name FROM customers LIMIT 1"
        ).fetchone()
        if not customers:
            return

        statuses = self._connection.execute(
            "SELECT id, name FROM quote_statuses WHERE name = 'draft'"
        ).fetchone()
        if not statuses:
            return

        sample_quote = {
            "quote_number": "QT20250115001",
            "customer_id": customers["id"],
            "customer_name": customers["name"],
            "total_amount": 15000.00,
            "quote_date": datetime.now().date(),
            "valid_until": datetime.now().date(),
            "quote_status_id": statuses["id"],
            "notes": "示例报价单",
        }

        # 检查是否已存在
        existing = self._connection.execute(
            "SELECT id FROM quotes WHERE quote_number = ?",
            (sample_quote["quote_number"],),
        ).fetchone()

        if not existing:
            self._connection.execute(
                """
                INSERT INTO quotes (
                    quote_number, customer_id, customer_name, total_amount,
                    quote_date, valid_until, quote_status_id, notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    sample_quote["quote_number"],
                    sample_quote["customer_id"],
                    sample_quote["customer_name"],
                    sample_quote["total_amount"],
                    sample_quote["quote_date"],
                    sample_quote["valid_until"],
                    sample_quote["quote_status_id"],
                    sample_quote["notes"],
                ),
            )
