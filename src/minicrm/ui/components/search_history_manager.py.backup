"""
MiniCRM 搜索历史管理器

负责管理搜索历史和搜索建议功能，包括：
- 搜索历史记录
- 搜索建议管理
- 自动完成功能
"""

import logging
from typing import Any

from PySide6.QtCore import QObject, QStringListModel, Qt
from PySide6.QtWidgets import QCompleter, QLineEdit

from minicrm.ui.components.search_config import SearchBarConfig


class SearchHistoryManager(QObject):
    """
    搜索历史管理器

    负责管理搜索历史记录和搜索建议功能。
    """

    def __init__(self, config: SearchBarConfig, parent: QObject | None = None):
        """
        初始化搜索历史管理器

        Args:
            config: 搜索栏配置
            parent: 父对象
        """
        super().__init__(parent)

        # 配置
        self._config = config

        # 日志记录器
        self._logger = logging.getLogger(self.__class__.__name__)

        # 搜索数据
        self._search_history: list[str] = []
        self._suggestions: list[str] = []

        # 自动完成器
        self._completer: QCompleter | None = None
        self._search_input: QLineEdit | None = None

        self._logger.debug("搜索历史管理器初始化完成")

    def setup_completer(self, search_input: QLineEdit) -> None:
        """
        设置自动完成器

        Args:
            search_input: 搜索输入框
        """
        try:
            if not self._config.enable_suggestions:
                return

            self._search_input = search_input

            # 创建自动完成器
            self._completer = QCompleter()
            self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self._completer.setFilterMode(Qt.MatchFlag.MatchContains)

            # 设置模型
            model = QStringListModel()
            self._completer.setModel(model)

            # 关联到输入框
            search_input.setCompleter(self._completer)

            self._logger.debug("自动完成器设置完成")

        except Exception as e:
            self._logger.error(f"设置自动完成器失败: {e}")

    def add_to_history(self, query: str) -> None:
        """
        添加到搜索历史

        Args:
            query: 搜索查询
        """
        try:
            if not self._config.enable_history or not query.strip():
                return

            # 移除重复项并添加到开头
            if query in self._search_history:
                self._search_history.remove(query)

            self._search_history.insert(0, query)

            # 限制历史记录数量
            max_items = self._config.max_history_items
            if len(self._search_history) > max_items:
                self._search_history = self._search_history[:max_items]

            # 更新自动完成
            self._update_completer()

            self._logger.debug(f"添加搜索历史: {query}")

        except Exception as e:
            self._logger.error(f"添加搜索历史失败: {e}")

    def set_suggestions(self, suggestions: list[str]) -> None:
        """
        设置搜索建议

        Args:
            suggestions: 建议列表
        """
        try:
            self._suggestions = suggestions
            self._update_completer()

            self._logger.debug(f"设置搜索建议: {len(suggestions)}个")

        except Exception as e:
            self._logger.error(f"设置搜索建议失败: {e}")

    def get_history(self) -> list[str]:
        """
        获取搜索历史

        Returns:
            list[str]: 搜索历史列表
        """
        return self._search_history.copy()

    def get_suggestions(self) -> list[str]:
        """
        获取搜索建议

        Returns:
            list[str]: 搜索建议列表
        """
        return self._suggestions.copy()

    def clear_history(self) -> None:
        """清除搜索历史"""
        try:
            self._search_history.clear()
            self._update_completer()

            self._logger.debug("搜索历史已清除")

        except Exception as e:
            self._logger.error(f"清除搜索历史失败: {e}")

    def remove_from_history(self, query: str) -> None:
        """
        从历史记录中移除指定查询

        Args:
            query: 要移除的查询
        """
        try:
            if query in self._search_history:
                self._search_history.remove(query)
                self._update_completer()

                self._logger.debug(f"从历史记录中移除: {query}")

        except Exception as e:
            self._logger.error(f"移除历史记录失败: {e}")

    def get_popular_queries(self, limit: int = 5) -> list[str]:
        """
        获取热门搜索查询（基于历史记录频率）

        Args:
            limit: 返回数量限制

        Returns:
            list[str]: 热门查询列表
        """
        try:
            # 简单实现：返回最近的查询
            # 实际项目中可以基于查询频率统计
            return self._search_history[:limit]

        except Exception as e:
            self._logger.error(f"获取热门查询失败: {e}")
            return []

    def search_in_history(self, keyword: str) -> list[str]:
        """
        在历史记录中搜索包含关键词的查询

        Args:
            keyword: 搜索关键词

        Returns:
            list[str]: 匹配的历史查询列表
        """
        try:
            if not keyword.strip():
                return []

            keyword_lower = keyword.lower()
            matches = [
                query
                for query in self._search_history
                if keyword_lower in query.lower()
            ]

            return matches

        except Exception as e:
            self._logger.error(f"搜索历史记录失败: {e}")
            return []

    def _update_completer(self) -> None:
        """更新自动完成器"""
        try:
            if not self._completer:
                return

            model = self._completer.model()
            if isinstance(model, QStringListModel):
                # 合并历史记录和建议
                all_suggestions = list(set(self._search_history + self._suggestions))
                model.setStringList(all_suggestions)

        except Exception as e:
            self._logger.error(f"更新自动完成器失败: {e}")

    def cleanup_resources(self) -> None:
        """清理资源"""
        try:
            if self._completer:
                self._completer.deleteLater()
                self._completer = None

            self._logger.debug("搜索历史管理器资源清理完成")

        except Exception as e:
            self._logger.error(f"搜索历史管理器资源清理失败: {e}")

    def export_history(self) -> dict[str, Any]:
        """
        导出搜索历史数据

        Returns:
            dict[str, Any]: 历史数据
        """
        return {
            "history": self._search_history.copy(),
            "suggestions": self._suggestions.copy(),
        }

    def import_history(self, data: dict[str, Any]) -> None:
        """
        导入搜索历史数据

        Args:
            data: 历史数据
        """
        try:
            if "history" in data:
                self._search_history = data["history"][: self._config.max_history_items]

            if "suggestions" in data:
                self._suggestions = data["suggestions"]

            self._update_completer()

            self._logger.debug("搜索历史数据导入完成")

        except Exception as e:
            self._logger.error(f"导入搜索历史数据失败: {e}")

    def __str__(self) -> str:
        """返回搜索历史管理器的字符串表示"""
        return f"SearchHistoryManager(history={len(self._search_history)}, suggestions={len(self._suggestions)})"
