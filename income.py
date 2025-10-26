"""
Income Analysis Module
Generates selling models (royalties, subscription, one-time sale) using OpenAI
"""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any
import PyPDF2

# Load environment variables
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


def read_pdf(pdf_path: str) -> str:
    """Extract text from PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def generate_royalties_model(pdf_content: str, sales_volume_data: Dict[str, int]) -> Dict[str, Any]:
    """
    Generate royalties-based selling model with online research.
    """
    
    # Format sales volume data for the prompt
    volume_info = "\n".join([f"{year}: {volume} units" for year, volume in sorted(sales_volume_data.items())])
    
    prompt = f"""
    Based on the following product/project information, create a detailed ROYALTIES-BASED selling model.
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
    Product Information:
    {pdf_content[:30000]}
    
    Projected Sales Volumes:
    {volume_info}
    
    Please research similar projects/products using royalty-based models in the automotive/motorcycle accessory industry.
    
    Return ONLY valid JSON in EXACTLY this format (no markdown, no extra text):
    
    {{
        "yearly_projections": [
            {{
                "year": 2024,
                "royalty_percentage": 10,
                "price_per_piece": 150.00,
                "number_of_units": 5000,
                "yearly_income": 75000.00
            }},
            {{
                "year": 2025,
                "royalty_percentage": 10,
                "price_per_piece": 155.00,
                "number_of_units": 6000,
                "yearly_income": 93000.00
            }}
        ],
        "total_income": 168000.00,
        "summary": "Explanation of why these percentages were chosen, market assumptions, growth projections reasoning, industry standards for royalty rates",
        "methodology": "Explanation of data sources and assumptions used",
        "comparable_projects": [
            {{
                "name": "Project Name",
                "description": "Brief description",
                "royalty_rate": 8,
                "source": "URL or reference"
            }}
        ]
    }}
    
    CRITICAL: 
    - yearly_projections MUST be an array of objects
    - Each object MUST have: year (number), royalty_percentage (number), price_per_piece (number), number_of_units (number), yearly_income (number)
    - Use the provided sales volumes for number_of_units
    - Calculate yearly_income = price_per_piece * (royalty_percentage/100) * number_of_units
    - Return valid JSON only, no explanatory text
    """
    
    try:
        print("🤖 [SERVER] Generating royalties model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst. Return ONLY valid JSON matching the exact structure provided. No markdown, no explanations, just the JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
        
        # Validate structure
        if "yearly_projections" not in result or not isinstance(result["yearly_projections"], list):
            raise ValueError("Invalid JSON structure: missing or invalid yearly_projections array")
        
        if len(result["yearly_projections"]) == 0:
            raise ValueError("Invalid JSON structure: yearly_projections array is empty")
        
        # Validate first projection has required fields
        first_proj = result["yearly_projections"][0]
        required_fields = ["year", "royalty_percentage", "price_per_piece", "number_of_units", "yearly_income"]
        for field in required_fields:
            if field not in first_proj:
                raise ValueError(f"Invalid JSON structure: missing required field '{field}' in yearly_projections")
        
        print("✅ [SERVER] Royalties model generated successfully!")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"✗ [SERVER ERROR] Failed to parse JSON: {e}")
        return {"error": "Failed to parse JSON", "raw_response": json_text}
    except Exception as e:
        print(f"✗ [SERVER ERROR] Error generating royalties model: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def generate_subscription_model(pdf_content: str, sales_volume_data: Dict[str, int]) -> Dict[str, Any]:
    """
    Generate subscription-based selling model with online research.
    """
    
    # Format sales volume data for the prompt
    volume_info = "\n".join([f"{year}: {volume} subscribers" for year, volume in sorted(sales_volume_data.items())])
    
    prompt = f"""
    Based on the following product/project information, create a detailed SUBSCRIPTION-BASED selling model.
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
    Product Information:
    {pdf_content[:30000]}
    
    Projected Subscriber Numbers:
    {volume_info}
    
    Please research similar subscription-based projects/products in the automotive/motorcycle accessory industry.
    
    Return ONLY valid JSON in EXACTLY this format (no markdown, no extra text):
    
    {{
        "yearly_projections": [
            {{
                "year": 2024,
                "monthly_cost": 50.00,
                "number_of_subscribers": 5000,
                "churn_rate": 5,
                "yearly_income": 3000000.00
            }},
            {{
                "year": 2025,
                "monthly_cost": 52.00,
                "number_of_subscribers": 6000,
                "churn_rate": 4.5,
                "yearly_income": 3744000.00
            }}
        ],
        "total_income": 6744000.00,
        "summary": "Explanation of why this pricing was chosen, market assumptions, growth projections, churn rate assumptions, customer lifetime value",
        "methodology": "Explanation of data sources and assumptions used",
        "comparable_projects": [
            {{
                "name": "Project Name",
                "description": "Brief description",
                "monthly_price": 45,
                "source": "URL or reference"
            }}
        ]
    }}
    
    CRITICAL:
    - yearly_projections MUST be an array of objects
    - Each object MUST have: year (number), monthly_cost (number), number_of_subscribers (number), churn_rate (number), yearly_income (number)
    - Use the provided subscriber numbers for number_of_subscribers
    - Calculate yearly_income = monthly_cost * 12 * number_of_subscribers
    - Return valid JSON only, no explanatory text
    """
    
    try:
        print("🤖 [SERVER] Generating subscription model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst. Return ONLY valid JSON matching the exact structure provided. No markdown, no explanations, just the JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
        
        # Validate structure
        if "yearly_projections" not in result or not isinstance(result["yearly_projections"], list):
            raise ValueError("Invalid JSON structure: missing or invalid yearly_projections array")
        
        if len(result["yearly_projections"]) == 0:
            raise ValueError("Invalid JSON structure: yearly_projections array is empty")
        
        # Validate first projection has required fields
        first_proj = result["yearly_projections"][0]
        required_fields = ["year", "monthly_cost", "number_of_subscribers", "churn_rate", "yearly_income"]
        for field in required_fields:
            if field not in first_proj:
                raise ValueError(f"Invalid JSON structure: missing required field '{field}' in yearly_projections")
        
        print("✅ [SERVER] Subscription model generated successfully!")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"✗ [SERVER ERROR] Failed to parse JSON: {e}")
        return {"error": "Failed to parse JSON", "raw_response": json_text}
    except Exception as e:
        print(f"✗ [SERVER ERROR] Error generating subscription model: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def generate_one_time_sale_model(pdf_content: str, sales_volume_data: Dict[str, int]) -> Dict[str, Any]:
    """
    Generate one-time sale selling model with online research.
    """
    
    # Format sales volume data for the prompt
    volume_info = "\n".join([f"{year}: {volume} units" for year, volume in sorted(sales_volume_data.items())])
    
    prompt = f"""
    Based on the following product/project information, create a detailed ONE-TIME SALE selling model.
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
    Product Information:
    {pdf_content[:30000]}
    
    Projected Sales Volumes:
    {volume_info}
    
    Please research similar one-time sale projects/products in the automotive/motorcycle accessory industry.
    
    Return ONLY valid JSON in EXACTLY this format (no markdown, no extra text):
    
    {{
        "yearly_projections": [
            {{
                "year": 2024,
                "price": 150.00,
                "number_of_units": 5000,
                "yearly_income": 750000.00
            }},
            {{
                "year": 2025,
                "price": 155.00,
                "number_of_units": 6000,
                "yearly_income": 930000.00
            }}
        ],
        "total_income": 1680000.00,
        "summary": "Explanation of why this pricing was chosen, market assumptions, growth projections, market saturation, pricing strategy over time",
        "methodology": "Explanation of data sources and assumptions used",
        "comparable_projects": [
            {{
                "name": "Project Name",
                "description": "Brief description",
                "price": 140,
                "source": "URL or reference"
            }}
        ]
    }}
    
    CRITICAL:
    - yearly_projections MUST be an array of objects
    - Each object MUST have: year (number), price (number), number_of_units (number), yearly_income (number)
    - Use the provided sales volumes for number_of_units
    - Calculate yearly_income = price * number_of_units
    - Return valid JSON only, no explanatory text
    """
    
    try:
        print("🤖 [SERVER] Generating one-time sale model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst. Return ONLY valid JSON matching the exact structure provided. No markdown, no explanations, just the JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
        
        # Validate structure
        if "yearly_projections" not in result or not isinstance(result["yearly_projections"], list):
            raise ValueError("Invalid JSON structure: missing or invalid yearly_projections array")
        
        if len(result["yearly_projections"]) == 0:
            raise ValueError("Invalid JSON structure: yearly_projections array is empty")
        
        # Validate first projection has required fields
        first_proj = result["yearly_projections"][0]
        required_fields = ["year", "price", "number_of_units", "yearly_income"]
        for field in required_fields:
            if field not in first_proj:
                raise ValueError(f"Invalid JSON structure: missing required field '{field}' in yearly_projections")
        
        print("✅ [SERVER] One-time sale model generated successfully!")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"✗ [SERVER ERROR] Failed to parse JSON: {e}")
        return {"error": "Failed to parse JSON", "raw_response": json_text}
    except Exception as e:
        print(f"✗ [SERVER ERROR] Error generating one-time sale model: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def generate_income_analysis(pdf_content: str, sales_volume_data: Dict[str, int], model_type: str) -> Dict[str, Any]:
    """
    Main function to generate income analysis based on selected model type.
    
    Args:
        pdf_content: Extracted PDF text
        sales_volume_data: Sales volumes by year
        model_type: "Royalties", "Subscription", or "Single Buy"
        
    Returns:
        Complete income analysis for the selected model
    """
    
    if not client:
        return {"error": "OpenAI API key not configured"}
    
    if model_type == "Royalties":
        return generate_royalties_model(pdf_content, sales_volume_data)
    elif model_type == "Subscription":
        return generate_subscription_model(pdf_content, sales_volume_data)
    elif model_type == "Single Buy":
        return generate_one_time_sale_model(pdf_content, sales_volume_data)
    else:
        return {"error": f"Unknown model type: {model_type}"}
