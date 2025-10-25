"""
Script to generate selling models for Motorrad using Google Gemini 2.5 Flash API.
Creates three models: royalties, subscription, and one-time sale with online research.
"""

import os
import json
import PyPDF2
import google.generativeai as genai
from typing import Dict, List, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not set in environment variables")
    print("Please set it in .env file or using: export GOOGLE_API_KEY='your-api-key'")
    
genai.configure(api_key=GOOGLE_API_KEY)


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


def generate_royalties_model(pdf_content: str, model) -> Dict[str, Any]:
    """
    Generate royalties-based selling model with online research.
    """
    prompt = f"""
    Based on the following product/project information, create a detailed ROYALTIES-BASED selling model.
    
    Product Information:
    {pdf_content}
    
    Please search online for similar projects/products using royalty-based models in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections from 2024 to 2030 with:
       - royalty_percentage: The percentage taken per sale (e.g., 5, 10, 15%)
       - price_per_piece: Selling price of one unit in EUR
       - number_of_users: Estimated number of users/buyers per year
       - yearly_income: Calculated income (price_per_piece * royalty_percentage/100 * number_of_users)
    
    2. A "summary" field explaining:
       - Why these percentages were chosen
       - Market assumptions
       - Growth projections reasoning
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their royalty model details
    
    4. A "methodology" field explaining data sources and assumptions
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))


def generate_subscription_model(pdf_content: str, model) -> Dict[str, Any]:
    """
    Generate subscription-based selling model with online research.
    """
    prompt = f"""
    Based on the following product/project information, create a detailed SUBSCRIPTION-BASED selling model.
    
    Product Information:
    {pdf_content}
    
    Please search online for similar subscription-based projects/products in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections from 2024 to 2030 with:
       - monthly_cost: Subscription price per month in EUR
       - number_of_users: Estimated number of subscribers per year
       - yearly_income: Calculated income (monthly_cost * 12 * number_of_users)
    
    2. A "summary" field explaining:
       - Why this pricing was chosen
       - Market assumptions
       - Growth projections reasoning
       - Churn rate assumptions
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their subscription model details
    
    4. A "methodology" field explaining data sources and assumptions
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))


def generate_one_time_sale_model(pdf_content: str, model) -> Dict[str, Any]:
    """
    Generate one-time sale selling model with online research.
    """
    prompt = f"""
    Based on the following product/project information, create a detailed ONE-TIME SALE selling model.
    
    Product Information:
    {pdf_content}
    
    Please search online for similar one-time sale projects/products in the automotive/motorcycle accessory industry.
    
    Create a JSON structure with the following:
    1. Yearly projections from 2024 to 2030 with:
       - price: One-time purchase price in EUR
       - number_of_users: Estimated number of buyers per year
       - yearly_income: Calculated income (price * number_of_users)
    
    2. A "summary" field explaining:
       - Why this pricing was chosen
       - Market assumptions
       - Growth projections reasoning
       - Market saturation considerations
    
    3. A "comparable_projects" field with:
       - At least 2-3 real or realistic comparable projects
       - Include URLs/links where possible
       - Brief description of each comparable
       - Their pricing details
    
    4. A "methodology" field explaining data sources and assumptions
    
    Return ONLY valid JSON, no markdown formatting or extra text.
    """
    
    response = model.generate_content(prompt)
    return json.loads(response.text.strip().replace('```json', '').replace('```', ''))


def save_json(data: Dict[str, Any], filename: str):
    """Save data to JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Successfully saved: {filename}")
    except Exception as e:
        print(f"✗ Error saving {filename}: {e}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("Motorrad Selling Models Generator")
    print("Using Google Gemini 2.5 Flash API")
    print("=" * 70)
    print()
    
    # Check API key
    if not GOOGLE_API_KEY:
        print("Error: Please set GOOGLE_API_KEY environment variable")
        return
    
    # PDF path
    pdf_path = 'input/Motorrad_Accessory_Bundles_1-Pager_missing_section.pdf'
    
    # Read PDF
    print(f"📄 Reading PDF: {pdf_path}")
    pdf_content = read_pdf(pdf_path)
    
    if not pdf_content:
        print("Error: Could not extract content from PDF")
        return
    
    print(f"✓ Successfully extracted {len(pdf_content)} characters from PDF")
    print()
    
    # Initialize Gemini model with grounding for web search
    print("🤖 Initializing Google Gemini 2.5 Flash model...")
    
    # Use gemini-2.0-flash-exp for better search capabilities
    # Note: Gemini 2.5 Flash might be labeled as gemini-1.5-flash-latest or gemini-2.0-flash-exp
    model = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 8192,
        }
    )
    
    print("✓ Model initialized")
    print()
    
    # Generate models
    print("=" * 70)
    print("Generating Selling Models (this may take a few minutes)...")
    print("=" * 70)
    print()
    
    try:
        # 1. Royalties Model
        print("1️⃣  Generating Royalties-Based Model...")
        royalties_model = generate_royalties_model(pdf_content, model)
        save_json(royalties_model, 'selling_model_royalties.json')
        print()
        
        # 2. Subscription Model
        print("2️⃣  Generating Subscription-Based Model...")
        subscription_model = generate_subscription_model(pdf_content, model)
        save_json(subscription_model, 'selling_model_subscription.json')
        print()
        
        # 3. One-Time Sale Model
        print("3️⃣  Generating One-Time Sale Model...")
        one_time_model = generate_one_time_sale_model(pdf_content, model)
        save_json(one_time_model, 'selling_model_one_time_sale.json')
        print()
        
        # Summary
        print("=" * 70)
        print("✅ All models generated successfully!")
        print("=" * 70)
        print()
        print("Generated files:")
        print("  - selling_model_royalties.json")
        print("  - selling_model_subscription.json")
        print("  - selling_model_one_time_sale.json")
        print()
        
        # Display quick summary
        print("Quick Summary:")
        print("-" * 70)
        
        if 'yearly_projections' in royalties_model:
            total_royalty = sum(year.get('yearly_income', 0) 
                              for year in royalties_model['yearly_projections'])
            print(f"📊 Royalties Model Total (2024-2030): €{total_royalty:,.2f}")
        
        if 'yearly_projections' in subscription_model:
            total_subscription = sum(year.get('yearly_income', 0) 
                                   for year in subscription_model['yearly_projections'])
            print(f"📊 Subscription Model Total (2024-2030): €{total_subscription:,.2f}")
        
        if 'yearly_projections' in one_time_model:
            total_one_time = sum(year.get('yearly_income', 0) 
                               for year in one_time_model['yearly_projections'])
            print(f"📊 One-Time Sale Model Total (2024-2030): €{total_one_time:,.2f}")
        
        print()
        
    except json.JSONDecodeError as e:
        print(f"✗ Error: Failed to parse JSON response from AI: {e}")
        print("The AI might have returned invalid JSON. Please try running again.")
    except Exception as e:
        print(f"✗ Error generating models: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
