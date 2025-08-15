"""
MiniCRM 搜索栏使用示例

展示重构后的搜索栏组件的使用方法。
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from minicrm.ui.components.search_bar import SearchBar
from minicrm.ui.components.search_config import FilterConfig, SearchBarConfig


class SearchBarDemo(QMainWindow):
    """搜索栏演示窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MiniCRM 搜索栏演示")
        self.setGeometry(100, 100, 800, 600)

        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # 1. 基础搜索栏
        basic_config = SearchBarConfig.create_simple()
        basic_search = SearchBar(basic_config)
        basic_search.search_requested.connect(self.on_basic_search)
        layout.addWidget(basic_search)

        # 2. 全功能搜索栏
        full_config = SearchBarConfig.create_full_featured()
        full_search = SearchBar(full_config)

        # 添加筛选器
        self.setup_filters(full_search)

        # 设置搜索建议
        suggestions = ["客户名称", "联系电话", "公司地址", "业务类型"]
        full_search.set_suggestions(suggestions)

        # 连接信号
        full_search.search_requested.connect(self.on_full_search)
        full_search.filter_changed.connect(self.on_filter_changed)

        layout.addWidget(full_search)

        # 3. 自定义配置搜索栏
        custom_config = SearchBarConfig(
            placeholder="搜索板材客户...",
            search_button_text="🔍",
            clear_button_text="❌",
            advanced_button_text="⚙️",
            search_delay=500,
            max_history_items=30,
        )
        custom_search = SearchBar(custom_config)
        custom_search.search_requested.connect(self.on_custom_search)
        layout.addWidget(custom_search)

    def setup_filters(self, search_bar: SearchBar) -> None:
        """设置筛选器"""
        # 客户类型筛选器
        customer_type_filter = FilterConfig.create_combo(
            key="customer_type",
            title="客户类型",
            options=[
                {"label": "生态板客户", "value": "eco_board"},
                {"label": "家具板客户", "value": "furniture_board"},
                {"label": "阻燃板客户", "value": "fire_resistant"},
            ],
        )
        search_bar.add_filter(customer_type_filter)

        # 创建日期筛选器
        date_filter = FilterConfig.create_date(key="created_date", title="创建日期")
        search_bar.add_filter(date_filter)

        # 订单金额筛选器
        amount_filter = FilterConfig.create_number(
            key="order_amount", title="订单金额", min_value=0, max_value=1000000
        )
        search_bar.add_filter(amount_filter)

        # 地区筛选器
        region_filter = FilterConfig.create_text(
            key="region", title="地区", placeholder="输入地区名称..."
        )
        search_bar.add_filter(region_filter)

        # 活跃状态筛选器
        active_filter = FilterConfig.create_checkbox(
            key="is_active", title="活跃状态", checkbox_text="仅显示活跃客户"
        )
        search_bar.add_filter(active_filter)

    def on_basic_search(self, query: str, filters: dict) -> None:
        """处理基础搜索"""
        print(f"基础搜索: '{query}'")

    def on_full_search(self, query: str, filters: dict) -> None:
        """处理全功能搜索"""
        print(f"全功能搜索: '{query}', 筛选条件: {filters}")

    def on_custom_search(self, query: str, filters: dict) -> None:
        """处理自定义搜索"""
        print(f"自定义搜索: '{query}'")

    def on_filter_changed(self, filters: dict) -> None:
        """处理筛选条件变化"""
        print(f"筛选条件变化: {filters}")


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 创建演示窗口
    demo = SearchBarDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
