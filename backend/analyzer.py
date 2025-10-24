import google.generativeai as genai
from backend.config import get_settings
from backend.models import (
    ComprehensiveAnalysis, Variable, Formula, TAMMetrics, SAMMetrics, 
    SOMMetrics, ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential
)
import json


def analyze_bmw_1pager(text: str) -> ComprehensiveAnalysis:
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
You are an expert financial analyst and business strategist specializing in automotive innovation and market potential assessment. 
Analyze the following BMW 1-Pager document and generate a comprehensive market and financial analysis.

CRITICAL INSTRUCTIONS:
1. Extract ALL relevant business information from the document
2. Calculate realistic financial metrics based on the business model described
3. Use automotive industry benchmarks and comparable market data
4. Provide specific numbers with clear reasoning
5. Rate your confidence (0-100%) for each metric based on data availability
6. Include actionable recommendations for improvement

INPUT DOCUMENT:
{text}

REQUIRED OUTPUT (JSON format):
{{
  "tam": {{
    "market_size": <float: Total Addressable Market in EUR/USD>,
    "growth_rate": <float: Annual growth rate %>,
    "time_horizon": <string: "2025-2030" or relevant period>,
    "insight": <string: Clear explanation of TAM calculation and sources>,
    "confidence": <int: 0-100>
  }},
  "sam": {{
    "region": <string: Geographic focus>,
    "target_segment": <string: Specific customer segment>,
    "market_size": <float: Serviceable Available Market in EUR/USD>,
    "insight": <string: How SAM was derived from TAM>,
    "confidence": <int: 0-100>
  }},
  "som": {{
    "market_share": <float: Realistic market share % in 3-5 years>,
    "revenue_potential": <float: Expected revenue in EUR/USD>,
    "capture_period": <string: "Year 1-3" timeframe>,
    "insight": <string: Market penetration strategy and assumptions>,
    "confidence": <int: 0-100>
  }},
  "roi": {{
    "revenue": <float: Projected revenue>,
    "cost": <float: Total investment/cost>,
    "roi_percentage": <float: ROI %>,
    "insight": <string: ROI calculation breakdown and timeline>,
    "confidence": <int: 0-100>
  }},
  "turnover": {{
    "year": <int: Projection year>,
    "total_revenue": <float: Annual revenue>,
    "yoy_growth": <float: Year-over-year growth %>,
    "insight": <string: Revenue projection rationale>,
    "confidence": <int: 0-100>
  }},
  "volume": {{
    "units_sold": <int: Expected transaction/unit volume>,
    "region": <string: Geographic scope>,
    "period": <string: "Annual" or specific period>,
    "insight": <string: Volume calculation based on market size and penetration>,
    "confidence": <int: 0-100>
  }},
  "unit_economics": {{
    "unit_revenue": <float: Average revenue per unit/transaction>,
    "unit_cost": <float: Cost per unit>,
    "margin": <float: Profit margin per unit>,
    "insight": <string: Unit economics breakdown and sustainability>,
    "confidence": <int: 0-100>
  }},
  "ebit": {{
    "revenue": <float: Total revenue>,
    "operating_expense": <float: Operating expenses>,
    "ebit_margin": <float: EBIT (revenue - opex)>,
    "insight": <string: Operational profitability analysis>,
    "confidence": <int: 0-100>
  }},
  "cogs": {{
    "material": <float: Material costs>,
    "labor": <float: Labor costs>,
    "overheads": <float: Overhead costs>,
    "total_cogs": <float: Sum of all COGS>,
    "insight": <string: Cost structure breakdown>,
    "confidence": <int: 0-100>
  }},
  "market_potential": {{
    "market_size": <float: Overall market opportunity>,
    "penetration": <float: Achievable penetration %>,
    "growth_rate": <float: Market growth %>,
    "insight": <string: Overall market attractiveness and opportunity>,
    "confidence": <int: 0-100>
  }},
  "identified_variables": [
    {{
      "name": <string: Variable name>,
      "value": <string: Estimated value with units>,
      "description": <string: Why this variable is critical>
    }}
  ],
  "formulas": [
    {{
      "name": <string: Formula name>,
      "formula": <string: Mathematical formula>,
      "calculation": <string: Calculated result with explanation>
    }}
  ],
  "business_assumptions": [
    <string: List all key assumptions made in the analysis>
  ],
  "improvement_recommendations": [
    <string: Actionable recommendations to increase market potential>
  ],
  "value_market_potential_text": <string: Professional 2-3 paragraph summary for BMW documentation>,
  "executive_summary": <string: 1 paragraph high-level overview for executives>
}}

CALCULATION GUIDELINES:
- Use automotive industry averages (e.g., motorcycle accessories market ~$50B globally)
- Consider BMW's premium positioning (higher margins, smaller volume)
- Account for geographic variations in market size
- Factor in digital transformation trends and e-commerce growth
- Include realistic cost structures for automotive retail
- Use conservative estimates where data is uncertain
- Reference industry reports, market research, and comparable companies
- For BMW motorcycle accessories: consider install base, accessory attach rate, average order value

CONTEXT-SPECIFIC ANALYSIS:
- Analyze the specific business model described
- Identify cost drivers and revenue drivers mentioned
- Extract customer segments and their needs
- Assess competitive advantages and barriers to entry
- Consider implementation complexity and timeline
- Evaluate scalability and long-term sustainability

OUTPUT ONLY VALID JSON. Be specific, quantitative, and investor-ready.
"""
    
    response = model.generate_content(prompt)
    
    try:
        response_text = response.text.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        analysis_data = json.loads(response_text.strip())
        
        return ComprehensiveAnalysis(
            tam=TAMMetrics(**analysis_data["tam"]),
            sam=SAMMetrics(**analysis_data["sam"]),
            som=SOMMetrics(**analysis_data["som"]),
            roi=ROIMetrics(**analysis_data["roi"]),
            turnover=TurnoverMetrics(**analysis_data["turnover"]),
            volume=VolumeMetrics(**analysis_data["volume"]),
            unit_economics=UnitEconomics(**analysis_data["unit_economics"]),
            ebit=EBITMetrics(**analysis_data["ebit"]),
            cogs=COGSMetrics(**analysis_data["cogs"]),
            market_potential=MarketPotential(**analysis_data["market_potential"]),
            identified_variables=[Variable(**v) for v in analysis_data.get("identified_variables", [])],
            formulas=[Formula(**f) for f in analysis_data.get("formulas", [])],
            business_assumptions=analysis_data.get("business_assumptions", []),
            improvement_recommendations=analysis_data.get("improvement_recommendations", []),
            value_market_potential_text=analysis_data.get("value_market_potential_text", ""),
            executive_summary=analysis_data.get("executive_summary", "")
        )
        
    except Exception as e:
        return ComprehensiveAnalysis(
            tam=TAMMetrics(insight=f"Error in TAM calculation: {str(e)}", confidence=0),
            sam=SAMMetrics(insight=f"Error in SAM calculation: {str(e)}", confidence=0),
            som=SOMMetrics(insight=f"Error in SOM calculation: {str(e)}", confidence=0),
            roi=ROIMetrics(insight=f"Error in ROI calculation: {str(e)}", confidence=0),
            turnover=TurnoverMetrics(insight=f"Error in turnover calculation: {str(e)}", confidence=0),
            volume=VolumeMetrics(insight=f"Error in volume calculation: {str(e)}", confidence=0),
            unit_economics=UnitEconomics(insight=f"Error in unit economics calculation: {str(e)}", confidence=0),
            ebit=EBITMetrics(insight=f"Error in EBIT calculation: {str(e)}", confidence=0),
            cogs=COGSMetrics(insight=f"Error in COGS calculation: {str(e)}", confidence=0),
            market_potential=MarketPotential(insight=f"Error in market potential calculation: {str(e)}", confidence=0),
            identified_variables=[],
            formulas=[],
            business_assumptions=[],
            improvement_recommendations=[],
            value_market_potential_text=f"Analysis encountered an error: {str(e)}",
            executive_summary=f"Analysis could not be completed: {str(e)}"
        )
