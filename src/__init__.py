"""
Data Analyst Agent - Core Package
AI-powered data analysis using Gemini AI
"""

__version__ = "1.0.0"
__author__ = "Renee Noronha"
__email__ = "reneenoronha2006@gmail.com"

from .data_analyzer import DataAnalyzer
from .gemini_client import GeminiClient
from .visualization import VisualizationEngine
from .data_processor import DataProcessor

__all__ = [
    'DataAnalyzer',
    'GeminiClient', 
    'VisualizationEngine',
    'DataProcessor'
]
