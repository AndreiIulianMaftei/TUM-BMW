import google.generativeai as genai
from openai import OpenAI
from backend.config import get_settings
from backend.models import (
    ComprehensiveAnalysis, Variable, Formula, TAMMetrics, SAMMetrics, 
    SOMMetrics, ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential, AnalysisSettings
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
        "quick": "Provide high-level estimates with key assumptions. Focus on headline metrics and primary insights.",
        "standard": "Balance detail with efficiency. Include main calculations and critical assumptions.",
        "comprehensive": "Provide detailed analysis with multiple scenarios, sensitivity analysis, and thorough justification for all assumptions."
    }
    depth_instruction = depth_instructions.get(settings.analysis_depth, depth_instructions["comprehensive"])
    
    currency_symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(settings.currency, "€")
    
    return f"""
You are ProspectAI - an elite financial analyst and business strategist with deep expertise in market analysis, 
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
    "market_size": <float: Total Addressable Market in {settings.currency}>,
    "growth_rate": <float: CAGR %>,
    "time_horizon": <string: e.g., "2025-2030">,
    "insight": <string: Detailed TAM calculation with data sources and methodology>,
    "confidence": <int: 0-100>
  }},
  "sam": {{
    "region": <string: Primary geographic market>,
    "target_segment": <string: Specific customer segment description>,
    "market_size": <float: Serviceable Available Market in {settings.currency}>,
    "insight": <string: How SAM was narrowed from TAM - geographic/segment filters>,
    "confidence": <int: 0-100>
  }},
  "som": {{
    "market_share": <float: Realistic market share % achievable in 3-5 years>,
    "revenue_potential": <float: Expected annual revenue in {settings.currency}>,
    "capture_period": <string: Timeline to achieve this share>,
    "insight": <string: Market penetration strategy, competitive positioning, growth drivers>,
    "confidence": <int: 0-100>
  }},
  "roi": {{
    "revenue": <float: Total projected revenue>,
    "cost": <float: Total investment required>,
    "roi_percentage": <float: ROI % = (Revenue-Cost)/Cost * 100>,
    "insight": <string: Payback period, key cost assumptions, revenue ramp timeline>,
    "confidence": <int: 0-100>
  }},
  "turnover": {{
    "year": <int: Target year for projection>,
    "total_revenue": <float: Annual revenue in {settings.currency}>,
    "yoy_growth": <float: Year-over-year growth %>,
    "insight": <string: Revenue composition, growth drivers, scaling assumptions>,
    "confidence": <int: 0-100>
  }},
  "volume": {{
    "units_sold": <int: Annual units/transactions>,
    "region": <string: Geographic scope>,
    "period": <string: "Annual" or specific period>,
    "insight": <string: Volume calculation: market size × penetration / avg transaction value>,
    "confidence": <int: 0-100>
  }},
  "unit_economics": {{
    "unit_revenue": <float: Average revenue per unit in {settings.currency}>,
    "unit_cost": <float: Fully loaded cost per unit>,
    "margin": <float: Contribution margin per unit>,
    "insight": <string: Margin %, path to profitability, economies of scale>,
    "confidence": <int: 0-100>
  }},
  "ebit": {{
    "revenue": <float: Total revenue>,
    "operating_expense": <float: OpEx including R&D, S&M, G&A>,
    "ebit_margin": <float: EBIT in {settings.currency}>,
    "insight": <string: Operating leverage, fixed vs variable costs, path to positive EBIT>,
    "confidence": <int: 0-100>
  }},
  "cogs": {{
    "material": <float: Direct material costs>,
    "labor": <float: Direct labor costs>,
    "overheads": <float: Manufacturing/delivery overhead>,
    "total_cogs": <float: Sum of all COGS>,
    "insight": <string: Cost structure, supplier dependencies, opportunities for cost reduction>,
    "confidence": <int: 0-100>
  }},
  "market_potential": {{
    "market_size": <float: Overall addressable opportunity>,
    "penetration": <float: Realistic penetration %>,
    "growth_rate": <float: Market CAGR %>,
    "insight": <string: Market attractiveness: growth, competition, barriers, timing>,
    "confidence": <int: 0-100>
  }},
  "identified_variables": [
    {{
      "name": <string: e.g., "Customer Acquisition Cost">,
      "value": <string: e.g., "€250 per customer">,
      "description": <string: Why this drives the business model>
    }}
  ],
  "formulas": [
    {{
      "name": <string: e.g., "LTV/CAC Ratio">,
      "formula": <string: e.g., "(€1,200 × 3 years) / €250">,
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
  "executive_summary": <string: 1-paragraph elevator pitch highlighting the opportunity>
}}

=== CRITICAL OUTPUT REQUIREMENTS ===
1. OUTPUT ONLY VALID JSON - no markdown, no explanations outside JSON
2. ALL monetary values in {settings.currency}
3. Insights must be specific, quantitative, and actionable
4. Confidence scores must reflect data quality honestly
5. Recommendations must be prioritized and implementable
6. Use conservative assumptions (better to under-promise)

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
        print(f"Response preview: {response_text[:500]}")
    except Exception as e:
        error_msg = str(e)
        print(f"Analysis Error: {error_msg}")
    
    # Return error structure if parsing fails
    return ComprehensiveAnalysis(
        tam=TAMMetrics(insight="Unable to complete TAM analysis due to response parsing error. Please try again or contact support.", confidence=0),
        sam=SAMMetrics(insight="Unable to complete SAM analysis due to response parsing error. Please try again or contact support.", confidence=0),
        som=SOMMetrics(insight="Unable to complete SOM analysis due to response parsing error. Please try again or contact support.", confidence=0),
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
        "max_output_tokens": 8192,
        "response_mime_type": "application/json",  # Enforce JSON output
    }
    
    model = genai.GenerativeModel(
        'gemini-2.5-flash',  # Latest Gemini 2.5 Flash model
        generation_config=generation_config
    )
    
    prompt = get_analysis_prompt(text, settings)
    
    try:
        response = model.generate_content(prompt)
        return parse_analysis_response(response.text)
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        # Return error structure
        return ComprehensiveAnalysis(
            tam=TAMMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            sam=SAMMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            som=SOMMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            roi=ROIMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            turnover=TurnoverMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            volume=VolumeMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            unit_economics=UnitEconomics(insight=f"Gemini API error: {str(e)}", confidence=0),
            ebit=EBITMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            cogs=COGSMetrics(insight=f"Gemini API error: {str(e)}", confidence=0),
            market_potential=MarketPotential(insight=f"Gemini API error: {str(e)}", confidence=0),
            identified_variables=[],
            formulas=[],
            business_assumptions=["API Error occurred"],
            improvement_recommendations=["Try again", "Use OpenAI provider"],
            value_market_potential_text=f"Error: {str(e)}",
            executive_summary=f"Analysis failed: {str(e)}"
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
