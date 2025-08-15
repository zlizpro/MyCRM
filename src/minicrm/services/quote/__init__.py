"""
MiniCRM 报价服务模块

重构后的报价服务，按照单一职责原则拆分为多个专门服务：
- QuoteCoreService: 报价基础CRUD操作
- QuoteComparisonService: 报价比对分析
- QuoteSuggestionService: 智能报价建议
- QuoteAnalyticsService: 成功率统计分析
- QuoteExpiryService: 过期管理和预警
"""

from .quote_analytics_service import QuoteAnalyticsService
from .quote_comparison_service import QuoteComparisonService
from .quote_core_service import QuoteCoreService
from .quote_expiry_service import QuoteExpiryService
from .quote_suggestion_service import QuoteSuggestionService


__all__ = [
    "QuoteCoreService",
    "QuoteComparisonService",
    "QuoteSuggestionService",
    "QuoteAnalyticsService",
    "QuoteExpiryService",
]
