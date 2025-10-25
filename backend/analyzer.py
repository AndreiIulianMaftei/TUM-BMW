import google.generativeai as genai
from openai import OpenAI
from backend.config import get_settings
from backend.models import (
    ComprehensiveAnalysis, Variable, Formula, TAMMetrics, SAMMetrics, 
    SOMMetrics, ROIMetrics, TurnoverMetrics, VolumeMetrics, UnitEconomics,
    EBITMetrics, COGSMetrics, MarketPotential, AnalysisSettings, 
    IndustryExample, DevelopmentCost, CustomerAcquisitionCost,
    DistributionOperationsCost, AfterSalesCost, COGSItem, YearlyCostBreakdown,
    SevenYearSummary, KeyRisk, CompetitiveAdvantage
)
import json
import os
from datetime import datetime
from pathlib import Path


def get_analysis_prompt(text: str, settings: AnalysisSettings = None) -> str:
    """
    Generate the comprehensive analysis prompt for both LLM providers.
    
    THIS IS THE MOST CRITICAL FUNCTION - The system prompt determines analysis quality.
    
    Key improvements:
    1. Structured output format with strict JSON schema
    2. Industry-specific context injection
    3. Currency-aware calculations
    4. Comprehensive cost breakdown structure
    5. Real-world data derivation with source validation
    """
    
    # Default settings if none provided
    if settings is None:
        settings = AnalysisSettings()
    
    return f"""You are Quant AI - an elite financial analyst specializing in market analysis and financial modeling for the automotive and technology industries.

CONFIGURATION: Currency={settings.currency}{f", Industry={settings.industry_focus.upper()}" if settings.industry_focus else ""}

ANALYZE THIS BUSINESS CONCEPT:
{text}

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE GUIDELINES:

1. DATA DERIVATION & CALCULATION:
   - DO NOT use mock or placeholder data
   - DERIVE all estimates from real industry benchmarks, competitor data, and market research
   - CALCULATE projections based on logical assumptions and growth models
   - RESEARCH online for supporting evidence including company examples, industry reports, and market data
   - VALIDATE your estimates against similar projects/companies in the automotive, motorcycle, or related industries

2. SOURCE VALIDATION & EVIDENCE:
   - For EVERY cost estimate, provide real company examples with actual project costs
   - Include reference_links to credible sources (annual reports, press releases, industry publications)
   - Cite specific companies (BMW competitors like Mercedes-Benz, Audi, Porsche, Harley-Davidson, Ducati, etc.)
   - Use market_comparison fields to show how your estimates compare to real-world examples
   - Sources must be verifiable and recent (prefer 2020-2024 data)

3. MARKET ANALYSIS REQUIREMENTS:
   - TAM/SAM/SOM: Base on actual market sizes from industry reports
   - Include real industry examples with links for each metric
   - Provide justification showing your calculation methodology
   - Use competitor benchmarks to validate your projections

4. COST BREAKDOWN STRUCTURE:
   - Development Costs: Itemize IT development, system integration, project management
   - Customer Acquisition: Calculate CAC with channel-specific costs and industry benchmarks
   - Distribution/Operations: Include logistics, warehousing, IT maintenance with real operational costs
   - After-Sales: Support, warranty, documentation costs with competitor comparisons
   - COGS: Detailed per-unit costs with margin analysis vs. industry standards

5. PROJECTIONS (2024-2030):
   - Provide realistic volume growth based on market penetration models
   - Show year-by-year cost breakdowns
   - Calculate cumulative totals and averages
   - Base growth rates on industry trends and competitor performance

6. QUALITY STANDARDS:
   - All monetary amounts must be realistic (not round numbers like 0, 1000, 5000)
   - Every "market_comparison" must include real company names and actual project data
   - Reference links must be real URLs (not placeholders)
   - Reasoning fields must explain the logic behind each estimate
   - Confidence levels should reflect data quality (70-85% typical range)

OUTPUT REQUIREMENTS - Return ONLY valid JSON with this exact structure:

{{
  "tam": {{
    "description_of_public": "Clear description of the total addressable market",
    "market_size": <realistic_number>,
    "growth_rate": <percentage>,
    "time_horizon": "2024-2030",
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "justification": "Detailed calculation methodology with data sources",
    "insight": "Key market insight (2-3 sentences)",
    "confidence": 75,
    "industry_example": {{
      "name": "Real Company Name",
      "description": "Specific example of TAM in related market",
      "link": "https://real-url.com/source",
      "metric_value": <actual_market_size>
    }},
    "breakdown": {{"segment1": <amount>, "segment2": <amount>}}
  }},
  "sam": {{
    "description_of_public": "Serviceable available market description",
    "region": "Geographic/demographic scope",
    "target_segment": "Specific customer segment",
    "market_size": <realistic_number>,
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "justification": "How SAM was derived from TAM with supporting data",
    "insight": "Market opportunity insight",
    "confidence": 75,
    "industry_example": {{
      "name": "Competitor Company",
      "description": "Their addressable market example",
      "link": "https://source-url.com",
      "metric_value": <number>
    }},
    "penetration_rate": <percentage>
  }},
  "som": {{
    "description_of_public": "Serviceable obtainable market description",
    "market_share": <percentage>,
    "revenue_potential": <amount>,
    "capture_period": "Timeline (e.g., 3-5 years)",
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "justification": "Realistic market capture strategy with competitive analysis",
    "insight": "Strategic positioning insight",
    "confidence": 70,
    "industry_example": {{
      "name": "Similar Company Launch",
      "description": "Their market penetration example",
      "link": "https://url.com",
      "metric_value": <number>
    }},
    "customer_acquisition_cost": <calculated_CAC>
  }},
  "roi": {{
    "revenue": <projected_total_revenue>,
    "cost": <total_investment>,
    "roi_percentage": <calculated_roi>,
    "numbers": {{"2024": <roi>, "2025": <roi>, "2026": <roi>, "2027": <roi>, "2028": <roi>, "2029": <roi>, "2030": <roi>}},
    "payback_period_months": <calculated_months>,
    "insight": "ROI analysis with risk factors",
    "confidence": 70,
    "cost_breakdown": {{"development": <amount>, "marketing": <amount>, "operations": <amount>}}
  }},
  "turnover": {{
    "year": 2024,
    "total_revenue": <amount>,
    "yoy_growth": <percentage>,
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "revenue_streams": {{"primary_product": <amount>, "services": <amount>, "recurring": <amount>}},
    "insight": "Revenue drivers and sustainability",
    "confidence": 70
  }},
  "volume": {{
    "units_sold": <projected_units>,
    "region": "Market scope",
    "period": "Annual",
    "numbers": {{"2024": <units>, "2025": <units>, "2026": <units>, "2027": <units>, "2028": <units>, "2029": <units>, "2030": <units>}},
    "insight": "Volume trajectory explanation",
    "confidence": 70,
    "growth_drivers": ["Driver 1 with data support", "Driver 2 with market evidence"]
  }},
  "unit_economics": {{
    "unit_revenue": <avg_selling_price>,
    "unit_cost": <total_unit_cost>,
    "margin": <gross_margin_amount>,
    "margin_percentage": <percentage>,
    "ltv_cac_ratio": <calculated_ratio>,
    "insight": "Unit economics health assessment",
    "confidence": 70,
    "cost_components": {{"variable_costs": <amount>, "fixed_costs_per_unit": <amount>}}
  }},
  "ebit": {{
    "revenue": <operating_revenue>,
    "operating_expense": <opex>,
    "ebit_margin": <ebit_amount>,
    "ebit_percentage": <percentage>,
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "insight": "Operating profitability trajectory",
    "confidence": 70,
    "opex_breakdown": {{"rd": <amount>, "sales_marketing": <amount>, "general_admin": <amount>}}
  }},
  "cogs": {{
    "material": <amount>,
    "labor": <amount>,
    "overheads": <amount>,
    "total_cogs": <sum>,
    "cogs_percentage": <percentage_of_revenue>,
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "insight": "Cost structure efficiency",
    "confidence": 70
  }},
  "market_potential": {{
    "market_size": <total_market>,
    "penetration": <target_percentage>,
    "growth_rate": <annual_cagr>,
    "numbers": {{"2024": <amount>, "2025": <amount>, "2026": <amount>, "2027": <amount>, "2028": <amount>, "2029": <amount>, "2030": <amount>}},
    "market_drivers": ["Driver 1 with industry evidence", "Driver 2 with trends"],
    "barriers_to_entry": ["Barrier 1", "Barrier 2"],
    "insight": "Overall market attractiveness",
    "confidence": 70
  }},
  "development_costs": [
    {{
      "category": "IT Development (System Name/Component)",
      "estimated_amount": <realistic_cost>,
      "currency": "{settings.currency}",
      "reasoning": "Detailed explanation of why this development is needed, what it includes (e.g., frontend, backend, integration, testing), and how the estimate was derived",
      "market_comparison": {{
        "similar_case": "Real Company - Actual Project Name",
        "comparison_details": "Detailed comparison explaining why this company's project is similar and how costs align. Include project scope, timeline, and outcomes.",
        "cost_figures": [
          {{
            "company": "Company Name (e.g., Mercedes-Benz, Audi, Porsche)",
            "project": "Specific project name (e.g., Configurator Upgrade, DMS Integration)",
            "amount": <actual_reported_cost>,
            "currency": "{settings.currency}",
            "year": 2023
          }}
        ],
        "source": "Specific source type (e.g., Annual Report, Press Release, Industry Analysis)",
        "reference_links": ["https://real-verifiable-url.com/source"]
      }}
    }}
  ],
  "total_development_cost": <sum_of_all_development_costs>,
  "customer_acquisition_costs": [
    {{
      "category": "Marketing Channel (e.g., Digital Marketing, Dealer Training)",
      "estimated_amount_per_customer": <calculated_CAC>,
      "estimated_annual_budget": <total_annual_budget>,
      "currency": "{settings.currency}",
      "reasoning": "How this channel contributes to customer acquisition, expected reach, conversion rates, and budget calculation methodology",
      "market_comparison": {{
        "similar_case": "Competitor Marketing Program",
        "comparison_details": "How competitor's CAC and marketing spend validates this estimate",
        "cost_figures": [
          {{
            "company": "Competitor Name",
            "project": "Marketing campaign/program",
            "amount": <actual_budget>,
            "currency": "{settings.currency}",
            "year": 2023
          }}
        ],
        "source": "Industry report or company disclosure",
        "reference_links": ["https://source-url.com"]
      }}
    }}
  ],
  "total_customer_acquisition_cost": <sum_of_annual_budgets>,
  "distribution_and_operations_costs": [
    {{
      "category": "Operations Category (e.g., Logistics, IT Maintenance)",
      "estimated_amount": <annual_cost>,
      "currency": "{settings.currency}",
      "reasoning": "What this covers, why it's necessary, and how the cost was estimated",
      "market_comparison": {{
        "similar_case": "Industry Benchmark",
        "comparison_details": "How industry standards validate this operational cost",
        "cost_figures": [
          {{
            "company": "Company Name",
            "project": "Similar operations",
            "amount": <benchmark_cost>,
            "currency": "{settings.currency}",
            "year": 2023
          }}
        ],
        "source": "Logistics report or OEM disclosure",
        "reference_links": ["https://url.com"]
      }}
    }}
  ],
  "total_distribution_operations_cost": <sum>,
  "after_sales_costs": [
    {{
      "category": "After-sales Category (e.g., Support, Warranty)",
      "estimated_amount": <annual_cost>,
      "currency": "{settings.currency}",
      "reasoning": "Scope of after-sales support and cost drivers",
      "market_comparison": {{
        "similar_case": "Industry Example",
        "comparison_details": "How competitors handle similar after-sales costs",
        "cost_figures": [
          {{
            "company": "Company",
            "project": "Support program",
            "amount": <cost>,
            "currency": "{settings.currency}",
            "year": 2023
          }}
        ],
        "source": "Source type",
        "reference_links": ["https://url.com"]
      }}
    }}
  ],
  "total_after_sales_cost": <sum>,
  "cost_of_goods_sold": [
    {{
      "product_category": "Product/Bundle Type",
      "price_per_item": <selling_price>,
      "cogs_per_item": <cost_to_produce>,
      "gross_margin_percentage": <margin>,
      "currency": "{settings.currency}",
      "reasoning": "COGS breakdown including materials, labor, overhead. How margin was determined.",
      "market_comparison": {{
        "similar_case": "Competitor Product Margins",
        "comparison_details": "Industry margin benchmarks for similar products",
        "cost_figures": [
          {{
            "company": "Competitor",
            "product": "Similar product",
            "cogs": <cost>,
            "retail_price": <price>,
            "margin": <percentage>,
            "currency": "{settings.currency}",
            "year": 2023
          }}
        ],
        "source": "Market analysis or teardown report",
        "reference_links": ["https://url.com"]
      }}
    }}
  ],
  "average_cogs_per_bundle": <weighted_average>,
  "volume_projections": {{"2024": <units>, "2025": <units>, "2026": <units>, "2027": <units>, "2028": <units>, "2029": <units>, "2030": <units>}},
  "yearly_cost_breakdown": {{
    "2024": {{
      "projected_volume": <units>,
      "one_time_development": <amount>,
      "customer_acquisition": <annual>,
      "distribution_operations": <annual>,
      "after_sales": <annual>,
      "total_cogs": <volume_x_unit_cogs>,
      "cogs_per_unit": <unit_cogs>,
      "total_cost": <sum_all_costs>,
      "currency": "{settings.currency}"
    }},
    "2025": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}},
    "2026": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}},
    "2027": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}},
    "2028": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}},
    "2029": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}},
    "2030": {{"projected_volume": <units>, "one_time_development": 0, "customer_acquisition": <amount>, "distribution_operations": <amount>, "after_sales": <amount>, "total_cogs": <amount>, "cogs_per_unit": <amount>, "total_cost": <amount>, "currency": "{settings.currency}"}}
  }},
  "seven_year_summary": {{
    "total_cost_2024_2030": <sum_all_years>,
    "total_volume_2024_2030": <sum_units>,
    "average_cost_per_unit": <total_cost_div_total_volume>,
    "currency": "{settings.currency}"
  }},
  "total_estimated_cost_summary": {{
    "one_time_development": <total_dev_costs>,
    "annual_customer_acquisition": <avg_annual>,
    "annual_distribution_operations": <avg_annual>,
    "annual_after_sales": <avg_annual>,
    "average_cogs_per_unit": <unit_cogs>
  }},
  "confidence_level": "Medium",
  "additional_notes": "Key assumptions, limitations, and important context about the analysis. Include any data gaps or estimation methodologies that affect confidence.",
  "identified_variables": [
    {{"name": "Variable Name", "value": "Value/Range", "description": "Why this variable is critical to the business model"}}
  ],
  "formulas": [
    {{"name": "Formula Name", "formula": "Mathematical expression", "calculation": "Sample calculation with numbers"}}
  ],
  "business_assumptions": [
    "Specific assumption 1 with basis",
    "Specific assumption 2 with market data"
  ],
  "improvement_recommendations": [
    "Actionable recommendation 1 with expected impact",
    "Actionable recommendation 2 with implementation guidance"
  ],
  "value_market_potential_text": "3-paragraph executive summary: (1) Market opportunity with TAM/SAM/SOM context, (2) Competitive positioning and differentiation, (3) Growth strategy and financial outlook",
  "executive_summary": "Concise 2-3 sentence investment pitch highlighting the opportunity, differentiation, and potential ROI",
  "sources": [
    "https://real-industry-report.com",
    "https://competitor-annual-report.com",
    "https://market-research-firm.com/study"
  ],
  "key_risks": [
    "Specific risk 1 with probability and mitigation",
    "Specific risk 2 with impact assessment"
  ],
  "competitive_advantages": [
    "Advantage 1 with market validation",
    "Advantage 2 with sustainability assessment"
  ]
}}

REMEMBER:
- Use REAL company examples (BMW, Mercedes, Audi, Porsche, Harley-Davidson, Ducati, Honda, Yamaha, etc.)
- Provide ACTUAL cost figures from industry (not zeros or placeholders)
- Include VERIFIABLE reference links to sources
- Calculate ALL projections with clear methodology
- Base estimates on COMPETITIVE intelligence and market data
- Show your work in reasoning/justification fields
- Currency: {settings.currency}

Return ONLY the JSON. No additional text or explanations outside the JSON structure."""


def save_json_response(response_text: str, provider: str) -> str:
    """
    Save LLM JSON response to Json_Results folder for inspection.
    Returns the filepath where the JSON was saved.
    """
    try:
        # Create Json_Results directory if it doesn't exist
        results_dir = Path("Json_Results")
        results_dir.mkdir(exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{provider}_{timestamp}.json"
        filepath = results_dir / filename
        
        # Clean up the response text if it has markdown code blocks
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        cleaned_text = cleaned_text.strip()
        
        # Try to parse and pretty-print JSON
        try:
            parsed_json = json.loads(cleaned_text)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            # If parsing fails, save raw text
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        
        print(f"✓ Saved LLM response to: {filepath}")
        return str(filepath)
    except Exception as e:
        print(f"Warning: Could not save JSON response: {e}")
        return ""


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
            
            # Advanced repair logic
            # 1. Try to find incomplete arrays and close them
            lines = response_text.split('\n')
            
            # Track open brackets
            open_braces = response_text.count('{') - response_text.count('}')
            open_brackets = response_text.count('[') - response_text.count(']')
            
            # Remove incomplete last line if it doesn't end with proper punctuation
            last_line = lines[-1].strip()
            if last_line and not last_line.endswith((',', '}', ']', '"')):
                lines = lines[:-1]
                response_text = '\n'.join(lines)
                # Recalculate
                open_braces = response_text.count('{') - response_text.count('}')
                open_brackets = response_text.count('[') - response_text.count(']')
            
            # Close any open arrays first
            closing = ''
            if open_brackets > 0:
                # Check if last character is a comma, if not add one before closing
                if response_text.rstrip().endswith(','):
                    closing = '\n  ]'
                else:
                    closing = '\n  ]'
                open_brackets -= 1
            
            # Close remaining arrays
            closing += '\n  ]' * open_brackets
            
            # Close any open objects
            closing += '\n}' * open_braces
            
            response_text = response_text.rstrip() + closing
            
            print(f"Repair: Added {open_braces} closing braces and {open_brackets + (1 if '[' in closing[:10] else 0)} closing brackets")
        
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
    """Analyze document using Google Gemini"""
    config = get_settings()
    genai.configure(api_key=config.gemini_api_key)
    
    if settings is None:
        settings = AnalysisSettings()
    
    generation_config = {
        "temperature": settings.temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,  # Increase token limit to prevent truncation
    }
    
    # Configure model with extended request options and proper safety settings
    model = genai.GenerativeModel(
        config.gemini_model_name,  # Use environment variable
        generation_config=generation_config,
        # Disable all safety filters for business/financial analysis
        # This prevents false positives on terms like "risk", "exposure", "dangerous", etc.
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
    )
    
    prompt = get_analysis_prompt(text, settings)
    
    # Log prompt size for debugging
    prompt_chars = len(prompt)
    prompt_tokens_estimate = prompt_chars // 4  # Rough estimate: 4 chars per token
    print(f"Gemini - Prompt size: {prompt_chars} chars (~{prompt_tokens_estimate} tokens)")
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        
        # Check if response was blocked by safety filters
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            feedback = response.prompt_feedback
            print(f"Gemini Safety Filter Triggered: {feedback}")
            error_msg = f"Content blocked by safety filter: {feedback.block_reason}. Safety ratings: {feedback.safety_ratings}"
            raise Exception(error_msg)
        
        # Check if we have actual text response
        if not response.text or len(response.text.strip()) == 0:
            print(f"Gemini Response Debug - Parts: {response.parts if hasattr(response, 'parts') else 'N/A'}")
            print(f"Gemini Response Debug - Candidates: {response.candidates if hasattr(response, 'candidates') else 'N/A'}")
            error_msg = "Gemini returned an empty response. This might be due to safety filters or API issues."
            raise Exception(error_msg)
        
        print(f"Gemini - Response received: {len(response.text)} chars")
        
        # Save the raw JSON response for inspection
        save_json_response(response.text, "gemini")
        
        return parse_analysis_response(response.text)
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error Details: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        
        # Check for specific error types
        if "DeadlineExceeded" in str(type(e).__name__) or "timeout" in error_msg.lower() or "deadline" in error_msg.lower():
            error_msg = f"Gemini API timeout (likely > 60 seconds default). Original error: {error_msg}. Try using OpenAI provider for complex analysis."
        elif "ResourceExhausted" in str(type(e).__name__) or "quota" in error_msg.lower() or "429" in error_msg or "limit" in error_msg.lower():
            error_msg = f"API quota/rate limit exceeded: {error_msg}. Wait a moment and try again or use OpenAI provider."
        elif "safety" in error_msg.lower() or "blocked" in error_msg.lower() or "block_reason" in error_msg.lower():
            error_msg = f"Content flagged by safety filters: {error_msg}. Try OpenAI provider."
        elif "500" in error_msg or "503" in error_msg or "InternalServerError" in str(type(e).__name__):
            error_msg = f"Gemini API internal error: {error_msg}. Try again or use OpenAI provider."
        else:
            # Keep original error for debugging
            error_msg = f"Gemini API error: {error_msg}"
        
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
            business_assumptions=["Analysis failed due to API error"],
            improvement_recommendations=["Try OpenAI provider", "Check your input document for potential issues"],
            value_market_potential_text=f"Analysis could not be completed: {error_msg}",
            executive_summary=f"Analysis failed: {error_msg}"
        )


def analyze_with_openai(text: str, settings: AnalysisSettings = None) -> ComprehensiveAnalysis:
    """Analyze document using OpenAI GPT"""
    config = get_settings()
    client = OpenAI(api_key=config.openai_api_key)
    
    if settings is None:
        settings = AnalysisSettings()
    
    prompt = get_analysis_prompt(text, settings)
    
    # Use configured model name from environment
    response = client.chat.completions.create(
        model=config.openai_model_name,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Save the raw JSON response for inspection
    save_json_response(response.choices[0].message.content, "openai")
    
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
