import google.generativeai as genai
from backend.config import get_settings
from backend.models import AnalysisResult, Variable, Formula
import json


def analyze_bmw_1pager(text: str) -> AnalysisResult:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
You are a BMW business analyst expert. Generate a complete "Value | Market Potential" section for a BMW 1-Pager innovation document.

Process:
1. Identify the business model and key variables for market potential
2. Create formulas using these variables to calculate market size and revenue
3. Make quantitative assumptions based on industry data and business logic
4. Generate a complete "Value | Market Potential" section

Input BMW 1-Pager Text:
{text}

Output as JSON:
{{
  "identified_variables": [
    {{"name": "Variable name", "value": "Estimated value", "description": "Why this variable matters"}}
  ],
  "formulas": [
    {{"name": "Formula name", "formula": "Mathematical formula", "calculation": "Calculated result"}}
  ],
  "market_size": "Total addressable market estimate with justification",
  "revenue_potential": "Expected revenue with timeframe",
  "addressable_market": "TAM - Total Addressable Market",
  "serviceable_market": "SAM - Serviceable Available Market",
  "target_market_share": "Expected market share percentage",
  "unit_economics": "Revenue per unit, cost per unit, margin",
  "roi_estimate": "Return on investment projection",
  "business_assumptions": ["Assumption 1", "Assumption 2"],
  "value_market_potential_text": "Complete 2-3 paragraph text for the Value | Market Potential section, written professionally for BMW innovation documentation. Include all key metrics, assumptions, and business logic."
}}

Be specific, data-driven, and cite realistic assumptions. Focus on automotive/mobility industry context for BMW.
"""
    
    response = model.generate_content(prompt)
    
    try:
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        analysis_data = json.loads(response_text.strip())
        
        variables = [Variable(**v) for v in analysis_data.get("identified_variables", [])]
        formulas = [Formula(**f) for f in analysis_data.get("formulas", [])]
        
        return AnalysisResult(
            identified_variables=variables,
            formulas=formulas,
            market_size=analysis_data.get("market_size"),
            revenue_potential=analysis_data.get("revenue_potential"),
            addressable_market=analysis_data.get("addressable_market"),
            serviceable_market=analysis_data.get("serviceable_market"),
            target_market_share=analysis_data.get("target_market_share"),
            unit_economics=analysis_data.get("unit_economics"),
            roi_estimate=analysis_data.get("roi_estimate"),
            business_assumptions=analysis_data.get("business_assumptions", []),
            value_market_potential_text=analysis_data.get("value_market_potential_text", "")
        )
        
    except Exception as e:
        return AnalysisResult(
            identified_variables=[],
            formulas=[],
            business_assumptions=[],
            value_market_potential_text=f"Analysis completed. Error: {str(e)}"
        )
