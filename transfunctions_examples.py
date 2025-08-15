# Transfunctions 可复用函数库示例
# 这个文件包含了MiniCRM项目中transfunctions的设计方案和示例实现

"""
Transfunctions 设计原则：
1. 单一职责 - 每个函数专注于一个特定功能
2. 可复用性 - 函数可在多个模块中使用
3. 一致性 - 统一的参数格式和返回值
4. 可测试性 - 易于编写单元测试
5. 文档完整 - 详细的docstring和类型注解
"""

# 标准库导入
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Callable

# ============================================================================
# MiniCRM 自定义异常类
# ============================================================================

class MiniCRMError(Exception):
    """MiniCRM基础异常类"""
    pass

class ValidationError(MiniCRMError):
    """数据验证异常"""
    pass

class BusinessLogicError(MiniCRMError):
    """业务逻辑异常"""
    pass

class DatabaseError(MiniCRMError):
    """数据库操作异常"""
    pass

# ============================================================================
# 业务验证函数 (business_validation.py)
# ============================================================================

def validate_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证客户数据
    
    Args:
        data: 客户数据字典，包含客户的基本信息
        
    Returns:
        验证后的数据字典，包含清理和格式化后的数据
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    # 必填字段验证
    if not data.get('name', '').strip():
        raise ValidationError("客户名称不能为空")
    validated['name'] = data['name'].strip()
    
    # 电话号码验证
    phone = data.get('phone', '').strip()
    if not phone:
        raise ValidationError("客户电话不能为空")
    if not re.match(r'^1[3-9]\d{9}$', phone):
        raise ValidationError("电话格式不正确")
    validated['phone'] = phone
    
    # 可选字段
    validated['email'] = data.get('email', '').strip()
    validated['company'] = data.get('company', '').strip()
    validated['address'] = data.get('address', '').strip()
    
    return validated

def validate_supplier_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证供应商数据
    
    Args:
        data: 供应商数据字典，包含供应商的基本信息
        
    Returns:
        验证后的数据字典
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    if not data.get('name', '').strip():
        raise ValidationError("供应商名称不能为空")
    validated['name'] = data['name'].strip()
    
    if not data.get('contact_person', '').strip():
        raise ValidationError("联系人不能为空")
    validated['contact_person'] = data['contact_person'].strip()
    
    return validated

def validate_quote_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证报价数据
    
    Args:
        data: 报价数据字典，包含客户ID和报价项目
        
    Returns:
        验证后的数据字典
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    if not data.get('customer_id'):
        raise ValidationError("客户ID不能为空")
    validated['customer_id'] = int(data['customer_id'])
    
    if not data.get('items') or not isinstance(data['items'], list):
        raise ValidationError("报价项目不能为空")
    validated['items'] = data['items']
    
    return validated

def validate_contract_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证合同数据
    
    Args:
        data: 合同数据字典，包含合同的基本信息
        
    Returns:
        验证后的数据字典
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    if not data.get('customer_id'):
        raise ValidationError("客户ID不能为空")
    validated['customer_id'] = int(data['customer_id'])
    
    if not data.get('contract_number', '').strip():
        raise ValidationError("合同编号不能为空")
    validated['contract_number'] = data['contract_number'].strip()
    
    return validated

def validate_service_ticket_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证售后工单数据
    
    Args:
        data: 售后工单数据字典
        
    Returns:
        验证后的数据字典
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    if not data.get('customer_id'):
        raise ValidationError("客户ID不能为空")
    validated['customer_id'] = int(data['customer_id'])
    
    if not data.get('issue_description', '').strip():
        raise ValidationError("问题描述不能为空")
    validated['issue_description'] = data['issue_description'].strip()
    
    return validated

def validate_interaction_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证互动记录数据
    
    Args:
        data: 互动记录数据字典
        
    Returns:
        验证后的数据字典
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated = {}
    
    if not data.get('customer_id'):
        raise ValidationError("客户ID不能为空")
    validated['customer_id'] = int(data['customer_id'])
    
    if not data.get('interaction_type', '').strip():
        raise ValidationError("互动类型不能为空")
    validated['interaction_type'] = data['interaction_type'].strip()
    
    return validated

def validate_batch_data(data_list: List[Dict[str, Any]], validation_func: Callable) -> List[Dict[str, Any]]:
    """批量验证数据
    
    Args:
        data_list: 数据列表
        validation_func: 验证函数
        
    Returns:
        验证后的数据列表
        
    Raises:
        ValidationError: 数据验证失败时抛出
    """
    validated_list = []
    errors = []
    
    for i, data in enumerate(data_list):
        try:
            validated = validation_func(data)
            validated_list.append(validated)
        except ValidationError as e:
            errors.append(f"第{i+1}行: {str(e)}")
    
    if errors:
        raise ValidationError(f"批量验证失败:\n" + "\n".join(errors))
    
    return validated_list

# ============================================================================
# 数据格式化函数 (data_formatting.py)
# ============================================================================

def format_currency(amount: Union[int, float], currency: str = "¥") -> str:
    """格式化货币显示
    
    Args:
        amount: 金额
        currency: 货币符号
        
    Returns:
        格式化后的货币字符串
    """
    if amount is None:
        return f"{currency}0.00"
    
    # 格式化为千分位分隔
    formatted = f"{amount:,.2f}"
    return f"{currency}{formatted}"

def format_phone_number(phone: str) -> str:
    """格式化电话号码显示"""
    if not phone:
        return ""
    
    # 中国手机号格式化：138-1234-5678
    if re.match(r'^1[3-9]\d{9}$', phone):
        return f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
    
    return phone

def format_date(date_obj: Union[datetime, str], format_type: str = "default") -> str:
    """格式化日期显示
    
    Args:
        date_obj: 日期对象或字符串
        format_type: 格式类型 ('default', 'chinese', 'short')
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except:
            return date_obj
    
    if not isinstance(date_obj, datetime):
        return str(date_obj)
    
    formats = {
        'default': '%Y-%m-%d %H:%M:%S',
        'chinese': '%Y年%m月%d日',
        'short': '%m/%d'
    }
    
    return date_obj.strftime(formats.get(format_type, formats['default']))

def format_datetime(date_obj: Union[datetime, str], format_type: str = "default") -> str:
    """格式化日期时间显示"""
    return format_date(date_obj, format_type)

def format_address(address: str) -> str:
    """格式化地址显示"""
    if not address:
        return ""
    return address.strip()

def format_contact_info(customer: Dict[str, Any]) -> Dict[str, str]:
    """格式化联系信息显示"""
    return {
        'name': customer.get('name', ''),
        'phone': format_phone_number(customer.get('phone', '')),
        'email': customer.get('email', ''),
        'company': customer.get('company', ''),
        'address': customer.get('address', '')
    }

def format_quote_summary(quote: Dict[str, Any]) -> str:
    """格式化报价摘要"""
    customer_name = quote.get('customer_name', '未知客户')
    total_amount = quote.get('total_amount', 0)
    item_count = len(quote.get('items', []))
    
    return f"{customer_name} - {item_count}项 - {format_currency(total_amount)}"

# ============================================================================
# 业务计算函数 (business_calculations.py)
# ============================================================================

def calculate_quote_total(items: List[Dict[str, Any]]) -> Dict[str, float]:
    """计算报价总额
    
    Args:
        items: 报价项目列表，每项包含 quantity, unit_price
        
    Returns:
        包含小计、税额、总计的字典
    """
    subtotal = 0.0
    
    for item in items:
        quantity = float(item.get('quantity', 0))
        unit_price = float(item.get('unit_price', 0))
        subtotal += quantity * unit_price
    
    tax_rate = 0.13  # 13%增值税
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'tax_rate': tax_rate,
        'total': total
    }

def calculate_customer_value_score(customer: Dict[str, Any]) -> float:
    """计算客户价值评分 (0-100)"""
    score = 0.0
    
    # 交易金额权重 40%
    total_amount = float(customer.get('total_amount', 0))
    if total_amount > 100000:
        score += 40
    elif total_amount > 50000:
        score += 30
    elif total_amount > 10000:
        score += 20
    else:
        score += 10
    
    # 交易频率权重 30%
    transaction_count = int(customer.get('transaction_count', 0))
    if transaction_count > 10:
        score += 30
    elif transaction_count > 5:
        score += 20
    elif transaction_count > 1:
        score += 15
    else:
        score += 5
    
    # 合作时长权重 20%
    cooperation_months = int(customer.get('cooperation_months', 0))
    if cooperation_months > 24:
        score += 20
    elif cooperation_months > 12:
        score += 15
    elif cooperation_months > 6:
        score += 10
    else:
        score += 5
    
    # 互动频率权重 10%
    interaction_count = int(customer.get('interaction_count', 0))
    if interaction_count > 20:
        score += 10
    elif interaction_count > 10:
        score += 8
    elif interaction_count > 5:
        score += 5
    else:
        score += 2
    
    return min(score, 100.0)

def calculate_supplier_performance_score(supplier: Dict[str, Any]) -> float:
    """计算供应商绩效评分 (0-100)"""
    score = 0.0
    
    # 质量评分权重 40%
    quality_score = float(supplier.get('quality_score', 0))
    score += (quality_score / 10) * 40
    
    # 交付及时性权重 30%
    delivery_rate = float(supplier.get('on_time_delivery_rate', 0))
    score += delivery_rate * 30
    
    # 价格竞争力权重 20%
    price_competitiveness = float(supplier.get('price_competitiveness', 0))
    score += price_competitiveness * 20
    
    # 服务质量权重 10%
    service_score = float(supplier.get('service_score', 0))
    score += (service_score / 10) * 10
    
    return min(score, 100.0)

def calculate_growth_rate(current: float, previous: float) -> float:
    """计算增长率"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100

def calculate_trend_analysis(data_points: List[float]) -> Dict[str, Any]:
    """计算趋势分析"""
    if len(data_points) < 2:
        return {'trend': 'insufficient_data', 'slope': 0, 'direction': 'unknown'}
    
    # 简单线性趋势计算
    n = len(data_points)
    x_sum = sum(range(n))
    y_sum = sum(data_points)
    xy_sum = sum(i * data_points[i] for i in range(n))
    x2_sum = sum(i * i for i in range(n))
    
    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
    
    if slope > 0.1:
        direction = 'increasing'
    elif slope < -0.1:
        direction = 'decreasing'
    else:
        direction = 'stable'
    
    return {
        'trend': direction,
        'slope': slope,
        'direction': direction
    }

def dashboard_calculations(data: Dict[str, Any]) -> Dict[str, Any]:
    """仪表盘指标计算"""
    customers = data.get('customers', [])
    quotes = data.get('quotes', [])
    contracts = data.get('contracts', [])
    
    return {
        'total_customers': len(customers),
        'total_quotes': len(quotes),
        'total_contracts': len(contracts),
        'avg_customer_value': sum(calculate_customer_value_score(c) for c in customers) / len(customers) if customers else 0,
        'total_quote_amount': sum(calculate_quote_total(q.get('items', []))['total'] for q in quotes),
        'quote_success_rate': len(contracts) / len(quotes) * 100 if quotes else 0
    }

# ============================================================================
# CRUD模板函数 (crud_templates.py)
# ============================================================================

def crud_create_template(dao_instance, entity_type: str, validation_func=None):
    """创建CRUD操作模板函数
    
    Args:
        dao_instance: DAO实例
        entity_type: 实体类型名称
        validation_func: 验证函数
        
    Returns:
        创建操作函数
    """
    def create_entity(data: Dict[str, Any]) -> int:
        # 数据验证
        if validation_func:
            validated_data = validation_func(data)
        else:
            validated_data = data
        
        # 执行创建
        entity_id = dao_instance.insert(validated_data)
        
        # 日志记录
        print(f"成功创建{entity_type}: {entity_id}")
        
        return entity_id
    
    return create_entity

def crud_update_template(dao_instance, entity_type: str, validation_func=None):
    """更新CRUD操作模板函数"""
    def update_entity(entity_id: int, data: Dict[str, Any]) -> bool:
        # 数据验证
        if validation_func:
            validated_data = validation_func(data)
        else:
            validated_data = data
        
        # 执行更新
        success = dao_instance.update(entity_id, validated_data)
        
        if success:
            print(f"成功更新{entity_type}: {entity_id}")
        
        return success
    
    return update_entity

def crud_delete_template(dao_instance, entity_type: str):
    """删除CRUD操作模板函数"""
    def delete_entity(entity_id: int) -> bool:
        # 执行删除
        success = dao_instance.delete(entity_id)
        
        if success:
            print(f"成功删除{entity_type}: {entity_id}")
        
        return success
    
    return delete_entity

def crud_get_template(dao_instance, entity_type: str):
    """查询CRUD操作模板函数"""
    def get_entity(entity_id: int) -> Optional[Dict[str, Any]]:
        # 执行查询
        entity = dao_instance.get_by_id(entity_id)
        
        if entity:
            print(f"成功查询{entity_type}: {entity_id}")
        
        return entity
    
    return get_entity

def build_crud_service(dao_instance, entity_type: str, validation_func=None):
    """构建完整CRUD服务"""
    return {
        'create': crud_create_template(dao_instance, entity_type, validation_func),
        'update': crud_update_template(dao_instance, entity_type, validation_func),
        'delete': crud_delete_template(dao_instance, entity_type),
        'get': crud_get_template(dao_instance, entity_type)
    }

# ============================================================================
# 搜索模板函数 (search_templates.py)
# ============================================================================

def paginated_search_template(dao_instance, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None):
    """分页搜索模板"""
    offset = (page - 1) * page_size
    
    # 构建查询条件
    where_conditions = []
    params = []
    
    if filters:
        for key, value in filters.items():
            if value:
                where_conditions.append(f"{key} LIKE ?")
                params.append(f"%{value}%")
    
    where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
    
    # 执行查询
    total_count = dao_instance.count(where_clause, params)
    items = dao_instance.search(where_clause, params, offset, page_size)
    
    return {
        'items': items,
        'total_count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    }

def advanced_search_template(dao_instance, search_criteria: Dict[str, Any]):
    """高级搜索模板"""
    conditions = []
    params = []
    
    # 文本搜索
    if search_criteria.get('keyword'):
        keyword = search_criteria['keyword']
        conditions.append("(name LIKE ? OR phone LIKE ? OR email LIKE ?)")
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    
    # 日期范围搜索
    if search_criteria.get('date_from'):
        conditions.append("created_at >= ?")
        params.append(search_criteria['date_from'])
    
    if search_criteria.get('date_to'):
        conditions.append("created_at <= ?")
        params.append(search_criteria['date_to'])
    
    # 分类搜索
    if search_criteria.get('category'):
        conditions.append("category = ?")
        params.append(search_criteria['category'])
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    return dao_instance.search(where_clause, params)

def search_with_aggregation(dao_instance, search_criteria: Dict[str, Any], aggregation_fields: List[str]):
    """聚合搜索模板"""
    # 基础搜索
    results = advanced_search_template(dao_instance, search_criteria)
    
    # 聚合计算
    aggregations = {}
    for field in aggregation_fields:
        values = [item.get(field, 0) for item in results if item.get(field) is not None]
        if values:
            aggregations[field] = {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values)
            }
    
    return {
        'results': results,
        'aggregations': aggregations,
        'total_count': len(results)
    }

# ============================================================================
# 报表生成函数 (report_templates.py)
# ============================================================================

def generate_customer_report(customers: List[Dict[str, Any]], options: Dict[str, Any]) -> Dict[str, Any]:
    """生成客户分析报表"""
    if not customers:
        return {'error': '没有客户数据'}
    
    # 基础统计
    total_customers = len(customers)
    total_value = sum(float(c.get('total_amount', 0)) for c in customers)
    avg_value = total_value / total_customers if total_customers > 0 else 0
    
    # 价值分级统计
    high_value = len([c for c in customers if float(c.get('total_amount', 0)) > 100000])
    medium_value = len([c for c in customers if 50000 <= float(c.get('total_amount', 0)) <= 100000])
    low_value = total_customers - high_value - medium_value
    
    return {
        'total_customers': total_customers,
        'total_value': total_value,
        'avg_value': avg_value,
        'value_distribution': {
            'high_value': high_value,
            'medium_value': medium_value,
            'low_value': low_value
        },
        'formatted_total_value': format_currency(total_value),
        'formatted_avg_value': format_currency(avg_value)
    }

def generate_sales_report(sales_data: List[Dict[str, Any]], options: Dict[str, Any]) -> Dict[str, Any]:
    """生成销售分析报表"""
    if not sales_data:
        return {'error': '没有销售数据'}
    
    total_sales = sum(float(s.get('amount', 0)) for s in sales_data)
    total_orders = len(sales_data)
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'formatted_total_sales': format_currency(total_sales),
        'formatted_avg_order_value': format_currency(avg_order_value)
    }

def generate_supplier_report(suppliers: List[Dict[str, Any]], options: Dict[str, Any]) -> Dict[str, Any]:
    """生成供应商分析报表"""
    if not suppliers:
        return {'error': '没有供应商数据'}
    
    total_suppliers = len(suppliers)
    avg_performance = sum(calculate_supplier_performance_score(s) for s in suppliers) / total_suppliers
    
    # 绩效分级
    excellent = len([s for s in suppliers if calculate_supplier_performance_score(s) >= 90])
    good = len([s for s in suppliers if 70 <= calculate_supplier_performance_score(s) < 90])
    average = len([s for s in suppliers if 50 <= calculate_supplier_performance_score(s) < 70])
    poor = total_suppliers - excellent - good - average
    
    return {
        'total_suppliers': total_suppliers,
        'avg_performance': avg_performance,
        'performance_distribution': {
            'excellent': excellent,
            'good': good,
            'average': average,
            'poor': poor
        }
    }

def create_dashboard_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    """创建仪表盘摘要"""
    customers = data.get('customers', [])
    quotes = data.get('quotes', [])
    contracts = data.get('contracts', [])
    suppliers = data.get('suppliers', [])
    
    # 基础指标
    basic_metrics = dashboard_calculations(data)
    
    # 客户报表
    customer_report = generate_customer_report(customers, {})
    
    # 供应商报表
    supplier_report = generate_supplier_report(suppliers, {})
    
    return {
        'basic_metrics': basic_metrics,
        'customer_analysis': customer_report,
        'supplier_analysis': supplier_report,
        'generated_at': format_datetime(datetime.now(), 'chinese')
    }

# ============================================================================
# 文档处理函数 (document_processing.py)
# ============================================================================

def generate_word_document(template_path: str, data: Dict[str, Any], output_path: str) -> bool:
    """生成Word文档
    
    Args:
        template_path: 模板文件路径
        data: 数据字典
        output_path: 输出文件路径
        
    Returns:
        是否成功生成
    """
    try:
        # 这里应该使用docxtpl库，但为了示例简化
        print(f"生成Word文档: {template_path} -> {output_path}")
        print(f"数据: {data}")
        return True
    except Exception as e:
        print(f"生成Word文档失败: {e}")
        return False

def generate_quote_document(quote_data: Dict[str, Any], template_path: str = None) -> str:
    """生成报价单文档"""
    if not template_path:
        template_path = "templates/quote_template.docx"
    
    output_path = f"output/quote_{quote_data.get('id', 'unknown')}.docx"
    
    # 准备文档数据
    doc_data = {
        'customer_name': quote_data.get('customer_name', ''),
        'quote_date': format_date(datetime.now(), 'chinese'),
        'items': quote_data.get('items', []),
        'total': calculate_quote_total(quote_data.get('items', []))
    }
    
    success = generate_word_document(template_path, doc_data, output_path)
    return output_path if success else None

def generate_contract_document(contract_data: Dict[str, Any], template_path: str = None) -> str:
    """生成合同文档"""
    if not template_path:
        template_path = "templates/contract_template.docx"
    
    output_path = f"output/contract_{contract_data.get('id', 'unknown')}.docx"
    
    # 准备文档数据
    doc_data = {
        'customer_name': contract_data.get('customer_name', ''),
        'contract_number': contract_data.get('contract_number', ''),
        'contract_date': format_date(datetime.now(), 'chinese'),
        'terms': contract_data.get('terms', [])
    }
    
    success = generate_word_document(template_path, doc_data, output_path)
    return output_path if success else None

def generate_pdf_report(report_data: Dict[str, Any], output_path: str) -> bool:
    """生成PDF报表"""
    try:
        # 这里应该使用reportlab库，但为了示例简化
        print(f"生成PDF报表: {output_path}")
        print(f"报表数据: {report_data}")
        return True
    except Exception as e:
        print(f"生成PDF报表失败: {e}")
        return False

# ============================================================================
# 数据导入导出函数 (import_export.py)
# ============================================================================

def import_csv_data(file_path: str, validation_func: Callable = None) -> List[Dict[str, Any]]:
    """导入CSV数据"""
    try:
        # 这里应该使用pandas或csv库，但为了示例简化
        print(f"导入CSV数据: {file_path}")
        
        # 模拟数据
        mock_data = [
            {'name': '测试客户1', 'phone': '13812345678'},
            {'name': '测试客户2', 'phone': '13987654321'}
        ]
        
        if validation_func:
            return validate_batch_data(mock_data, validation_func)
        
        return mock_data
    except Exception as e:
        raise ValidationError(f"导入CSV数据失败: {e}")

def import_excel_data(file_path: str, sheet_name: str = None, validation_func: Callable = None) -> List[Dict[str, Any]]:
    """导入Excel数据"""
    try:
        print(f"导入Excel数据: {file_path}, 工作表: {sheet_name}")
        
        # 模拟数据
        mock_data = [
            {'name': '测试供应商1', 'contact_person': '张三'},
            {'name': '测试供应商2', 'contact_person': '李四'}
        ]
        
        if validation_func:
            return validate_batch_data(mock_data, validation_func)
        
        return mock_data
    except Exception as e:
        raise ValidationError(f"导入Excel数据失败: {e}")

def export_csv_data(data: List[Dict[str, Any]], file_path: str, columns: List[str] = None) -> bool:
    """导出CSV数据"""
    try:
        print(f"导出CSV数据: {file_path}")
        print(f"数据行数: {len(data)}")
        print(f"导出列: {columns}")
        return True
    except Exception as e:
        print(f"导出CSV数据失败: {e}")
        return False

def export_excel_data(data: List[Dict[str, Any]], file_path: str, sheet_name: str = "Sheet1", columns: List[str] = None) -> bool:
    """导出Excel数据"""
    try:
        print(f"导出Excel数据: {file_path}, 工作表: {sheet_name}")
        print(f"数据行数: {len(data)}")
        print(f"导出列: {columns}")
        return True
    except Exception as e:
        print(f"导出Excel数据失败: {e}")
        return False

def create_import_template(entity_type: str, file_path: str) -> bool:
    """创建导入模板"""
    templates = {
        'customer': ['name', 'phone', 'email', 'company', 'address'],
        'supplier': ['name', 'contact_person', 'phone', 'email', 'address'],
        'quote': ['customer_name', 'product_name', 'quantity', 'unit_price']
    }
    
    columns = templates.get(entity_type, ['name', 'description'])
    
    # 创建空模板
    template_data = [dict.fromkeys(columns, '')]
    
    return export_excel_data(template_data, file_path, f"{entity_type}_template", columns)

def validate_import_data(data: List[Dict[str, Any]], entity_type: str) -> List[Dict[str, Any]]:
    """验证导入数据"""
    validation_funcs = {
        'customer': validate_customer_data,
        'supplier': validate_supplier_data,
        'quote': validate_quote_data
    }
    
    validation_func = validation_funcs.get(entity_type)
    if not validation_func:
        raise ValidationError(f"不支持的实体类型: {entity_type}")
    
    return validate_batch_data(data, validation_func)

# ============================================================================
# 通知模板函数 (notification_templates.py)
# ============================================================================

def generate_email_notification(notification_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """生成邮件通知"""
    templates = {
        'quote_created': {
            'subject': '新报价单已创建',
            'body': f"客户 {data.get('customer_name')} 的报价单已创建，总金额：{format_currency(data.get('total_amount', 0))}"
        },
        'contract_signed': {
            'subject': '合同签署通知',
            'body': f"合同 {data.get('contract_number')} 已签署，客户：{data.get('customer_name')}"
        },
        'service_ticket_created': {
            'subject': '新售后工单',
            'body': f"客户 {data.get('customer_name')} 提交了新的售后工单：{data.get('issue_description')}"
        }
    }
    
    template = templates.get(notification_type, {
        'subject': '系统通知',
        'body': '您有新的系统通知'
    })
    
    return template

def generate_sms_notification(notification_type: str, data: Dict[str, Any]) -> str:
    """生成短信通知"""
    templates = {
        'quote_reminder': f"【MiniCRM】您的报价单即将到期，请及时处理。客户：{data.get('customer_name')}",
        'contract_reminder': f"【MiniCRM】合同即将到期，请及时续签。合同号：{data.get('contract_number')}",
        'service_reminder': f"【MiniCRM】售后工单待处理，客户：{data.get('customer_name')}"
    }
    
    return templates.get(notification_type, "【MiniCRM】您有新的系统通知")

def generate_system_notification(notification_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """生成系统通知"""
    return {
        'type': notification_type,
        'title': data.get('title', '系统通知'),
        'message': data.get('message', '您有新的系统通知'),
        'created_at': datetime.now(),
        'read': False,
        'priority': data.get('priority', 'normal')
    }

def create_notification_batch(notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """创建批量通知"""
    batch_notifications = []
    
    for notification in notifications:
        notification_type = notification.get('type')
        data = notification.get('data', {})
        
        if notification.get('email'):
            email_notification = generate_email_notification(notification_type, data)
            batch_notifications.append({
                'channel': 'email',
                'recipient': notification.get('recipient'),
                'content': email_notification
            })
        
        if notification.get('sms'):
            sms_notification = generate_sms_notification(notification_type, data)
            batch_notifications.append({
                'channel': 'sms',
                'recipient': notification.get('recipient'),
                'content': sms_notification
            })
        
        if notification.get('system'):
            system_notification = generate_system_notification(notification_type, data)
            batch_notifications.append({
                'channel': 'system',
                'recipient': notification.get('recipient'),
                'content': system_notification
            })
    
    return batch_notifications

# ============================================================================
# 使用示例
# ============================================================================

if __name__ == "__main__":
    # 数据验证示例
    customer_data = {
        'name': '测试公司',
        'phone': '13812345678',
        'email': 'test@example.com'
    }
    
    try:
        validated = validate_customer_data(customer_data)
        print("验证成功:", validated)
    except ValidationError as e:
        print("验证失败:", e)
    
    # 格式化示例
    print("货币格式化:", format_currency(12345.67))
    print("电话格式化:", format_phone_number('13812345678'))
    print("日期格式化:", format_date(datetime.now(), 'chinese'))
    
    # 计算示例
    quote_items = [
        {'quantity': 10, 'unit_price': 100.0},
        {'quantity': 5, 'unit_price': 200.0}
    ]
    quote_total = calculate_quote_total(quote_items)
    print("报价计算:", quote_total)
    
    customer_info = {
        'total_amount': 50000,
        'transaction_count': 8,
        'cooperation_months': 18,
        'interaction_count': 15
    }
    value_score = calculate_customer_value_score(customer_info)
    print("客户价值评分:", value_score)
