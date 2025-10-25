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
    
    Product Information:
    {pdf_content[:30000]}
    
    Projected Sales Volumes:
    {volume_info}
    
    Please research similar projects/products using royalty-based models in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections matching the provided years with:
       - royalty_percentage: The percentage taken per sale (e.g., 5, 10, 15%)
       - price_per_piece: Selling price of one unit in EUR
       - number_of_units: Use the provided sales volume
       - yearly_income: Calculated income (price_per_piece * royalty_percentage/100 * number_of_units)
    
    2. A "summary" field explaining:
       - Why these percentages were chosen
       - Market assumptions
       - Growth projections reasoning
       - Industry standards for royalty rates
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their royalty model details
    
    4. A "methodology" field explaining data sources and assumptions
    
    5. A "total_income" field with sum of all yearly incomes
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    try:
        print("🤖 [SERVER] Generating royalties model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst expert in automotive sales models and revenue strategies. Provide detailed income analysis in JSON format with realistic estimates based on industry knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
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
    
    Product Information:
    {pdf_content[:30000]}
    
    Projected Subscriber Numbers:
    {volume_info}
    
    Please research similar subscription-based projects/products in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections matching the provided years with:
       - monthly_cost: Subscription price per month in EUR
       - number_of_subscribers: Use the provided sales volume
       - yearly_income: Calculated income (monthly_cost * 12 * number_of_subscribers)
       - churn_rate: Expected customer churn rate (percentage)
    
    2. A "summary" field explaining:
       - Why this pricing was chosen
       - Market assumptions
       - Growth projections reasoning
       - Churn rate assumptions
       - Customer lifetime value considerations
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their subscription model details
    
    4. A "methodology" field explaining data sources and assumptions
    
    5. A "total_income" field with sum of all yearly incomes
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    try:
        print("🤖 [SERVER] Generating subscription model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst expert in subscription business models and recurring revenue strategies. Provide detailed income analysis in JSON format with realistic estimates based on industry knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
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
    
    Product Information:
    {pdf_content[:30000]}
    
    Projected Sales Volumes:
    {volume_info}
    
    Please research similar one-time sale projects/products in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections matching the provided years with:
       - price: One-time purchase price in EUR
       - number_of_units: Use the provided sales volume
       - yearly_income: Calculated income (price * number_of_units)
    
    2. A "summary" field explaining:
       - Why this pricing was chosen
       - Market assumptions
       - Growth projections reasoning
       - Market saturation considerations
       - Pricing strategy over time
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their pricing details
    
    4. A "methodology" field explaining data sources and assumptions
    
    5. A "total_income" field with sum of all yearly incomes
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    try:
        print("🤖 [SERVER] Generating one-time sale model with OpenAI...")
        
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": "You are a BMW Group business analyst expert in product pricing and one-time sale models. Provide detailed income analysis in JSON format with realistic estimates based on industry knowledge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if '```json' in json_text:
            json_text = json_text.split('```json')[1].split('```')[0].strip()
        elif '```' in json_text:
            json_text = json_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(json_text)
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
