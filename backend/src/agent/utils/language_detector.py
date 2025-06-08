"""Language detection utility for automatically determining query language."""

import re
from typing import Dict, Tuple


class LanguageDetector:
    """Utility class for detecting the language of input text."""
    
    # Language patterns and characteristics
    LANGUAGE_PATTERNS = {
        'chinese': {
            'patterns': [
                r'[\u4e00-\u9fff]',  # CJK Unified Ideographs
                r'[\u3400-\u4dbf]',  # CJK Extension A
                r'[\uf900-\ufaff]',  # CJK Compatibility Ideographs
            ],
            'common_words': ['的', '是', '在', '有', '和', '了', '不', '我', '你', '他', '她', '它', '这', '那', '什么', '怎么', '为什么'],
            'name': 'chinese'
        },
        'japanese': {
            'patterns': [
                r'[\u3040-\u309f]',  # Hiragana
                r'[\u30a0-\u30ff]',  # Katakana
                r'[\u4e00-\u9fff]',  # Kanji (shared with Chinese)
            ],
            'common_words': ['の', 'に', 'は', 'を', 'が', 'で', 'と', 'から', 'まで', 'です', 'である', 'した', 'する'],
            'name': 'japanese'
        },
        'korean': {
            'patterns': [
                r'[\uac00-\ud7af]',  # Hangul Syllables
                r'[\u1100-\u11ff]',  # Hangul Jamo
                r'[\u3130-\u318f]',  # Hangul Compatibility Jamo
            ],
            'common_words': ['이', '가', '을', '를', '에', '에서', '와', '과', '의', '는', '은', '도', '만', '까지'],
            'name': 'korean'
        },
        'english': {
            'patterns': [
                r'[a-zA-Z]',  # Basic Latin alphabet
            ],
            'common_words': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'],
            'name': 'english'
        },
        'spanish': {
            'patterns': [
                r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]',  # Spanish alphabet with accents
            ],
            'common_words': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para'],
            'name': 'spanish'
        },
        'french': {
            'patterns': [
                r'[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]',  # French alphabet with accents
            ],
            'common_words': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se'],
            'name': 'french'
        },
        'german': {
            'patterns': [
                r'[a-zA-ZäöüßÄÖÜ]',  # German alphabet with umlauts
            ],
            'common_words': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als'],
            'name': 'german'
        },
        'russian': {
            'patterns': [
                r'[а-яёА-ЯЁ]',  # Cyrillic alphabet
            ],
            'common_words': ['в', 'и', 'не', 'на', 'я', 'быть', 'тот', 'он', 'оно', 'она', 'они', 'с', 'а', 'как', 'это', 'по', 'но', 'они', 'мы', 'этот'],
            'name': 'russian'
        }
    }
    
    @classmethod
    def detect_language(cls, text: str, confidence_threshold: float = 0.3) -> Tuple[str, float]:
        """
        Detect the language of the given text.
        
        Args:
            text: The text to analyze
            confidence_threshold: Minimum confidence score to return a language (default: 0.3)
            
        Returns:
            Tuple[str, float]: (language_name, confidence_score)
        """
        if not text or not text.strip():
            return 'english', 0.0
        
        text = text.strip().lower()
        language_scores = {}
        
        # Calculate scores for each language
        for lang_code, lang_data in cls.LANGUAGE_PATTERNS.items():
            score = cls._calculate_language_score(text, lang_data)
            language_scores[lang_code] = score
        
        # Find the language with the highest score
        best_language = max(language_scores, key=language_scores.get)
        best_score = language_scores[best_language]
        
        # Apply confidence threshold
        if best_score < confidence_threshold:
            # Default to English if confidence is too low
            return 'english', best_score
        
        return best_language, best_score
    
    @classmethod
    def _calculate_language_score(cls, text: str, lang_data: Dict) -> float:
        """
        Calculate a score for how likely the text is in a specific language.
        
        Args:
            text: The text to analyze
            lang_data: Language data containing patterns and common words
            
        Returns:
            float: Score between 0 and 1
        """
        total_chars = len(text)
        if total_chars == 0:
            return 0.0
        
        # Score based on character patterns
        pattern_score = 0.0
        for pattern in lang_data['patterns']:
            matches = len(re.findall(pattern, text))
            pattern_score += matches / total_chars
        
        # Score based on common words
        words = re.findall(r'\b\w+\b', text.lower())
        word_score = 0.0
        if words:
            common_word_count = sum(1 for word in words if word in lang_data['common_words'])
            word_score = common_word_count / len(words)
        
        # Combine scores (weighted average)
        combined_score = (pattern_score * 0.7) + (word_score * 0.3)
        
        # Normalize to 0-1 range
        return min(combined_score, 1.0)
    
    @classmethod
    def get_language_display_name(cls, language_code: str) -> str:
        """
        Get the display name for a language code.
        
        Args:
            language_code: The language code
            
        Returns:
            str: Display name for the language
        """
        display_names = {
            'chinese': '中文',
            'english': 'English',
            'japanese': '日本語',
            'korean': '한국어',
            'spanish': 'Español',
            'french': 'Français',
            'german': 'Deutsch',
            'russian': 'Русский'
        }
        return display_names.get(language_code, language_code.title())
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """
        Get a list of all supported language codes.
        
        Returns:
            list: List of supported language codes
        """
        return list(cls.LANGUAGE_PATTERNS.keys())


def detect_query_language(query: str) -> str:
    """
    Convenience function to detect the language of a query string.
    
    Args:
        query: The query string to analyze
        
    Returns:
        str: Detected language code
    """
    language, confidence = LanguageDetector.detect_language(query)
    return language
