import google.generativeai as genai
from openai import OpenAI
from backend.config import get_settings
from backend.models import (
    ComprehensiveAnalysis, Variable, Formula, TAMMetrics, SAMMetrics, 
    SOMMetrics, ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential, AnalysisSettings, 
    IndustryExample, YearlyProjection
)
import json


def get_analysis_prompt(text: str, settings: AnalysisSettings = None) -> str:
    """
    Generate the comprehensive analysis prompt for both LLM providers.
    
    THIS IS THE MOST CRITICAL FUNCTION - The system prompt determines analysis quality.
    
    Key improvements:
    1. Structured output format with strict JSON schema
    2. Industry-specific context injection
    3. Confidence scoring methodology
    4. Currency-aware calculations
    5. Depth-based detail requirements
    """
    
    # Default settings if none provided
    if settings is None:
        settings = AnalysisSettings()
    
    # Industry-specific context
    industry_context = ""
    if settings.industry_focus:
        industry_contexts = {
            "automotive": "Focus on automotive industry dynamics, supply chain complexity, capital intensity, and long development cycles. Consider EV transition, autonomous driving trends, and changing mobility patterns.",
            "tech": "Focus on software/SaaS metrics, user acquisition costs, churn rates, network effects, and scalability. Consider rapid iteration cycles and platform dynamics.",
            "healthcare": "Focus on regulatory requirements, reimbursement models, clinical validation timelines, and patient outcomes. Consider compliance costs and long sales cycles.",
            "retail": "Focus on customer acquisition costs, inventory turnover, omnichannel strategies, and margin pressure. Consider seasonal patterns and consumer behavior shifts.",
            "fintech": "Focus on transaction volumes, regulatory compliance, security costs, and customer lifetime value. Consider trust factors and switching costs."
        }
        industry_context = industry_contexts.get(settings.industry_focus, "")
    
    # Depth requirements
    depth_instructions = {
        "quick": "High-level estimates only. Keep insights under 150 characters. Focus on numbers.",
        "standard": "Balanced detail. Keep insights under 200 characters. Include key calculations.",
        "comprehensive": "Detailed analysis. Keep insights under 250 characters. Show methodology."
    }
    depth_instruction = depth_instructions.get(settings.analysis_depth, depth_instructions["standard"])
    
    currency_symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(settings.currency, "€")
    
    return f"""
You are Quant AI - an elite financial analyst and business strategist with deep expertise in market analysis, 
financial modeling, and strategic planning. You combine rigorous analytical methods with practical business acumen.

=== ANALYSIS CONFIGURATION ===
Analysis Depth: {settings.analysis_depth.upper()}
Currency: {settings.currency} ({currency_symbol})
Confidence Threshold: {settings.confidence_threshold}%
{f"Industry Focus: {settings.industry_focus.upper()}" if settings.industry_focus else ""}

{industry_context}

=== YOUR MISSION ===
Analyze the following business concept and generate an investor-ready financial and market analysis.
{depth_instruction}

=== INPUT DOCUMENT ===
{text}

=== ANALYSIS FRAMEWORK ===

CONFIDENCE SCORING METHODOLOGY:
- 80-100%: Based on hard data, industry reports, or clear comparable companies
- 60-79%: Based on reasonable assumptions with some market data support
- 40-59%: Educated estimates with limited data, but logical reasoning
- 20-39%: Rough estimates with high uncertainty
- 0-19%: Pure speculation, significant data gaps

Only include metrics with confidence >= {settings.confidence_threshold}% unless critical for completeness.

CALCULATION PRINCIPLES:
1. Work from first principles - show your math
2. Use industry benchmarks (cite sources when possible)
3. Consider market maturity, competition, and barriers to entry
4. Account for customer acquisition costs and churn
5. Factor in seasonality and economic cycles
6. Include realistic implementation timelines

CURRENCY FORMATTING:
- Express ALL monetary values in {settings.currency}
- Use actual numbers, not ranges (pick conservative midpoint)
- Round to 2 decimal places for precision

=== REQUIRED JSON OUTPUT ===
{{
  "tam": {{
    "description_of_public": <string: Clear description of the total addressable market>,
    "market_size": <float: Total Addressable Market in {settings.currency}>,
    "growth_rate": <float: CAGR %>,
    "time_horizon": <string: e.g., "2024-2030">,
    "numbers": {{
      "2024": <float: TAM value for 2024>,
      "2025": <float: TAM value for 2025>,
      "2026": <float: TAM value for 2026>,
      "2027": <float: TAM value for 2027>,
      "2028": <float: TAM value for 2028>,
      "2029": <float: TAM value for 2029>,
      "2030": <float: TAM value for 2030>
    }},
    "justification": <string: Detailed explanation of TAM calculation methodology and assumptions>,
    "insight": <string: Key insights about TAM>,
    "confidence": <int: 0-100>,
    "industry_example": {{
      "name": <string: Name of comparable company/industry>,
      "description": <string: How this example validates the TAM>,
      "link": <string: URL to source or null>,
      "metric_value": <string: Specific metric from example or null>
    }},
    "breakdown": {{
      "segment_1": <float: Value>,
      "segment_2": <float: Value>
    }}
  }},
  "sam": {{
    "description_of_public": <string: Clear description of serviceable available market>,
    "region": <string: Primary geographic market>,
    "target_segment": <string: Specific customer segment description>,
    "market_size": <float: Serviceable Available Market in {settings.currency}>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "justification": <string: Detailed SAM calculation and filtering logic>,
    "insight": <string: How SAM was narrowed from TAM>,
    "confidence": <int: 0-100>,
    "industry_example": {{
      "name": <string>,
      "description": <string>,
      "link": <string or null>,
      "metric_value": <string or null>
    }},
    "penetration_rate": <float: % of TAM that SAM represents>
  }},
  "som": {{
    "description_of_public": <string: Clear description of serviceable obtainable market>,
    "market_share": <float: Realistic market share % achievable>,
    "revenue_potential": <float: Expected annual revenue in {settings.currency}>,
    "capture_period": <string: Timeline to achieve this share>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "justification": <string: Detailed SOM calculation and market capture strategy>,
    "insight": <string: Market penetration strategy and competitive positioning>,
    "confidence": <int: 0-100>,
    "industry_example": {{
      "name": <string>,
      "description": <string>,
      "link": <string or null>,
      "metric_value": <string or null>
    }},
    "customer_acquisition_cost": <float: CAC in {settings.currency} or null>
  }},
  "roi": {{
    "revenue": <float: Total projected revenue>,
    "cost": <float: Total investment required>,
    "roi_percentage": <float: ROI % = (Revenue-Cost)/Cost * 100>,
    "numbers": {{
      "2024": <float: ROI for each year>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "payback_period_months": <int: Number of months to break even or null>,
    "insight": <string: Payback period and ROI trajectory>,
    "confidence": <int: 0-100>,
    "cost_breakdown": {{
      "development": <float or null>,
      "marketing": <float or null>,
      "operations": <float or null>
    }}
  }},
  "turnover": {{
    "year": <int: Target year for projection>,
    "total_revenue": <float: Annual revenue in {settings.currency}>,
    "yoy_growth": <float: Year-over-year growth %>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "revenue_streams": {{
      "primary_product": <float or null>,
      "services": <float or null>,
      "recurring": <float or null>
    }},
    "insight": <string: Revenue composition and growth drivers>,
    "confidence": <int: 0-100>
  }},
  "volume": {{
    "units_sold": <int: Annual units/transactions>,
    "region": <string: Geographic scope>,
    "period": <string: "Annual">,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "insight": <string: Volume trajectory and drivers>,
    "confidence": <int: 0-100>,
    "growth_drivers": [<string: Key factor 1>, <string: Key factor 2>]
  }},
  "unit_economics": {{
    "unit_revenue": <float: Average revenue per unit in {settings.currency}>,
    "unit_cost": <float: Fully loaded cost per unit>,
    "margin": <float: Contribution margin per unit>,
    "margin_percentage": <float: Margin as % or null>,
    "ltv_cac_ratio": <float: Lifetime Value / CAC or null>,
    "insight": <string: Unit economics health and scalability>,
    "confidence": <int: 0-100>,
    "cost_components": {{
      "variable_costs": <float or null>,
      "fixed_costs_per_unit": <float or null>
    }}
  }},
  "ebit": {{
    "revenue": <float: Total revenue>,
    "operating_expense": <float: OpEx including R&D, S&M, G&A>,
    "ebit_margin": <float: EBIT in {settings.currency}>,
    "ebit_percentage": <float: EBIT as % of revenue or null>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "insight": <string: Operating leverage and path to profitability>,
    "confidence": <int: 0-100>,
    "opex_breakdown": {{
      "rd": <float or null>,
      "sales_marketing": <float or null>,
      "general_admin": <float or null>
    }}
  }},
  "cogs": {{
    "material": <float: Direct material costs or null>,
    "labor": <float: Direct labor costs or null>,
    "overheads": <float: Manufacturing/delivery overhead or null>,
    "total_cogs": <float: Sum of all COGS>,
    "cogs_percentage": <float: COGS as % of revenue or null>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "insight": <string: Cost structure and optimization opportunities>,
    "confidence": <int: 0-100>
  }},
  "market_potential": {{
    "market_size": <float: Overall addressable opportunity>,
    "penetration": <float: Realistic penetration %>,
    "growth_rate": <float: Market CAGR %>,
    "numbers": {{
      "2024": <float>,
      "2025": <float>,
      "2026": <float>,
      "2027": <float>,
      "2028": <float>,
      "2029": <float>,
      "2030": <float>
    }},
    "market_drivers": [<string: Driver 1>, <string: Driver 2>],
    "barriers_to_entry": [<string: Barrier 1>, <string: Barrier 2>],
    "insight": <string: Market attractiveness assessment>,
    "confidence": <int: 0-100>
  }},
  "identified_variables": [
    {{
      "name": <string: e.g., "Customer Acquisition Cost">,
      "value": <string: e.g., "{currency_symbol}250 per customer">,
      "description": <string: Why this drives the business model>
    }}
  ],
  "formulas": [
    {{
      "name": <string: e.g., "LTV/CAC Ratio">,
      "formula": <string: e.g., "({currency_symbol}1,200 × 3 years) / {currency_symbol}250">,
      "calculation": <string: e.g., "14.4x - Excellent unit economics">
    }}
  ],
  "business_assumptions": [
    <string: List 5-10 critical assumptions underpinning this analysis>
  ],
  "improvement_recommendations": [
    <string: List 5-8 specific, actionable recommendations to strengthen the business case>
  ],
  "value_market_potential_text": <string: Professional 3-paragraph executive summary for formal documentation>,
  "executive_summary": <string: 1-paragraph elevator pitch highlighting the opportunity>,
  "sources": [<string: URL 1>, <string: URL 2>],
  "key_risks": [<string: Risk 1>, <string: Risk 2>],
  "competitive_advantages": [<string: Advantage 1>, <string: Advantage 2>]
}}

=== CRITICAL OUTPUT REQUIREMENTS ===
1. OUTPUT ONLY VALID JSON - no markdown, no text outside JSON
2. Keep ALL "insight" fields concise (under 200 chars each)
3. Use proper JSON escaping - no unescaped quotes or line breaks in strings
4. ALL monetary values in {settings.currency}
5. Round numbers to 2 decimal places
6. Be specific and quantitative

Begin analysis now:
"""


def parse_analysis_response(response_text: str) -> ComprehensiveAnalysis:
    """Parse and validate the LLM response into ComprehensiveAnalysis model with robust error handling"""
    try:
        # Clean up markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to fix common JSON issues
        # Replace smart quotes with regular quotes
        response_text = response_text.replace('"', '"').replace('"', '"')
        response_text = response_text.replace(''', "'").replace(''', "'")
        
        # Check if response was truncated (doesn't end with })
        if not response_text.rstrip().endswith('}'):
            print("WARNING: Response appears truncated, attempting to repair...")
            # Find the last complete field and close the JSON
            last_complete = response_text.rfind('",')
            if last_complete > 0:
                response_text = response_text[:last_complete + 1] + '\n    }\n  }\n}'
        
        # Attempt to parse JSON
        analysis_data = json.loads(response_text)
        
        # Validate all required fields exist
        required_sections = ['tam', 'sam', 'som', 'roi', 'turnover', 'volume', 
                           'unit_economics', 'ebit', 'cogs', 'market_potential']
        
        for section in required_sections:
            if section not in analysis_data:
                raise ValueError(f"Missing required section: {section}")
        
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
    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed at line {e.lineno}, column {e.colno}: {e.msg}"
        print(f"JSON Error: {error_msg}")
        print(f"Response preview (first 1000 chars): {response_text[:1000]}")
        print(f"Response ending (last 500 chars): {response_text[-500:]}")
    except Exception as e:
        error_msg = str(e)
        print(f"Analysis Error: {error_msg}")
    
    # Return error structure if parsing fails
    return ComprehensiveAnalysis(
        tam=TAMMetrics(description_of_public="Error", justification="Error", insight="Unable to complete TAM analysis due to response parsing error. Please try again or contact support.", confidence=0),
        sam=SAMMetrics(description_of_public="Error", justification="Error", insight="Unable to complete SAM analysis due to response parsing error. Please try again or contact support.", confidence=0),
        som=SOMMetrics(description_of_public="Error", justification="Error", insight="Unable to complete SOM analysis due to response parsing error. Please try again or contact support.", confidence=0),
        roi=ROIMetrics(insight="Unable to complete ROI analysis due to response parsing error. Please try again or contact support.", confidence=0),
        turnover=TurnoverMetrics(insight="Unable to complete turnover analysis due to response parsing error. Please try again or contact support.", confidence=0),
        volume=VolumeMetrics(insight="Unable to complete volume analysis due to response parsing error. Please try again or contact support.", confidence=0),
        unit_economics=UnitEconomics(insight="Unable to complete unit economics analysis due to response parsing error. Please try again or contact support.", confidence=0),
        ebit=EBITMetrics(insight="Unable to complete EBIT analysis due to response parsing error. Please try again or contact support.", confidence=0),
        cogs=COGSMetrics(insight="Unable to complete COGS analysis due to response parsing error. Please try again or contact support.", confidence=0),
        market_potential=MarketPotential(insight="Unable to complete market potential analysis due to response parsing error. Please try again or contact support.", confidence=0),
        identified_variables=[],
        formulas=[],
        business_assumptions=["Analysis failed due to technical error. Please retry."],
        improvement_recommendations=["Try uploading the document again", "Use a different AI provider", "Ensure document contains clear business information"],
        value_market_potential_text="The analysis could not be completed due to a technical error in processing the AI response. This may be due to the complexity of the document or temporary issues with the AI service. Please try again, or consider using the alternative AI provider.",
        executive_summary="Analysis temporarily unavailable. Please retry or use the alternative AI provider."
    )


def analyze_with_gemini(text: str, settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """Analyze document using Google Gemini 2.5 Flash (latest)"""
    config = get_settings()
    genai.configure(api_key=config.gemini_api_key)
    
    # Use temperature from settings
    if settings is None:
        settings = AnalysisSettings()
    
    generation_config = {
        "temperature": settings.temperature,
        "top_p": 0.95,
        "top_k": 40,
    }
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash',  # Latest Gemini 2.5 Flash
        generation_config=generation_config
    )
    
    prompt = get_analysis_prompt(text, settings)
    
    # Add explicit JSON-only instruction at the end
    prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Keep all insight fields under 200 characters. Use concise language. Start with { and end with }."
    
    try:
        response = model.generate_content(prompt)
        return parse_analysis_response(response.text)
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        
        # Provide helpful error message
        if "timeout" in error_msg.lower() or "504" in error_msg:
            error_msg = "Request timed out. Try using 'Quick' analysis mode or the OpenAI provider."
        
        # Return error structure
        return ComprehensiveAnalysis(
            tam=TAMMetrics(description_of_public="Error", justification="Error", insight=f"Analysis failed. {error_msg}", confidence=0),
            sam=SAMMetrics(description_of_public="Error", justification="Error", insight=f"Analysis failed. {error_msg}", confidence=0),
            som=SOMMetrics(description_of_public="Error", justification="Error", insight=f"Analysis failed. {error_msg}", confidence=0),
            roi=ROIMetrics(insight=f"Analysis failed. {error_msg}", confidence=0),
            turnover=TurnoverMetrics(insight=f"Analysis failed. {error_msg}", confidence=0),
            volume=VolumeMetrics(insight=f"Analysis failed. {error_msg}", confidence=0),
            unit_economics=UnitEconomics(insight=f"Analysis failed. {error_msg}", confidence=0),
            ebit=EBITMetrics(insight=f"Analysis failed. {error_msg}", confidence=0),
            cogs=COGSMetrics(insight=f"Analysis failed. {error_msg}", confidence=0),
            market_potential=MarketPotential(insight=f"Analysis failed. {error_msg}", confidence=0),
            identified_variables=[],
            formulas=[],
            business_assumptions=["Analysis failed due to API timeout or error"],
            improvement_recommendations=["Use 'Quick' analysis depth in settings", "Try OpenAI provider", "Simplify your input document"],
            value_market_potential_text=f"Analysis could not be completed: {error_msg}",
            executive_summary=f"Analysis failed: {error_msg}"
        )


def analyze_with_openai(text: str, settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """Analyze document using OpenAI o1 (best reasoning model for complex analysis)"""
    config = get_settings()
    client = OpenAI(api_key=config.openai_api_key)
    
    if settings is None:
        settings = AnalysisSettings()
    
    prompt = get_analysis_prompt(text, settings)
    
    # o1 models don't support system messages or temperature
    # They use reasoning tokens for complex analysis
    response = client.chat.completions.create(
        model="o1",  # Best OpenAI model for complex reasoning
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return parse_analysis_response(response.choices[0].message.content)


def analyze_bmw_1pager(text: str, provider: str = "gemini", settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """
    Main analysis function that routes to the appropriate LLM provider
    
    Args:
        text: The extracted document text
        provider: Either 'gemini' or 'openai'
        settings: Optional analysis settings for customization
    
    Returns:
        ComprehensiveAnalysis model with all financial metrics
    """
    if provider.lower() == "openai":
        return analyze_with_openai(text, settings)
    else:
        return analyze_with_gemini(text, settings)
