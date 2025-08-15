#!/usr/bin/env python3
"""
测试样例文件 - 包含各种代码质量问题
用于验证代码质量检查器的功能
"""

import os
import sys
import json  # 这个导入未使用
from typing import Dict, List
import datetime


class customerManager:  # 类名应该使用大驼峰命名
    """客户管理器"""

    def __init__(self, database_path):  # 缺少类型注解
        self.db_path = database_path
        self.customers = []

    def addCustomer(self, customerData):  # 函数名应该使用下划线命名，缺少类型注解和文档字符串
        if not customerData:
            return False

        # 这行太长了，超过了88个字符的限制，应该被检查器发现并建议拆分为多行以提高可读性
        customer_id = self._generate_customer_id(customerData.get(
            'name', ''), customerData.get('phone', ''), customerData.get('email', ''))

        self.customers.append({
            'id': customer_id,
            'data': customerData,
            'created_at': datetime.datetime.now()
        })
        return True

    def _generate_customer_id(self, name, phone, email):  # 缺少类型注解和文档字符串
        return f"{name}_{phone}_{email}".replace(' ', '_')

    def get_customer_by_id(self, customer_id):
        # 这个函数有高复杂度
        for customer in self.customers:
            if customer['id'] == customer_id:
                if customer['data']:
                    if customer['data'].get('active', True):
                        if customer['data'].get('verified', False):
                            if customer['created_at']:
                                if (datetime.datetime.now() - customer['created_at']).days < 365:
                                    if customer['data'].get('type') == 'premium':
                                        return customer
                                    elif customer['data'].get('type') == 'standard':
                                        return customer
                                    else:
                                        return None
        return None


def processCustomerData(data):  # 函数名应该使用下划线命名，缺少类型注解和文档字符串
    if not data:
        return None

    result = {}
    for key, value in data.items():
        if key == 'name':
            result['customer_name'] = value.strip().title()
        elif key == 'phone':
            result['customer_phone'] = value.replace('-', '').replace(' ', '')
        elif key == 'email':
            result['customer_email'] = value.lower().strip()

    return result


# 全局变量应该使用大写命名
default_config = {
    'max_customers': 1000,
    'auto_save': True
}


class DataProcessor:
    pass  # 空类，缺少文档字符串


def short():  # 缺少文档字符串
    pass
