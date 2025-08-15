"""
MiniCRM 枚举类型定义

定义了应用程序中使用的所有枚举类型，包括：
- 客户相关枚举
- 供应商相关枚举
- 业务流程枚举
- 财务相关枚举
- 系统状态枚举
"""

from enum import Enum


class CustomerLevel(Enum):
    """客户等级枚举"""

    VIP = "vip"  # VIP客户
    IMPORTANT = "important"  # 重要客户
    NORMAL = "normal"  # 普通客户
    POTENTIAL = "potential"  # 潜在客户


class CustomerType(Enum):
    """客户类型枚举"""

    ENTERPRISE = "enterprise"  # 企业客户
    INDIVIDUAL = "individual"  # 个人客户
    GOVERNMENT = "government"  # 政府客户
    NONPROFIT = "nonprofit"  # 非营利组织


class SupplierLevel(Enum):
    """供应商等级枚举"""

    STRATEGIC = "strategic"  # 战略供应商
    IMPORTANT = "important"  # 重要供应商
    NORMAL = "normal"  # 普通供应商
    BACKUP = "backup"  # 备选供应商


class SupplierType(Enum):
    """供应商类型枚举"""

    MANUFACTURER = "manufacturer"  # 制造商
    DISTRIBUTOR = "distributor"  # 分销商
    SERVICE = "service"  # 服务商
    LOGISTICS = "logistics"  # 物流商


class InteractionType(Enum):
    """互动类型枚举"""

    PHONE_CALL = "phone_call"  # 电话沟通
    EMAIL = "email"  # 邮件沟通
    MEETING = "meeting"  # 会议
    VISIT = "visit"  # 拜访
    ONLINE = "online"  # 在线沟通
    OTHER = "other"  # 其他


class InteractionStatus(Enum):
    """互动状态枚举"""

    PLANNED = "planned"  # 计划中
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class ContractStatus(Enum):
    """合同状态枚举"""

    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审核
    APPROVED = "approved"  # 已批准
    SIGNED = "signed"  # 已签署
    ACTIVE = "active"  # 执行中
    COMPLETED = "completed"  # 已完成
    TERMINATED = "terminated"  # 已终止
    EXPIRED = "expired"  # 已过期


class QuoteStatus(Enum):
    """报价状态枚举"""

    DRAFT = "draft"  # 草稿
    SENT = "sent"  # 已发送
    VIEWED = "viewed"  # 已查看
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期
    CANCELLED = "cancelled"  # 已取消


class PaymentStatus(Enum):
    """付款状态枚举"""

    PENDING = "pending"  # 待付款
    PARTIAL = "partial"  # 部分付款
    PAID = "paid"  # 已付款
    OVERDUE = "overdue"  # 逾期
    CANCELLED = "cancelled"  # 已取消


class PaymentMethod(Enum):
    """付款方式枚举"""

    CASH = "cash"  # 现金
    BANK_TRANSFER = "bank_transfer"  # 银行转账
    CHECK = "check"  # 支票
    CREDIT_CARD = "credit_card"  # 信用卡
    ONLINE = "online"  # 在线支付
    OTHER = "other"  # 其他


class TaskStatus(Enum):
    """任务状态枚举"""

    TODO = "todo"  # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    OVERDUE = "overdue"  # 已逾期


class TaskPriority(Enum):
    """任务优先级枚举"""

    LOW = "low"  # 低优先级
    NORMAL = "normal"  # 普通优先级
    HIGH = "high"  # 高优先级
    URGENT = "urgent"  # 紧急


class DocumentType(Enum):
    """文档类型枚举"""

    CONTRACT = "contract"  # 合同
    QUOTE = "quote"  # 报价单
    INVOICE = "invoice"  # 发票
    RECEIPT = "receipt"  # 收据
    REPORT = "report"  # 报告
    OTHER = "other"  # 其他


class EventType(Enum):
    """事件类型枚举"""

    CUSTOMER_CREATED = "customer_created"  # 客户创建
    CUSTOMER_UPDATED = "customer_updated"  # 客户更新
    CUSTOMER_DELETED = "customer_deleted"  # 客户删除
    SUPPLIER_CREATED = "supplier_created"  # 供应商创建
    SUPPLIER_UPDATED = "supplier_updated"  # 供应商更新
    SUPPLIER_DELETED = "supplier_deleted"  # 供应商删除
    CONTRACT_SIGNED = "contract_signed"  # 合同签署
    CONTRACT_EXPIRED = "contract_expired"  # 合同过期
    QUOTE_SENT = "quote_sent"  # 报价发送
    QUOTE_ACCEPTED = "quote_accepted"  # 报价接受
    PAYMENT_RECEIVED = "payment_received"  # 收到付款
    PAYMENT_OVERDUE = "payment_overdue"  # 付款逾期
    TASK_CREATED = "task_created"  # 任务创建
    TASK_COMPLETED = "task_completed"  # 任务完成
    INTERACTION_LOGGED = "interaction_logged"  # 互动记录
    SYSTEM_BACKUP = "system_backup"  # 系统备份
    USER_LOGIN = "user_login"  # 用户登录
    USER_LOGOUT = "user_logout"  # 用户登出


class NotificationType(Enum):
    """通知类型枚举"""

    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    ERROR = "error"  # 错误
    SUCCESS = "success"  # 成功


class Gender(Enum):
    """性别枚举"""

    MALE = "male"  # 男性
    FEMALE = "female"  # 女性
    OTHER = "other"  # 其他


class Currency(Enum):
    """货币类型枚举"""

    CNY = "CNY"  # 人民币
    USD = "USD"  # 美元
    EUR = "EUR"  # 欧元
    JPY = "JPY"  # 日元
    GBP = "GBP"  # 英镑


class ProductCategory(Enum):
    """产品类别枚举（板材行业）"""

    ECOLOGICAL_BOARD = "ecological_board"  # 生态板
    FURNITURE_BOARD = "furniture_board"  # 家具板
    FLAME_RETARDANT_BOARD = "flame_retardant_board"  # 阻燃板
    PLYWOOD = "plywood"  # 胶合板
    PARTICLE_BOARD = "particle_board"  # 刨花板
    MDF = "mdf"  # 中密度纤维板
    OSB = "osb"  # 定向刨花板
    BLOCKBOARD = "blockboard"  # 细木工板
    OTHER = "other"  # 其他


class QualityGrade(Enum):
    """质量等级枚举"""

    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"  # 良好
    AVERAGE = "average"  # 一般
    POOR = "poor"  # 较差


class UnitOfMeasure(Enum):
    """计量单位枚举"""

    PIECE = "piece"  # 张
    CUBIC_METER = "cubic_meter"  # 立方米
    SQUARE_METER = "square_meter"  # 平方米
    KILOGRAM = "kilogram"  # 千克
    TON = "ton"  # 吨
    SET = "set"  # 套
    BOX = "box"  # 箱
    PACKAGE = "package"  # 包
