"""Tools for language detection and handling."""

import logging
from typing import Optional, Dict, Any
from strands import Agent
from ..utils.language_detector import detect_query_language, LanguageDetector

logger = logging.getLogger(__name__)

class LanguageTools:
    """Tools for language detection and handling."""
    
    def __init__(self, language: str = "auto"):
        """
        Initialize language tools.
        
        Args:
            language: The language to use (default: "auto" for auto-detection)
        """
        self.language = language
        self.auto_detect_language = (language == "auto")
        self._current_language = "english"
        
    def detect_and_set_language(self, query: str) -> str:
        """
        Detect the language of the query.

        Args:
            query: The query text to analyze

        Returns:
            str: The detected or configured language
        """
        if self.auto_detect_language:
            detected_language = detect_query_language(query)
            logger.info(f"Auto-detected language: {detected_language} for query: '{query[:50]}...'")
            self._current_language = detected_language
            return detected_language
        else:
            return self.language
            
    def get_current_language(self) -> str:
        """
        Get the current language.
        
        Returns:
            str: The current language
        """
        return self._current_language
        
    def generate_initialization_info(self, query: str, detected_language: str, max_research_loops: int, 
                                    models_info: Dict[str, str]) -> str:
        """
        Generate comprehensive initialization information for the research process.

        Args:
            query: The research query
            detected_language: The detected language
            max_research_loops: Maximum research loops
            models_info: Dictionary with model information

        Returns:
            str: Formatted initialization information
        """
        from ..utils.language_detector import LanguageDetector
        language_display_name = LanguageDetector.get_language_display_name(detected_language)

        # Analyze query characteristics
        query_length = len(query)
        word_count = len(query.split())
        query_type = self.analyze_query_type(query)

        # Generate search strategy based on query
        search_strategy = self.generate_search_strategy(query, detected_language)

        from datetime import datetime
        initialization_info = f"""## 🔍 Research Initialization

### 📋 Query Analysis
- **Research Topic**: {query}
- **Query Type**: {query_type}
- **Query Length**: {query_length} characters ({word_count} words)
- **Detected Language**: {language_display_name} ({detected_language})
- **Auto-Detection**: {'✅ Enabled' if self.auto_detect_language else '❌ Disabled'}

### 🤖 AI Agent Configuration
- **Researcher Agent**: {models_info['researcher']} (Information Collection)
- **Analyst Agent**: {models_info['analyst']} (Quality Assessment)
- **Writer Agent**: {models_info['writer']} (Report Generation)
- **Max Research Loops**: {max_research_loops}

### 🎯 Search Strategy
{search_strategy}

### 📊 Expected Process Flow
1. **Information Collection** (15-35%) - Multi-source web search
2. **Quality Analysis** (35-65%) - Source verification & gap identification
3. **Additional Research** (65-85%) - Targeted follow-up searches (if needed)
4. **Report Generation** (85-100%) - Comprehensive report synthesis

### ⏰ Session Information
- **Start Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Session ID**: {datetime.now().strftime('%Y%m%d_%H%M%S')}

---
🚀 **Initializing research process...**"""

        return initialization_info
        
    def analyze_query_type(self, query: str) -> str:
        """
        Analyze the type of research query.

        Args:
            query: The research query

        Returns:
            str: Query type description
        """
        query_lower = query.lower()

        # Question patterns
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which',
                         '什么', '如何', '怎么', '为什么', '什么时候', '哪里', '谁', '哪个',
                         '何', 'なに', 'どう', 'なぜ', 'いつ', 'どこ', 'だれ', 'どの',
                         '무엇', '어떻게', '왜', '언제', '어디', '누구', '어느']

        if any(word in query_lower for word in question_words):
            if any(word in query_lower for word in ['how', '如何', '怎么', 'どう', '어떻게']):
                return "📚 How-to / Process Inquiry"
            elif any(word in query_lower for word in ['what', '什么', 'なに', '무엇']):
                return "🔍 Definition / Concept Research"
            elif any(word in query_lower for word in ['why', '为什么', 'なぜ', '왜']):
                return "🤔 Causal Analysis"
            else:
                return "❓ General Question"

        # Topic research patterns
        elif any(word in query_lower for word in ['trend', 'development', 'future', 'latest', 'recent',
                                                 '趋势', '发展', '未来', '最新', '最近',
                                                 'トレンド', '発展', '未来', '最新', '最近',
                                                 '트렌드', '발전', '미래', '최신', '최근']):
            return "📈 Trend Analysis"

        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference',
                                                 '比较', '对比', '区别',
                                                 '比較', '対比', '違い',
                                                 '비교', '대비', '차이']):
            return "⚖️ Comparative Analysis"

        elif any(word in query_lower for word in ['market', 'industry', 'business', 'company',
                                                 '市场', '行业', '商业', '公司',
                                                 '市場', '業界', 'ビジネス', '会社',
                                                 '시장', '업계', '비즈니스', '회사']):
            return "💼 Market/Business Research"

        else:
            return "📖 General Topic Research"
            
    def generate_search_strategy(self, query: str, language: str) -> str:
        """
        Generate a search strategy description based on query and language.

        Args:
            query: The research query
            language: The detected language

        Returns:
            str: Search strategy description
        """
        query_type = self.analyze_query_type(query)

        # Base strategy
        strategy = f"""**Primary Approach**: Multi-source information gathering
**Language Focus**: {language} sources with English supplements
**Search Engines**: Tavily, Google, DuckDuckGo, Wikipedia
**Source Types**: Academic papers, news articles, official documents, expert blogs"""

        # Add specific strategies based on query type
        if "Definition" in query_type:
            strategy += "\n**Specialized Focus**: Authoritative definitions, academic sources, official documentation"
        elif "Trend" in query_type:
            strategy += "\n**Specialized Focus**: Recent publications, market reports, industry analyses"
        elif "Comparative" in query_type:
            strategy += "\n**Specialized Focus**: Side-by-side comparisons, feature matrices, expert reviews"
        elif "Market" in query_type:
            strategy += "\n**Specialized Focus**: Market research, financial reports, industry statistics"
        elif "How-to" in query_type:
            strategy += "\n**Specialized Focus**: Step-by-step guides, tutorials, best practices"

        # Add language-specific considerations
        if language == "chinese":
            strategy += "\n**Regional Sources**: 百度, 知乎, 学术搜索, 官方网站"
        elif language == "japanese":
            strategy += "\n**Regional Sources**: Yahoo Japan, Goo, J-STAGE, 政府サイト"
        elif language == "korean":
            strategy += "\n**Regional Sources**: Naver, Daum, KISS, 정부사이트"

        return strategy
