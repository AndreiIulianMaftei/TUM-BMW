import json
import os
from dotenv import load_dotenv
import PyPDF2
from pathlib import Path
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini
GEMINI_API_KEY = os.getenv('gemini_api_key')
GEMINI_MODEL_NAME = os.getenv('gemini_model_name')

if not GEMINI_API_KEY:
    raise ValueError("Please set gemini_api_key in .env file")
if not GEMINI_MODEL_NAME:
    raise ValueError("Please set gemini_model_name in .env file")

genai.configure(api_key=GEMINI_API_KEY)


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


def analyze_costs_with_llm(pdf_text):
    """
    Send PDF text to LLM for cost analysis using Google Gemini.
    
    Args:
        pdf_text (str): Extracted text from PDF
        
    Returns:
        dict: Structured cost analysis JSON
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
    7. Include concrete financial figures from similar projects (e.g., "Project X cost €5M", "Budget was $10M USD")
    8. Provide verifiable URLs when possible (annual reports, press releases, news articles)
    
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
                    "comparison_details": "Detailed comparison with MULTIPLE SPECIFIC COST FIGURES from real market cases. Example: 'Mercedes-Benz spent €8.5M on their dealer portal upgrade in 2022, while Audi's similar project was €12M in 2021'",
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
                    "reference_links": [
                        "https://example.com/annual-report-2023.pdf",
                        "https://example.com/press-release"
                    ]
                }}
            }}
        ],
        "total_development_cost": <sum of all development costs - NEVER null>,
        "customer_acquisition_costs": [
            {{
                "category": "Digital Marketing" or "Dealer Incentives" or "Customer Campaigns" or other relevant category,
                "estimated_amount_per_customer": <numeric value - cost per customer acquired>,
                "estimated_annual_budget": <numeric value - total annual budget>,
                "currency": "EUR",
                "reasoning": "Detailed explanation of customer acquisition strategy and costs",
                "market_comparison": {{
                    "similar_case": "Specific real company and project name",
                    "comparison_details": "Comparison with actual CAC figures from market cases",
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
                    "reference_links": ["URL1", "URL2"]
                }}
            }}
        ],
        "total_customer_acquisition_cost": <sum of annual CAC budgets>,
        "distribution_and_operations_costs": [
            {{
                "category": "Logistics" or "Warehousing" or "Dealer Support" or "Order Fulfillment" or other relevant category,
                "estimated_amount": <numeric value - annual cost>,
                "currency": "EUR",
                "reasoning": "Detailed explanation of operational costs",
                "market_comparison": {{
                    "similar_case": "Specific real company and project name",
                    "comparison_details": "Comparison with operational cost figures from market cases",
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
                    "reference_links": ["URL1", "URL2"]
                }}
            }}
        ],
        "total_distribution_operations_cost": <sum of all distribution/operations costs>,
        "after_sales_costs": [
            {{
                "category": "Installation Support" or "Warranty" or "Customer Service" or "Maintenance" or other relevant category,
                "estimated_amount": <numeric value - annual cost>,
                "currency": "EUR",
                "reasoning": "Detailed explanation of after-sales service costs",
                "market_comparison": {{
                    "similar_case": "Specific real company and project name",
                    "comparison_details": "Comparison with after-sales cost figures from market cases",
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
                    "reference_links": ["URL1", "URL2"]
                }}
            }}
        ],
        "total_after_sales_cost": <sum of all after-sales costs>,
        "cost_of_goods_sold": [
            {{
                "product_category": "Specific accessory bundle type or category",
                "price_per_item": <numeric value - retail price>,
                "cogs_per_item": <numeric value - cost of goods sold per item>,
                "gross_margin_percentage": <percentage>,
                "currency": "EUR",
                "reasoning": "Detailed explanation of COGS calculation including parts, labor, overhead",
                "market_comparison": {{
                    "similar_case": "Specific real company and product",
                    "comparison_details": "Comparison with COGS and margin figures from market cases",
                    "cost_figures": [
                        {{
                            "company": "Company name",
                            "product": "Product name",
                            "cogs": <numeric value>,
                            "retail_price": <numeric value>,
                            "margin": <percentage>,
                            "currency": "EUR or USD",
                            "year": <year>
                        }}
                    ],
                    "source": "Specific source with URLs when available",
                    "reference_links": ["URL1", "URL2"]
                }}
            }}
        ],
        "average_cogs_per_bundle": <average cost of goods sold>,
        "total_estimated_cost_summary": {{
            "one_time_development": <total development cost>,
            "annual_customer_acquisition": <total CAC>,
            "annual_distribution_operations": <total distribution/ops>,
            "annual_after_sales": <total after-sales>,
            "average_cogs_per_unit": <average COGS>
        }},
        "confidence_level": "High/Medium/Low",
        "additional_notes": "Methodology used for estimation and any assumptions made"
    }}
    
    Document content:
    {pdf_text[:50000]}
    
    REMEMBER: Use your knowledge base to provide complete estimates. DO NOT leave fields as null.
    Research similar automotive retail IT projects, accessory bundle systems, and BMW Group initiatives to provide realistic figures.
    
    Provide ONLY the JSON response, no additional text.
    """
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        
        # Generate content
        response = model.generate_content(prompt)
        content = response.text
        
        # Try to parse the JSON from the content
        try:
            # Remove markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            cost_data = json.loads(content)
            return cost_data
        except json.JSONDecodeError:
            print("Could not parse JSON from LLM response")
            return {"error": "Failed to parse JSON", "raw_response": content}
            
    except Exception as e:
        print(f"Error calling Google Gemini API: {e}")
        return {"error": str(e)}


def calculate_yearly_costs(cost_data, volume_projections=None):
    """
    Calculate year-by-year costs from 2024-2030 based on volume projections.
    
    Args:
        cost_data (dict): Cost analysis data from LLM
        volume_projections (dict): Projected sales volumes for each year
        
    Returns:
        dict: Updated cost data with yearly breakdown
    """
    # Default sample volume projections (progressive growth)
    if volume_projections is None:
        volume_projections = {
            "2024": 5000,   # Launch year - conservative
            "2025": 12000,  # Growth as market awareness increases
            "2026": 18000,  # Strong adoption
            "2027": 22000,  # Market maturity
            "2028": 25000,  # Peak growth
            "2029": 27000,  # Continued growth
            "2030": 30000   # Mature market
        }
    
    # Extract cost components
    one_time_dev = cost_data.get('total_development_cost', 0)
    annual_cac = cost_data.get('total_customer_acquisition_cost', 0)
    annual_ops = cost_data.get('total_distribution_operations_cost', 0)
    annual_after_sales = cost_data.get('total_after_sales_cost', 0)
    cogs_per_unit = cost_data.get('average_cogs_per_bundle', 0)
    
    yearly_breakdown = {}
    years = ["2024", "2025", "2026", "2027", "2028", "2029", "2030"]
    
    for year in years:
        volume = volume_projections.get(year, 0)
        
        # First year includes one-time development cost
        dev_cost = one_time_dev if year == "2024" else 0
        
        # Calculate total COGS based on volume
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
    total_7_years = sum(yearly_breakdown[year]["total_cost"] for year in years)
    total_volume_7_years = sum(volume_projections[year] for year in years)
    
    # Add to cost_data
    cost_data["volume_projections"] = volume_projections
    cost_data["yearly_cost_breakdown"] = yearly_breakdown
    cost_data["seven_year_summary"] = {
        "total_cost_2024_2030": round(total_7_years, 2),
        "total_volume_2024_2030": total_volume_7_years,
        "average_cost_per_unit": round(total_7_years / total_volume_7_years, 2) if total_volume_7_years > 0 else 0,
        "currency": "EUR"
    }
    
    return cost_data


def process_bmw_pdf(pdf_path, output_path=None, volume_projections=None):
    """
    Main function to process a BMW Group PDF and generate cost analysis.
    
    Args:
        pdf_path (str): Path to the BMW PDF file
        output_path (str, optional): Path to save the output JSON. If None, returns the data.
        volume_projections (dict, optional): Projected sales volumes by year. If None, uses default projections.
        
    Returns:
        dict: Cost analysis data
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    if not pdf_text:
        return {"error": "Failed to extract text from PDF"}
    
    print(f"Extracted {len(pdf_text)} characters from PDF")
    
    # Analyze costs with LLM
    print("Analyzing costs with LLM...")
    cost_data = analyze_costs_with_llm(pdf_text)
    
    # Calculate yearly costs
    print("Calculating yearly cost breakdown (2024-2030)...")
    cost_data = calculate_yearly_costs(cost_data, volume_projections)
    
    # Save to file if output path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cost_data, f, indent=2, ensure_ascii=False)
        print(f"Cost analysis saved to: {output_path}")
    
    return cost_data


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python costs.py <path_to_bmw_pdf> [output_json_path]")
        print("\nExample: python costs.py input/bmw_document.pdf costs_output.json")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "cost_analysis.json"
    
    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    result = process_bmw_pdf(pdf_path, output_path)
    
    print("\n" + "="*50)
    print("Cost Analysis Complete!")
    print("="*50)
    
    # Print yearly breakdown summary
    if "yearly_cost_breakdown" in result:
        print("\n📊 YEARLY COST BREAKDOWN (2024-2030):")
        print("-" * 50)
        for year, data in result["yearly_cost_breakdown"].items():
            print(f"\n{year}:")
            print(f"  Volume: {data['projected_volume']:,} units")
            if data['one_time_development'] > 0:
                print(f"  Development: €{data['one_time_development']:,.2f}")
            print(f"  CAC: €{data['customer_acquisition']:,.2f}")
            print(f"  Operations: €{data['distribution_operations']:,.2f}")
            print(f"  After-sales: €{data['after_sales']:,.2f}")
            print(f"  COGS: €{data['total_cogs']:,.2f} ({data['projected_volume']:,} × €{data['cogs_per_unit']:.2f})")
            print(f"  ➜ Total: €{data['total_cost']:,.2f}")
        
        if "seven_year_summary" in result:
            summary = result["seven_year_summary"]
            print("\n" + "="*50)
            print("7-YEAR SUMMARY (2024-2030):")
            print(f"  Total Cost: €{summary['total_cost_2024_2030']:,.2f}")
            print(f"  Total Volume: {summary['total_volume_2024_2030']:,} units")
            print(f"  Average Cost/Unit: €{summary['average_cost_per_unit']:,.2f}")
            print("="*50)
    
    # Print full JSON
    print("\n📄 Full JSON output:")
    print(json.dumps(result, indent=2))
