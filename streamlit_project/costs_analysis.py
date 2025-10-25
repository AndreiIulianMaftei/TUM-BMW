"""
Cost Analysis Module
Analyzes development, customer acquisition, distribution, and COGS costs
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


def analyze_costs_with_llm(pdf_content: str) -> Dict[str, Any]:
    """
    Analyze costs using OpenAI.
    
    Args:
        pdf_content: Extracted text from PDF
        
    Returns:
        Dict with comprehensive cost analysis
    """
    
    prompt = f"""
    You are a BMW Group business analyst with expertise in automotive industry cost estimation and market research.
    
    Analyze the following BMW Group document and provide a COMPLETE development cost analysis.
    
    CRITICAL INSTRUCTIONS:
    1. DO NOT return null values for estimated_amount, currency, or market_comparison fields
    2. If the document lacks specific cost figures, use your knowledge of:
       - Automotive industry standards
       - BMW Group typical project costs
       - Similar projects from BMW, Mercedes-Benz, Audi, Tesla, etc.
       - IT system development costs in automotive retail
       - Marketing and communication campaign costs
       - Engineering and development typical budgets
    3. Provide realistic estimates in EUR based on industry benchmarks
    4. ALWAYS include real market comparison cases with actual company names and projects
    5. Be specific with numbers - provide ranges if uncertain (e.g., 50000-100000)
    6. In market_comparison, provide MULTIPLE SPECIFIC NUMBERS and ACTUAL URLs/LINKS where available
    7. Include concrete financial figures from similar projects
    
    Please provide a detailed cost analysis in JSON format with the following structure:
    {{
        "development_costs": [
            {{
                "category": "Manufacturing Cost" or "Engineering Cost" or "IT Development" or other relevant category,
                "estimated_amount": <numeric value - NEVER null>,
                "currency": "EUR",
                "reasoning": "Detailed explanation combining document information AND industry knowledge",
                "market_comparison": {{
                    "similar_case": "Specific real company and project name - NEVER null",
                    "comparison_details": "Detailed comparison with MULTIPLE SPECIFIC COST FIGURES",
                    "cost_figures": [
                        {{
                            "company": "Company name",
                            "project": "Project name",
                            "amount": <numeric value>,
                            "currency": "EUR or USD",
                            "year": <year>
                        }}
                    ],
                    "source": "Specific source with URLs when available",
                    "reference_links": ["https://example.com/link1", "https://example.com/link2"]
                }}
            }}
        ],
        "total_development_cost": <sum of all development costs - NEVER null>,
        "customer_acquisition_costs": [
            {{
                "category": "Digital Marketing" or "Dealer Incentives" or "Customer Campaigns",
                "estimated_amount_per_customer": <numeric value>,
                "estimated_annual_budget": <numeric value>,
                "currency": "EUR",
                "reasoning": "Detailed explanation",
                "market_comparison": {{
                    "similar_case": "Company and project",
                    "comparison_details": "Details with figures",
                    "cost_figures": [],
                    "source": "Source",
                    "reference_links": []
                }}
            }}
        ],
        "total_customer_acquisition_cost": <sum of annual CAC budgets>,
        "distribution_and_operations_costs": [
            {{
                "category": "Logistics" or "Warehousing" or "Dealer Support",
                "estimated_amount": <numeric value>,
                "currency": "EUR",
                "reasoning": "Detailed explanation",
                "market_comparison": {{
                    "similar_case": "Company and project",
                    "comparison_details": "Details with figures",
                    "cost_figures": [],
                    "source": "Source",
                    "reference_links": []
                }}
            }}
        ],
        "total_distribution_operations_cost": <sum of all costs>,
        "after_sales_costs": [
            {{
                "category": "Installation Support" or "Warranty" or "Customer Service",
                "estimated_amount": <numeric value>,
                "currency": "EUR",
                "reasoning": "Detailed explanation",
                "market_comparison": {{
                    "similar_case": "Company and project",
                    "comparison_details": "Details with figures",
                    "cost_figures": [],
                    "source": "Source",
                    "reference_links": []
                }}
            }}
        ],
        "total_after_sales_cost": <sum of all costs>,
        "cost_of_goods_sold": [
            {{
                "product_category": "Specific accessory bundle type",
                "price_per_item": <numeric value>,
                "cogs_per_item": <numeric value>,
                "gross_margin_percentage": <percentage>,
                "currency": "EUR",
                "reasoning": "Detailed COGS calculation",
                "market_comparison": {{
                    "similar_case": "Company and product",
                    "comparison_details": "Details with figures",
                    "cost_figures": [],
                    "source": "Source",
                    "reference_links": []
                }}
            }}
        ],
        "average_cogs_per_bundle": <average cost>,
        "total_estimated_cost_summary": {{
            "one_time_development": <total>,
            "annual_customer_acquisition": <total>,
            "annual_distribution_operations": <total>,
            "annual_after_sales": <total>,
            "average_cogs_per_unit": <average>
        }},
        "confidence_level": "High/Medium/Low",
        "additional_notes": "Methodology and assumptions"
    }}
    
    Document content:
    {pdf_content[:50000]}
    
    REMEMBER: Use your knowledge base to provide complete estimates. DO NOT leave fields as null.
    Provide ONLY the JSON response, no additional text.
    """
    
    try:
        print("🤖 [SERVER] Starting cost analysis with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst expert in automotive cost estimation. Provide detailed cost analysis in JSON format with realistic estimates based on industry knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8192
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
        print("✅ [SERVER] Cost analysis completed successfully!")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"✗ [SERVER ERROR] Failed to parse JSON: {e}")
        return {"error": "Failed to parse JSON", "raw_response": json_text}
    except Exception as e:
        print(f"✗ [SERVER ERROR] Error in cost analysis: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def calculate_yearly_costs(cost_data: Dict[str, Any], sales_volume_data: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate year-by-year costs based on actual sales volume.
    
    Args:
        cost_data: Cost analysis data from LLM
        sales_volume_data: Actual sales volumes for each year from TAM/SAM/SOM
        
    Returns:
        Updated cost data with yearly breakdown
    """
    
    # Extract cost components
    one_time_dev = cost_data.get('total_development_cost', 0)
    annual_cac = cost_data.get('total_customer_acquisition_cost', 0)
    annual_ops = cost_data.get('total_distribution_operations_cost', 0)
    annual_after_sales = cost_data.get('total_after_sales_cost', 0)
    cogs_per_unit = cost_data.get('average_cogs_per_bundle', 0)
    
    yearly_breakdown = {}
    
    # Use the years from sales_volume_data instead of hard-coded list
    years = sorted(sales_volume_data.keys())
    
    for year in years:
        volume = sales_volume_data.get(year, 0)
        
        # First year includes one-time development cost
        dev_cost = one_time_dev if year == years[0] else 0
        
        # Calculate total COGS based on actual volume
        total_cogs = volume * cogs_per_unit
        
        # Total cost for the year
        total_cost = dev_cost + annual_cac + annual_ops + annual_after_sales + total_cogs
        
        yearly_breakdown[year] = {
            "projected_volume": volume,
            "one_time_development": dev_cost,
            "customer_acquisition": annual_cac,
            "distribution_operations": annual_ops,
            "after_sales": annual_after_sales,
            "total_cogs": round(total_cogs, 2),
            "cogs_per_unit": cogs_per_unit,
            "total_cost": round(total_cost, 2),
            "currency": "EUR"
        }
    
    # Calculate cumulative totals
    total_all_years = sum(yearly_breakdown[year]["total_cost"] for year in years)
    total_volume_all_years = sum(sales_volume_data[year] for year in years)
    
    # Add to cost_data
    cost_data["volume_projections"] = sales_volume_data
    cost_data["yearly_cost_breakdown"] = yearly_breakdown
    cost_data["seven_year_summary"] = {
        "total_cost_2024_2030": round(total_all_years, 2),
        "total_volume_2024_2030": total_volume_all_years,
        "average_cost_per_unit": round(total_all_years / total_volume_all_years, 2) if total_volume_all_years > 0 else 0,
        "currency": "EUR"
    }
    
    return cost_data


def generate_cost_analysis(pdf_content: str, sales_volume_data: Dict[str, int]) -> Dict[str, Any]:
    """
    Main function to generate complete cost analysis with yearly breakdown.
    
    Args:
        pdf_content: Extracted PDF text
        sales_volume_data: Sales volumes by year
        
    Returns:
        Complete cost analysis with yearly breakdown
    """
    
    # Get cost analysis from LLM
    cost_data = analyze_costs_with_llm(pdf_content)
    
    if "error" in cost_data:
        return cost_data
    
    # Calculate yearly costs with actual sales volumes
    cost_data = calculate_yearly_costs(cost_data, sales_volume_data)
    
    return cost_data
