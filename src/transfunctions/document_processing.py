"""
Transfunctions - 文档处理模块

提供文档生成、模板处理等功能.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

# 配置日志
logger = logging.getLogger(__name__)


class DocumentError(Exception):
    """文档处理异常类"""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


def generate_contract_document(
    contract_data: Dict[str, Any],
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """生成合同文档

    Args:
        contract_data: 合同数据
        template_path: 模板文件路径(可选)

    Returns:
        Dict[str, Any]: 文档生成结果

    Example:
        >>> contract = {"contract_number": "C2025001", "party_name": "ABC公司"}
        >>> result = generate_contract_document(contract)
        >>> print(result["status"])
        success
    """
    try:
        # 验证必要字段
        required_fields = ["contract_number", "party_name", "contract_amount"]
        missing_fields = [field for field in required_fields if not contract_data.get(field)]
        
        if missing_fields:
            raise DocumentError(f"缺少必要字段: {', '.join(missing_fields)}")
        
        # 准备文档数据
        doc_data = {
            "contract_number": contract_data.get("contract_number", ""),
            "party_name": contract_data.get("party_name", ""),
            "contract_type": contract_data.get("contract_type", ""),
            "contract_amount": _format_amount(contract_data.get("contract_amount", 0)),
            "sign_date": _format_date(contract_data.get("sign_date")),
            "effective_date": _format_date(contract_data.get("effective_date")),
            "expiry_date": _format_date(contract_data.get("expiry_date")),
            "payment_method": contract_data.get("payment_method", ""),
            "payment_terms": contract_data.get("payment_terms", ""),
            "generated_date": datetime.now().strftime("%Y年%m月%d日"),
            "generated_time": datetime.now().strftime("%H:%M:%S")
        }
        
        # 生成文档内容
        document_content = _generate_contract_content(doc_data)
        
        result = {
            "status": "success",
            "document_type": "contract",
            "contract_number": doc_data["contract_number"],
            "content": document_content,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_used": template_path or "default",
                "data_fields": len(doc_data)
            }
        }
        
        logger.info(f"合同文档生成成功: {doc_data['contract_number']}")
        return result
        
    except Exception as e:
        logger.error(f"合同文档生成失败: {e}")
        return {
            "status": "error",
            "error": str(e),
            "contract_number": contract_data.get("contract_number", "unknown")
        }


def generate_quote_document(
    quote_data: Dict[str, Any],
    template_path: Optional[str] = None
) -> Dict[str, Any]:
    """生成报价单文档

    Args:
        quote_data: 报价数据
        template_path: 模板文件路径(可选)

    Returns:
        Dict[str, Any]: 文档生成结果
    """
    try:
        # 验证必要字段
        required_fields = ["quote_number", "customer_name", "total_amount"]
        missing_fields = [field for field in required_fields if not quote_data.get(field)]
        
        if missing_fields:
            raise DocumentError(f"缺少必要字段: {', '.join(missing_fields)}")
        
        # 准备文档数据
        doc_data = {
            "quote_number": quote_data.get("quote_number", ""),
            "customer_name": quote_data.get("customer_name", ""),
            "quote_date": _format_date(quote_data.get("quote_date")),
            "expiry_date": _format_date(quote_data.get("expiry_date")),
            "total_amount": _format_amount(quote_data.get("total_amount", 0)),
            "items": quote_data.get("items", []),
            "notes": quote_data.get("notes", ""),
            "generated_date": datetime.now().strftime("%Y年%m月%d日"),
            "generated_time": datetime.now().strftime("%H:%M:%S")
        }
        
        # 处理报价项目
        formatted_items = []
        for i, item in enumerate(doc_data["items"], 1):
            formatted_item = {
                "序号": i,
                "产品名称": item.get("product_name", ""),
                "规格型号": item.get("specification", ""),
                "数量": item.get("quantity", 0),
                "单位": item.get("unit", "个"),
                "单价": _format_amount(item.get("unit_price", 0)),
                "小计": _format_amount(item.get("subtotal", 0))
            }
            formatted_items.append(formatted_item)
        
        doc_data["formatted_items"] = formatted_items
        
        # 生成文档内容
        document_content = _generate_quote_content(doc_data)
        
        result = {
            "status": "success",
            "document_type": "quote",
            "quote_number": doc_data["quote_number"],
            "content": document_content,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "template_used": template_path or "default",
                "items_count": len(formatted_items)
            }
        }
        
        logger.info(f"报价单文档生成成功: {doc_data['quote_number']}")
        return result
        
    except Exception as e:
        logger.error(f"报价单文档生成失败: {e}")
        return {
            "status": "error",
            "error": str(e),
            "quote_number": quote_data.get("quote_number", "unknown")
        }


def generate_service_ticket_report(
    ticket_data: Dict[str, Any],
    include_history: bool = True
) -> Dict[str, Any]:
    """生成售后工单报表

    Args:
        ticket_data: 工单数据
        include_history: 是否包含历史记录

    Returns:
        Dict[str, Any]: 报表生成结果
    """
    try:
        # 验证必要字段
        required_fields = ["ticket_number", "customer_name", "issue_type"]
        missing_fields = [field for field in required_fields if not ticket_data.get(field)]
        
        if missing_fields:
            raise DocumentError(f"缺少必要字段: {', '.join(missing_fields)}")
        
        # 准备报表数据
        report_data = {
            "ticket_number": ticket_data.get("ticket_number", ""),
            "customer_name": ticket_data.get("customer_name", ""),
            "issue_type": ticket_data.get("issue_type", ""),
            "priority": ticket_data.get("priority", "中"),
            "status": ticket_data.get("status", "待处理"),
            "description": ticket_data.get("description", ""),
            "solution": ticket_data.get("solution", ""),
            "created_date": _format_date(ticket_data.get("created_date")),
            "resolved_date": _format_date(ticket_data.get("resolved_date")),
            "satisfaction": ticket_data.get("satisfaction", ""),
            "generated_date": datetime.now().strftime("%Y年%m月%d日"),
            "generated_time": datetime.now().strftime("%H:%M:%S")
        }
        
        # 计算处理时长
        if ticket_data.get("created_date") and ticket_data.get("resolved_date"):
            try:
                created = datetime.strptime(ticket_data["created_date"], "%Y-%m-%d")
                resolved = datetime.strptime(ticket_data["resolved_date"], "%Y-%m-%d")
                processing_days = (resolved - created).days
                report_data["processing_days"] = processing_days
            except:
                report_data["processing_days"] = "未知"
        else:
            report_data["processing_days"] = "处理中"
        
        # 生成报表内容
        report_content = _generate_service_report_content(report_data, include_history)
        
        result = {
            "status": "success",
            "document_type": "service_report",
            "ticket_number": report_data["ticket_number"],
            "content": report_content,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "include_history": include_history,
                "processing_days": report_data["processing_days"]
            }
        }
        
        logger.info(f"售后工单报表生成成功: {report_data['ticket_number']}")
        return result
        
    except Exception as e:
        logger.error(f"售后工单报表生成失败: {e}")
        return {
            "status": "error",
            "error": str(e),
            "ticket_number": ticket_data.get("ticket_number", "unknown")
        }


def format_quote_summary(quote_data: Dict[str, Any]) -> str:
    """格式化报价摘要

    Args:
        quote_data: 报价数据

    Returns:
        str: 格式化的报价摘要

    Example:
        >>> quote = {"quote_number": "Q2025001", "total_amount": 120000, "items_count": 3}
        >>> summary = format_quote_summary(quote)
        >>> print(summary)
        报价Q2025001：3项产品，总金额¥120,000.00
    """
    try:
        quote_number = quote_data.get("quote_number", "未知")
        total_amount = quote_data.get("total_amount", 0)
        items_count = len(quote_data.get("items", []))
        customer_name = quote_data.get("customer_name", "")
        
        # 格式化金额
        formatted_amount = _format_amount(total_amount)
        
        # 生成摘要
        summary_parts = [f"报价{quote_number}"]
        
        if customer_name:
            summary_parts.append(f"客户：{customer_name}")
        
        if items_count > 0:
            summary_parts.append(f"{items_count}项产品")
        
        summary_parts.append(f"总金额{formatted_amount}")
        
        # 添加状态信息
        status = quote_data.get("status", "")
        if status:
            status_map = {
                "draft": "草稿",
                "sent": "已发送",
                "confirmed": "客户确认",
                "accepted": "已接受",
                "rejected": "已拒绝",
                "expired": "已过期"
            }
            status_text = status_map.get(status, status)
            summary_parts.append(f"状态：{status_text}")
        
        summary = "，".join(summary_parts)
        
        logger.debug(f"报价摘要格式化完成: {quote_number}")
        return summary
        
    except Exception as e:
        logger.error(f"报价摘要格式化失败: {e}")
        return f"报价摘要生成失败: {str(e)}"


def format_service_status(status: str, priority: str = "") -> str:
    """格式化服务状态

    Args:
        status: 状态值
        priority: 优先级(可选)

    Returns:
        str: 格式化的状态文本
    """
    try:
        # 状态映射
        status_map = {
            "pending": "待处理",
            "processing": "处理中",
            "waiting_customer": "待客户确认",
            "resolved": "已解决",
            "closed": "已关闭",
            "cancelled": "已取消"
        }
        
        # 优先级映射
        priority_map = {
            "low": "低",
            "medium": "中",
            "high": "高",
            "urgent": "紧急"
        }
        
        formatted_status = status_map.get(status, status)
        
        if priority:
            formatted_priority = priority_map.get(priority, priority)
            return f"{formatted_status}（{formatted_priority}优先级）"
        
        return formatted_status
        
    except Exception as e:
        logger.error(f"服务状态格式化失败: {e}")
        return status


def _format_amount(amount: Any) -> str:
    """格式化金额"""
    try:
        if amount is None:
            return "¥0.00"
        
        amount_float = float(amount)
        return f"¥{amount_float:,.2f}"
    except (ValueError, TypeError):
        return "¥0.00"


def _format_date(date_value: Any) -> str:
    """格式化日期"""
    try:
        if not date_value:
            return ""
        
        if isinstance(date_value, str):
            # 尝试解析日期字符串
            try:
                date_obj = datetime.strptime(date_value, "%Y-%m-%d")
                return date_obj.strftime("%Y年%m月%d日")
            except ValueError:
                return date_value
        elif hasattr(date_value, "strftime"):
            return date_value.strftime("%Y年%m月%d日")
        else:
            return str(date_value)
    except:
        return ""


def _generate_contract_content(doc_data: Dict[str, Any]) -> str:
    """生成合同文档内容"""
    content = f"""
合同编号：{doc_data['contract_number']}

甲方：[公司名称]
乙方：{doc_data['party_name']}

根据《中华人民共和国合同法》及相关法律法规，甲乙双方在平等、自愿、公平、诚实信用的基础上，就以下事项达成一致，签订本合同。

一、合同基本信息
合同类型：{doc_data['contract_type']}
合同金额：{doc_data['contract_amount']}
签署日期：{doc_data['sign_date']}
生效日期：{doc_data['effective_date']}
到期日期：{doc_data['expiry_date']}

二、付款条款
付款方式：{doc_data['payment_method']}
付款期限：{doc_data['payment_terms']}

三、其他条款
[具体条款内容]

甲方（盖章）：                    乙方（盖章）：

日期：{doc_data['generated_date']}        日期：{doc_data['generated_date']}

本合同一式两份，甲乙双方各执一份，具有同等法律效力。

生成时间：{doc_data['generated_date']} {doc_data['generated_time']}
"""
    return content.strip()


def _generate_quote_content(doc_data: Dict[str, Any]) -> str:
    """生成报价单文档内容"""
    content = f"""
报价单

报价编号：{doc_data['quote_number']}
客户名称：{doc_data['customer_name']}
报价日期：{doc_data['quote_date']}
有效期至：{doc_data['expiry_date']}

产品清单：
"""
    
    # 添加表头
    content += "\n序号\t产品名称\t规格型号\t数量\t单位\t单价\t小计\n"
    content += "-" * 60 + "\n"
    
    # 添加产品项目
    for item in doc_data['formatted_items']:
        content += f"{item['序号']}\t{item['产品名称']}\t{item['规格型号']}\t{item['数量']}\t{item['单位']}\t{item['单价']}\t{item['小计']}\n"
    
    content += "-" * 60 + "\n"
    content += f"总计：{doc_data['total_amount']}\n\n"
    
    if doc_data['notes']:
        content += f"备注：{doc_data['notes']}\n\n"
    
    content += f"生成时间：{doc_data['generated_date']} {doc_data['generated_time']}\n"
    
    return content


def _generate_service_report_content(report_data: Dict[str, Any], include_history: bool) -> str:
    """生成售后工单报表内容"""
    content = f"""
售后服务工单报表

工单编号：{report_data['ticket_number']}
客户名称：{report_data['customer_name']}
问题类型：{report_data['issue_type']}
优先级：{report_data['priority']}
当前状态：{report_data['status']}

问题描述：
{report_data['description']}

解决方案：
{report_data['solution'] if report_data['solution'] else '待处理'}

时间信息：
创建日期：{report_data['created_date']}
解决日期：{report_data['resolved_date'] if report_data['resolved_date'] else '处理中'}
处理时长：{report_data['processing_days']}天

客户满意度：{report_data['satisfaction'] if report_data['satisfaction'] else '未评价'}

生成时间：{report_data['generated_date']} {report_data['generated_time']}
"""
    
    if include_history:
        content += "\n\n历史记录：\n[历史记录将在此显示]\n"
    
    return content


# 导出的公共接口
__all__ = [
    "DocumentError",
    "generate_contract_document",
    "generate_quote_document", 
    "generate_service_ticket_report",
    "format_quote_summary",
    "format_service_status"
]