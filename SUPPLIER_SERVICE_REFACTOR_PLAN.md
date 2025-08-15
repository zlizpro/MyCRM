# 供应商服务重构计划

## 当前问题
- 文件大小: 956行 (严重超标)
- 违反单一职责原则
- 代码维护困难

## 拆分方案

### 1. 核心供应商服务 (200行)
**文件**: `src/minicrm/services/supplier/supplier_service.py`
**职责**: 基础CRUD操作
```python
class SupplierService(BaseService):
    - create_supplier()
    - update_supplier()
    - delete_supplier()
    - search_suppliers()
    - _check_supplier_exists()
    - _apply_supplier_defaults()
```

### 2. 供应商质量评估服务 (180行)
**文件**: `src/minicrm/services/supplier/supplier_quality_service.py`
**职责**: 质量评估和分级
```python
class SupplierQualityService(BaseService):
    - evaluate_supplier_quality()
    - _determine_supplier_grade()
    - _update_supplier_quality_from_event()
    - _adjust_supplier_quality_score()
    - _adjust_supplier_service_score()
```

### 3. 供应商交流事件服务 (250行)
**文件**: `src/minicrm/services/supplier/supplier_event_service.py`
**职责**: 交流事件处理
```python
class SupplierEventService(BaseService):
    - create_communication_event()
    - update_event_status()
    - process_event()
    - get_overdue_events()
    - _validate_event_data()
    - _determine_event_priority()
    - _calculate_event_due_time()
    - _generate_event_number()
```

### 4. 供应商统计分析服务 (150行)
**文件**: `src/minicrm/services/supplier/supplier_statistics_service.py`
**职责**: 统计分析
```python
class SupplierStatisticsService(BaseService):
    - get_event_statistics()
    - get_supplier_performance_metrics()
    - generate_supplier_reports()
```

### 5. 供应商任务管理服务 (120行)
**文件**: `src/minicrm/services/supplier/supplier_task_service.py`
**职责**: 任务和跟进管理
```python
class SupplierTaskService(BaseService):
    - manage_supplier_interaction()
    - _create_follow_up_task()
    - get_pending_tasks()
    - complete_tasks()
```

### 6. 枚举和常量 (50行)
**文件**: `src/minicrm/services/supplier/supplier_enums.py`
**职责**: 枚举定义
```python
class CommunicationEventType(Enum): ...
class EventStatus(Enum): ...
class EventPriority(Enum): ...
```

## 重构步骤

1. **创建目录结构**
```bash
mkdir -p src/minicrm/services/supplier
```

2. **拆分文件**
- 按职责拆分现有代码
- 保持接口兼容性
- 添加服务协调器

3. **创建服务协调器**
```python
# src/minicrm/services/supplier_service.py (新的主入口)
class SupplierService:
    def __init__(self, supplier_dao):
        self.core = SupplierCoreService(supplier_dao)
        self.quality = SupplierQualityService(supplier_dao)
        self.events = SupplierEventService(supplier_dao)
        self.statistics = SupplierStatisticsService(supplier_dao)
        self.tasks = SupplierTaskService(supplier_dao)
```

4. **更新导入和依赖**
- 更新所有引用
- 保持向后兼容
- 添加单元测试

## 预期效果
- 每个文件 < 300行
- 职责清晰分离
- 易于测试和维护
- 符合SOLID原则
