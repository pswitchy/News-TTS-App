# models/__init__.py
"""Models package for news summarization and TTS application."""

from .news_extractor import NewsExtractor
from .sentiment_analyzer import SentimentAnalyzer
from .text_to_speech import TextToSpeech
from .comparative_analyzer import ComparativeAnalyzer

__all__ = [
    'NewsExtractor',
    'SentimentAnalyzer',
    'TextToSpeech',
    'ComparativeAnalyzer'
]