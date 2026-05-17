"""
fortune-core: AI-powered divination engine
Support for I Ching, Tarot, Feng Shui, and more.
"""

from .hexagrams import get_hexagram, get_trigram
from .tarot_engine import TarotEngine
from .divination_entry import DivineEntryEngine, DivineEntry, DivineRecommendation
from .report_generator import ReportGenerator, ReadingReport

__all__ = [
    # I Ching
    "get_hexagram",
    "get_trigram",
    # Tarot
    "TarotEngine",
    # Divination Entry
    "DivineEntryEngine",
    "DivineEntry",
    "DivineRecommendation",
    # Report Generation
    "ReportGenerator",
    "ReadingReport",
]

__version__ = "0.2.0"
__author__ = "fortune-core developers"