# MiniCRM 依赖准入规范与导入白/黑名单

目的：用清晰的分层依赖规则、白/黑名单与CI校验，约束跨层与跨组件实现的导入，降低耦合与回归风险。

适用范围：src/minicrm 下所有 Python 模块（core/data/models/services/ui/transfunctions）。

---

## 1. 分层模型与允许依赖

层级（由底向上）：
- transfunctions：通用函数库（formatting/calculations/validation/data_operations/async）
- core：异常、日志、性能、架构工具、依赖注入框架（非具体绑定）
- models：领域模型
- data：数据库 schema/initializer/manager 与 DAO 层
- services：业务编排与聚合
- ui：界面组件、页面管理、主题与响应式

允许的依赖方向（-> 表示“可以依赖”）：
- transfunctions -> 无（最底层）
- core -> transfunctions（仅工具性依赖）
- models -> core、transfunctions
- data -> models、core、transfunctions
- services -> data、models、core、transfunctions
- ui -> services、models、core（受限）、transfunctions

禁止示例：
- ui -> data（任何形式）
- services -> ui
- data -> services/ui
- core -> services/data/具体实现（仅允许工具性）

---

## 2. UI 组件内部的边界

- 只允许通过以下方式使用其他组件：
  - 依赖同层公开的 Facade/Manager/Utils 接口（稳定入口）
  - 通过信号/事件/依赖注入/装配传入依赖，避免直接 import 实现类
- 推荐导入形式（示例）：
  - from minicrm.ui.components.table import TableDataManager  # 通过子包 Facade 暴露
  - from minicrm.ui.components.search.search_widget import SearchWidget  # 公开组件入口
- 禁止导入：
  - 直接 import 其他组件的“实现文件”（非 manager/utils/facade）
  - 直接 import 其他组件的私有模块（下划线或内部路径）

---

## 3. 导入白/黑名单（按层）

白名单（正则/前缀，按消费层列出）
- ui 允许导入：
  - ^minicrm\.services(\.|$)
  - ^minicrm\.models(\.|$)
  - ^minicrm\.core\.(exceptions|logger|performance|utils)(\.|$)
  - ^minicrm\.transfunctions(\.|$)
  - ^minicrm\.ui\.components\.[a-z0-9_]+\.(?:.*_manager|.*_utils|.*_facade)$
  - 公开门面：^minicrm\.ui\.components\.(data_table|search\.search_widget|table\.[a-z0-9_]+)$
- services 允许导入：
  - ^minicrm\.data(\.|$)
  - ^minicrm\.models(\.|$)
  - ^minicrm\.core(\.|$)
  - ^minicrm\.transfunctions(\.|$)
- data 允许导入：
  - ^minicrm\.models(\.|$)
  - ^minicrm\.core(\.|$)
  - ^minicrm\.transfunctions(\.|$)
- models 允许导入：
  - ^minicrm\.core(\.|$)
  - ^minicrm\.transfunctions(\.|$)
- core 允许导入：
  - ^minicrm\.transfunctions(\.|$)

黑名单（正则/前缀）
- 所有层：
  - 禁止循环依赖（CI 自动检测）
- ui：
  - ^minicrm\.data(\.|$)  # UI 直连数据层
  - ^minicrm\.ui\.components\.[^.]+\.[^.]+$ 且不以(_manager|_utils|_facade)结尾  # 跨组件实现导入
- services：
  - ^minicrm\.ui(\.|$)
- data：
  - ^minicrm\.services(\.|$)
  - 直接导入具体数据库实现：^minicrm\.data\.database(?!\.interfaces)  # 应通过接口/manager 注入
- core：
  - ^minicrm\.(services|data) 具体实现  # 仅允许抽象与工具

备注：如内部尚未建立 database 接口包，可先约定接口路径命名（例如 minicrm.data.database.interfaces），逐步迁移。

---

## 4. transfunctions 导入规范

- 使用稳定入口，避免耦合子包内部布局：
  - from transfunctions.formatting import format_currency, format_date, format_percentage
  - from transfunctions.calculations import calculate_average, calculate_growth_rate
  - from transfunctions.validation import validate_required_fields, ValidationError
  - from transfunctions.data_operations import create_crud_template
- 如确需使用子模块，请在 transfunctions 层增加统一重导出，业务侧仍从稳定入口导入。

---

## 5. CI 校验方案（示例脚本）

以下 Python 脚本可在 CI 中执行，扫描 src/minicrm 下所有 .py 文件的 import，并与白/黑名单匹配：

```python
# ci_check_imports.py
import ast
import re
from pathlib import Path

ROOT = Path('src/minicrm')
BLACKLIST = [
    re.compile(r'^minicrm\.data(\.|$)'),  # for UI only; 看调用方层级
]
UI_PATH = re.compile(r'.*/ui/.*')

# 仅演示：UI 禁止导入 data；可扩展到完整白/黑名单表

def iter_imports(py: Path):
    tree = ast.parse(py.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                yield n.name, node.lineno
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ''
            yield mod, node.lineno

violations = []
for py in ROOT.rglob('*.py'):
    is_ui = bool(UI_PATH.match(str(py)))
    for mod, line in iter_imports(py):
        if is_ui and any(pat.match(mod) for pat in BLACKLIST):
            violations.append((str(py), line, mod))

if violations:
    print('\nImport dependency violations:')
    for path, line, mod in violations:
        print(f' - {path}:{line} -> {mod}')
    raise SystemExit(1)
```

在 CI 中：
- 将脚本加入 `scripts/` 并在 workflow 中执行；
- 可拓展为：按文件路径推断层级，然后对照完整白/黑名单；
- 搭配 ruff/mypy 与现有 `architecture_validator.py` 输出综合报告。

---

## 6. 示例（允许 vs 禁止）

允许：
- ui → services：`from minicrm.services.analytics_service import AnalyticsService`
- services → data：`from minicrm.data.dao.customer_dao import CustomerDAO`
- data → core/transfunctions：`from transfunctions.data_operations import create_crud_template`
- ui 通过门面：`from minicrm.ui.components.data_table import DataTable`

禁止：
- ui → data：`from minicrm.data.database import DatabaseManager`
- ui 跨组件实现：`from minicrm.ui.components.metric_card import MetricCard`（应通过门面或 manager）
- core → 具体实现：`from minicrm.services.customer_service import CustomerService`
- data → 具体 database 实现：`from minicrm.data.database import DatabaseManager`（应依赖接口注入）

---

## 7. 推行步骤

1) 文档落地并在评审中执行；
2) 在 CI 中开启导入校验脚本（先以 warning 观察，再切换为 hard fail）；
3) 为缺失的“接口/门面”补齐导出，提供替代导入路径；
4) 批量迁移 import（脚本辅助）；
5) 清理遗留与新增规则持续迭代。

---

## 8. 常见问答

- Q: 某些 UI 组件确需直接复用另一个组件的内部实现？
  - A: 将可复用能力上移为 manager/utils 或 Facade，对外暴露稳定入口；避免直接耦合实现类。
- Q: DAO 如何避免直连 DatabaseManager？
  - A: 定义 database 接口（Protocol/ABC），在构造/工厂中注入实现；或通过 database_manager 门面转发。
- Q: 旧版组件如何处理？
  - A: 标注弃用并替换运行路径；CI 黑名单禁止旧路径导入。 
