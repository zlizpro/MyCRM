# Transfunctions 库参考指南

## 概述

[Transfunctions](https://github.com/pomponchik/transfunctions) 是一个创新的Python库，旨在解决Python生态系统中最重要的问题之一：同步和异步代码的重复。通过使用模板和代码生成技术，它消除了因语法差异导致的代码重复。

## 核心概念

### 问题背景

自从Python引入`asyncio`模块以来，许多知名库都有了异步版本，导致大量代码重复。这是因为Python选择了通过语法实现异步的方式（`async`/`await`关键字），使代码变成"[多色的](https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/)"：
- 🔴 红色函数（异步）
- 🔵 蓝色函数（同步）

### 解决方案

Transfunctions通过模板化解决这个问题：
- 📝 编写一个模板函数
- 🔄 生成多个版本：同步、异步、生成器
- ✨ 避免代码重复

## 基本用法

### 1. 安装

```bash
pip install transfunctions
```

### 2. 基础示例

```python
from asyncio import run
from transfunctions import (
    transfunction,
    sync_context,
    async_context,
    generator_context,
)

@transfunction
def template():
    print('共同部分, ', end='')
    with sync_context:
        print("这是普通函数!")
    with async_context:
        print("这是异步函数!")
    with generator_context:
        print("这是生成器函数!")
        yield

# 生成普通函数
function = template.get_usual_function()
function()
#> 共同部分, 这是普通函数!

# 生成异步函数
async_function = template.get_async_function()
run(async_function())
#> 共同部分, 这是异步函数!

# 生成生成器函数
generator_function = template.get_generator_function()
list(generator_function())
#> 共同部分, 这是生成器函数!
```

## 标记器（Markers）

### 上下文管理器

- `sync_context`: 标记同步代码块
- `async_context`: 标记异步代码块
- `generator_context`: 标记生成器代码块

### await标记

```python
from asyncio import sleep
from transfunctions import transfunction, async_context, await_it

@transfunction
def template():
    with async_context:
        await_it(sleep(5))

# 生成的异步函数等价于：
# async def template():
#     await sleep(5)
```

## 超级函数（Superfunctions）

最强大的功能 - 自动选择函数类型：

```python
from transfunctions import (
    superfunction,
    sync_context,
    async_context,
    generator_context,
)

@superfunction
def my_superfunction():
    print('共同部分, ', end='')
    with sync_context:
        print("普通调用!")
    with async_context:
        print("异步调用!")
    with generator_context:
        print("生成器调用!")
        yield

# 普通调用（使用波浪号语法）
~my_superfunction()
#> 共同部分, 普通调用!

# 异步调用
from asyncio import run
run(my_superfunction())
#> 共同部分, 异步调用!

# 生成器调用
list(my_superfunction())
#> 共同部分, 生成器调用!
```

## 在MiniCRM中的应用潜力

### 1. 数据库操作统一

```python
from transfunctions import transfunction, sync_context, async_context, await_it

@transfunction
def database_query_template(sql: str, params: tuple = ()):
    """统一的数据库查询模板"""
    with sync_context:
        # 同步数据库操作
        return sqlite3_connection.execute(sql, params).fetchall()

    with async_context:
        # 异步数据库操作
        return await_it(async_connection.execute(sql, params))

# 生成同步版本
sync_query = database_query_template.get_usual_function()

# 生成异步版本
async_query = database_query_template.get_async_function()
```

### 2. API客户端统一

```python
@transfunction
def api_request_template(url: str, data: dict = None):
    """统一的API请求模板"""
    with sync_context:
        import requests
        return requests.post(url, json=data)

    with async_context:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            return await_it(session.post(url, json=data))
```

### 3. 文件操作统一

```python
@transfunction
def file_operation_template(file_path: str, content: str = None):
    """统一的文件操作模板"""
    with sync_context:
        if content:
            with open(file_path, 'w') as f:
                f.write(content)
        else:
            with open(file_path, 'r') as f:
                return f.read()

    with async_context:
        import aiofiles
        if content:
            async with aiofiles.open(file_path, 'w') as f:
                await_it(f.write(content))
        else:
            async with aiofiles.open(file_path, 'r') as f:
                return await_it(f.read())
```

## 最佳实践

### 1. 模板设计原则

- ✅ 将共同逻辑放在上下文管理器外
- ✅ 使用适当的标记器分离不同类型的代码
- ✅ 避免在模板上使用第三方装饰器

### 2. 错误处理

```python
@transfunction
def error_handling_template():
    try:
        with sync_context:
            # 同步错误处理
            result = risky_sync_operation()

        with async_context:
            # 异步错误处理
            result = await_it(risky_async_operation())

        return result
    except Exception as e:
        # 共同的错误处理逻辑
        logger.error(f"操作失败: {e}")
        raise
```

### 3. 类型注解

```python
from typing import Union, Awaitable, Generator

@transfunction
def typed_template() -> Union[str, Awaitable[str], Generator[str, None, None]]:
    with sync_context:
        return "同步结果"

    with async_context:
        return "异步结果"

    with generator_context:
        yield "生成器结果"
```

## 限制和注意事项

### 1. 语法限制

- ❌ 不能在非异步上下文中使用`await_it`
- ❌ 不能在非生成器上下文中使用`yield`
- ❌ 不能在模板上使用第三方装饰器

### 2. 超级函数限制

使用`tilde_syntax=False`模式时：
- ❌ 不能使用返回值
- ❌ 异常处理受限

### 3. 调试考虑

- 生成的代码可能难以调试
- 需要理解AST转换过程

## 与MiniCRM Transfunctions的关系

我们的MiniCRM项目中的`transfunctions`库专注于：
- 🔧 **可复用函数**：验证、格式化、计算
- 📊 **业务逻辑统一**：客户管理、报价计算等
- 🎯 **代码重用**：避免重复实现

而pomponchik/transfunctions专注于：
- 🔄 **同步/异步统一**：消除语法差异
- 🏗️ **代码生成**：基于模板生成多版本函数
- ✨ **超级函数**：智能函数类型选择

两者可以互补使用：
```python
# 结合使用示例
from transfunctions import superfunction, sync_context, async_context
from minicrm.transfunctions import validate_customer_data, format_currency

@superfunction
def process_customer_data(customer_data: dict):
    # 使用MiniCRM的验证函数
    errors = validate_customer_data(customer_data)
    if errors:
        raise ValueError(f"数据验证失败: {errors}")

    with sync_context:
        # 同步处理
        result = sync_database.save_customer(customer_data)

    with async_context:
        # 异步处理
        result = await_it(async_database.save_customer(customer_data))

    # 使用MiniCRM的格式化函数
    return {
        'id': result.id,
        'name': customer_data['name'],
        'formatted_phone': format_phone(customer_data['phone'])
    }
```

## 总结

Transfunctions库为Python开发者提供了一个优雅的解决方案来处理同步/异步代码重复问题。虽然它不能完全解决Python的"多色函数"问题，但它提供了一个实用的工具来减少代码重复并提高开发效率。

在MiniCRM项目中，我们可以考虑在需要同时支持同步和异步操作的场景中使用这个库，特别是在数据库操作、API调用和文件处理等方面。
