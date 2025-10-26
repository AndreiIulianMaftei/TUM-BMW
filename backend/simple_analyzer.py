from openai import OpenAI
from backend.config import get_settings
from backend.calculator import calculate_complete_analysis
from backend.models import ComprehensiveAnalysis
from datetime import datetime
from pathlib import Path
import json

def get_minimal_extraction_prompt(text: str) -> str:
    return f"""Extract ONLY these financial metrics from the business document. Return valid JSON only.

DOCUMENT:
{text}

EXTRACT (use null if not found):
1. project_name: Project title
2. project_type: Identify the business model:
   - "savings" if document mentions cost reduction/efficiency/avoiding costs
   - "one_time_sale" if selling products once (cars, hardware, equipment)
   - "subscription" if recurring revenue (SaaS, membership, monthly fees)
   - "royalty" if taking percentage of transactions (marketplace, licensing, platform)
   - "mixed" if combination
3. annual_revenue_or_savings: Total annual revenue OR savings in EUR (e.g., "€5 million p.a." → 5000000)
4. fleet_size_or_units: Number of units/customers/vehicles (null if savings project without units)
5. price_per_unit: Price or value per unit in EUR (null if savings project)
6. stream_values: Array of revenue/savings stream values [stream1, stream2, ...] in EUR (ANNUAL values)
7. development_cost: One-time development/setup/implementation cost in EUR (look for: feasibility studies, software dev, training costs)
8. growth_rate: Annual growth rate as percentage (default 5)
9. royalty_percentage: For royalty model - percentage taken (0-100, use 0 if not applicable)
10. take_rate: Customer adoption/conversion rate as percentage (default 10)
11. market_coverage: Market penetration percentage (default 50)

IMPORTANT INSTRUCTIONS:
- Stream values should be ANNUAL amounts (p.a. values), NOT one-time totals
- For development_cost: Add up any mentioned costs for studies, software, implementation, training
- If costs aren't specified but project needs implementation, estimate 10-20% of annual value
- Growth rate: Look for phrases like "5% annual growth", "CAGR", "year-over-year increase"

Return ONLY this JSON:
{{
  "project_name": "string or null",
  "project_type": "savings or one_time_sale or subscription or royalty or mixed",
  "annual_revenue_or_savings": number or null,
  "fleet_size_or_units": number or null,
  "price_per_unit": number or null,
  "stream_values": [number] or null,
  "development_cost": number or null,
  "growth_rate": number or null,
  "royalty_percentage": number or null,
  "take_rate": number or null,
  "market_coverage": number or null
}}"""

def analyze_document_fast(text: str) -> ComprehensiveAnalysis:
    print("\n" + "="*80)
    print("🚀 STARTING DOCUMENT ANALYSIS")
    print("="*80)
    
    try:
        settings = get_settings()
        print(f"✓ Config loaded - OpenAI Key: {settings.openai_api_key[:10]}...")
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        print(f"📝 Document length: {len(text)} characters")
        print(f"📝 Document preview (first 200 chars): {text[:200]}...")
        
        prompt = get_minimal_extraction_prompt(text)
        print(f"📤 Sending to LLM - Prompt length: {len(prompt)} chars")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=800
        )
        
        print(f"✓ LLM Response received")
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        print(f"📥 LLM Raw Response:\n{content}\n")
        
        try:
            extracted = json.loads(content)
            
            results_dir = Path("Json_Results")
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            extraction_path = results_dir / f"extraction_{timestamp}.json"
            with open(extraction_path, "w", encoding="utf-8") as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)
            
            print(f"✓ LLM Extraction saved: {extraction_path}")
            print(f"📊 Extracted Data:")
            for key, value in extracted.items():
                print(f"   {key}: {value}")
            print()
            
        except Exception as e:
            print(f"❌ JSON Parse Error: {e}")
            print(f"Raw content causing error: {content[:500]}")
            extracted = {}
        
        print("🧮 Starting calculator with extracted data...")
        print(f"Input to calculator: {json.dumps(extracted, indent=2)}")
        
        full_analysis = calculate_complete_analysis(extracted)
        
        print(f"✓ Calculator completed successfully")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_path = results_dir / f"full_analysis_{timestamp}.json"
        
        analysis_dict = full_analysis.model_dump()
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump(analysis_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Full Analysis saved: {analysis_path}")
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   TAM: €{full_analysis.tam.market_size:,.0f}")
        print(f"   SAM: €{full_analysis.sam.market_size:,.0f}")
        print(f"   SOM: €{full_analysis.som.revenue_potential:,.0f}")
        print(f"   ROI: {full_analysis.roi.roi_percentage:.1f}%")
        print(f"   Break-even: {full_analysis.roi.payback_period_months} months")
        print(f"   Units: {full_analysis.volume.units_sold:,.0f}")
        print("="*80 + "\n")
        
        return full_analysis
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR in analyze_document_fast:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        raise
