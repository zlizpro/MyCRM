"""
供应商数据访问对象测试

测试SupplierDAO的所有方法，包括：
- 基本CRUD操作
- 搜索和查询功能
- 财务相关操作
- 交流事件管理
- 异常处理和边界条件
"""

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from minicrm.core.exceptions import DatabaseError
from minicrm.data.dao.supplier_dao import SupplierDAO
from minicrm.data.database import DatabaseManager


class TestSupplierDAO:
    """供应商DAO测试类"""

    @pytest.fixture
    def mock_db_manager(self):
        """创建模拟数据库管理器"""
        mock_db = Mock(spec=DatabaseManager)
        return mock_db

    @pytest.fixture
    def supplier_dao(self, mock_db_manager):
        """创建供应商DAO实例"""
        return SupplierDAO(mock_db_manager)

    @pytest.fixture
    def sample_supplier_data(self):
        """示例供应商数据"""
        return {
            "name": "测试供应商",
            "contact_person": "李经理",
            "phone": "13987654321",
            "email": "supplier@example.com",
            "address": "北京市朝阳区",
            "quality_rating": 4.5,
            "cooperation_years": 3,
            "notes": "优质供应商",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    @pytest.fixture
    def sample_supplier_row(self):
        """示例供应商数据库行"""
        return (
            1,
            "测试供应商",
            "13987654321",
            "supplier@example.com",
            "北京市朝阳区",
            "李经理",
            4.5,
            3,
            "优质供应商",
            "2025-01-15 10:00:00",
            "2025-01-15 10:00:00",
        )

    # ==================== 基本CRUD操作测试 ====================

    def test_insert_success(self, supplier_dao, mock_db_manager, sample_supplier_data):
        """测试成功插入供应商数据"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 执行插入
        result = supplier_dao.insert(sample_supplier_data)

        # 验证结果
        assert result == 1
        mock_db_manager.execute_insert.assert_called_once()

        # 验证SQL和参数
        call_args = mock_db_manager.execute_insert.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO suppliers" in sql
        assert params[0] == "测试供应商"
        assert params[1] == "李经理"
        assert params[2] == "13987654321"

    def test_insert_database_error(
        self, supplier_dao, mock_db_manager, sample_supplier_data
    ):
        """测试插入时数据库错误"""
        # 设置模拟抛出异常
        mock_db_manager.execute_insert.side_effect = Exception("数据库连接失败")

        # 验证抛出DatabaseError
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.insert(sample_supplier_data)

        assert "插入供应商数据失败" in str(exc_info.value)

    def test_get_by_id_success(
        self, supplier_dao, mock_db_manager, sample_supplier_row
    ):
        """测试成功根据ID获取供应商"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [sample_supplier_row]

        # 执行查询
        result = supplier_dao.get_by_id(1)

        # 验证结果
        assert result is not None
        assert result["id"] == 1
        assert result["name"] == "测试供应商"
        assert result["contact_person"] == "李经理"

        # 验证调用
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT * FROM suppliers WHERE id = ?", (1,)
        )

    def test_get_by_id_not_found(self, supplier_dao, mock_db_manager):
        """测试根据ID获取不存在的供应商"""
        # 设置模拟返回空结果
        mock_db_manager.execute_query.return_value = []

        # 执行查询
        result = supplier_dao.get_by_id(999)

        # 验证结果
        assert result is None

    def test_update_success(self, supplier_dao, mock_db_manager):
        """测试成功更新供应商数据"""
        # 设置模拟返回值
        mock_db_manager.execute_update.return_value = 1

        # 准备更新数据
        update_data = {
            "name": "更新后的供应商名",
            "quality_rating": 4.8,
            "notes": "更新后的备注",
        }

        # 执行更新
        result = supplier_dao.update(1, update_data)

        # 验证结果
        assert result is True
        mock_db_manager.execute_update.assert_called_once()

    def test_delete_success(self, supplier_dao, mock_db_manager):
        """测试成功删除供应商"""
        # 设置模拟返回值
        mock_db_manager.execute_update.return_value = 1

        # 执行删除
        result = supplier_dao.delete(1)

        # 验证结果
        assert result is True
        mock_db_manager.execute_update.assert_called_once_with(
            "DELETE FROM suppliers WHERE id = ?", (1,)
        )

    # ==================== 搜索和查询功能测试 ====================

    def test_search_with_conditions(
        self, supplier_dao, mock_db_manager, sample_supplier_row
    ):
        """测试带条件搜索"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [sample_supplier_row]

        # 执行搜索
        conditions = {"quality_rating": 4.5, "name": "测试供应商"}
        result = supplier_dao.search(conditions=conditions)

        # 验证结果
        assert len(result) == 1
        assert result[0]["name"] == "测试供应商"

        # 验证SQL构建
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]

        assert "WHERE" in sql
        assert "quality_rating = ?" in sql
        assert "name = ?" in sql

    def test_count_with_conditions(self, supplier_dao, mock_db_manager):
        """测试带条件统计"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [(3,)]

        # 执行统计
        conditions = {"quality_rating": 4.0}
        result = supplier_dao.count(conditions=conditions)

        # 验证结果
        assert result == 3

    def test_search_by_name_or_contact(
        self, supplier_dao, mock_db_manager, sample_supplier_row
    ):
        """测试根据名称或联系方式搜索"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [sample_supplier_row]

        # 执行搜索
        result = supplier_dao.search_by_name_or_contact("测试")

        # 验证结果
        assert len(result) == 1
        assert result[0]["name"] == "测试供应商"

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "name LIKE ?" in sql
        assert "contact_person LIKE ?" in sql
        assert "phone LIKE ?" in sql
        assert "%测试%" in params

    def test_get_by_quality_rating(
        self, supplier_dao, mock_db_manager, sample_supplier_row
    ):
        """测试根据质量评级获取供应商"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [sample_supplier_row]

        # 执行查询
        result = supplier_dao.get_by_quality_rating(4.0)

        # 验证结果
        assert len(result) == 1
        assert result[0]["quality_rating"] == 4.5

        # 验证SQL调用
        mock_db_manager.execute_query.assert_called_once_with(
            "SELECT * FROM suppliers WHERE quality_rating >= ? ORDER BY quality_rating DESC",
            (4.0,),
        )

    def test_get_statistics(self, supplier_dao, mock_db_manager):
        """测试获取供应商统计信息"""
        # 设置模拟返回值
        mock_db_manager.execute_query.side_effect = [
            [(10,)],  # 总供应商数
            [("优秀", 3), ("良好", 5), ("一般", 2)],  # 按评级统计
            [(4.2,)],  # 平均评级
        ]

        # 执行统计
        result = supplier_dao.get_statistics()

        # 验证结果
        assert result["total_suppliers"] == 10
        assert result["by_rating"]["优秀"] == 3
        assert result["by_rating"]["良好"] == 5
        assert result["avg_quality_rating"] == 4.2

        # 验证调用次数
        assert mock_db_manager.execute_query.call_count == 3

    # ==================== 交流事件管理测试 ====================

    def test_insert_communication_event(self, supplier_dao, mock_db_manager):
        """测试插入交流事件"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备事件数据
        event_data = {
            "supplier_id": 1,
            "event_number": "EVT001",
            "event_type": "inquiry",
            "title": "价格询问",
            "content": "询问产品价格",
            "priority": "medium",
            "status": "pending",
            "created_at": datetime.now(),
            "due_time": datetime.now(),
            "created_by": "admin",
            "urgency_level": 2,
        }

        # 执行插入
        result = supplier_dao.insert_communication_event(event_data)

        # 验证结果
        assert result == 1
        mock_db_manager.execute_insert.assert_called_once()

    def test_get_communication_event(self, supplier_dao, mock_db_manager):
        """测试获取交流事件"""
        # 设置模拟返回值
        event_row = (
            1,
            1,
            "EVT001",
            "inquiry",
            "价格询问",
            "询问产品价格",
            "medium",
            "pending",
            "2025-01-15",
            "2025-01-16",
            "admin",
            2,
        )
        mock_db_manager.execute_query.return_value = [event_row]

        # 执行查询
        result = supplier_dao.get_communication_event(1)

        # 验证结果
        assert result is not None
        assert result["id"] == 1

    def test_update_communication_event(self, supplier_dao, mock_db_manager):
        """测试更新交流事件"""
        # 设置模拟返回值
        mock_db_manager.execute_update.return_value = 1

        # 准备更新数据
        update_data = {"status": "completed", "content": "已完成处理"}

        # 执行更新
        result = supplier_dao.update_communication_event(1, update_data)

        # 验证结果
        assert result is True

    def test_get_communication_events_with_filters(self, supplier_dao, mock_db_manager):
        """测试获取交流事件列表（带筛选）"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = []

        # 执行查询
        result = supplier_dao.get_communication_events(
            supplier_id=1,
            start_date=datetime(2025, 1, 1),
            status_filter=["pending", "in_progress"],
        )

        # 验证结果
        assert result == []

        # 验证SQL构建
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]

        assert "supplier_id = ?" in sql
        assert "created_at >= ?" in sql
        assert "status IN" in sql

    def test_get_daily_event_count(self, supplier_dao, mock_db_manager):
        """测试获取日事件数量"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = [(5,)]

        # 执行查询
        result = supplier_dao.get_daily_event_count(1, "2025-01-15")

        # 验证结果
        assert result == 5

    def test_insert_event_processing_result(self, supplier_dao, mock_db_manager):
        """测试插入事件处理结果"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备处理结果数据
        result_data = {
            "event_id": 1,
            "solution": "提供了详细报价",
            "result": "客户满意",
            "satisfaction_rating": 5,
            "processing_time": 30,
            "processed_by": "admin",
            "follow_up_required": False,
        }

        # 执行插入
        result = supplier_dao.insert_event_processing_result(result_data)

        # 验证结果
        assert result == 1

    # ==================== 财务相关功能测试 ====================

    def test_insert_payable(self, supplier_dao, mock_db_manager):
        """测试插入应付账款记录"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备应付账款数据
        payable_data = {
            "supplier_id": 1,
            "amount": 50000.0,
            "due_date": date(2025, 2, 15),
            "status": "pending",
            "description": "采购订单应付款",
            "created_at": datetime.now(),
        }

        # 执行插入
        result = supplier_dao.insert_payable(payable_data)

        # 验证结果
        assert result == 1
        mock_db_manager.execute_insert.assert_called_once()

        # 验证SQL和参数
        call_args = mock_db_manager.execute_insert.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "INSERT INTO financial_records" in sql
        assert "'payable'" in sql
        assert params[0] == 1  # supplier_id
        assert params[1] == 50000.0  # amount

    def test_insert_supplier_payment(self, supplier_dao, mock_db_manager):
        """测试插入供应商付款记录"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备付款数据
        payment_data = {
            "supplier_id": 1,
            "amount": 25000.0,
            "payment_date": date(2025, 1, 15),
            "description": "部分付款",
            "created_at": datetime.now(),
        }

        # 执行插入
        result = supplier_dao.insert_supplier_payment(payment_data)

        # 验证结果
        assert result == 1

        # 验证SQL构建
        call_args = mock_db_manager.execute_insert.call_args
        sql = call_args[0][0]

        assert "INSERT INTO financial_records" in sql
        assert "'payment'" in sql
        assert "'paid'" in sql

    def test_get_payables_by_supplier(self, supplier_dao, mock_db_manager):
        """测试获取特定供应商的应付账款"""
        # 设置模拟返回值
        payable_row = (
            1,
            None,
            1,
            None,
            "payable",
            50000.0,
            "2025-02-15",
            None,
            "pending",
            "采购订单",
            "2025-01-15",
            None,
            "测试供应商",
        )
        mock_db_manager.execute_query.return_value = [payable_row]

        # 执行查询
        result = supplier_dao.get_payables(supplier_id=1)

        # 验证结果
        assert len(result) == 1

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "WHERE fr.supplier_id = ?" in sql
        assert "fr.record_type = 'payable'" in sql
        assert params == (1,)

    def test_get_all_payables(self, supplier_dao, mock_db_manager):
        """测试获取所有应付账款"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = []

        # 执行查询
        result = supplier_dao.get_payables()

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "WHERE fr.supplier_id = ?" not in sql
        assert "fr.record_type = 'payable'" in sql
        assert params == ()

    def test_get_supplier_payments(self, supplier_dao, mock_db_manager):
        """测试获取供应商付款记录"""
        # 设置模拟返回值
        payment_row = (
            1,
            None,
            1,
            None,
            "payment",
            25000.0,
            None,
            "2025-01-15",
            "paid",
            "付款",
            "2025-01-15",
            None,
            "测试供应商",
        )
        mock_db_manager.execute_query.return_value = [payment_row]

        # 执行查询
        result = supplier_dao.get_supplier_payments(supplier_id=1)

        # 验证结果
        assert len(result) == 1

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]

        assert "fr.record_type = 'payment'" in sql

    def test_get_payables_summary(self, supplier_dao, mock_db_manager):
        """测试获取应付账款汇总"""
        # 设置模拟返回值
        mock_db_manager.execute_query.side_effect = [
            [(100000.0,)],  # 总应付账款
            [(30000.0,)],  # 逾期应付账款
        ]

        # 执行查询
        result = supplier_dao.get_payables_summary()

        # 验证结果
        assert result["total_amount"] == 100000.0
        assert result["overdue_amount"] == 30000.0

        # 验证调用次数
        assert mock_db_manager.execute_query.call_count == 2

    def test_update_payable_status(self, supplier_dao, mock_db_manager):
        """测试更新应付账款状态"""
        # 设置模拟返回值
        mock_db_manager.execute_update.return_value = 1

        # 执行更新
        result = supplier_dao.update_payable_status(1, "paid")

        # 验证结果
        assert result is True

        # 验证SQL调用
        call_args = mock_db_manager.execute_update.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "UPDATE financial_records" in sql
        assert "SET status = ?" in sql
        assert "record_type = 'payable'" in sql
        assert params == ("paid", 1)

    # ==================== 其他功能测试 ====================

    def test_get_quality_ratings(self, supplier_dao, mock_db_manager):
        """测试获取供应商质量评级记录"""
        # 设置模拟返回值
        rating_row = (1, 1, 4.5, "质量很好", "2025-01-15")
        mock_db_manager.execute_query.return_value = [rating_row]

        # 执行查询
        result = supplier_dao.get_quality_ratings(1)

        # 验证结果
        assert len(result) == 1

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "supplier_quality_ratings" in sql
        assert "supplier_id = ?" in sql
        assert params == (1,)

    def test_get_transaction_history(self, supplier_dao, mock_db_manager):
        """测试获取供应商交易历史"""
        # 设置模拟返回值
        transaction_row = (1, 1, 10000.0, "采购", "2025-01-15")
        mock_db_manager.execute_query.return_value = [transaction_row]

        # 执行查询
        result = supplier_dao.get_transaction_history(1)

        # 验证结果
        assert len(result) == 1

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]

        assert "supplier_transactions" in sql

    def test_get_interaction_history(self, supplier_dao, mock_db_manager):
        """测试获取供应商互动历史"""
        # 设置模拟返回值
        interaction_row = (1, 1, "电话沟通", "讨论价格", "2025-01-15", "admin")
        mock_db_manager.execute_query.return_value = [interaction_row]

        # 执行查询
        result = supplier_dao.get_interaction_history(1)

        # 验证结果
        assert len(result) == 1

    def test_insert_interaction(self, supplier_dao, mock_db_manager):
        """测试插入供应商互动记录"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备互动数据
        interaction_data = {
            "supplier_id": 1,
            "interaction_type": "phone",
            "content": "电话沟通产品规格",
            "created_at": datetime.now(),
            "created_by": "admin",
        }

        # 执行插入
        result = supplier_dao.insert_interaction(interaction_data)

        # 验证结果
        assert result == 1

    def test_get_payment_terms(self, supplier_dao, mock_db_manager):
        """测试获取供应商账期设置"""
        # 设置模拟返回值
        terms_row = (1, 1, 30, "bank_transfer", 0.02, 10, "2025-01-15")
        mock_db_manager.execute_query.return_value = [terms_row]

        # 执行查询
        result = supplier_dao.get_payment_terms(1)

        # 验证结果
        assert result is not None

    def test_insert_payment_terms(self, supplier_dao, mock_db_manager):
        """测试插入供应商账期设置"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备账期数据
        terms_data = {
            "supplier_id": 1,
            "payment_days": 30,
            "payment_method": "bank_transfer",
            "discount_rate": 0.02,
            "discount_days": 10,
            "created_at": datetime.now(),
        }

        # 执行插入
        result = supplier_dao.insert_payment_terms(terms_data)

        # 验证结果
        assert result == 1

    def test_get_pending_payables(self, supplier_dao, mock_db_manager):
        """测试获取待付款应付账款"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = []

        # 执行查询
        result = supplier_dao.get_pending_payables(1)

        # 验证结果
        assert result == []

        # 验证SQL调用
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "status = 'pending'" in sql
        assert "record_type = 'payable'" in sql
        assert params == (1,)

    # ==================== 辅助方法测试 ====================

    def test_row_to_dict_with_keys(self, supplier_dao):
        """测试行转字典（带keys方法的行对象）"""
        # 创建模拟行对象
        mock_row = Mock()
        mock_row.keys.return_value = ["id", "name", "phone"]
        mock_row.__getitem__ = lambda self, key: {
            "id": 1,
            "name": "测试",
            "phone": "123",
        }[key]
        mock_row.__iter__ = lambda self: iter(
            [("id", 1), ("name", "测试"), ("phone", "123")]
        )

        # 模拟dict()构造函数
        with patch("builtins.dict") as mock_dict:
            mock_dict.return_value = {"id": 1, "name": "测试", "phone": "123"}

            # 执行转换
            result = supplier_dao._row_to_dict(mock_row)

            # 验证结果
            assert result["id"] == 1
            assert result["name"] == "测试"

    def test_row_to_dict_tuple(self, supplier_dao, sample_supplier_row):
        """测试行转字典（元组格式）"""
        # 执行转换
        result = supplier_dao._row_to_dict(sample_supplier_row)

        # 验证结果
        assert result["id"] == 1
        assert result["name"] == "测试供应商"
        assert result["phone"] == "13987654321"
        assert result["contact_person"] == "李经理"

    def test_financial_row_to_dict(self, supplier_dao):
        """测试财务记录行转字典"""
        # 创建财务记录行
        financial_row = (
            1,
            None,
            1,
            None,
            "payable",
            50000.0,
            "2025-02-15",
            None,
            "pending",
            "采购订单",
            "2025-01-15",
            None,
            "测试供应商",
        )

        # 执行转换
        result = supplier_dao._financial_row_to_dict(financial_row)

        # 验证结果
        assert result["id"] == 1
        assert result["supplier_id"] == 1
        assert result["record_type"] == "payable"
        assert result["amount"] == 50000.0
        assert result["supplier_name"] == "测试供应商"

    # ==================== 边界条件和异常测试 ====================

    def test_insert_with_none_values(self, supplier_dao, mock_db_manager):
        """测试插入包含None值的数据"""
        # 设置模拟返回值
        mock_db_manager.execute_insert.return_value = 1

        # 准备包含None值的数据
        data_with_none = {
            "name": "测试供应商",
            "contact_person": None,
            "phone": None,
            "email": None,
            "address": None,
            "quality_rating": None,
            "cooperation_years": None,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # 执行插入
        result = supplier_dao.insert(data_with_none)

        # 验证结果
        assert result == 1

    def test_search_with_empty_conditions(self, supplier_dao, mock_db_manager):
        """测试使用空条件搜索"""
        # 设置模拟返回值
        mock_db_manager.execute_query.return_value = []

        # 执行搜索
        result = supplier_dao.search(conditions={})

        # 验证结果
        assert result == []

        # 验证SQL不包含WHERE子句
        call_args = mock_db_manager.execute_query.call_args
        sql = call_args[0][0]
        assert "WHERE" not in sql

    def test_update_no_data(self, supplier_dao, mock_db_manager):
        """测试更新时没有提供数据"""
        # 执行更新（空数据）
        result = supplier_dao.update(1, {})

        # 验证结果
        assert result is False
        mock_db_manager.execute_update.assert_not_called()

    def test_database_errors(self, supplier_dao, mock_db_manager):
        """测试各种数据库错误"""
        # 设置模拟抛出异常
        mock_db_manager.execute_query.side_effect = Exception("查询失败")

        # 测试获取供应商错误
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.get_by_id(1)
        assert "获取供应商记录失败" in str(exc_info.value)

        # 测试搜索错误
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.search()
        assert "搜索供应商记录失败" in str(exc_info.value)

        # 测试统计错误
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.count()
        assert "统计供应商记录失败" in str(exc_info.value)

    def test_financial_operations_database_errors(self, supplier_dao, mock_db_manager):
        """测试财务操作的数据库错误"""
        # 设置模拟抛出异常
        mock_db_manager.execute_insert.side_effect = Exception("插入失败")

        # 测试插入应付账款错误
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.insert_payable({"supplier_id": 1, "amount": 1000})
        assert "插入应付账款记录失败" in str(exc_info.value)

        # 测试插入付款错误
        with pytest.raises(DatabaseError) as exc_info:
            supplier_dao.insert_supplier_payment({"supplier_id": 1, "amount": 1000})
        assert "插入供应商付款记录失败" in str(exc_info.value)

    def test_private_methods(self, supplier_dao, mock_db_manager):
        """测试私有方法"""
        # 测试统计逾期应付账款
        mock_db_manager.execute_query.return_value = [(5,)]
        result = supplier_dao._count_overdue_payables()
        assert result == 5

        # 测试统计即将到期应付账款
        mock_db_manager.execute_query.return_value = [(3,)]
        result = supplier_dao._count_upcoming_payables()
        assert result == 3

        # 测试异常处理
        mock_db_manager.execute_query.side_effect = Exception("查询失败")
        overdue_result = supplier_dao._count_overdue_payables()
        assert overdue_result == 0
