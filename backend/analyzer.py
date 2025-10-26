"""Analyzer module - Routes to simple_analyzer for fast analysis"""

from backend.models import ComprehensiveAnalysis, AnalysisSettings
from typing import Tuple, Dict, Any


def analyze_bmw_1pager(text: str, provider: str = "gemini", settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """Main entry point for document analysis."""
    if settings is None:
        settings = AnalysisSettings()
    from backend.simple_analyzer import analyze_document_fast
    return analyze_document_fast(text)


def analyze_bmw_1pager_with_extraction(text: str, provider: str = "gemini", settings: AnalysisSettings = None) -> Tuple[ComprehensiveAnalysis, Dict[str, Any]]:
    """Analyze document and return both analysis and extraction data for auto-scaling."""
    if settings is None:
        settings = AnalysisSettings()
    from backend.simple_analyzer import analyze_document_fast_with_extraction
    return analyze_document_fast_with_extraction(text)
