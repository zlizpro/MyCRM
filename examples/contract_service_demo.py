#!/usr/bin/env python3
"""
MiniCRM 合同管理服务演示

展示合同管理服务的主要功能，包括：
- 合同创建和管理
- 合同生命周期管理
- 合同到期提醒
- 合同模板管理
- 业务统计功能

使用方法:
    python examples/contract_service_demo.py
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.minicrm.models.contract import Contract, ContractStatus, ContractType
from src.minicrm.models.contract_template import (
    ContractTemplate,
    TemplateStatus,
    TemplateType,
)
from src.minicrm.services.contract_service import ContractService


def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def print_contract_info(contract: Contract):
    """打印合同信息"""
    print(f"合同编号: {contract.contract_number}")
    print(f"合同名称: {contract.name}")
    print(f"合同方: {contract.party_name}")
    print(f"合同金额: {contract.get_formatted_amount()}")
    print(f"合同状态: {contract.get_status_display()}")
    print(f"合同类型: {contract.contract_type.value}")
    if contract.effective_date:
        print(f"生效日期: {contract.get_formatted_effective_date()}")
    if contract.expiry_date:
        print(f"到期日期: {contract.get_formatted_expiry_date()}")
        print(f"剩余天数: {contract.get_remaining_days()}天")
    print(f"执行进度: {contract.progress_percentage}%")


def print_template_info(template: ContractTemplate):
    """打印模板信息"""
    print(f"模板ID: {template.id}")
    print(f"模板名称: {template.template_name}")
    print(f"模板类型: {template.get_type_display()}")
    print(f"合同类型: {template.contract_type.value}")
    print(f"模板状态: {template.get_status_display()}")
    print(f"使用次数: {template.usage_count}")
    print(f"创建者: {template.created_by}")


def demo_contract_creation():
    """演示合同创建功能"""
    print_section("1. 合同创建演示")

    # 创建合同服务实例
    contract_service = ContractService()

    # 创建销售合同
    sales_contract_data = {
        "name": "ABC公司销售合同",
        "contract_number": "S202501150001",
        "contract_type": ContractType.SALES,
        "customer_id": 1,
        "party_name": "ABC制造公司",
        "contract_amount": Decimal("500000.00"),
        "currency": "CNY",
        "effective_date": datetime.now(),
        "expiry_date": datetime.now() + timedelta(days=365),
        "terms_and_conditions": "标准销售合同条款",
        "payment_terms": 30,
    }

    try:
        sales_contract = contract_service.create_contract(sales_contract_data)
        print("✅ 销售合同创建成功:")
        print_contract_info(sales_contract)
    except Exception as e:
        print(f"❌ 销售合同创建失败: {e}")

    # 创建采购合同
    purchase_contract_data = {
        "name": "XYZ供应商采购合同",
        "contract_number": "P202501150001",
        "contract_type": ContractType.PURCHASE,
        "supplier_id": 1,
        "party_name": "XYZ材料供应商",
        "contract_amount": Decimal("200000.00"),
        "currency": "CNY",
        "effective_date": datetime.now(),
        "expiry_date": datetime.now() + timedelta(days=180),
        "terms_and_conditions": "标准采购合同条款",
        "payment_terms": 45,
    }

    try:
        purchase_contract = contract_service.create_contract(purchase_contract_data)
        print("\n✅ 采购合同创建成功:")
        print_contract_info(purchase_contract)
        return sales_contract, purchase_contract
    except Exception as e:
        print(f"❌ 采购合同创建失败: {e}")
        return sales_contract, None


def demo_contract_lifecycle(contract: Contract):
    """演示合同生命周期管理"""
    print_section("2. 合同生命周期管理演示")

    contract_service = ContractService()

    try:
        print(f"原始状态: {contract.get_status_display()}")

        # 签署合同
        print("\n📝 签署合同...")
        signed_contract = contract_service.sign_contract(
            contract.id, datetime.now(), "张经理"
        )
        print(f"签署后状态: {signed_contract.get_status_display()}")

        # 更新执行进度
        print("\n📊 更新执行进度...")
        progress_contract = contract_service.update_contract_progress(
            contract.id, 25.0, Decimal("125000.00")
        )
        print(f"执行进度: {progress_contract.progress_percentage}%")
        print(f"实际金额: {progress_contract.get_formatted_actual_amount()}")
        print(f"当前状态: {progress_contract.get_status_display()}")

        # 继续更新进度
        print("\n📊 继续更新进度...")
        final_contract = contract_service.update_contract_progress(
            contract.id, 100.0, contract.contract_amount
        )
        print(f"最终进度: {final_contract.progress_percentage}%")
        print(f"最终状态: {final_contract.get_status_display()}")

    except Exception as e:
        print(f"❌ 生命周期管理失败: {e}")


def demo_contract_expiry_management():
    """演示合同到期管理"""
    print_section("3. 合同到期管理演示")

    contract_service = ContractService()

    # 创建即将到期的合同
    expiring_contract_data = {
        "name": "即将到期测试合同",
        "contract_number": "E202501150001",
        "contract_type": ContractType.SALES,
        "party_name": "测试客户",
        "contract_amount": Decimal("100000.00"),
        "effective_date": datetime.now() - timedelta(days=300),
        "expiry_date": datetime.now() + timedelta(days=15),  # 15天后到期
    }

    try:
        expiring_contract = contract_service.create_contract(expiring_contract_data)
        # 签署合同使其变为活跃状态
        contract_service.sign_contract(expiring_contract.id)

        print("✅ 即将到期合同创建成功:")
        print_contract_info(expiring_contract)

        # 获取即将到期的合同
        print("\n🔍 查找即将到期的合同...")
        expiring_contracts = contract_service.get_expiring_contracts(30)
        print(f"发现 {len(expiring_contracts)} 个即将到期的合同")

        for contract in expiring_contracts:
            print(
                f"- {contract.contract_number}: 剩余 {contract.get_remaining_days()} 天"
            )

        # 创建已过期的合同
        expired_contract_data = {
            "name": "已过期测试合同",
            "contract_number": "X202501150001",
            "contract_type": ContractType.SALES,
            "party_name": "测试客户2",
            "contract_amount": Decimal("50000.00"),
            "effective_date": datetime.now() - timedelta(days=400),
            "expiry_date": datetime.now() - timedelta(days=10),  # 10天前过期
        }

        expired_contract = contract_service.create_contract(expired_contract_data)
        contract_service.sign_contract(expired_contract.id)

        # 获取已过期的合同
        print("\n🔍 查找已过期的合同...")
        expired_contracts = contract_service.get_expired_contracts()
        print(f"发现 {len(expired_contracts)} 个已过期的合同")

        # 处理过期合同
        print("\n⚙️ 处理过期合同...")
        result = contract_service.process_expired_contracts()
        print(f"处理结果: 成功 {result['processed']} 个, 错误 {result['errors']} 个")

    except Exception as e:
        print(f"❌ 到期管理演示失败: {e}")


def demo_contract_templates():
    """演示合同模板管理"""
    print_section("4. 合同模板管理演示")

    contract_service = ContractService()

    # 创建销售合同模板
    sales_template_data = {
        "name": "标准销售合同模板",
        "template_name": "标准销售合同模板",
        "contract_type": ContractType.SALES,
        "template_type": TemplateType.SYSTEM,
        "template_status": TemplateStatus.ACTIVE,
        "created_by": "系统管理员",
        "terms_template": """
        1. 甲方应按约定时间交付产品
        2. 乙方应按约定时间支付货款
        3. 产品质量保证期为12个月
        4. 违约方应承担相应责任
        """,
        "delivery_terms_template": "货物交付方式：送货上门，运费由甲方承担",
        "warranty_terms_template": "保修期内免费维修，保修期外收费维修",
        "default_values": {
            "currency": "CNY",
            "payment_terms": 30,
            "reminder_days": 30,
        },
        "required_fields": ["party_name", "contract_amount", "expiry_date"],
    }

    try:
        sales_template = contract_service.create_template(sales_template_data)
        print("✅ 销售合同模板创建成功:")
        print_template_info(sales_template)

        # 基于模板创建合同
        print("\n📋 基于模板创建合同...")
        template_contract_data = {
            "name": "基于模板的合同",
            "contract_number": "T202501150001",
            "party_name": "模板测试客户",
            "contract_amount": Decimal("300000.00"),
            "expiry_date": datetime.now() + timedelta(days=365),
        }

        template_contract = contract_service.create_from_template(
            sales_template.id, template_contract_data
        )
        print("✅ 基于模板的合同创建成功:")
        print_contract_info(template_contract)

        # 验证模板默认值是否应用
        print(f"\n🔍 验证模板默认值:")
        print(f"货币类型: {template_contract.currency}")
        print(f"付款期限: {template_contract.payment_terms}天")
        print(f"提醒天数: {template_contract.reminder_days}天")

    except Exception as e:
        print(f"❌ 模板管理演示失败: {e}")


def demo_contract_statistics():
    """演示合同统计功能"""
    print_section("5. 合同统计功能演示")

    contract_service = ContractService()

    try:
        # 获取合同统计信息
        stats = contract_service.get_contract_statistics()

        print("📊 合同统计信息:")
        print(f"合同总数: {stats['total_contracts']}")
        print(f"合同总金额: {stats['total_amount']}")
        print(f"活跃合同金额: {stats['active_amount']}")
        print(f"即将到期合同: {stats['expiring_contracts']} 个")
        print(f"已过期合同: {stats['expired_contracts']} 个")

        print("\n📈 按状态分布:")
        for status, count in stats["status_distribution"].items():
            if count > 0:
                print(f"  {status}: {count} 个")

        print("\n📈 按类型分布:")
        for contract_type, count in stats["type_distribution"].items():
            if count > 0:
                print(f"  {contract_type}: {count} 个")

    except Exception as e:
        print(f"❌ 统计功能演示失败: {e}")


def demo_contract_renewal():
    """演示合同续约功能"""
    print_section("6. 合同续约功能演示")

    contract_service = ContractService()

    # 创建一个活跃合同用于续约
    original_contract_data = {
        "name": "原始合同",
        "contract_number": "R202501150001",
        "contract_type": ContractType.SALES,
        "party_name": "续约测试客户",
        "contract_amount": Decimal("400000.00"),
        "effective_date": datetime.now() - timedelta(days=300),
        "expiry_date": datetime.now() + timedelta(days=30),
    }

    try:
        original_contract = contract_service.create_contract(original_contract_data)
        contract_service.sign_contract(original_contract.id)

        print("✅ 原始合同创建成功:")
        print_contract_info(original_contract)

        # 创建续约合同
        print("\n🔄 创建续约合同...")
        renewal_data = {
            "contract_amount": Decimal("450000.00"),  # 增加金额
            "effective_date": datetime.now() + timedelta(days=30),
            "expiry_date": datetime.now() + timedelta(days=395),  # 新的一年
        }

        renewal_contract = contract_service.create_renewal_contract(
            original_contract.id, renewal_data
        )

        print("✅ 续约合同创建成功:")
        print_contract_info(renewal_contract)

        print(f"\n📝 续约说明:")
        print(f"原合同金额: {original_contract.get_formatted_amount()}")
        print(f"续约合同金额: {renewal_contract.get_formatted_amount()}")
        print(
            f"金额增长: {float(renewal_contract.contract_amount - original_contract.contract_amount):,.2f} 元"
        )

    except Exception as e:
        print(f"❌ 续约功能演示失败: {e}")


def main():
    """主函数"""
    print("🎯 MiniCRM 合同管理服务功能演示")
    print("=" * 60)

    try:
        # 1. 合同创建演示
        sales_contract, purchase_contract = demo_contract_creation()

        # 2. 合同生命周期管理演示
        if sales_contract:
            demo_contract_lifecycle(sales_contract)

        # 3. 合同到期管理演示
        demo_contract_expiry_management()

        # 4. 合同模板管理演示
        demo_contract_templates()

        # 5. 合同统计功能演示
        demo_contract_statistics()

        # 6. 合同续约功能演示
        demo_contract_renewal()

        print_section("演示完成")
        print("✅ 所有功能演示完成！")
        print("\n📋 合同管理服务主要功能:")
        print("  ✓ 合同创建和基础管理")
        print("  ✓ 合同生命周期管理（签署、进度跟踪、完成）")
        print("  ✓ 合同到期提醒和过期处理")
        print("  ✓ 合同模板管理和应用")
        print("  ✓ 合同统计和分析")
        print("  ✓ 合同续约管理")
        print("  ✓ 完善的业务规则验证")
        print("  ✓ 异常处理和错误管理")

    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
