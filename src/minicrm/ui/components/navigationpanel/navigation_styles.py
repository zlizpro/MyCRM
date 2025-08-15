"""
MiniCRM 导航面板样式定义

定义导航面板的样式表和主题配置
"""


class NavigationStyles:
    """导航面板样式管理器"""

    @staticmethod
    def get_default_stylesheet() -> str:
        """获取默认样式表"""
        return """
            QWidget#navigationTitle {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }

            QLabel#navigationTitleLabel {
                color: #495057;
                font-weight: bold;
            }

            QTreeWidget#navigationTree {
                background-color: #ffffff;
                border: none;
                outline: none;
                font-size: 13px;
            }

            QTreeWidget#navigationTree::item {
                height: 36px;
                padding: 4px 8px;
                border: none;
            }

            QTreeWidget#navigationTree::item:hover {
                background-color: #e9ecef;
            }

            QTreeWidget#navigationTree::item:selected {
                background-color: #007bff;
                color: white;
            }

            QTreeWidget#navigationTree::item:selected:hover {
                background-color: #0056b3;
            }

            QTreeWidget#navigationTree::branch {
                background: transparent;
            }

            QTreeWidget#navigationTree::branch:has-children:!has-siblings:closed,
            QTreeWidget#navigationTree::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(:/icons/branch-closed.png);
            }

            QTreeWidget#navigationTree::branch:open:has-children:!has-siblings,
            QTreeWidget#navigationTree::branch:open:has-children:has-siblings {
                border-image: none;
                image: url(:/icons/branch-open.png);
            }
        """

    @staticmethod
    def get_dark_theme_stylesheet() -> str:
        """获取深色主题样式表"""
        return """
            QWidget#navigationTitle {
                background-color: #2b2b2b;
                border-bottom: 1px solid #404040;
            }

            QLabel#navigationTitleLabel {
                color: #ffffff;
                font-weight: bold;
            }

            QTreeWidget#navigationTree {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                outline: none;
                font-size: 13px;
            }

            QTreeWidget#navigationTree::item {
                height: 36px;
                padding: 4px 8px;
                border: none;
            }

            QTreeWidget#navigationTree::item:hover {
                background-color: #404040;
            }

            QTreeWidget#navigationTree::item:selected {
                background-color: #0078d4;
                color: white;
            }

            QTreeWidget#navigationTree::item:selected:hover {
                background-color: #106ebe;
            }

            QTreeWidget#navigationTree::branch {
                background: transparent;
            }
        """
