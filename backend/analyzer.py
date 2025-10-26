"""Analyzer module - Routes to simple_analyzer for fast analysis"""

from backend.models import ComprehensiveAnalysis, AnalysisSettings


def analyze_bmw_1pager(text: str, provider: str = "gemini", settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """Main entry point for document analysis."""
    if settings is None:
        settings = AnalysisSettings()
    from backend.simple_analyzer import analyze_document_fast
    return analyze_document_fast(text)
