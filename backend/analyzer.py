import google.generativeai as genai
from openai import OpenAI
from backend.config import get_settings
from backend.models import (
    ComprehensiveAnalysis, Variable, Formula, TAMMetrics, SAMMetrics, 
    SOMMetrics, ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential, AnalysisSettings, 
    IndustryExample, YearlyProjection, DevelopmentCost, CustomerAcquisitionCost,
    DistributionOperationsCost, AfterSalesCost, COGSItem, YearlyCostBreakdown,
    SevenYearSummary
)
import json


def get_analysis_prompt(text: str, settings: AnalysisSettings = None) -> str:
    """
    Generate the comprehensive analysis prompt for both LLM providers.
    
    THIS IS THE MOST CRITICAL FUNCTION - The system prompt determines analysis quality.
    
    Key improvements:
    1. Structured output format with strict JSON schema
    2. Industry-specific context injection
    3. Currency-aware calculations
    4. Comprehensive cost breakdown structure
    """
    
    # Default settings if none provided
    if settings is None:
        settings = AnalysisSettings()
    
    return f"""You are Quant AI - an elite financial analyst specializing in market analysis and financial modeling.

CONFIGURATION: Currency={settings.currency}{f", Industry={settings.industry_focus.upper()}" if settings.industry_focus else ""}

ANALYZE THIS BUSINESS CONCEPT:
{text}

OUTPUT REQUIREMENTS - Return ONLY valid JSON with this exact structure:

{{
  "tam": {{"description_of_public": "TAM description", "market_size": 0, "growth_rate": 0, "time_horizon": "2024-2030", "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "justification": "Calculation method", "insight": "Key insight", "confidence": 75, "industry_example": {{"name": "Company", "description": "Example", "link": null, "metric_value": null}}, "breakdown": {{}}}},
  "sam": {{"description_of_public": "SAM description", "region": "Geographic market", "target_segment": "Customer segment", "market_size": 0, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "justification": "Calculation", "insight": "Insight", "confidence": 75, "industry_example": {{"name": "Co", "description": "Ex", "link": null, "metric_value": null}}, "penetration_rate": 0}},
  "som": {{"description_of_public": "SOM description", "market_share": 0, "revenue_potential": 0, "capture_period": "Timeline", "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "justification": "Calculation", "insight": "Strategy", "confidence": 70, "industry_example": {{"name": "Co", "description": "Ex", "link": null, "metric_value": null}}, "customer_acquisition_cost": null}},
  "roi": {{"revenue": 0, "cost": 0, "roi_percentage": 0, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "payback_period_months": null, "insight": "ROI analysis", "confidence": 70, "cost_breakdown": {{"development": null, "marketing": null, "operations": null}}}},
  "turnover": {{"year": 2024, "total_revenue": 0, "yoy_growth": 0, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "revenue_streams": {{"primary_product": null, "services": null, "recurring": null}}, "insight": "Revenue drivers", "confidence": 70}},
  "volume": {{"units_sold": 0, "region": "Scope", "period": "Annual", "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "insight": "Volume trajectory", "confidence": 70, "growth_drivers": ["Driver1", "Driver2"]}},
  "unit_economics": {{"unit_revenue": 0, "unit_cost": 0, "margin": 0, "margin_percentage": null, "ltv_cac_ratio": null, "insight": "Economics health", "confidence": 70, "cost_components": {{"variable_costs": null, "fixed_costs_per_unit": null}}}},
  "ebit": {{"revenue": 0, "operating_expense": 0, "ebit_margin": 0, "ebit_percentage": null, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "insight": "Operating leverage", "confidence": 70, "opex_breakdown": {{"rd": null, "sales_marketing": null, "general_admin": null}}}},
  "cogs": {{"material": null, "labor": null, "overheads": null, "total_cogs": 0, "cogs_percentage": null, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "insight": "Cost structure", "confidence": 70}},
  "market_potential": {{"market_size": 0, "penetration": 0, "growth_rate": 0, "numbers": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}}, "market_drivers": ["D1", "D2"], "barriers_to_entry": ["B1", "B2"], "insight": "Market attractiveness", "confidence": 70}},
  "development_costs": [{{"category": "IT Development", "estimated_amount": 0, "currency": "{settings.currency}", "reasoning": "Why needed", "market_comparison": {{"similar_case": "Company Example", "comparison_details": "Validation", "cost_figures": [{{"company": "Co", "project": "Proj", "amount": 0, "currency": "{settings.currency}", "year": 2023}}], "source": "Source", "reference_links": ["URL"]}}}}],
  "total_development_cost": 0,
  "customer_acquisition_costs": [{{"category": "Marketing", "estimated_amount_per_customer": null, "estimated_annual_budget": 0, "currency": "{settings.currency}", "reasoning": "Why", "market_comparison": {{"similar_case": "Ex", "comparison_details": "Val", "cost_figures": [{{"company": "Co", "project": "P", "amount": 0, "currency": "{settings.currency}", "year": 2023}}], "source": "Src", "reference_links": ["URL"]}}}}],
  "total_customer_acquisition_cost": 0,
  "distribution_and_operations_costs": [{{"category": "Logistics", "estimated_amount": 0, "currency": "{settings.currency}", "reasoning": "Why", "market_comparison": {{"similar_case": "Ex", "comparison_details": "Val", "cost_figures": [{{"company": "Co", "project": "P", "amount": 0, "currency": "{settings.currency}", "year": 2023}}], "source": "Src", "reference_links": ["URL"]}}}}],
  "total_distribution_operations_cost": 0,
  "after_sales_costs": [{{"category": "Support", "estimated_amount": 0, "currency": "{settings.currency}", "reasoning": "Why", "market_comparison": {{"similar_case": "Ex", "comparison_details": "Val", "cost_figures": [{{"company": "Co", "project": "P", "amount": 0, "currency": "{settings.currency}", "year": 2023}}], "source": "Src", "reference_links": ["URL"]}}}}],
  "total_after_sales_cost": 0,
  "cost_of_goods_sold": [{{"product_category": "Product", "price_per_item": 0, "cogs_per_item": 0, "gross_margin_percentage": 0, "currency": "{settings.currency}", "reasoning": "COGS breakdown", "market_comparison": {{"similar_case": "Ex", "comparison_details": "Margin comp", "cost_figures": [{{"company": "Co", "project": "P", "amount": 0, "currency": "{settings.currency}", "year": 2023}}], "source": "Src", "reference_links": ["URL"]}}}}],
  "average_cogs_per_bundle": 0,
  "volume_projections": {{"2024": 0, "2025": 0, "2026": 0, "2027": 0, "2028": 0, "2029": 0, "2030": 0}},
  "yearly_cost_breakdown": {{"2024": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2025": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2026": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2027": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2028": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2029": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}, "2030": {{"projected_volume": 0, "one_time_development": 0, "customer_acquisition": 0, "distribution_operations": 0, "after_sales": 0, "total_cogs": 0, "cogs_per_unit": 0, "total_cost": 0, "currency": "{settings.currency}"}}}},
  "seven_year_summary": {{"total_cost_2024_2030": 0, "total_volume_2024_2030": 0, "average_cost_per_unit": 0, "currency": "{settings.currency}"}},
  "total_estimated_cost_summary": {{"one_time_development": 0, "annual_customer_acquisition": 0, "annual_distribution_operations": 0, "annual_after_sales": 0, "average_cogs_per_unit": 0}},
  "confidence_level": "Medium",
  "additional_notes": "Analysis notes and assumptions",
  "identified_variables": [{{"name": "Var", "value": "Val", "description": "Why matters"}}],
  "formulas": [{{"name": "Formula", "formula": "Math", "calculation": "Result"}}],
  "business_assumptions": ["Assumption 1", "Assumption 2"],
  "improvement_recommendations": ["Rec 1", "Rec 2"],
  "value_market_potential_text": "3-paragraph executive summary",
  "executive_summary": "1-paragraph pitch",
  "sources": ["URL1"],
  "key_risks": ["Risk 1"],
  "competitive_advantages": ["Advantage 1"]
}}

CRITICAL: Return ONLY this JSON. Replace 0 with real estimates. Fill ALL fields. Use proper escaping. Currency={settings.currency}. Provide detailed market comparisons with real company examples and sources. Keep insights concise but complete."""


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
        
        # Parse optional new cost fields
        development_costs = None
        if 'development_costs' in analysis_data and analysis_data['development_costs']:
            development_costs = [DevelopmentCost(**item) for item in analysis_data['development_costs']]
        
        customer_acquisition_costs = None
        if 'customer_acquisition_costs' in analysis_data and analysis_data['customer_acquisition_costs']:
            customer_acquisition_costs = [CustomerAcquisitionCost(**item) for item in analysis_data['customer_acquisition_costs']]
        
        distribution_costs = None
        if 'distribution_and_operations_costs' in analysis_data and analysis_data['distribution_and_operations_costs']:
            distribution_costs = [DistributionOperationsCost(**item) for item in analysis_data['distribution_and_operations_costs']]
        
        after_sales_costs = None
        if 'after_sales_costs' in analysis_data and analysis_data['after_sales_costs']:
            after_sales_costs = [AfterSalesCost(**item) for item in analysis_data['after_sales_costs']]
        
        cogs_items = None
        if 'cost_of_goods_sold' in analysis_data and analysis_data['cost_of_goods_sold']:
            cogs_items = [COGSItem(**item) for item in analysis_data['cost_of_goods_sold']]
        
        yearly_cost_breakdown = None
        if 'yearly_cost_breakdown' in analysis_data and analysis_data['yearly_cost_breakdown']:
            yearly_cost_breakdown = {
                year: YearlyCostBreakdown(**data) 
                for year, data in analysis_data['yearly_cost_breakdown'].items()
            }
        
        seven_year_summary = None
        if 'seven_year_summary' in analysis_data and analysis_data['seven_year_summary']:
            seven_year_summary = SevenYearSummary(**analysis_data['seven_year_summary'])
        
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
            development_costs=development_costs,
            total_development_cost=analysis_data.get("total_development_cost"),
            customer_acquisition_costs=customer_acquisition_costs,
            total_customer_acquisition_cost=analysis_data.get("total_customer_acquisition_cost"),
            distribution_and_operations_costs=distribution_costs,
            total_distribution_operations_cost=analysis_data.get("total_distribution_operations_cost"),
            after_sales_costs=after_sales_costs,
            total_after_sales_cost=analysis_data.get("total_after_sales_cost"),
            cost_of_goods_sold=cogs_items,
            average_cogs_per_bundle=analysis_data.get("average_cogs_per_bundle"),
            volume_projections=analysis_data.get("volume_projections"),
            yearly_cost_breakdown=yearly_cost_breakdown,
            seven_year_summary=seven_year_summary,
            total_estimated_cost_summary=analysis_data.get("total_estimated_cost_summary"),
            confidence_level=analysis_data.get("confidence_level"),
            additional_notes=analysis_data.get("additional_notes"),
            identified_variables=[Variable(**v) for v in analysis_data.get("identified_variables", [])],
            formulas=[Formula(**f) for f in analysis_data.get("formulas", [])],
            business_assumptions=analysis_data.get("business_assumptions", []),
            improvement_recommendations=analysis_data.get("improvement_recommendations", []),
            value_market_potential_text=analysis_data.get("value_market_potential_text", ""),
            executive_summary=analysis_data.get("executive_summary", ""),
            sources=analysis_data.get("sources"),
            key_risks=analysis_data.get("key_risks"),
            competitive_advantages=analysis_data.get("competitive_advantages")
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
    """Analyze document using Google Gemini 2.0 Flash Experimental"""
    config = get_settings()
    genai.configure(api_key=config.gemini_api_key)
    
    # Use temperature from settings
    if settings is None:
        settings = AnalysisSettings()
    
    # Optimized configuration for high-quality analysis
    generation_config = {
        "temperature": settings.temperature,  # Use full temperature range for quality
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 16384,  # Increased for comprehensive responses
    }
    
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp',  # Latest fastest Gemini model
        generation_config=generation_config
    )
    
    prompt = get_analysis_prompt(text, settings)
    
    try:
        response = model.generate_content(prompt)
        return parse_analysis_response(response.text)
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        
        # Provide helpful error message
        if "timeout" in error_msg.lower() or "504" in error_msg or "deadline" in error_msg.lower():
            error_msg = "Request timed out. The analysis is too complex. Try using the OpenAI provider."
        elif "quota" in error_msg.lower() or "429" in error_msg:
            error_msg = "API quota exceeded. Please try again later or use OpenAI provider."
        
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
            improvement_recommendations=["Try OpenAI provider", "Simplify your input document"],
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
